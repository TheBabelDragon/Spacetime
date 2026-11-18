"""Dimension-independent discrete geometry primitives."""

from spacetime.geometry.complex import SimplicialComplex
from spacetime.geometry.simplex import OrientedSimplex, VertexId
from spacetime.geometry.boundary import boundary, boundary_square_is_zero
from spacetime.geometry.validation import GeometryDiagnostics, validate_complex

__all__ = [
    "SimplicialComplex",
    "OrientedSimplex",
    "VertexId",
    "boundary",
    "boundary_square_is_zero",
    "GeometryDiagnostics",
    "validate_complex",
]
