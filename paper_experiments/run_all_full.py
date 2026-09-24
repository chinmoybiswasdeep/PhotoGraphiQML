"""Fingerprint-aware, subprocess-isolated publication experiment runner."""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from publication import fingerprint, fingerprint_hash, required_artifacts, source_dirty_paths
from run_all_safe import SCRIPTS

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "results" / "logs"
STATE_PATH = ROOT / "results" / "json" / "run_all_full_state.json"


def script_id(relative_path):
    numeric = int(Path(relative_path).stem.split("_", 1)[0])
    return "R_PERF" if numeric == 49 else "R" + str(numeric)


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
    parser.add_argument("--restart", action="store_true", help="ignore matching saved fingerprints")
    parser.add_argument("--publication", action="store_true", help="refuse dirty source files")
    parser.add_argument("--filter", default=None, help="only run scripts matching this ID or path substring")
    args = parser.parse_args()

    source_dirty = source_dirty_paths()
    if args.publication and source_dirty:
        print("PUBLICATION PREFLIGHT FAILED: source files are dirty:\n" + "\n".join(source_dirty))
        sys.exit(2)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    state = {} if args.restart else load_state()

    scripts = [
        relative_path
        for relative_path, _ in SCRIPTS
        if matches_filter(relative_path, args.filter)
    ]
    if not scripts:
        print(f"No scripts matched filter {args.filter!r}")
        sys.exit(1)

    results, started = [], datetime.now(timezone.utc).isoformat()
    start_all = time.perf_counter()
    for relative_path in scripts:
        script = ROOT / relative_path
        current_fingerprint = fingerprint(script)
        previous = state.get(relative_path, {})
        artifacts_ok = all(
            path.is_file() for path in required_artifacts(script_id(relative_path), relative_path)
        )
        if (
            not args.restart
            and previous.get("execution_status") == "completed"
            and previous.get("fingerprint") == current_fingerprint
            and artifacts_ok
        ):
            reason = "matching fingerprint and complete artifacts"
            print(f"RESUMED  {relative_path} ({reason})")
            results.append({"script": relative_path, "execution_status": "resumed", "reason": reason, "seconds": 0.0})
            continue
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
        execution_status = "completed" if proc.returncode == 0 else "failed"
        reason = "restart requested" if args.restart else "new or invalidated fingerprint/artifacts"
        record = {
            "script": relative_path,
            "execution_status": execution_status,
            "reason": reason,
            "seconds": seconds,
            "returncode": proc.returncode,
            "log": str(log_path.relative_to(ROOT)),
        }
        state[relative_path] = {
            "fingerprint": current_fingerprint,
            "fingerprint_sha256": fingerprint_hash(current_fingerprint),
            **record,
        }
        print(f"{execution_status.upper()}  {relative_path} ({seconds:.1f}s; {reason})")
        results.append(record)
        save_state(state)

    total_seconds = time.perf_counter() - start_all
    passed = sum(1 for r in results if r["execution_status"] == "completed")
    failed = sum(1 for r in results if r["execution_status"] == "failed")
    resumed = sum(1 for r in results if r["execution_status"] == "resumed")
    print(
        f"\n=== run_all_full summary ===\npassed={passed} failed={failed} resumed={resumed} total_wall_seconds={total_seconds:.1f}"
    )

    # Status generation consumes the machine-readable summary, so make a
    # provisional version available before the publication finalizers run.
    summary_path = ROOT / "results" / "json" / "run_all_full_summary.json"
    summary_path.write_text(json.dumps({
        "schema_version": 2, "publication_mode": args.publication,
        "source_dirty_paths": source_dirty, "started_utc": started,
        "completed_utc": datetime.now(timezone.utc).isoformat(), "results": results,
        "completed": passed, "resumed": resumed, "failed": failed,
        "total_wall_seconds": total_seconds,
    }, indent=2), encoding="utf-8")
    finalizers = []
    if args.publication and failed == 0:
        for relative_path in ("generate_tables.py", "build_notebook.py", "build_manifest.py", "generate_status.py"):
            script = ROOT / relative_path
            process = subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True)
            log_path = LOG_DIR / f"publication_{script.stem}.log"
            log_path.write_text(process.stdout + "\n--- stderr ---\n" + process.stderr, encoding="utf-8")
            finalizers.append({"step": relative_path, "returncode": process.returncode, "log": str(log_path.relative_to(ROOT))})
        process = subprocess.run([sys.executable, "-m", "pytest", "tests/paper_experiments", "-q"], cwd=ROOT.parent, capture_output=True, text=True)
        log_path = LOG_DIR / "publication_consistency_tests.log"
        log_path.write_text(process.stdout + "\n--- stderr ---\n" + process.stderr, encoding="utf-8")
        finalizers.append({"step": "tests/paper_experiments", "returncode": process.returncode, "log": str(log_path.relative_to(ROOT))})
        failed += sum(step["returncode"] != 0 for step in finalizers)

    summary_path.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "publication_mode": args.publication,
                "source_dirty_paths": source_dirty,
                "started_utc": started,
                "completed_utc": datetime.now(timezone.utc).isoformat(),
                "results": results,
                "finalizers": finalizers,
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
