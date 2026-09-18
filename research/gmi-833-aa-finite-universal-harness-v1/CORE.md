# CORE — `gmi-833-aa-finite-universal-harness-v1`

**Issue #833, section AA. One row: AA21 — "Search for finite-scope-to-universal
extrapolation."** Claim ceiling `REGISTERED_DETECTOR_VALIDATED_V1`.

The detector already existed and was already firing on `main`. Nobody had ever
tested it. This package tests it.

## What it establishes (exact numbers)

| result | statement | number |
|---|---|---|
| FU-1 | two independent routes agree on the registered `FIN2UNIV` population | **283 records**, **269 distinct gap ids**, **269 distinct claim ids**, **182 source files**, over **22553** objects — agreeing by **set equality**, symmetric difference **0** |
| FU-2 | integrity defect disclosed, not absorbed | 283 records collapse to **269** identities — **14 duplicates**, emitted per object *row* while the id is a function of `object_id`; 0 empty required cells; all 5 non-identifying columns constant |
| FU-3 | recall and no-alarm | **8/8** planted positives detected, **0/14** alarms on constructed clean input **and 0 alarms on 21548 real non-target objects** (331 universal-with-analytic-warrant, 21217 non-universal), with the clean case proven falsifiable |
| FU-4 | hostiles and null | **6/6** hostiles detected, each moving its own quantity; **0/200** randomized nulls reproduce the true set, max overlap **15/269** |

Route B never opens the gap graph. It recovers the firing condition *and* the
gap-id construction out of the parent census' own source text and re-derives the
population from the object corpus; if the census source stops saying what route
B parses, route B raises instead of agreeing by coincidence.

## The number that says what the detector is not

Hostile H6 replaces the declared quantifier class with a prose grep for
universal wording. On the real corpus that moves the flagged count
**283 → 351**: **68** objects read universally but are not registered
universal. That is the exact size of the gap between a metadata predicate and a
text predicate — and it is why AA16–AA20 and AA22–AA37 stay open. A flag here
is a review requirement, never a refuted claim.

## Reproduce

```sh
python3 -I -B  research/gmi-833-aa-finite-universal-harness-v1/finite_universal_harness_v1.py
python3 -I -B  research/gmi-833-aa-finite-universal-harness-v1/independent_fin2univ_oracle_v1.py
python3 -I -B  research/gmi-833-aa-finite-universal-harness-v1/test_finite_universal_harness_v1.py
python3 -I -O -B research/gmi-833-aa-finite-universal-harness-v1/test_finite_universal_harness_v1.py
python3 -I -B  research/gmi-833-aa-finite-universal-harness-v1/check_receipt_v1.py
```

Stdlib only. Exact arithmetic (`int` / `fractions.Fraction`); the test walks the
whole receipt and fails on any float. 73 checks, both modes.
