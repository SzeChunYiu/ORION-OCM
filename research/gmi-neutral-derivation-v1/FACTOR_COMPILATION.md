# Deriving finite inference circuits by distributivity

Status: constructive exact theorem and prospective registered execution. This
adds a positive compiler to the previous finite relational-domain reduction.
It does not claim a new algorithm or an unrestricted domain basis.

## FC1: explicit premises and the protected function

Let variables \(X_1,\ldots,X_n\) have nonempty finite domains of sizes
\(d_i\le q\). Supply finite factors \(f_j\) on declared variable scopes,
with complete tables, and a commutative semiring
\((R,\oplus,\otimes,0,1)\): both operations are associative, addition and
multiplication commute, multiplication distributes over addition, and zero
annihilates multiplication. These are additional task/algebra assumptions.
The protected query is
\[
Z=\bigoplus_{x_1,\ldots,x_n}\ \bigotimes_{j=1}^m f_j(x_{\mathrm{scope}(j)}).
\]
Our three executable cases use Boolean OR/AND, nonnegative rational +/×,
and nonnegative integer min/+ with infinity. Infinity is encoded as `None`;
there are no floating-point approximations. The product of no factors is one.
The learner is not supplied a Bayesian, CSP or message-passing architecture.
It is supplied factorization and algebra; those cannot be erased from the claim.

## FC2: elimination is a derived semantics-preserving rewrite

Choose any remaining variable \(v\). Collect its \(k_v\) incident factors
into a bucket and let \(U_v\) be their union of scopes together with \(v\).
Construct the table
\[
g_v(x_{U_v\setminus\{v\}})
=\bigoplus_{x_v}\ \bigotimes_{f\text{ in bucket}}f(x_{\mathrm{scope}(f)}).
\]
Replace the bucket by \(g_v\). **Proof:** all other factors are independent
of \(x_v\); finite distributivity moves their product outside that sum.
Associativity/commutativity permit regrouping the remaining sums/products.
Thus the protected scalar is unchanged. Repeating for any permutation of all
variables leaves scalar factors whose product is exactly \(Z\). This proves
termination and correctness for every finite input, not just registered graphs.

Empty buckets are retained: eliminating an isolated variable gives
\(\bigoplus_{x_v}1\), which equals \(d_v\) over rationals, true over
Booleans and zero in min/+. Discarding it corrupts partition counts. Original
scalar factors also remain in the final product. These are explicit controls.

The compiler lowers each new table to loops, table reads and scalar
\(\oplus,\otimes\) operations. Its intermediate tables and their dependency
edges form an inference circuit. The distributed message interpretation is
obtained from that circuit; no `belief_propagate` or `solve_CSP` instruction
is required. This is derivation inside the declared factor algebra, not
neutral recovery of that algebra from arbitrary experience.

## FC3: exact cost certificate and width-dependent upper bound

The registered schedule initializes every product at one and every sum at
zero, performing every indicated operation even when a short circuit exists.
Define \(A_v=\prod_{u\in U_v}d_u\), \(B_v=A_v/d_v\), and let \(r\)
be the number of scalar factors remaining after elimination. Then exactly
\[
N_\otimes=N_{\mathrm{read}}=\sum_vk_vA_v+r,
\quad N_\oplus=\sum_v A_v,
\quad N_{\mathrm{new\ entries}}=\sum_v B_v.
\]
Therefore registered scalar/read work is
\(W=\sum_v(2k_v+1)A_v+2r\). Every original factor and every generated
factor is consumed at most once, so \(\sum_vk_v\le m+n\) and
\(r\le m+n\). Writing \(w=\max_v(|U_v|-1)\), for \(n\ge1\),
\[
W\le(2m+3n)q^{w+1}+2(m+n).
\]
This is an upper bound for this compiler, not a lower bound on all solvers.
High width alone does not force hardness: special factors may admit an
algebraic simplification, and a different algorithm may avoid these tables.

