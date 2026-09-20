# Formal scope V21

Read [CORE.md](CORE.md) first. This file delimits the evidence for
[FREEZE_V21.md](FREEZE_V21.md). Original-atom authority belongs to the reviewed
successor record; these proofs do not promote a whole round.

## Replay

[proof_contract_v21.py](proof_contract_v21.py) contains 152 explicit typed
registrations. These include data types, constructors, operational equations
and mathematical theorems; they are not 152 independent scientific results.
[check_lean_v21.py](check_lean_v21.py) stages and freshly compiles 19 sources:
13 new modules and six immutable V8, V15, V20 and original R3 dependencies.

The compiler is Lean 4.19.0 with warnings treated as errors. The generated
separate audit binds fixed declared types to the named source terms and prints
their kernel dependencies. Types are not discovered dynamically during replay.
No existing project object file substitutes for a source compilation.

From this package on laptop billy:

```sh
GMI_LEAN_BIN=/home/billy/.elan/bin/lean /home/billy/.local/bin/python3.12 -c \
 'import check_lean_v21; print(check_lean_v21.evaluate())'
```

Unavailable compiler/source inputs give CannotCheck. Invalid source and
invalid typed registration give separate InvalidProof stages.
ProofTargetsV21 isolates three exact-statement leaves for source-valid hostile
replacements; those replacements must compile before failing the typed audit.
Final source, contract and audit hashes are recorded by the integrated receipt.

## Actual weighted execution

[WeightedExecutionV21.lean](WeightedExecutionV21.lean) follows the immutable
V8 Machine.next. Each successful result contains its physical endpoint and
the ordered product of actual edge costs. Empty words have identity cost;
missing transitions produce None. Both recursion equations are registered.

The concatenation theorem uses the actual intermediate endpoint. Cost products
retain execution order and are associated using the declared monoid law.
The endpoint-projection theorem identifies success with actual physical
execution; a cost result is not assumed to exist for a failed word.

## Residual Nat resources and complete responses

[BudgetResidualV21.lean](BudgetResidualV21.lean) executes the destination
projection of the actual immutable V8 budgetMachine. Its residual_iff states:

`budgetEndpoint(s,b,w)=some(t,r)` iff some actual weighted execution has
result `(t,c)`, with `c≤b` and `r=b−c`.

This covers arbitrary finite words, zero costs, absent transitions, and empty
state/action types. Budget concatenation uses the actual residual returned by
the prefix. Larger budgets preserve successful words and physical endpoints,
with the correctly changed remainder; residual states need not be equal.

[SuccessfulResponseV21.lean](SuccessfulResponseV21.lean) proves that on every
such successful complete word, the full V8 budgeted Response equals the full
unrestricted Response. This includes every intermediate observation and edge
payload. It is stronger than endpoint equality, and conditional on success.
It does not equate a resource failure with an unrestricted successful trace.

V8 transition functions are total mathematical functions returning Option.
None means an unadmitted transition, not proved divergence of an implementation.

## Actual fixed history contexts

[HistoryContextsV21.lean](HistoryContextsV21.lean) uses raw histories
`(start, finite word)` and actual V15 Context records.
A Scenario consists of an admission predicate and that Context.
Unrestricted admission is original P, declared selection, and physical success.
Bounded admission additionally requires actual total Nat cost at most b.

The complete Context is retained exactly: ambient E, evaluator, and preorder.
The view applies V15 observe to the new admission predicate and the unchanged
Context. Illegal, admitted-but-undefined, and actual value cases are separately
bound. Defined ambient evaluations on illegal histories are allowed.

within_operational links bounded admission to actual residual execution.
within_mono derives its inclusion through the successful-execution theorem.
image_mono, selector_mono, bounded_subset and bounded_mono then transport those
history inclusions through the fixed evaluator. A changing evaluator does not
satisfy these premises merely because its parameter is called a budget.

## Finite-history unions and original meanings

[HistoryUnionsV21.lean](HistoryUnionsV21.lean) defines fromStart and fromScenario.
from_image binds the selected start to the actual first coordinate, not to an
unused parameter. Arbitrary selectors are also supported as a broader result.

all_horizon_union proves that the unrestricted selected finite-history image
is the union of its bounded-length images. Every witness supplies its own word
length. Infinite action types are permitted, so even a bounded-length family
need not be finite. No enumeration algorithm follows from this union.

