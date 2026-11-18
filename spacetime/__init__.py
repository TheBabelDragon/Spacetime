"""Spacetime — Quantum Geometry & Gravity Research Engine.

v0.1: dimension-independent discrete geometry core + 2D CDT model.
"""

__version__ = "0.1.0"

from spacetime.geometry.complex import SimplicialComplex
from spacetime.geometry.simplex import OrientedSimplex, VertexId

__all__ = [
    "SimplicialComplex",
    "OrientedSimplex",
    "VertexId",
    "__version__",
]
