# Suite execution status

## Accepted publication evidence

- Accepted: `True`
- Run identifier: `864af1b907a9-20260924T211728Z`
- Source commit: `864af1b907a9c2875965744c352ae373f15cb3ea`
- Source-tree fingerprint: `60874c92aca19e1bd542303e432ec9b16c2e781c37e240c4ab3174b56fa8c88b`
- Evidence commit: `02c41761043e91ebb3e2ed65fcb5bb71d3bbc184`
- Branch: `manuscript-experiments`
- Started: `2026-09-24T21:17:28.563557+00:00`
- Completed: `2026-09-24T22:13:53.573068+00:00`
- Experiments completed or hash-resumed: `59` / `59`
- Executed in this run: `59`
- Hash-resumed: `0`
- Failed: `0`
- Skipped: `0`
- Manifest SHA-256: `590cd80fa7bdbb9a38928f80b80fb4d95c0069a29de4bd053e5cd6b1565e643f`

## Scientific outcomes

- descriptive: `12`
- negative: `2`
- positive: `45`

Structural pass means execution and declared checks passed; it is not a positive scientific finding.
R48 retains the observed physical-training instability as a negative result.

## Quality gates

- `generate_tables`: `pass` (0.3 s; log `results/logs/publication_generate_tables.log`)
- `build_notebook`: `pass` (0.5 s; log `results/logs/publication_build_notebook.log`)
- `build_manifest`: `pass` (1.1 s; log `results/logs/publication_build_manifest.log`)
- `verify_evidence_pre_status`: `pass` (0.7 s; log `results/logs/publication_verify_evidence_pre_status.log`)
- `repository_validation`: `pass` (118.2 s; log `results/logs/publication_repository_validation.log`)
- `notebook_validation`: `pass` (0.3 s; log `results/logs/publication_notebook_validation.log`)
- `clean_install`: `pass` (6.7 s; log `results/logs/publication_clean_install.log`)
- `installed_import_smoke`: `pass` (2.4 s; log `results/logs/publication_installed_import_smoke.log`)

## Capability boundary

Arbitrary-angle physical XY measurements, general physical MuTA, native CVMuTA, loss/detector-noise models, soft adaptive flow decoding, and physical MuTA kernels remain unsupported. No experiment is described as quantum advantage.
