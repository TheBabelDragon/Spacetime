"""Spacetime — Quantum Geometry & Gravity Research Engine.

v0.3: CDT ensemble engine (reproducible multi-geometry experiments).
"""

__version__ = "0.3.0"

from spacetime.geometry.complex import SimplicialComplex
from spacetime.geometry.simplex import OrientedSimplex, VertexId

__all__ = [
    "SimplicialComplex",
    "OrientedSimplex",
    "VertexId",
    "__version__",
]
