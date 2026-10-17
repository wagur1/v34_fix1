"""Coverage sweep: lower CAL coverage rescales the one-sided bound post-hoc.

The calibrated arm is pinned to identity when the q0.9 residual bound exceeds
the 0.05 tolerance for every useful action; this ablation checks that lower
coverage factors tighten that bound, stay monotone, and can revive selection.
"""
import numpy as np
import pytest


def _fixture(domains=True):
    damages=[0.01]*14+[0.30]*6
    predicted=[dict(risk=np.zeros((2,3)),rate=np.ones(2)) for _ in damages]
    rows=[]
    for value in damages:
        row=dict(damage=[[0,None,0],[value,None,0]],rate=[1,1],mask=[1,0,1])
        if domains: row['domain']='od'
        rows.append(row)
    return rows,predicted


def test_coverage_sweep_is_monotone_and_revives_selection():
    from adaptive_vcm.v34.learning import coverage_calibrations,calibrate_domains,domain_calibration,select_action
    rows,predicted=_fixture()
    with pytest.raises(ValueError): coverage_calibrations(rows,predicted,[0.,1.2])
    entries=coverage_calibrations(rows,predicted,[0.9,0.5,0.6])
    assert [entry['coverage'] for entry in entries]==[0.5,0.6,0.9]
    bounds={entry['coverage']:domain_calibration(entry['calibration'],'od')['risk'][1][0] for entry in entries}
    assert bounds[0.5]<=bounds[0.6]<=bounds[0.9]<=0.30
    assert bounds[0.9]>0.05 and bounds[0.6]<=0.05
    risk=np.zeros((2,3)); rate=np.array([1.,.5]); mask=[True,False,True]
    strict=select_action(risk,rate,domain_calibration(calibrate_domains(rows,predicted,.9),'od'),mask,[.05]*3,1.01)
    relaxed=select_action(risk,rate,domain_calibration(entries[1]['calibration'],'od'),mask,[.05]*3,1.01)
    assert strict==0 and relaxed==1


def test_single_table_layout_matches_the_od_kernel():
    from adaptive_vcm.v34.learning import coverage_calibrations,domain_calibration
    rows,predicted=_fixture(domains=False)
    entries=coverage_calibrations(rows,predicted,[0.9,0.6],domains=False)
    assert [entry['coverage'] for entry in entries]==[0.6,0.9] and 'domains' not in entries[0]['calibration']
    strict=domain_calibration(entries[1]['calibration'],'od')['risk'][1][0]
    relaxed=domain_calibration(entries[0]['calibration'],'od')['risk'][1][0]
    assert strict==pytest.approx(0.30) and relaxed<=0.05
