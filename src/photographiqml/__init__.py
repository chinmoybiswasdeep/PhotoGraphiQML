"""PhotoGraphiQML: logical MuTA and explicit photonic research boundaries."""

from photographiq.expressions import Parameter

from .ansatz.muta import MuTA
from .ansatz.triangle import TriangleNeuron
from .gkp import GKPBridge
from .kernels import MuTAKernel
from .models import MuTAClassifier, MuTARegressor, QuantumInstrumentModel
from .training import History, Trainer

__version__ = "0.1.0"
__all__ = [
    "MuTA",
    "TriangleNeuron",
    "GKPBridge",
    "MuTAKernel",
    "MuTAClassifier",
    "MuTARegressor",
    "QuantumInstrumentModel",
    "Trainer",
    "History",
    "Parameter",
]
