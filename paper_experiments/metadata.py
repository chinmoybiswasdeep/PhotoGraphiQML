"""Environment/provenance metadata recorded alongside every experiment's output.

Every script calls ``metadata.collect()`` once and writes the result as a
companion ``<name>.metadata.json`` file via ``common.write_metadata``. This is
descriptive provenance only: it does not certify reproducibility on a
different machine, only records the conditions a result was produced under.

Oracle/reference-independence classes (declared per-experiment; see
paper_experiments/README.md and section 5 of the manuscript-experiments task):
"""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_PACKAGES = (
    "photographiqml",
    "photographiq",
    "mentpy",
    "piquasso",
    "numpy",
    "scipy",
    "networkx",
    "matplotlib",
    "scikit-learn",
)

ORACLE_CLASSES = {
    "A": "independent analytic oracle",
    "B": "independent external implementation",
    "C": "external implementation with explicitly identified shared inputs/resources",
    "D": "independent code path or cross-backend comparison",
    "E": "structural/self-consistency test",
    "N/A": "descriptive performance measurement with no correctness oracle",
}


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def _cpu_model() -> str | None:
    if platform.system() == "Windows":
        return platform.processor()
    if platform.system() == "Linux":
        try:
            text = Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="ignore")
            for line in text.splitlines():
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
        except OSError:
            return None
    return platform.processor() or None


def _package_versions() -> dict:
    out = {}
    for name in _PACKAGES:
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            out[name] = None
    return out


def collect() -> dict:
    status = _git("status", "--porcelain")
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(status),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "cpu_model": _cpu_model(),
        "packages": _package_versions(),
    }


if __name__ == "__main__":
    print(json.dumps(collect(), indent=2))
