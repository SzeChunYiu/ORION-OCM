# gmi-833-h-real-scale-particle-population-v1 — CORE

**What this is.** A continuation of the Section-H real-scale line of issue
#833 for the named-family row `Particle/population inference.`

It imports **no gate certificate from any parent**. All eleven Section-H
coordinates R01–R11 are earned at this package's own scope — `SIGMA_H19R` — on
a sha256-bound external real source (`/usr/share/dict/american-english`,
104,334 tokens, digest `9e66281f7e51`), with exact integer decision counts and
two materially independent routes. `CROSS_SCOPE_GATE_COMPOSITION` is in
`forbidden_promotions` and a test asserts that no gate certificate carries a
scope other than its own.

## The headline

| row | scope | outcome |
|---|---|---|
| `Particle/population inference.` | `SIGMA_H19R` | **closed**, 11 of 11 |

The family-blind winner rule over the registered readout language `R` (63 arms,
frozen pre-outcome in `FREEZE_V1_SLICE_ADDENDUM.md`) recovers the family's own
mechanism — the **population plurality**: a query is predicted positive iff the
stored **population of particles** attached to it carries a strict plurality of
positive votes (`PLUR`, the mode over many weak samples, not the value of any
one stored item). On 53,230 scored held-out real descriptors it makes **622
decision errors** against the fit-majority rule's **20,001** (prototype
agreement 52,608 / 53,230). Both registered nulls fire: the label-shuffle null
gives 24,596 errors, the particle-reweight design null 33,268 (> 3× the arm).
The store ladder is monotone to 622; the scan-vs-vocabulary-index crossover is
`m* = 110,799`. The matched **source-order presentation control fires**: under
the un-permuted presentation the family readout degrades to 21,096 errors
against the majority's 21,104 and the winning readout (`LEN<=6`, 15,162) fails
the registered F1 margin. The **single-particle-store control fires**: with each
query's stored population collapsed to one particle the plurality read makes
12,210 errors and fails F1, while on the registered ecology it makes 622.

## The registered design, in one paragraph

The ecology `F19` is the stored-particle-population table over the descriptor
closure of the sha-bound source: every prefix of length ≥ 2 of every token,
776,142 descriptors in total. The **population** of a query `q` is its distinct
one-letter extensions over the full source; a **particle** `p` votes 1 iff its
source occurrence count is ≥ 3 (`VOTE_K = 3`). The protected interface is the
decision `y(q) = 1 iff the strict plurality of pop(q) votes 1` (ties → 0),
evaluated on the descriptors with at least two particles (37,965 distinct;
53,230 scored held queries). The registered presentation is the parents'
target-independent Knuth multiplicative hash `key(i) = (i * 2654435761) mod
2**32`, then the arithmetic 7:1 slice (`n_fit` 679,124 / `n_held` 97,018, clear
of the R11 bar), with a `rank_fit`/`rank_score` split for the ranking stage. The
readout language `R` (63 arms) was closed before any outcome; the winner rule
(fewest exact decision errors, ties by charged cost then name) chose `PLUR`, and
the symmetric half-split regeneration (R09, applied from the start) recovers the
same readout and the same class on both halves. Every claimed quantity is an
exact integer decision count, committed in `REAL_RUNS/` and re-derived by route
B. The frozen-prediction record (`R08`) is written before any null or control is
computed and is committed alongside the receipt.

## Reproduce

Stdlib only, no network, no real source needed: the real run's receipts are
committed and every claimed quantity replays exactly from them.

```
cd research/gmi-833-h-real-scale-particle-population-v1
python3 -I -B  independent_oracle_pp_v1.py                       # route B -> ORACLE_RESULT_V1.json
python3 -I -B  real_scale_particle_population_v1.py              # route A -> RESULT_V1.json
python3 -I -O -B test_real_scale_particle_population_v1.py -v
```

To re-run the real-scale extraction from the bound source (host of record
billy-old only, CPython 3.14.4, ~6.5 minutes):

```
python3 -B run_real_scale_particle_population_v1.py
```

## Files

| file | what it is |
|---|---|
| `FREEZE_V1.md` + two addenda | the custody chain: scope, ecology, frozen predictions/falsifiers/claim ceiling; the exact slice form, the registered particle vote and query set, and the readout language `R`; the symmetric half-split R09, the null constructions, the single-particle-store control and the presentation control |
| `MANIFEST_V1.json` | the package manifest with source binding, scope, the row's evidence key `L:17a6204cf5d5` and parent pins |
| `grammar_pp_v1.py` | the readout grammar `G_PP`: the closed 63-arm language `R`, the post-hoc classifier, the registered particle vote, the presentation key, the digest |
| `run_real_scale_particle_population_v1.py` | the real-scale run driver; the only file that reads the real source |
| `real_scale_particle_population_v1.py` | route A: exact replay, the eleven-coordinate ledger, the hostiles, `RESULT_V1.json` |
| `independent_oracle_pp_v1.py` | route B: source-separated, imports none of the above |
| `test_real_scale_particle_population_v1.py` | custody, scope, slice, readout, control and reconciliation tests |
| `REAL_SCALE_PARTICLE_POPULATION_THEOREMS_V1.md` | the named results, each with its four ledgers |
| `PARENT_LEDGER.md` | the assimilation ledger: what is taken from which parent and what is not |
| `REAL_RUNS/` | `scope_SIGMA_H19R.json` (the receipt), `sources.json`, `FROZEN_PREDICTIONS_R8.json` |
| `ISSUE_833_RECONCILIATION_H19_V1.json` | the one row this package closes, ending `L:17a6204cf5d5` |
