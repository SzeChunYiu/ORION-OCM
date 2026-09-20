# Kernel scope: resource thresholds V10

Read [CORE.md](CORE.md) first; [THEORY_V10.md](THEORY_V10.md)
contains the mathematical argument and [PARENTS_V10.json](PARENTS_V10.json)
records prior work. This file binds the scope of [ResourceV10.lean](ResourceV10.lean).

## Actual model

The Lean development imports only `Std`. It quantifies over arbitrary state,
action, observation and event types. It does not require finite state spaces,
decidable equality on those types, or an effective transition table.

A machine has an observation function and a mathematically total function
`next : S → A → Option (E × Nat × S)`. Here `none` means an absent
transition. It does not represent a proof that a computation diverges.

A finite response is one of:

- `done observation`: the supplied finite input word has been exhausted;
- `illegal observation`: the next requested transition is absent or unaffordable;
- `step observation event cost tail`: an admitted transition followed by its response.

Thus the current observation, each admitted event, and its exact natural-number
cost are visible. The nested representation contains the successor observation
at the head of its tail. It corresponds to the executable flattened observation,
event/cost, successor-observation trace, with the same first-failure stopping rule.
This correspondence is a representation explanation, not a proved Python refinement.

`run` follows actual transitions without resource guards. `runBudget` admits a
transition exactly when its cost is at most the residual resource, subtracts that
cost, and recurses on the remaining input word. Both stop at the first absent
transition; the latter also stops at the first unaffordable transition. These
failures deliberately share one `illegal` constructor.

`prune` is an independently defined operation on traces. It applies the same
guards to visible costs, without inspecting a machine or its hidden state.
Zero-cost edges and cycles are permitted: recursion terminates on the finite
input word or trace. Infinite input words and internal silent computation are
outside this development. Observation and affordability checks incur no extra
charge in this declared model.

## Theorems checked by Lean

- `prune_contracts`: if `lo ≤ hi`, pruning at `hi` and then at `lo`
  equals pruning the original trace at `lo`.
- `actual_budget_is_pruned`: the actual guarded machine response is exactly
  the pruning of its actual unguarded response.
- `actual_response_contracts`: pruning an actual response at a larger initial
  resource yields the actual response at the smaller initial resource.
- `pointwise_equal_contracts` and `budget_equivalence_nested`: equality of
  responses for a word, or all finite words, at the larger resource implies
  equality at the smaller resource.
- `same_witness_persists` and `distinction_upward`: a distinguishing word
  remains distinguishing at every larger resource.
- `equivalence_trans`: equality of all finite-word responses is transitive.
- `bounded_threshold_exists`: any distinguishing natural-number resource
  has a least distinguishing resource at or below it.
- `threshold_exists` and `threshold_unique`: every state pair has exactly
  one threshold in `Option Nat`, where `none` denotes infinity.
- `diagonal_threshold` and `threshold_symmetric`: self-thresholds are
  infinite and thresholds are symmetric.
- `first_distinction_cutoff` and `threshold_cutoff`: states are equivalent
  at resource `b` exactly when `b` is strictly below their threshold.
- `threshold_anti_triangle`: for actual thresholds of three state pairs,
  every finite `b` strictly below both leg thresholds is strictly below the
  third threshold. This is the extended anti-triangle inequality stated by
  strict finite cuts; it includes infinite thresholds and zero thresholds.

These theorems do not assume nesting or witness persistence as inputs.
They derive both from actual machine execution. The threshold theorems use
classical logic for existence when no effective search is supplied; they do
not provide an executable threshold finder for arbitrary infinite machines.
The `Threshold` relation used in the final theorem is proved inhabited and
unique, rather than being an unchecked certificate predicate.

## Results outside this kernel development

The following are paper arguments and/or executable checks, not Lean theorems
in this file: reverse-Dijkstra correctness and witness extraction; the sharp
finite `(n−k)Cmax` bound; the characterization for action-conditioned
cost-recoverable event encodings; the real-valued transform `2^(−D)`;
finite partition and fixed-length code-count bounds; and equivalence between
an infinite threshold and equality of unguarded finite-word responses.
The last statement uses the fact that any particular finite trace has finite
total natural-number cost.

The kernel model exposes exact cost directly. It does not mechanize the more
general encoding theorem merely because cost can be recovered in the paper model.
It does not verify the Python implementation, finite fixtures, certificate
validator, or their correspondence to these definitions. Their independent
checks have their own scope.

These results concern symmetric resource needed to distinguish responses.
They do not establish the directed transformation burden of R5, empirical
resource scaling, a physical cost calibration, prior-independent objective
selection, or derivation of every machine-intelligence architecture.

## Reproduce

On laptop billy, from the repository root:

```sh
/home/billy/.elan/bin/lean +leanprover/lean4:v4.19.0 \
  -DwarningAsError=true \
  research/gmi-1068-resource-threshold-v10/ResourceV10.lean
```

The file contains no `sorry`, `admit`, additional axiom declaration, or
unsafe definition. The trusted base includes Lean's kernel and the imported
standard library, including classical reasoning used by the proofs.
