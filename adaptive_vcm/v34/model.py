"""Compact spatial encoder + temporal GRU predicts finite action/risk/rate."""
import torch
from torch import nn
import torch.nn.functional as F

class Controller(nn.Module):
    def __init__(self, actions, conditions=6, task_logits=False):
        super().__init__(); self.actions=actions; self.conditions=conditions
        self.task_logits=bool(task_logits)
        self.encoder=nn.Sequential(nn.Conv2d(6,12,3,stride=2,padding=1),nn.SiLU(),
            nn.Conv2d(12,16,3,stride=2,padding=1),nn.SiLU(),nn.AdaptiveAvgPool2d(1))
        self.temporal=nn.GRU(16,24,batch_first=True)
        width=actions*(7 if self.task_logits else 5)
        self.head=nn.Sequential(nn.Linear(24+conditions,32),nn.SiLU(),nn.Linear(32,width))
    def forward(self,x,maps,condition):
        if x.ndim!=5 or maps.shape!=x.shape or condition.shape!=(len(x),self.conditions):
            raise ValueError('controller condition/input shape mismatch')
        b,t,c,h,w=x.shape
        image=torch.cat((x,maps),2).reshape(b*t,6,h,w)
        image=F.interpolate(image,(48,48),mode='bilinear',align_corners=False)
        z=self.encoder(image).reshape(b,t,16)
        _,hidden=self.temporal(z)
        raw=self.head(torch.cat((hidden[-1],condition),1)).reshape(b,self.actions,7 if self.task_logits else 5)
        if not self.task_logits:
            return dict(logits=raw[:,:,0],risk=raw[:,:,1:4],rate=F.softplus(raw[:,:,4])+.05)
        # Per-task action logits: combined proposal restricts to active tasks only.
        active=condition[:,2:5]
        task=raw[:,:,:3]
        combined=(task*active[:,None,:]).sum(-1)
        return dict(logits=combined,logits_task=task,risk=raw[:,:,3:6],rate=F.softplus(raw[:,:,6])+.05)

class EnsembleController(nn.Module):
    """Elementwise mean of member outputs; calibration bounds are merged by the caller."""
    def __init__(self,members,metadata=None):
        super().__init__(); self.members=nn.ModuleList(members); self.metadata=metadata or {}
        self.task_logits=any(getattr(m,'task_logits',False) for m in members)
    def forward(self,x,maps,condition):
        outputs=[m(x,maps,condition) for m in self.members]
        keys=set(outputs[0])
        for value in outputs[1:]:
            if set(value)!=keys: raise ValueError('ensemble member output mismatch')
        return {k:torch.stack([value[k] for value in outputs]).mean(0) for k in outputs[0]}
