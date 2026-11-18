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
    assert s.orientation == 1


def test_oriented_simplex_odd_permutation():
    s = OrientedSimplex.from_vertices([1, 0, 2])
    assert s.vertices == (0, 1, 2)
    assert s.orientation == -1


def test_opposite():
    s = OrientedSimplex((0, 1, 2), 1)
    assert s.opposite().orientation == -1
    assert s.opposite().vertices == (0, 1, 2)


def test_face_orientation():
    s = OrientedSimplex((0, 1, 2), 1)
    f0 = s.face(0)
    assert f0.vertices == (1, 2) and f0.orientation == 1
    f1 = s.face(1)
    assert f1.vertices == (0, 2) and f1.orientation == -1


def test_boundary_of_triangle():
    s = OrientedSimplex((0, 1, 2), 1)
    chain = boundary(s)
    keys = {k.vertices: k.orientation * coeff for k, coeff in chain.items()}
    assert keys[(1, 2)] == 1
    assert keys[(0, 2)] == -1
    assert keys[(0, 1)] == 1
    assert len(keys) == 3


def test_boundary_square_zero_triangle():
    assert boundary_square_is_zero(OrientedSimplex((0, 1, 2), 1))


def test_boundary_square_zero_tetrahedron():
    s = OrientedSimplex((0, 1, 2, 3), 1)
    assert boundary_square_is_zero(s)
    assert s.dimension == 3


def test_boundary_square_zero_edge():
    assert boundary_square_is_zero(OrientedSimplex((0, 1), 1))


def test_simplicial_complex_add():
    complex_ = SimplicialComplex(dimension=2)
    complex_.add_vertices(3)
    complex_.add_simplex([0, 1, 2])
    assert complex_.n_top_simplices() == 1
    assert complex_.n_vertices() == 3
    assert complex_.has_simplex([2, 0, 1])


def test_duplicate_opposite_orientation_raises():
    complex_ = SimplicialComplex(dimension=2)
    complex_.add_simplex([0, 1, 2], 1)
    with pytest.raises(ValueError, match="opposite orientation"):
        complex_.add_simplex([0, 1, 2], -1)


def test_connected_components():
    complex_ = SimplicialComplex(dimension=1)
    complex_.add_simplex([0, 1], allow_lower=True)
    complex_.add_simplex([2, 3], allow_lower=True)
    comps = complex_.connected_components()
    assert len(comps) == 2


def test_serialization_roundtrip():
    complex_ = SimplicialComplex(dimension=2)
    complex_.add_simplex([0, 1, 2])
    complex_.add_simplex([0, 1, 3])
    text = complex_.to_json()
    complex2 = SimplicialComplex.from_json(text)
    assert complex2.n_top_simplices() == 2
    assert complex2.n_vertices() == 4
    assert complex2.has_simplex([0, 1, 2])
    assert complex2.check_boundary_square()


def test_validate_complex_ok():
    complex_ = SimplicialComplex(dimension=2)
    complex_.add_simplex([0, 1, 2])
    diag = validate_complex(complex_)
    assert diag.ok
    assert diag.boundary_square_ok


def test_tetrahedron_euler():
    complex_ = SimplicialComplex(dimension=2)
    for face in ([0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]):
        complex_.add_simplex(face)
    assert simplex_counts(complex_)[0] == 4
    assert simplex_counts(complex_)[1] == 6
    assert simplex_counts(complex_)[2] == 4
    assert euler_characteristic(complex_) == 2


def test_empty_complex_boundary_ok():
    complex_ = SimplicialComplex(dimension=2)
    assert complex_.check_boundary_square()
