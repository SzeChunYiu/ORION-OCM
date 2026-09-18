# SUPPLEMENT 1 — post-freeze deviations

`FREEZE_V1.md` section 11 binds this tranche to record every decision taken
AFTER seeing a result that affects a claim, and to **measure** its exposure
rather than assert it. This file is that record. The direct parent's standard —
`D1_SENSITIVITY_V1.json`, 1 changed field of 774 — is adopted unchanged.

Eight deviations are recorded. Two carry claims and their exposure is measured
by re-running with the deviation forced off and diffing every leaf field of the
regenerated receipt. Six are conventions or scope refinements whose dependent
claims are named exactly.

---

## D1 — the ascent evaluation charge

**What changed.** The charge for evaluating candidates during a breadth ascent
was first implemented as `breadth * Tsteps * max_degree` units of `p_test`, i.e.
one unit per candidate. It is now
`breadth * (Tsteps + 1) * (max_degree + 1) * T`: each carried member, at each
step, evaluates itself and its neighbours, and **one candidate evaluation costs
`T` elementary evaluations**, because `FREEZE_V1.md` section 2.1 declares
`p_test` to buy "one elementary evaluation of **one candidate on one
instance**".

**Shape.** The `#976` `POST_HOC_SUSPECT` shape: the correction was found by
inspecting the first run, in which the breadth law won every cell on every
environment. The justification — conformity to a price semantics frozen before
any run — does not exempt it from disclosure.

**Dependent results.** Every charge involving the ascent branch, hence the
`SIG-P` and `NULL-0` coefficient vectors, `pistar*`'s comparator, and every cell
count.

**Deviation-free fallback.** The per-candidate charge; reachable by running the
executor with `REGIMES_D1_OFF=1`.

**Exposure: MEASURED.** See `D1_SENSITIVITY_V1.json` for the leaf-field diff
between the shipped receipt and the deviation-free re-run, reported as
changed/total in the parent's format.

---

## D4 — the non-redundancy filter on the search space (UL-9)

**What changed.** The blind structural search ranges over the **non-redundant**
laws of the registered grammar rather than all of them. A law is redundant when
lowering one structural coordinate to the next registered level leaves the
emitted predictor identical at every registered input.

**Why.** The first census found the blind argmin was a law carrying a wasted
coordinate — a constant predictor paying a mutation charge, or a cross-episode
slot that changed no step. Such a law is strictly dominated at every positive
price by a behaviourally identical cheaper law, so including it in a search over
*update laws* is a modelling error, not a finding.

**Shape.** Adopted after seeing the first census. The justification is that this
is the general form of the freeze's own wastefulness lemma (section 4.2), which
was registered before any run and is claimed there as unconditional.

**Dependent results.** The neutral-recovery row, and the derived `vacuous`
verdicts reported in section 4 of the theorem note. **It does NOT carry the
seven converses**: UL-2's converse is checked directly by comparing charges at
every registered price; UL-6's by comparing every breadth tuple against its
breadth-1 counterpart; UL-7's pointwise over every registered input; UL-8's by
comparing charges at every registered price. All four are computed without the
filter and are invariant to it.

**Exposure.** Confined to the recovery census and the vacuity labels, both of
which are reported with their counts in the receipt.

---

## D5 — the ascent as the fallback branch

