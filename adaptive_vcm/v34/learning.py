"""Supervision from measured candidates; gradients never enter the codec."""
import math
import numpy as np
import torch
import torch.nn.functional as F

def oracle_weights(weights):
    if weights is None: return np.full(3,.25)
    value=np.asarray(weights,float)
    if value.shape!=(3,) or not (value>=0).all(): raise ValueError('nonnegative per-task oracle weights required')
    return value

def targets(rate,damage,mask,tolerance,budget,weights=None):
    rate=np.asarray(rate,float); damage=np.asarray(damage,float); mask=np.asarray(mask,bool)
    if not mask.any() or damage.shape!=(len(rate),3) or mask.shape!=(3,):
        raise ValueError('active measured task required')
    valid=np.isfinite(damage[:,mask]).all(1)&np.isfinite(rate)&(rate<=budget)
    valid &= (damage[:,mask]<=np.asarray(tolerance)[mask]).all(1)
    if not valid[0] or abs(rate[0]-1)>1e-6 or np.max(np.abs(damage[0,mask]))>1e-6:
        raise ValueError('identity anchor missing')
    score=rate+oracle_weights(weights)[mask].mean()*np.nan_to_num(damage[:,mask]).mean(1)
    return int(np.argmin(np.where(valid,score,np.inf)))

def targets_per_task(rate,damage,mask,tolerance,budget,weights=None):
    """One rate-aware label per active task; -1 marks tasks with no supervision.

    Fix1: the deployed decision combines per-task risk/rate, so each active task
    supervises its own action ranking instead of a single averaged score.
    """
    rate=np.asarray(rate,float); damage=np.asarray(damage,float); mask=np.asarray(mask,bool)
    if damage.shape!=(len(rate),3) or mask.shape!=(3,) or not mask.any():
        raise ValueError('invalid per-task target inputs')
    labels=np.full(3,-1,np.int64)
    tolerance=np.asarray(tolerance,float); oracle=oracle_weights(weights)
    for task in range(3):
        if not mask[task]: continue
        valid=np.isfinite(rate)&(rate<=budget)&np.isfinite(damage[:,task])
        valid &= damage[:,task]<=tolerance[task]
        if not valid[0] or abs(rate[0]-1)>1e-6 or abs(damage[0,task])>1e-6:
            raise ValueError('identity anchor missing')
        score=rate+oracle[task]*np.nan_to_num(damage[:,task])
        labels[task]=int(np.argmin(np.where(valid,score,np.inf)))
    return labels

def relative_damage(rows,floor=None):
    """Fix2 units: damage as a fraction of the measured identity cost per row/task.

    V34-R1 compared raw nat-scale damage (AR composite ~ CE + .25 KL + .1 feat,
    OD summed detector losses) against the dimensionless tolerance 0.05, so the
    oracle pruned nearly every non-identity action and the calibrated bound was
    trained against the wrong unit. Rescaling each active task by that row's
    identity cost changes labels, supervision and calibration together and makes
    the tolerance interpretable as a fraction of the no-preprocessing cost.
    """
    floor=np.full(3,1e-3) if floor is None else np.asarray(floor,float)
    if floor.shape!=(3,) or not (floor>0).all(): raise ValueError('positive per-task damage floor required')
    result=[]
    for r in rows:
        if 'cost' not in r: raise ValueError('measured cost required for relative damage')
        cost=np.asarray(r['cost'],float)
        if not np.isfinite(cost[0][np.asarray(r['mask'],bool)]).all():
            raise ValueError('finite identity cost required for active tasks')
        damage=np.array([[np.nan if v is None else float(v) for v in row] for row in r['damage']],float)
        reference=np.maximum(cost[0],floor)
        normalized=damage/reference
        normalized[0]=np.where(np.isfinite(damage[0]),0.,np.nan)
        value=dict(r,damage_absolute=r['damage'],
                   damage_reference=[None if not np.isfinite(v) else float(v) for v in reference])
        value['damage']=[[None if not np.isfinite(v) else float(v) for v in row] for row in normalized]
        result.append(value)
    return result

def masked_loss(prediction,target,mask,scale=None):
    active=mask[:,None,:].expand_as(prediction)
    if not active.any(): raise ValueError('empty supervised task mask')
    if not torch.isfinite(target[active]).all(): raise ValueError('nonfinite active task target')
    if scale is None: return (prediction[active]-target[active]).square().mean()
    scale=torch.as_tensor(scale,device=prediction.device,dtype=prediction.dtype)
    if scale.shape!=(3,) or not (scale>0).all(): raise ValueError('positive task scales required')
    # Dimensionless residuals avoid fitting AR CE and track counts on one scale.
    # Huber limits outlier dominance without clipping the measured risk targets.
    return F.smooth_l1_loss((prediction/scale)[active],(target/scale)[active])

