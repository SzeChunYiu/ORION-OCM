# Registered Section H obstruction theorems V1

All statements below use the exact grammar, ecology, cost, and 43-row registry
frozen in commit `d2cbd897890e67a2866552b4df50b7583a2f3ceb`.

## Objects

Let `X={0,1}^8`.  A grammar expression has leaves
`0,1,x0,x1,x2,x3`, operators `NOT`, `XOR`, and `AND`, and node-count
cost `c`.  `G_B` is the semantic image of expressions with `c<=B`.  The
protected interface is all 256 members of `X`; the observation ecology `O`
contains the eight points on which `x0,x1,x2` vary and `x3..x7=0`.  Complete
search keeps every `g in G_3` equal to the target on `O`, then keeps every
minimum-cost fit.  It does not break ties.

Family names never occur in the grammar or search.  The registry maps each
Issue #833 row to a finite operational hallmark target only after the common
grammar, ecology, cost, and search have been fixed.

That mapping is an authored post-hoc evaluation prior.  Its per-row
external-semantics rationales are frozen in `FROZEN_FAMILY_REGISTRY_V1.json`.
The machine derives a disposition only after accepting those authored
mappings; it does not derive the meanings of the historical family names.

## H-EXP — expressivity obstruction

Every `g` in the unbounded grammar is invariant under flipping any of
`x4,x5,x6,x7`.

**Proof.** Each leaf is invariant in those coordinates.  Pointwise `NOT`,
`XOR`, and `AND` preserve invariance.  Structural induction over expression
trees proves the claim at every finite cost.  Each unavailable-channel target
`xi`, `i in {4,5,6,7}`, changes under its own coordinate flip, hence is outside
the grammar image at every budget.  The checker additionally verifies the
invariant for all 96 semantic classes first appearing through cost five; that
enumeration is a witness, not the analytic proof. ∎

## H-RES — resource obstruction

The minimum grammar cost of both `x0 XOR x1 XOR x2` and
`x0 AND x1 AND x2` is exactly five.  Therefore both are absent from `G_3` but
expressible in the same grammar.

**Proof.** The semantic dynamic programme enumerates all minimum-cost semantic
classes.  Its completeness is inductive: any cost-`c` tree consists of one
operator and subtrees whose costs sum to `c-1`; replacing a non-minimum subtree
by its minimum extensionally equal representative preserves the root
denotation and does not increase cost.  The two targets are absent from the
complete layers 1–4.  The displayed expressions are cost-five witnesses.
A source-separated tuple-table closure independently gives layer sizes
`6,4,12,24,50` and the same minima. ∎

## H-ID — identifiability obstruction

The protected semantics of target `x3` is not identified by `O` under complete
minimum-cost search.

**Proof.** `x3=0` on every point in `O`; constant zero therefore has the same
observation vector.  Both are leaves of cost one and disagree whenever `x3=1`.
The exact candidate census shows these are the two distinct minimum-cost
protected truth tables consistent with the target observations.  With no
registered tie-breaker, the query image is not a singleton. ∎

## H-POS — positive controls

Complete search uniquely recovers `x0`, `NOT x0`, `x0 XOR x1`, and
`x0 AND x1` at respective minimum costs `1,2,3,3`.  All eight combinations of
the excited coordinates occur in `O`; complete semantic enumeration finds no
equal-cost protected competitor.

## H-CENSUS — complete registered quantification

The frozen registry contains each of the 43 named Section H family rows exactly
once.  Applying H-EXP, H-RES, H-ID, or H-POS to its frozen hallmark map yields:

- 21 expressivity obstructions;
- 9 resource obstructions;
- 6 identifiability obstructions; and
- 7 recovered positive controls.

Thus 36 of 43 registered hallmark contracts cannot be recovered in the frozen
scope, with a typed theorem witness for every failure.  This is not a theorem
that 36 historical families are universally unrecoverable.  A positive control
recovers only its finite hallmark, never a full named family.

## H-REMINT — presentation invariance

Reversing the candidate list and independently hash-ordering/reminting every
candidate identifier preserves the semantic quotient, minimum costs, fit sets,
all target dispositions, and the 43-row census.  This covers surface identifier
and enumeration-order changes, not arbitrary grammar changes.

## H-SCOPE — obstruction classes are not monotone across scope changes

Three matched hostiles prevent promotion of the census into a universal
claim.  Raising the node budget from three to five uniquely recovers the
triple-parity target, so its resource obstruction disappears.  Expanding the
ecology to vary `x3` uniquely identifies the formerly unexcited-context target.
Adding `x4` as a legal leaf and varying it in the ecology uniquely recovers the
history/state target at cost one.  Therefore grammar, ecology, and budget are
essential theorem premises; enlarging any of them can change the obstruction
class.

## Claim ceiling

`REGISTERED_43_FAMILY_HALLMARK_CENSUS_COMPLETE__UNIVERSAL_NONRECOVERABILITY_FORBIDDEN`

No named family row satisfies the Section H ten-gate rule here.  In particular,
there is no real-scale test, so all 43 family boxes must remain open.
