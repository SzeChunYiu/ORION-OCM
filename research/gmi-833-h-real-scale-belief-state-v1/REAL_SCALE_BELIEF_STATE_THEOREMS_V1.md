# Named results — gmi-833-h-real-scale-belief-state-v1

Every result below is stated at one registered scope and at no other. No result
here is composed with any certificate of any parent package; `FGS-2` forbids it
and `CROSS_SCOPE_GATE_COMPOSITION` is in `forbidden_promotions`.

Scope, from `FREEZE_V1.md` sections 3 and 4 and
`FREEZE_V1_SLICE_ADDENDUM_H17_V1.md`: `SIGMA_H17R` — row `Bayesian
inference/belief-state systems.`; grammar `G_BS`; ecology `F17`, the set-valued
whole-word hypothesis table over the descriptor-closure positions of the
sha256-bound source `D = /usr/share/dict/american-english` (104,334 tokens,
digest `9e66281f7e51`), 776,142 positions, presented under the registered Knuth
permutation `key(i) = (i * 2654435761) mod 2**32`; `n_fit` 679,124, `n_held`
97,018.

**This package closes nothing.** The single registered row is left open; the
reconciliation carries an empty `replacements` list. What the package delivers
is one boundary and one adjacent scoped positive.

---

## `BS-1` — the registered readout language does not recover the weighted-evidence-belief class at `SIGMA_H17R`; the family-blind winner rule recovers the stored-label read instead

**Statement.** The family-blind winner rule (fewest exact decision errors on the
rank-score set, ties by charged cost then readout name; the readout language `R`
of 88 arms closed before any outcome: `C0`, `C1`, `LEN<=6..12`, `CNT>=1..3`,
`EXT>=1..4`, `WSUM>=8..64`, `WMAX>=7..16`, `WAVG>=6..12`, `WDOM>=3..12`,
`WPAIR>=a_T` for `a` = 3, 4, 5, 6, 8, 10, 12 and `T` = 6, 7, 8, 9, 10, 12 (the
registered 7x6 grid), `MEM_FALLBACK`) selects
**`MEM_FALLBACK`** at the rank stage (6,709 errors vs the fit-majority rule's
21,227), at the held stage (**1,005 errors vs 10,099**, prototype agreement
96,013 / 97,018), and at both regeneration halves (17,338 and 17,200 against
35,481 and 35,618). Its post-hoc structural class is
`STORED_LABEL_READ_WITH_FALLBACK` — the **sibling's** mechanism, not this
row's.

The intended class `WEIGHTED_EVIDENCE_BELIEF` does not win at any stage. Its
best arm at the held stage is `WPAIR>=3_12` at **11,421** errors — an order of
magnitude worse than the stored-label read, and worse than what the row's own
posterior clause delivers when the store can read its own table. The reason is
measured and one-stage: the registered label of `FREEZE_V1.md` section 4 is a
function of the stored completions only, so a store that holds the completions
holds the label; with the store set to the whole source the winner reproduces
it **exactly (0 errors on 97,018 held queries)**. The registered
weight-reassignment design null does not separate the two: the weighted winner
moves only 11,421 → 14,083 (1.23×), against the registered 3× bar of the
sibling packages, and it moves in the direction of a *worse* arm rather than to
chance. The raw count arms are bit-identical under the reassignment
(`EXT>=1` 78,159, `EXT>=2` 68,919, `EXT>=3` 73,842, `EXT>=4` 65,523 — all
unmoved), so the null is clean but weak, and the weakness is structural: with
`EXT >= 2` fixed by the pair clause, the posterior clause `3 * MAX >= 2 * SUM`
is a dominance test whose outcome the length distribution of the completions
largely fixes.

The matched **source-order presentation control fires**: under the un-permuted
contiguous presentation the winner is the constant arm at 11,128 errors against
the majority's 11,128 — it does not beat the majority at all — so the
registered presentation lever is load-bearing. The store ladder of the winning
readout is monotone non-increasing in the stored budget: `{1000: 10081, 5000:
10019, 10000: 9923, 30000: 9517, 67912: 8847, 135824: 8021, 271649: 5519,
679124: 1005}`. The scan-vs-vocabulary-index crossover is `m* = 110,799` (the
smallest `m` with `2m > V + 27`, `V = 221,569` distinct stored descriptors,
index cost 221,596). The label-shuffle null makes 17,379 errors, strictly more
than the majority rule's 10,099. Every quantity is an exact integer decision
count, committed in `REAL_RUNS/scope_SIGMA_H17R.json`, replayed exactly by
route A and re-derived by route B (`independent_oracle_bs_v1.py`, which imports
none of the primary executor).

**Quantifiers.** This scope only, this ecology only, this source only, this
label only. Nothing is claimed about Bayesian inference or belief-state systems
on any other ecology, source, presentation, grammar or label. In particular
this result does NOT claim that the row is unrecoverable: it claims that on the
registered amended ecology `F17`, the intended class loses to the stored-label
read and the registered null cannot separate them.

**Assumptions.** The `D` digest holds at run time (`9e66281f7e51`); the
registered Knuth presentation key `(i * 2654435761) mod 2**32`; the arithmetic
7:1 slice and the `rank_fit`/`rank_score`/`fit_lo`/`fit_hi` sub-splits; the
registered label `y(q) = 1 iff EXT(q) >= 2 and 2*MAX(q) > SUM(q) and
MAX(q) >= T*` with `T* = 8` fixed pre-outcome as the modal source-token length;
the readout language `R` and the winner rule of the slice addendum; the
registered null constructions and seeds; the charged-cost model (`2m` vs
`V + 27`).

