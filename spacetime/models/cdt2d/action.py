"""Regge-style discrete action for 2D CDT.

In two dimensions the continuum Einstein–Hilbert action reduces (up to
boundary terms) to a topological contribution proportional to the Euler
characteristic, plus a cosmological-constant term proportional to the
volume (number of triangles).

We adopt the standard CDT 2D form (see Ambjørn, Loll et al.):

    S = κ₀ χ  +  κ₂ N₂

or equivalently, with a single coupling,

    S[λ] = λ N₂   (topological term can be absorbed / treated separately)

where N₂ is the number of triangles.

For a closed triangulation χ is fixed by topology; for the cylinder
(open in time) χ depends on the boundary.

This module documents the convention and provides an exact integer /
rational evaluation so that unit tests can match hand calculations.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Union

from spacetime.models.cdt2d.triangulation import CDT2DTriangulation
from spacetime.observables.combinatorics import euler_characteristic, simplex_counts


Number = Union[int, float, Fraction]


@dataclass(frozen=True)
class ActionParameters:
    """Couplings for the 2D Regge / CDT action."""

    kappa0: Number = 0  # coefficient of Euler characteristic
    kappa2: Number = 1  # coefficient of N₂ (cosmological / volume term)


def regge_action_2d(
    triangulation: CDT2DTriangulation,
    params: ActionParameters | None = None,
) -> Fraction:
    """Evaluate the discrete action as an exact Fraction.

    S = κ₀ · χ + κ₂ · N₂

    No continuum limit is claimed; this is the combinatorial action
    on a finite triangulation.
    """
    if params is None:
        params = ActionParameters()
    counts = simplex_counts(triangulation.complex)
    n2 = counts.get(2, 0)
    chi = euler_characteristic(triangulation.complex)
    k0 = Fraction(params.kappa0)
    k2 = Fraction(params.kappa2)
    return k0 * chi + k2 * n2


def volume_n2(triangulation: CDT2DTriangulation) -> int:
    """Number of triangles (exact combinatorial volume in units where a=1)."""
    return triangulation.complex.n_top_simplices()
