# gmi-833-architecture-choice-v1 (internal identifier unchanged)

Bounded #892 / #833-J tranche for exactly two finite formal laws:

- positive-mass niche allocation preserves the union of complete local argmax
  sets, including ties, while zero-mass niches add nothing;
- nonnegative linear resource repricing changes pair order only on exact
  hyperplanes and cannot reverse quality/resource dominance.

Merged #893/#894 owns the general architecture-choice/affine-phase schema, and #895 owns
history/switching. The three empirical Section-J rows remain open.

## Reproduce

The package directory is the frozen internal identifier (it carries retired legacy terms; see `research/gmi-833-terminology-migration-v1/`); resolve it via the unique executor file name:

```bash
PKG=$(dirname $(ls research/gmi-833-*/selection_v1.py))
python3 -I -B $PKG/test_selection_v1.py -v
python3 -I -O -B $PKG/test_selection_v1.py -v
python3 -I -B $PKG/selection_v1.py
```

Claim ceiling:
`GMI_833_FINITE_NICHE_AND_RESOURCE_REPRICING_LAWS_AT_REGISTERED_SCOPE`.
