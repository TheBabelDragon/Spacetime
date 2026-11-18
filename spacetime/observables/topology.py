"""Lightweight topological diagnostics (not a full manifold checker)."""

from __future__ import annotations

from spacetime.geometry.complex import SimplicialComplex


def is_closed_surface_candidate(complex_: SimplicialComplex) -> bool:
    """Heuristic: 2-complex, connected, every edge shared by exactly two triangles."""
    if complex_.dimension != 2:
        return False
    if not complex_.is_connected():
        return False
    from collections import Counter

    edge_count: Counter = Counter()
    for s in complex_.top_simplices():
        v = s.vertices
        for e in ((v[0], v[1]), (v[0], v[2]), (v[1], v[2])):
            edge_count[e] += 1
    return all(c == 2 for c in edge_count.values()) and len(edge_count) > 0
