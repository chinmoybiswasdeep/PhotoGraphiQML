# Suite execution status

## Evidence-status warning (2026-09-24)

The historical per-experiment table below was generated while the repository
was dirty and must **not** be treated as final publication evidence.  The
active checkout is also dirty because the user has uncommitted notebook
changes and the experiment-suite corrections under review.  A fresh
subprocess-isolated safe run on this checkout completed on 2026-09-24 with
**36 passed, 0 failed, and 13 explicitly skipped heavy experiments** in
389.6 s; its raw runner output is
`results/logs/safe_validation_20260924.stdout.log` and machine-readable
summary is `results/json/run_all_safe_summary.json`.  This establishes
current runnable logical/resource/lowering coverage, but is deliberately
not a clean-commit full-publication run.  The 13 named skips require the
full runner; they remain execution work, not positive results.

The current provenance records PhotoGraphiQ commit
`6d49da06fa6ede78bf06ea1df07ccfb3b4f5250e`, package versions, and import
origins so an unrelated installed `photographiqml` checkout cannot be
mistaken for the system under test.

Latest real execution on this host (Windows 11, Python 3.14.4, `.venv`),
branch `manuscript-experiments`, commit as recorded in each experiment's own
`<name>.metadata.json` (git was dirty throughout authoring, since these are
the new files being added). All 127 pre-existing repository tests
(`python -m pytest -q`) continue to pass unchanged, `mypy` reports no
issues, `mkdocs build --strict` succeeds, and `ruff check`/`ruff format
--check` are clean on `paper_experiments/` — `src/photographiqml` was never
modified.

