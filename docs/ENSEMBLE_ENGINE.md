# CDT Ensemble Engine (v0.3)

Authoritative path: **Python** (`spacetime.ensemble`).
Browser Observatory may mirror algorithms for interactive previews; do not mix sources in a published claim.

## Experiment class

**`fixed_geometry_sampling_ensemble`**

Each run uses the **same** flat 2D CDT cylinder/torus for fixed `(N, T, periodic_time)`.
Independent Mulberry32 streams control **diffusion start-vertex sampling only**.

This is **not** an ensemble of independent triangulations.

| Concept | This release |
|---------|--------------|
| Diffusion-start sampling variability | Yes |
| Geometry-to-geometry variability | **No** |

## RNG

- Mulberry32 (32-bit)
- `geometry_seed(master, index) = (master + 10007 * (index + 1)) mod 2^32`
- Python and JavaScript share known test vectors

## Statistics

| n_valid | mean | variance / stderr / CI95 |
|---------|------|---------------------------|
| 0 | null | null |
| 1 | yes | **null** (never zero uncertainty) |
| ≥2 | yes | calculated |

CI95 method: `normal_approx_1.96_stderr` (not Student-t).

## Reproducibility

- `canonical_payload()`: sorted-key JSON, non-finite → null
- `canonical_fingerprint()`: SHA-256 hex of UTF-8 payload

Cross-platform float identity is **not** claimed unless verified.

## Non-claims

No continuum limit; no independent triangulation ensemble; no dual-graph mixing.
