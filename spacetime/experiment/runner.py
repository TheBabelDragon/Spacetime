"""Execute a CDT-2D experiment and produce a reproducible record."""

from __future__ import annotations

from datetime import datetime, timezone

from spacetime.experiment.config import ExperimentConfig, ExperimentResult
from spacetime.models.cdt2d.action import ActionParameters, regge_action_2d, volume_n2
from spacetime.models.cdt2d.triangulation import CDT2DConfig
from spacetime.models.cdt2d.validation import validate_cdt2d
from spacetime.observables.combinatorics import euler_characteristic
from spacetime.samplers.cdt2d_mc import CDT2DSampler, SamplerConfig


def run_cdt2d_experiment(
    config: ExperimentConfig,
    *,
    include_snapshot: bool = False,
) -> ExperimentResult:
    """Build initial config, optionally run identity sweeps, record results."""
    cdt_cfg = CDT2DConfig(
        n_spatial=config.n_spatial,
        n_time=config.n_time,
        periodic_time=config.periodic_time,
    )
    action_params = ActionParameters(kappa0=config.kappa0, kappa2=config.kappa2)
    sampler_cfg = SamplerConfig(
        seed=config.seed,
        n_sweeps=config.n_sweeps,
        action_params=action_params,
    )
    sampler = CDT2DSampler(cdt_cfg, sampler_cfg)
    if config.n_sweeps > 0:
        sampler.run_sweeps(config.n_sweeps)

    diag = validate_cdt2d(sampler.triangulation)
    action = float(regge_action_2d(sampler.triangulation, action_params))
    n2 = volume_n2(sampler.triangulation)
    chi = euler_characteristic(sampler.triangulation.complex)

    return ExperimentResult(
        config=config,
        validation_ok=diag.ok,
        action=action,
        n_triangles=n2,
        euler_char=chi,
        sampler_stats=sampler.stats.to_dict(),
        executed_at=datetime.now(timezone.utc).isoformat(),
        diagnostics_summary=diag.summary(),
        triangulation_snapshot=sampler.triangulation.to_dict() if include_snapshot else None,
    )
