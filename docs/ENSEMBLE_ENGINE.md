# CDT Ensemble Engine (v0.3)

Authoritative path: **Python** (`spacetime.ensemble`).
Browser Observatory may mirror algorithms for interactive previews; do not mix sources in a single published claim.

## Geometry (v0.3 limitation)

Each geometry is the **flat** 2D CDT cylinder or torus for fixed `(N, T, periodic_time)`.
Combinatorial structure is identical across geometry indices. Independent per-geometry RNG streams control diffusion start-vertex sampling. Stochastic triangulation diversification is deferred.

## RNG

- Algorithm: Mulberry32
- `geometry_seed(master, index) = (master + 10007 * (index + 1)) mod 2^32`

## Diffusion

- Graph: undirected **primal** 1-skeleton
- $P(\sigma)$: mean return probability over starts after $\sigma$ steps
- $D_s(\sigma) = -2 \Delta\ln P / \Delta\ln \sigma$ when both $P$ positive; else undefined

## Ensemble statistics

Across geometries only: mean, variance, std, stderr, 95% CI (normal approx $1.96\times$ stderr), `n_valid`.

## Non-claims

No continuum-limit results; no dual-graph mixing; no silent success from invalid measurements.
