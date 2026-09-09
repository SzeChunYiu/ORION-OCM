# Hostile — G14: cone-local reasoning fails without cone completeness (xi)

Atom: G14 (dependency cone). Rung: R1 (sub-finding on the parent's
precondition). Verdict for the atom: PARENT_SUFFICIENT; the xi-removal
counterexample below is recorded because it breaks the parent's precondition.

## Claim under attack
Updates carry declared dependency cones; cone-local reasoning ("an update's
effect is confined to its declared cone") remains sound when the declared cone
may be INCOMPLETE — some real dependencies undeclared. Assumption removed: xi
(cone completeness).

## Minimal counterexample
State coordinates: (L, Q, V). Update u has declared cone {L}: it rewrites the
language as f(L, c) where c is a cached value derived from the verifier V.

- World A: V = v (hence c = c_v). u(L, Q, v) = (f(L, c_v), Q, v).
- World B: identical except V = v' (hence c = c_{v'} ≠ c_v). u(L, Q, v') =
  (f(L, c_{v'}), Q, v').

V ∉ declared cone, so cone-local reasoning certifies: intervening on V (or any
swap v → v') cannot change u's behaviour on its cone; the predicted L-posterior
is the same in both worlds. Actual posteriors differ whenever f(L, c_v) ≠
f(L, c_{v'}). Cone-local prediction is therefore unsound in general.

This is exactly the causal-DAG parent's precondition failing: intervention
locality holds only in a *complete and correct* DAG; a missing edge (the
undeclared V-dependence) destroys descendant-invariance. G14's positive R1
content is thus owned by the parent conditional on xi — removing xi removes
the parent's applicability, not a weakness of the lift itself.

## Repair directions (for the registry, not claimed as done)
- Treat every declared cone as an over-approximation (sound abstraction):
  cone-local conclusions must be conditioned on completeness certificates, or
  stated as one-sided bounds robust to undeclared reads.
- Blackwell 1951/53 reading: an incomplete cone acts as a garbling of the true
  dependency information; value of cone-local reasoning is then bounded by the
  garbled-experiment value — never by the full-DAG value.

## Propagation note
Any consumer of cone locality (incremental burden accounting, modular update
scheduling, G16 amortization scoped to modules) inherits this failure when
cones are not certified complete.
