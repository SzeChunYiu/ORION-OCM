# CORE — `gmi-833-aa-gap-object-v1`

**Issue #833, section AA. Rows: AA01, AA07, AA09, AA39.**
Claim ceiling `FINITE_EXACT_GOVERNANCE_INSTRUMENT_V1` — exact finite checks over
one named universe, never an analytic proof.

## What it establishes (exact numbers)

| result | statement | number |
|---|---|---|
| AAG-1 | nine AA01 names bound injectively; every frozen gap realizes them | 1140/1140 conforming, 0 missing, 0 empty, 1094 distinct `claim_id` |
| AAG-2 | the incumbent grading columns carry zero information | exact Gini impurity **0/1** for `severity`, `materiality`, `status`, `owner_role`, `parent_result`, `descendants` (6 columns, 1 distinct value each) |
| AAG-3 | declared monotone materiality threshold, non-degenerate on the real universe | 0 violations / 768 comparisons over 256 domain points; applied → **847 MATERIAL + 293 CRITICAL** |
| AAG-4 | four closure grades form a total chain; bare `closed` is detectable | 0 violations / 32 evidence points; **1490 bare-`closed` sites in 178 packages** over 2577 markdown files; recall 3/3, no-alarm 0/4 |
| AAG-5 | repair-successor interrogation is automatic and total | 1140/1140 `REPAIR_DELTA` records emitted; emitter refuses empty id / empty repair / non-declared grade |

Two routes agree on every number. Eight hostiles, each asserted to have moved
its own quantity. Null: **0/200** randomized records conform while the true
result passes.

The AAG-1..AAG-5 numbers are over a **pinned blob** and are checked by equality
in CI. The bare-`closed` scan is a **repo-wide measurement over a corpus other
lanes are actively extending**, so CI asserts it non-vacuously (> 1000 hits,
> 100 packages, files scanned > packages with hits) and prints the live number
rather than demanding equality: AAG-4 claims that the detector works and the
backlog is large, not that the backlog is exactly 1490.

The workflow's freeze-order step reads `git log --reverse` over the package
path and requires the first commit to contain only `FREEZE_V1.md`. It therefore
assumes **merge-commit** history; a squash merge collapses freeze and
implementation into one commit and the check would fail permanently on `main`.
This repository's #833 history is merge commits.

## Explicitly not earned

**AA38** — `descendants` is non-empty in **0 of 1140** records; the incumbent
graph is a flat list. AA40 depends on it. Both stay open.

## Reproduce

```sh
python3 -I -B  research/gmi-833-aa-gap-object-v1/gap_object_v1.py --scan
python3 -I -B  research/gmi-833-aa-gap-object-v1/independent_oracle_v1.py
python3 -I -B  research/gmi-833-aa-gap-object-v1/test_gap_object_v1.py
python3 -I -O -B research/gmi-833-aa-gap-object-v1/test_gap_object_v1.py
```

Stdlib only. Exact arithmetic (`int` / `fractions.Fraction`); no float appears
in any reported quantity.
