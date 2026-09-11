# Contributing

Install the audited PhotoGraphiQ revision and `pip install -e ".[dev,docs]"`.
Run `python scripts/validate_release.py` before proposing a change. For exact
logical reference checks, install `tests/mentpy_reference/requirements.txt`.

For new physics, include the convention, derivation, independent validator and
convergence study. Distinguish logical qubits, finite GKP states and native CV
channels throughout APIs, examples and claims. A measurement substitution
without an induced-channel derivation is insufficient. Do not normalize away
leakage or compare Fock amplitudes to a qubit vector.

Small bug reports should include a script, versions, seed and expected result.
Keep expensive experiments optional, retain individual seed results and cite
sources. Preserve attribution for any reused code. Add tests for changed
scientific behavior; prefer analytical checks over self-confirming fixtures.
