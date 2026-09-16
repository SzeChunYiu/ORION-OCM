# gmi-833-morphology-selection-v1

Bounded #892 / #833-J tranche for exactly two finite formal laws:

- positive-mass niche allocation preserves the union of complete local argmax
  sets, including ties, while zero-mass niches add nothing;
- nonnegative linear resource repricing changes pair order only on exact
  hyperplanes and cannot reverse quality/resource dominance.

Merged #893/#894 owns the general selection/affine-phase schema, and #895 owns
history/switching. The three empirical Section-J rows remain open.

## Reproduce

```bash
python3 -I -B research/gmi-833-morphology-selection-v1/test_selection_v1.py -v
python3 -I -O -B research/gmi-833-morphology-selection-v1/test_selection_v1.py -v
python3 -I -B research/gmi-833-morphology-selection-v1/selection_v1.py
```

Claim ceiling:
`GMI_833_FINITE_NICHE_AND_RESOURCE_REPRICING_LAWS_AT_REGISTERED_SCOPE`.
