# CORE — GMI #833 Section I: update-law regimes for seven external signatures

Read order: `FREEZE_V1.md` (pre-implementation custody, commit `6e42ccd2`) ->
`PARENT_OWNERSHIP_V1.md` (what is NOT claimed) ->
`UPDATE_LAW_REGIMES_THEOREMS_V1.md` (the named results) ->
`SUPPLEMENT_1_POST_FREEZE_DEVIATIONS.md` -> `RESULT_V1.json`.

**Claim ceiling:**
`GMI_833_SECTION_I_UPDATE_LAW_REGIME_CONDITIONS_AND_PROSPECTIVE_SELECTOR_AT_REGISTERED_FINITE_SCOPE`
Evidence EV1 + EV2, maturity M1-M2. Finite registered scope only.

## What this answers

#870 proved a useful preference between update laws needs stated assumptions.
#1014 built the law space and answered two of the preferences. This tranche
answers seven more, plus the selector, the blind recovery and the held-out test —
by deriving each signature from structure and locating where the preference
flips. The seven mechanism names appear in exactly one file,
`PARENT_OWNERSHIP_V1.md`.

## The results in one line each

- **UL-1** — `A_k` is closed under arbitrary pointwise selection, because the
  parent's admissibility is a pointwise conjunction. Strengthens IL-1.2 and
  absorbs history-dependent switching, which composition does not.
- **UL-2** — exact conditional weighting beats its point-summary comparator
  exactly below `beta* = alpha_gain/((M-1)T)`; unconditionally never when
  `alpha_gain <= 0`.
- **UL-3** — never-retrieved instances are strictly wasteful, so the minimal
  retrieval law stores exactly the retrieved set; the crossover against
  compression is `chi*`, exact.
- **UL-4** — production compression pays exactly below `disc*`, a bound on the
  size of the space the productions are searched in: 10 and 20 on two
  environments (at most 5/2 and 10/3 productions) and **0** on the other three.
  At the registered 72-production space the condition is satisfiable nowhere,
  three environments carry a coordinatewise `DOMINATED_EVERYWHERE` certificate,
  and the regime is witnessed on none. The row closes on the mapped boundary and
  the exhibited bound, not on a positive regime.
- **UL-5** — reuse-indexed construction, closed BY RECONCILIATION TO #897, whose
  lifecycle threshold `Hocc*Delta > Kdef` is restated in these coordinates.
- **UL-6** — breadth beats the single incumbent exactly below
  `pistar* = (Vglob-Vloc)/((Bmin-1)Tsteps)`; unconditionally never when the
  landscape is unimodal.
- **UL-7** — cross-episode indexing pays exactly below
  `tau* = rT(K-k0)/(M'K)`; at zero relatedness it is behaviourally identical to
  the base rule, verified pointwise, and strictly dearer.
- **UL-8** — **the conditions favouring successor-set change are EMPTY** inside
  any pointwise-selection-closed class, deductively, with the matched positive
  earned from the parent's own `A_1` non-closure counterexample.
- **UL-9** — the non-redundancy lemma: a wasted structural coordinate is
  strictly dominated at every positive price. This is the single shape of every
  converse above.
- **UL-10a** — the seven predicates do NOT separate law space: 16 of 21 pairs are
  COMPATIBLE, with `SIG-L` nested in `SIG-R`. Reported as a matrix; the word
  partition is not applied to it.
- **UL-10b** — the argmin cells DO partition the positive price cone,
  unconditionally, with 21 exact crossover hyperplanes.
- **UL-11 / UL-12 / UL-13** — the frozen selector, the blind search, the held-out
  test.

## Headline numbers (all reproducible from `RESULT_V1.json`)

