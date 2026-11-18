"""Ensemble aggregate statistics across geometries only."""

from __future__ import annotations

import math
from typing import List, Optional, Sequence


def mean(xs: Sequence[float]) -> float:
    if not xs:
        return float("nan")
    return sum(xs) / len(xs)


def sample_variance(xs: Sequence[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (n - 1)


def std_dev(xs: Sequence[float]) -> float:
    return math.sqrt(sample_variance(xs))


def std_error(xs: Sequence[float]) -> float:
    n = len(xs)
    if n < 1:
        return float("nan")
    if n == 1:
        return 0.0
    return std_dev(xs) / math.sqrt(n)


def ci95(xs: Sequence[float]) -> tuple[float, float]:
    m = mean(xs)
    se = std_error(xs)
    half = 1.96 * se
    return m - half, m + half


def aggregate_series(series_list: Sequence[Sequence[Optional[float]]]) -> dict:
    if not series_list:
        return {
            "mean": [], "variance": [], "std": [], "stderr": [],
            "ci95_low": [], "ci95_high": [], "n_valid": [],
            "ci95_method": "normal_approx_1.96_stderr",
        }
    n_steps = len(series_list[0])
    means: List[Optional[float]] = []
    variances: List[Optional[float]] = []
    stds: List[Optional[float]] = []
    stderrs: List[Optional[float]] = []
    lo: List[Optional[float]] = []
    hi: List[Optional[float]] = []
    n_valid: List[int] = []
    for t in range(n_steps):
        vals = [
            float(s[t])
            for s in series_list
            if s[t] is not None and math.isfinite(float(s[t]))
        ]
        n_valid.append(len(vals))
        if not vals:
            means.append(None)
            variances.append(None)
            stds.append(None)
            stderrs.append(None)
            lo.append(None)
            hi.append(None)
            continue
        means.append(mean(vals))
        variances.append(sample_variance(vals))
        stds.append(std_dev(vals))
        stderrs.append(std_error(vals))
        a, b = ci95(vals)
        lo.append(a)
        hi.append(b)
    return {
        "mean": means,
        "variance": variances,
        "std": stds,
        "stderr": stderrs,
        "ci95_low": lo,
        "ci95_high": hi,
        "n_valid": n_valid,
        "ci95_method": "normal_approx_1.96_stderr",
    }