| ID | Implemented | Executed | Passed | Skipped | Reason | Runtime (approx.) | Output paths |
|---|---|---|---|---|---|---|---|
| R1 | Y | Y | Y | - | - | <1s | `results/{csv,json}/R1_triangle_anatomy.*`, `figures/*/R1_triangle_anatomy.*` |
| R2 | Y | Y | Y | - | - | <1s | `R2_table_one_identities.*` |
| R3 | Y | Y | Y | - | - | <1s | `R3_entangling_identity.*` |
| R4 | Y | Y | Y | - | - | <1s | `R4_adaptive_branches.*` |
| R5 | Y | Y | Y | - | - | ~1s | `R5_brute_force_agreement.*` |
| R6 | Y | Y | Y | - | - | <1s | `R6_batch_consistency.*` |
| R7 | Y | Y | Y | - | - | ~1s | `R7_semantic_topology.*` |
| R8 | Y | Y | Y | - | - | ~1s | `R8_flow_dependency_order.*` |
| R9 | Y | Y | Y | - | - | ~3s | `R9_state_density_agreement.*` |
| R10 | Y | Y | Y | - | - | ~1s | `R10_trainability_audit.*` |
| R11 | Y | Y | Y | - | - | ~1s | `R11_kernel_gram_agreement.*` |
| R12 | Y | Y | Y | - | - | ~1s | `R12_instrument_agreement.*` |
| R13 | Y | Y | Y | - | - | ~5s | `R13_runtime_scaling.*` |
| R14 | Y | Y | Y | - | - | <1s | `R14_parameter_contracts.*` |
| R15 | Y | Y | Y | - | - | <1s | `R15_persistence_roundtrip.*` |
| R16 | Y | Y | Y | - | - | <1s | `R16_invalid_input_matrix.*` |
| R17 | Y | Y | Y | - | - | ~20s (32-shot physical run, cutoff=40) | `R17_seeded_reproducibility.*` |
| R18 | Y | Y | Y | - | - | ~1s | `R18_parameter_shift_vs_fd.*` |
| R19 | Y | Y | Y | - | - | ~2s | `R19_optimizer_convergence.*` |
| R20 | Y | Y | Y | - | - | ~15s (20 seeds x 120 epochs) | `R20_haar_gate_learning.*` |
| R21 | Y | Y | Y | - | - | ~15s | `R21_ising_gate_learning.*` |
| R22 | Y | Y | Y | - | - | ~90s (108 short runs) | `R22_gate_learning_sensitivity.*` |
| R23 | Y | Y | Y | - | - | ~5s (rescoped, see ISSUES_FOUND.md #3) | `R23_classifier_verification.*` |
| R24 | Y | Y | Y | - | - | ~5s | `R24_regressor_verification.*` |
| R25 | Y | Y | Y | - | - | <1s | `R25_kernel_feature_state.*` |
| R26 | Y | Y | Y | - | - | <1s | `R26_kernel_properties.*` |
| R27 | Y | Y | Y | - | - | ~40s (24 SVM fits, 3 datasets) | `R27_kernel_classification.*` |
| R28 | Y | Y | Y | - | - | ~30s | `R28_kernel_robustness.*` |
| R29 | Y | Y | Y | - | - | <1s | `R29_instrument_diagnostics.*` |
| R30 | Y | Y | Y | - | - | <1s | `R30_concurrence.*` |
| R31 | Y | Y | Y | - | - | <1s | `R31_qfi.*` |
| R32 | Y | Y | Y | - | - | <1s | `R32_lie_closure.*` |
| R33 | Y | Y | Y | - | - | <1s | `R33_fisher_spectra.*` |
| R34 | Y | Y | Y | - | - | ~5s | `R34_gkp_codeword_projection.*` |
| R35 | Y | Y | Y | - | - | <1s | `R35_capability_map.*` |
| R36 | Y | Y | Y | - | - | ~5s | `R36_lowering_preservation.*` |
| R37 | Y | Y | Y | - | - | ~1s | `R37_pauli_frame_validation.*` |
| R38 | Y | Y | Y | - | - | ~5s (after fixing JIT-scheduling design bug in the independent Pattern; see below) | `R38_public_pattern_comparison.*` |
| R39 | Y | Y | Y | - | - | ~1s | `R39_raw_piquasso_state_prep.*` |
| R40 | Y | Y | Y | - | - | ~30s (2-mode Fock sim, cutoff up to 80) | `R40_raw_piquasso_cz.*` |
| R41 | Y | Y | Y | - | - | ~10s | `R41_conditional_execution_comparison.*` |
| R42 | Y | Y | Y | - | - | ~10s | `R42_abstraction_overhead.*` |
| R43 | Y | Y | Y | - | - | ~15s | `R43_decoded_statistics.*` |
| R44 | Y | Y | Y | - | - | ~5 min (many physical-shots simulations at cutoff=40) | `R44_shot_convergence.*` |
| R45 | Y | Y | Y | - | - | ~15s | `R45_joint_readout_correlations.*` |
| R46 | Y | Y | Y | - | - | <1s | `R46_hard_vs_soft_decoding.*` |
| R47 | Y | Y | Y | - | - | ~3 min (5 axes x up to 4 points) | `R47_resource_axis_convergence.*` |
| R48 | Y | Y | Y | - | - | ~12 min (144 physical-shot Fock simulations across 6 seeds, cutoff=40) | `R48_physical_training_stability.*` |
| R_PERF | Y | Y | Y | - | - | <1s (reads saved JSON only) | `R_PERF_aggregate_performance.*` |

**48/48 (+R_PERF) implemented, 48/48 executed, 48/48 (+R_PERF) passed.**
`run_all_safe.py` classifies 10 experiments (R17, R22, R27, R28, R38,
R40-R48) as moderate/heavy and skips them by default with an explicit
reason each; `run_all_full.py` runs everything. R48's instability finding
itself: `instability_rate=0.33` (2/6 training seeds selected a
configuration whose accuracy changed on fresh validation trajectories),
`distinct_selected_configurations=2` across 6 seeds — a genuine instability
result, exactly as the physical-training documentation anticipates (see
`docs/physical/physical-training.md` and `MANUSCRIPT_MAP.md`'s anti-claims
section).

## Genuine findings made while building this suite

See `ISSUES_FOUND.md` for full detail. Summary: (1) MentPy's
`restrict_trainable` never actually fixes the underlying `Ment` angle in any
tested configuration (upstream, documented, not a PhotoGraphiQML defect);
(2) MentPy's raw `Flow.correction_op` includes a physically-inert
self-correction term PhotoGraphiQML's own convention excludes (upstream
convention difference, not a defect); (3) a composite two-feature
`MuTAClassifier` decision boundary did not train reliably within a moderate
epoch budget (a genuine ansatz/optimizer-scope finding, not a code defect;
`R23` was rescoped to the single-feature task the package's README already
demonstrates working).

## Assessment for the manuscript

**Strongest results:** R7-R9 (exact MentPy agreement to ~1e-13), R20/R21
(20-seed gate-learning statistics with MentPy checkpoints), R38-R41
(independent public-Pattern/raw-Piquasso agreement, exact to numerical
precision), R32 (Lie-closure cross-check via an entirely independent
matrix-commutator algorithm).

**Numerically exact/converged:** R1-R6, R14-R18, R25-R26, R29-R37, R39,
R43, R45-R46 (all exact, class A/D/E oracles, roundoff-level agreement).

**Illustrative rather than tightly quantitative:** R22, R27, R28 (kernel/
learning sensitivity sweeps — descriptive, N/A oracle class by design);
R13, R42 (local single-machine timing observations).

**Remain explicitly experimental/uncertified:** R44 (shot convergence —
Monte Carlo, never claims resource accuracy), R47 (resource-axis
convergence — `certified` is always `False` by construction), R48 (discrete
physical training — an explicit instability finding, not a performance
claim).

**Should be rerun on a more powerful machine:** R44, R47, R48 (each several
minutes on this host; would benefit from more shots/seeds/axis points than
used here for tighter confidence intervals).
