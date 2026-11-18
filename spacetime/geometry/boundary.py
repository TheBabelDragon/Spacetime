"""Boundary operator on oriented simplicial chains.

For an oriented k-simplex σ = [v₀, …, vₖ] (vertices in the stored order,
orientation sign separate):

    ∂σ = Σᵢ (-1)ⁱ [v₀, …, v̂ᵢ, …, vₖ]

Chains are formal integer linear combinations of oriented simplices,
represented as dict[OrientedSimplex, int] (orientation absorbed into the
coefficient via the canonical +1 representative when convenient).

Mathematical identity: ∂² = 0 for any simplicial complex.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Mapping, MutableMapping

from spacetime.geometry.simplex import OrientedSimplex


Chain = Dict[OrientedSimplex, int]


def _add_to_chain(chain: MutableMapping[OrientedSimplex, int], sigma: OrientedSimplex, coeff: int) -> None:
    """Add coeff * sigma into chain, cancelling opposites and zero terms."""
    if coeff == 0:
        return
    # Reduce to positive-orientation key
    if sigma.orientation < 0:
        key = OrientedSimplex(sigma.vertices, 1)
        coeff = -coeff
    else:
        key = sigma
    new = chain.get(key, 0) + coeff
    if new == 0:
        chain.pop(key, None)
    else:
        chain[key] = new


def boundary(sigma: OrientedSimplex) -> Chain:
    """Return ∂σ as a chain (dict of OrientedSimplex → coefficient).

    The boundary of a 0-simplex (vertex) is the empty chain.
    """
    if sigma.dimension == 0:
        return {}
    result: Chain = {}
    for i in range(sigma.dimension + 1):
        face = sigma.face(i)
        _add_to_chain(result, face, 1)
    return result


def boundary_of_chain(chain: Mapping[OrientedSimplex, int]) -> Chain:
    """Extend ∂ linearly to a chain."""
    result: Chain = {}
    for sigma, coeff in chain.items():
        if coeff == 0:
            continue
        for face, face_coeff in boundary(sigma).items():
            _add_to_chain(result, face, coeff * face_coeff)
    return result


def boundary_square_is_zero(sigma: OrientedSimplex) -> bool:
    """Verify ∂(∂σ) = 0 for a single simplex."""
    return len(boundary_of_chain(boundary(sigma))) == 0


def boundary_square_is_zero_complex(simplices: Iterable[OrientedSimplex]) -> bool:
    """Verify ∂² = 0 on every simplex in the collection."""
    for sigma in simplices:
        if not boundary_square_is_zero(sigma):
            return False
    return True


def chain_to_canonical(chain: Mapping[OrientedSimplex, int]) -> Chain:
    """Normalise a chain to positive-orientation keys with non-zero coeffs."""
    result: Chain = {}
    for sigma, coeff in chain.items():
        _add_to_chain(result, sigma, coeff)
    return result
