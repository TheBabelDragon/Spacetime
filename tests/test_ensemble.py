"""CDT ensemble engine tests — reproducibility and statistics."""

from __future__ import annotations

import json
import math

import pytest

from spacetime.ensemble import (
    EnsembleConfig,
    export_csv_ds,
    export_csv_p,
    export_json,
    run_ensemble,
    validate_config,
)
from spacetime.ensemble.engine import run_geometry
from spacetime.ensemble.rng import Mulberry32, geometry_seed
from spacetime.ensemble.stats import mean, sample_variance, std_error, ci95


def test_invalid_config_rejected():
    with pytest.raises(ValueError):
        validate_config(EnsembleConfig(n_spatial=2))
    with pytest.raises(ValueError):
        validate_config(EnsembleConfig(n_time=1))
    with pytest.raises(ValueError):
        validate_config(EnsembleConfig(n_geometries=0))
    with pytest.raises(ValueError):
        validate_config(EnsembleConfig(sigma_max=1))
    with pytest.raises(ValueError):
        validate_config(EnsembleConfig(n_starts=0))


def test_geometry_seed_derivation():
    assert geometry_seed(0, 0) == 10007
    assert geometry_seed(0, 1) == 20014
    assert geometry_seed(1, 0) == 10008


def test_mulberry32_deterministic():
    a = Mulberry32(42)
    b = Mulberry32(42)
    assert [a.next_u32() for _ in range(20)] == [b.next_u32() for _ in range(20)]


def test_stats_hand_fixtures():
    xs = [1.0, 2.0, 3.0]
    assert mean(xs) == 2.0
    assert abs(sample_variance(xs) - 1.0) < 1e-12
    assert abs(std_error(xs) - math.sqrt(1.0 / 3.0)) < 1e-12
    lo, hi = ci95(xs)
    assert lo < 2.0 < hi


def test_small_ensemble_runs():
    cfg = EnsembleConfig(
        n_spatial=3, n_time=2, n_geometries=5, master_seed=7, sigma_max=10, n_starts=4
    )
    result = run_ensemble(cfg)
    assert len(result.geometries) == 5
    assert result.geometries[0].n2 == 6
    assert len(result.sigma) == 10
    assert result.P_ensemble["n_valid"][0] == 5


def test_bit_identical_repeat():
    cfg = EnsembleConfig(
        n_spatial=4, n_time=3, n_geometries=20, master_seed=123, sigma_max=15, n_starts=8
    )
    r1 = run_ensemble(cfg)
    r2 = run_ensemble(cfg)
    assert r1.canonical_fingerprint() == r2.canonical_fingerprint()


def test_execution_order_independence():
    cfg = EnsembleConfig(
        n_spatial=3, n_time=2, n_geometries=3, master_seed=1, sigma_max=8, n_starts=3
    )
    g_fwd = [run_geometry(cfg, i) for i in range(3)]
    g_rev = [run_geometry(cfg, i) for i in reversed(range(3))]
    g_rev_sorted = sorted(g_rev, key=lambda g: g.geometry_index)
    for a, b in zip(g_fwd, g_rev_sorted):
        assert a.seed == b.seed
        assert a.P == b.P
        assert a.Ds == b.Ds


def test_adding_geometry_preserves_prefix():
    cfg100 = EnsembleConfig(
        n_spatial=3, n_time=2, n_geometries=10, master_seed=99, sigma_max=8, n_starts=4
    )
    cfg101 = EnsembleConfig(
        n_spatial=3, n_time=2, n_geometries=11, master_seed=99, sigma_max=8, n_starts=4
    )
    r10 = run_ensemble(cfg100)
    r11 = run_ensemble(cfg101)
    for i in range(10):
        assert r10.geometries[i].to_dict() == r11.geometries[i].to_dict()


def test_acceptance_100_geometries_reproducible():
    cfg = EnsembleConfig(
        n_spatial=4, n_time=3, n_geometries=100, master_seed=2026, sigma_max=20, n_starts=8
    )
    r1 = run_ensemble(cfg)
    r2 = run_ensemble(cfg)
    assert len(r1.geometries) == 100
    assert r1.canonical_fingerprint() == r2.canonical_fingerprint()
    assert all(math.isfinite(x) for x in r1.P_ensemble["mean"] if x is not None)


def test_export_roundtrip_fields():
    cfg = EnsembleConfig(n_geometries=3, master_seed=2, sigma_max=5, n_starts=2)
    result = run_ensemble(cfg)
    js = export_json(result)
    data = json.loads(js)
    assert data["source"] == "python"
    assert data["format"] == "spacetime-ensemble-manifest/v1"
    assert len(data["geometries"]) == 3
    assert "P_mean" in export_csv_p(result)
    assert "Ds_mean" in export_csv_ds(result)


def test_no_silent_nan_success_in_fingerprint():
    cfg = EnsembleConfig(n_geometries=2, master_seed=0, sigma_max=5, n_starts=2)
    r = run_ensemble(cfg)
    fp = r.canonical_fingerprint()
    assert "nan" not in fp.lower()