**Dependencies.** `grammar_bs_v1.py` for the readout language, the classifier
and the presentation key; `FREEZE_V1.md` sections 3 to 12;
`FREEZE_V1_SLICE_ADDENDUM_H17_V1.md`; `F15_EARNED_BOUNDARY_V1.md` for the
amendment's registered justification. It depends on no artifact of any parent
package. Receipt: `REAL_RUNS/scope_SIGMA_H17R.json`, `RESULT_V1.json` row
`H17`, `ORACLE_RESULT_V1.json`.

**Falsifiers.** A registered readout that beats `MEM_FALLBACK` at the held
stage under the registered winner rule; a weight reassignment under which the
weighted winner degrades by more than 3× while the raw count arms stay intact
(which would make the intended class separable and this boundary void); a
source-order presentation that clears F1; a non-monotone ladder; any cross-scope
gate composition or foreign `sigma`; disagreement between routes A and B. One
registered falsifier of the amendment's first draft DID fire and is recorded in
`CORRECTED_CLAIM_V1.md`: the draft's claim that F1 was structurally
unsatisfiable at this label is refuted by this package's own measurement (the
full-source optimum is 0 errors against a half-majority of 5,049), and the
claim was corrected to the dominance statement above.

**Strongest parents.** For the machinery: the sibling real-scale packages
(`gmi-833-h-real-scale-nearest-neighbor-v1`,
`gmi-833-h-real-scale-associative-memory-v1`,
`gmi-833-h-real-scale-decision-trees-v1`) supply the freeze-first custody chain,
the closed readout-language architecture, the winner rule, the symmetric
half-split regeneration and the matched-presentation control form — form only,
no number. For the mechanism: A. J. Bayes (1763) and P.-S. Laplace
(1812/1814) for the posterior as a ratio of accumulated evidence to total
evidence; J. Pearl (1988), *Probabilistic Reasoning in Intelligent Systems*,
for belief as a distribution over hypotheses updated by evidence; E. T. Jaynes
(2003), *Probability Theory: The Logic of Science*, for the maximum-entropy and
evidence-accumulation reading of the posterior; D. E. Knuth (1997) for the
presentation lever; G. Salton, A. Wong and C. S. Yang (1975) for the descriptor
vocabulary. None of it is claimed novel here.

**Forbidden extrapolations.** `CROSS_SCOPE_GATE_COMPOSITION`;
`ROW_CLOSED_BY_MEASUREMENT`; `BOUNDARY_IS_A_RECOVERY`;
`RAW_COUNT_ARM_IS_THE_FAMILY`; `REAL_SCALE_VALIDATION_COMPLETE`;
`SECTION_H_COMPLETE`; `INDEPENDENT_TEAM_REPLICATION`; `M5`; `EV4`; `EV5`;
`FINITE_EVIDENCE_IMPLIES_REAL_SCALE`; `ALL_KNOWN_FORM_RECOVERY`;
`UNIVERSAL_GRAMMAR_NEUTRALITY`; `FRONTIER_SCALE_VALIDATION`; `COMPLETE_GMI`;
any statement about `SIGMA_H15R`, `SIGMA_H06R`, `SIGMA_H05R`, `SIGMA_H08R` or
any other scope; any claim that the stored-label read recovered here is this
row's family mechanism — it is the sibling's, and the row stays open.

---

## `BS-2` — the adjacent scoped positive: on the two-evidence subpopulation the registered winner rule recovers a class with all four stages agreeing and clears F1

**Statement.** Restrict the held set to the subpopulation on which the
registered label defines a response at all — held queries whose stored table
presents at least two hypotheses (`EXT(q) >= 2`), on which the two-evidence
posterior of `FREEZE_V1.md` section 4 is defined, versus the single-completion
contexts the label registers as **ties** taking `0`. That subpopulation is
**75,618 of 97,018** held queries (0.7794). On it the full registered winner
rule recovers one class at **all four stages** — rank, held, and both
regeneration halves — with the rank stage at 2,575 errors against the
majority's 8,397, the held stage at **917 errors against the majority's 8,399**
(the registered F1 need is 4,199), regeneration at 3,347 and 3,459 against
7,387 and 7,879, and class-sharing `True`. The ladder on the subpopulation is
monotone to 917.

The recovered class on that subpopulation is `STORED_LABEL_READ_WITH_FALLBACK`.
**It is not claimed for this row.** It is recorded because the row's own
boundary implies that this subpopulation is the only place the row's posterior
is even defined, and because the boundary doctrine requires the adjacent scoped
positive to be delivered alongside the boundary rather than left implicit. It
is delivered here, labelled with the class actually recovered, and flagged
`claimed_for_this_row: false` in the receipt.

**Quantifiers.** The subpopulation only, this scope only, this ecology only.
Nothing is claimed about the full held set (where the same class wins by a
larger margin but on queries the label calls ties), and nothing is claimed for
this row's intended class on either population.

**Assumptions.** As `BS-1`, plus the subpopulation definition `EXT(q) >= 2`
evaluated against the fit store's table.

**Dependencies.** As `BS-1`. The scoped quantities are in
`REAL_RUNS/scope_SIGMA_H17R.json` under `adjacent_scoped_positive` and
re-derived by route B.

**Falsifiers.** A subpopulation restriction under which class-sharing fails; a
subpopulation at which the recovered class is not the one recorded; a scoped
F1 margin that does not hold; any reading of this result as a recovery of this
row's row.

**Strongest parents.** The sibling packages' scoped-boundary and
adjacent-positive forms; the requirement ledger's `R05` doctrine that a
boundary is reported with its neighbour rather than alone.
