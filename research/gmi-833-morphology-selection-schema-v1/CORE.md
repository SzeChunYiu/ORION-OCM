# gmi-833-architecture-choice-schema-v1 (internal identifier unchanged)

Finite architecture-name-free architecture-choice and affine phase-boundary theorem tranche for #893 / #833 Section J.

It keeps raw Pareto vectors primary, returns full argmin/tie sets, derives exact rational affine crossover cells, and gives typed robust-vs-ambiguous choice under interval uncertainty. It includes exhaustive small-grid and affine-cell machine checks plus hostiles against fabricated coordinatewise optima and midpoint-only uncertainty analysis.

Reproduce:

The package directory is the frozen internal identifier (it carries retired legacy terms; see `research/gmi-833-terminology-migration-v1/`); resolve it via the unique executor file name:

```bash
PKG=$(dirname $(ls research/gmi-833-*/morphology_selection_schema_v1.py))
python -I -B $PKG/test_morphology_selection_schema_v1.py -v
python -I -O -B $PKG/test_morphology_selection_schema_v1.py -v
python -I -B $PKG/morphology_selection_schema_v1.py
```

Claim ceiling: `GMI_FINITE_MORPHOLOGY_SELECTION_AND_AFFINE_PHASE_SCHEMA_AT_REGISTERED_SCOPE`.

Open successors remain history/hysteresis, switching/migration, finite-search-budget choice, niche/coexistence dynamics, held-out repricing transitions and real-system validation.
