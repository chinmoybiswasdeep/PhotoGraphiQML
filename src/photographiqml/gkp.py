"""Controlled GKP resource bridge; no implicit qubit-to-homodyne substitution."""

from dataclasses import dataclass

import numpy as np
from photographiq.gkp import GKPResource, superposition

from .logical import execute, statevector


@dataclass(frozen=True)
class GKPBridge:
    """One-mode finite-resource preparation and explicitly ideal logical targets.

    ``encode`` prepares a normalized finite superposition; because codewords
    overlap, this is not asserted to be an isometric quantum channel.
    """

    cutoff: int = 32
    peak_width: float = 0.4
    envelope: float = 0.4
    peaks: int = 8
    grid_points: int = 4097

    @property
    def resource_options(self):
        return {
            "peak_width": self.peak_width,
            "envelope": self.envelope,
            "peaks": self.peaks,
            "grid_points": self.grid_points,
        }

    def encode(self, logical_state):
        vector = statevector(logical_state, 1)
        return superposition(*vector, cutoff=self.cutoff, **self.resource_options)

    def diagnostics(self):
        projections = [
            GKPResource(bit, **self.resource_options).project(self.cutoff) for bit in (0, 1)
        ]
        basis = np.column_stack([p[0].amplitudes for p in projections])
        gram = basis.conj().T @ basis
        return {
            "cutoff": self.cutoff,
            "captured_weights": [float(p[1]) for p in projections],
            "codeword_overlap": float(abs(gram[0, 1])),
            "gram_eigenvalues": np.linalg.eigvalsh(gram).tolist(),
            "physical_muta_validated": False,
        }

    def logical_target(self, model, input_state, parameters=None):
        """Execute ideal MuTA; result remains labeled logical, never finite GKP."""
        return execute(model, input_state, model._parameters.bind(parameters))

    def run(self, *args, **kwargs):
        raise NotImplementedError(
            "Finite-energy GKP MuTA needs a validated logical XY measurement/injection protocol and decoder; resource preparation alone does not implement it"
        )
