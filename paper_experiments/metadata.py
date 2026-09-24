"""Environment/provenance metadata recorded alongside every experiment's output.

Every script calls ``metadata.collect()`` once and writes the result as a
companion ``<name>.metadata.json`` file via ``common.write_metadata``. This is
descriptive provenance only: it does not certify reproducibility on a
different machine, only records the conditions a result was produced under.

Oracle/reference-independence classes (declared per-experiment; see
paper_experiments/README.md and section 5 of the manuscript-experiments task):
"""

from __future__ import annotations

import importlib.util
import json
import platform
import subprocess
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import publication

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


def _sibling_git(name: str) -> dict:
    """Return immutable provenance for a sibling source checkout, if present."""
    root = REPO_ROOT.parent / name
    if not (root / ".git").exists():
        return {"path": str(root), "commit": None, "dirty": None}
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, timeout=10
        )
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.TimeoutExpired):
        return {"path": str(root), "commit": None, "dirty": None}
    return {
        "path": str(root),
        "commit": commit.stdout.strip() if commit.returncode == 0 else None,
        "dirty": bool(dirty.stdout.strip()) if dirty.returncode == 0 else None,
    }


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


def _package_locations() -> dict:
    """Record import origins to detect accidental execution against another checkout."""
    locations = {}
    for name in ("photographiqml", "photographiq", "mentpy", "piquasso"):
        spec = importlib.util.find_spec(name)
        locations[name] = str(spec.origin) if spec and spec.origin else None
    return locations


def collect() -> dict:
    status = _git("status", "--porcelain")
    source = publication.source_tree_fingerprint()
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        # Generated evidence is expected to change during a run; the legacy
        # key therefore records scientific-source dirtiness for acceptance.
        "git_dirty": bool(publication.source_dirty_paths()),
        "worktree_dirty": bool(status),
        "source_dirty": bool(publication.source_dirty_paths()),
        "source_dirty_paths": publication.source_dirty_paths(),
        "source_tree_fingerprint": source["sha256"],
        "provenance_schema_version": publication.SCHEMA_VERSION,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "cpu_model": _cpu_model(),
        "packages": _package_versions(),
        "package_import_origins": _package_locations(),
        "upstream_repositories": {"PhotoGraphiQ": _sibling_git("PhotoGraphiQ")},
    }


if __name__ == "__main__":
    print(json.dumps(collect(), indent=2))