**What changed.** The precedence that determines a tuple's emitted predictor now
places the breadth ascent as the fallback when no weight slot, no store and no
construction is registered — so `breadth = 1` is the **single incumbent**, as
`FREEZE_V1.md` section 7 describes the coordinate ("candidates carried in
parallel"), rather than a constant predictor.

**Why.** Under the first precedence the breadth-1 counterpart of a breadth law
was the constant predictor, which made the unimodal converse untestable inside
the tuple space: the natural comparator did not exist.

**Dependent results.** The `NULL-0` comparator, the `SIG-P` vacuity verdict on
the unimodal environments, and the `HO-P3` breadth clause.

**Shape.** Adopted after the first census, for conformity with the frozen
grammar's own description of the coordinate.

---

## D2 — the `HO-P1` scoring convention

**What changed.** `HO-P1` is scored with the explicit convention that a closed
form at or below zero predicts **no crossover inside the positive price cone**,
which the bisection reports as `None`. Without the convention the two sides use
different conventions for the same fact and disagree trivially.

**Shape.** The convention was written after `HO-P1` first read MISS. A held-out
prediction whose scoring rule was adjusted post-outcome is **weaker evidence than
one that hit as stated**, and it is reported that way rather than as a clean 4/4.

---

## D3 — the `HO-P3` scoring convention

**What changed.** `HO-P3` is evaluated on the two UNCONDITIONAL claims
themselves — "the weighting law is strictly dearer than the point summary at
every registered price when `alpha_gain <= 0`" and "every breadth-`>=2` tuple is
strictly dearer than its breadth-1 counterpart when the landscape is unimodal" —
rather than on cell counts. The cell-count proxy was both weaker and unsound: a
signature can have zero cells for reasons unrelated to its converse.

**Shape.** Written after `HO-P3` first read MISS under the proxy. The same
weaker-evidence caveat as D2 applies, although the replacement is strictly
closer to the claim the freeze states.

---

## D6 — the anchored price census

**What changed.** An anchored price set was ADDED alongside the frozen uniform
grid: for every pair of registered representatives and every price coordinate,
the exact crossover in that coordinate, probed at half it, at it, and at twice
it.

**Why.** The frozen uniform grid lies entirely in the resource-dominated regime —
at the registered query-set sizes the loss differences are single digits while
the resource differences run to hundreds, and the frozen `lam` levels cannot
close the gap — so it exercises no crossover.

**Shape.** The construction is geometric: it is fixed by the crossover surfaces
themselves, not chosen by looking at an outcome, and it is the direct parent's
own IL-2/IL-3 anchored-probe design (`rho*/2`, `rho*`, `2 rho*`) lifted to this
space. **The frozen grid is NOT replaced**: its cell counts are reported in the
receipt, and the theorem note states plainly that they are not load-bearing.

---

## D7 — splitting the two comparators

**What changed.** The single-best point summary (`BASE-0`) and the single
incumbent (`NULL-0`) are distinct labelled comparators. They were initially
collapsed into one label, which made the first recovery census uninterpretable —
two laws with very different charges reported under one name.

**Dependent results.** The readability of the recovery census; no threshold
moves.

---

## D8 — `select_v2`

**What changed.** A second selector is delivered that ranks the charge-minimal
**non-redundant** law of each signature class rather than the canonical
representative.

**Why.** `HO-P2` MISSED as stated. The attribution is to one stage: the frozen
selector ranks canonical representatives, a canonical representative can itself
be redundant, and the blind search ranges only over non-redundant laws, so it can
never return that law. By UL-9, ranking a redundant representative is ranking a
law that is dominated at every positive price, so `select_v2` is strictly more
sound, not merely better-scoring.

**Shape.** A post-freeze repair whose necessity was exposed by a held-out miss —
which is exactly what a held-out test is for. **The frozen selector's own numbers
are reported unchanged beside it**, `HO-P2`'s verdict remains MISS as stated, and
the repair's agreement is reported separately under
`heldout.HO_P2.repair_select_v2`. The row `Build a prospective learning-law
selector` is claimed on the FROZEN selector; `select_v2` is disclosed as the
revival, not substituted for it.

---

## What is NOT a deviation

- The claim ceiling, the forbidden promotions, the eleven rows in scope, the
  price vector and its loss commensuration, the noise rate `eps = 1/4`, the
  production-space size bound `KMAX = 3`, the registered tie rules, the selector
  decision table, the neutral grammar's coordinates and level sets, the twelve
  environments' construction rules, the 46-ratio pairwise grid and the `3^7`
  joint grid are all exactly as frozen.
- No threshold formula was changed after a run. `beta*`, `chi*`, `pistar*`,
  `tau*` and `s*` are the forms frozen in `FREEZE_V1.md` section 4, and `disc*`
  is obtained by solving the frozen `SIG-R` inequality for a different one of its
  own variables.
- `Test on realistic learning systems` was pre-committed as expected-to-remain-
  open and remains open. That is not a deviation; it is the freeze's own
  abstention rule being honoured.
