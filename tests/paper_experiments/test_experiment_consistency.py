"""Fast guards against experiment-reporting drift."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = ROOT / "paper_experiments"


def test_r23_protocol_matches_its_executed_one_dimensional_task():
    source = (EXPERIMENTS / "04_gradients_and_training" / "23_classifier_verification.py").read_text(encoding="utf-8")
    assert '"protocol": "MuTAClassifier on the one-dimensional threshold y=1[x < pi/2]' in source
    assert "X[:, 0] < np.pi / 2" in source


def test_bootstrap_calls_explicitly_name_their_statistic():
    for path in EXPERIMENTS.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr not in {"bootstrap_ci", "paired_difference_ci"}:
                continue
            assert any(keyword.arg == "statistic" for keyword in node.keywords), path


def test_lie_labels_do_not_call_dimension_six_full_su4():
    source = (EXPERIMENTS / "06_expressivity_and_diagnostics" / "32_lie_closure.py").read_text(encoding="utf-8")
    assert "two_qubit_full_su4_seed" not in source
    assert "two_qubit_local_su2_direct_sum_dim6" in source
    assert "two_qubit_full_su4_dim15" in source
