"""Ensemble aggregate statistics across independent sampling runs.

| n_valid | mean | variance | stderr | CI95 |
|---------|------|----------|--------|------|
| 0       | null | null     | null   | null |
| 1       | yes  | null     | null   | null |
| ≥2      | yes  | yes      | yes    | yes  |

CI95 method: normal_approx_1.96_stderr (not Student-t).
Never report zero uncertainty for n_valid < 2.
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence


def mean(xs: Sequence[float]) -> Optional[float]:
    if not xs:
        return None
    return sum(xs) / len(xs)


def sample_variance(xs: Sequence[float]) -> Optional[float]:
    n = len(xs)
    if n < 2:
        return None
    m = mean(xs)
    assert m is not None
    return sum((x - m) ** 2 for x in xs) / (n - 1)


def std_dev(xs: Sequence[float]) -> Optional[float]:
    v = sample_variance(xs)
    if v is None:
        return None
    return math.sqrt(v)


def std_error(xs: Sequence[float]) -> Optional[float]:
    n = len(xs)
    if n < 2:
        return None
    sd = std_dev(xs)
    if sd is None:
        return None
    return sd / math.sqrt(n)


def ci95(xs: Sequence[float]) -> tuple[Optional[float], Optional[float]]:
    m = mean(xs)
    se = std_error(xs)
    if m is None or se is None:
        return None, None
    half = 1.96 * se
    return m - half, m + half


def aggregate_series(series_list: Sequence[Sequence[Optional[float]]]) -> dict:
    empty = {
        "mean": [], "variance": [], "std": [], "stderr": [],
        "ci95_low": [], "ci95_high": [], "n_valid": [],
        "ci95_method": "normal_approx_1.96_stderr",
    }
    if not series_list:
        return empty
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
            means.append(None); variances.append(None); stds.append(None)
            stderrs.append(None); lo.append(None); hi.append(None)
            continue
        means.append(mean(vals))
        variances.append(sample_variance(vals))
        stds.append(std_dev(vals))
        stderrs.append(std_error(vals))
        a, b = ci95(vals)
        lo.append(a); hi.append(b)
    return {
        "mean": means, "variance": variances, "std": stds, "stderr": stderrs,
        "ci95_low": lo, "ci95_high": hi, "n_valid": n_valid,
        "ci95_method": "normal_approx_1.96_stderr",
    }
