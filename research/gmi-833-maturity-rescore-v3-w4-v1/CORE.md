# gmi-833-maturity-rescore-v3-w4-v1 — CORE

**What this is.** A correction of a headline claim carried by two ALREADY-CLOSED rows of
issue #833. It closes no row, earns no row, and edits no frozen artifact. Read
`MATURITY_RESCORE_V3_W4.md` for the full audit, `RESCORE_V3_W4_THEOREMS_V1.md` for the named
results MRW-1..MRW-5, `FREEZE_V3_W4.md` for the pre-implementation freeze.

**The correction in one line.** `gmi-novel-intelligence-w4-v1` was scored `M4` (= frozen
held-out prediction) on support `FROZEN_HELDOUT`, whose frozen precondition is "freeze
artifact precedes outcome" — a precondition the corpus's own #976 audit CONFIRMED to be
false for that package. It earns `M2/EV2`. The revival package that re-earned
prospectiveness, `gmi-novel-intelligence-w4-prospective-v1`, was unscored; it earns
`M4/EV3`.

**Corrected headline.**

| | M0 | M1 | M2 | M3 | M4 | UNKNOWN | total |
|---|---|---|---|---|---|---|---|
| published | 48 | 30 | 89 | 6 | 23 | 1 | 197 |
| corrected | 48 | 30 | 90 | 6 | 23 | 1 | 198 |

`M4` stays at 23 and its membership swaps: `gmi-novel-intelligence-w4-v1` out,
`gmi-novel-intelligence-w4-prospective-v1` in. The count holds AND becomes true.

**Propagation sweep.** 30 adverse verdict entries checked; `UNREFLECTED 3` (2 distinct
packages), `OUT_OF_SCORED_POPULATION 18`, `REFLECTED_OR_IMMATERIAL_TO_SCORE 8`,
`NOT_ADVERSE 1`. The second flagged package, `gmi-833-g0-grammar-growth-v1`, was adjudicated
and its `M4` score is SUSTAINED — the flag is a squash-merge artifact. Nothing about that
package is altered here.

## Reproduce

Requires a full clone with tags. Stdlib only; Python 3.8+.

```sh
git clone https://github.com/SzeChunYiu/ORION-OCM.git && cd ORION-OCM
git fetch origin --tags
git fetch origin 'research/833-g0-grammar-expansion-v1:refs/remotes/origin/research/833-g0-grammar-expansion-v1'
cd research/gmi-833-maturity-rescore-v3-w4-v1

python3 -I -B  rescore_v3_w4.py        # route A  -> RESULT_V1.json        (exit 0 = all green)
python3 -I -B  oracle_v3_w4.py         # route B  -> ORACLE_RESULT_V1.json
python3 -I -O -B test_rescore_v3_w4.py # 32 tests, incl. hostiles H1-H5 and both nulls
```

`rescore_v3_w4.py` exits non-zero if any pinned blob has drifted, if custody cannot be
checked (which it reports as NOT-CHECKED, never as fine), or if any self-check fails.

## Custody of this package

The permutation null is an honest negative: the true flag count does not beat it, so the flag *count* is not offered as evidence — see `MATURITY_RESCORE_V3_W4.md` §6 and §6b for what was and was not read.

`FREEZE_V3_W4.md` was committed alone at `b5c5de53`, before any executor, oracle, test,
score record or receipt existed. `test_rescore_v3_w4.py::TestFreezeIsFirst` re-checks that
mechanically, and so does the CI workflow `.github/workflows/gmi-833-maturity-rescore-v3-w4-v1.yml`.

## Files

| file | what |
|---|---|
| `FREEZE_V3_W4.md` | pre-implementation freeze: source_main, ceiling, the two rows corrected, predictions P1-P6, hostiles, falsifiers, forbidden promotions |
| `MATURITY_RESCORE_V3_W4.md` | audit narrative, parent-ownership disclosure, results W4R-1..W4R-4 |
| `RESCORE_V3_W4_THEOREMS_V1.md` | named results MRW-1..MRW-5 with scope, assumptions, falsifiers, forbidden extrapolations |
| `rescore_v3_w4.py` | route A executor |
| `oracle_v3_w4.py` | route B, materially independent oracle |
| `test_rescore_v3_w4.py` | 32 tests: frozen rule, pins, custody, exactness, census, propagation, hostiles, null, two-route agreement, freeze-is-first |
| `RESULT_V1.json` | machine-readable receipt (route A) |
| `ORACLE_RESULT_V1.json` | machine-readable receipt (route B) |
| `SCORES_V3_DELTA.json` | the two delta score records; supersedes `THEOREM_SCORES_V2.json` by reference, never in place |
| `MANIFEST_V1.json` | parent pins (path + blob + claim ceiling), source_main, freeze_commit, forbidden promotions |
| `CORRECTION_NOTICE_V1.json` | schema `GMI_CORRECTION_NOTICE_V1` — shipped INSTEAD of a reconciliation JSON, because no row is earned |
