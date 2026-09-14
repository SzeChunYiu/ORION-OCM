# B1 measured: what the derived families actually share, and what cannot be read off them

Date: 2026-09-14. Addresses checklist item B1 (common protocol for every derived family).
Witness: `gmi_microscope/protocol_conformance_audit.py`.
Receipt: `microscopes/results/STAGE_PROTOCOL_CONFORMANCE_V1.json`.

B1 asks every derived family to follow one protocol. The honest way to close it is not to assert
conformance but to **measure** it across the nineteen families that now exist. This document reports two
measured conformance numbers, and a negative about method that is itself a positive result: for the
remaining requirements, conformance **cannot be recovered from the artifacts as currently emitted**, and
the reason is exhibited rather than guessed.

## 1  Two measured conformance numbers

These are hand-adjudicated against the committed receipts, not inferred from a text proxy. Every row names
the receipt key that carries the finding, so a reader can check it.

| Requirement | Families conforming | How adjudicated |
|---|---|---|
| matched negative control constructed | **11 of 19** | a named receipt arm that is supposed to *fail*, reported beside one that passes |
| replication at a real regime | **0 of 19** | every receipt reports exhaustive enumeration or small closed-form ladders |

The eleven families carrying a matched control, with the key that carries it:

`B2 stateless`, `B4-neural negative_twin`, `B5 negative_twin`, `B7 negative_ecology`,
`B8 negative_twin`, `B10 twins`, `B14 relation_twin`, `B15 collapsing_control`,
`B17 iterative_structural_negative`, `B18 exploration_twin`, `B19 substrate_control`.

The eight without one — B3, B4-credit, B4-update, B6, B9, B11, B13, B16 — report comparisons or crossover
curves, but no arm that is required to fail. B4-update-law's `hypothesis_A_horizon_survives` and
`hypothesis_B_substrate_survives` record a **refuted hypothesis**, which is not the same thing as a matched
control: the hypothesis was the author's, not a designed foil.

**`0 of 19` for real-regime replication is the corpus's largest honest gap**, and it is not a surprise —
it is the corpus's own stated scope. Every result here is exact enumeration over small spaces. That is what
makes the numbers trustworthy and also what bounds them.

## 2  The other twelve requirements are not measurable from the artifacts

The natural mechanical audit is to search each receipt for vocabulary indicating the requirement was met.
That method was tried and **it fails in both directions**, which is why no conformance table for the other
twelve requirements appears in this document.

**It misses conformance that is really there.** Validated against the adjudicated answers above, the
matched-control signal `twin|negative|control|matched` scores precision 10/10 but **misses B2**, whose
control is named `stateless`. A single miss out of eleven is a usable signal; it is not a sound one, and
for requirements with no adjudicated answer there is no way to know the miss rate.

**Loosening it destroys it.** Widening the same patterns from the receipt to the witness source saturates
four of eight signals at 18–19 of 19, because every witness is a Python file that says `verify`, `cost` and
`threshold`:

| Requirement | receipt only | receipt + source |
|---|---:|---:|
| constructive realization | 5/19 | 19/19 — saturates |
| complexity coordinate | 18/19 | 19/19 — saturates |
| lifecycle/resource law | 16/19 | 19/19 — saturates |
| crossover prediction | 10/19 | 18/19 — saturates |
| obligation-sufficient state | 8/19 | 16/19 |
| lower bound proved | 8/19 | 12/19 |
| matched negative twin | 10/19 | 15/19 |
| neutral recovery | 13/19 | 16/19 |

Neither setting is a measurement. A number produced this way would say more about each author's prose than
about their derivation.

**The real-regime signal has no true positives at all.** Searching witness source for
`real-regime|real-scale|production|full-scale` fires on exactly two families, and both are substring
artefacts: B14 writes *"production system"* (a rewrite-systems term) and B15 writes *"reproduction"* (of a
receipt). Precision zero. This is the same defect class as the `"copyable)" ⊂ "not copyable)"` self-match
caught earlier in B14's own census — substring matching without a word boundary or a semantic check.

## 3  The cause, exhibited: there is no shared protocol vocabulary

Eleven families construct the same object and give it **nine different names**:

```
collapsing_control   exploration_twin   iterative_structural_negative
negative_ecology     negative_twin      relation_twin
stateless            substrate_control  twins
```

