# A conditional proof-space comparison

This elementary observation narrows the experiment. It is not an OCM novelty
claim, a measured result or a statement about current implementation correctness.

## Statement

Let an action have one conclusion and a finite ordered list of premises. Lists
retain repeated premises and may be empty. A derivation is either a permitted
task-hypothesis leaf, costing zero, or an action node with one derivation child per
ordered premise. An action costs one plus the sum of its child costs; a zero-premise
action therefore costs one. All derivations are finite. Shared subproofs count
once per occurrence in this tree objective.

Let R be the available ordinary-plus-recipe actions and L the available
ordinary-plus-derived-theorem actions, with identical initial hypotheses.
Suppose every action in R has an action in L with exactly the same conclusion,
ordered premise list and unit application cost. The correspondence need not be
injective. It must hold for the current task, substitutions, scope and eligibility.

Then every R derivation has an L derivation of the same conclusion and tree cost.
Consequently, for each goal and every finite tree-cost bound, existence of an
R proof implies existence of an L proof within that bound. The minimum L tree
cost is at most the minimum R tree cost, taking an unreachable goal's cost as
infinity. If the correspondence also exists in the opposite direction, the two
minimum costs and bounded proof-existence sets are equal.

## Proof

Induct on a finite R derivation tree. A hypothesis leaf is also an L hypothesis
leaf, with the same cost. For an action node, replace its action by the stated
L action and replace each ordered child by its inductively obtained L derivation.
The premise list and conclusion still match. The cost remains one plus the same
ordered sum, including each repeated child occurrence. This proves preservation
of each finite derivation; the minimum-cost and reverse-correspondence conclusions
follow. A zero-premise action has no child obligations and retains cost one.
Cycles in the action graph do not affect induction on a finite proof tree.

## Conditions the software must establish

An admitted learned theorem is a plausible way to supply this correspondence,
but a proved sequent alone does not establish the software conditions. Check:

- The derived theorem is actually available in the parent search catalogue and
  its proof is checked under the exact successor native environment.
- Every recipe action's substitution, ordered premise ports and conclusion has
  a corresponding parent action, with identical current use permissions.
- Grammar, syntax-proof availability, DV rules and finite-bank restrictions admit
  those instances. No compiler omission silently removes the required action.
- Both proof objectives use the stated tree cost. A shared-DAG objective, weighted
  application costs or bounded expanded-proof length needs a separate comparison.

Broader legal parent substitutions can add actions beyond the correspondence.
They cannot worsen this mathematical minimum; materializing and searching those
actions may nevertheless cost more in an actual implementation.

## What this removes, and what remains

Once the correspondence is established, another task run is not needed to prove
this conditional tree-cost dominance. Use actual runs to test correspondence,
implementation behavior and costs. Different tie order, compilation, time/memory
limits, pruning and proof-emission bounds can change observed outcomes; this result
does not promise equal solver outputs under an equal computation allowance.

There is also no equality claim for emitted proof strings, native checker work,
storage, acquisition, revision or full lifetime cost. Those are meaningful targets
for the empirical comparison. If a recipe helps because of a narrower action set,
evaluate that selection mechanism in the equally equipped conventional host.

Focus the research on which explicit representation and policy make useful
verified cognition cheaper over time, under the stated obligations.
