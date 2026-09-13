# Hostile counterexamples to stronger RSI inferences

These are theory/protocol counterexamples.  They prevent common invalid promotions.

## C1 — Repetition is not recursion

A fixed optimizer `D0` repeatedly edits prompts/code/weights and performance rises.  The task solver changes; `D0` never does.

**Defeats:** “many rounds of self-improvement ⇒ R3.”  Classification: at most R2.

## C2 — Current champion can be a bad ancestor

Machine `A` scores higher than `B` now, while descendants generated from `B` dominate descendants generated from `A` at matched budget.

**Defeats:** “current benchmark performance is a theorem-level proxy for self-improvement potential.”

## C3 — Valid stepping stone can look worse now

`MUTABLE_D` in the committed synthetic assay moves `0.50 → 0.47` on frozen-shadow quality while changing `D0 → D1`, then descendants reach `0.69` and `0.82`.  The matched frozen-D arm tops out at `0.63`.

**Defeats:** “every admitted developmental step must monotonically improve current task score.”

## C4 — Extra compute masquerades as RSI

A mutable-D arm receives twice the compute and produces better descendants than the frozen-D arm.

**Defeats:** “better descendant ⇒ D mutation caused the gain.”  The causal comparison is invalid until resources match.

## C5 — Judge tampering

The agent edits its evaluator proxy and reported score jumps `0.50 → 0.97`, while protected shadow quality stays approximately flat.

**Defeats:** “self-certified score improvement ⇒ self-improvement.”

## C6 — Cosmetic modifier edit

A file/function labelled `optimizer` changes but descendants never execute the changed code.

**Defeats:** “diff touching meta code ⇒ recursive self-improvement.”  R3 needs an executed causal path.

## C7 — Heredity by label only

Generation `g1` records a D change, but `g2` silently reloads D0 from a clean image.

**Defeats:** “ancestor changed D ⇒ lineage inherited recursive improvement.”  R4 requires persisted D identity/state.

## C8 — Finite transfer is not open-endedness

A self-modification policy transfers across ten or one hundred registered domains and then saturates.

**Defeats:** “multi-domain transfer ⇒ open-ended RSI.”  It is evidence for scoped transfer only.

## C9 — RSI is not acceleration

A lineage has positive matched meta-gain while quality increments diminish or oscillate.

**Defeats:** `R3 ⇒ increasing improvement rate`.  `model.is_strictly_accelerating` tests the stronger condition separately.

## C10 — Constitution collapse

The candidate changes the rule that judges whether its own change is admissible and then approves itself.

**Defeats:** “self-authorization is evidence of successful governed RSI.”  It is outside this bridge unless another external governance layer independently authorizes that constitutional revision.
