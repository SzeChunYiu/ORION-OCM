# gmi-833-morphology-selection-schema-v1

Finite architecture-name-free morphology-selection and affine phase-boundary theorem tranche for #893 / #833 Section J.

It keeps raw Pareto vectors primary, returns full argmin/tie sets, derives exact rational affine crossover cells, and gives typed robust-vs-ambiguous selection under interval uncertainty. It includes exhaustive small-grid and affine-cell machine checks plus hostiles against fabricated coordinatewise optima and midpoint-only uncertainty analysis.

Reproduce:

```bash
python -I -B research/gmi-833-morphology-selection-schema-v1/test_morphology_selection_schema_v1.py -v
python -I -O -B research/gmi-833-morphology-selection-schema-v1/test_morphology_selection_schema_v1.py -v
python -I -B research/gmi-833-morphology-selection-schema-v1/morphology_selection_schema_v1.py
```

Claim ceiling: `GMI_FINITE_MORPHOLOGY_SELECTION_AND_AFFINE_PHASE_SCHEMA_AT_REGISTERED_SCOPE`.

Open successors remain history/hysteresis, switching/migration, finite-search-budget selection, niche/coexistence dynamics, held-out repricing transitions and real-system validation.
