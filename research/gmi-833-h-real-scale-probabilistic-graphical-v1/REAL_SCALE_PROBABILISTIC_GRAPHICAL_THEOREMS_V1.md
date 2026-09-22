# Named results — gmi-833-h-real-scale-probabilistic-graphical-v1

Every result below is stated at one registered scope and at no other. No
result here is composed with any certificate of any parent package; `FGS-2`
forbids it and `CROSS_SCOPE_GATE_COMPOSITION` is in `forbidden_promotions`.

Scope, from `FREEZE_V1.md` section 3 and the slice addenda: `SIGMA_H18R` —
row `Probabilistic graphical models.`; grammar `G_PGM`; ecology `F16`, the
stored factor graph over the descriptor closure (prefixes of length ≥ 2) of
the sha256-bound source `D = /usr/share/dict/american-english` (104,334
tokens, digest `9e66281f7e51`), 776,142 descriptors, split into two
independent factors `R1` (even-length tokens, 387,582 descriptor occurrences)
and `R2` (odd-length tokens, 388,560), presented under the registered Knuth
permutation `key(i) = (i * 2654435761) mod 2**32`; `n_fit` 679,124, `n_held`
97,018.

The single registered result **closes** at 11 of 11. Both routes agree; the
checker's verdict is `GREEN`, which reports internal soundness.

The row's registered contract is recorded in `FREEZE_V1.md` section 2 as a
**steer** — `research/gmi-833-obstruction-census-v1/FROZEN_FAMILY_REGISTRY_V1.json`
records `TRIPLE_PARITY` / "registered three-variable dependency response" for
this row, and `FREEZE_V1_SLICE_ADDENDUM_R3.md` is the measurement addendum that
records, at this scope, the two pre-measurement design statistics that did not
survive measurement and the one stage they are attributed to. The steer
constrains the structure of the recovered readout (a dependency response over
the stored factorisation, every factor must agree) and supplies no evidence;
the addendum changes no registered form.

---

## `RSC-PGM-1` — a family-blind recovery over the registered readout language identifies the factor-product (message-passing) readout at `SIGMA_H18R`

**Statement.** The family-blind recovery procedure (fewest exact decision
errors on the rank-score set, ties by charged cost then readout name; the
readout language `R` of 54 arms closed before any outcome: `C0`, `C1`,
`LEN<=6..12`, `R1CNT>=1..3`, `R2CNT>=1..3`, `R1ASSOC>=1..3`,
`R2ASSOC>=1..3`, the 16 factor-product arms `R1x&R2y`, the length-gated joint
arms `LEN<=L&R1ASSOC>=1&R2ASSOC>=1` and `LEN<=L&R1CNT>=1&R2CNT>=1` for
L = 6..12, `PREF_VOTE`, `EXT_VOTE`, `MEM_FALLBACK`) selects
**`R1ASSOC>=1&R2ASSOC>=1`** — "do BOTH stored factors agree that the query has
a continuation?" — whose post-hoc structural class is
`FACTOR_JOINT_CONSISTENCY`: a conjunction over factor-local evidence of two
INDEPENDENT stored relations. At the rank stage it makes **13,385 decision
errors** on 203,738 rank-score queries against the fit-majority rule's
**62,716**. Fitted at full scale (store = all 679,124 fit descriptors) and
evaluated on the disjoint 97,018 held-out descriptors, it makes **1,893
decision errors** against the fit-majority rule's **29,821** — prototype
agreement 95,125 / 97,018. The symmetric half-split regeneration (R09,
registered from the start) recovers the same class AND the same arm on both
halves: `R1ASSOC>=1&R2ASSOC>=1` at 42,732 errors (store `fit_lo`, score
`fit_hi`, majority 104,377) and at 51,085 errors (store `fit_hi`, score
`fit_lo`, majority 104,395). Both registered nulls fire against the committed
constructions: the label-shuffle null (`random.Random(20260926)`) makes
**42,019** errors, strictly more than the majority rule's 29,821; the
one-factor design null (`random.Random(20260927)`), which replaces the R2
factor with a same-size relation drawn from the descriptor list, leaving the
R1 factor, the store size, the length structure and the query set fixed,
makes **9,770** errors, more than three times the arm's 1,893 — and under
that corruption the arm reading the **intact** factor alone keeps exactly its
uncorrupted error count (**11,113**) while the arm reading the **corrupted**
factor falls to **15,536** (toward chance, 29,821), which is what proves
exactly one factor was broken. The membership-with-fallback arm
`MEM_FALLBACK` (admitted because its stored branch reads the STORED label of
the query, two-valued over the store) is **rejected by the winner rule** at
every stage — 55,719 rank errors, 18,985 held errors, 116,632 / 124,082 on the
two regeneration halves. The store ladder of the selected readout is monotone
non-increasing in the stored budget: `{1000: 64554, 5000: 57021, 10000:
52720, 30000: 45591, 67912: 38812, 135824: 31879, 271649: 22458, 679124:
1893}`. The scan-vs-vocabulary-index crossover is `m* = 110,799` (the smallest
`m` with `2m > V + 27`, `V = 221,569` distinct stored descriptors, index cost
221,596). Every quantity is an exact integer decision count, committed in
`REAL_RUNS/scope_SIGMA_H18R.json`, replayed exactly by route A and re-derived
by route B (`independent_oracle_pgm_v1.py`, which imports none of the primary
executor).

