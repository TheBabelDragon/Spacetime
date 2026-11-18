"""Validated ensemble experiment configuration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Literal


SCHEMA_VERSION = "ensemble/v1"
ALGORITHM_VERSION = "cdt2d-flat+rw-primal/0.3.0"
ENGINE_VERSION = "0.3.0"

StartPolicy = Literal["uniform_seeded"]


@dataclass(frozen=True)
class EnsembleConfig:
    """Configuration for a reproducible CDT ensemble experiment.

    Geometry (v0.3): flat 2D CDT cylinder/torus for (N, T, periodic_time).
    Independent per-geometry RNG streams control diffusion start sampling.
    """

    n_spatial: int = 4
    n_time: int = 3
    periodic_time: bool = False
    n_geometries: int = 10
    master_seed: int = 0
    sigma_max: int = 20
    n_starts: int = 8
    start_policy: StartPolicy = "uniform_seeded"
    schema_version: str = SCHEMA_VERSION
    algorithm_version: str = ALGORITHM_VERSION
    engine_version: str = ENGINE_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_config(cfg: EnsembleConfig) -> EnsembleConfig:
    if cfg.n_spatial < 3:
        raise ValueError("n_spatial must be ≥ 3")
    if cfg.n_time < 2:
        raise ValueError("n_time must be ≥ 2")
    if cfg.n_geometries < 1:
        raise ValueError("n_geometries must be ≥ 1")
    if cfg.n_geometries > 10_000:
        raise ValueError("n_geometries exceeds hard limit 10000")
    if cfg.sigma_max < 2:
        raise ValueError("sigma_max must be ≥ 2")
    if cfg.sigma_max > 10_000:
        raise ValueError("sigma_max exceeds hard limit 10000")
    if cfg.n_starts < 1:
        raise ValueError("n_starts must be ≥ 1")
    if cfg.master_seed < 0:
        raise ValueError("master_seed must be ≥ 0")
    if cfg.start_policy not in ("uniform_seeded",):
        raise ValueError(f"unsupported start_policy: {cfg.start_policy}")
    return cfg
