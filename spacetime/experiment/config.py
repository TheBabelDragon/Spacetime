"""Experiment configuration and result records."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from spacetime import __version__


@dataclass
class ExperimentConfig:
    experiment_id: str
    model: str = "cdt2d"
    model_version: str = "0.1.0"
    n_spatial: int = 4
    n_time: int = 3
    periodic_time: bool = False
    seed: int = 0
    n_sweeps: int = 0
    kappa0: float = 0.0
    kappa2: float = 1.0
    software_version: str = field(default_factory=lambda: __version__)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict) -> ExperimentConfig:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ExperimentResult:
    config: ExperimentConfig
    validation_ok: bool
    action: float
    n_triangles: int
    euler_char: int
    sampler_stats: Dict[str, Any]
    executed_at: str
    diagnostics_summary: str
    triangulation_snapshot: Optional[dict] = None

    def to_dict(self) -> dict:
        d = {
            "config": self.config.to_dict(),
            "validation_ok": self.validation_ok,
            "action": self.action,
            "n_triangles": self.n_triangles,
            "euler_char": self.euler_char,
            "sampler_stats": self.sampler_stats,
            "executed_at": self.executed_at,
            "diagnostics_summary": self.diagnostics_summary,
        }
        if self.triangulation_snapshot is not None:
            d["triangulation_snapshot"] = self.triangulation_snapshot
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
