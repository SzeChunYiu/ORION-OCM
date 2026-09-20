# Independent formal review V21

Read [CORE.md](CORE.md) and [FORMAL_SCOPE_V21.md](FORMAL_SCOPE_V21.md).
This reviewer authored the paper derivations and independently inspected the
other author's Lean implementation and exact typed registrations. This is not
a second independent authorship of the paper proof.

## Fresh replay

Ran check_lean_v21.evaluate on laptop billy against the final frozen sources.
Lean 4.19.0 freshly compiled all 19 sources in isolated storage, then compiled
the generated audit containing 152 explicit typed registrations. Result PASS.
The count includes constructors and operational equations, not 152 new theorems.

- Audit SHA256: 4cfeda2438df892f1dfbd5a5318ac4498aee853ea9dcf0bd3d98f3bfe6c80a80.
- Contract SHA256: c34abddda77f8252b0926a81619a17f376baad72984342e8d68796bdfb033d95.

The checker reads immutable dependency sources, builds fresh objects, fixes the
registered types independently of the candidate terms, and inspects printed
axioms. Source and audit failures have distinct stages; unavailable inputs are
CannotCheck. Classical.choice, propext and Quot.sound have their ordinary Lean
meaning; they do not supply execution, image, or resource conclusions.

## Execution and context bridges

WeightedExecution follows actual V8 next transitions and preserves factor order.
Its concatenation proof uses the actual intermediate state. BudgetResidual's
endpoint executes the actual V8 budgetMachine; residual_iff derives its success
condition, endpoint and remainder from guarded Nat subtraction. Larger resource
amounts preserve physical endpoints, not equal residual states.

SuccessfulResponse proves equality of full original V8 responses on complete
successful words. It retains observations and edge payloads; a failed resource
trace is outside that equality. The empty-word and absent-transition cases are
not hidden by nonempty-state assumptions in the generic definitions.

HistoryContexts uses actual V15 Context, separate P and E, and actual finite
histories. Bounded admission changes P while preserving the whole evaluator
record. within_operational and within_mono connect inclusion to execution,
not merely to a resource label. The registered view equations bind illegal,
undefined and value observations. fromStart/from_image bind the supplied start
to the actual first coordinate of each history.

HistoryUnions constructs all finite-length witnesses and identifies their union.
JointImages similarly proves the all-Nat-resource union. Infinite action spaces
are allowed; neither theorem promises a finite enumeration or an infinite trace.
The original Attainability source and three original lemmas are freshly replayed.
Its actual Attain is connected to the same Context/image witnesses, including
maximality and target capability; a new theorem name is not a replacement.

## Information and thresholds

J pairs the actual execution cost with the value of that same admitted evaluated
history. joint_filtration and projection_image are witness equivalences.
Projection constructor registrations bind its actual domain, evaluator, order
and retained admission. An arbitrary declared coordinate map needs no monotonicity
for the image equation; no preference-preservation claim is inferred.

CapabilityThreshold proves existence and uniqueness of a least Nat member before
choosing it. threshold_attained produces an actual history, endpoint and target
value at that cost. value_cutoff proves that singleton-target thresholds determine
the filtration. Classical selection does not make arbitrary target existence
computable. Full J is not claimed recoverable from its filtration; the paper
separately exhibits invisible higher-cost duplicate witnesses.

## Resource assumptions and repaired registration

CostMonoid contains an ordered associative unital product compatible in both
arguments. It assumes neither commutativity nor positive increments. Cumulative
checks the initial prefix as well as each reached step. Capacity nesting is
proved without positivity. PathPositive supplies the sharper final-affordability
iff under positivity along the actual word, rather than over every possible
payload. Nonzero initial spending is retained in this general theorem.

The concrete Nat residual correspondence is registered at zero initial spending.
Its nonzero-initial-spending corollary remains paper-level, as stated in scope.
Nat-add, Nat-max, vector-add and mixed models bind their actual operations.
The signed resource-word machine and maximum-prefix-demand theorem are real
constructions, including arbitrary initial spending and the initial prefix.
They are not a generic signed shortest-path theorem for arbitrary machines.

Review found a registration weakness in the preliminary signed-model inventory:
abstract record/result types alone did not bind addition, order, transitions and
maximum recursion. The author added seven exact equations for the Int operation,
identity and order, the machine next/observation, and demand nil/cons. I read the
final equations and corresponding typed entries and replayed that strengthened
152-entry inventory. The weakness is resolved.

The root reports four final source-valid hostile replacements: all-empty sources
and weakened residual, joint and pathwise-prefix/final leaves. Each changed
source compiled, then failed at AUDIT. This report is corroborating root evidence;
the independent replay above is my own execution. Canonical mutation outcomes
belong to RESULT_V21.json and its bound test sources.

## Boundaries and verdict

No assumed conclusion, mismatched quantifier or outstanding formal defect was
found in the reviewed final inventory. The paper's prefix-list characterization,
nonzero Nat adapter, general resource-image corollaries, noncommuting matrix
illustration and Real nonattained infimum are not silently called kernel proofs.
Finite Python calibration remains independent of the Lean implementation.
Neither code generation nor a universal shortest-path solver is certified.

These results support the six named R3 records for their registered scopes.
They establish no enabling-barrier identity, generic probabilistic success,
unique objective, whole-round completion, or full GMI theory.
