"""Combinatorial measurements. No physical interpretation is implied."""

from __future__ import annotations

from typing import Dict

from spacetime.geometry.complex import SimplicialComplex


def simplex_counts(complex_: SimplicialComplex) -> Dict[int, int]:
    """Number of simplices of each dimension 0 … dim."""
    counts: Dict[int, int] = {0: complex_.n_vertices()}
    for d in range(1, complex_.dimension + 1):
        counts[d] = len(complex_.all_faces(d))
    return counts


def euler_characteristic(complex_: SimplicialComplex) -> int:
    """χ = Σ (-1)^k N_k for a finite simplicial complex."""
    counts = simplex_counts(complex_)
    chi = 0
    for k, n in counts.items():
        chi += n if k % 2 == 0 else -n
    return chi


def vertex_degrees(complex_: SimplicialComplex) -> Dict[int, int]:
    """Map vertex id → degree (number of incident edges)."""
    return {v: complex_.vertex_degree(v) for v in complex_.vertices}
