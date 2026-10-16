"""Unattended overnight chain for V34-Fix2 on Kaggle.

Flow:
 1. wait for the running fix1 OD kernel (wagur124705/v34-fix1-od-coco)
 2. download outputs, extract measurements.json + controller_inputs.pth into caches/v34_od_coco
 3. commit + push the reusable measurement cache
 4. submit the three Fix2 OD variants (rank / huber / forced) on pool accounts
 5. submit the scaled Fix2 AR+OD pilot (K400 cleaned + COCO)
 6. monitor, download and analyze every kernel; write a Vietnamese morning report

The script is append-only with respect to its report, so a crash still leaves the
partial timeline on disk. Restarting it is safe: an already-committed cache and
already-submitted kernels are detected and skipped.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_POOL = Path(r"C:\Users\Wagur1\Downloads\pool (2).json")
DEFAULT_REPORT = Path(r"C:\Users\Wagur1\v34-night-report.md")
DEFAULT_LOG = Path(r"C:\Users\Wagur1\AppData\Local\Temp\opencode\ap_analysis\autopilot_v34.log")

FIX1 = dict(account="wagur124705", slug="v34-fix1-od-coco", kind="fix1")
VARIANTS = [
    dict(account="tranthihongdieu", slug="v34-fix2-od-rank", config="v34.json", kind="variant"),
    dict(account="hieusunday0412", slug="v34-fix2-od-huber", config="v34_fix2_huber.json", kind="variant"),
    dict(account="nguyenhoanglan1232", slug="v34-fix2-od-forced", config="v34_fix2_forced.json", kind="variant"),
]
VARIANT_SPARES = ["ngynanhthuw", "linhowi05", "vtk269"]
AR = dict(account="dngbolm", slug="v34-fix2-ar-od-scaled", kind="ar")
COUNTS = {"train": 192, "cal": 64, "dev": 48, "test": 256}
TERMINAL = ("COMPLETE", "ERROR", "CANCEL")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def status_word(text: str) -> str:
    upper = text.upper()
    match = re.search(r"KERNELWORKERSTATUS\.([A-Z_]+)", upper)
    raw = match.group(1) if match else upper
    for key in TERMINAL:
        if key in raw:
            return key
    for key in ("RUNNING", "QUEUED"):
        if key in raw:
            return key
    return "UNKNOWN"


class Night:
    def __init__(self, pool: Path, report: Path, log_path: Path):
        self.pool = pool
        self.report = report
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.submit_od = load_module("autopilot_submit_od", ROOT / "scripts" / "submit_fix1_od_kaggle.py")
        self.submit_ar = load_module("autopilot_submit_ar", ROOT / "scripts" / "submit_v34_ar_kaggle.py")

    # ---------------------------------------------------------------- logging
    def log(self, message: str, to_report: bool = False):
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{stamp}] {message}"
        print(line, flush=True)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        if to_report:
            self.report.parent.mkdir(parents=True, exist_ok=True)
            with self.report.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")

    def section(self, title: str):
        with self.report.open("a", encoding="utf-8") as handle:
            handle.write(f"\n## {title}\n\n")

    def note(self, text: str):
        with self.report.open("a", encoding="utf-8") as handle:
            handle.write(text.rstrip() + "\n")

    def begin_report(self):
        self.report.write_text(
            "# Báo cáo đêm V34-Fix2 (tự động)\n\n"
            f"Bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M')} (giờ máy)\n\n"
            "Chuỗi: fix1 OD (đang chạy) → cache đo đạc → 3 biến thể Fix2 OD "
            "(rank/huber/forced) → AR+OD scaled pilot → báo cáo này.\n"
            "Log thô: `" + str(self.log_path) + "`\n",
            encoding="utf-8",
        )

    # ------------------------------------------------------------- kaggle io
    def run_kaggle(self, module, account: str, arguments, timeout: int = 3600) -> str:
        environment, secret = module.pool_environment(self.pool, account)
        environment["PYTHONUTF8"] = "1"
        environment["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable, "-m", "kaggle", *arguments],
            env=environment, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
        output = (result.stdout + result.stderr).replace(secret, "[REDACTED]")
        print(output, end="" if output.endswith("\n") else "\n", flush=True)
        if result.returncode:
            raise RuntimeError(f"kaggle command failed (exit {result.returncode}): {' '.join(arguments)}")
        return output

    def kernel_status(self, module, target) -> str:
        try:
            text = self.run_kaggle(module, target["account"],
                                   ["kernels", "status", f"{target['account']}/{target['slug']}"],
                                   timeout=300)
        except Exception as error:
            self.log(f"status {target['slug']}: truy vấn lỗi ({error})")
            return "UNKNOWN"
        return status_word(text)

    def kernel_exists(self, module, target) -> bool:
        try:
            self.run_kaggle(module, target["account"],
                            ["kernels", "status", f"{target['account']}/{target['slug']}"], timeout=300)
            return True
        except Exception:
            return False

    def download(self, module, target, timeout: int = 5400) -> bool:
        destination = ROOT / "outputs" / "kaggle" / target["slug"]
        destination.mkdir(parents=True, exist_ok=True)
        try:
            self.run_kaggle(module, target["account"],
                            ["kernels", "output", f"{target['account']}/{target['slug']}",
                             "--path", str(destination), "--force"], timeout=timeout)
            return True
        except Exception as error:
            self.log(f"tải output {target['slug']} thất bại: {error}")
            return False

    # ------------------------------------------------------------- lifecycle
    def wait_single(self, target, module, hours: float, poll_minutes: float = 5.0,
                    on_error=None, heartbeat_minutes: float = 45.0):
        deadline = time.time() + hours * 3600
        last_heartbeat = time.time()
        while True:
            status = self.kernel_status(module, target)
            if status in TERMINAL:
                target["status"] = status
                self.log(f"{target['slug']}: {status} ({target['account']})", to_report=True)
                if status == "ERROR" and on_error is not None:
                    replacement = on_error(target)
                    if replacement is not None:
                        module, target = replacement
                        deadline = time.time() + hours * 3600
                        continue
                return status
            if status != target.get("last_status"):
                target["last_status"] = status
                self.log(f"{target['slug']}: {status} ({target['account']})", to_report=True)
            if time.time() >= deadline:
                target["status"] = "TIMEOUT"
                self.log(f"{target['slug']}: quá hạn chờ {hours:.0f}h, bỏ theo dõi", to_report=True)
                return "TIMEOUT"
            if (time.time() - last_heartbeat) >= heartbeat_minutes * 60:
                last_heartbeat = time.time()
                self.log(f"heartbeat: {target['slug']} vẫn {target.get('last_status', status)}")
            time.sleep(poll_minutes * 60)

    def submit_od_variant(self, target, commit: str) -> bool:
        try:
            self.submit_od.prepare_and_submit(target["account"], target["slug"], self.pool, commit,
                                              COUNTS, target["config"])
            return True
        except Exception as error:
            self.log(f"submit {target['slug']} trên {target['account']} lỗi: {error}", to_report=True)
            return False

    def submit_ar(self, target, commit: str) -> bool:
        try:
            self.submit_ar.prepare_and_submit(target["account"], target["slug"], self.pool, commit)
            return True
        except Exception as error:
            self.log(f"submit {target['slug']} trên {target['account']} lỗi: {error}", to_report=True)
            return False

    # ----------------------------------------------------------- extraction
    def extract_from_tar(self, target_dir: Path, select):
        tgz_files = sorted((p for p in target_dir.rglob("*.tgz") if p.is_file()),
                           key=lambda p: p.stat().st_size, reverse=True)
        if not tgz_files:
            self.log(f"không thấy .tgz trong {target_dir}")
            return []
        extracted = []
        with tarfile.open(tgz_files[0]) as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                base = Path(member.name).name
                for matcher, out_dir in select:
                    if matcher(base):
                        out_dir.mkdir(parents=True, exist_ok=True)
                        handle = tar.extractfile(member)
                        if handle is None:
                            continue
                        (out_dir / base).write_bytes(handle.read())
                        extracted.append(f"{base} -> {out_dir}")
                        break
        return extracted

    def analyse(self, slug: str, with_rows: bool) -> str:
        directory = ROOT / "outputs" / "kaggle" / slug
        command = [sys.executable, str(ROOT / "scripts" / "fix1_od_report.py"), str(directory)]
        if not with_rows:
            command.append("--no-rows")
        result = subprocess.run(command, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=3600, cwd=str(ROOT))
        output = (result.stdout or "") + (("\n[stderr]\n" + result.stderr) if result.stderr else "")
        analysis_file = ROOT / "results" / slug / "analysis.txt"
        analysis_file.parent.mkdir(parents=True, exist_ok=True)
        analysis_file.write_text(output, encoding="utf-8")
        return output

    # ------------------------------------------------------------------ git
    def git(self, *arguments, check=True) -> subprocess.CompletedProcess:
        result = subprocess.run(["git", "-C", str(ROOT), *arguments],
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
        if check and result.returncode:
            raise RuntimeError(f"git {' '.join(arguments)} failed: {result.stderr.strip()}")
        return result

    def git_push(self, attempts: int = 5) -> bool:
        for attempt in range(1, attempts + 1):
            result = self.git("push", check=False)
            if result.returncode == 0:
                self.log(f"git push OK (lần {attempt})")
                return True
            result = self.git("push", "origin", "HEAD:main", check=False)
            if result.returncode == 0:
                self.log(f"git push origin HEAD:main OK (lần {attempt})")
                return True
            self.log(f"git push lỗi lần {attempt}: {result.stderr.strip()[:300]}")
            time.sleep(60)
        return False


def build_summary_table(night: Night, slugs) -> str:
    arms_wanted = ("selected_303401", "selected_ensemble", "calibrated_303401", "calibrated_ensemble",
                   "forced_303401", "fixed")
    lines = ["| Run | Codec | arm | BD-rate | PCHIP |", "|---|---|---|---:|---:|"]
    for slug in slugs:
        summary_path = ROOT / "results" / slug / "test_summary.json"
        if not summary_path.is_file():
            lines.append(f"| {slug} | - | (no test_summary) | - | - |")
            continue
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except Exception as error:
            lines.append(f"| {slug} | - | (unreadable: {error}) | - | - |")
            continue
        for codec, data in summary.get("results", {}).items():
            comparisons = data.get("comparisons", {})
            present = [arm for arm in arms_wanted if arm in comparisons]
            for arm in present:
                value = comparisons[arm]
                bd = value.get("bd_rate_pct")
                pchip = value.get("pchip_bd_rate_pct")
                fmt = lambda v: "N/A" if v is None else f"{v:+.2f}%"
                lines.append(f"| {slug} | {codec} | `{arm}` | {fmt(bd)} | {fmt(pchip)} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="V34-Fix2 overnight autopilot")
    parser.add_argument("--pool", type=Path, default=DEFAULT_POOL)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--fix1-hours", type=float, default=8.0)
    parser.add_argument("--later-hours", type=float, default=8.0)
    parser.add_argument("--poll-minutes", type=float, default=5.0)
    args = parser.parse_args()

    night = Night(args.pool, args.report, args.log)
    night.begin_report()
    night.log("=== Autopilot V34-Fix2 bắt đầu ===", to_report=True)

    cache_dir = ROOT / "caches" / "v34_od_coco"
    fix1_results = ROOT / "results" / "v34_fix1_od_coco"
    cache_committed = night.git("ls-files", "--error-unmatch", "caches/v34_od_coco/measurements.json",
                                check=False).returncode == 0

    # ---------------------------------------------------------------- stage 1: fix1
    night.section("1. Kernel fix1 OD (nguồn cache)")
    fix1_status = "COMPLETE" if cache_committed else None
    if cache_committed:
        night.note("Cache fix1 đã có trong git; bỏ qua tải output fix1.")
    if fix1_status is None:
        fix1_status = night.wait_single(FIX1, night.submit_od, args.fix1_hours,
                                        poll_minutes=args.poll_minutes)
    if fix1_status != "COMPLETE":
        night.note(f"fix1 kết thúc với trạng thái {fix1_status}; không thể tiếp tục chuỗi biến thể.")
        night.log("Dừng chuỗi do fix1 không COMPLETE", to_report=True)
        return
    if not cache_committed:
        if not night.download(night.submit_od, FIX1):
            night.log("Tải fix1 thất bại", to_report=True)
            return
        extracted = night.extract_from_tar(ROOT / "outputs" / "kaggle" / FIX1["slug"], [
            (lambda b: b in ("measurements.json", "controller_inputs.pth"), cache_dir),
            (lambda b: b in ("OD_REPORT.md", "test_summary.json", "dev_summary.json",
                             "train_oracle.json", "complete.json"), fix1_results),
            (lambda b: b.startswith("training_") and b.endswith(".json"), fix1_results),
        ])
        night.log(f"giải nén fix1: {extracted}")
        if not (cache_dir / "measurements.json").is_file():
            night.note("Không tìm thấy measurements.json trong output fix1; dừng chuỗi.")
            return
        night.git("add", "caches/v34_od_coco", "results/v34_fix1_od_coco")
        commit = night.git("commit", "-m", "Night autopilot: fix1 OD measured cache + summaries", check=False)
        if commit.returncode:
            night.log(f"git commit: {commit.stdout.strip()} {commit.stderr.strip()}")
        if not night.git_push():
            night.note("CẢNH BÁO: git push thất bại — các biến thể sẽ tự đo lại từ đầu (chậm hơn).")
    head = night.git("rev-parse", "HEAD").stdout.strip()
    night.log(f"HEAD để chạy biến thể: {head}", to_report=True)

    # --------------------------------------------------- stage 2: fix1 analysis
    night.section("2. Phân tích fix1 OD")
    try:
        output = night.analyse(FIX1["slug"], with_rows=True)
        night.note("```\n" + output.strip() + "\n```")
    except Exception as error:
        night.note(f"phân tích fix1 lỗi: {error}")
    try:
        fix1_summary = json.loads((ROOT / "results" / FIX1["slug"] / "test_summary.json").read_text(encoding="utf-8"))
        night.note(f"measurements sha256: `{json.loads((cache_dir / 'measurements.json').read_text(encoding='utf-8'))['sha256']}`")
        night.note(f"dev: {fix1_summary.get('split')} | count test: {fix1_summary.get('count')}")
    except Exception as error:
        night.log(f"đọc summary fix1 lỗi: {error}")

    # ------------------------------------------------- stage 3: submit variants
    night.section("3. Biến thể Fix2 OD")
    submitted = []
    spare_pool = list(VARIANT_SPARES)
    for target in VARIANTS:
        if night.kernel_exists(night.submit_od, target):
            night.log(f"{target['slug']}: đã submit từ trước trên {target['account']}")
        else:
            night.log(f"submit {target['slug']} trên {target['account']} (config {target['config']})")
            if not night.submit_od_variant(target, head):
                if spare_pool:
                    target["account"] = spare_pool.pop(0)
                    night.log(f"thử lại {target['slug']} trên {target['account']}")
                    night.submit_od_variant(target, head)
        submitted.append(target)

    # ------------------------------------------------------- stage 4: submit AR
    night.section("4. AR+OD scaled pilot")
    if night.kernel_exists(night.submit_ar, AR):
        night.log(f"{AR['slug']}: đã submit từ trước trên {AR['account']}")
    else:
        night.log(f"submit {AR['slug']} trên {AR['account']} (K400 cleaned + COCO)")
        night.submit_ar(AR, head)

    # ------------------------------------------------------ stage 5: monitoring
    night.section("5. Theo dõi + tải + phân tích")
    for target in submitted:
        def make_on_error(spare_pool=spare_pool, target=target):
            state = {"used": False}

            def on_error(t):
                if state["used"] or not spare_pool:
                    return None
                state["used"] = True
                t["account"] = spare_pool.pop(0)
                night.log(f"{t['slug']}: lỗi — thử lại trên {t['account']}", to_report=True)
                if not night.submit_od_variant(t, head):
                    return None
                return (night.submit_od, t)

            return on_error

        status = night.wait_single(target, night.submit_od, args.later_hours,
                                   poll_minutes=args.poll_minutes, on_error=make_on_error())
        if status in TERMINAL:
            module = night.submit_od
            night.download(module, target)
            extracted = night.extract_from_tar(ROOT / "outputs" / "kaggle" / target["slug"], [
                (lambda b: b in ("OD_REPORT.md", "test_summary.json", "dev_summary.json",
                                 "train_oracle.json", "complete.json"), ROOT / "results" / target["slug"]),
                (lambda b: b.startswith("training_") and b.endswith(".json"), ROOT / "results" / target["slug"]),
            ])
            night.log(f"{target['slug']}: giải nén {len(extracted)} tệp")
            if (ROOT / "outputs" / "kaggle" / target["slug"]).is_dir():
                try:
                    analysis = night.analyse(target["slug"], with_rows=False)
                    night.note(f"### {target['slug']}\n\n```\n" + analysis.strip() + "\n```")
                except Exception as error:
                    night.note(f"### {target['slug']}\n\nphân tích lỗi: {error}")
    # AR last (its output is larger)
    if AR.get("status") not in ("COMPLETE",):
        status = night.wait_single(AR, night.submit_ar, args.later_hours, poll_minutes=args.poll_minutes)
        AR["status"] = status
    if AR.get("status") in TERMINAL:
        night.download(night.submit_ar, AR)
        night.extract_from_tar(ROOT / "outputs" / "kaggle" / AR["slug"], [
            (lambda b: b in ("test_summary.json", "dev_summary.json", "complete.json",
                             "origin.json", "train_oracle.json"), ROOT / "results" / AR["slug"]),
            (lambda b: b.startswith("training_") and b.endswith(".json"), ROOT / "results" / AR["slug"]),
        ])
        try:
            analysis = night.analyse(AR["slug"], with_rows=False)
            night.note(f"### {AR['slug']}\n\n```\n" + analysis.strip() + "\n```")
        except Exception as error:
            night.note(f"### {AR['slug']}\n\nphân tích lỗi: {error}")

    # ------------------------------------------------------------- stage 6: report
    slugs = [FIX1["slug"]] + [t["slug"] for t in submitted] + [AR["slug"]]
    night.section("6. Tổng hợp BD-rate (các arm chính)")
    night.note(build_summary_table(night, slugs))
    cache_sha = None
    try:
        cache_sha = json.loads((cache_dir / "measurements.json").read_text(encoding="utf-8"))["sha256"]
    except Exception:
        pass
    night.note(f"\ncache sha256 = `{cache_sha}` — mọi biến thể tái sử dụng cùng cache này (đối chiếu `measurements.json sha256` trong log từng biến thể).")
    night.section("7. Trạng thái kernel cuối")
    for target in [FIX1] + submitted + [AR]:
        night.note(f"- `{target['account']}/{target['slug']}`: **{target.get('status', 'UNKNOWN')}**  "
                   f"https://www.kaggle.com/code/{target['account']}/{target['slug']}")
    shutil.copyfile(night.report, ROOT / "results" / "night_report.md")
    night.git("add", "results", check=False)
    night.git("commit", "-m", "Night autopilot: variant results + report", check=False)
    night.git_push(attempts=2)
    night.log("=== Autopilot hoàn tất ===", to_report=True)


if __name__ == "__main__":
    main()
