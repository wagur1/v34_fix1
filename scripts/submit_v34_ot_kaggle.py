"""Submit the V34 MOT20 OT measurement/baseline pass to a private Kaggle GPU kernel."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/wagur1/v34_fix1.git"
TRACKEVAL_URL = "https://github.com/JonathonLuiten/TrackEval.git"


def trackeval_pin():
    """Single source of truth for the pinned TrackEval checkout."""
    match = re.search(r"TRACKEVAL_COMMIT\s*=\s*'([0-9a-f]{40})'",
                      (ROOT / "adaptive_vcm" / "v32" / "tracking.py").read_text(encoding="utf-8"))
    if not match:
        raise ValueError("TRACKEVAL_COMMIT pin not found")
    return match.group(1)


def pool_environment(path: Path, account: str):
    pool = json.loads(path.read_text(encoding="utf-8-sig"))
    value = pool[account]
    environment = dict(os.environ)
    for name in ("KAGGLE_API_TOKEN", "KAGGLE_USERNAME", "KAGGLE_KEY"):
        environment.pop(name, None)
    if isinstance(value, str):
        environment["KAGGLE_API_TOKEN"] = value
        secret = value
    elif isinstance(value, dict) and value.get("key"):
        secret = value["key"]
        environment["KAGGLE_USERNAME"] = value.get("username", account)
        environment["KAGGLE_KEY"] = secret
    else:
        raise ValueError("unsupported pool credential format")
    return environment, secret


def kaggle_call(arguments, pool, account):
    environment, secret = pool_environment(pool, account)
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONIOENCODING"] = "utf-8"
    command = [sys.executable, "-m", "kaggle", *arguments]
    result = subprocess.run(command, env=environment, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=600)
    safe_output = (result.stdout + result.stderr).replace(secret, "[REDACTED]")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(safe_output, end="" if safe_output.endswith("\n") else "\n")
    if result.returncode:
        raise RuntimeError(f"Kaggle command failed (exit {result.returncode}); no success inferred")
    return safe_output


def build_notebook_script(commit: str, slug: str, stage: str, config_name: str, time_budget: int,
                          dataset_slug: str) -> str:
    pin = trackeval_pin()
    return f'''import os, pathlib, shutil, subprocess, sys, tarfile, time

WORK = pathlib.Path('/kaggle/working')
INPUT = pathlib.Path('/kaggle/input')
REPO = WORK / 'v34_fix1'
TRACKEVAL = WORK / 'TrackEval'
SLUG = {repr(slug)}
STAGE = {repr(stage)}
CONFIG = {repr(config_name)}
TIME_BUDGET = {time_budget}
OUT = WORK / 'outputs' / SLUG
OUT.mkdir(parents=True, exist_ok=True)
os.environ.update(PYTHONUNBUFFERED='1', PYTHONPATH=str(REPO))

def cmd(argv, cwd=None):
    print(">> Executing:", ' '.join(argv), flush=True)
    subprocess.run(argv, check=True, cwd=cwd or str(WORK))

print("=== V34 MOT20 OT pass | stage " + STAGE + " ===", flush=True)
start_time = time.time()

cmd(['git', 'clone', '-q', {REPO_URL!r}, str(REPO)])
cmd(['git', '-C', str(REPO), 'checkout', '-q', {commit!r}])
print("HEAD is", subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'],
      capture_output=True, text=True).stdout.strip(), flush=True)

cmd([sys.executable, '-m', 'pip', 'install', '-q', 'supervision==0.27.0'])

matches = [p for p in INPUT.rglob('seqinfo.ini') if p.parent.name in ('MOT20-01', 'MOT20-02', 'MOT20-03')]
assert matches, 'MOT20 seqinfo.ini not found under /kaggle/input'
mot_root = None
for candidate in sorted({{str(p.parent.parent) for p in matches}}):
    if all((pathlib.Path(candidate) / name / 'seqinfo.ini').is_file()
           for name in ('MOT20-01', 'MOT20-02', 'MOT20-03')):
        mot_root = candidate
        break
assert mot_root, 'MOT20-01/02/03 not colocated under one root'
print("MOT20 root:", mot_root, flush=True)

if STAGE in ('baseline', 'full'):
    cmd(['git', 'clone', '-q', {TRACKEVAL_URL!r}, str(TRACKEVAL)])
    cmd(['git', '-C', str(TRACKEVAL), 'checkout', '-q', {pin!r}])

# Reuse the committed measurement cache when present: baseline runs only
# retrain and re-evaluate and never repeat the codec roundtrips. A committed
# partial cache lets a budget-stopped measure kernel resume instead of restarting.
cache_dir = REPO / 'caches' / 'v34_ot_mot20'
if cache_dir.is_dir():
    for name in ('measurements.json', 'measurements.partial.json', 'controller_inputs.pth'):
        source = cache_dir / name
        if source.is_file():
            shutil.copyfile(source, OUT / name)
            print("Seeded output with cached", name, flush=True)

argv = [sys.executable, str(REPO / 'scripts' / 'run_v34_ot.py'),
        '--mot-root', mot_root, '--config', str(REPO / 'configs' / CONFIG), '--out', str(OUT),
        '--stage', STAGE, '--time-budget', str(TIME_BUDGET),
        '--provenance-slug', {dataset_slug!r}, '--repo-commit', {commit!r}]
if STAGE in ('baseline', 'full'):
    argv += ['--trackeval', str(TRACKEVAL)]
cmd(argv, cwd=str(REPO))

for name in ('test_summary.json', 'dev_summary.json', 'complete.json', 'incomplete.json'):
    src = OUT / name
    if src.is_file():
        shutil.copyfile(src, WORK / name)

tgz_path = WORK / f'{{SLUG}}.tgz'
with tarfile.open(tgz_path, 'w:gz') as tar:
    tar.add(OUT, arcname=f'outputs/{{SLUG}}')

print(f"=== Job complete in {{time.time() - start_time:.1f}} seconds ===", flush=True)
print("Archive written to", tgz_path, flush=True)
'''


def prepare_and_submit(account: str, slug: str, pool_path: Path, commit: str, stage: str,
                       config_name: str, time_budget: int, dataset_slug: str):
    payload_dir = ROOT / "outputs" / "kaggle" / slug
    payload_dir.mkdir(parents=True, exist_ok=True)
    script_source = build_notebook_script(commit, slug, stage, config_name, time_budget, dataset_slug)
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
        "cells": [{"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                   "source": script_source.splitlines(True)}],
    }
    metadata = {
        "id": f"{account}/{slug}",
        "title": slug,
        "code_file": "notebook.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_internet": True,
        "dataset_sources": [dataset_slug],
        "competition_sources": [],
        "kernel_sources": [],
    }
    (payload_dir / "notebook.ipynb").write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    (payload_dir / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Created payload at {payload_dir.resolve()}", flush=True)
    print(f"Pushing kernel to Kaggle account {account} (stage {stage})...", flush=True)
    kaggle_call(["kernels", "push", "--path", str(payload_dir), "--accelerator", "NvidiaTeslaT4"], pool_path, account)
    time.sleep(5)
    status_out = kaggle_call(["kernels", "status", f"{account}/{slug}"], pool_path, account)
    print(f"Initial status: {status_out.strip()}", flush=True)


def main():
    p = argparse.ArgumentParser(description="V34 MOT20 OT Kaggle submitter")
    p.add_argument("mode", choices=["push", "status", "output"])
    p.add_argument("--account", required=True)
    p.add_argument("--slug", default="v34-ot-measure")
    p.add_argument("--stage", choices=["measure", "baseline", "full"], default="measure")
    p.add_argument("--pool", type=Path, default=Path(r"C:\Users\Wagur1\Downloads\pool (2).json"))
    p.add_argument("--commit", default="")
    p.add_argument("--config-name", default="v34_arot_r1.json")
    p.add_argument("--dataset-slug", default="ismailelbouknify/mot-20")
    p.add_argument("--time-budget", type=int, default=36000)
    p.add_argument("--destination", type=Path, default=None)
    args = p.parse_args()
    if args.mode == "push":
        commit = args.commit or subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                               capture_output=True, text=True, check=True).stdout.strip()
        prepare_and_submit(args.account, args.slug, args.pool, commit, args.stage,
                           args.config_name, args.time_budget, args.dataset_slug)
    elif args.mode == "status":
        kaggle_call(["kernels", "status", f"{args.account}/{args.slug}"], args.pool, args.account)
    else:
        destination = args.destination or (ROOT / "outputs" / "kaggle" / args.slug)
        destination.mkdir(parents=True, exist_ok=True)
        kaggle_call(["kernels", "output", f"{args.account}/{args.slug}", "--path", str(destination), "--force"],
                    args.pool, args.account)
        print(f"Downloaded to {destination.resolve()}", flush=True)


if __name__ == "__main__":
    main()
