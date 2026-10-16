"""V34-Fix2: units fix (relative damage) and rank-seeded shortlist.

The R1 development recipe compared raw nat-scale damage against the
dimensionless tolerance 0.05. Every plausible action therefore failed the
oracle filter, labels collapsed onto the identity, and the calibrated bound was
trained against the wrong unit. Fix2 rescales each active task's damage by the
measured identity cost of the same row, so tolerance/calibration/selection all
speak the same relative unit.
"""
import numpy as np
import pytest
import torch
from adaptive_vcm.v34.learning import relative_damage, targets, targets_per_task, train_controller
from adaptive_vcm.v34.model import Controller


def raw_row():
    # Identity composite costs O(1) nats; every non-identity raw damage exceeds
    # the 0.05 tolerance, exactly the V34-R1 situation the units fix removes.
    return dict(id='image', mask=[1, 0, 1], rate=[1., .8, .9, .95],
                cost=[[2.0, None, 2.0], [2.1, None, 2.09], [2.4, None, 2.1], [2.08, None, 2.06]],
                damage=[[0., None, 0.], [.09, None, .09], [.4, None, .1], [.08, None, .06]])


def test_relative_damage_keeps_identity_anchor_and_none_tasks():
    row = raw_row()
    out = relative_damage([row], [.001] * 3)
    assert len(out) == 1 and out[0] is not row
    value = out[0]
    assert value['damage'][0] == [0.0, None, 0.0]
    assert value['damage'][1][0] == pytest.approx(.09 / 2.0)
    assert value['damage'][1][2] == pytest.approx(.09 / 2.0)
    assert value['damage_absolute'] == row['damage'] and row['damage'][1][0] == .09
    assert value['damage_reference'][0] == pytest.approx(2.0)
    assert value['damage_reference'][1] is None


def test_relative_damage_floor_bounds_near_zero_baseline_and_requires_cost():
    row = dict(id='near-zero', mask=[1, 0, 0], rate=[1., .9],
               cost=[[1e-6, None, None], [2e-6, None, None]],
               damage=[[0., None, None], [1e-4, None, None]])
    value = relative_damage([row], [.001, .001, .001])[0]
    assert value['damage'][0][0] == 0.0
    assert value['damage'][1][0] == pytest.approx(1e-4 / .001)
    with pytest.raises(ValueError):
        relative_damage([dict(id='x', mask=[1, 0, 0], damage=[[0, None, None]])])
    with pytest.raises(ValueError):
        relative_damage([row], [0., .001, .001])


def test_units_fix_restores_non_identity_oracle_labels():
    row = raw_row()
    raw = targets(row['rate'], np.array(row['damage'], float), row['mask'], [.05] * 3, 1.01)
    assert raw == 0  # every raw action exceeds the nat-scale tolerance
    fixed = relative_damage([row], [.001] * 3)[0]
    assert targets(fixed['rate'], np.array(fixed['damage'], float), fixed['mask'], [.05] * 3, 1.01) == 1
    labels = targets_per_task(fixed['rate'], np.array(fixed['damage'], float), fixed['mask'], [.05] * 3, 1.01)
    assert labels.tolist() == [1, -1, 1]


def test_oracle_weight_can_price_consistency_above_rate():
    rate = [1., .9]
    damage = [[0., None, None], [.03, None, None]]
    mask = [1, 0, 0]
    assert targets(rate, damage, mask, [.05] * 3, 1.01) == 1
    assert targets(rate, damage, mask, [.05] * 3, 1.01, [4., 0., 0.]) == 0
    assert targets_per_task(rate, damage, mask, [.05] * 3, 1.01, [4., 0., 0.]).tolist() == [0, -1, -1]
    with pytest.raises(ValueError):
        targets(rate, damage, mask, [.05] * 3, 1.01, [.25] * 2)


def test_rank_seeded_shortlist_does_not_pin_collapsed_ce_choice():
    from adaptive_vcm.v34.evaluation import choose_packet
    from adaptive_vcm.v32.codec import Packet
    class Model(torch.nn.Module):
        def __init__(self):
            super().__init__(); self.weight = torch.nn.Parameter(torch.zeros(()))
            self.metadata = {'calibration': {'risk': [[0] * 3] * 3, 'rate': [0] * 3}}
        def forward(self, x, m, c):
            # CE head collapsed onto action 2 while rate/risk prefer action 1.
            return dict(logits=torch.tensor([[0., 0., 5.]]),
                        risk=torch.tensor([[[0., 0., 0.], [0., 0., 0.], [1., 0., 1.]]]),
                        rate=torch.tensor([[1., .9, 1.2]]))
    rgb = np.zeros((2, 8, 8, 3), np.uint8)
    packets = [Packet(bytes([i]) * size, rgb + i, rgb.shape, size - 40, 40, 0.) for i, size in enumerate([100, 90, 80])]
    calls = []
    def encode(action):
        calls.append(action); return packets[action]
    def score(decoded):
        action = int(decoded[0, 0, 0, 0]); return [[0, None, 0], [.01, None, .01], [.2, None, .2]][action]
    cfg = {'damage_tolerance': [.05] * 3, 'budget_ratio': 1.01, 'source_shortlist': 1,
           'source_guard_limits': [.025, 0, .05]}
    pair = (torch.zeros(2, 3, 8, 8), torch.ones(2, 3, 8, 8) / 3)
    forced, selected, packet, details = choose_packet(Model(), pair, 'h264', 35, [1, 0, 1], cfg,
                                                      packets[0], encode, source_score=score)
    assert forced == 2
    assert details['calibrated_action'] == 1
    assert 2 not in details['tried_actions'] and calls == [1]
    assert selected == 1 and packet is packets[1]


def test_train_controller_runs_on_relative_rows_with_weights():
    cfg = {'epochs': 2, 'lr': .001, 'damage_tolerance': [.05] * 3, 'budget_ratio': 1.01,
           'task_ce_weight': 1.0, 'risk_loss': 'pinball', 'risk_quantile': .9,
           'oracle_damage_weight': [4., .25, .25]}
    inputs = {'image': (torch.rand(1, 3, 12, 12), torch.ones(1, 3, 12, 12) / 3)}
    row = raw_row()
    row['condition'] = [0., .7, *row['mask'], 1.01]
    rows = relative_damage([row], [.001] * 3)
    history = train_controller(Controller(4, conditions=6, task_logits=True), rows, inputs, cfg, 'cpu')
    assert len(history) == 2 and all(np.isfinite(h['loss']) for h in history)
