# gmi-833-h-real-scale-model-free-rl-v1 — CORE

**What this is.** A continuation of the Section-H real-scale line of issue
#833 for the named-family row `Model-free RL-like learning.`

It imports **no gate certificate from any parent**. All eleven Section-H
coordinates R01–R11 are earned at this package's own scope — `SIGMA_HMLR` — on
a sha256-bound external real source (`/usr/share/dict/american-english`,
104,334 tokens, digest `9e66281f7e51`), with exact integer decision counts and
two materially independent routes. `CROSS_SCOPE_GATE_COMPOSITION` is in
`forbidden_promotions` and a test asserts that no gate certificate carries a
scope other than its own.

## The headline

| row | scope | outcome |
|---|---|---|
| `Model-free RL-like learning.` | `SIGMA_HMLR` | **closed**, 11 of 11 |

The family-blind winner rule over the registered readout language `R` (frozen
pre-outcome in `FREEZE_V1_SLICE_ADDENDUM.md`) recovers the family's own
mechanism — the **accumulated-outcome-feedback readout**: a query is predicted
positive iff the accumulated experienced-outcome mass at its state reaches half
that state's experience count (`VOTE>=5/10`, the class
`REWARD_PROPENSITY_ACCUMULATION`). On 83,983 held-out real experiences it makes
**931 decision errors against the fallback rule's 27,222** (prototype agreement
83,052 / 83,983). Both registered nulls fire: the label-shuffle null gives
36,939 errors, the feedback-shuffle design null 27,222 (> 3× the arm, and in
fact exactly the fallback rule's count). The **matched negative control fires**:
under a marginal-matched, cell-blind received outcome no arm of `R` clears the
registered margin and every raw sibling arm is bit-identical. The store ladder
is monotone to 931; the scan-vs-vocabulary-index crossover is `m* = 79,644`.
The matched **source-order presentation control fires**: under the un-permuted
presentation the family readout carries 23,237 errors and fails the registered
`F1` margin, so the registered presentation lever is load-bearing.

## The registered design, in one paragraph

The ecology `F_ML` is the **experience table** over the descriptor closure of
the sha-bound source: for every token `w` and every split `2 <= k <= len(w)-1`,
one experience (context `q = w[:k]`, received outcome `rho(w[k]) = 1 iff
w[k] in {a,e,i,o,u}`), 671,860 experiences in total. The state of an experience
is `sigma(q) = (q[:1], q[-1:])`; the protected decision is the boolean threshold
`2 * P_full(sigma(q)) >= N_full(sigma(q))` on the accumulated outcome feedback
over the whole table. The registered presentation is the parent's
target-independent Knuth multiplicative hash `key(i) = (i * 2654435761) mod
2**32`, then the arithmetic 7:1 slice (`n_fit` 587,877 / `n_held` 83,983, clear
of the R11 bar), with a `rank_fit`/`rank_score` split of the fit for the ranking
stage. The readout language `R` (70 arms: `C0`, `C1`, `LEN<=6..12`,
`CNT>=1..3`, `ASSOC>=1..3`, the two conjunction families, `PREF_VOTE`,
`EXT_VOTE`, `MEM_FALLBACK`, `RECENCY_LAST`, `VOTE>=j/10`) was closed before any
outcome; the winner rule (fewest exact decision errors, ties by charged cost
then arm name) chose `VOTE>=5/10` at the rank stage (1,303 errors vs the
fallback rule's 56,687), and the symmetric half-split regeneration (R09,
registered from the start) recovers the same class on both halves. Every
claimed quantity is an exact integer decision count, committed in `REAL_RUNS/`
and re-derived by route B.

## Reproduce

Stdlib only, no network, no real source needed: the real run's receipts are
committed and every claimed quantity replays exactly from them.

```
cd research/gmi-833-h-real-scale-model-free-rl-v1
python3 -I -B  independent_oracle_ml_v1.py            # route B, writes ORACLE_RESULT_V1.json
python3 -I -B  real_scale_model_free_rl_v1.py         # route A, writes RESULT_V1.json
python3 -I -O -B test_real_scale_model_free_rl_v1.py -v
```

To re-run the real-scale extraction from the bound source (host of record
billy-old only, CPython 3.14.4, ~6 minutes):

```
python3 -B run_real_scale_model_free_rl_v1.py
```

## Files

| file | what it is |
|---|---|
| `FREEZE_V1.md` + two addenda | the custody chain: scope, ecology, frozen predictions/falsifiers/claim ceiling; the exact slice form, the readout language `R` and the charged-cost model; the symmetric half-split R09, the null constructions, the matched negative control and the admission of `RECENCY_LAST` |
| `MANIFEST_V1.json` | the package manifest with source binding, scope and parent pins |
| `grammar_ml_v1.py` | the readout grammar `G_ML`: the closed language `R`, the post-hoc classifier, the presentation key, the digest |
| `run_real_scale_model_free_rl_v1.py` | the real-scale run driver; the only file that reads the real source |
| `real_scale_model_free_rl_v1.py` | route A: exact replay, the eleven-coordinate ledger, the hostiles, `RESULT_V1.json` |
| `independent_oracle_ml_v1.py` | route B: source-separated, imports none of the above |
| `test_real_scale_model_free_rl_v1.py` | custody, scope, slice, readout, control and reconciliation tests |
| `REAL_SCALE_MODEL_FREE_RL_THEOREMS_V1.md` | the named results, each with its four ledgers |
| `PARENT_LEDGER.md` | the assimilation ledger: what is taken from which parent and what is not |
