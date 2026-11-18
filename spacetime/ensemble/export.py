"""JSON and CSV export of ensemble experiments."""

from __future__ import annotations

import csv
import io
import json
from typing import TextIO

from spacetime.ensemble.engine import EnsembleResult


def export_json(result: EnsembleResult, fp: TextIO | None = None) -> str:
    text = json.dumps(result.to_dict(), indent=2, sort_keys=True, allow_nan=False)
    if fp is not None:
        fp.write(text)
        if not text.endswith("\n"):
            fp.write("\n")
    return text


def export_csv_p(result: EnsembleResult, fp: TextIO | None = None) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["sigma", "P_mean", "P_std", "P_stderr", "P_ci95_low", "P_ci95_high", "n_valid"])
    agg = result.P_ensemble
    for i, s in enumerate(result.sigma):
        w.writerow([
            s, agg["mean"][i], agg["std"][i], agg["stderr"][i],
            agg["ci95_low"][i], agg["ci95_high"][i], agg["n_valid"][i],
        ])
    text = buf.getvalue()
    if fp is not None:
        fp.write(text)
    return text


def export_csv_ds(result: EnsembleResult, fp: TextIO | None = None) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["sigma", "Ds_mean", "Ds_std", "Ds_stderr", "Ds_ci95_low", "Ds_ci95_high", "n_valid"])
    ds_sigma = result.geometries[0].Ds_sigma if result.geometries else []
    agg = result.Ds_ensemble
    for i, s in enumerate(ds_sigma):
        w.writerow([
            s, agg["mean"][i], agg["std"][i], agg["stderr"][i],
            agg["ci95_low"][i], agg["ci95_high"][i], agg["n_valid"][i],
        ])
    text = buf.getvalue()
    if fp is not None:
        fp.write(text)
    return text
