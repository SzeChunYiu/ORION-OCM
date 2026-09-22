# Named results — gmi-833-h-real-scale-particle-population-v1

Every result below is stated at one registered scope and at no other. No result
here is composed with any certificate of any parent package; `FGS-2` forbids it
and `CROSS_SCOPE_GATE_COMPOSITION` is in `forbidden_promotions`.

Scope, from `FREEZE_V1.md` section 3 and the slice addenda: `SIGMA_H19R` — row
`Particle/population inference.`; grammar `G_PP`; ecology `F19`, the
stored-particle-population table over the descriptor closure (prefixes of length
≥ 2) of the sha256-bound source `D = /usr/share/dict/american-english` (104,334
tokens, digest `9e66281f7e51`), 776,142 descriptors, presented under the
registered Knuth permutation `key(i) = (i * 2654435761) mod 2**32`; `n_fit`
679,124, `n_held` 97,018. The registered query set is the descriptors with at
least two particles (37,965 distinct; 373,409 scored fit queries, 53,230 scored
held queries). The registered particle vote is `VOTE_K = 3`.

The single registered result **closes** at 11 of 11. Both routes agree; the
checker's verdict is `GREEN`, which reports internal soundness.

---

## `RSC-PP-1` — a family-blind recovery over the registered readout language identifies the population-plurality readout at `SIGMA_H19R`

