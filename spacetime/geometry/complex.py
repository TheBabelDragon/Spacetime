"""Dimension-independent simplicial complex.

Stores oriented top-dimensional simplices and derives lower-dimensional
faces via the boundary operator. Does **not** assume the complex is a
manifold; structural validity and manifold validity are separate checks.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from spacetime.geometry.simplex import OrientedSimplex, VertexId
from spacetime.geometry.boundary import boundary, boundary_square_is_zero


@dataclass
class SimplicialComplex:
    """Finite abstract simplicial complex with oriented top simplices.

    Parameters
    ----------
    dimension :
        Maximum dimension of simplices that will be added as *top* simplices.
        Lower-dimensional faces are derived automatically.
    """

    dimension: int
    _top: Dict[Tuple[VertexId, ...], OrientedSimplex] = field(default_factory=dict)
    _vertices: Set[VertexId] = field(default_factory=set)
    _next_vertex_id: int = 0

    def __post_init__(self) -> None:
        if self.dimension < 0:
            raise ValueError("dimension must be ≥ 0")

    def add_vertex(self, vid: Optional[VertexId] = None) -> VertexId:
        if vid is None:
            while self._next_vertex_id in self._vertices:
                self._next_vertex_id += 1
            vid = self._next_vertex_id
            self._next_vertex_id += 1
        if vid < 0:
            raise ValueError(f"vertex id must be non-negative, got {vid}")
        self._vertices.add(vid)
        if vid >= self._next_vertex_id:
            self._next_vertex_id = vid + 1
        return vid

    def add_vertices(self, n: int) -> List[VertexId]:
        return [self.add_vertex() for _ in range(n)]

    @property
    def vertices(self) -> Set[VertexId]:
        return set(self._vertices)

    def n_vertices(self) -> int:
        return len(self._vertices)

    def add_simplex(
        self,
        vertices: Sequence[VertexId],
        orientation: int = 1,
        *,
        allow_lower: bool = False,
    ) -> OrientedSimplex:
        sigma = OrientedSimplex.from_vertices(vertices, orientation)
        if sigma.dimension > self.dimension:
            raise ValueError(
                f"simplex dimension {sigma.dimension} exceeds complex dimension {self.dimension}"
            )
        if sigma.dimension != self.dimension and not allow_lower:
            raise ValueError(
                f"expected top simplex of dimension {self.dimension}, got {sigma.dimension}; "
                "pass allow_lower=True to store lower-dimensional simplices explicitly"
            )
        for v in sigma.vertices:
            self._vertices.add(v)
            if v >= self._next_vertex_id:
                self._next_vertex_id = v + 1
        key = sigma.key
        if key in self._top:
            existing = self._top[key]
            if existing.orientation != sigma.orientation:
                raise ValueError(
                    f"simplex {key} already present with opposite orientation"
                )
            return existing
        self._top[key] = sigma
        return sigma

    def remove_simplex(self, vertices: Sequence[VertexId]) -> bool:
        key = tuple(sorted(vertices))
        return self._top.pop(key, None) is not None

    def has_simplex(self, vertices: Sequence[VertexId]) -> bool:
        return tuple(sorted(vertices)) in self._top

    def get_simplex(self, vertices: Sequence[VertexId]) -> Optional[OrientedSimplex]:
        return self._top.get(tuple(sorted(vertices)))

    def top_simplices(self) -> List[OrientedSimplex]:
        return list(self._top.values())

    def n_top_simplices(self) -> int:
        return len(self._top)

    def all_faces(self, dim: Optional[int] = None) -> Set[Tuple[VertexId, ...]]:
        faces: Set[Tuple[VertexId, ...]] = set()
        for sigma in self._top.values():
            verts = sigma.vertices
            k = len(verts)
            from itertools import combinations

            if dim is None:
                for r in range(1, k + 1):
                    for comb in combinations(verts, r):
                        faces.add(tuple(sorted(comb)))
            else:
                if dim + 1 > k or dim < 0:
                    continue
                for comb in combinations(verts, dim + 1):
                    faces.add(tuple(sorted(comb)))
        return faces

    def edges(self) -> Set[Tuple[VertexId, VertexId]]:
        return {(a, b) for a, b in self.all_faces(1)}  # type: ignore[misc]

    def vertex_degree(self, v: VertexId) -> int:
        return sum(1 for e in self.edges() if v in e)

    def adjacent_vertices(self, v: VertexId) -> Set[VertexId]:
        result: Set[VertexId] = set()
        for a, b in self.edges():
            if a == v:
                result.add(b)
            elif b == v:
                result.add(a)
        return result

    def star(self, v: VertexId) -> List[OrientedSimplex]:
        return [s for s in self._top.values() if v in s.vertices]

    def connected_components(self) -> List[Set[VertexId]]:
        remaining = set(self._vertices)
        components: List[Set[VertexId]] = []
        while remaining:
            start = next(iter(remaining))
            stack = [start]
            comp: Set[VertexId] = set()
            while stack:
                u = stack.pop()
                if u in comp:
                    continue
                comp.add(u)
                for w in self.adjacent_vertices(u):
                    if w not in comp:
                        stack.append(w)
            components.append(comp)
            remaining -= comp
        return components

    def is_connected(self) -> bool:
        if not self._vertices:
            return True
        return len(self.connected_components()) == 1

    def check_boundary_square(self) -> bool:
        return all(boundary_square_is_zero(s) for s in self._top.values())

    def to_dict(self) -> dict:
        tops = sorted(
            [
                {"vertices": list(s.vertices), "orientation": s.orientation}
                for s in self._top.values()
            ],
            key=lambda d: (d["vertices"], d["orientation"]),
        )
        return {
            "dimension": self.dimension,
            "vertices": sorted(self._vertices),
            "top_simplices": tops,
        }

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict) -> SimplicialComplex:
        dim = int(data["dimension"])
        c = cls(dimension=dim)
        for v in data.get("vertices", []):
            c.add_vertex(int(v))
        for entry in data.get("top_simplices", []):
            c.add_simplex(entry["vertices"], entry.get("orientation", 1))
        return c

    @classmethod
    def from_json(cls, text: str) -> SimplicialComplex:
        return cls.from_dict(json.loads(text))

    def copy(self) -> SimplicialComplex:
        return SimplicialComplex.from_dict(self.to_dict())

    def __repr__(self) -> str:
        return (
            f"SimplicialComplex(dim={self.dimension}, "
            f"V={self.n_vertices()}, top={self.n_top_simplices()})"
        )
