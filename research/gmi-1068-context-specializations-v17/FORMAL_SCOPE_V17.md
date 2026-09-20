# V17 formal scope

Read FREEZE_V17.md first. Only original GMI2-R2-005 is a closure candidate.
This document records mathematical proof coverage, not an automatic adjudication.
R2-003/007 remain unchanged originals; R2-008/009 are outside this study.
No complete intelligence theory or new mathematical mechanism is certified.

## Kernel replay and source custody

All Lean sources compile with pinned Lean 4.19.0 and warningAsError.
The immutable V15 PartialContextV15.lean supplies the actual Context interface.
Six new modules depend on it; no alternative shadow Context is introduced.

On billy-laptop, from this package:

```sh
GMI_LEAN_BIN=/home/billy/.elan/bin/lean /home/billy/.local/bin/python3.12 \
  -c 'import check_lean_v17; print(check_lean_v17.evaluate())'
```

The integrated driver supplies reviewed sibling imports in isolated Python.
check_lean_v17.py freshly stages all seven source files in a temporary directory,
compiles every dependency there, and then compiles the generated typed audit.
LEAN_PATH points to that isolated directory, not previous build artifacts.
The receipt binds every source digest, audit digest and registration count.
Missing tooling or unreadable sources raise CannotCheck; rejected source/types
raise InvalidProof with a stage. These are different evidence outcomes.

proof_contract_v17.py contains 97 explicit, fixed typed registrations.
They include actual constructor result types and their domain, value and order
equations; merely returning an unrelated Context with the same type is insufficient.
The generated definitions are checked at those exact types and their assumptions
are printed. Source bytes and registrations remain independently bound.
The audit does not reconstruct its contract from the source being tested.

Standard Lean foundations include proposition extensionality, quotient soundness
and classical choice where used. No additional mathematical axiom is introduced.
Generic preorders, explicit domains and comparison hypotheses remain premises.
The general partial observation function is noncomputable over arbitrary predicates.

## Context maps and observable tags

ContextMapsV17.lean constructs OrderMap from a function and monotonicity proof.
identity and compose have actual application equations, identity and associativity.
This package does not add a bundled category of preorders.

postcompose accepts any value map and declared target preorder.
Its defined domain equals the original domain, its evaluator is actual function
composition, and its order equals the supplied target order.
Identity and composition of postprocessing are proved as Context equalities.

outcomeMap changes only value payloads.
post_observe equates actual postprocessed observation with that tag-preserving map.
Immutable V15 illegal/undefined/value equations and their pairwise disjointness
are freshly registered. An evaluator may be defined on an illegal history;
admission still suppresses its value.

Monotonicity preserves active comparisons.
An additional explicit order-reflection hypothesis gives an iff.
Neither monotonicity nor injectivity alone is claimed to provide reflection,
preserve incomparability or preserve distinct tied values.

dual reverses order while retaining definedness and values.
Its active comparison is the original reversed comparison.
dual_observe preserves the entire observation, including its payload.
Double dual returns the original Context.

## Products and the empty-family distinction

ProductContextsV17.lean constructs finite dependent tuple preorders pointwise.
No scalarization or total order of incomparable vectors is introduced.

shared receives one domain E and evaluators for every coordinate on E.
Its domain remains exactly E for every finite dimension, including zero.
Projection and active-comparison laws refer to those actual coordinate evaluators.
shared_observe records the exact admission/domain/value conditional.

independent takes Context-valued components with possibly different domains.
Its domain is their intersection; its evaluator forms the actual tuple.
The comparison theorem is pointwise on jointly defined histories.
Projection recovers each component value on that joint domain only.

independent_observe and independent_has_value give the exact joint observation.
independent_undefined proves admission together with failure of joint definedness.
No missing component is replaced by a default.

For zero independent components, the intersection is True.
Every admitted history then returns the unique empty tuple, as proved by
independent_empty_defined and independent_empty_observe.
An illegal history still returns illegal.
This differs deliberately from the shared-domain zero-dimensional constructor.