**Quantifiers.** This scope only, this ecology only, this source only, this
factor split only. Nothing is claimed about probabilistic graphical models on
any other ecology, source, presentation, factor split or grammar; in
particular no claim about decision trees / rule systems (`H08`), about
associative memory (`H06`), about nearest-neighbour / exemplar memory (`H05`),
about Bayesian inference/belief-state systems, or about a different pair of
factors under a different presentation.

**Assumptions.** The `D` digest holds at run time (`9e66281f7e51`); the
registered Knuth presentation key `(i * 2654435761) mod 2**32`; the arithmetic
7:1 slice and the `rank_fit`/`rank_score`/`fit_lo`/`fit_hi` sub-splits of the
slice addenda; the factor split rule `R1` = even-length tokens, `R2` =
odd-length tokens, and the measured occurrence counts 387,582 / 388,560 whose
sum is `T`; the readout language `R` and the constant-branch exclusion rule of
the slice addendum, which admits `MEM_FALLBACK`; the fit positive fraction
exceeds 1/2 (the executor asserts it before enumeration, 470,352 / 679,124);
the winner rule; the symmetric half-split R09; the registered null
constructions and seeds; the charged-cost model (`2m` vs `V + 27`).

**Dependencies.** `grammar_pgm_v1.py` for the readout language, the classifier
and the presentation key; `FREEZE_V1.md` sections 3 to 11 (section 2 carries the
row's registered contract steer); `FREEZE_V1_SLICE_ADDENDUM.md`;
`FREEZE_V1_SLICE_ADDENDUM_R2.md`; `FREEZE_V1_SLICE_ADDENDUM_R3.md`. It depends
on no artifact of any parent package. Receipt:
`REAL_RUNS/scope_SIGMA_H18R.json`, `RESULT_V1.json` row `H18`,
`ORACLE_RESULT_V1.json`.

**Falsifiers.** A different selected readout class at the rank stage or on
either half of the regeneration; a selected arm whose held error count exceeds
half the fit-majority rule's (F1); a label-null that fails to exceed the
fit-majority rule (F2); a design-null that fails to exceed three times the arm
(F3); an intact-factor arm whose error count MOVES under the one-factor
corruption (F4); a non-monotone store ladder; a crossover `m*` at which the
scan arm does not strictly exceed the index arm; any cross-scope gate
composition or foreign `sigma`; disagreement between routes A and B.

**Strongest parents.** Pearl 1988 (Bayesian networks as a factorisation),
Kschischang, Frey & Loeliger 2001 (factor graphs and message passing),
Lauritzen & Spiegelhalter 1988 (local computation over graph structure),
Bishop 2006 and Koller & Friedman 2009 (factors and independence structure as
the stored object); Knuth 1997 for the multiplicative-hash presentation lever;
Salton, Wong & Yang 1975 for the descriptor vocabulary; the in-repository
parents in `PARENT_LEDGER.md` for the ledger shape, the classifier idea, the
presentation lever, the null constructions and the custody chain. None of it
is claimed novel here.

**Forbidden extrapolations.** `CROSS_SCOPE_GATE_COMPOSITION`;
`REAL_SCALE_VALIDATION_COMPLETE`; `INDEPENDENT_TEAM_REPLICATION`; `M5`; `EV4`;
`EV5`; `FINITE_EVIDENCE_IMPLIES_REAL_SCALE`; `SECTION_H_COMPLETE`;
`ALL_KNOWN_FORM_RECOVERY`; `UNIVERSAL_GRAMMAR_NEUTRALITY`;
`FRONTIER_SCALE_VALIDATION`; `COMPLETE_GMI`; any statement about `SIGMA_H05R`,
`SIGMA_H06R`, `SIGMA_H08R` or any other scope; any claim that the single-factor
readouts (`R1CNT>=1` 9,828, `R2CNT>=1` 10,033, `R1ASSOC>=1` 11,113,
`R2ASSOC>=1` 11,824 held errors), the neighbourhood votes, or the
membership-with-fallback readout (`MEM_FALLBACK` 18,985 held errors) beat the
factor-product readout under the registered presentation — what is recovered
is the factor-product conjunction, a joint readout over two independent
factors, distinct from the siblings' single-dimension classes.

---

## `RSC-PGM-2` — the matched negatives pin the class down: the joint structure, not the readout form, is what the winner rule recovers

**Statement.** Two matched negatives are registered and both behave as the
class requires.

*(a) The single-factor ecology control.* Holding the ecology, the readout
language `R` and the winner rule fixed, replacing the protected interface with
one that depends on a SINGLE factor — `y_sf(q) = 1 iff |A1(q)| >= 1` — moves
the win away from every factor-product arm: the winner is `R1ASSOC>=1` at
**899 errors** (class `SINGLE_FACTOR_ASSOCIATION`, fit-majority rule 19,277)
and the best factor-product arm is `R1ASSOC>=1&R2ASSOC>=1` at **12,437**
errors. The joint arm is 13.8 times WORSE than the single-factor arm on a
single-factor ecology, so its win on the registered ecology is evidence about
the JOINT structure and not about the readout form. **The direction is the
registered one**: this is the R06 lower-bound control doing its job, and a
reader who takes `899 < 12,437` for a failed gate would have the control
inverted — the control asserts that the joint arm LOSES when the ecology
depends on one factor.

*(b) The one-factor design null.* Destroying exactly ONE of the two stored
factors — replacing `R2` with a same-size relation drawn from the descriptor
list (`random.Random(20260927)`), leaving `R1`, the store size, the length
structure and the query set untouched — breaks the family readout: the joint
arm rises to **9,770** errors (> 3× its 1,893), while the arm that reads the
INTACT factor alone keeps exactly its uncorrupted error count at **11,113**
and the arm that reads the corrupted factor falls to **15,536**. Exactly one
factor moved.

*(c) The source-order presentation control.* Under the identical ecology,
readout language, recovery procedure and arithmetic slice, but with the
descriptor list read in source order instead of under the registered Knuth
permutation, the winning readout is `LEN<=6` at **22,919** errors against the
majority rule's **32,834** (F1 half 16,417), so it fails the registered F1
margin and the control fires; the family readout under source order is
**64,099** errors, far worse than the majority rule. The registered
presentation lever is load-bearing.

**Quantifiers.** This scope only. Each control is a matched negative: only the
named coordinate differs.

**Assumptions.** Same as `RSC-PGM-1`, with the stated coordinate replaced.

**Dependencies.** Same as `RSC-PGM-1`; the control numbers are in
`REAL_RUNS/scope_SIGMA_H18R.json` under `single_factor_control`,
`nulls.design` and `presentation_control`, and are re-derived by route B.

**Falsifiers.** A single-factor ecology on which a factor-product arm wins;
a one-factor corruption under which the intact factor's arm moves, or the
corrupted factor's arm does not; a source-order presentation under which the
winning readout clears F1. Any one falsifies the class claim.

**Strongest parents.** The matched-negative-control doctrine of the Section-H
requirement ledger (`R05`); the siblings' registered control forms; the
factor-graph literature of `RSC-PGM-1` for what a corruption of one factor
must do to a factor-product readout.

---

## `RSC-PGM-3` — exact inference over the stored factorisation agrees with the family-blind winner (boundary datum)

**Statement.** As a **boundary datum**, scored outside the readout language
`R` (which stays closed at 54 arms), the executor evaluates the
exact-inference comparison readout `ECM_PRODUCT_FORM_MESSAGE` — the product
form of the two factor-local messages at the query, i.e. what message passing
over the stored two-factor model returns. On the 97,018 held-out descriptors
it makes **1,893 decision errors**: **decision-identical to the family-blind
winner**. The family-blind winner rule therefore recovers, from a closed
pre-outcome readout language, the readout that exact inference over the stored
factorisation produces — this is the closest thing to the row's registered
contract steer being earned rather than declared, since the family-blind
recovery lands on the dependency response the contract names, without the
readout language ever containing a marginal, a joint table, or any
message-passing routine.

**Quantifiers.** This scope only, this held slice only. The datum is a
comparison, not a gate: it is not a member of `R`, it drives no winner, and no
gate certificate depends on it.

**Assumptions.** Same as `RSC-PGM-1`.

**Dependencies.** Same as `RSC-PGM-1`; the datum is in
`REAL_RUNS/scope_SIGMA_H18R.json` under `ecm` and is re-derived by route B.

**Falsifiers.** A product-form readout that disagrees with the winner at the
held stage would falsify the agreement claim (it would not falsify
`RSC-PGM-1`, which does not depend on it).

**Strongest parents.** Kschischang, Frey & Loeliger 2001 and Lauritzen &
Spiegelhalter 1988 for the message-passing/exact-inference semantics; the
sibling `gmi-833-h-real-scale-decision-trees-v1` for the boundary-datum
reporting form.
