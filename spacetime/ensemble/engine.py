"""Run a full CDT ensemble experiment (authoritative Python path)."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import List, Optional

from spacetime.ensemble.config import EnsembleConfig, validate_config
from spacetime.ensemble.diffusion import (
    primal_adjacency_from_edges,
    return_probabilities,
    spectral_dimension,
)
from spacetime.ensemble.rng import Mulberry32, geometry_seed
from spacetime.ensemble.stats import aggregate_series
from spacetime.models.cdt2d.triangulation import CDT2DConfig, CDT2DTriangulation


def _json_safe(obj):
    if isinstance(obj, float):
        if not math.isfinite(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


@dataclass
class GeometryRecord:
    geometry_index: int
    seed: int
    n0: int
    n2: int
    sigma: List[int]
    P: List[float]
    Ds_sigma: List[int]
    Ds: List[Optional[float]]
    n_starts_used: int

    def to_dict(self) -> dict:
        return {
            "geometry_index": self.geometry_index,
            "seed": self.seed,
            "n0": self.n0,
            "n2": self.n2,
            "n_starts_used": self.n_starts_used,
            "sigma": self.sigma,
            "P": self.P,
            "Ds_sigma": self.Ds_sigma,
            "Ds": self.Ds,
        }


@dataclass
class EnsembleResult:
    config: EnsembleConfig
    geometries: List[GeometryRecord]
    sigma: List[int]
    P_ensemble: dict
    Ds_ensemble: dict
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return _json_safe({
            "format": "spacetime-ensemble-manifest/v1",
            "source": "python",
            "config": self.config.to_dict(),
            "notes": self.notes,
            "sigma": self.sigma,
            "P_ensemble": self.P_ensemble,
            "Ds_ensemble": self.Ds_ensemble,
            "geometries": [g.to_dict() for g in self.geometries],
            "n_geometries": len(self.geometries),
        })

    def canonical_fingerprint(self) -> str:
        payload = {
            "config": self.config.to_dict(),
            "sigma": self.sigma,
            "P_ensemble": self.P_ensemble,
            "Ds_ensemble": {
                k: self.Ds_ensemble[k]
                for k in (
                    "mean", "variance", "std", "stderr",
                    "ci95_low", "ci95_high", "n_valid", "ci95_method",
                )
                if k in self.Ds_ensemble
            },
            "geometries": [
                {
                    "geometry_index": g.geometry_index,
                    "seed": g.seed,
                    "n0": g.n0,
                    "n2": g.n2,
                    "n_starts_used": g.n_starts_used,
                    "sigma": g.sigma,
                    "P": g.P,
                    "Ds_sigma": g.Ds_sigma,
                    "Ds": g.Ds,
                }
                for g in self.geometries
            ],
        }
        return json.dumps(_json_safe(payload), sort_keys=True, separators=(",", ":"), allow_nan=False)


def _edges_from_tri(tri: CDT2DTriangulation) -> List[tuple[int, int]]:
    return [(a, b) for a, b in tri.complex.edges()]


def run_geometry(cfg: EnsembleConfig, geometry_index: int) -> GeometryRecord:
    seed = geometry_seed(cfg.master_seed, geometry_index)
    cdt = CDT2DConfig(
        n_spatial=cfg.n_spatial,
        n_time=cfg.n_time,
        periodic_time=cfg.periodic_time,
    )
    tri = CDT2DTriangulation(cdt)
    tri.build_flat_cylinder()
    adj = primal_adjacency_from_edges(_edges_from_tri(tri))
    rng = Mulberry32(seed)
    sigma, P, n_used = return_probabilities(adj, cfg.sigma_max, cfg.n_starts, rng)
    ds_s, ds = spectral_dimension(sigma, P)
    return GeometryRecord(
        geometry_index=geometry_index,
        seed=seed,
        n0=tri.complex.n_vertices(),
        n2=tri.complex.n_top_simplices(),
        sigma=sigma,
        P=P,
        Ds_sigma=ds_s,
        Ds=ds,
        n_starts_used=n_used,
    )


def run_ensemble(cfg: EnsembleConfig) -> EnsembleResult:
    cfg = validate_config(cfg)
    geos = [run_geometry(cfg, i) for i in range(cfg.n_geometries)]
    if not geos:
        raise RuntimeError("no geometries produced")
    sigma = geos[0].sigma
    p_series = [g.P for g in geos]
    ds_series = [list(g.Ds) for g in geos]
    notes = [
        "source=python authoritative engine",
        "graph=primal (not dual)",
        "geometry_v0.3=flat_cylinder_or_torus (combinatorially identical for fixed N,T,periodic)",
        "ensemble_independence=per_geometry diffusion start streams derived from master_seed",
        "ci95=normal_approx 1.96*stderr across geometries",
        "no continuum-limit claims",
    ]
    return EnsembleResult(
        config=cfg,
        geometries=geos,
        sigma=sigma,
        P_ensemble=aggregate_series(p_series),
        Ds_ensemble=aggregate_series(ds_series),
        notes=notes,
    )