def pinball_loss(prediction,target,mask,quantile,scale=None):
    """Per-task quantile (pinball) risk loss; default upper quantile 0.9.

    Fix1: the calibrated arm needs a one-sided upper estimate of measured damage,
    not a conditional mean, so the risk head is trained directly as that quantile.
    """
    active=mask[:,None,:].expand_as(prediction)
    if not active.any(): raise ValueError('empty supervised task mask')
    if not torch.isfinite(target[active]).all(): raise ValueError('nonfinite active task target')
    q=float(quantile)
    if not 0<q<1: raise ValueError('quantile outside (0,1)')
    if scale is None: residual=target[active]-prediction[active]
    else:
        scale=torch.as_tensor(scale,device=prediction.device,dtype=prediction.dtype)
        if scale.shape!=(3,) or not (scale>0).all(): raise ValueError('positive task scales required')
        residual=(target/scale)[active]-(prediction/scale)[active]
    return torch.where(residual>=0,residual*q,residual*(q-1)).mean()

def calibrate(predicted,actual,rate_pred,rate_actual,mask,coverage):
    p,a=np.asarray(predicted),np.asarray(actual)
    mask=np.asarray(mask,bool)
    if p.shape!=a.shape or p.ndim!=3 or mask.shape!=(len(p),3) or not 0<coverage<1:
        raise ValueError('invalid calibration table')
    def upper(values):
        # Finite-sample one-sided order statistic. This is empirical calibration,
        # not a guarantee under distribution shift or correlated codec conditions.
        if not len(values): return 1e6
        return max(0.,float(np.sort(values)[min(len(values)-1,math.ceil((len(values)+1)*coverage)-1)]))
    risk=[[upper((a[:,j,k]-p[:,j,k])[mask[:,k]]) for k in range(3)] for j in range(p.shape[1])]
    r=np.asarray(rate_actual)-np.asarray(rate_pred)
    if r.shape!=p.shape[:2] or not np.isfinite(r).all(): raise ValueError('invalid calibrated rates')
    for k in range(3):
        if mask[:,k].any() and not np.isfinite((a-p)[mask[:,k],:,k]).all(): raise ValueError('invalid calibrated risks')
    risk[0]=[0.]*3
    rates=[upper(r[:,j]) for j in range(p.shape[1])]; rates[0]=0.
    return dict(risk=risk,rate=rates,coverage=coverage,count=len(p),scope='empirical one-sided CAL residuals')

def merge_calibrations(calibrations):
    """Elementwise mean of member bounds for the exploratory ensemble arm."""
    if not calibrations: raise ValueError('no calibrations to merge')
    if all('domains' in value for value in calibrations):
        names=sorted(calibrations[0]['domains'])
        if any(sorted(value['domains'])!=names for value in calibrations):
            raise ValueError('ensemble domain calibration mismatch')
        domains={name:merge_calibrations([value['domains'][name] for value in calibrations]) for name in names}
        return dict(domains=domains,count=min(value['count'] for value in calibrations),
                    coverage=calibrations[0]['coverage'],
                    scope='merged ensemble domains: elementwise mean of member one-sided bounds')
    if any('domains' in value for value in calibrations): raise ValueError('mixed calibration layouts')
    def mean_table(key):
        tables=[np.asarray(value[key],float) for value in calibrations]
        if any(table.shape!=tables[0].shape for table in tables): raise ValueError('calibration shape mismatch')
        return np.stack(tables).mean(0).tolist()
    def mean_scalar(key):
        if any(value[key]!=calibrations[0][key] for value in calibrations): raise ValueError('calibration scalar mismatch')
        return calibrations[0][key]
    return dict(risk=mean_table('risk'),rate=mean_table('rate'),coverage=mean_scalar('coverage'),
                count=min(value['count'] for value in calibrations),
                scope='merged ensemble: elementwise mean of member one-sided bounds')

def select_action(risk,rate,calibration,mask,tolerance,budget):
    risk=np.asarray(risk,float).copy(); rate=np.asarray(rate,float).copy(); mask=np.asarray(mask,bool)
    if risk.shape!=(len(rate),3) or mask.shape!=(3,) or not mask.any(): raise ValueError('invalid selection inputs')
    bounds=np.asarray(calibration['risk'])+risk; rate_bound=rate+np.asarray(calibration['rate'])
    bounds[0]=0; rate_bound[0]=1; risk[0]=0; rate[0]=1
    feasible=(bounds[:,mask]<=np.asarray(tolerance)[mask]).all(1)&(rate_bound<=budget)
    feasible &= np.isfinite(bounds[:,mask]).all(1)&np.isfinite(rate_bound)
    score=rate+.25*risk[:,mask].mean(1)
    return int(np.argmin(np.where(feasible,score,np.inf))) if feasible.any() else 0

