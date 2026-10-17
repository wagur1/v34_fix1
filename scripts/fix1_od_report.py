"""Summarize V34 OD/AR Kaggle outputs (BD-rate, arm behavior, calibration health)."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import tarfile


def find(directory: Path, name: str, tar: tarfile.TarFile | None):
    direct = directory / name
    if direct.is_file():
        return json.loads(direct.read_text(encoding="utf-8"))
    if tar is not None:
        for member in tar.getmembers():
            if member.name.endswith("/" + name):
                handle = tar.extractfile(member)
                if handle is not None:
                    return json.loads(handle.read().decode("utf-8"))
    candidate = sorted(directory.rglob(name))
    if candidate:
        return json.loads(candidate[0].read_text(encoding="utf-8"))
    raise FileNotFoundError(name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--no-rows", action="store_true",
                        help="skip the (large) per-row arm behavior section")
    args = parser.parse_args()
    directory = args.directory
    tgz = [p for p in directory.rglob("*.tgz") if p.is_file()]
    tar = tarfile.open(tgz[0]) if tgz else None
    try:
        summary = find(directory, "test_summary.json", tar)
        print(f"=== BD-rate test (qps={summary.get('qps')}, n={summary.get('count')}) ===")
        for codec, data in summary.get("results", {}).items():
            print(f"\n-- {str(codec).upper()} --")
            rows = []
            for arm, value in data.get("comparisons", {}).items():
                rows.append((arm, value.get("bd_rate_pct"), value.get("pchip_bd_rate_pct"),
                             value.get("bd_quality_pp")))
            for arm, bd, pchip, quality in sorted(rows, key=lambda r: (r[1] is None, r[1] or 0)):
                def fmt(value, scale=1.0, suffix=""):
                    return "N/A" if value is None else f"{value*scale:+.2f}{suffix}"
                print(f"{arm:>24}  BD={fmt(bd, 1, '%'):>9}  PCHIP={fmt(pchip, 1, '%'):>9}  dQ={fmt(quality, 1, 'pp'):>8}")

        if not args.no_rows:
            try:
                rows_data = find(directory, "test_rows.json", tar)
            except FileNotFoundError:
                rows_data = None
            if rows_data:
                print("\n=== Arm behavior on test rows ===")
                by_arm: dict[str, list] = {}
                for row in rows_data:
                    by_arm.setdefault(row["arm"], []).append(row)
                for arm in sorted(by_arm):
                    rows = by_arm[arm]
                    actions = Counter(r["action"] for r in rows)
                    identity = actions.get(0, 0) / len(rows)
                    top = ", ".join(f"a{a}:{n}" for a, n in actions.most_common(4))
                    calibrated = [r.get("calibrated_action") for r in rows if r.get("calibrated_action") is not None]
                    cal_identity = (sum(1 for a in calibrated if a == 0) / len(calibrated)) if calibrated else None
                    extra = f"  calibrated_nonidentity={(1-cal_identity)*100:5.1f}%" if cal_identity is not None else ""
                    print(f"{arm:>24}  identity={identity*100:5.1f}%  {top}{extra}")

        cache_sha = None
        try:
            cache_sha = find(directory, "measurements.json", tar).get("sha256")
        except FileNotFoundError:
            pass
        if cache_sha:
            print(f"\nmeasurements.json sha256 = {cache_sha}")

        print("\n=== Checkpoint calibration (bound vs tolerance) ===")
        names = sorted({m.name for m in tar.getmembers()}) if tar else []
        seen = False
        for name in [n for n in names if Path(n).name.startswith("training_")]:
            value = json.loads(tar.extractfile(name).read().decode("utf-8"))
            calibration = value["calibration"]
            risk = calibration["risk"]
            limits = value["settings"]["damage_tolerance"]
            bounds = [row[1] for row in risk if row[1] is not None]
            if not bounds:
                continue
            seen = True
            feasible = [j for j, row in enumerate(risk) if row[1] is not None and row[1] <= limits[1]]
            print(f"{Path(name).name}: seed={value['seed']} tolerance_od={limits[1]} "
                  f"feasible_actions={feasible} bound_range=[{min(bounds):.4f}..{max(bounds):.4f}]")
        if not seen:
            print("(no training_*.json inside archive; skipped)")
    finally:
        if tar is not None:
            tar.close()


if __name__ == "__main__":
    main()