| quantity | value |
|---|---|
| registered environments (derivation / held-out) | 6 / 6 |
| `beta*` on `D1..D6` | 1/16, 0, -1/32, 1/48, 3/16, 3/16 |
| `chi*` on the five usable environments | 147/8, 109/6, 221/3, 163/4, 163/4 |
| `pistar*` multimodal / unimodal | 1 / **0** |
| `tau*` at `r=4` / at `r=0` | 12/5, 18/5, 18/5, 6/5, 6/5 / **0** |
| `s*` on every environment | **0** |
| UL-2 converse violations (`D2`, `D3`) | 0 of 2187 prices each |
| UL-7 pointwise reduction at `r=0` | 32 inputs checked, **0 mismatches** |
| UL-8 prices where the change is not strictly dearer | **0 of 2187**, every environment |
| UL-6 held-out unimodal breadth comparisons | **157,464**, 0 violations |
| compatibility matrix | 16 COMPATIBLE / 5 EXCLUSIVE of 21 |
| argmin partition failures, frozen grid and anchored | **0** everywhere |
| selector soundness / mixture-hull violations | **0 / 0** everywhere |
| blind-search regime disagreements | **0** everywhere, both grids, both routes |
| nulls | true 131/131 hits, best null 33, **0/200** reach it; **0/200** foreign thresholds locate the target crossover |
| `disc*` on `D1`, `D2` / on `D4`, `D5`, `D6` | 10, 20 (at most 5/2 and 10/3 productions) / **0** |
| `SIG-R` / `SIG-L` witnessed anywhere | **never**, on either grid |
| held-out predictions | HO-P1 HIT 10/10, HO-P3 HIT, HO-P4 HIT, **HO-P2 MISS** (260 mismatches, 260/260 attributed, 0 unattributed) |
| `select_v2` revival on held-out | 794 agreements, **0 disagreements** |
| name-freedom screen | CLEAN_AT_REGISTERED_AUDIT_SCOPE, 36,129 tokens, 47 denylist entries, 0 unmatched, 0 stale |
| check suite | **329 checks, 329 green** |
| hostiles detected | **14 / 14** |
| two-route agreement | scope fingerprint, every invariant, every coefficient vector, every threshold, every cell count |

## Reproduce exactly

Standard library only, exact rational arithmetic, Python 3.8 compatible.
Run off the Mac per the environment rule; the receipts below were produced on
laptop-billy with `python3` 3.8.10.

```
cd research/gmi-833-update-law-regimes-v1
python3 -I -B  oracle_update_law_regimes_v1.py   # route B, writes ORACLE_RESULT_V1.json
python3 -I -B  update_law_regimes_v1.py          # route A, writes RESULT_V1.json
python3 -I -B  test_update_law_regimes_v1.py     # prints ALL GREEN
python3 -I -B  measure_d1_sensitivity_v1.py      # writes D1_SENSITIVITY_V1.json

python3 -I -O -B oracle_update_law_regimes_v1.py
python3 -I -O -B update_law_regimes_v1.py
python3 -I -O -B test_update_law_regimes_v1.py
```

Both receipts are byte-identical under `-B` and `-O -B`. No claim is gated by a
bare `assert`, which `-O` would erase. CI:
`.github/workflows/gmi-833-update-law-regimes-v1.yml`, which also checks that
the freeze commit is a strict ancestor of the first implementation commit.

## What this does NOT close

- **`Test on realistic learning systems` is LEFT OPEN.** The freeze
  pre-committed that it closes only on real trained systems with sha256-bound
  real data sources and predictions frozen before outcomes, following #903, and
  that synthetic data may not close it. Real systems were not reached in this
  round, so the row stays open. `REAL_SYSTEM_VALIDATION` is a forbidden
  promotion.
- The held-out prediction `HO-P2` **MISSED as stated**. Every mismatch is
  attributed to one stage — the frozen selector ranks canonical representatives,
  and a canonical representative can itself be redundant, so the blind search
  over non-redundant laws can never return it. The revival, `select_v2`, is
  delivered and disclosed as a post-freeze repair; the frozen selector's own
  numbers are reported unchanged beside it.
- Nothing here is validated at real scale, replicated, or held out beyond the six
  registered held-out environments. The binding forbidden promotions are in
  `MANIFEST_V1.json`.
