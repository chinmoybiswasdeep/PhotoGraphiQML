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
        experiment_id, script, question, api, oracle, oracle_class, metric, acceptance, kind, cost, destination, status = cells
        script_match = re.search(r"`([^`]+)`", script)
        rows.append({
            "experiment_id": experiment_id,
            "script": script_match.group(1) if script_match else script,
            "scientific_question": question,
            "hypothesis": "descriptive; no directional performance hypothesis" if oracle_class == "N/A" else "the stated implementation contract agrees with the declared oracle",
            "api": api,
            "oracle": oracle,
            "oracle_class": oracle_class,
            "metric": metric,
            "acceptance_condition": acceptance,
            "result_kind": kind,
            "estimated_cost": cost,
            "manuscript_destination": destination,
            "index_status": status,
            "seed_set": "recorded by the executed script result; N/A for deterministic checks",
            "result_paths": {
                "csv": f"results/csv/{experiment_id}_*.csv",
                "json": f"results/json/{experiment_id}_*.json",
                "metadata": f"results/json/{experiment_id}_*.metadata.json",
            },
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
