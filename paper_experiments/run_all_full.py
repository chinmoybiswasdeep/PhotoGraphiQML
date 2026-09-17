"""Run the complete experiment suite (including heavy physical-simulation
experiments), with resumable execution, ID/category filtering, and full
stdout/stderr logs.

Usage:
    python run_all_full.py                  # run everything, resuming completed scripts
    python run_all_full.py --restart        # ignore prior completion, rerun everything
    python run_all_full.py --filter R4      # only run scripts whose ID matches (R4, R40-R48, ...)
    python run_all_full.py --filter physical_statistics   # only run scripts in a category directory
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from run_all_safe import (
    SCRIPTS as SAFE_SCRIPTS,  # reuse the same ordered list; nothing is skipped here
)

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "results" / "logs"
STATE_PATH = ROOT / "results" / "json" / "run_all_full_state.json"


def script_id(relative_path):
    name = Path(relative_path).stem
    return name.split("_", 1)[0].upper()


def matches_filter(relative_path, pattern):
    if pattern is None:
        return True
    pattern = pattern.lower()
    return pattern in relative_path.lower() or pattern.upper() == script_id(relative_path)


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {}


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--restart", action="store_true", help="ignore prior completion state and rerun everything"
    )
    parser.add_argument(
        "--filter", default=None, help="only run scripts matching this ID or path substring"
    )
    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    state = {} if args.restart else load_state()

    scripts = [
        relative_path
        for relative_path, _ in SAFE_SCRIPTS
        if matches_filter(relative_path, args.filter)
    ]
    if not scripts:
        print(f"No scripts matched filter {args.filter!r}")
        sys.exit(1)

    results = []
    start_all = time.perf_counter()
    for relative_path in scripts:
        if state.get(relative_path) == "passed":
            print(f"RESUME-SKIP  {relative_path} (already passed)")
            results.append({"script": relative_path, "status": "resumed", "seconds": 0.0})
            continue
        script = ROOT / relative_path
        log_path = LOG_DIR / (Path(relative_path).stem + ".log")
        start = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(script)], cwd=str(script.parent), capture_output=True, text=True
        )
        seconds = time.perf_counter() - start
        log_path.write_text(
            f"$ {sys.executable} {script}\n\n--- stdout ---\n{proc.stdout}\n\n--- stderr ---\n{proc.stderr}\n",
            encoding="utf-8",
        )
        if proc.returncode == 0:
            print(f"PASS  {relative_path} ({seconds:.1f}s)")
            state[relative_path] = "passed"
            results.append({"script": relative_path, "status": "passed", "seconds": seconds})
        else:
            print(f"FAIL  {relative_path} ({seconds:.1f}s) -- see {log_path}")
            state[relative_path] = "failed"
            results.append({"script": relative_path, "status": "FAILED", "seconds": seconds})
        save_state(state)

    total_seconds = time.perf_counter() - start_all
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    resumed = sum(1 for r in results if r["status"] == "resumed")
    print(
        f"\n=== run_all_full summary ===\npassed={passed} failed={failed} resumed={resumed} total_wall_seconds={total_seconds:.1f}"
    )

    summary_path = ROOT / "results" / "json" / "run_all_full_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "results": results,
                "passed": passed,
                "failed": failed,
                "resumed": resumed,
                "total_wall_seconds": total_seconds,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
