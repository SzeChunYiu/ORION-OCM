# CORE — `gmi-833-ac-lanes-harness-v1`

**Issue #833, section AC. Four rows closed: AC01, AC03, AC04, AC06. AC07
measured and left open.** Claim ceiling
`REGISTERED_LITERATURE_STRUCTURE_VERIFIED_V1`.

## What it establishes (exact numbers)

| result | statement | number |
|---|---|---|
| ACL-1 | lane coverage against **AC01's own eleven-item list**, injective both ways | **11/11** bound one-to-one, **0** unbound, **0** lanes serving two items, **74** entries, min **6** per lane |
| ACL-2 | every `EXACT` row adopts a canonical term | **27/27** (adopt-rule **25**, canonical token overlap **19**); **21** rows outside the antecedent counted, not judged; **0** violations |
| ACL-3 | cross-field synonyms with one primary term | **40** antecedent rows — **38** resolved by the frozen crosswalk, **2** (`niche`, `parent subtraction`) supplied here; **0** unresolved |
| ACL-4 | an earliest-or-strongest parent record per idea | **48/48** — **40** in the parent artifact, **8** supplied here; split **15 VERIFIED / 29 CITE-TF / 4 UNMARKED**, and all 8 supplied are **CITE-TF** |
| ACL-5 | AC07 is not earned, with the reason measured | **2 of 6** kinds have a discriminator among registered fields; **4** have none |

Two independent routes agree on every quantity and on every row-id **set**;
route B re-reads the AC row strings out of `FREEZE_V1.md` rather than sharing a
constant with route A, and uses no regular expression anywhere. **6/6** hostiles
detected, each moving its own quantity. Null: **0/200** random lane
permutations bind all eleven (max **4**, exact mean **199/200**). 78 checks,
both modes.

## The AC05 firewall

The parent lanes file and crosswalk self-flag most references `CITE-TF`. Nothing
in this package verifies a citation, every result carries the verification split
as a disclosed field, and the eight parent records supplied here are all marked
`CITE-TF`. **AC05 stays open.** Closing it off this table would be closing it by
narrowing its meaning.

## A false-positive class caught before it shipped

A first draft tested AC04 with a list of instruction verbs and reported **9**
violations; **7** were wrong, because the list lacked `prefer`, `adopt` and
`map`. Widening a vocabulary until violations vanish is outcome tuning. The
shipped test is structural — the parent document's own convention puts the
selection rule in a parenthetical — and reports **2**. AC03 has the mirror
story: a single-witness test flagged 12 rows, most of them morphological
variants (`bisimulation` vs `bisimilarity`); the shipped two-witness test
reports **0**.

## Reproduce

```sh
python3 -I -B  research/gmi-833-ac-lanes-harness-v1/ac_lanes_harness_v1.py
python3 -I -B  research/gmi-833-ac-lanes-harness-v1/independent_ac_oracle_v1.py
python3 -I -B  research/gmi-833-ac-lanes-harness-v1/test_ac_lanes_harness_v1.py
python3 -I -O -B research/gmi-833-ac-lanes-harness-v1/test_ac_lanes_harness_v1.py
python3 -I -B  research/gmi-833-ac-lanes-harness-v1/check_receipt_v1.py
```

Stdlib only; every reported quantity is an `int` or an exact `Fraction`.
