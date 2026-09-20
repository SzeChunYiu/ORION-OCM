# Complete continuation semantics — #1068 repair H / V8

Baseline main: 1f0648194b55afe8fec07d158ae0f5d3c9b31505.
This freeze precedes all outcome-bearing V8 implementation and generated results.
No empirical novelty or discovery prediction is registered by this mathematical repair.

## Intended general statements

Declare a deterministic partial machine: state set S, action set A, observation
o:S→O (including an explicit undefined evaluation token), and transition
d:S×A→Option(E×S). Edge observations E include outputs and nonnegative
integer resource costs. Absence of a transition means ILLEGAL, distinct from
an admitted state's undefined observation. Observe every finite action word,
including the empty word, recording intermediate observations, edges and the
first illegal transition. The test family is all finite words, not a supplied
finite response table.

Prove: equality of all continuation responses is an equivalence and a
transition congruence; construct its quotient machine with representative-
independent observations and transitions; prove response preservation by
induction. Any representation decoding every continuation factors uniquely
onto the response quotient on its attained image. Infer state lower bounds
and minimality up to isomorphism among reachable exact deterministic models.

For finite input machines compute the coarsest stable partition and shortest
distinguishing continuations. Prove termination/completeness and a finite
distinguishing-length bound with its exact assumptions. The general semantics
is not restricted to finite S; finite computability/minimality claims are.
Record paper proofs separately from kernel-checked statements.

Lift full-observation equivalence to residual-budget states using the actual
Nat-cost transition guard/subtraction. Prove legal/cost response preservation
for every residual budget. Do not infer equivalence from equal final outputs,
one endpoint total, or a bounded/incomplete test set.

## Independent executable evidence

Exhaust all two-state, two-action partial machines with observations from
{UNDEFINED,0,1}, edge output in {0,1}, cost in {0,1}, and either next state.
There are 9^2 * 9^4 = 59049 machines. Compare iterative partition refinement
with independently implemented product-pair breadth-first distinguishing-word
search; execute each returned witness, reject false distinctions, and compare
actual quotient-machine execution. Include deterministic larger generated
machines and long distinguishing chains; report exact coverage.

Test budget lifting, disabled actions versus undefined evaluation, delayed
future distinctions, cost-only distinctions, lossy output-only abstractions,
relabeling, omitted tests, malformed inputs and corrupted quotient certificates.
Counterexamples must actually execute; do not fabricate counts or derive the
oracle from production partitions.

## Source ownership and scope

Read primary coalgebra/automata and weighted-transducer sources. Ordinary
behavioral quotient/minimization results remain parent-owned. Observe the
difference between completed-path weight semantics and prefix operational
cost semantics. Nondeterminism, stochastic laws, approximate equivalence,
continuous-state effective minimization and all-family discovery are separate
requirements, not consequences of this deterministic theorem.

Preserve earlier frozen artifacts and original 222 requirements. Add explicit
subclaim evidence for R3/R4/R14, not automatic whole-round closure.
Use independent hostile review, optimized/normal replay, Lean4.19.0 where
feasible, and exact-head CI before ancestry-preserving merge.
