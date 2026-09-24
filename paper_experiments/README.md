# PhotoGraphiQML manuscript experiment suite

Reproducible experiments (R1–R48, plus an aggregate performance figure)
supporting a QUANTUM-journal manuscript on PhotoGraphiQML: ideal logical
MuTA (validated against MentPy), the restricted signed-X physical GKP
bridge (validated against Piquasso and independently assembled
PhotoGraphiQ patterns), and the classical-ML wrappers built on top of both.

Mirrors the organization and visual style of the sibling
[PhotoGraphiQ `manuscript-experiments`](../../PhotoGraphiQ) suite
(`common.py`/`metadata.py` utility surface, rcParams, PDF+PNG figure
policy, CSV+JSON+metadata "save triple") while testing entirely different
scientific content, and adds oracle-classification (A–E, N/A), bootstrap
confidence intervals, and declared-in-advance tolerances that this suite's
broader physical/statistical scope requires beyond what PhotoGraphiQ's
core suite needed.

## Layout

```
paper_experiments/
├── 01_logical_foundations/      R1-R6   ideal logical MuTA, analytic/independent oracles
├── 02_mentpy_validation/        R7-R13  independent MentPy cross-checks
├── 03_parameters_and_contracts/ R14-R17 parameter/persistence/fail-fast/reproducibility contracts
├── 04_gradients_and_training/   R18-R24 gradients, optimizers, gate learning, classifier/regressor
├── 05_kernels_and_learning/     R25-R28 Eq. 5 kernel properties and classification
├── 06_expressivity_and_diagnostics/ R29-R33 instruments, concurrence, QFI, Lie closure, Fisher spectra
├── 07_gkp_resources/            R34     finite-GKP codeword diagnostics
├── 08_physical_lowering/        R35-R38 capability audit, lowering preservation, Pauli frames
├── 09_piquasso_validation/      R39-R42 raw Piquasso / independent Pattern validation
├── 10_physical_statistics/      R43-R46, R48  decoded statistics, shot convergence, decoding, training stability
├── 11_convergence/              R47     resource-axis convergence studies
├── 12_performance/              aggregate performance figure (reproduced from saved results)
├── results/{csv,json,raw,logs}/ machine-readable outputs
├── figures/{pdf,png,svg}/       publication figures
├── tables/                      generated CSV+Markdown summary tables
├── common.py, metadata.py       shared utilities (see their own docstrings)
├── EXPERIMENT_INDEX.md          one row per experiment: question, oracle class, acceptance, status
├── STATUS.md                    latest real execution record
├── ISSUES_FOUND.md              genuine findings (not silently patched)
├── MANUSCRIPT_MAP.md            proposed figure/table/claim mapping + anti-claims
├── run_all_safe.py              light/deterministic subset, subprocess-isolated
├── run_all_full.py              complete suite, resumable, filterable
├── generate_tables.py           CSV+Markdown summary tables from saved results
├── build_notebook.py            assembles one notebook from these scripts
└── PhotoGraphiQML_Manuscript_Experiments.ipynb
```

## Running

```bash
# from the repository root, using the project's .venv
.venv/Scripts/python.exe paper_experiments/run_all_safe.py     # light/deterministic subset
.venv/Scripts/python.exe paper_experiments/run_all_full.py     # complete suite (heavy; physical shots take minutes)
.venv/Scripts/python.exe paper_experiments/generate_tables.py  # rebuild tables/ from results/
.venv/Scripts/python.exe paper_experiments/build_notebook.py   # rebuild the notebook
```

Or run any single script directly, e.g.
`.venv/Scripts/python.exe paper_experiments/01_logical_foundations/01_triangle_anatomy.py`.
Every script is self-contained (imports only `common`/`metadata` plus public
`photographiqml`/`photographiq`/`mentpy`/`piquasso` APIs) and can be re-run
independently.

## Conventions

- **Oracle classes** (A–E, N/A): declared in every script's docstring, its
  saved JSON, `EXPERIMENT_INDEX.md`, and figure caption/title. See that
  file's header for the class definitions.
- **Tolerances** for exact comparisons are computed by
  `common.declare_tolerance(...)` *before* the acceptance check runs, and
  recorded in the saved JSON — never chosen after inspecting results.
- **Multi-seed studies** use >=20 seeds for logical gate-learning claims
  (R20, R21), report individual trajectories plus median and bootstrap 95%
  CIs (`common.bootstrap_ci(..., statistic=np.median)`), and never
  cherry-pick a "representative" seed. The statistic is mandatory and is
  persisted in each CI object.
- Every experiment imports this checkout's `src/` before the public API, so
  an unrelated installed package with the same name cannot silently supply
  the implementation under test.
- **Physical/shot statistics** distinguish conditional POVM probabilities
  (Rao–Blackwell estimator) from empirical sampled-bit frequencies, each
  with its own standard error, per `docs/physical/execution-modes.md`.
- Every experiment prints a short greppable summary; full evidence is in
  its saved CSV/JSON/metadata/figures, never only in console output.
- A script's pass/fail is computed from its saved metrics against its
  declared acceptance condition — never hard-coded.

See `requirements_notes.md` for the environment this suite was executed in.