## Concrete codomain specializations

SpecializationsV17.lean uses actual Context records throughout.
utility accepts a declared preorder and an evaluator on E; its comparisons
are exactly those of the declared codomain applied to the evaluator's values.
intUtility binds this constructor to the actual Int order.
No Real type or Real order instance is supplied to the kernel in this package;
ordinary Real utility is a paper specialization of the generic construction.

acceptance evaluates the declared predicate to Bool on the same domain E.
acceptance_true proves the exact predicate equivalence.
Acceptance comparison is implication between these predicates.
bitScore maps false/true to actual Int zero/one; bit_order_iff proves both
comparison directions, and bit_embedding_apply binds the actual OrderMap payload.

vector is the shared-domain tuple constructor with coordinatewise comparison.
pareto_comparison states that comparison exactly, including empty tuples.
cost uses its dual: a larger preference value means no greater burden in each
coordinate. cost_defined/cost_value/cost_comparison bind the actual constructor.
The orientation is declared; it is not inferred from physics or resource names.

ConfidenceV17.lean constructs Region X as a predicate together with a
nonemptiness proof. precision is reverse inclusion and is proved antisymmetric
as well as satisfying its constructed preorder laws.
confidence is an actual Context with the caller's E and region evaluator.
Its domain, value, nonemptiness and exact active comparison are registered.
This is a declared information order. No probability, statistical calibration,
coverage, truth guarantee or empirical confidence quality is inferred.
No interval-specific construction is included.

## Viability fixedpoint and trajectories

ViabilityV17.lean takes arbitrary X, safe predicate K and one-step relation R.
R need not be finite, deterministic, serial, decidable or finitely branching.
It denotes a discrete evolution step. Category identities and empty paths
are not inserted into R; a time-advancing self-loop must be explicitly supplied.

step(K,R,I)(x) means K(x) and some R-successor belongs to I.
Postfixed means I is included in this actual step image.
Viable is the union of all postfixed sets, expressed by an existential witness I.

step_monotone, viable_greatest, viable_postfixed and viable_safe are derived.
viable_fixedpoint proves equality with the actual step image in both directions.
These conclusions are not supplied as fields of an assumed fixedpoint interface.
This is the classical powerset instance of the parent fixedpoint construction.

Trajectory requires one function Nat -> X, the specified initial state,
safety at every index and every successive R-edge.
next chooses a successor within Viable using Classical.choose.
walk uses Nat recursion on that viable-state subtype.
viable_to_trajectory therefore produces one complete infinite trajectory.
trajectory_to_viable uses the range of an actual trajectory as its postfixed set.
Both directions and viable_iff_trajectory are separately registered.

viabilityContext applies this actual Viable predicate to an endpoint map on E.
Its Bool value, comparison, definedness and full tagged observation are registered.
It does not claim effective membership testing for arbitrary state types.
Existential evolution is not robust adversarial safety or a universal-successor rule.

## Infinite branching and algorithmic boundary

CountdownV17.lean gives root an edge to every natural countdown chain.
A positive counter decreases by one; zero has no successor; all states are safe.
every_finite_horizon constructs a trajectory prefix for every natural horizon.
The function outside that horizon has no required continuation semantics.
chain_no_trajectory and root_no_trajectory rule out infinite runs.
finite_horizons_do_not_imply_viability combines this with the generic theorem.

Thus independently possible finite prefixes do not establish one infinite run.
No compactness or finite-branching premise is silently inserted.
The finite production elimination algorithm, its termination/cycle arguments
and its independent oracles are paper-and-test evidence, not kernel-checked
algorithm implementations or proved Python/Lean correspondence.
Finite enumeration does not replace the arbitrary-space proofs above.

Parent ownership remains preorder/product order, information ordering and
classical fixedpoint/trajectory mathematics. Continuous-time limits, numerical
convergence, physical identification and canonical objectives remain outside scope.
