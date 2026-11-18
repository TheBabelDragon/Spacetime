"""Regge-style discrete action for 2D CDT.

S = κ₀ · χ + κ₂ · N₂
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
    kappa0: Number = 0
    kappa2: Number = 1


def regge_action_2d(
    triangulation: CDT2DTriangulation,
    params: ActionParameters | None = None,
) -> Fraction:
    if params is None:
        params = ActionParameters()
    counts = simplex_counts(triangulation.complex)
    n2 = counts.get(2, 0)
    chi = euler_characteristic(triangulation.complex)
    k0 = Fraction(params.kappa0)
    k2 = Fraction(params.kappa2)
    return k0 * chi + k2 * n2


def volume_n2(triangulation: CDT2DTriangulation) -> int:
    return triangulation.complex.n_top_simplices()
