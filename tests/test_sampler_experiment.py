"""Sampler and experiment reproducibility tests."""

from __future__ import annotations

from spacetime.experiment import ExperimentConfig, run_cdt2d_experiment
from spacetime.models.cdt2d import CDT2DConfig
from spacetime.samplers import CDT2DSampler, SamplerConfig


def test_sampler_initial_valid():
    cfg = CDT2DConfig(n_spatial=4, n_time=3)
    sc = SamplerConfig(seed=42, n_sweeps=5)
    sampler = CDT2DSampler(cfg, sc)
    stats = sampler.run_sweeps()
    assert stats.proposed == 5
    assert stats.accepted == 5
    assert stats.acceptance_rate == 1.0


def test_seeded_reproducibility():
    cfg = CDT2DConfig(n_spatial=3, n_time=2)
    s1 = CDT2DSampler(cfg, SamplerConfig(seed=7, n_sweeps=10))
    s1.run_sweeps()
    snap1 = s1.snapshot()

    s2 = CDT2DSampler(cfg, SamplerConfig(seed=7, n_sweeps=10))
    s2.run_sweeps()
    snap2 = s2.snapshot()

    assert snap1["action"] == snap2["action"]
    assert snap1["stats"] == snap2["stats"]


def test_experiment_runs():
    exp = ExperimentConfig(
        experiment_id="cdt2d-smoke-001",
        n_spatial=4,
        n_time=3,
        seed=1,
        n_sweeps=3,
        kappa0=0.0,
        kappa2=1.0,
    )
    result = run_cdt2d_experiment(exp)
    assert result.validation_ok
    assert result.n_triangles == 16
    assert result.action == 16.0
    assert result.sampler_stats["accepted"] == 3


def test_experiment_json_roundtrip_fields():
    exp = ExperimentConfig(experiment_id="x", n_spatial=3, n_time=2, seed=0)
    result = run_cdt2d_experiment(exp, include_snapshot=True)
    data = result.to_dict()
    assert data["config"]["experiment_id"] == "x"
    assert "triangulation_snapshot" in data
    assert data["validation_ok"] is True
