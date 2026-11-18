# Experiment: 2D Causal Dynamical Triangulations

**Status:** Planned (first concrete research target)

## Intent

A small, falsifiable numerical laboratory for studying whether continuum-like geometry can emerge from discrete, causally constrained triangulations in two dimensions.

This is deliberately a toy model. It is not a claim about four-dimensional quantum gravity.

## Planned pipeline

1. **Generate** discrete spacetime configurations (triangulations) obeying causal and geometric constraints.
2. **Sample** an ensemble (Metropolis or related).
3. **Measure** geometric observables, with priority on **spectral dimension**.
4. **Probe** continuum-limit behaviour under controlled scaling.
5. **Validate** key numerical results independently via Spectral Bridge.

## Success / failure criteria (to be refined)

- Reproducible measurement of spectral dimension as a function of scale.
- Clear documentation of parameters, seeds, and raw data.
- Independent cross-check of at least one core observable.
- Explicit statement of what would constitute evidence for (or against) continuum-like behaviour in this model.

## Notes

Implementation will live primarily under `representations/`, `samplers/`, and `observables/`, with run records and configurations kept here.
