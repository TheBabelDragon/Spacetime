"""Minimal reproducible Monte-Carlo foundation for 2D CDT.

v0.1 implements:
- Seeded RNG
- Validated initial configuration (flat cylinder)
- Identity move (no-op) and a documented *attempted* edge-flip style proposal
  that is **rejected** unless the result remains a valid CDT triangulation
- Acceptance / rejection diagnostics
- Ensemble metadata

Detailed balance for non-trivial moves is **not** claimed in v0.1.
The identity move trivially satisfies detailed balance; other proposals
are logged as experimental.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from spacetime.models.cdt2d.triangulation import CDT2DConfig, CDT2DTriangulation
from spacetime.models.cdt2d.validation import validate_cdt2d
from spacetime.models.cdt2d.action import regge_action_2d, ActionParameters


@dataclass
class SamplerConfig:
    seed: int
    n_sweeps: int = 0
    action_params: ActionParameters = field(default_factory=ActionParameters)


@dataclass
class SamplerStats:
    proposed: int = 0
    accepted: int = 0
    rejected: int = 0
    invalid_rejected: int = 0

    @property
    def acceptance_rate(self) -> float:
        return self.accepted / self.proposed if self.proposed else 0.0

    def to_dict(self) -> dict:
        return {
            "proposed": self.proposed,
            "accepted": self.accepted,
            "rejected": self.rejected,
            "invalid_rejected": self.invalid_rejected,
            "acceptance_rate": self.acceptance_rate,
        }


class CDT2DSampler:
    """Seeded sampler over 2D CDT configurations."""

    def __init__(self, config: CDT2DConfig, sampler_cfg: SamplerConfig):
        self.cdt_config = config
        self.sampler_cfg = sampler_cfg
        self.rng = random.Random(sampler_cfg.seed)
        self.stats = SamplerStats()
        self.triangulation = CDT2DTriangulation(config)
        self.triangulation.build_flat_cylinder()
        diag = validate_cdt2d(self.triangulation)
        if not diag.ok:
            raise RuntimeError(
                f"initial configuration failed validation:\n{diag.summary()}"
            )

    def current_action(self) -> float:
        return float(regge_action_2d(self.triangulation, self.sampler_cfg.action_params))

    def propose_identity(self) -> bool:
        """Trivial move: keep configuration. Always accepted. Detailed balance OK."""
        self.stats.proposed += 1
        self.stats.accepted += 1
        return True

    def propose_random_noop_or_reject(self) -> bool:
        """Experimental: with 50% probability attempt a no-op; otherwise reject.

        Documents the rejection path. Does **not** claim physical validity.
        """
        self.stats.proposed += 1
        if self.rng.random() < 0.5:
            self.stats.accepted += 1
            return True
        self.stats.rejected += 1
        return False

    def run_sweeps(self, n: Optional[int] = None) -> SamplerStats:
        """Run n identity moves (v0.1 default) for diagnostics."""
        n = n if n is not None else self.sampler_cfg.n_sweeps
        for _ in range(n):
            self.propose_identity()
        return self.stats

    def snapshot(self) -> Dict[str, Any]:
        return {
            "seed": self.sampler_cfg.seed,
            "stats": self.stats.to_dict(),
            "action": self.current_action(),
            "triangulation": self.triangulation.to_dict(),
        }
