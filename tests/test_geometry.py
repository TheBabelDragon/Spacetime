"""Core simplicial geometry tests."""

from __future__ import annotations

import pytest

from spacetime.geometry import (
    OrientedSimplex,
    SimplicialComplex,
    boundary,
    boundary_square_is_zero,
    validate_complex,
)
from spacetime.observables import euler_characteristic, simplex_counts


def test_oriented_simplex_canonical():
    s = OrientedSimplex.from_vertices([2, 0, 1])
    assert s.vertices == (0, 1, 2)
    # permutation 2,0,1 → sorted 0,1,2: inversions (2,0),(2,1) = 2 even → +1
    assert s.orientation == 1


def test_oriented_simplex_odd_permutation():
    s = OrientedSimplex.from_vertices([1, 0, 2])
    assert s.vertices == (0, 1, 2)
    assert s.orientation == -1  # one inversion


def test_opposite():
    s = OrientedSimplex((0, 1, 2), 1)
    assert s.opposite().orientation == -1
    assert s.opposite().vertices == (0, 1, 2)


def test_face_orientation():
    s = OrientedSimplex((0, 1, 2), 1)
    f0 = s.face(0)  # omit 0 → (1,2), sign (+1)
    assert f0.vertices == (1, 2)
    assert f0.orientation == 1
    f1 = s.face(1)  # omit 1 → (0,2), sign (-1)
    assert f1.vertices == (0, 2)
    assert f1.orientation == -1


def test_boundary_of_triangle():
    s = OrientedSimplex((0, 1, 2), 1)
    chain = boundary(s)
    # ∂[0,1,2] = [1,2] - [0,2] + [0,1]
    keys = {k.vertices: k.orientation * c for k, c in chain.items()}
    assert keys[(1, 2)] == 1
    assert keys[(0, 2)] == -1
    assert keys[(0, 1)] == 1
    assert len(keys) == 3


def test_boundary_square_zero_triangle():
    s = OrientedSimplex((0, 1, 2), 1)
    assert boundary_square_is_zero(s)


def test_boundary_square_zero_tetrahedron():
    s = OrientedSimplex((0, 1, 2, 3), 1)
    assert boundary_square_is_zero(s)
    assert s.dimension == 3


def test_boundary_square_zero_edge():
    s = OrientedSimplex((0, 1), 1)
    assert boundary_square_is_zero(s)


def test_simplicial_complex_add():
    c = SimplicialComplex(dimension=2)
    c.add_vertices(3)
    c.add_simplex([0, 1, 2])
    assert c.n_top_simplices() == 1
    assert c.n_vertices() == 3
    assert c.has_simplex([2, 0, 1])


def test_duplicate_opposite_orientation_raises():
    c = SimplicialComplex(dimension=2)
    c.add_simplex([0, 1, 2], 1)
    with pytest.raises(ValueError, match="opposite orientation"):
        c.add_simplex([0, 1, 2], -1)


def test_connected_components():
    c = SimplicialComplex(dimension=1)
    c.add_simplex([0, 1], allow_lower=True)
    c.add_simplex([2, 3], allow_lower=True)
    comps = c.connected_components()
    assert len(comps) == 2


def test_serialization_roundtrip():
    c = SimplicialComplex(dimension=2)
    c.add_simplex([0, 1, 2])
    c.add_simplex([0, 1, 3])
    text = c.to_json()
    c2 = SimplicialComplex.from_json(text)
    assert c2.n_top_simplices() == 2
    assert c2.n_vertices() == 4
    assert c2.has_simplex([0, 1, 2])
    assert c2.check_boundary_square()


def test_validate_complex_ok():
    c = SimplicialComplex(dimension=2)
    c.add_simplex([0, 1, 2])
    diag = validate_complex(c)
    assert diag.ok
    assert diag.boundary_square_ok


def test_tetrahedron_euler():
    """Boundary of a 3-simplex is an S² triangulation: χ = 2."""
    c = SimplicialComplex(dimension=2)
    for face in ([0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]):
        c.add_simplex(face)
    assert simplex_counts(c)[0] == 4
    assert simplex_counts(c)[1] == 6
    assert simplex_counts(c)[2] == 4
    assert euler_characteristic(c) == 2


def test_empty_complex_boundary_ok():
    c = SimplicialComplex(dimension=2)
    assert c.check_boundary_square()