The original Attainability.lean is freshly compiled. Its actual Attain and
three original lemmas are explicitly registered. original_attain_bridge,
v15_active_bridge and v20_attained_bridge identify the same partial-evaluator
image across those representations; original_maximal_bridge relates the
original strict-part formulation to V20 maximality. No historical statement
is replaced by an unrelated declaration with the same name.

These unions concern finite witnesses. They add no infinite trace, limit point,
almost-sure event or asymptotic attainment.

## Joint cost/value information and resource projections

[JointImagesV21.lean](JointImagesV21.lean) constructs J from actual selected
physical histories, original admission, evaluator definedness, actual execution
cost and evaluated value. joint_filtration proves
`A_b(v) ↔ ∃c≤b, J(c,v)`; joint_unrestricted identifies the unrestricted image.
all_budget_union covers all Nat budgets, not a finite test interval.

Capability is existential membership in a declared target, and capability_joint
derives its resource response from J. Targets can be arbitrary: this is exact
image inclusion, unlike the upward-goal condition for V20 cofinal pruning.

The separate value-coordinate meaning is implemented by projectContext:
its evaluator is the actual composition with a declared rho, its domain is E,
and its order is the supplied target preorder. projectScenario retains
admission. projection_image proves exactly rho applied to the attainable image.
No undeclared coordinate, order preservation, or intrinsic scalar score is
inferred from the existence of an image.

## Attained least Nat costs

[CapabilityThresholdV21.lean](CapabilityThresholdV21.lean) derives existence
and uniqueness of a least member of each nonempty Nat target-cost set.
The constructed threshold is Some n for that attained minimum and None for
no finite successful witness. capability_cutoff is the exact budget criterion.
threshold_attained exhibits a selected admitted physical history of cost n,
its endpoint, defined evaluator, and a value in the target.

value_cutoff shows that singleton-target thresholds determine every A_b.
Thus J is sufficient but is not asserted minimal or recoverable from the
filtration: higher-cost occurrences of an already cheaper value can be hidden.

The abstract minimum uses classical choice. There is no decision procedure or
shortest-path solver for arbitrary history predicates or partial evaluators.

## Ordered accumulation and signed revival

[OrderedCostsV21.lean](OrderedCostsV21.lean) supplies an explicit preorder,
identity, associative multiplication and compatibility with both ordered
arguments. Commutativity, cancellation, positivity and subtraction are absent
from this interface. Actual Nat-add, Nat-max, vector-add and mixed
time-add/peak-max instances and operations are registered.

[CumulativeV21.lean](CumulativeV21.lean) checks initial spending and every
subsequent prefix. Capacity nesting requires no positive increments.
Its global-positive theorem is complemented by the stronger
[PathPositiveV21.lean](PathPositiveV21.lean) result: Nonnegative follows only
the actual specified word and reached transitions.
prefix_path_iff_final proves exact final-affordability equivalence under
that pathwise hypothesis, including the initial/empty prefix.
Unreachable payloads need not have nonnegative costs.
The Nat zero-initial-spending model is connected to actual V8 residual
accounting by cumulative_nat and cumulative_residual.

[ResourceControlsV21.lean](ResourceControlsV21.lean) also constructs an actual
Int resource-word machine. For arbitrary signed cost words and initial
spending, signed_prefix_demand proves affordability iff the computed maximum
prefix demand fits. The initial value participates in the maximum.
The final-cost counterexample and its successful larger-capacity repair,
initial-prefix failure, peak-versus-additive mismatch, and vector
incomparability are exact kernel controls.

The nonzero-initial-spending Nat residual corollary, extension of the signed
word model to arbitrary physical machines, and matrix-instance calculations
are paper/finite evidence unless separately identified. No generic resource
monoid is given a subtraction operation or a least scalar capacity.

## Evidence boundary

ConstructorBindingsV21 and the signed-control equations bind actual operations.
Ordinary Lean dependencies may include Classical.choice, propext and Quot.sound;
no unproved scientific assumption substitutes for execution or image results.
Finite Python implementations and their malformed-input checks have independent
calibration; they are not generated from these Lean definitions.
No kernel correspondence for a generic shortest-path algorithm is claimed.
