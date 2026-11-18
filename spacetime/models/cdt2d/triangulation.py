"""2D Causal Dynamical Triangulations — discrete spacetime with time foliation.

Geometry is stored in a generic SimplicialComplex (dim=2). Causal structure
and time labels are model-specific metadata layered on top.

Conventions
-----------
- Discrete time slices t = 0 … T-1 (periodic in time only if configured).
- Each slice has exactly N spatial vertices arranged on a circle (topology S¹).
- Vertices are indexed as (t, x) with x ∈ {0, …, N-1}; global id = t * N + x.
- Triangles are of type (1,2) or (2,1): one vertex in one slice, two in an adjacent slice.
- Spacelike edges connect vertices within a slice; timelike edges connect adjacent slices.

Topology note
-------------
- periodic_time=False → discrete cylinder (open in time, closed spatial S¹).
- periodic_time=True  → discrete torus (S¹ × S¹ combinatorially).
These are distinguished by config and by triangle count (T-1 vs T time gaps).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

from spacetime.geometry.complex import SimplicialComplex
from spacetime.geometry.simplex import OrientedSimplex, VertexId


@dataclass(frozen=True)
class CDT2DConfig:
    """Fixed combinatorial parameters of a 2D CDT configuration."""

    n_spatial: int  # vertices per time slice (S¹)
    n_time: int  # number of time slices
    periodic_time: bool = False  # identify t=0 with t=T if True

    def __post_init__(self) -> None:
        if self.n_spatial < 3:
            raise ValueError("n_spatial must be ≥ 3 for S¹ triangulation")
        if self.n_time < 2:
            raise ValueError("n_time must be ≥ 2")

    @property
    def n_vertices(self) -> int:
        return self.n_spatial * self.n_time


def vertex_id(t: int, x: int, n_spatial: int) -> VertexId:
    return t * n_spatial + x


def time_of(vid: VertexId, n_spatial: int) -> int:
    return vid // n_spatial


def space_of(vid: VertexId, n_spatial: int) -> int:
    return vid % n_spatial


@dataclass
class CDT2DTriangulation:
    """A 2D CDT spacetime built on a SimplicialComplex."""

    config: CDT2DConfig
    complex: SimplicialComplex = field(init=False)
    # triangle type: +1 for (2,1) [two vertices in lower slice], -1 for (1,2)
    triangle_types: Dict[Tuple[VertexId, ...], int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.complex = SimplicialComplex(dimension=2)
        for t in range(self.config.n_time):
            for x in range(self.config.n_spatial):
                self.complex.add_vertex(vertex_id(t, x, self.config.n_spatial))

    def add_triangle(
        self,
        v0: VertexId,
        v1: VertexId,
        v2: VertexId,
        *,
        orientation: int = 1,
    ) -> OrientedSimplex:
        """Add a causal triangle after validating slice adjacency."""
        times = sorted(
            {
                time_of(v0, self.config.n_spatial),
                time_of(v1, self.config.n_spatial),
                time_of(v2, self.config.n_spatial),
            }
        )
        if len(times) != 2:
            raise ValueError(
                f"triangle vertices must occupy exactly two adjacent time slices; got times {times}"
            )
        t_lo, t_hi = times
        adjacent = (t_hi == t_lo + 1) or (
            self.config.periodic_time
            and t_lo == 0
            and t_hi == self.config.n_time - 1
        )
        if not adjacent:
            raise ValueError(f"time slices {t_lo} and {t_hi} are not adjacent")

        n_lo = sum(1 for v in (v0, v1, v2) if time_of(v, self.config.n_spatial) == t_lo)
        n_hi = 3 - n_lo
        if not ((n_lo, n_hi) in ((1, 2), (2, 1))):
            raise ValueError(
                f"causal triangle must be type (1,2) or (2,1); got ({n_lo},{n_hi})"
            )
        tri_type = 1 if n_lo == 2 else -1  # (2,1) vs (1,2)

        sigma = self.complex.add_simplex((v0, v1, v2), orientation)
        self.triangle_types[sigma.key] = tri_type
        return sigma

    def build_flat_cylinder(self) -> None:
        """Construct the standard regular triangulation of a cylinder (or torus if periodic_time).

        Each pair of adjacent slices is filled with 2 * n_spatial triangles
        forming a regular band. Spatial boundary is periodic (S¹).

        Triangle count:
        - cylinder (periodic_time=False): 2 * N * (T - 1)
        - torus    (periodic_time=True):  2 * N * T
        """
        cfg = self.config
        N = cfg.n_spatial
        T = cfg.n_time
        time_pairs = [(t, t + 1) for t in range(T - 1)]
        if cfg.periodic_time:
            time_pairs.append((T - 1, 0))

        for t_lo, t_hi in time_pairs:
            for x in range(N):
                x_next = (x + 1) % N
                # Type (2,1): two vertices in lower slice
                a = vertex_id(t_lo, x, N)
                b = vertex_id(t_lo, x_next, N)
                c = vertex_id(t_hi, x, N)
                self.add_triangle(a, b, c)
                # Type (1,2): two vertices in upper slice
                d = vertex_id(t_hi, x_next, N)
                self.add_triangle(b, c, d)

    def edge_kind(self, a: VertexId, b: VertexId) -> str:
        """Return 'spacelike', 'timelike', or 'invalid'."""
        ta, tb = time_of(a, self.config.n_spatial), time_of(b, self.config.n_spatial)
        if ta == tb:
            xa, xb = space_of(a, self.config.n_spatial), space_of(b, self.config.n_spatial)
            N = self.config.n_spatial
            if (xa - xb) % N in (1, N - 1):
                return "spacelike"
            return "invalid"
        if abs(ta - tb) == 1 or (
            self.config.periodic_time
            and {ta, tb} == {0, self.config.n_time - 1}
        ):
            return "timelike"
        return "invalid"

    def spacelike_edges(self) -> Set[Tuple[VertexId, VertexId]]:
        return {
            e
            for e in self.complex.edges()
            if self.edge_kind(*e) == "spacelike"
        }

    def timelike_edges(self) -> Set[Tuple[VertexId, VertexId]]:
        return {
            e
            for e in self.complex.edges()
            if self.edge_kind(*e) == "timelike"
        }

    def to_dict(self) -> dict:
        return {
            "config": {
                "n_spatial": self.config.n_spatial,
                "n_time": self.config.n_time,
                "periodic_time": self.config.periodic_time,
            },
            "complex": self.complex.to_dict(),
            "triangle_types": {
                str(list(k)): v for k, v in sorted(self.triangle_types.items())
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> CDT2DTriangulation:
        import ast

        cfg = CDT2DConfig(**data["config"])
        tri = cls(config=cfg)
        tri.complex = SimplicialComplex.from_dict(data["complex"])
        fixed: Dict[Tuple[VertexId, ...], int] = {}
        for k, v in data.get("triangle_types", {}).items():
            if isinstance(k, str):
                key = tuple(ast.literal_eval(k))
            else:
                key = tuple(k)
            fixed[key] = int(v)
        tri.triangle_types = fixed
        return tri
