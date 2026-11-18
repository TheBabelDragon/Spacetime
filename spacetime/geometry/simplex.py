"""Oriented simplices with stable combinatorial identity.

A k-simplex is determined by (k+1) distinct vertices.
Orientation is a sign (+1 or -1). The canonical representative stores
vertices in strictly increasing order with orientation +1; any other
ordering is reduced to the canonical form via the sign of the permutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple

VertexId = int


def _parity_of_permutation(seq: Sequence[int]) -> int:
    """Return +1 for even permutation of sorted order, -1 for odd.

    Uses inversion count. Empty / singleton sequences are even.
    """
    n = len(seq)
    if n <= 1:
        return 1
    inversions = 0
    for i in range(n):
        for j in range(i + 1, n):
            if seq[i] > seq[j]:
                inversions += 1
    return 1 if inversions % 2 == 0 else -1


@dataclass(frozen=True, slots=True)
class OrientedSimplex:
    """An oriented k-simplex.

    Attributes
    ----------
    vertices :
        Canonical (sorted ascending) vertex tuple. Length = k+1.
    orientation :
        +1 or -1 relative to the ascending vertex order.
    """

    vertices: Tuple[VertexId, ...]
    orientation: int = 1

    def __post_init__(self) -> None:
        if self.orientation not in (1, -1):
            raise ValueError(f"orientation must be ±1, got {self.orientation}")
        if len(self.vertices) == 0:
            raise ValueError("simplex must have at least one vertex")
        if len(set(self.vertices)) != len(self.vertices):
            raise ValueError(f"duplicate vertices in simplex: {self.vertices}")
        if tuple(sorted(self.vertices)) != self.vertices:
            raise ValueError(
                f"vertices must be strictly sorted ascending; got {self.vertices}"
            )

    @property
    def dimension(self) -> int:
        """Topological dimension k (number of vertices minus one)."""
        return len(self.vertices) - 1

    @property
    def key(self) -> Tuple[VertexId, ...]:
        """Unordered combinatorial identity (sorted vertices)."""
        return self.vertices

    def opposite(self) -> OrientedSimplex:
        """Return the same geometric simplex with reversed orientation."""
        return OrientedSimplex(self.vertices, -self.orientation)

    def face(self, omit_index: int) -> OrientedSimplex:
        """Oriented face obtained by omitting the vertex at omit_index.

        The induced orientation is (-1)^omit_index * self.orientation,
        matching the standard boundary formula.
        """
        if omit_index < 0 or omit_index > self.dimension:
            raise IndexError(
                f"omit_index {omit_index} out of range for dim {self.dimension}"
            )
        verts = self.vertices[:omit_index] + self.vertices[omit_index + 1 :]
        sign = self.orientation * (1 if omit_index % 2 == 0 else -1)
        return OrientedSimplex(verts, sign)

    @classmethod
    def from_vertices(
        cls, vertices: Iterable[VertexId], orientation: int = 1
    ) -> OrientedSimplex:
        """Build an oriented simplex from an arbitrary vertex ordering.

        The orientation is composed with the sign of the permutation that
        sorts the vertices into ascending order.
        """
        verts = tuple(vertices)
        if len(verts) == 0:
            raise ValueError("simplex must have at least one vertex")
        if len(set(verts)) != len(verts):
            raise ValueError(f"duplicate vertices: {verts}")
        if orientation not in (1, -1):
            raise ValueError(f"orientation must be ±1, got {orientation}")
        parity = _parity_of_permutation(verts)
        sorted_verts = tuple(sorted(verts))
        return cls(sorted_verts, orientation * parity)

    def __repr__(self) -> str:
        sign = "+" if self.orientation > 0 else "-"
        return f"{sign}{self.vertices}"
