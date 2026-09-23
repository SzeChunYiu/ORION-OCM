# Named results — gmi-833-h-real-scale-diffusion-refinement-v1

Every result below is stated at one registered scope and at no other. No result
here is composed with any certificate of any parent package; `FGS-2` forbids it
and `CROSS_SCOPE_GATE_COMPOSITION` is in `forbidden_promotions`.

Scope, from `FREEZE_V1.md` sections 3 and 4 and
`FREEZE_V1_SLICE_ADDENDUM_H33_V1.md`: `SIGMA_H33R` — row
`Diffusion/iterative-refinement systems.`; grammar `G_DR`; ecology `F33`, the
stochastic-refinement table over the descriptor-closure contexts of the
sha256-bound source `D = /usr/share/dict/american-english` (104,334 tokens,
digest `9e66281f7e51`), 671,860 context positions, 168,834 distinct contexts,
presented under the registered Knuth permutation
`key(i) = (i * 2654435761) mod 2**32`; `n_fit` 587,877, `n_held` 83,983; query
set 38,103 held tasks.

---

## `DR-1` — the family-blind winner rule recovers a refinement step index at `SIGMA_H33R`, and the registered single-draw and cardinality families are separated from it by measurement

**Statement.** The registered configuring rule of `FREEZE_V1.md` section 4
selects the labelling configuration `(probe key from the descriptor,
corruption 1)` with `T* = 25`, at a full-source label rate of
`84,340 / 168,834` — the most even split attainable among the four registered
configurations, measured on the source-derived distribution alone with no
slice, no store and no readout evaluated. On the held query set the family-blind
winner rule (fewest exact decision errors on the rank-score set, ties by charged
cost then readout name; the readout language `R` of 51 arms closed before any
outcome, built as the registered base ladder unioned with the registered `T*`)
selects **`REFINE<=25`** at the rank stage (6,057 errors vs the fit-majority
rule's 11,218), at the held stage (**1,479 errors vs 5,197**, prototype
agreement 36,624 / 38,103), and at both regeneration halves (`REFINE<=25` at
15,409 and 18,069 against 18,574 and 18,638). Its post-hoc structural class is
`REFINEMENT_INDEX`.

The registered sibling channel is rejected on the same held set: the best
**single-draw** arm is `DRAW0` at **30,557** errors — the refinement family
beats it by a factor of **20.7** — and the best **cardinality** arm is `CNT>=1`
at 5,197, beaten by a factor of **3.5**. Registered falsifier 3 of
`FREEZE_V1.md` section 9 therefore does not fire, so the recovered class is this
row's refinement channel rather than the sibling's single-draw source channel.

The **admitted storable-label arm `MEM_FALLBACK` loses**: it makes the same
1,479 errors as the winner but loses the registered tie-break on charged cost
(2 units against 1), and the winner rule reports `REFINE<=25`, not
`MEM_FALLBACK`. It is admitted, judged by the data, reported at every stage, and
never exempted.

The registered **global** design null fires and is matched: reassigning each
stored unit's candidate character from a different context's unit multiset
degrades the refinement arm from 1,479 to **6,678** (**4.52x**, past the
registered 3x bar) while leaving the cardinality arm **bit-identical** at 5,197,
and moving the single-draw arm only 30,557 → 27,553. The three families are
therefore separated mechanically by one registered reassignment, not by their
labels. The label-shuffle null makes **10,043** errors, strictly more than the
majority rule's 5,197. The store ladder of the winning readout is monotone
non-increasing in the stored budget: `{1000: 32173, 5000: 29133, 10000: 26392,
20000: 23135, 50000: 17661, 100000: 13478, 200000: 9064, 587877: 1479}`. The
scan-vs-vocabulary-index crossover is `m* = 57,567` (the smallest `m` with
`2m > V + 27`, `V` = 115,105 distinct stored contexts, index cost 115,132). The
matched **source-order presentation control fires**: under the un-permuted
contiguous presentation the registered arm makes 4,657 errors against the
majority's 5,197 — it does not clear the F1 margin of 2,598 — so the registered
presentation lever is load-bearing. Every quantity is an exact integer decision
count, committed in `REAL_RUNS/scope_SIGMA_H33R.json`, replayed exactly by route
A and re-derived by route B (`independent_oracle_dr_v1.py`, which imports none
of the primary executor).

