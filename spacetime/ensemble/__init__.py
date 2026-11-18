"""CDT ensemble engine — reproducible multi-geometry experiments.

Authoritative numerical path for published claims (Python).
Browser Observatory may mirror algorithms for interactive previews;
results must not be silently mixed.
"""

from spacetime.ensemble.config import EnsembleConfig, validate_config
from spacetime.ensemble.engine import run_ensemble, EnsembleResult
from spacetime.ensemble.export import export_json, export_csv_p, export_csv_ds

__all__ = [
    "EnsembleConfig",
    "validate_config",
    "run_ensemble",
    "EnsembleResult",
    "export_json",
    "export_csv_p",
    "export_csv_ds",
]
