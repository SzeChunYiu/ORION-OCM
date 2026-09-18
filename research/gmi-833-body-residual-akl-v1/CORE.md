# CORE — `gmi-833-body-residual-akl-v1`

**Issue #833 body, the three open non-M rows of sections A, K and L. All three
are disposed OPEN, under rules fixed before any evidence existed.** Closing a row
was possible under each rule; none of the three met its rule.

Claim ceiling `GMI_833_BODY_RESIDUAL_AKL_DISPOSITION_AT_REGISTERED_FINITE_SCOPE`.
`source_main 5e57d429`, freeze `c9dec25d` (freeze first, `git log` proves it, CI
re-derives it with a negative control).

## The three dispositions, with the number that keeps each row open

| row | result | headline |
|---|---|---|
| A — the corpus-mutating `Replace` row | `RA-1`/`RA-2`/`RA-3` | the audited term still occurs **2,710 times in 704 of 2,645** flagship files at `source_main`; a further **21 in 8** files are *required to remain* by the row's own preservation clause; **73** residual files are content-hash pinned by another package's manifest, so the repair belongs to the migration lane |
| K — test the predictor on real trained systems | `BR-1`/`BR-2`/`BR-3` | under a bridge that is **truthful by construction**, `F` emits **0 non-degenerate world-invariant points on 155,520** registered inputs across all three real populations — while the same counter returns **1,680 / 3,408 / 3,472** under the parent's registered law |
| L — evolvability on genuinely future task families | `FC-1`/`FC-2` | **0 of 6** in-session candidates pass the custody criterion `FFA-1`; the checker admits a constructed admissible candidate and rejects three clause-failing ones |

## Why K is now a proof rather than an absence

The parent tried three registration laws on 96 real torch-trained systems and all
three were falsified by their own pre-registered falsifiers (truthfulness
19/32 → 28/32 → 26/32, non-monotone). Its `FREEZE_V3_ADDENDUM` §6 pre-registered
that a fourth fitted law would be tuning to outcomes. **No fourth law is proposed
here.** Instead the bridge is attacked directly: the survivor set is
world-independent, so the admissible image is computable without enumerating a
world, and under the protocol-conservative bridge no machine in any of the three
populations has a singleton admissible value set with a positive value. Hence at
every input a non-degenerate point requires the bridge to resolve every surviving
admissible machine exactly. The resolution curve prices that requirement, and it
is **order-dependent** — 1,024 points after 3 machines ascending, 0 until 12
descending — so it is reported as a bound, not a law.

`BR-3` names the property that makes the parent's own decision correct: `KE-3`'s
*0 of 161,632* is conditioned on truthful registration, which held on **73 of 96**
systems chosen by the measured outcome. That is not a claim that `F` is defective.

## The instrument is not stuck at zero

`HB1b` runs the same counter over the parent's V4 held-out populations at full
resolution and returns **3,872** and **2,400** — exactly the non-degenerate point
counts the parent publishes for `KE-1` and `KE-2`. `NULL_UNIFORM` over **200**
randomized bridges emits up to **3,456** points; the truthful bridge emits 0. A
census of 0 is therefore a property of truthfulness, not of the counter.

## Two routes, and eight hostiles that each move their own quantity

Route B imports nothing from route A. Row A: a hand-written character scanner
with no regular expression. Row K: **black box** — concrete worlds installed on
the registration surface, the parent `F` run end to end. Row L: ISO dates through
a different git query. The routes agree on all nine scope numbers, both
preservation numbers, the census, the input total and all three positive controls.

`HA1` singular-only pattern 2,710 → 1,926 · `HA2` dropped package 2,645 → 2,112 ·
`HA4` fabricated hash pin refused 1/1 while all 73 true pins verify 0 refused ·
`HB1` fitted law > 0 · `HB2` widened bridge must not raise the census and does not ·
`HB3` counting degenerate points raises it to 4,928 · `HC1`/`HC2` rejected at the
clause each targets. Scanner nulls: a control token absent from the corpus scores
**0**, a control word that must occur scores **100,844**.

## Two robustness properties the receipts depend on

**The counted bytes are the frozen blobs.** Both routes read `source_main`
through the git object store, not the worktree, so `RA-1` is reproducible at any
HEAD. Checked by running with one in-scope file given three extra planted hits
and another deleted from the worktree: both routes still return
`2,710 / 704 / 2,645`.

**The futurity verdict does not move when main does.** `FFA-1` clause 3 excludes
any blob of this repository whatever its date — the freeze had qualified it *at
the freeze commit*, which would have let a sibling lane's later commit pass as
"exogenous" and made the verdict depend on the branch. The amended clause is
strictly stronger; disclosed as deviation `D3`.

## A false positive caught in this package's own checker

The first real run of the hash-pin index matched repo-root `README.md`,
`LICENSE` and `NOTICE` against manifest entries for *different* files of the same
basename nested inside a source packet. The rule now requires a path separator;
the three rejected claims are reported rather than dropped.

## Reproduce

```bash
python3 -I -B  research/gmi-833-body-residual-akl-v1/check_freeze_order_v1.py .
python3 -I -B  research/gmi-833-body-residual-akl-v1/body_residual_akl_v1.py --out /tmp/a.json
python3 -I -B  research/gmi-833-body-residual-akl-v1/oracle_route_b_v1.py --worlds 4 --null-seeds 8 --out /tmp/b.json
python3 -I -B  research/gmi-833-body-residual-akl-v1/check_receipt_v1.py
python3 -I -B  research/gmi-833-body-residual-akl-v1/test_body_residual_akl_v1.py -v
python3 -I -O -B research/gmi-833-body-residual-akl-v1/test_body_residual_akl_v1.py -v
```

Stdlib only, exact `Fraction`/`int` arithmetic, no floats in any claim. The
committed `ORACLE_RESULT_V1.json` is the 12-world, 200-seed run; CI replays a
4-world, 8-seed smoke and gates the stable quantities. **This package never edits
the issue body**; `ISSUE_833_RECONCILIATION_BODY_RESIDUAL_V1.json` carries an
empty `replacements` list and three `rows_deliberately_left_open` entries.
