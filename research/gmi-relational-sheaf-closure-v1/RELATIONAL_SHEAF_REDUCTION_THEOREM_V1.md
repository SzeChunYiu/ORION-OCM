# Relational/sheaf parent-reduction theorem v1

## Carrier and exact family

For variables \(x_0,\ldots,x_{n-1}\in[d]\), patches
\(P_i=\{x_i,x_{i+1}\}\), and local relations
\(R_i\subseteq[d]^2\), a local section is an allowed pair. RESTRICT projects
to an overlap; GLUE joins agreeing sections; CHECK decides extendability; PROJECT
returns the canonical global section. The obstruction is an empty propagated
boundary fiber or an inconsistent cycle syndrome on a general factor graph.

The committed N3 receipt contains 11 dense, sparse, and late-failure families,
two storage columns, five rows, 110 executed cells, and 508 frontier cells. The
no-glue twin differs in all 22 cell-column answer signatures.

## Theorem RS-1 — CSP/SAT and factor-graph reduction

Create one CSP variable per \(x_i\) and one binary constraint with table \(R_i\)
per patch. Global sections are exactly satisfying assignments. A SAT compiler
uses one-hot literals \(X_{i,v}\), exactly-one constraints, and clauses
\(\neg X_{i,u}\lor\neg X_{i+1,v}\) for every disallowed pair. This is
\(O(nd^2)\) clauses/literals at fixed arity and preserves solutions exactly.

The same construction is a factor graph with indicator factor
\(\phi_i(u,v)=1[(u,v)\in R_i]\). Sum-product over the Boolean semiring decides
existence; min/lexicographic messages recover the canonical section. On the chain
cover, forward/backward messages are exactly GLUE/RESTRICT dynamic programming.
Probability weights may be added, but none are required for the relational
obligation.

## Theorem RS-2 — message-passing/GNN and D7 reduction

Assign one D7 component to each variable/factor and a length-\(d\) Boolean
message to each directed incidence. Inward update is

\[
m_{i\to i+1}(v)=\bigvee_u(m_{i-1\to i}(u)\land R_i(u,v)).
\]

After at most \(n-1\) forward and \(n-1\) backward rounds, the messages equal
the candidate's restrictions, so CHECK and canonical backtracking give the same
answer. A discrete message-passing GNN with Boolean-semiring aggregation and
typed messages implements this update exactly. An unconstrained learned GNN is
not asserted to discover it; the reduction is to the explicit parent operator.
State is \(O(nd^2)\), messages \(O(nd)\), and work \(O(nd^2)\).

Thus the candidate reduces to CSP/SAT, a factor graph, explicit message passing,
and D7. The committed receipt separately confirms bit-identical answers against
an eager table parent and a lazy program-search parent in 22/22 cells each.

## Frontier prediction and burden gate

The frozen niche was bounded-overlap, late global failure: eager materialization
pays \(d^n\) construction, lazy DFS fails late, while propagation remains
polynomial. The receipt confirms SHEAF as sole frontier occupant through
\(H=1024\) in the \(n=10,d=3\) late family under both reduced storage columns,
then the materialized parent wins beyond its analytic crossover. This is a
compile/serve phase, not domain novelty.

A failed semantic reduction is insufficient for novelty. It must carry a
nonempty, material lifecycle/asymptotic burden-separation witness; otherwise the
terminal is `CANNOT_IDENTIFY`. Here reductions succeed, so no failed-reduction
residual is claimed.

## Claim ceiling

Seven reduction/infrastructure tasks close. “Neutral recovery” remains open:
the executed microscope instantiates the candidate directly and is not a blind
search over a neutral grammar.