**No token is common to all nine.** That is asserted in the witness, not asserted in prose: the audit
intersects the token sets and fails if the intersection is non-empty. The regex catches eight of the nine
and misses `stateless`.

This is the whole explanation. The construct is present; the word is not; and no word covers it. Any
vocabulary proxy over this corpus is measuring naming convention, and the corpus has none.

**This is a statement about the artifacts, not about the derivations.** The eleven controls are real and
were checked individually. What is missing is a declaration.

## 4  The repair, and an honest count of who has adopted it

Conformance becomes checkable if each receipt declares it. The schema:

```json
{"protocol": {
  "version": "B1/v1",
  "obligation": "what the family must do, stated without family labels",
  "state_sufficient": "bool -- a sufficient state set was exhibited",
  "lower_bound": "int|null -- proved floor on the native coordinate",
  "upper_bound_construction": "str|null -- identifier of the exhibited realization",
  "coordinate": "str -- the native complexity coordinate",
  "resource_law": "str|null -- the lifecycle/reuse law charged",
  "negative_control": "str|null -- receipt key of the arm that must fail",
  "prediction_frozen_before_outcome": "bool",
  "neutral_search_blind_to_family": "bool",
  "replication": "list[str] -- independent re-derivations"}}
```

The witness validates every receipt against it and reports **0 of 19 families currently emit one**. The
audit refuses partial adoption: it asserts that the compliant count is either zero or all nineteen, because
a half-populated schema would invite a reader to mistake *2 of 19 emitting* for *2 of 19 conforming* —
exactly the confusion this document exists to prevent.

## 5  What this closes, and what it does not

**B1 is not closed by this audit.** Two of its requirements are now measured (11/19 and 0/19); the other
twelve are shown to be unmeasurable from the artifacts as emitted, with the cause exhibited and a repair
specified and validated.

What *is* closed is the prior question, which was unmeasured: **where does the corpus stand against its own
protocol?** The answer is that it stands better than a text proxy suggests on matched controls, exactly as
badly as feared on real-regime replication, and that the remaining requirements were never recoverable
without a declaration.

**A caveat that bears directly on a requirement this audit could not validate.** The protocol asks for a
prediction frozen before the outcome. A prediction computed earlier in the *same run* is not a
pre-registration, and most of this corpus is retrospective.

A subsequent field-by-field adjudication of 21 families settled this one: **`prediction_frozen_before_outcome`
is true for zero of them.** Four artifacts claimed otherwise in prose and none met the bar — a section
headed "FROZEN THEN MEASURED" whose `predicted` and `measured` are built in the same dict in the same loop;
a descriptor said to predict "BEFORE any machine is built" in the same file and the same run; and two more
in the same shape. Those statements have been corrected in place; the receipts were unaffected and verified
byte-identical.

**The corpus already owns the mechanism it is not using, which makes this a gap with a known fix rather than
a missing capability.** The RV-377 revival work does pre-registration properly and in two phases:
`predict_sym.py` is written and run *before* the frontier runs, emits `STAGE_DE_SYM_PREDICTION.json` as its
own committed receipt, and states at the top which inputs were admissible at freeze time; `compare_sym.py`
is a separate script that adjudicates the executed frontiers against that frozen receipt afterwards. That is
exactly what the protocol asks for. None of the 21 derivation families do it — every one states its
prediction and measures it inside a single script.

So the repair for this field is not new machinery. It is applying an existing in-house pattern: split the
prediction into its own script and its own receipt, commit that receipt, and adjudicate against it in a
second pass.

## 6  Scope

Nineteen derived families. Two requirements adjudicated by hand against committed receipts. Eight were
probed by vocabulary, of which exactly one — the matched control — also has an adjudicated answer, so it is
the only one whose miss rate is known; the unreliability of the other seven is inferred from the saturation
test and from the real-regime signal's precision of zero, not measured directly. Five of B1's fourteen
requirements were not probed at all. Everything not adjudicated is reported as not measurable rather than
as met or unmet. The
adjudication is machine-verified against the receipts — the witness fails if any named key is absent from
the receipt it is attributed to, or if a family adjudicated as having no control turns out to carry one
under a control-like name.
