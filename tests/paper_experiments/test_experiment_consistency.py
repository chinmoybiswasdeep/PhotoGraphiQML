"""Generated-evidence consistency checks for the manuscript suite."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = ROOT / "paper_experiments"


def index_rows():
    rows = []
    for line in (EXPERIMENTS / "EXPERIMENT_INDEX.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| R") and not line.startswith("| ID"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            rows.append({"id": cells[0], "script": re.search(r"`([^`]+)`", cells[1]).group(1), "oracle": cells[5], "acceptance": cells[7], "status": cells[11]})
    return rows


def stem(row):
    script_stem = Path(row["script"]).stem
    if row["id"] == "R_PERF":
        return "R_PERF_aggregate_performance"
    number, suffix = script_stem.split("_", 1)
    return f"R{int(number)}_{suffix}"


def result(row):
    return json.loads((EXPERIMENTS / "results" / "json" / f"{stem(row)}.json").read_text(encoding="utf-8"))


def test_indexed_scripts_and_evidence_are_unique_and_present():
    rows = index_rows()
    assert len(rows) == 49
    assert len({row["id"] for row in rows}) == len(rows)
    assert len({row["script"] for row in rows}) == len(rows)
    for row in rows:
        assert (EXPERIMENTS / row["script"]).is_file(), row
        for suffix, directory in ((".json", "results/json"), (".metadata.json", "results/json"), (".csv", "results/csv"), (".pdf", "figures/pdf"), (".png", "figures/png"), (".svg", "figures/svg")):
            assert (EXPERIMENTS / directory / f"{stem(row)}{suffix}").is_file(), row


def test_results_and_metadata_match_index_oracle_and_status():
    for row in index_rows():
        evidence = result(row)
        metadata = json.loads((EXPERIMENTS / "results" / "json" / f"{stem(row)}.metadata.json").read_text(encoding="utf-8"))
        assert evidence["oracle_class"] == row["oracle"], row
        assert metadata["oracle_class"] == row["oracle"], row
        assert evidence["status"].casefold() == row["status"].casefold(), row
        for key in ("git_commit", "git_branch", "python_version", "packages"):
            assert key in metadata, (row, key)


def test_r2_declared_tolerance_matches_script_index_result_and_manifest():
    row = next(row for row in index_rows() if row["id"] == "R2")
    tolerance = result(row)["tolerance"]
    assert tolerance == pytest.approx(2.220446049250313e-15)
    assert float(re.search(r"([0-9.]+e-[0-9]+)", row["acceptance"]).group(1)) == pytest.approx(tolerance, rel=0.02)
    entry = next(item for item in json.loads((EXPERIMENTS / "EXPERIMENT_MANIFEST.json").read_text(encoding="utf-8"))["experiments"] if item["experiment_id"] == "R2")
    assert float(re.search(r"([0-9.]+e-[0-9]+)", entry["acceptance_condition"]).group(1)) == pytest.approx(tolerance, rel=0.02)
    assert "declare_tolerance(scale=1.0)" in (EXPERIMENTS / row["script"]).read_text(encoding="utf-8")


def test_bootstrap_statistics_are_explicit_and_recorded():
    for path in EXPERIMENTS.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for call in ast.walk(tree):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr in {"bootstrap_ci", "paired_difference_ci"}:
                assert any(keyword.arg == "statistic" for keyword in call.keywords), path
    for row in index_rows():
        for key, value in result(row).items():
            if key.endswith("_ci") and isinstance(value, dict) and "n_boot" in value:
                assert value.get("statistic") in {"mean", "median"}, (row, key)


def test_r23_and_lie_labels_are_scientifically_correct():
    assert "one-dimensional threshold" in result(next(row for row in index_rows() if row["id"] == "R23"))["protocol"]
    r32 = result(next(row for row in index_rows() if row["id"] == "R32"))
    dimensions = {row["case"]: row["production_dimension"] for row in r32["rows"]}
    assert dimensions["two_qubit_local_su2_direct_sum_dim6"] == 6
    assert dimensions["two_qubit_full_su4_dim15"] == 15
