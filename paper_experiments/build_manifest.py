"""Build the machine-readable experiment manifest from EXPERIMENT_INDEX.md.

The index is the human-readable source of truth.  This script makes its
declared question, oracle, metric, threshold, cost, and manuscript location
queryable, while assigning an explicit non-performance hypothesis to
descriptive studies.  Experiment scripts add exact seeds/configuration to
their per-run result and metadata files.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from publication import fingerprint, required_artifacts, result_stem, sha256

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "EXPERIMENT_INDEX.md"
OUT = ROOT / "EXPERIMENT_MANIFEST.json"


def main() -> None:
    rows = []
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| R") or line.startswith("| ID"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 12:
            raise ValueError(f"Malformed experiment-index row: {line}")
        experiment_id, script, question, api, oracle, oracle_class, metric, acceptance, kind, cost, destination, index_status = cells
        script_match = re.search(r"`([^`]+)`", script)
        script_path = script_match.group(1) if script_match else script
        stem = result_stem(experiment_id, script_path)
        result_path = ROOT / "results" / "json" / f"{stem}.json"
        result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {}
        artifacts = required_artifacts(experiment_id, script_path)
        exact_artifacts = [
            {"path": str(path.relative_to(ROOT)), "exists": path.exists(), "sha256": sha256(path) if path.exists() else None}
            for path in artifacts
        ]
        script_file = ROOT / script_path
        result_status = result.get("status", "missing")
        descriptive = oracle_class == "N/A"
        rows.append({
            "experiment_id": experiment_id,
            "script": script_path,
            "scientific_question": question,
            "hypothesis": "descriptive; no directional performance hypothesis" if oracle_class == "N/A" else "the stated implementation contract agrees with the declared oracle",
            "api": api,
            "layer": "physical" if "physical" in script_path or "piquasso" in script_path else "resource" if "gkp" in script_path or "convergence" in script_path else "logical",
            "oracle": oracle,
            "oracle_class": oracle_class,
            "metric": metric,
            "acceptance_condition": acceptance,
            "result_protocol": result.get("protocol"),
            "result_acceptance_condition": result.get("acceptance_condition"),
            "result_kind": kind,
            "estimated_cost": cost,
            "manuscript_destination": destination,
            "index_status": index_status,
            "seed_set": result.get("seeds", result.get("n_splits", "N/A for deterministic checks")),
            "configuration": result.get("config", {}),
            "execution_status": result.get("execution_status", "completed" if result else "missing"),
            "structural_status": result.get("structural_status", result_status),
            "scientific_outcome": result.get("scientific_outcome", "descriptive" if descriptive else "positive" if result_status == "pass" else "inconclusive"),
            "claim_supported": result.get("claim_supported", question if result_status == "pass" else ""),
            "claim_not_supported": result.get("claim_not_supported", "No general performance claim" if descriptive else ""),
            "artifacts": exact_artifacts,
            "source_fingerprint": fingerprint(script_file) if script_file.exists() else None,
        })
    OUT.write_text(json.dumps({
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": "EXPERIMENT_INDEX.md",
        "experiments": rows,
    }, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} with {len(rows)} experiments")


if __name__ == "__main__":
    main()
