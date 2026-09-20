# V24 — full candidate identity preference correspondences

## X2.1 — actual coordinate context and Pareto frontier

Fix candidate IDs I and vectors r_i in A^n, where A has declared ordered-ring laws.
Mathematical coordinate order needs neither nonnegative resources nor n>0.
The faithful old executable domain additionally requires finite valid rosters,
unique nonempty IDs, n>=1, nonnegative exact Fraction coordinates and Boolean flags.
For reachable_only flag R set P(i)=viable(i) and (not R or reachable(i)); E is total.
Construct context values (i,r_i) and reverse-coordinate order:
(i,x)<=W(j,y) iff every coordinate y_k<=x_k.
Reflexivity/transitivity hold coordinatewise; identity tags are not compared.
Its attained image consists exactly of (i,r_i) for active i, by actual V15/V20 images.

A competing image is strictly better iff all its coordinates are no greater and
some coordinate is strictly smaller. Forward: failure of the converse coordinate
comparison gives a coordinate where it fails, which totality makes strict.
Backward: that strict coordinate prevents the converse comparison. Therefore
(i,r_i) is maximal iff no active candidate strictly Pareto-dominates i.
Projection to I equals the full old pareto_front after actual viable_set.
Distinct IDs with equal vectors remain distinct maxima. No representative of a
preorder-equivalence class replaces this full identity correspondence.

## X2.2 — declared positive-price specialization

Supply weights w_k>0 and let s(i)=sum_k w_k*r_i,k. Construct a second context
with values (i,s(i)), total E, same P, and reversed scalar order. Its full maximal
image projects exactly to all IDs attaining the minimum among active candidates:
a strictly lower competing scalar is exactly a strictly better image value.
A finite nonempty active roster attains such a minimum; empty active image stays empty.

If j Pareto-dominates i, each difference r_i,k-r_j,k is nonnegative and one is
positive. Products with w_k are nonnegative and that positive-coordinate product
is positive. The finite sum is positive; distributivity yields s(j)<s(i), the
immutable V12 dot_strict mechanism. Thus a scalar minimizer cannot be dominated.
The converse, every Pareto point supported by positive prices, is not asserted.
This proof uses declared weights, not a discovered canonical price or objective.

## X2.3 — complete lists, emptiness and exact old behavior

An explicit finite roster must cover every candidate in its registered universe.
Filtering it by P and applying the actual full V20 frontier gives precisely the
mathematical active maximal membership. Duplicated vectors keep distinct IDs;
list membership results do not alone establish canonical serialized ordering.
The Python adapter separately checks sorted IDs and exact old output dictionaries.

The old selection_record returns NO_VIABLE_MORPHOLOGY with empty Pareto/argmin lists
when viable_set is empty; otherwise it returns SELECTION_DEFINED and the two full
correspondences. Old scalar_scores/selection_record may skip weight checks on
empty active input. The new strict boundary validates even unused weights; it
compares old semantics only on valid inputs and does not rewrite old parsing claims.
The generic n=0 theorem (all vectors equal) does not permit empty resource vectors
in that faithful old interface. Likewise negative resources allowed by abstract
order proofs do not become valid old resource declarations.

The adequate-output Gamma source and its setup/implementation cost accounting are
not silently imported here: same-task adequacy and full cost assumptions require
their own contract. AI0 SEL is a downstream interface; a unique choice additionally
needs an actual strict optimum or a separately supplied tie-breaking rule.
