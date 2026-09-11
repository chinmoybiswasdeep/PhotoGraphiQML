# PhotoGraphiQML

Trainable logical MuTA models with an explicit bridge to PhotoGraphiQ's finite-energy GKP resources.

[![Tests](https://github.com/chinmoybiswasdeep/PhotoGraphiQML/actions/workflows/ci.yml/badge.svg)](https://github.com/chinmoybiswasdeep/PhotoGraphiQML/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/chinmoybiswasdeep/PhotoGraphiQML)](LICENSE)
[![Release](https://img.shields.io/github/v/release/chinmoybiswasdeep/PhotoGraphiQML)](https://github.com/chinmoybiswasdeep/PhotoGraphiQML/releases)
[![Issues](https://img.shields.io/github/issues/chinmoybiswasdeep/PhotoGraphiQML)](https://github.com/chinmoybiswasdeep/PhotoGraphiQML/issues)
[![Pull requests](https://img.shields.io/github/issues-pr/chinmoybiswasdeep/PhotoGraphiQML)](https://github.com/chinmoybiswasdeep/PhotoGraphiQML/pulls)
[![Stars](https://img.shields.io/github/stars/chinmoybiswasdeep/PhotoGraphiQML)](https://github.com/chinmoybiswasdeep/PhotoGraphiQML)

Research software, version 0.1.0. Logical MuTA is executable and independently
validated. The GKP bridge prepares finite resources and exposes ideal targets;
general finite-energy GKP MuTA execution is **unsupported**. CVMuTA remains a
separate derivation proposal pending that bridge. These are three distinct
scientific models. See the [release report](docs/release-report.md).

![Logical MuTA graph](docs/assets/muta.svg)

```mermaid
flowchart TD
    P[Piquasso] --> Q[PhotoGraphiQ: optical resources and simulation]
    Q --> ML[PhotoGraphiQML]
    ML --> L[Logical MuTA: implemented]
    ML --> G[GKP bridge: resources and ideal targets]
    ML --> C[CVMuTA: derivation proposal]
```

## Install from source

Python 3.11–3.14 is targeted; see the release report for versions actually run.
Install the audited PhotoGraphiQ revision, then this repository:

```bash
python -m pip install "photographiq @ git+https://github.com/chinmoybiswasdeep/PhotoGraphiQ.git@f15957d297f65f1e4761007e189f11119282dfdd"
python -m pip install -e ".[dev,docs]"
```

For optional independent MentPy validation:

```bash
python -m pip install -r tests/mentpy_reference/requirements.txt
python -m pytest
```

Core execution does not import MentPy. `.[validation]` installs its release;
the requirements file pins the exact audited source revision.

## Five-minute example

```python
import numpy as np
import photographiqml as pqml

# one_column=True means one paper (2,0) layer.
model = pqml.MuTA(2, 1, one_column=True, representation="logical")
result = model.run([1, 0, 0, 0], {"alpha.w1.c1": np.pi / 2})
print(result.probabilities)  # [0.5, 0, 0, 0.5], up to numerical roundoff
print(model.summary())
```

Without `one_column=True`, each requested layer cycles through every pivot
wire, matching MentPy's convention. Angles are in radians. Inputs must already
be normalized; named parameters default to stored values (initially zero).
`restrict_trainable=True` explicitly fixes column 3 at X across all layers.
The full paper ansatz, with all four measurements per wire trainable, is the
default. This fixes a documented upstream trainability inconsistency.

## Train and predict

```python
from photographiqml import MuTAClassifier, Trainer

classifier = MuTAClassifier(
    pqml.MuTA(1), trainer=Trainer(epochs=60), seed=0
)
classifier.fit([[0.0], [0.1], [3.0], [3.14]], [1, 1, 0, 0])
print(classifier.predict([[0.05], [3.1]]))  # [1, 0]
```

This example fits a small classical dataset using explicit product Ry encoding.
It is a functionality demonstration, not an advantage benchmark.

## Features and scientific boundaries

- Semantic triangle graphs, causal flow and ideal logical inference.
- PhotoGraphiQ symbolic parameters, initialization, freezing and JSON model state.
- Adam/SGD and SciPy L-BFGS, deterministic finite differences and histories.
- Binary classifiers, scalar regressors, quantum-output instruments and Eq. 5 kernels.
- Logical concurrence, pure-state QFI, Pauli Lie closure and local Fisher diagnostics.
- GKP resource projection, overlap and cutoff/grid diagnostics through PhotoGraphiQ.
- Table I identities, all small adaptive branches and optional MentPy comparisons.

MentPy validates qubit structure and logical outputs; it never serves as an
oracle for arbitrary CV physics. There is no `alpha -> homodyne angle`
substitution. Physical XY measurements, magic-state injection and decoding
remain prerequisites for full GKP MuTA. See [research mapping](docs/research/muta-mapping.md),
[tutorials](docs/tutorials/index.md), [API shapes](docs/api.md), and
[reproducible gate learning](experiments/paper_reproduction/README.md).

Build docs with `mkdocs build --strict`; run local checks with
`python scripts/validate_release.py`. CI defines the Python matrix and an
optional pinned MentPy job. No published workflow or release status is
asserted by the dynamic badges.

## Cite and contribute

MuTA: L. Mantilla Calderón, R. Raussendorf, P. Feldmann, D. Bondarenko,
*Measurement-based quantum machine learning*, PRA **113**, 042421 (2026),
[doi:10.1103/2snk-m8c6](https://doi.org/10.1103/2snk-m8c6).
Reference software: [MentPy](https://github.com/mentpy/mentpy), Apache-2.0.
Optical engine: [PhotoGraphiQ](https://github.com/chinmoybiswasdeep/PhotoGraphiQ).

See [CITATION.cff](CITATION.cff), [CONTRIBUTING.md](CONTRIBUTING.md),
[ROADMAP.md](ROADMAP.md), and [MIT license](LICENSE).
