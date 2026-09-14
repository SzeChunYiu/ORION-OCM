# Morphology Phase R/V Extension: read first

Extends the idealized morphology phase theorem (IDEALIZED_MORPHOLOGY_PHASE_THEOREM_V1) by making R (resource budget vector) and V (verifier constraint) explicit axes alongside E (ecology).

## Key result

Given (E, R, V), the morphology that minimizes total burden under PVR-3 is predicted. The 2D phase diagram (R x V at fixed E) has piecewise-linear boundaries separating neural-like, symbolic/algorithmic, and probabilistic dominance regions.

| Files | What |
|-------|------|
| [MORPHOLOGY_PHASE_RV_THEOREM_V1.md](MORPHOLOGY_PHASE_RV_THEOREM_V1.md) | Formal statement, R/V burden parameterization, 2-morphology phase condition, corner regimes |
| [phase_rv_witness.py](phase_rv_witness.py) | Exact computation on a small world: 3 archetypes, 8x8 R/V grid, held-out test |
| [test_phase_rv.py](test_phase_rv.py) | 12+ unittest controls: phase boundaries, held-out accuracy, negative twins, R/V independence |

Run tests: `python3 -I -B test_phase_rv.py -v`
