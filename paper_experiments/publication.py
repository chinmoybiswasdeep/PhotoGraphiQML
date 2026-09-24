"""Publication-run provenance, source-cleanliness, and artifact helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
GENERATED_PREFIXES = (
    "paper_experiments/results/",
    "paper_experiments/figures/",
    "paper_experiments/tables/",
    "paper_experiments/EXPERIMENT_MANIFEST.json",
    "paper_experiments/PhotoGraphiQML_Manuscript_Experiments.ipynb",
    "paper_experiments/STATUS.md",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str | None:
    process = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    # Preserve porcelain's leading status columns; only remove final newlines.
    return process.stdout.rstrip("\r\n") if process.returncode == 0 else None


def status_paths() -> list[str]:
    return [line[3:] for line in (git("status", "--porcelain") or "").splitlines()]


def source_dirty_paths() -> list[str]:
    """Dirty paths excluding controlled regenerated evidence only."""
    return [path for path in status_paths() if not path.replace("\\", "/").startswith(GENERATED_PREFIXES)]


def package_versions() -> dict[str, str | None]:
    output = {}
    for package in ("photographiqml", "photographiq", "mentpy", "piquasso", "numpy", "scipy"):
        try:
            output[package] = version(package)
        except PackageNotFoundError:
            output[package] = None
    return output


def sibling_commit(name: str) -> str | None:
    sibling = REPO.parent / name
    process = subprocess.run(["git", "rev-parse", "HEAD"], cwd=sibling, capture_output=True, text=True)
    return process.stdout.strip() if process.returncode == 0 else None


def fingerprint(script: Path) -> dict:
    """Inputs whose change invalidates a resumable experiment result."""
    return {
        "photographiqml_commit": git("rev-parse", "HEAD"),
        "script_sha256": sha256(script),
        "common_sha256": sha256(ROOT / "common.py"),
        "metadata_sha256": sha256(ROOT / "metadata.py"),
        "python": sys.version,
        "package_versions": package_versions(),
        "photographiq_commit": sibling_commit("PhotoGraphiQ"),
        "mentpy_commit": "63c3d83e495696b4491c9d376dab7e3e6cf6c863",
    }


def fingerprint_hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest()


def result_stem(experiment_id: str, script: str) -> str:
    stem = Path(script).stem
    if experiment_id == "R_PERF":
        return "R_PERF_aggregate_performance"
    number, suffix = stem.split("_", 1)
    return f"R{int(number)}_{suffix}"


def required_artifacts(experiment_id: str, script: str) -> list[Path]:
    stem = result_stem(experiment_id, script)
    return [
        ROOT / "results" / "csv" / f"{stem}.csv",
        ROOT / "results" / "json" / f"{stem}.json",
        ROOT / "results" / "json" / f"{stem}.metadata.json",
        ROOT / "figures" / "pdf" / f"{stem}.pdf",
        ROOT / "figures" / "png" / f"{stem}.png",
        ROOT / "figures" / "svg" / f"{stem}.svg",
    ]
