"""Publication-run provenance, source-cleanliness, and artifact helpers."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SCHEMA_VERSION = 3
ALLOWED_OUTCOMES = {"positive", "negative", "descriptive", "inconclusive", "not_run"}
GENERATED_PREFIXES = (
    "paper_experiments/results/",
    "paper_experiments/figures/",
    "paper_experiments/tables/",
    "paper_experiments/EXPERIMENT_MANIFEST.json",
    "paper_experiments/PhotoGraphiQML_Manuscript_Experiments.ipynb",
    "paper_experiments/STATUS.md",
)
EXPECTED_IDS = tuple(
    [f"R{number}" for number in range(1, 49)]
    + ["R_PERF"]
    + [f"R{number}" for number in range(50, 60)]
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_sha256(path: Path) -> str:
    """Hash source bytes after applying Git's declared text normalization."""
    relative = str(path.relative_to(REPO)).replace("\\", "/")
    attributes = subprocess.run(
        ["git", "check-attr", "-z", "text", "--", relative],
        cwd=REPO,
        capture_output=True,
        check=True,
    ).stdout.split(b"\0")
    text_attribute = attributes[2].decode("utf-8") if len(attributes) >= 3 else "unspecified"
    data = path.read_bytes()
    if text_attribute in {"set", "auto"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    """Atomically replace a UTF-8 text artifact in its destination directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_write_json(path: Path, value: object) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=False) + "\n")


def git(*args: str) -> str | None:
    process = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    # Preserve porcelain's leading status columns; only remove final newlines.
    return process.stdout.rstrip("\r\n") if process.returncode == 0 else None


def status_paths() -> list[str]:
    return [line[3:] for line in (git("status", "--porcelain") or "").splitlines()]


def source_dirty_paths() -> list[str]:
    """Dirty paths excluding controlled regenerated evidence only."""
    return [
        path
        for path in status_paths()
        if not path.replace("\\", "/").startswith(GENERATED_PREFIXES)
    ]


def index_rows() -> list[dict[str, str]]:
    """Parse the canonical 12-column experiment index."""
    rows = []
    for line in (ROOT / "EXPERIMENT_INDEX.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("| R") or line.startswith("| ID"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 12:
            raise ValueError(f"Malformed experiment-index row: {line}")
        script = cells[1].strip("`")
        rows.append(
            dict(
                zip(
                    (
                        "experiment_id",
                        "script",
                        "scientific_question",
                        "api",
                        "oracle",
                        "oracle_class",
                        "metric",
                        "acceptance_condition",
                        "result_kind",
                        "estimated_cost",
                        "manuscript_destination",
                        "index_status",
                    ),
                    [cells[0], script, *cells[2:]],
                    strict=True,
                )
            )
        )
    return rows


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
    if not sibling.is_dir():
        return None
    process = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=sibling, capture_output=True, text=True
    )
    return process.stdout.strip() if process.returncode == 0 else None


def sibling_dirty(name: str) -> bool | None:
    sibling = REPO.parent / name
    if not sibling.is_dir():
        return None
    process = subprocess.run(
        ["git", "status", "--porcelain"], cwd=sibling, capture_output=True, text=True
    )
    return bool(process.stdout.strip()) if process.returncode == 0 else None


def scientifically_relevant_files() -> list[Path]:
    """Tracked inputs defining experiments, package behavior, and environment."""
    process = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True)
    tracked = [
        value.decode("utf-8", errors="surrogateescape")
        for value in process.stdout.split(b"\0")
        if value
    ]
    excluded = tuple(prefix.rstrip("/") for prefix in GENERATED_PREFIXES)
    files = []
    for relative in tracked:
        normalized = relative.replace("\\", "/")
        if normalized.startswith(excluded):
            continue
        path = REPO / relative
        if path.is_file():
            files.append(path)
    return sorted(files)


def source_tree_fingerprint() -> dict:
    entries = {
        str(path.relative_to(REPO)).replace("\\", "/"): source_sha256(path)
        for path in scientifically_relevant_files()
    }
    return {"sha256": fingerprint_hash(entries), "files": entries}


def fingerprint(script: Path) -> dict:
    """Inputs whose change invalidates a resumable experiment result."""
    experiment_id = (
        "R_PERF" if script.stem.startswith("49_") else f"R{int(script.stem.split('_', 1)[0])}"
    )
    relative_script = str(script.relative_to(ROOT)).replace("\\", "/")
    artifacts = [
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in required_artifacts(experiment_id, relative_script)
    ]
    contracts = ROOT / "EXPERIMENT_CONTRACTS.json"
    return {
        "schema_version": SCHEMA_VERSION,
        "source_commit": git("rev-parse", "HEAD"),
        "source_tree_fingerprint": source_tree_fingerprint()["sha256"],
        "script_sha256": source_sha256(script),
        "common_sha256": source_sha256(ROOT / "common.py"),
        "metadata_sha256": source_sha256(ROOT / "metadata.py"),
        "contract_sha256": source_sha256(contracts) if contracts.exists() else None,
        "expected_artifacts": artifacts,
        "python": sys.version,
        "package_versions": package_versions(),
        "photographiq_commit": sibling_commit("PhotoGraphiQ"),
        "photographiq_dirty": sibling_dirty("PhotoGraphiQ"),
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


def artifact_records(experiment_id: str, script: str) -> list[dict]:
    return [
        {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "size": path.stat().st_size if path.exists() else None,
            "sha256": sha256(path) if path.exists() else None,
        }
        for path in required_artifacts(experiment_id, script)
    ]


def environment_record() -> dict:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "dependencies": package_versions(),
        "photographiq_commit": sibling_commit("PhotoGraphiQ"),
        "photographiq_dirty": sibling_dirty("PhotoGraphiQ"),
        "mentpy_commit": "63c3d83e495696b4491c9d376dab7e3e6cf6c863",
    }
