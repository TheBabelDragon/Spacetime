"""2D CDT model tests."""

from __future__ import annotations

from fractions import Fraction

import pytest

from spacetime.models.cdt2d import (
    CDT2DConfig,
    CDT2DTriangulation,
    regge_action_2d,
    validate_cdt2d,
)
from spacetime.models.cdt2d.action import ActionParameters, volume_n2
from spacetime.observables import euler_characteristic


def test_config_validation():
    with pytest.raises(ValueError):
        CDT2DConfig(n_spatial=2, n_time=3)
    with pytest.raises(ValueError):
        CDT2DConfig(n_spatial=4, n_time=1)


def test_flat_cylinder_construction():
    cfg = CDT2DConfig(n_spatial=4, n_time=3, periodic_time=False)
    tri = CDT2DTriangulation(cfg)
    tri.build_flat_cylinder()
    # 2 time-gaps × 2 * N triangles each = 2 * 2 * 4 = 16
    assert tri.complex.n_top_simplices() == 2 * 2 * 4
    assert tri.complex.n_vertices() == 4 * 3


def test_flat_cylinder_validation():
    cfg = CDT2DConfig(n_spatial=5, n_time=4, periodic_time=False)
    tri = CDT2DTriangulation(cfg)
    tri.build_flat_cylinder()
    diag = validate_cdt2d(tri)
    assert diag.ok, diag.summary()
    assert diag.causal_ok
    assert diag.spatial_periodic_ok
    assert diag.foliation_ok


def test_periodic_time_torus():
    cfg = CDT2DConfig(n_spatial=4, n_time=3, periodic_time=True)
    tri = CDT2DTriangulation(cfg)
    tri.build_flat_cylinder()
    # 3 time-gaps (including wrap) × 2 * 4 = 24 triangles
    assert volume_n2(tri) == 3 * 2 * 4
    diag = validate_cdt2d(tri)
    assert diag.ok, diag.summary()


def test_cylinder_vs_torus_triangle_count():
    """Cylinder and torus constructions are combinatorially distinct."""
    N, T = 5, 4
    cyl = CDT2DTriangulation(CDT2DConfig(n_spatial=N, n_time=T, periodic_time=False))
    cyl.build_flat_cylinder()
    tor = CDT2DTriangulation(CDT2DConfig(n_spatial=N, n_time=T, periodic_time=True))
    tor.build_flat_cylinder()
    assert volume_n2(cyl) == 2 * N * (T - 1)
    assert volume_n2(tor) == 2 * N * T
    assert volume_n2(tor) == volume_n2(cyl) + 2 * N


def test_invalid_triangle_rejected():
    cfg = CDT2DConfig(n_spatial=4, n_time=3)
    tri = CDT2DTriangulation(cfg)
    with pytest.raises(ValueError, match="exactly two adjacent"):
        tri.add_triangle(0, 1, 2)


def test_non_adjacent_slices_rejected():
    cfg = CDT2DConfig(n_spatial=4, n_time=4)
    tri = CDT2DTriangulation(cfg)
    with pytest.raises(ValueError, match="not adjacent"):
        tri.add_triangle(0, 1, 8)  # 8 = vertex_id(2, 0, 4)


def test_action_volume_term():
    cfg = CDT2DConfig(n_spatial=4, n_time=3)
    tri = CDT2DTriangulation(cfg)
    tri.build_flat_cylinder()
    n2 = volume_n2(tri)
    assert n2 == 16
    S = regge_action_2d(tri, ActionParameters(kappa0=0, kappa2=1))
    assert S == Fraction(16)


def test_action_with_euler():
    cfg = CDT2DConfig(n_spatial=4, n_time=3)
    tri = CDT2DTriangulation(cfg)
    tri.build_flat_cylinder()
    chi = euler_characteristic(tri.complex)
    S = regge_action_2d(tri, ActionParameters(kappa0=2, kappa2=3))
    assert S == Fraction(2) * chi + Fraction(3) * 16


def test_hand_calculated_small_system():
    """N=3, T=2, open time: 1 time-gap × 2 × N = 6 triangles.

    Action with κ₂=1, κ₀=0 equals N₂ = 6.
    """
    cfg = CDT2DConfig(n_spatial=3, n_time=2)
    tri = CDT2DTriangulation(cfg)
    tri.build_flat_cylinder()
    assert volume_n2(tri) == 6
    S = regge_action_2d(tri, ActionParameters(kappa0=0, kappa2=1))
    assert S == 6
    diag = validate_cdt2d(tri)
    assert diag.ok, diag.summary()


def test_serialization_roundtrip_cdt():
    cfg = CDT2DConfig(n_spatial=4, n_time=2)
    tri = CDT2DTriangulation(cfg)
    tri.build_flat_cylinder()
    data = tri.to_dict()
    tri2 = CDT2DTriangulation.from_dict(data)
    assert volume_n2(tri2) == volume_n2(tri)
    assert validate_cdt2d(tri2).ok


def test_edge_classification():
    cfg = CDT2DConfig(n_spatial=4, n_time=2)
    tri = CDT2DTriangulation(cfg)
    tri.build_flat_cylinder()
    sl = tri.spacelike_edges()
    tl = tri.timelike_edges()
    assert len(sl) == 2 * 4  # two slices × N edges
    assert len(tl) > 0
    assert sl.isdisjoint(tl)