**Provenance of this paragraph.** An earlier revision of this package shipped
`MEM_FALLBACK` with only its stored branch, which made it the same predicate as
`REFINE<=T*` under a second name; that revision was merged to `main` as
`3cbf841c` and is corrected by the follow-up commit on this branch, with no
change to any claimed number (the receipt differs by the single added key
`query_fallback_label`). The guard that prevents the class is
`ci_gates_v1.py alias-guard`, which evaluates every registered arm over a grid
that sweeps every walk value `0..256` and every registered threshold of every
family, and fails on any pair of distinct names that agree everywhere; one
declared redundancy, `CARD>=1` `≡` `REFINE<=256`, rests on the registered step
cap and is asserted rather than tolerated.

**On the tie, disclosed and checked.** At every stage the minimum-error set
contains exactly two arms, `REFINE<=25` and `MEM_FALLBACK`, separated by the
registered charged-cost tie-break (`1` against `2`). They are **distinct
readouts with distinct code branches**, not one predicate under two names — the
defect the sibling row H32 hit. The slice addendum registers `MEM_FALLBACK` as
*"if the descriptor `q` is stored, read out the stored predicate of `q` … else
the fit majority"*: its stored branch reads the registered label form, and its
**fallback branch reads the fit-majority constant** on a query whose descriptor
is not stored. `REFINE<=k` has no fallback: it reads `0` there. Measured on the
committed tallies and asserted in
`test_real_scale_diffusion_refinement_v1.py::Scopes::test_the_tied_arms_are_distinct_readouts`:
**every one of the 38,103 held queries has a stored descriptor**, so the
fallback branch is never taken on the held set and the two predictions coincide
on all of them — the tie is decided purely by charged cost. The branches do
differ, and the test exercises the difference on synthetic rows where the
descriptor is unstored: the fallback reads the registered constant while
`REFINE` reads `0`. The difference between the two arms is therefore real but
**never exercised by this held set**, which is the honest form of the claim; the
597 held queries whose store covers no candidate are a different case, on which
both arms read `0` (the walk is capped), 363 of the 597 being majority errors. The
adjacent ladder rung `REFINE<=24` is not the fallback either — it differs from
it on 242 held queries — so the winner is the registered label threshold itself.

**Quantifiers.** This scope only, this ecology only, this source only, this
label only. Nothing is claimed about diffusion, denoising or iterative
refinement on any other ecology, source, presentation, grammar or label, and
nothing is claimed about the sibling rows at `SIGMA_H31R`, `SIGMA_H19R`,
`SIGMA_H35R` or `SIGMA_H05R`.

**Assumptions.** The `D` digest holds at run time (`9e66281f7e51`); the
registered Knuth alphabet order and its successor; the registered ecology `F33`
with the descriptor closure over prefixes of length ≥ 2 and the registered
context cut of length ≥ 3; the registered configuring rule and the `T*` it
selects, measured on the full source before any fit; the arithmetic 7:1 slice
and the `rank_fit`/`rank_score`/`fit_lo`/`fit_hi` sub-splits; the registered
readout language `R` and the ladder meta-rule (the ladder must contain the
registered `T*`); the registered null constructions and seeds; the charged-cost
model (`2m` vs `V + 27`).

**Dependencies.** `grammar_dr_v1.py` for the readout language, the classifier
and the presentation key; `FREEZE_V1.md` sections 3 to 12;
`FREEZE_V1_SLICE_ADDENDUM_H33_V1.md`. It depends on no artifact of any parent
package. Receipt: `REAL_RUNS/scope_SIGMA_H33R.json`, `RESULT_V1.json` row
`H33`, `ORACLE_RESULT_V1.json`.

**Falsifiers.** A registered readout that beats `REFINE<=25` at the held stage
under the registered winner rule; a registered single-draw arm at or below the
refinement family's held error (which would make the recovered class the
sibling's and this result void); a design null that leaves the refinement family
within the 3x bar, or one under which a cardinality arm moves; a ladder that is
not monotone; a source-order presentation at which the registered arm clears
F1; any cross-scope gate composition or foreign `sigma`; disagreement between
routes A and B. None of the registered falsifiers fired on the delivered
receipt.

**Strongest parents.** For the machinery: the sibling real-scale packages
(`gmi-833-h-real-scale-decision-trees-v1`,
`gmi-833-h-real-scale-particle-population-v1`,
`gmi-833-h-real-scale-belief-state-v1`) supply the freeze-first custody chain,
the closed readout-language architecture, the family-blind winner rule, the
symmetric half-split regeneration and the matched-presentation control form —
form only, no number. For the mechanism: Boltzmann (1872) and Metropolis et al.
(1953) for stochastic relaxation by successive perturbation; Sohl-Dickstein et
al. (2015), Ho et al. (2020) and Song et al. (2021) for the step-indexed
refinement view; Knuth (1997) for the presentation lever and the registered
alphabet order; Salton, Wong and Yang (1975) for the descriptor vocabulary.
None of it is claimed novel here.

