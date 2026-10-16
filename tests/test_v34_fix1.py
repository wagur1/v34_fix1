"""V34-Fix1: per-task targets, pinball risk, ensemble arms and checkpoint flags."""
import numpy as np
import torch
import pytest
from adaptive_vcm.v34.learning import targets, targets_per_task, pinball_loss, masked_loss, merge_calibrations, train_controller
from adaptive_vcm.v34.model import Controller, EnsembleController
from adaptive_vcm.v34.checkpoint import save_checkpoint, load_checkpoint


def rows_fixture():
    # AR alone is best served by the cheap action 1 (rate .8) while OT rejects it
    # (damage .2 > tolerance .05) and lands on action 3; the joint scalarized
    # target lands on action 3 for both.
    rate = [1., .8, .9, .95]
    damage = [[0., None, 0.], [.01, None, .2], [.04, None, .1], [.02, None, .04]]
    return rate, damage, [1, 0, 1]


def test_per_task_targets_rank_each_active_task_separately():
    rate, damage, mask = rows_fixture()
    labels = targets_per_task(rate, damage, mask, [.05]*3, 1.01)
    # AR alone prefers the cheap action 1 (rate .8) while OT needs action 3;
    # the joint scalarized target picks action 3 for both.
    assert labels.tolist() == [1, -1, 3]
    assert targets(rate, damage, mask, [.05]*3, 1.01) == 3
    with pytest.raises(ValueError): targets_per_task(rate, damage, mask, [.05]*3, .9)


def test_pinball_loss_is_upper_quantile_and_masks_inactive_tasks():
    prediction = torch.zeros((1, 2, 3), requires_grad=True)
    target = torch.tensor([[[1., float('nan'), 0.], [1., float('nan'), 0.]]])
    mask = torch.tensor([[True, False, True]])
    loss = pinball_loss(prediction, target, mask, .9)
    assert loss.item() == pytest.approx(.45)  # rows: (0.9 + 0) twice over 4 active cells
    prediction2 = torch.tensor([[[1., 0., 0.]]], requires_grad=True)
    loss2 = pinball_loss(prediction2, torch.tensor([[[0., 0., 0.]]]), torch.tensor([[True, False, False]]), .9)
    assert loss2.item() == pytest.approx(.1)  # overprediction costs (1-q)
    scaled = pinball_loss(torch.zeros((1, 1, 3)) + .5, torch.tensor([[[1., 0., 0.]]]), torch.tensor([[True, False, False]]), .9, [.5, .5, .5])
    assert scaled.item() == pytest.approx(.9)
    with pytest.raises(ValueError): pinball_loss(prediction, target, mask, 1.5)


def test_merged_calibration_means_bounds_and_keeps_scope():
    a = dict(risk=[[0]*3, [1., 1., 1.]], rate=[0., .1], coverage=.9, count=4)
    b = dict(risk=[[0]*3, [3., 3., 3.]], rate=[0., .3], coverage=.9, count=6)
    merged = merge_calibrations([a, b])
    assert merged['risk'][1] == [2., 2., 2.] and merged['rate'][1] == pytest.approx(.2)
    assert merged['count'] == 4 and 'merged ensemble' in merged['scope']
    domains = merge_calibrations([dict(domains={'ar': a}, count=4, coverage=.9),
                                  dict(domains={'ar': b}, count=6, coverage=.9)])
    assert domains['domains']['ar']['risk'][1] == [2., 2., 2.]
    with pytest.raises(ValueError): merge_calibrations([a, dict(b, coverage=.8)])


def test_task_logits_model_combines_only_active_tasks_and_roundtrips(tmp_path):
    model = Controller(3, conditions=6, task_logits=True).eval()
    pair = torch.rand(2, 1, 3, 12, 12)
    mask_ar = torch.tensor([[0., .7, 1., 0., 0., 1.01], [0., .7, 0., 1., 0., 1.01]])
    out = model(pair, pair, mask_ar)
    assert out['logits_task'].shape == (2, 3, 3) and out['logits'].shape == (2, 3)
    assert torch.allclose(out['logits'][0], out['logits_task'][0, :, 0])
    assert torch.allclose(out['logits'][1], out['logits_task'][1, :, 1])
    before = {k: v.detach().clone() for k, v in out.items() if k != 'logits_task'}
    path = tmp_path/'task_logits.pth'
    save_checkpoint(path, model, {'seed': 1})
    loaded = load_checkpoint(path)
    assert loaded.task_logits and loaded.conditions == 6
    after = loaded(pair, pair, mask_ar)
    assert torch.allclose(before['logits'], after['logits']) and torch.allclose(before['risk'], after['risk'])
    legacy = Controller(3, conditions=6)
    assert not legacy.task_logits
    assert legacy(pair, pair, mask_ar)['logits'].shape == (2, 3)


def test_ensemble_controller_averages_member_outputs():
    torch.manual_seed(0)
    a = Controller(3, conditions=6, task_logits=True).eval()
    b = Controller(3, conditions=6, task_logits=True).eval()
    with torch.no_grad():
        b.load_state_dict(a.state_dict())
        for parameter in b.parameters(): parameter.mul_(3)
    pair = torch.rand(1, 2, 3, 12, 12)
    condition = torch.tensor([[0., .7, 1., 1., 0., 1.01]])
    with torch.no_grad():
        ea, eb = a(pair, pair, condition), b(pair, pair, condition)
    ensemble = EnsembleController([a, b], {'ensemble': True}).eval()
    out = ensemble(pair, pair, condition)
    assert torch.allclose(out['logits'], (ea['logits'] + eb['logits'])/2)
    assert torch.allclose(out['rate'], (ea['rate'] + eb['rate'])/2)
    assert ensemble.task_logits


def test_candidate_arms_adds_ensemble_after_seeds(tmp_path):
    from adaptive_vcm.v34.evaluation import candidate_arms
    models = []
    calibration = dict(risk=[[0.]*3]*2, rate=[0., 0.], coverage=.9, count=2)
    for seed in (303401, 303402):
        model = Controller(2, conditions=6)
        path = tmp_path/f'{seed}.pth'
        save_checkpoint(path, model, {'seed': seed, 'calibration': calibration})
        models.append(load_checkpoint(path))
    tags = [tag for tag, _ in candidate_arms(models, {'ensemble': True})]
    assert tags == ['303401', '303402', 'ensemble']
    assert [tag for tag, _ in candidate_arms(models, {'ensemble': False})] == ['303401', '303402']
    assert [tag for tag, _ in candidate_arms(models[:1], {'ensemble': True})] == ['303401']


def test_train_controller_per_task_ce_and_pinball_run_with_finite_loss():
    cfg = {'epochs': 2, 'lr': .001, 'damage_tolerance': [.05]*3, 'budget_ratio': 1.01,
           'task_ce_weight': 1.0, 'risk_loss': 'pinball', 'risk_quantile': .9}
    inputs = {'image': (torch.rand(1, 3, 12, 12), torch.ones(1, 3, 12, 12)/3)}
    rate, damage, mask = rows_fixture()
    rows = [dict(id='image', condition=[0., .7, *mask, 1.01], mask=mask, rate=rate, damage=damage)]
    history = train_controller(Controller(len(rate), conditions=6, task_logits=True), rows, inputs, cfg, 'cpu')
    assert len(history) == 2 and all(np.isfinite(h['loss']) for h in history)
