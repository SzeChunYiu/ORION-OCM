# Next original scientific requirements to adjudicate
Read-only planning against the original atomic registry and V9 proofs.
No status is changed here. Freeze and independently audit each successor.

## First: GMI2-R2-002
Original target: prove context is not derived from process law, using an
explicit same-process countermodel with different evaluations/orderings.
V9 already proves the general collision criterion and constructs actual
opposite rankings on the same full process and ambient history domain.
Relevant declarations: recoverable_iff_fiber_constant,
no_recovery_of_collision, process_does_not_recover_context,
actual_ranking_reversal in RecoverabilityV9.lean.

Independently check that process maps are literally identical, both evaluators
share their domain, disagreement occurs on admitted histories, and rankings
reverse on actual actions rather than selector names. Semantic nonrecoverability
does not imply probabilistic independence. This could close the original atom
while R2 remains OPEN; gate.py permits evidenced closed atoms within open
rounds. Only whole-round EARNED requires every parent round EARNED.

## Next: GMI2-R1-002 and GMI2-R1-003
Original targets: prove typing/associativity and identities.
The original ProcessCore.lean assumes category laws as fields and projects
them. Construct finite typed paths for an arbitrary graph E:V→V→Type,
then prove endpoint preservation, append associativity and both empty-path
unit laws. Prove the unique identity/composition-preserving interpretation
extending fixed object and edge interpretations into any category.

Strongest registered parent: Riehl, Category Theory in Context, Example4.1.13.
This is a faithful classical construction, not new universal primitive
minimality. Controls must reject incompatible endpoints, reversed append,
collapsed parallel edges, altered empty-path semantics and an unfixed
generator/object interpretation masquerading as uniqueness.

## Next: GMI2-R2-006
Original scalarization target admits only licensed order conclusions.
For finite real vectors prove nonnegative weighted sums preserve domination;
positive weights preserve strict Pareto domination. Every incomparable pair
admits two strictly positive weight vectors giving opposite strict rankings.
Increase one positive and then one negative difference coordinate from the
all-ones weight vector. Prove these bounds generally; do not only replay
the old two-coordinate example. Negative weights, ignored strict improvements,
comparable vectors and ties are explicit falsifiers.

## Targets requiring a declared correction
R2-003 originally types contexts over admitted histories. Their domain exposes
admission, so reverse independence is false under that formulation. V9's
shared ambient evaluation domain plus separate admission is the constructive
repair. Explicitly reconcile the corrected target before closing anything.

R2-007's title concerns nonuniqueness but its freeze claims every universal
scalar needs a measure/weighting. V5's min/max examples refute that claim.
A corrected theorem concerns extra aggregation structure; probability weights
follow only under appropriate linearity and normalization assumptions.

R1-001/006/007 primitive-count minimality is not presentation invariant.
Fix a model class, retained observations and allowed translations, then prove
nonrecoverability for proposed deletions. V9's unique-unit elimination and
fiber theorem support this repair; they do not prove a smallest ontology.

These are concrete original-requirement targets, avoiding an indefinite chain
of local results without adjudication. All 214 other statuses remain unchanged
in V10. Historical false formulations and successful repairs both remain visible.
