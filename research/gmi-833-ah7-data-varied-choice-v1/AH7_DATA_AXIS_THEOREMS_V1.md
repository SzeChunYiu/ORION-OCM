# AH7D-1 … AH7D-3 — the data axis with everything else held fixed

Stated at the scope fixed in `FREEZE_V1.md`. Every number is reproduced by `RESULT_V1.json`
(route A), `ORACLE_RESULT_V1.json` (route B) and `TEST_RESULT_V1.json`.

---

## AH7D-1 — The same possible space, different data, a different preferred form

**Statement.** With the possibility space, the raw pricing, the requirement and the interaction
horizon all held fixed and fingerprinted, varying only the observed data moves the preferred
form.

**Quantifiers.** One space of 260 systems — four cell-free and 256 one-cell, at the AJ4 binary
budget, rebuilt here. One four-coordinate raw price
`(state_cells, table_rows, flip_transitions, unit_outputs)`, no scalarization. One requirement:
agree with every observed pair, then be non-dominated. One horizon: words of length at most
three. Twenty datasets — five target behaviours crossed with four coverages.

**Result.** The fixed-input fingerprint is identical for all twenty datasets. They produce
**7 distinct preferred sets**; **162** of the 190 dataset pairs have disjoint answers, **10** of
those sharing one target behaviour.

**The sharp case.** For the delay-by-one behaviour the preferred form changes three times with
the target held fixed and only the observed words varying: two length-one observations prefer
the constant-zero system `S000`; adding the length-two words moves it to `M051`; the length-three
words move it to `M043`. Running parity behaves the same way: `S001` to `M066` to `M064`. Two of
five behaviours move on coverage alone, which is what makes the move attributable to data and
not to the requirement.

**Assumptions.** Deterministic systems, binary alphabet, one persistent state cell at most,
exact integer comparison throughout.

**Falsifier.** If every registered dataset had yielded the same preferred set, or if answers had
differed only across target behaviours and never across coverages of one behaviour, the row
would not be earned.

**Forbidden extrapolation.** `DATA_CREATES_THE_POSSIBILITY_SPACE` — the space is prior to the
data and identical throughout, which is the whole point of the fingerprint.
`MORE_DATA_IS_ALWAYS_BETTER`, `DATA_AXIS_DOMINATES_REQUIREMENTS_OR_PRICING`,
`LEARNING_THEORY_DERIVED`.

**Dependencies.** The four fixed inputs and the twenty-dataset family frozen in `FREEZE_V1.md`
sections 1–2, and the choice map of section 3; the AJ4 organization set
(`gmi-833-aj4-process-organizations-v1`, blob pinned in `MANIFEST_V1.json`), rebuilt here as
the possibility space; AH7D-2, which makes each answer a function of the data rather than of
enumeration order; `fixed_input_fingerprint` and `per_dataset` in `RESULT_V1.json`, with all
twenty per-dataset answers matched by route B in `ORACLE_RESULT_V1.json`.

**Strongest parents.** Mitchell, *Generalization as Search* (1982), which owns a hypothesis
class fixed in advance and narrowed by consistency with observations; Gold (1967), which owns
the dependence of surviving hypotheses on how the data is presented, the coverage axis here;
Pareto (1906) for the non-domination rule; and the merged niche-repricing and
objective-provenance packages pinned in `MANIFEST_V1.json`, which own the sibling
requirements-and-pricing axis (`PARENT_LEDGER.md`).

---

## AH7D-2 — The choice map is a function of the data, and narrowing is monotone

**Statement.** Two properties the construction must have, checked rather than assumed.

**Result.** Reordering a dataset's pairs never changes the answer: **0 failures** over all
twenty datasets, three shuffles each. Extending a dataset never admits a system the shorter
dataset excluded: **0 failures** over 10 extension checks. With no observations at all the
filter admits the whole space — 260 of 260 — and the front is a single system.

**Why this matters.** Without the first property the numbers in AH7D-1 would depend on
enumeration order rather than on data. A rule that takes the first consistent member instead of
the non-dominated front differs from the true rule on **16 of 20** datasets, which is how large
that mistake would have been.

**Falsifier.** One reordering that changes an answer voids every number here.

**Assumptions.** The fixed space, pricing, requirement and horizon of AH7D-1 (`FREEZE_V1.md`
section 1). Order invariance is checked on the twenty registered datasets with three seeded
shuffles each; monotone narrowing on the ten registered extensions, from the two length-one
words to all words of length at most two and to all fourteen words, for each of the five
target behaviours. Monotone narrowing is a statement about the consistent set, not about the
non-dominated front.

**Dependencies.** The choice map of `FREEZE_V1.md` section 3 and its reordering and extension
falsifiers in section 5; the registered datasets of AH7D-1; `order_invariance_failures`,
`monotone_narrowing_checks` and `monotone_narrowing_failures` in `RESULT_V1.json`; the
hostiles `order_dependence`, `monotonicity_broken`, `empty_dataset_admits_everything` and
`first_consistent_instead_of_front` in `TEST_RESULT_V1.json`.

**Strongest parents.** Mitchell (1982), whose version space shrinks monotonically as
consistent observations are added, the parent fact checked here; Pareto (1906) for the front
that the first-consistent hostile is compared against (`PARENT_LEDGER.md`). None registered
beyond these.

---

## AH7D-3 — Two measurements that do not support the row, published anyway

**Statement.** Two things this tranche looked for and did not find, recorded so the picture is
not tidier than the evidence.

**Scalarizing the price changes nothing here.** Collapsing the four raw coordinates to their sum
moves the answer on **0 of 20** datasets, and the sum-minimal set coincides with the
non-domination front on **0 of 20** differences. The preferred set is a singleton for every
registered dataset, and that singleton is also the unique sum-minimizer. The no-scalarization
rule is kept because it is the correct general discipline, not because it bites at this scope.
Dropping a price coordinate likewise moves **0 of 20**.

**An arbitrary-label null is uninformative here.** Of 200 datasets built by assigning random
outputs to four random words, **183** are consistent with no system at all. A null built that
way would mostly compare empty answers with empty answers. The informative null draws realizable
datasets — a random member of the space, then a random sample of its own behaviour — and over
200 such pairs only **18** share an answer, across **93** distinct answers. That is the number
that says the data axis is informative rather than an artefact.

**Falsifier.** If the realizable null had produced one answer almost always, the moves in
AH7D-1 would be a property of the chosen datasets rather than of the data axis.

**Assumptions.** The twenty registered datasets, the fixed space and the four-coordinate raw
price of AH7D-1. Scalarizing replaces the price by the sum of its four coordinates, and
dropping a coordinate uses the three-coordinate price without `unit_outputs`; the nulls are
200 seeded draws each, of four random words with random outputs and of realizable four-word
datasets sampled from two random members' own behaviour. Both findings hold at this scope
only.

**Dependencies.** AH7D-1's per-dataset answers, each a singleton; the no-scalarization
discipline of `FREEZE_V1.md` sections 1 and 3 and the randomized-family falsifier of section
5; `datasets_whose_answer_moves_under_scalarization`,
`datasets_where_the_sum_rule_differs_from_non_domination`,
`datasets_whose_answer_moves_under_coarser_pricing` and the `null_*` counts in
`RESULT_V1.json`; the hostile `arbitrary_label_null` in `TEST_RESULT_V1.json`.

**Strongest parents.** Pareto (1906), which owns non-domination over incommensurable
quantities and hence the refusal to scalarize; Mitchell (1982), under whose version space an
unrealizable dataset leaves no consistent member (`PARENT_LEDGER.md`). None registered beyond
these.
