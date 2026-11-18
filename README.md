# Spacetime

**Quantum Geometry & Gravity Research Engine**

Part of the [Babel Dragon](https://github.com/TheBabelDragon) ecosystem.

Spacetime investigates how spacetime could emerge from quantum degrees of freedom.  
It is a research domain, not a feature of MetaField and not a quantum circuit simulator.

---

## Position in the Ecosystem

```
BABEL DRAGON ECOSYSTEM
│
├── Shared discovery, execution, provenance and validation infrastructure
│
├── Quantum Gravity Research          ← Spacetime (this repository)
│   ├── Quantum spacetime models
│   ├── Discrete and emergent geometry
│   ├── Background-independent formulations
│   ├── Quantum field theory on curved spacetime
│   └── Black-hole information and holography
│
├── MetaField
│   └── Fields, geometry, dynamics, lattice representations and physical models
│
├── TensorGate
│   └── Numerical engines, tensor operations, simulation and optimization
│
├── Spectral Bridge
│   └── Independent mathematical validation and numerical claims
│
├── Quantum Simulator                 (future)
│   └── Circuit simulation, quantum algorithms and hardware abstractions
│
└── REA
    └── Research and reverse-engineering assistance
```

**Key principle:** Spacetime owns the physics and the research questions.  
MetaField, TensorGate and Spectral Bridge provide the computational and validation substrate.  
Multiple competing quantum-gravity models should be able to use the same infrastructure.

---

## What Spacetime Owns

| Area | Responsibility |
|------|----------------|
| Theory / model definitions | Formal statements of candidate quantum-spacetime models |
| Discrete spacetime representations | Causal sets, triangulations, spin networks, tensor networks, etc. |
| Quantum geometry experiments | Numerical probes of geometric observables |
| Gravitational observables | Spectral dimension, volume scaling, curvature measures, causal structure |
| Model comparisons | Side-by-side evaluation under shared protocols |
| Reproducible experiment records | Provenance, seeds, parameters, raw and derived data |
| Falsifiable numerical predictions | Clear criteria for accepting or rejecting continuum-limit claims |

---

## Research Directions

1. **Causal Dynamical Triangulations (CDT)**  
   Build spacetime from discrete geometric building blocks and study whether continuum-like geometry emerges.

2. **Loop Quantum Gravity**  
   Spin networks, quantized geometric observables, spin foams and discrete evolution.

3. **Emergent Spacetime / Holography**  
   Relationships between quantum entanglement, tensor networks and geometric structure.

4. **Quantum Fields in Curved Spacetime**  
   Quantum field dynamics on gravitational backgrounds.

---

## First Experiment: 2D Causal Dynamical Triangulations

A deliberately small, falsifiable toy model.

### Goals
- Generate discrete spacetime configurations under causal and geometric constraints.
- Implement an ensemble sampler.
- Measure geometric observables, especially **spectral dimension**.
- Investigate continuum-limit behaviour.
- Cross-check numerical results independently through Spectral Bridge.

This is **not** a claim to have solved four-dimensional quantum gravity.  
It is a controlled numerical laboratory for testing the emergence of continuum geometry from discrete building blocks.

### Implementation sketch
```
theory/          # formal model definitions and constraints
representations/ # discrete geometry data structures
samplers/        # ensemble generation (Metropolis, etc.)
observables/     # spectral dimension, volume, curvature proxies
experiments/     # reproducible run configurations + records
validation/      # interfaces to Spectral Bridge / independent checks
```

---

## Architectural Pipeline (target)

```
THEORY
  Propose a quantum spacetime model
      ↓
REPRESENTATION
  Construct its mathematical geometry
      ↓
SIMULATION
  MetaField + TensorGate + (optional) quantum backends
      ↓
VALIDATION
  Spectral Bridge + independent references
      ↓
DISCOVERY
  Record results, compare models, reject unsupported claims
```

---

## Design Constraints

- Spacetime is a **first-class research project**, not a MetaField feature.
- It must not depend on quantum hardware to make progress.
- TensorGate is the numerical engine; Spacetime defines *what* is being computed.
- All claims must be accompanied by reproducible numerical evidence and independent validation paths.
- Competing models are welcome and encouraged under the same experimental protocols.

---

## Live Observatory (GitHub Pages)

The browser-based Spacetime Observatory is published at:

**https://thebabeldragon.github.io/Spacetime/**

- Deployment target: GitHub Pages
- Published source: `site/`
- Workflow: `.github/workflows/pages.yml`
- Production branch: `main`
- Pull requests: build and validation only
- Deployment: automatic after qualifying pushes to `main`
- Manual deployment: GitHub Actions `workflow_dispatch`

### Configuration

Repository Settings → Pages → Build and deployment:

**Source: GitHub Actions**

A successful PR validation does **not** publish the site.
Production deployment occurs after merging into `main` and
successfully completing the Pages deployment job.

## Status

**v0.1 — Discrete geometry core + Observatory shell**

- Repository created and positioned in the Babel Dragon ecosystem.
- Dimension-independent simplicial geometry core and 2D CDT model implemented.
- Browser Observatory (`site/`) published via GitHub Pages after merge to `main`.
- Next milestone: ensemble-based spectral dimension with reproducible experiment records (v0.2 research engine).

---

## License

MIT (to be confirmed with the rest of the ecosystem).
