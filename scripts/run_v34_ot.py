"""Dedicated Object Tracking (MOT20) measurement pass and baseline on V34.

The AR+OD scaled pilot shipped a committed candidate cache for COCO, so unit
and loss variants only retrain and re-evaluate. MOT20 never had that pass:
every OT experiment would re-encode 16-frame 960px windows through the codec
roundtrip and the frozen detector. This script stages the same separation:

  --stage measure   build measurements.json + controller_inputs.pth once
  --stage baseline  retrain and evaluate from a committed cache
  --stage full      measure (or reuse) then train and evaluate

The candidate grid is the arot-r1 repair recipe pinned in configs:
MOT20-02 windows land in train/cal, MOT20-03 is dev, MOT20-01 is test, and
held-out GT is only read by the scoring stage inside evaluation.evaluate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adaptive_vcm.v34 import SCHEMA
from adaptive_vcm.v34.checkpoint import load_checkpoint, save_checkpoint
from adaptive_vcm.v34.evaluation import evaluate
from adaptive_vcm.v34.learning import (calibrate, calibrate_domains,
                                       coverage_calibrations, relative_damage,
                                       targets, train_controller)
from adaptive_vcm.v34.model import Controller
from adaptive_vcm.v34.preprocessing import region_maps
from adaptive_vcm.v34.protocol import ACTIONS, codec_factory, digest, settings
from adaptive_vcm.v34.runner import (condition, infer, input_pair,
                                     measure_candidates, validate_cache,
                                     write_json)
from adaptive_vcm.v34.tasks import Heads
from adaptive_vcm.v34.tracking import tracking_sources

# Runtime knobs that change measured bytes/damage or the frozen detector grid.
# Everything else (epochs, lr, risk loss) only shapes retraining and is free to
# evolve on top of a committed cache.
REUSE_KEYS = ("revision", "frames", "codecs", "qps", "ot_size", "ot_frames",
              "ot_detector_size", "detector", "detector_detections")


def settings_compatible(stored, cfg, keys=REUSE_KEYS):
    """Refuse to reuse a cache measured under different pixel/codec settings."""
    if not isinstance(stored, dict):
        raise ValueError("measurement cache settings missing")
    missing = [k for k in keys if k not in stored]
    if missing:
        raise ValueError(f"measurement cache settings missing keys: {missing}")
    drift = {k: (stored[k], cfg.get(k)) for k in keys if stored[k] != cfg.get(k)}
    if drift:
        raise ValueError(f"measurement cache mismatch {drift}; rerun with --fresh")
    return True


def load_ot_cohorts(mot_root, cfg):
    groups, plan = tracking_sources(Path(mot_root), cfg)
    return groups, {"ot": plan}


def cohort_provenance(plan, groups):
    """File-level provenance for the measured windows only.

    Held-out GT hashes are omitted for sequences that contribute no train/cal
    window, so dev/test labels are never opened before the scoring stage.
    """
    scored_sequences = {r.item["sequence"] for split in ("train", "cal") for r in groups[split]}
    entries = {}
    for item in plan:
        hasher = hashlib.sha256()
        for file in item["images"]:
            hasher.update(file.name.encode())
            hasher.update(file.read_bytes())
        gt = item["path"] / "gt" / "gt.txt"
        entries[item["name"]] = dict(
            frames=item["frames"], full_frames=item["full_frames"],
            width=item["width"], height=item["height"],
            seqinfo_sha256=hashlib.sha256((item["path"] / "seqinfo.ini").read_bytes()).hexdigest(),
            frames_sha256=hasher.hexdigest(),
            gt_sha256=hashlib.sha256(gt.read_bytes()).hexdigest() if item["name"] in scored_sequences and gt.is_file() else None)
    return entries


def measure_ot(cfg, groups, heads, out, time_budget=0, resume=True):
    """Per-candidate roundtrips for every train/cal MOT20 window.

    Writes measurements.partial.json after each window (crash/timeout
    resilience) and finalizes measurements.json + controller_inputs.pth. With
    --time-budget the loop stops gracefully and the partial cache resumes.
    """
    meas = out / "measurements.json"
    partial = out / "measurements.partial.json"
    cache = None
    measured = set()
    if resume and partial.is_file() and not meas.is_file():
        value = json.loads(partial.read_text(encoding="utf-8"))
        settings_compatible(value.get("settings", {}), cfg)
        value.pop("sha256", None)
        cache = value
        measured = set(cache["sources"])
        print(f"Resuming partial cache: {len(measured)} windows already measured", flush=True)
    if cache is None:
        cache = dict(schema=SCHEMA, experiment="ar_ot", settings=cfg, actions=[list(a) for a in ACTIONS],
                     sources={}, task_models=heads.hashes(), rows=[])
    inputs = {}
    timings = []
    start = time.time()
    todo = [(split, r) for split in ("train", "cal") for r in groups[split]]
    for index, (split, r) in enumerate(todo):
        window_start = time.perf_counter()
        heads.source(r)
        maps = region_maps(r.rgb, r.source_predictions["od"])
        inputs[r.id] = input_pair(r.rgb, maps)
        before = len(cache["rows"])
        if r.id not in measured:
            cache["sources"][r.id] = dict(split=split,
                pixel_sha256=hashlib.sha256(r.rgb.tobytes()).hexdigest(), frame_recipe=r.frame_recipe)
            for codec in cfg["codecs"]:
                for qp in cfg["qps"]:
                    engine = codec_factory(r.task, codec, qp, cfg)
                    table = measure_candidates(r.rgb, maps, ACTIONS, engine, r.task,
                                               lambda rgb: heads.costs(rgb, r))
                    cache["rows"].append(dict(id=r.id, split=split, domain=r.task, codec=codec, qp=qp,
                        mask=r.mask, provenance=r.provenance,
                        condition=condition(codec, qp, r.mask, cfg, domain=r.task), **table))
            measured.add(r.id)
        seconds = time.perf_counter() - window_start
        timings.append(dict(id=r.id, split=split, seconds=round(seconds, 3), rows=len(cache["rows"]) - before))
        write_json(partial, {k: v for k, v in cache.items() if k != "sha256"})
        print(f"OT measure {split} {index + 1}/{len(todo)} {r.id}: {seconds:.1f}s "
              f"({len(cache['sources'])} windows, {len(cache['rows'])} rows)", flush=True)
        if time_budget and time.time() - start > time_budget:
            write_json(out / "incomplete.json", dict(status="budget-stopped",
                measured_windows=len(cache["sources"]), expected_windows=len(todo),
                budget_seconds=time_budget, note="rerun to resume from measurements.partial.json"))
            print("Time budget reached; partial cache kept for resume", flush=True)
            return dict(cache=cache, inputs=inputs, incomplete=True)
    cache["sha256"] = digest(cache)
    write_json(meas, cache)
    torch.save(inputs, out / "controller_inputs.pth")
    write_json(out / "measure_timings.json", timings)
    if partial.is_file():
        partial.unlink()
    stale = out / "incomplete.json"
    if stale.is_file():
        stale.unlink()
    return dict(cache=cache, inputs=inputs, incomplete=False)


def train_ot_models(fit_rows, cal_rows, inputs, cfg, out, device, task_models):
    """Domain-conditioned controllers over MOT20 windows (same recipe fields)."""
    choices = [targets(r["rate"], np.array(r["damage"], float), r["mask"],
                       cfg["damage_tolerance"], cfg["budget_ratio"], cfg.get("oracle_damage_weight"))
               for r in fit_rows]
    write_json(out / "train_oracle.json", dict(
        scope="TRAIN measured oracle on MOT20 windows; never deployed TEST GT selection",
        count=len(choices), action_counts={str(a): choices.count(a) for a in range(len(ACTIONS))}))
    models = []
    for seed in cfg["seeds"]:
        torch.manual_seed(seed)
        np.random.seed(seed)
        model = Controller(len(ACTIONS), conditions=9 if cfg.get("domain_condition") else 6,
                           task_logits=cfg.get("task_logits", False))
        history = train_controller(model, fit_rows, inputs, cfg, device)
        pred = [infer(model, inputs[r["id"]], r["condition"]) for r in cal_rows]
        if cfg.get("domain_condition"):
            calibration = calibrate_domains(cal_rows, pred, cfg["cal_coverage"])
        else:
            calibration = calibrate(
                np.array([p["risk"] for p in pred]), np.array([r["damage"] for r in cal_rows], float),
                np.array([p["rate"] for p in pred]), np.array([r["rate"] for r in cal_rows]),
                np.array([r["mask"] for r in cal_rows], bool), cfg["cal_coverage"])
        metadata = dict(seed=seed, settings=cfg, actions=[list(a) for a in ACTIONS], experiment="ar_ot",
                        task_logits=cfg.get("task_logits", False), task_models=task_models,
                        calibration=calibration, checkpoint_role="LAST",
                        training_history=history, codec_backpropagation=False)
        if cfg.get("cal_coverage_extra"):
            metadata["calibration_extra"] = coverage_calibrations(
                cal_rows, pred, cfg["cal_coverage_extra"], domains=bool(cfg.get("domain_condition")))
        path = out / f"controller_{seed}.pth"
        save_checkpoint(path, model, metadata)
        models.append(load_checkpoint(path, device))
        write_json(out / f"training_{seed}.json", metadata)
        print(f"  OT controller seed {seed} trained and calibrated.", flush=True)
    return models


def run_pass(args):
    cfg = settings(args.config)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    if args.stage in ("baseline", "full") and not args.trackeval:
        raise SystemExit("--trackeval is required: OT curves are HOTA and held-out GT is scored "
                         "with the pinned TrackEval checkout")
    print(f"=== V34 OT pass | stage {args.stage} | device {device} ===", flush=True)
    print(f"Config: {args.config} | revision {cfg.get('revision')} | fix {cfg.get('fix')}", flush=True)
    groups, meta = load_ot_cohorts(args.mot_root, cfg)
    print(f"Cohorts: train {len(groups['train'])} cal {len(groups['cal'])} dev {len(groups['dev'])} "
          f"test {len(groups['test'])} MOT20 windows", flush=True)
    heads = Heads(device, "ar_ot", cfg)
    task_models = heads.hashes()
    sources = {r.id: dict(split=split, pixel_sha256=hashlib.sha256(r.rgb.tobytes()).hexdigest(),
                          frame_recipe=r.frame_recipe) for split in groups for r in groups[split]}
    write_json(out / "cohorts.json", sources)
    write_json(out / "mot20_provenance.json", dict(
        dataset=args.provenance_slug or "MOT20-02/03/01 windows", repo_commit=args.repo_commit or None,
        sequences=cohort_provenance(meta["ot"], groups),
        scope="measurement/selection inputs only; held-out GT staged separately at scoring time"))

    inputs = {}
    cache = None
    if args.stage in ("measure", "full"):
        meas = out / "measurements.json"
        if meas.is_file() and not args.fresh:
            cache = json.loads(meas.read_text(encoding="utf-8"))
            validate_cache(cache)
            settings_compatible(cache["settings"], cfg)
            inputs = torch.load(out / "controller_inputs.pth", map_location="cpu", weights_only=True)
            print(f"Reusing measured candidates from {meas.name} (no re-encoding)", flush=True)
        else:
            result = measure_ot(cfg, groups, heads, out, time_budget=args.time_budget, resume=not args.fresh)
            if result["incomplete"]:
                print("MEASUREMENT INCOMPLETE: rerun with the partial cache to resume", flush=True)
                return
            cache, inputs = result["cache"], result["inputs"]
        if args.stage == "measure":
            print(f"Measure stage complete: {len(cache['rows'])} rows for {len(cache['sources'])} windows "
                  f"(sha256 {cache['sha256'][:12]}...)", flush=True)
            return
    else:
        meas = out / "measurements.json"
        if not meas.is_file():
            raise SystemExit("baseline stage requires measurements.json (run --stage measure first "
                             "or seed the committed cache)")
        cache = json.loads(meas.read_text(encoding="utf-8"))
        validate_cache(cache)
        settings_compatible(cache["settings"], cfg)
        inputs = torch.load(out / "controller_inputs.pth", map_location="cpu", weights_only=True)
        print(f"Loaded {len(cache['rows'])} measured rows for {len(cache['sources'])} windows", flush=True)

    fit_rows = [r for r in cache["rows"] if r["split"] == "train"]
    cal_rows = [r for r in cache["rows"] if r["split"] == "cal"]
    if not fit_rows or not cal_rows:
        raise SystemExit("cache needs both train and cal rows to train the controller")
    if cfg.get("damage_units") == "relative":
        fit_rows = relative_damage(fit_rows, cfg.get("damage_floor"))
        cal_rows = relative_damage(cal_rows, cfg.get("damage_floor"))
    checkpoints = all((out / f"controller_{seed}.pth").is_file() for seed in cfg["seeds"])
    if checkpoints and not args.retrain:
        print("Reusing trained controllers from the output directory", flush=True)
        models = [load_checkpoint(out / f"controller_{seed}.pth", device) for seed in cfg["seeds"]]
    else:
        models = train_ot_models(fit_rows, cal_rows, inputs, cfg, out, device, task_models)
    for split in ("dev", "test"):
        if (out / f"{split}_tracking").exists():
            raise SystemExit(f"evaluation artifacts for {split} already exist in {out}; use a fresh output directory")
    print("Evaluating DEV and TEST MOT20 windows (shared packets + pinned TrackEval)", flush=True)
    evaluate(groups, heads, models, cfg, meta, out, Path(args.trackeval))
    write_json(out / "complete.json", dict(status="complete", experiment="ar_ot", stage=args.stage,
        cache_sha256=cache["sha256"], checkpoint_sha256=[m.checkpoint_sha256 for m in models],
        scope="dedicated MOT20 OT pass: MOT20-02 windows train/cal, MOT20-03 dev, MOT20-01 test; HOTA via pinned TrackEval"))
    print("OT pass complete", flush=True)


def parse_args():
    p = argparse.ArgumentParser(description="V34 Object Tracking (MOT20) measurement and baseline pass")
    p.add_argument("--mot-root", required=True, help="Directory containing MOT20-01/02/03 with img1 and gt")
    p.add_argument("--config", default=str(ROOT / "configs/v34_arot_r1.json"), help="Pinned arot-r1 recipe")
    p.add_argument("--out", required=True, help="Output directory (immutable cache + checkpoints + metrics)")
    p.add_argument("--stage", choices=["measure", "baseline", "full"], default="full")
    p.add_argument("--trackeval", default=None, help="Pinned TrackEval checkout (required for scoring)")
    p.add_argument("--device", default=None)
    p.add_argument("--fresh", action="store_true", help="Ignore measurement.partial.json / measurements.json")
    p.add_argument("--retrain", action="store_true", help="Retrain controllers even when checkpoints exist")
    p.add_argument("--time-budget", type=int, default=0,
                   help="Seconds before the measure stage stops gracefully with a resumable partial cache")
    p.add_argument("--provenance-slug", default="", help="Dataset slug recorded in mot20_provenance.json")
    p.add_argument("--repo-commit", default="", help="Repository commit recorded in mot20_provenance.json")
    return p.parse_args()


if __name__ == "__main__":
    run_pass(parse_args())
