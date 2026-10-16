"""Submit the scaled V34-Fix2 AR+OD pilot (K400 cleaned + COCO) to a private Kaggle GPU kernel."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/wagur1/v34_fix1.git"


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


def build_notebook_script(commit: str, slug: str, config_name: str = "v34_ar_od_scaled.json") -> str:
    return f'''import hashlib, json, os, pathlib, re, shutil, subprocess, sys, tarfile, time

WORK = pathlib.Path('/kaggle/working')
INPUT = pathlib.Path('/kaggle/input')
REPO = WORK / 'v34_fix1'
SLUG = {slug!r}
CONFIG = {config_name!r}
OUT = WORK / 'outputs' / SLUG
OUT.mkdir(parents=True, exist_ok=True)
os.environ.update(PYTHONUNBUFFERED='1', OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', PYTHONPATH=str(REPO))

def cmd(argv, cwd=None):
    print(">> Executing:", ' '.join(argv), flush=True)
    subprocess.run(argv, check=True, cwd=cwd or str(WORK))

print(f"=== V34 AR+OD scaled pilot | config {{CONFIG}} ===", flush=True)
start_time = time.time()
cmd(['git', 'clone', '-q', {REPO_URL!r}, str(REPO)])
cmd(['git', '-C', str(REPO), 'checkout', '-q', {commit!r}])
print("Cloned v34_fix1 at commit", {commit!r}, flush=True)
cmd([sys.executable, '-m', 'pip', 'install', '-q', 'pycocotools'])

# Locate K400 class folders exactly like adaptive_vcm.data.ar_plan maps them.
from torchvision.models.video import R3D_18_Weights
def canon(name):
    return re.sub(r'[^a-z0-9]+', ' ', name.lower()).strip()
mapping = {{canon(name): i for i, name in enumerate(R3D_18_Weights.KINETICS400_V1.meta['categories'])}}
class_dirs = set()
videos = 0
for path in INPUT.rglob('*.mp4'):
    category = next((p.name for p in path.parents if canon(p.name) in mapping), None)
    if category is None:
        raise SystemExit(f"unmapped video folder: {{path}}")
    class_dirs.add(path.parent)
    videos += 1
assert class_dirs, "no K400 class folders found in /kaggle/input"
ar_root = pathlib.Path(os.path.commonpath([str(p) for p in class_dirs]))
print(f"AR root: {{ar_root}} | classes: {{len(class_dirs)}} | videos: {{videos}}", flush=True)

ann_matches = list(INPUT.rglob('instances_val2017.json'))
assert ann_matches, "instances_val2017.json not found in /kaggle/input"
ann_file = str(ann_matches[0])
img_matches = [p for p in INPUT.rglob('val2017') if p.is_dir()]
assert img_matches, "val2017 image directory not found in /kaggle/input"
img_dir = str(img_matches[0])
print(f"COCO Images: {{img_dir}}", flush=True)
print(f"COCO Annotations: {{ann_file}}", flush=True)

origin = dict(origin_commit={commit!r},
              bundle_sha256=hashlib.sha256(('v34-fix2-ar-od-scaled/' + {commit!r}).encode()).hexdigest(),
              datasets='kineticscleaned+COCO2017 val2017',
              scope='exploratory V34-Fix2 AR+OD scaled pilot; shared controller recipe')
(WORK / 'origin.json').write_text(json.dumps(origin, indent=2))
print("Origin:", origin, flush=True)

cmd([sys.executable, '-m', 'adaptive_vcm.v34.runner',
     '--experiment', 'ar_od',
     '--config', str(REPO / 'configs' / {config_name!r}),
     '--ar-root', str(ar_root),
     '--od-root', img_dir,
     '--annotations', ann_file,
     '--origin', str(WORK / 'origin.json'),
     '--out', str(OUT)], cwd=str(REPO))

for name in ('test_summary.json', 'dev_summary.json', 'complete.json'):
    src = OUT / name
    if src.is_file():
        shutil.copyfile(src, WORK / name)

tgz_path = WORK / f'{{SLUG}}.tgz'
with tarfile.open(tgz_path, 'w:gz') as tar:
    tar.add(OUT, arcname=f'outputs/{{SLUG}}')

elapsed = time.time() - start_time
print(f"=== Job complete in {{elapsed:.1f}} seconds ===", flush=True)
print(f"Archive written to {{tgz_path}}", flush=True)
'''


def prepare_and_submit(account: str, slug: str, pool_path: Path, commit: str,
                       config_name: str = "v34_ar_od_scaled.json"):
    payload_dir = ROOT / "outputs" / "kaggle" / slug
    payload_dir.mkdir(parents=True, exist_ok=True)
    script_source = build_notebook_script(commit, slug, config_name)
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
        "dataset_sources": ["qktttttttttt/kineticscleaned", "awsaf49/coco-2017-dataset"],
        "competition_sources": [],
        "kernel_sources": [],
    }
    (payload_dir / "notebook.ipynb").write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    (payload_dir / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Created payload at {payload_dir.resolve()}", flush=True)
    print(f"Pushing kernel to Kaggle account {account} with NvidiaTeslaT4 accelerator...", flush=True)
    kaggle_call(["kernels", "push", "--path", str(payload_dir), "--accelerator", "NvidiaTeslaT4"], pool_path, account)
    time.sleep(5)
    status_out = kaggle_call(["kernels", "status", f"{account}/{slug}"], pool_path, account)
    print(f"Initial status: {status_out.strip()}", flush=True)


def main():
    p = argparse.ArgumentParser(description="V34-Fix2 AR+OD scaled Kaggle submitter")
    p.add_argument("mode", choices=["push", "status", "output"])
    p.add_argument("--account", default="qktttttttttt")
    p.add_argument("--slug", default="v34-fix2-ar-od-scaled")
    p.add_argument("--pool", type=Path, default=Path(r"C:\Users\Wagur1\Downloads\pool (2).json"))
    p.add_argument("--commit", default="")
    p.add_argument("--config-name", default="v34_ar_od_scaled.json")
    p.add_argument("--destination", type=Path, default=None)
    args = p.parse_args()
    if args.mode == "push":
        if not args.commit:
            commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        else:
            commit = args.commit
        prepare_and_submit(args.account, args.slug, args.pool, commit, args.config_name)
    elif args.mode == "status":
        kaggle_call(["kernels", "status", f"{args.account}/{args.slug}"], args.pool, args.account)
    else:
        destination = args.destination or (ROOT / "outputs" / "kaggle" / args.slug)
        destination.mkdir(parents=True, exist_ok=True)
        kaggle_call(["kernels", "output", f"{args.account}/{args.slug}", "--path", str(destination), "--force"], args.pool, args.account)
        print(f"Downloaded to {destination.resolve()}", flush=True)


if __name__ == "__main__":
    main()