**Statement.** The family-blind recovery procedure (fewest exact decision errors
on the rank-score set, ties by charged cost then readout name; the readout
language `R` of 63 arms closed before any outcome: `C0`, `C1`, `LEN<=6..12`,
`CNT>=1..3`, `ASSOC>=1..3`, the threshold conjunctions `LEN<=L&CNT>=j` and
`LEN<=L&ASSOC>=j` for L = 6..12, j = 1..3, `PLUR`, `PLUR_W`, `PREF_VOTE`,
`EXT_VOTE`, `MEM_FALLBACK`, `PARTICLE_1`) selects **`PLUR`** — "does the stored
population of particles attached to `q` carry a strict plurality of positive
votes?" — whose post-hoc structural class is `POPULATION_PLURALITY`: the answer
is the **mode over a population of many weak samples**, not the value of any one
stored item. At the rank stage (store = `rank_fit` 475,386, score = `rank_score`
203,738) it makes **5,366 decision errors** against the fit-majority rule's
**42,073**. Fitted at full scale (store = all 679,124 fit descriptors) and
evaluated on the disjoint 53,230 scored held queries, it makes **622 decision
errors** against the fit-majority rule's **20,001** — prototype agreement
**52,608 / 53,230**. The symmetric half-split regeneration (R09, registered from
the start) recovers the same readout and the same class on both halves: `PLUR`
at 16,581 errors (store `fit_lo`, score `fit_hi`, majority 70,170) and at 20,732
errors (store `fit_hi`, score `fit_lo`, majority 70,460); all four stages
recover `POPULATION_PLURALITY` and, unlike the siblings, the winner rule picks
the **same readout** at every stage. The store-size-asymmetric complementary
split (store = `rank_score` 203,738, score = `rank_fit` 475,386) degenerates —
the winner becomes `LEN<=6&CNT>=3` at 38,212 errors and `PLUR` rises to 46,478
against a majority of 98,557, because the store covers 89.1% of the score set's
positions (232,968 / 261,501) against the rank stage's 98.1% (109,816 / 111,908)
— recorded as the boundary datum that fixes the symmetric half-split as the
registered R09. Both registered nulls fire against the committed constructions:
the label-shuffle null (`random.Random(20260926)`) makes **24,596** errors,
strictly more than the majority rule's 20,001; the particle-reweight design null
(`random.Random(20260927)`), which permutes the stored particles' votes among
the stored descriptors and so destroys only the alignment between a particle's
vote and the population it belongs to while keeping the store size, the
population structure, the query set and the length structure fixed, makes
**33,268** errors — more than three times the arm's 622, and the winner under
that null becomes `MEM_FALLBACK` at 2,426 errors, so the plurality mechanism is
what the reweight destroys. The admitted arms that read a single stored item
are **rejected by the winner rule at every stage**: the stored-table read
`MEM_FALLBACK` (2,426 held), the one-particle read `PARTICLE_1` (12,278 held)
and the count-weighted plurality `PLUR_W` (9,533 held), against the arm's 622;
the best threshold conjunction (`LEN<=6&ASSOC>=3`) makes 11,522 held errors —
18.5 times the arm — and the sibling bare reads make `CNT>=1` 19,933, `LEN<=9`
18,338, `ASSOC>=2` 18,752. The store ladder of the selected readout is monotone
non-increasing in the stored budget: `{1000: 20024, 5000: 19914, 10000: 19596,
30000: 18501, 67912: 17014, 135824: 14364, 271649: 9943, 679124: 622}`. The
scan-vs-vocabulary-index crossover is `m* = 110,799` (the smallest `m` with
`2m > V + 27`, `V = 221,569` distinct stored descriptors, index cost 221,596).
The matched **source-order presentation control fires**: under the un-permuted
contiguous presentation the family readout `PLUR` degrades to 21,096 held errors
against the majority's 21,104 — it no longer separates at all — and the selected
readout (`LEN<=6`, 15,162 errors) fails the registered F1 margin (15,162 >
10,552 = 21,104 // 2), so the registered presentation lever is load-bearing. The
**single-particle-store control fires**: with each query's stored particle
population collapsed to at most one particle, `PLUR` makes 12,210 held errors
against the majority's 20,001 and fails F1 (12,210 > 10,000), while on the
registered ecology the same arm makes 622 — so the mechanism requires a stored
**population**, and one particle does not carry the answer. Every quantity is an
exact integer decision count, committed in `REAL_RUNS/scope_SIGMA_H19R.json`,
replayed exactly by route A and re-derived by route B
(`independent_oracle_pp_v1.py`, which imports none of the primary executor).

**Quantifiers.** This scope only, this ecology only, this source only. Nothing
is claimed about particle/population inference on any other ecology, source,
presentation, or grammar; in particular no claim about Bayesian
inference/belief-state systems (`H17`), about probabilistic graphical models
(`H18`), about nearest-neighbour / exemplar memory (`H05`), about associative
memory (`H06`), or about decision trees / rule systems (`H08`).

**Assumptions.** The `D` digest holds at run time (`9e66281f7e51`); the
registered Knuth presentation key `(i * 2654435761) mod 2**32`; the arithmetic
7:1 slice and the `rank_fit`/`rank_score`/`fit_lo`/`fit_hi` sub-splits of the
slice addenda; the registered query set `|pop(q)| >= 2`; the registered particle
vote `VOTE_K = 3`; the readout language `R` and the constant-branch exclusion
rule of the slice addendum, which admits `MEM_FALLBACK` (its stored branch reads
the stored-table plurality, two-valued: positive on 31,880 and negative on
21,279 of the held scored queries, with 3 queries left without a stored
particle); the fit scored positive fraction exceeds 1/2 (the executor asserts it
before enumeration, 232,779 / 373,409 = 0.623); the winner rule of the slice
addendum; the symmetric half-split R09; the registered null constructions and
seeds; the charged-cost model (`2m` vs `V + 27`) of the slice addendum.

**Dependencies.** `grammar_pp_v1.py` for the readout language, the classifier,
the registered particle vote and the presentation key; `FREEZE_V1.md` sections 3
to 11; `FREEZE_V1_SLICE_ADDENDUM.md`; `FREEZE_V1_SLICE_ADDENDUM_R2.md`. It
depends on no artifact of any parent package. Receipt:
`REAL_RUNS/scope_SIGMA_H19R.json`, `REAL_RUNS/FROZEN_PREDICTIONS_R8.json`,
`RESULT_V1.json` row `H19`, `ORACLE_RESULT_V1.json`.

**Falsifiers.** A different selected readout class at the rank stage or on
either half of the regeneration; a selected arm whose held error count exceeds
half the fit-majority rule's (F1); a label-null that fails to exceed the
fit-majority rule (F2); a particle-reweight design-null that fails to exceed
three times the arm (F3); a single-particle-store control in which the plurality
read keeps an advantage; a non-monotone store ladder; a crossover `m*` at which
the scan arm does not strictly exceed the index arm; a source-order control that
clears F1; a winning readout whose class is not `POPULATION_PLURALITY`; any
cross-scope gate composition or foreign `sigma`; disagreement between routes A
and B.

**Strongest parents.** Metropolis & Ulam 1949 (the Monte Carlo method) and
Metropolis, Rosenbluth, Rosenbluth, Teller & Teller 1953 for the population of
weighted samples as the computational object; Gordon, Salmond & Smith 1993 and
Kitagawa 1996 (bootstrap and auxiliary particle filters) for the
sequential-importance population whose answer is the mode/consensus over
particles rather than any single particle; Doucet, de Freitas & Gordon 2001 and
Doucet, Godsill & Andrieu 2000 for the particle-population approximation of a
distribution and its marginal-vs-joint reading; Del Moral 2004 for the
mean-field/normalised-consensus analysis of a particle population; Rosenblatt
1956 and Parzen 1962 for the local-averaging estimate over a sample population;
Breiman 1996 (bagging) and Dietterich 2000 for the ensemble consensus over many
weak members; Knuth 1997 for the multiplicative-hash presentation lever; Salton,
Wong & Yang 1975 for the descriptor vocabulary; the in-repository parents in
`PARENT_LEDGER.md` for the ledger shape, the classifier idea, the presentation
lever and the custody chain. None of it is claimed novel here.

**Forbidden extrapolations.** `CROSS_SCOPE_GATE_COMPOSITION`;
`REAL_SCALE_VALIDATION_COMPLETE`; `INDEPENDENT_TEAM_REPLICATION`; `M5`; `EV4`;
`EV5`; `FINITE_EVIDENCE_IMPLIES_REAL_SCALE`; `SECTION_H_COMPLETE`;
`ALL_KNOWN_FORM_RECOVERY`; `UNIVERSAL_GRAMMAR_NEUTRALITY`;
`FRONTIER_SCALE_VALIDATION`; `COMPLETE_GMI`; any statement about `SIGMA_HA`,
`SIGMA_H05R`, `SIGMA_H06R`, `SIGMA_H08R` or any other scope; any claim that the
bare membership readout (`CNT>=1` 19,933 held errors), the bare association
readout (`ASSOC>=2` 18,752), the length threshold (`LEN<=9` 18,338), the
neighbourhood votes (`PREF_VOTE` 14,160 / `EXT_VOTE` 33,232), the count-weighted
plurality (`PLUR_W` 9,533), the stored-table read (`MEM_FALLBACK` 2,426) or the
one-particle read (`PARTICLE_1` 12,278) beats the family readout under the
registered presentation — what is recovered is the **plurality over the stored
particle population**, the mode over a population of weak samples, distinct from
the siblings' stored-exemplar membership, cue-association fan-out and
threshold-conjunction classes.

---

## `RSC-PP-2` — the plurality mechanism requires a population: the single-particle-store control and the reweight null both fire

**Statement.** The recovered readout's mechanism is the **consensus over a
population**, and two registered matched negatives isolate it. (a) The
**single-particle-store control**: on the identical ecology, query set, label
and readout language, with each query's stored particle population collapsed to
at most one particle, `PLUR` makes **12,210** held errors against the majority's
20,001 and **fails F1** (12,210 > 10,000), while on the registered ecology the
same arm makes **622**; the admitted one-particle read `PARTICLE_1` lands within
68 decisions of the collapsed control (12,278), so with one particle the
plurality read *is* the single-particle read. (b) The **particle-reweight design
null**: permuting the stored particles' votes among the stored descriptors —
which preserves the store size, the population sizes, the query set and the
length structure and destroys only the alignment between a particle's vote and
the population it belongs to — raises `PLUR` to **33,268** errors, more than
three times the arm's 622, and moves the winner to `MEM_FALLBACK` (2,426); the
membership arm `CNT>=1` is untouched at its measured 19,933, as a construction
that moves only particle votes must be. Both negatives therefore fire, and
together they show the recovered effect is carried by the population's
consensus and not by the table's geometry or by any single stored item.

**Quantifiers.** This scope only. Both controls are matched: only the stored
population's composition changes.

**Assumptions.** Same as `RSC-PP-1`, with the store's particle population
collapsed (a) or its votes reweighted (b).

**Dependencies.** Same as `RSC-PP-1`; the control numbers are in
`REAL_RUNS/scope_SIGMA_H19R.json` under `single_particle_store` and
`nulls.design`, and re-derived by route B.

**Falsifiers.** A single-particle store under which the plurality read clears
F1, or a reweight null that leaves the plurality arm at its registered count,
would falsify the load-bearing claim.

**Strongest parents.** The parents' matched-negative-control doctrine (Section-H
requirement `R05`); the siblings' registered single-item rejection-datum form
(`gmi-833-h-real-scale-decision-trees-v1` `FREEZE_V1_SLICE_ADDENDUM_R2.md` R2.6;
`gmi-833-h-real-scale-associative-memory-v1`) — form only.