Original input tables stay resident. Immediately before releasing a bucket,
the peak resident numeric entries are input entries plus live generated
entries plus the new output table. The implementation records this schedule,
the corresponding exact numeric payload bits, generated entries/bits, maximum
scalar bit length and arithmetic-result bit volume. It separately counts
scope visits, indexing coordinates, assignment writes and validation checks.
The two-coordinate selection score is \((W,\text{peak entries})\); it is
a declared preference, not an assertion that other resource coordinates vanish.
Container, indexing-instruction, compiler and physical execution overhead
cannot be inferred from a unit scalar/read count. Bit counts prevent exact
rationals from being mislabeled as fixed-precision constant-cost hardware.

## FC4: complete finite order search, ties and paid optimization

`factor_search.py` enumerates all \(n!\) permutations, executes each compiler
plan, and compares its exact integral score lexicographically. Every order is
visited exactly once. The finite set is nonempty, so the smallest score is
attained; every minimizing order is retained, with the lexicographically
first selected. Equality is decidable here. This certifies a minimum within
the entire elimination-order family, not all programs or all factorizations.

The search reports the sum of every candidate's scalar and metadata counters,
\(n!\) candidate visits, \(n\,n!\) order coordinates, \(n!-1\) score
comparisons, certificate scalars/order coordinates and retained tie coordinates.
Candidate table-space peaks and certificate sizes are separate coordinates;
they are not represented as one measured process-memory figure. An amortized
deployment comparison must include search and certificate construction costs.
No order search is hidden in the reported selected circuit's query cost.

## FC5: known inference families and finite development

Boolean factors express local constraints: FC2 decides global satisfiability.
The uneliminated factors/messages also permit witness recovery by retaining
allowed values and reversing elimination, or by conditioning variables and
re-running the exact existence query. The latter is a finite constructive
algorithm, but its additional calls must be charged. Min/+ computes the minimum
sum of local costs, giving finite weighted search/optimization. Rational +/×
computes the partition function of a supplied factor model. Add unary indicator
factors and re-run for each queried value to obtain unnormalized marginals;
divide by positive \(Z\) to obtain normalized probabilities. \(Z=0\) means
conditioning is undefined, requiring an explicit operational response.

Bayesian semantics additionally require a correctly specified prior/likelihood
factorization; sum/product algebra does not identify causal interventions.
Replacing, adding or deleting a finite factor gives another legal finite
instance. Recompilation and execution preserve its new protected value by FC2,
so finite update sequences have the corresponding exact response sequence by
induction. The present implementation recomputes and charges the whole plan;
it claims no unimplemented incremental-cache advantage or convergence theorem.

## FC6: frozen predictions and falsifying comparisons

`factor_registration.json` fixes two calibration graphs and four held-out
graph/parameter cases before any laptop execution. All three algebras must
match independent full-assignment enumeration for every searched order.
The independent interpreter uses its own indexing and algebra operations.
Additional controls cover scalar zeros, empty factors, singleton domains,
cyclic local consistency without a global solution and invalid orders/tables.

Registered analytic predictions include exact chain/star operation laws, the
star's unfavorable center-first ordering, complete-graph order ties, and a
width-two cycle witness. A different selected order or favorable low-width
example alone is not novelty. A semantics mismatch, wrong count, omitted
order or lost tie falsifies the implementation claim at that case.
Held-out here means graph/size withheld from calibration, not autonomous
discovery of a new problem domain. No empirical result is asserted in this note.

## Parents and scope of the addition

This specializes the general distributive law of
[Aji and McEliece (2000)](https://authors.library.caltech.edu/records/sw1pm-bwj40)
and the compilation framework of
[Dechter (1999)](https://ics.uci.edu/~csp/r48b.pdf).
The added GMI result is an explicit algebra-to-circuit compiler with scoped
finite completeness, exact operation accounting, paid order search and
registered cross-algebra/held-graph controls. Classical elimination and message
passing remain the parents; no new intelligence domain is claimed.
