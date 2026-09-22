# gmi-833-h-real-scale-decision-trees-v1 — CORE

**What this is.** A continuation of the Section-H real-scale line of issue
#833 for the named-family row `Decision trees/rule systems.`

It imports **no gate certificate from any parent**. All eleven Section-H
coordinates R01–R11 are earned at this package's own scope — `SIGMA_H08R` — on
a sha256-bound external real source (`/usr/share/dict/american-english`,
104,334 tokens, digest `9e66281f7e51`), with exact integer decision counts and
two materially independent routes. `CROSS_SCOPE_GATE_COMPOSITION` is in
`forbidden_promotions` and a test asserts that no gate certificate carries a
scope other than its own.

## The headline

| row | scope | outcome |
|---|---|---|
| `Decision trees/rule systems.` | `SIGMA_H08R` | **closed**, 11 of 11 |

The family-blind winner rule over the registered readout language `R` (frozen
pre-outcome in `FREEZE_V1_SLICE_ADDENDUM.md`) recovers the family's own
mechanism — the **threshold conjunction**: a query is predicted positive iff
it is short **and** present in the stored rule table (`LEN<=9&CNT>=1`, a
decision rule over stored context). On 97,018 held-out real descriptors it
makes **1,391 decision errors** against the fit-majority rule's **20,446**
(prototype agreement 95,627 / 97,018). Both registered nulls fire: the
label-shuffle null gives 33,079 errors, the membership-shuffle design null
9,358 (> 3× the arm). The store ladder is monotone to 1,391; the
scan-vs-vocabulary-index crossover is `m* = 110,799`. The matched
**source-order presentation control fires**: under the un-permuted
presentation the family readout degenerates to 75,318 errors and the winning
readout (`LEN<=9`, 12,319) fails the registered F1 margin, so the registered
presentation lever is load-bearing.

## The registered design, in one paragraph

The ecology `F08` is the stored-context rule table over the descriptor closure
of the sha-bound source: every prefix of length ≥ 2 of every token, 776,142
descriptors in total, with the stored context of a query `q` being its
membership count among the stored descriptors and its trie fan-out. The
protected interface is the decision `y(q) = 1 iff len(q) <= 9 AND
source-count(q) >= 2` — the short shared descriptor, a threshold conjunction
over the source. The registered presentation is the parent's target-
independent Knuth multiplicative hash `key(i) = (i * 2654435761) mod 2**32`,
then the arithmetic 7:1 slice (`n_fit` 679,124 / `n_held` 97,018, clear of the
R11 bar), with a `rank_fit`/`rank_score` split of the fit for the ranking
stage. The readout language `R` (60 arms: `C0`, `C1`, `LEN<=6..12`,
`CNT>=1..3`, `ASSOC>=1..3`, `LEN<=L&CNT>=j`, `LEN<=L&ASSOC>=j`, `PREF_VOTE`,
`EXT_VOTE`, `MEM_FALLBACK`) was closed before any outcome; the winner rule
(fewest exact decision errors, ties by charged cost then name) chose
`LEN<=9&CNT>=1` at the rank stage (11,947 errors vs the majority's 42,936),
and the symmetric half-split regeneration (R09, applied from the start)
recovers the same class on both halves (`LEN<=9&ASSOC>=1`). Every claimed
quantity is an exact integer decision count, committed in `REAL_RUNS/` and
re-derived by route B.

## Reproduce

Stdlib only, no network, no real source needed: the real run's receipts are
committed and every claimed quantity replays exactly from them.

```
cd research/gmi-833-h-real-scale-decision-trees-v1
python3 -I -B  independent_oracle_dt_v1.py            # route B, writes ORACLE_RESULT_V1.json
python3 -I -B  real_scale_decision_trees_v1.py        # route A, writes RESULT_V1.json
python3 -I -O -B test_real_scale_decision_trees_v1.py -v
```

To re-run the real-scale extraction from the bound source (host of record
billy-old only, CPython 3.14.4, ~4 minutes):

```
python3 -B run_real_scale_decision_trees_v1.py
```

## Files

| file | what it is |
|---|---|
| `FREEZE_V1.md` + two addenda | the custody chain: scope, ecology, frozen predictions/falsifiers/claim ceiling; the exact slice form and readout language `R`; the symmetric half-split R09, the null constructions and the presentation control |
| `MANIFEST_V1.json` | the package manifest with source binding, scope and parent pins |
| `grammar_dt_v1.py` | the readout grammar `G_DT`: the closed language `R`, the post-hoc classifier, the presentation key, the digest |
| `run_real_scale_decision_trees_v1.py` | the real-scale run driver; the only file that reads the real source |
| `real_scale_decision_trees_v1.py` | route A: exact replay, the eleven-coordinate ledger, the hostiles, `RESULT_V1.json` |
| `independent_oracle_dt_v1.py` | route B: source-separated, imports none of the above |
| `test_real_scale_decision_trees_v1.py` | custody, scope, slice, readout, control and reconciliation tests |
| `REAL_SCALE_DECISION_TREES_THEOREMS_V1.md` | the named results, each with its four ledgers |
| `PARENT_LEDGER.md` | the assimilation ledger: what is taken from which parent and what is not |
