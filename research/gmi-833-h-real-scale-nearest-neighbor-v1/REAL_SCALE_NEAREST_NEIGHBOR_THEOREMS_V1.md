# Named results — gmi-833-h-real-scale-nearest-neighbor-v1

Every result below is stated at one registered scope and at no other. No
result here is composed with any certificate of any parent package; `FGS-2`
forbids it and `CROSS_SCOPE_GATE_COMPOSITION` is in `forbidden_promotions`.

Scope, from `FREEZE_V1.md` section 3 and the slice addenda: `SIGMA_H05R` —
row `Nearest-neighbor / exemplar memory.`; grammar `G_NN`; ecology `F05`, the
descriptor closure (prefixes of length ≥ 2) of the sha256-bound source
`D = /usr/share/dict/american-english` (104,334 tokens, digest
`9e66281f7e51`), 776,142 descriptors, presented under the registered Knuth
permutation `key(i) = (i * 2654435761) mod 2**32`; `n_fit` 679,124, `n_held`
97,018.

The single registered result **closes** at 11 of 11. Both routes agree; the
checker's verdict is `GREEN`, which reports internal soundness.

---

## `RNN-1` — a family-blind recovery over the registered readout language identifies the addressable stored-exemplar readout at `SIGMA_H05R`

**Statement.** The family-blind recovery procedure (fewest exact decision
errors on the rank-score set, ties by charged cost then readout name; the
readout language `R = {C0, C1, LEN<=7..12, CNT>=1..3, PREF_VOTE, EXT_VOTE}`
closed before any outcome) selects **`CNT>=1`** — "is the query addressable in
the stored exemplar table?" — whose post-hoc structural class is
`STORED_EXEMPLAR_MEMBERSHIP`, the class the parent's finite-scope contract
`ADDRESSABLE_CONTEXT_READ` names. At the rank stage it makes **13,810 decision
errors** on 203,738 rank-score queries against the fit-majority rule's
**32,887**. Fitted at full scale (store = all 679,124 fit descriptors) and
evaluated on the disjoint 97,018 held-out descriptors, it makes **1,535
decision errors** against the fit-majority rule's **15,615** — prototype
agreement 95,483 / 97,018. The symmetric half-split regeneration (R09,
corrected from the measured-asymmetric complementary split, whose failure is
recorded as the boundary of the store-size-asymmetry attribution) recovers the
same class on both halves: `CNT>=1` at 40,386 errors (store `fit_lo`, score
`fit_hi`, majority 54,714) and at 39,310 errors (store `fit_hi`, score
`fit_lo`, majority 54,936). Both registered nulls fire against the committed
constructions: the label-shuffle null (`random.Random(20260921)`) makes
**27,203** errors, strictly more than the majority rule's 15,615; the
shuffled-store design null (`random.Random(20260922)`) makes **13,854**
errors, more than three times the arm's 1,535. The store ladder of the
selected readout is monotone non-increasing in the stored budget:
`{1000: 72165, 5000: 61270, 10000: 55787, 30000: 45081, 67912: 35283,
135824: 25997, 271649: 13934, 679124: 1535}`. The scan-vs-vocabulary-index
crossover is `m* = 110,799` (the smallest `m` with `2m > V + 27`, `V =
221,569` distinct stored descriptors, index cost 221,596). The matched
**source-order presentation control fires**: under the un-permuted contiguous
presentation the family readout `CNT>=1` degrades to 79,435 held errors
against the majority's 17,454 and the selected readout (`LEN<=10`, 16,406
errors) fails the registered F1 margin (16,406 > 8,727), so the registered
presentation lever is load-bearing and the effect is not an artifact of the
table readout alone. Every quantity is an exact integer decision count,
committed in `REAL_RUNS/scope_SIGMA_H05R.json`, replayed exactly by route A
and re-derived by route B (`independent_oracle_nn_v1.py`, which imports none
of the primary executor).

**Quantifiers.** This scope only, this ecology only, this source only.
Nothing is claimed about nearest-neighbour or exemplar memory on any other
ecology, source, presentation, or grammar; in particular no claim about
associative memory (`H06`) or about a *k > 1* vote under a different
presentation.

**Assumptions.** The `D` digest holds at run time (`9e66281f7e51`); the
registered Knuth presentation key `(i * 2654435761) mod 2**32`; the arithmetic
7:1 slice and the `rank_fit`/`rank_score`/`fit_lo`/`fit_hi` sub-splits of the
slice addenda; the readout language `R` and the exclusion of the
membership-with-majority-fallback readout as semantically `C1`; the fit
shared fraction exceeds 1/2 (the executor asserts it before enumeration); the
winner rule of the slice addendum; the corrected symmetric half-split R09;
the registered null constructions and seeds; the charged-cost model
(`2m` vs `V + 27`) of the slice addendum.

