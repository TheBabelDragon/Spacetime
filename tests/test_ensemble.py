"""CDT ensemble tests — reproducibility, stats edge cases, RNG parity."""

from __future__ import annotations

import hashlib
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
from spacetime.ensemble.stats import mean, sample_variance, std_error, ci95, aggregate_series


def test_invalid_config_rejected():
    with pytest.raises(ValueError):
        validate_config(EnsembleConfig(n_spatial=2))
    with pytest.raises(ValueError):
        validate_config(EnsembleConfig(n_geometries=0))
    with pytest.raises(ValueError):
        validate_config(EnsembleConfig(sigma_max=1))


def test_geometry_seed_derivation():
    assert geometry_seed(0, 0) == 10007
    assert geometry_seed(0, 1) == 20014


def test_mulberry32_known_vectors():
    r = Mulberry32(0)
    assert [r.next_u32() for _ in range(5)] == [
        1144304738, 1416247, 958946056, 627933444, 2007157716
    ]
    r = Mulberry32(42)
    assert [r.next_u32() for _ in range(5)] == [
        2581720956, 1925393290, 3661312704, 2876485805, 750819978
    ]


def test_stats_n0_n1_n2_edge_cases():
    assert mean([]) is None
    assert sample_variance([]) is None
    assert std_error([]) is None
    assert ci95([]) == (None, None)
    assert mean([3.5]) == 3.5
    assert sample_variance([3.5]) is None
    assert std_error([3.5]) is None
    assert ci95([3.5]) == (None, None)
    xs = [1.0, 3.0]
    assert mean(xs) == 2.0
    assert sample_variance(xs) == 2.0
    assert abs(std_error(xs) - math.sqrt(1.0)) < 1e-12


def test_aggregate_series_null_uncertainty():
    agg = aggregate_series([[1.0, 2.0]])
    assert agg["variance"] == [None, None]
    assert agg["stderr"] == [None, None]
    assert agg["ci95_method"] == "normal_approx_1.96_stderr"
    agg2 = aggregate_series([[1.0], [3.0]])
    assert agg2["variance"] == [2.0]
    assert agg2["stderr"][0] is not None


def test_small_ensemble_runs():
    cfg = EnsembleConfig(n_spatial=3, n_time=2, n_geometries=5, master_seed=7, sigma_max=10, n_starts=4)
    result = run_ensemble(cfg)
    assert result.to_dict()["experiment_class"] == "fixed_geometry_sampling_ensemble"


def test_bit_identical_fingerprint():
    cfg = EnsembleConfig(n_spatial=4, n_time=3, n_geometries=20, master_seed=123, sigma_max=15, n_starts=8)
    r1 = run_ensemble(cfg)
    r2 = run_ensemble(cfg)
    assert r1.canonical_payload() == r2.canonical_payload()
    assert r1.canonical_fingerprint() == r2.canonical_fingerprint()
    assert len(r1.canonical_fingerprint()) == 64
    assert r1.canonical_fingerprint() == hashlib.sha256(r1.canonical_payload().encode()).hexdigest()


def test_execution_order_independence():
    cfg = EnsembleConfig(n_spatial=3, n_time=2, n_geometries=3, master_seed=1, sigma_max=8, n_starts=3)
    g_fwd = [run_geometry(cfg, i) for i in range(3)]
    g_rev = sorted([run_geometry(cfg, i) for i in reversed(range(3))], key=lambda g: g.geometry_index)
    for a, b in zip(g_fwd, g_rev):
        assert a.seed == b.seed and a.P == b.P


def test_adding_run_preserves_prefix():
    r10 = run_ensemble(EnsembleConfig(n_spatial=3, n_time=2, n_geometries=10, master_seed=99, sigma_max=8, n_starts=4))
    r11 = run_ensemble(EnsembleConfig(n_spatial=3, n_time=2, n_geometries=11, master_seed=99, sigma_max=8, n_starts=4))
    for i in range(10):
        assert r10.geometries[i].to_dict() == r11.geometries[i].to_dict()


def test_acceptance_100_fixed_geometry_sampling():
    cfg = EnsembleConfig(n_spatial=4, n_time=3, n_geometries=100, master_seed=2026, sigma_max=20, n_starts=8)
    r1 = run_ensemble(cfg)
    r2 = run_ensemble(cfg)
    assert len(r1.geometries) == 100
    assert r1.canonical_fingerprint() == r2.canonical_fingerprint()


def test_export_roundtrip_fields():
    result = run_ensemble(EnsembleConfig(n_geometries=3, master_seed=2, sigma_max=5, n_starts=2))
    data = json.loads(export_json(result))
    assert data["experiment_class"] == "fixed_geometry_sampling_ensemble"
    assert data["P_ensemble"]["ci95_method"] == "normal_approx_1.96_stderr"
    assert "P_mean" in export_csv_p(result)
    assert "Ds_mean" in export_csv_ds(result)


def test_fingerprint_no_nan_tokens():
    r = run_ensemble(EnsembleConfig(n_geometries=2, master_seed=0, sigma_max=5, n_starts=2))
    assert "nan" not in r.canonical_payload().lower()
    assert len(r.canonical_fingerprint()) == 64
