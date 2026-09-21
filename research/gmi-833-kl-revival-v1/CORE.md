# CORE — read me first

`gmi-833-kl-revival-v1` closes issue #833 rows **K** (already closed by #1106,
recorded here, not re-replaced) and **L** (this package) under rules frozen
before any implementation (`FREEZE_V1.md`, `FREEZE_V1_AMENDMENT_1.md`).

## Row L in one paragraph

`EP-1` — `Ev_Q(U)` under the POS history exceeds `Ev_Q(U)` under the NEG
history (`pH(POS) > pH(NEG)`, tie = MISS) — was frozen with a committed
timestamp and scored on genuinely future task families: English Wikipedia
page-creation revisions mechanically admitted by `PS-1` after the freeze +
60 s, each bound to Wikimedia's own revision sha1 (`FFA-1P`). Window 1:
**EP-1 5/6** (the miss is `P05`, a tie at 0/24 whose graded potential still
orders POS above NEG, `C_pot` 103 vs 78) — the row stayed OPEN. Window 2
(amendment 1): six scored sources (P06 was `AT_FLOOR_OR_CEILING` under `PR-1`,
excluded by name and replaced by the next admitted candidate P07 per
`FREEZE_V1.md` 4.6 clause 2), **EP-1 6/6**. Combined record 11/12 with exact
label-permutation null `13/4096` (two-window procedure null `70/4096`);
`EP-4` developmental-potential ordering 6/6 prospective on window 2, 6/6 post
hoc on window 1, 7/7 post hoc on the parent's sources. Two independent routes
agree on every `p0`, `pH`, `C_pot`, verdict and custody clause.

## How to verify (fresh)

```
python3 -I -B research/gmi-833-kl-revival-v1/check_freeze_order_v1.py .          # commit order + frozen bytes
python3 -I -B research/gmi-833-kl-revival-v1/kl_revival_v1.py                     # route A (full null, 200 seeds)
python3 -I -B research/gmi-833-kl-revival-v1/oracle_route_b_v1.py --random-worlds 8 \
    --route-a /tmp/routeA.json --out /tmp/routeB.json                            # route B, compares
python3 -I -B research/gmi-833-kl-revival-v1/check_receipt_v1.py --route-a /tmp/routeA.json \
    --route-b /tmp/routeB.json                                                   # committed == live
python3 -I -B research/gmi-833-kl-revival-v1/test_kl_revival_v1.py -v            # re-derives everything
```

Off-repository source bytes live only on laptop billy (`~/ocm-scratch/revive-kl/`),
as the parent did; the committed record carries ids, timestamps, Wikimedia's
sha1, this lane's sha256, lengths and 80-byte prefixes. Heavy training runs
(laptop billy) are the only torch steps; the scorer, oracle, tests and gates are
stdlib-only and re-run in CI.

## Files

- Freeze + amendment: `FREEZE_V1.md`, `FREEZE_V1_AMENDMENT_1.md`, `FREEZE_ROWS_V1.json`.
- Sources (windows 1 + 2): `POSTERIOR_SOURCES_V1.json`, `POSTERIOR_SOURCES_V2.json`,
  `POSTERIOR_SOURCES_V2_EXTENDED.json` (P06 replaced by P07, `replacement` metadata).
- Receipts: `REAL_RUNS_L4/` (window 1), `REAL_RUNS_L5/` (window 2, incl. P07).
- Row K material: `FROZEN_PREDICTIONS_REAL4_V1.json`, `REAL_RUNS_V4/REAL_MEASURED_V4.json`.
- Score layer: `kl_revival_v1.py` (route A), `oracle_route_b_v1.py` (route B),
  `test_kl_revival_v1.py`, `check_receipt_v1.py`, `check_freeze_order_v1.py`.
- Results: `RESULT_V1.json`, `ORACLE_RESULT_V1.json`, `MANIFEST_V1.json`,
  `ISSUE_833_RECONCILIATION_KL_REVIVAL_V1.json`.
- Detail: `KL_REVIVAL_THEOREMS_V1.md` (named results FP-1..FP-4, SB-1..SB-3),
  `PARENT_OWNERSHIP_V1.md` (assimilation-first), `L4_DIAGNOSIS_V1.json` (window-1 miss).
