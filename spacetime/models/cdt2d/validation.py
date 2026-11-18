"""Causal and topological validation for 2D CDT configurations.

Geometry validation (structural simplicial-complex checks) is separate from
manifold validity. This module does **not** claim that a passing complex is
a manifold; it only checks CDT causal/foliation constraints and spatial
periodicity of the flat constructions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from spacetime.geometry.validation import validate_complex, GeometryDiagnostics
from spacetime.models.cdt2d.triangulation import CDT2DTriangulation, time_of, space_of


@dataclass
class CDT2DDiagnostics:
    geometry: GeometryDiagnostics
    causal_ok: bool
    spatial_periodic_ok: bool
    foliation_ok: bool
    issues: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return (
            self.geometry.ok
            and self.causal_ok
            and self.spatial_periodic_ok
            and self.foliation_ok
            and not self.issues
        )

    def summary(self) -> str:
        status = "OK" if self.ok else "FAIL"
        lines = [
            f"CDT2DDiagnostics [{status}]",
            self.geometry.summary(),
            f"  causal_ok            = {self.causal_ok}",
            f"  spatial_periodic_ok  = {self.spatial_periodic_ok}",
            f"  foliation_ok         = {self.foliation_ok}",
        ]
        if self.issues:
            lines.append("  issues:")
            for i in self.issues:
                lines.append(f"    - {i}")
        return "\n".join(lines)


def validate_cdt2d(tri: CDT2DTriangulation) -> CDT2DDiagnostics:
    """Full structural + causal validation of a 2D CDT triangulation."""
    geom = validate_complex(tri.complex)
    issues: List[str] = list(geom.issues)
    cfg = tri.config
    N = cfg.n_spatial
    T = cfg.n_time

    foliation_ok = True
    for v in tri.complex.vertices:
        t = time_of(v, N)
        if t < 0 or t >= T:
            foliation_ok = False
            issues.append(f"vertex {v} has out-of-range time {t}")
        if space_of(v, N) < 0 or space_of(v, N) >= N:
            foliation_ok = False
            issues.append(f"vertex {v} has out-of-range spatial index")

    if tri.complex.n_vertices() != cfg.n_vertices:
        foliation_ok = False
        issues.append(
            f"vertex count {tri.complex.n_vertices()} ≠ expected {cfg.n_vertices}"
        )

    causal_ok = True
    for s in tri.complex.top_simplices():
        times = {time_of(v, N) for v in s.vertices}
        if len(times) != 2:
            causal_ok = False
            issues.append(f"triangle {s.vertices} spans {len(times)} time slices")
            continue
        t_lo, t_hi = sorted(times)
        adjacent = (t_hi == t_lo + 1) or (
            cfg.periodic_time and t_lo == 0 and t_hi == T - 1
        )
        if not adjacent:
            causal_ok = False
            issues.append(f"triangle {s.vertices} joins non-adjacent slices {t_lo},{t_hi}")
        n_lo = sum(1 for v in s.vertices if time_of(v, N) == t_lo)
        if n_lo not in (1, 2):
            causal_ok = False
            issues.append(f"triangle {s.vertices} is not type (1,2) or (2,1)")

    spatial_periodic_ok = True
    for t in range(T):
        slice_edges = 0
        for x in range(N):
            a = t * N + x
            b = t * N + (x + 1) % N
            if not any(set(e) == {a, b} for e in tri.complex.edges()):
                spatial_periodic_ok = False
                issues.append(f"missing spacelike edge ({a},{b}) on slice t={t}")
            else:
                slice_edges += 1
        if slice_edges != N:
            spatial_periodic_ok = False

    return CDT2DDiagnostics(
        geometry=geom,
        causal_ok=causal_ok,
        spatial_periodic_ok=spatial_periodic_ok,
        foliation_ok=foliation_ok,
        issues=issues,
    )
