# Suite execution status

## Current source fingerprint

- Commit: `b2afd24376ef37665c36f04416601ca4f99fa65b`
- Branch: `manuscript-experiments`
- Source files dirty (generated evidence excluded): `True`
- Dirty source paths: `['paper_experiments/12_performance/49_aggregate_performance_figure.py', 'paper_experiments/EXPERIMENT_INDEX.md', 'paper_experiments/build_manifest.py', 'paper_experiments/common.py', 'paper_experiments/run_all_full.py', 'tests/paper_experiments/test_experiment_consistency.py', '.gitattributes', 'paper_experiments/generate_status.py', 'paper_experiments/publication.py']`

## Current publication evidence

No clean-source publication run at this source fingerprint is accepted as final evidence.
Historical or dirty-source artifacts remain inspectable but are not final publication evidence.

## Outcome interpretation

- Positive: only results with a completed execution and an explicit positive scientific outcome.
- Negative: retained explicitly (notably R48 physical-training instability).
- Descriptive: runtime, scaling, and comparison studies do not imply performance success.
- Unsupported: arbitrary-angle physical XY, general physical MuTA, native CVMuTA, soft flow decoding, and entangled physical inputs remain unsupported unless a current experiment demonstrates otherwise.

## Remaining blockers

- A clean-source fingerprint-aware `--publication` run has not yet completed.
- Heavy physical experiments must be executed by that run; no skip is accepted in publication mode.
