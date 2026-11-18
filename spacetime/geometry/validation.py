"""Structured geometry validation and diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from spacetime.geometry.complex import SimplicialComplex
from spacetime.geometry.boundary import boundary_square_is_zero


@dataclass
class GeometryDiagnostics:
    """Result of structural validation of a simplicial complex."""

    ok: bool
    dimension: int
    n_vertices: int
    n_top_simplices: int
    connected: bool
    n_components: int
    boundary_square_ok: bool
    issues: List[str] = field(default_factory=list)

    def summary(self) -> str:
        status = "OK" if self.ok else "FAIL"
        lines = [
            f"GeometryDiagnostics [{status}]",
            f"  dimension       = {self.dimension}",
            f"  vertices        = {self.n_vertices}",
            f"  top simplices   = {self.n_top_simplices}",
            f"  connected       = {self.connected} ({self.n_components} component(s))",
            f"  ∂² = 0          = {self.boundary_square_ok}",
        ]
        if self.issues:
            lines.append("  issues:")
            for issue in self.issues:
                lines.append(f"    - {issue}")
        return "\n".join(lines)


def validate_complex(complex_: SimplicialComplex) -> GeometryDiagnostics:
    """Run structural checks. Does **not** assert manifold properties."""
    issues: List[str] = []

    if complex_.n_vertices() == 0:
        issues.append("complex has no vertices")

    for s in complex_.top_simplices():
        if s.dimension != complex_.dimension:
            issues.append(
                f"top simplex {s.vertices} has dim {s.dimension}, "
                f"expected {complex_.dimension}"
            )

    boundary_ok = True
    for s in complex_.top_simplices():
        if not boundary_square_is_zero(s):
            boundary_ok = False
            issues.append(f"∂² ≠ 0 on simplex {s.vertices}")
            break

    components = complex_.connected_components()
    n_comp = len(components)
    connected = n_comp <= 1

    if complex_.n_top_simplices() == 0 and complex_.n_vertices() > 0:
        issues.append("vertices present but no top simplices")

    ok = len(issues) == 0 and boundary_ok

    return GeometryDiagnostics(
        ok=ok,
        dimension=complex_.dimension,
        n_vertices=complex_.n_vertices(),
        n_top_simplices=complex_.n_top_simplices(),
        connected=connected,
        n_components=n_comp,
        boundary_square_ok=boundary_ok,
        issues=issues,
    )