def calibrate_domains(rows,predictions,coverage):
    domains={}
    for domain in sorted({r['domain'] for r in rows}):
        ids=[i for i,r in enumerate(rows) if r['domain']==domain]
        selected=[rows[i] for i in ids]; pred=[predictions[i] for i in ids]
        value=calibrate(np.array([p['risk'] for p in pred]),np.array([r['damage'] for r in selected],float),
                        np.array([p['rate'] for p in pred]),np.array([r['rate'] for r in selected]),
                        np.array([r['mask'] for r in selected],bool),coverage)
        value['source_count']=len({r.get('id',str(i)) for i,r in enumerate(selected)})
        domains[domain]=value
    return dict(domains=domains,count=len(rows),coverage=coverage,
                scope='domain-specific empirical CAL residuals; correlated QP/window rows; no coverage guarantee')

def domain_calibration(calibration,domain):
    if 'domains' not in calibration: return calibration
    if domain not in calibration['domains']: raise ValueError('missing domain calibration')
    return calibration['domains'][domain]

def train_controller(model,rows,inputs,cfg,device):
    optimizer=torch.optim.Adam(model.parameters(),lr=cfg['lr']); history=[]
    model.to(device).train()
    groups={}
    for i,r in enumerate(rows):
        groups.setdefault(inputs[r['id']][0].shape[0],[]).append(i)
    c=torch.tensor([r['condition'] for r in rows],device=device,dtype=torch.float32)
    rate=torch.tensor([r['rate'] for r in rows],device=device,dtype=torch.float32)
    damage=torch.tensor([[[float('nan') if v is None else v for v in a] for a in r['damage']] for r in rows],device=device,dtype=torch.float32)
    mask=torch.tensor([r['mask'] for r in rows],device=device,dtype=torch.bool)
    labels=torch.tensor([targets(r['rate'],np.array(r['damage'],float),r['mask'],cfg['damage_tolerance'],cfg['budget_ratio'],cfg.get('oracle_damage_weight')) for r in rows],device=device)
    task_weight=float(cfg.get('task_ce_weight',1.0 if getattr(model,'task_logits',False) else 0.0))
    # Fix1: per-task labels supervise each active task's own rate-aware ranking.
    if getattr(model,'task_logits',False) and task_weight:
        labels_task=torch.as_tensor(np.stack([targets_per_task(r['rate'],np.array(r['damage'],float),r['mask'],cfg['damage_tolerance'],cfg['budget_ratio'],cfg.get('oracle_damage_weight')) for r in rows]),device=device,dtype=torch.long)
    else:
        labels_task=None
    if cfg.get('risk_loss')=='pinball':
        risk_quantile=float(cfg.get('risk_quantile',.9))
        risk_loss=lambda prediction,target,rows_mask: pinball_loss(prediction,target,rows_mask,risk_quantile,cfg.get('risk_scale'))
    else:
        risk_loss=lambda prediction,target,rows_mask: masked_loss(prediction,target,rows_mask,cfg.get('risk_scale'))
    for epoch in range(cfg['epochs']):
        batches=[]; values=[]
        for group in groups.values():
            indices=torch.tensor(group)[torch.randperm(len(group))]
            batches.extend(indices.split(16))
        for index in torch.randperm(len(batches)).tolist():
            ids=batches[index].tolist(); batch=batches[index].to(device)
            x=torch.stack([inputs[rows[i]['id']][0] for i in ids]).to(device)
            m=torch.stack([inputs[rows[i]['id']][1] for i in ids]).to(device)
            out=model(x,m,c[batch])
            loss=F.cross_entropy(out['logits'],labels[batch])+4*risk_loss(out['risk'],damage[batch],mask[batch])+4*F.mse_loss(out['rate'],rate[batch])
            if labels_task is not None:
                per_action=out['logits_task'].permute(0,2,1).reshape(-1,model.actions)
                per_target=labels_task[batch].reshape(-1)
                per_active=mask[batch].reshape(-1)
                if per_active.any():
                    loss=loss+task_weight*F.cross_entropy(per_action[per_active],per_target[per_active])
            if not torch.isfinite(loss): raise ValueError('nonfinite controller loss')
            optimizer.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),5); optimizer.step()
            values.append(float(loss.detach()))
        history.append(dict(epoch=epoch+1,loss=float(np.mean(values))))
    model.eval(); return history