**Forbidden extrapolations.** `CROSS_SCOPE_GATE_COMPOSITION`;
`CONTRACT_IDENTITY_IMPLIES_FAMILY_IDENTITY` — sharing the registry's
`STOCHASTIC_SOURCE_CHANNEL` contract with `H19`, `H31` and `H35` implies no
identity of family, ecology or class;
`REGISTERED_CONTROL_SUBSTITUTION`; `POST_HOC_FALSIFIER_REPLACEMENT`;
`ECOLOGY_ITERATION_UNTIL_POSITIVE`; `ROW_CLOSED_BY_MEASUREMENT`;
`BOUNDARY_IS_A_RECOVERY`; `RAW_COUNT_ARM_IS_THE_FAMILY`;
`REAL_SCALE_VALIDATION_COMPLETE`; `SECTION_H_COMPLETE`;
`INDEPENDENT_TEAM_REPLICATION`; `M5`; `EV4`; `EV5`;
`FINITE_EVIDENCE_IMPLIES_REAL_SCALE`; `ALL_KNOWN_FORM_RECOVERY`;
`UNIVERSAL_GRAMMAR_NEUTRALITY`; `FRONTIER_SCALE_VALIDATION`; `COMPLETE_GMI`;
any statement about any other scope; and any use of the registry's
`EXPRESSIVITY_OBSTRUCTION` prediction for this contract as evidence in either
direction.

---

## `DR-2` — the registry contract is a steer, and the row's arity is registered from the contract while the winner rule stays family-blind

**Statement.** `FROZEN_FAMILY_REGISTRY_V1.json` records for `H33` the contract
`STOCHASTIC_SOURCE_CHANNEL` with hallmark "response dependence on a registered
stochastic-source probe", and its `target_contracts` entry gives that contract
the expression `x5` — a source address, not a boolean. The merged sibling
`gmi-833-h-real-scale-decision-trees-v1` registers the registry's contract as a
**steer** in as many words, and its own winner is a two-test conjunction rather
than the registry expression verbatim. Read as a binding expression, `x5`
admits exactly one family-blind winner rule — the nearest probe to the source
value — which is nearest-exemplar retrieval, i.e. the row `SIGMA_H05R` already
owns; the sibling `gmi-833-h-real-scale-particle-population-v1` records that
same collapse on the record and re-registers its contract's arity accordingly.
This package does the same: it registers the row's protected interface as a
**refinement step index** over a registered sequence of stochastic
perturbations, which is what distinguishes this row from
`Latent-variable generative systems.`'s single sampled source, and it registers
the contract and its hallmark as a steer with that citation. The winner rule
then stays family-blind: `DR-1` selects among the closed language by measured
error, and the refinement class wins by data.

**Quantifiers.** The registry reading only. No claim is made about `H19`,
`H31` or `H35` beyond the recorded fact that the registry assigns them the same
contract; nothing about their ecologies, classes or outcomes is imported,
mirrored or predicted here.

**Assumptions.** The registry file is the one on `main` at the pinned
`source_main`; its `families` entry for `H33` and its `target_contracts` entry
for `STOCHASTIC_SOURCE_CHANNEL` are read as written; the merged sibling
packages' recorded readings of their own contracts are as cited.

**Dependencies.** `FROZEN_FAMILY_REGISTRY_V1.json`;
`gmi-833-h-real-scale-decision-trees-v1/FREEZE_V1.md` section 3 for the steer
reading; `gmi-833-h-real-scale-particle-population-v1/CORE.md` for the recorded
`x5` collapse; `FREEZE_V1.md` section 12 of this package.

**Falsifiers.** A registry revision that binds the contract's expression as a
label arity rather than a steer; a sibling package recovering this row's class
without a step-index readout; a measured result in which the refinement family
is not separated from the single-draw family (which would make this statement
vacuous by making the row indistinguishable from `H31`).

**Strongest parents.** The two sibling packages cited above for the steer
reading and for the recorded `x5` arity problem; the requirement ledger's
`HRL-1` for the scope rule that keeps the steer from becoming a certificate.
