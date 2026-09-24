"""Generate an unambiguous evidence-status report from machine-readable runs."""

from __future__ import annotations

import json
from pathlib import Path

from publication import ROOT, git, source_dirty_paths


def main() -> None:
    summary_path = ROOT / "results" / "json" / "run_all_full_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else None
    commit = git("rev-parse", "HEAD")
    lines = ["# Suite execution status", "", "## Current source fingerprint", "", f"- Commit: `{commit}`", f"- Branch: `{git('branch', '--show-current')}`", f"- Source files dirty (generated evidence excluded): `{bool(source_dirty_paths())}`", f"- Dirty source paths: `{source_dirty_paths()}`", ""]
    if not summary or summary.get("source_dirty_paths"):
        lines += ["## Current publication evidence", "", "No clean-source publication run at this source fingerprint is accepted as final evidence.", "Historical or dirty-source artifacts remain inspectable but are not final publication evidence.", ""]
    else:
        lines += ["## Current publication run", "", f"- Started: `{summary['started_utc']}`", f"- Completed: `{summary['completed_utc']}`", f"- Completed: `{summary['completed']}`", f"- Resumed: `{summary['resumed']}`", f"- Failed: `{summary['failed']}`", ""]
    lines += ["## Outcome interpretation", "", "- Positive: only results with a completed execution and an explicit positive scientific outcome.", "- Negative: retained explicitly (notably R48 physical-training instability).", "- Descriptive: runtime, scaling, and comparison studies do not imply performance success.", "- Unsupported: arbitrary-angle physical XY, general physical MuTA, native CVMuTA, soft flow decoding, and entangled physical inputs remain unsupported unless a current experiment demonstrates otherwise.", "", "## Remaining blockers", "", "- A clean-source fingerprint-aware `--publication` run has not yet completed.", "- Heavy physical experiments must be executed by that run; no skip is accepted in publication mode."]
    (ROOT / "STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Wrote paper_experiments/STATUS.md")


if __name__ == "__main__":
    main()
