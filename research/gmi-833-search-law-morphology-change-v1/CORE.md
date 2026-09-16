# GMI #833 Search-Law Architecture Change V1

This package closes exactly one #833 Section-J row:

> Derive when a search law changes the observed candidate architecture.

## Authority

- issue: #879
- source main: `6368cda406d8e3395283049abacb36129ae94637`
- pre-implementation freeze: `619e44aca017d288435afce6e6f9765e675dde6a`
- claim ceiling: `GMI_FINITE_DETERMINISTIC_SEARCH_LAW_MORPHOLOGY_DISAGREEMENT_DERIVED_AT_REGISTERED_SCOPE`

## Residual

#877 already derives the candidate architecture selected by one registered deterministic charged search trace at a finite budget. This child compares **two** such laws on the same candidate universe and objective semantics and derives exactly when their observed architectures disagree.

The comparison distinguishes:

- `DISAGREEMENT_AVAILABILITY`: only one law has completed a candidate;
- `DISAGREEMENT_VALUE`: both have incumbents with different objective values;
- `DISAGREEMENT_EQUAL_VALUE_IDENTITY`: both have the same incumbent value but different candidate identities.

## Reproduce

```bash
PKG=$(ls -d research/gmi-833-search-law-*v1)
python -I -B $PKG/test_search_law_morphology_change_v1.py -v
python -I -O -B $PKG/test_search_law_morphology_change_v1.py -v
python -I -B $PKG/search_law_morphology_change_v1.py > /tmp/result.json
cmp /tmp/result.json $PKG/RESULT_V1.json
```

The bounded census is an implementation certificate. The analytic finite proofs are in `SEARCH_LAW_MORPHOLOGY_CHANGE_THEOREMS_V1.md`.
