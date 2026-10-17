import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
import torch

from adaptive_vcm.v34 import SCHEMA
from adaptive_vcm.v34.protocol import ACTIONS, digest, settings
from adaptive_vcm.v34.runner import validate_cache

ROOT = Path(__file__).resolve().parents[1]


def load_ot_module():
    spec = importlib.util.spec_from_file_location("run_v34_ot", ROOT / "scripts" / "run_v34_ot.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pinned_config():
    return settings(ROOT / "configs" / "v34_arot_r1.json")


def synthetic_cache(cfg):
    """Minimal digest-valid OT cache: one train and one cal MOT20 window."""
    rows = []
    sources = {}
    for identifier, split in (("ot/MOT20-02/000001", "train"), ("ot/MOT20-02/000209", "cal")):
        sources[identifier] = dict(split=split, pixel_sha256="0" * 64,
                                   frame_recipe=dict(kind="contiguous-MOT20"))
        rows.append(dict(id=identifier, split=split, domain="ot", codec="h264", qp=30,
                         mask=[True, False, True], provenance=[None, None, "synthetic"],
                         condition=[0.0] * 9, rate=[1.0] * len(ACTIONS),
                         damage=[[None, None, None] for _ in ACTIONS]))
    cache = dict(schema=SCHEMA, experiment="ar_ot", settings=dict(cfg),
                 actions=[list(a) for a in ACTIONS], sources=sources,
                 task_models={"synthetic": 1}, rows=rows)
    cache["sha256"] = digest(cache)
    return cache


def test_settings_compatible_accepts_pinned_config_and_rejects_drift():
    module = load_ot_module()
    cfg = pinned_config()
    assert module.settings_compatible(dict(cfg), cfg)
    drifted = dict(cfg)
    drifted["ot_frames"] = 128
    with pytest.raises(ValueError):
        module.settings_compatible(drifted, cfg)
    with pytest.raises(ValueError):
        module.settings_compatible({}, cfg)


def test_synthetic_ot_cache_roundtrips_and_rejects_tampering():
    module = load_ot_module()
    cfg = pinned_config()
    cache = synthetic_cache(cfg)
    assert module.settings_compatible(cache["settings"], cfg)
    validate_cache(cache)
    reloaded = json.loads(json.dumps(cache))
    validate_cache(reloaded)

    tampered = json.loads(json.dumps(cache))
    tampered["rows"][0]["qp"] = 35
    with pytest.raises(ValueError):
        validate_cache(tampered)

    unknown = json.loads(json.dumps(cache))
    unknown["rows"].append(dict(unknown["rows"][0], id="ot/MOT20-02/999999"))
    unknown["sha256"] = digest({k: v for k, v in unknown.items() if k != "sha256"})
    with pytest.raises(ValueError):
        validate_cache(unknown)


def test_submit_script_uses_tracking_pin():
    spec = importlib.util.spec_from_file_location(
        "submit_v34_ot", ROOT / "scripts" / "submit_v34_ot_kaggle.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from adaptive_vcm.v32.tracking import TRACKEVAL_COMMIT
    assert module.trackeval_pin() == TRACKEVAL_COMMIT


def write_mot_sequence(root, name, count):
    from PIL import Image
    sequence = root / name
    (sequence / "img1").mkdir(parents=True)
    (sequence / "gt").mkdir()
    (sequence / "seqinfo.ini").write_text(
        f"[Sequence]\nname={name}\nimDir=img1\nframeRate=25\nseqLength={count}\n"
        "imWidth=80\nimHeight=40\nimExt=.jpg\n")
    rows = []
    for number in range(1, count + 1):
        pixels = np.zeros((40, 80, 3), np.uint8)
        pixels[5:35, 10:70] = (number * 11) % 200 + 20
        Image.fromarray(pixels).save(sequence / "img1" / f"{number:06}.jpg")
        rows.append(f"{number},1,10,5,20,20,1,1,1")
        rows.append(f"{number},2,50,5,20,20,1,7,1")
    (sequence / "gt" / "gt.txt").write_text("\n".join(rows) + "\n")
    return sequence


class FakeHeads:
    """Deterministic stand-in for the frozen swin detector stack."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.experiment = "ar_ot"

    def hashes(self):
        return {"fixture": "ot-pass"}

    def source(self, r):
        frames = len(r.rgb)
        boxes = np.array([[2, 2, 12, 12], [16, 4, 28, 14]], np.float32)
        r.source_predictions = {
            "od": [dict(boxes=boxes.copy(), scores=np.array([.9, .8], np.float32),
                        labels=np.array([1, 1])) for _ in range(frames)],
            "ar": np.array([.5, .5]),
            "ot": [dict(boxes=boxes.copy(), scores=np.array([.9, .8], np.float32),
                        labels=np.array([1, 1]), track_ids=np.array([1, 2]),
                        frame_number=index + 1) for index in range(frames)]}
        r.source_features = {"ar": torch.zeros(1, 4)}
        r.mask = [True, False, True]
        r.provenance = [None, None, "fixture source tracks"]
        r.source_detector_seconds = 0.0
        r.diagnostic_teacher_seconds = 0.0

    def costs(self, rgb, r, source_only=False):
        shift = float(np.abs(rgb.astype(np.float32) - r.rgb.astype(np.float32)).mean())
        return [0.01, None, shift / 255.0]


class FakeCodec:
    def __init__(self):
        self.last_times = {}

    def roundtrip(self, pixels, source_shape=None, task=None):
        from types import SimpleNamespace
        import hashlib
        decoded = np.clip(pixels.astype(np.int16) + 1, 0, 255).astype(np.uint8)
        payload = decoded.tobytes()
        self.last_times = {"encode_seconds": .001, "decode_seconds": .001, "inverse_seconds": 0.}
        return SimpleNamespace(coded_bytes=len(payload) // 100 + 7, elementary_bytes=len(payload) // 100,
                               metadata_bytes=7, packet_sha256=hashlib.sha256(payload).hexdigest(),
                               decoded=decoded, last_times=dict(self.last_times))


def strip_timings(value):
    """Wall-clock fields differ between runs; measured content must not."""
    if isinstance(value, dict):
        return {k: strip_timings(v) for k, v in value.items() if not k.endswith("_seconds")}
    if isinstance(value, list):
        return [strip_timings(v) for v in value]
    return value


def test_measure_stage_stops_on_budget_resumes_and_matches_fresh_content(tmp_path, monkeypatch):
    module = load_ot_module()
    cfg = pinned_config()
    cfg.update(ot_frames=224, ot_size=32, qps=[30], codecs=["h264"], seeds=[303401],
               epochs=2, detector=None)
    root = tmp_path / "mot20"
    for name in ("MOT20-01", "MOT20-02", "MOT20-03"):
        write_mot_sequence(root, name, 224)
    groups, meta = module.load_ot_cohorts(root, cfg)
    assert len(groups["train"]) == 12 and len(groups["cal"]) == 2
    assert meta["ot"] and meta["ot"][0]["name"] == "MOT20-02"
    heads = FakeHeads(cfg)
    monkeypatch.setattr(module, "codec_factory", lambda task, codec, qp, settings_: FakeCodec())

    out = tmp_path / "out"
    out.mkdir()
    stopped = module.measure_ot(cfg, groups, heads, out, time_budget=1e-9)
    assert stopped["incomplete"] and (out / "measurements.json").is_file() is False
    assert (out / "measurements.partial.json").is_file() and (out / "incomplete.json").is_file()

    done = module.measure_ot(cfg, groups, heads, out)
    assert not done["incomplete"]
    validate_cache(done["cache"])
    assert (out / "incomplete.json").is_file() is False
    assert set(done["inputs"]) == {r.id for split in ("train", "cal") for r in groups[split]}
    expected_rows = len(groups["train"]) + len(groups["cal"])
    assert len(done["cache"]["rows"]) == expected_rows

    fresh = tmp_path / "fresh"
    fresh.mkdir()
    again = module.measure_ot(cfg, groups, FakeHeads(cfg), fresh)
    validate_cache(again["cache"])
    assert strip_timings(again["cache"]["rows"]) == strip_timings(done["cache"]["rows"])
    assert strip_timings(again["cache"]["sources"]) == strip_timings(done["cache"]["sources"])

    fit = [r for r in done["cache"]["rows"] if r["split"] == "train"]
    cal = [r for r in done["cache"]["rows"] if r["split"] == "cal"]
    models = module.train_ot_models(fit, cal, done["inputs"], cfg, out, "cpu", {"fixture": "ot-pass"})
    loaded = module.load_checkpoint(out / f"controller_{cfg['seeds'][0]}.pth", "cpu")
    assert "ot" in loaded.metadata["calibration"]["domains"]
    assert loaded.metadata["experiment"] == "ar_ot"
    assert len(models) == 1