**Dependencies.** `grammar_nn_v1.py` for the readout language, the classifier
and the presentation key; `FREEZE_V1.md` sections 3 to 11;
`FREEZE_V1_ARITHMETIC_ADDENDUM.md`; `FREEZE_V1_SLICE_ADDENDUM.md`;
`FREEZE_V1_SLICE_ADDENDUM_R2.md`. It depends on no artifact of any parent
package. Receipt: `REAL_RUNS/scope_SIGMA_H05R.json`, `RESULT_V1.json` row
`H05`, `ORACLE_RESULT_V1.json`.

**Falsifiers.** A different selected readout class at the rank stage or on
either half of the regeneration; a selected arm whose held error count
exceeds half the fit-majority rule's (F1); a label-null that fails to exceed
the fit-majority rule (F2); a design-null that fails to exceed three times the
arm (F3); a non-monotone store ladder; a crossover `m*` at which the scan arm
does not strictly exceed the index arm; a source-order control that clears F1;
any cross-scope gate composition or foreign `sigma`; disagreement between
routes A and B.

**Strongest parents.** Fix & Hodges 1951 and Cover & Hart 1967 for the
nearest-neighbour rule and its error bound; Hart 1968 for the condensed
exemplar set, whose addressability the recovered readout measures; Knuth 1997
for the multiplicative-hash presentation lever; Salton, Wong & Yang 1975 for
the descriptor vocabulary; Wilson & Martinez 2000 for stored-exemplar
reduction and its cost trade-off; the in-repository parents in
`PARENT_LEDGER.md` for the ledger shape, the classifier idea, the presentation
lever and the custody chain. None of it is claimed novel here.

**Forbidden extrapolations.** `CROSS_SCOPE_GATE_COMPOSITION`;
`REAL_SCALE_VALIDATION_COMPLETE`; `INDEPENDENT_TEAM_REPLICATION`; `M5`; `EV4`;
`EV5`; `FINITE_EVIDENCE_IMPLIES_REAL_SCALE`; `SECTION_H_COMPLETE`;
`ALL_KNOWN_FORM_RECOVERY`; `UNIVERSAL_GRAMMAR_NEUTRALITY`;
`FRONTIER_SCALE_VALIDATION`; `COMPLETE_GMI`; any statement about
`SIGMA_HA`, `SIGMA_H01`..`SIGMA_H04` or any other scope; any claim that a
*k-NN* vote with `k > 1` (PREF_VOTE/EXT_VOTE) beats the membership readout
under the registered presentation (it does not: 15,108 / 19,018 vs 1,535 on
held) — what is recovered is the addressable stored exemplar, not the vote.

---

## `RNN-2` — the registered presentation lever is load-bearing: the source-order matched control fires

**Statement.** Under the identical ecology, readout language, recovery
procedure and arithmetic slice, but with the descriptor list read in source
(alphabetical) order instead of under the registered Knuth permutation, the
held tail is dominated by long unique descriptors, the stored table barely
covers it, and the family readout `CNT>=1` makes **79,435** held decision
errors against the majority rule's **17,454** (it is *worse* than the
majority rule). The selected readout under the source-order presentation is
`LEN<=10` (16,406 errors), which fails the registered F1 margin (16,406 >
8,727 = 17,454 // 2). The control therefore fires, demonstrating that the
family effect recovered in `RNN-1` is not an artifact of the table readout
alone but requires the registered presentation — the target-independent
permutation that makes the stored table cover the held-out descriptors
uniformly.

**Quantifiers.** This scope only. The control is a matched negative: only the
presentation differs.

**Assumptions.** Same as `RNN-1`, with the presentation key replaced by the
identity (source order).

**Dependencies.** Same as `RNN-1`; the control numbers are in
`REAL_RUNS/scope_SIGMA_H05R.json` under `presentation_control` and re-derived
by route B.

**Falsifiers.** A source-order presentation under which the family readout
clears F1, or a selected source-order readout that clears F1, would falsify
the load-bearing claim.

**Strongest parents.** The parents' registered presentation lever
(`gmi-833-h-real-scale-classical-v1` `L1`); the matched-negative-control
doctrine of the Section-H requirement ledger (`R05`).
