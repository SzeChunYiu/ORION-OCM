# Architecture emergence — corrected AEM-1–7

**Conditional selection, exact finite constructions and evidence boundaries.**
The [original PR575/576 files](raw/pr575576-ef5be973/SOURCE_BINDINGS_V1.json)
remain byte-exact. This is an application of existing ARCH and MSC results,
not a new architecture or general optimization theory.

## Parents and selection interface

[Formal ARCH1–5](../gmi-formal-derivation-v1/ARCHITECTURE.md), unchanged at
formal1858, separates behavior, joint profiles, attainment and compilation.
[MSC1–3](../gmi-grand-unification-v1/CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md)
already supplies nonempty constructive coverage, complete fibers and common
approximate witnesses. The mature bounded-optimality parent is
[Russell, §§3–6](https://people.eecs.berkeley.edu/~russell/papers/aij-cnt.pdf):
selection depends on the environment, performance measure and machine.
The compatible-completion criterion below makes the overbroad AEM wording
precise; these parent mechanisms are inherited.

## AEM-1 — definition, identification and selection are distinct

Fix the candidate/development class, obligations and resource order.
A candidate denotes one implementation with its schedule; all profile
coordinates must come from that same candidate and schedule. Specify whether
they are expectations, pathwise bounds or other fixed statistics. Acquisition,
synthesis, verification and deployment are charged in the declared boundary.
Let A be the adequately feasible reachable set and pi(a) its finite real vector.
We minimize the product order: q strictly dominates p iff q<=p and q!=p.

Selection is M={a in A: pi(a) in Pareto(pi(A))}, not necessarily one machine.
Fix a label map lambda for the claimed partition of realizations and write
L={lambda(a):a in M}. For overlapping architectural properties instead ask
whether every a in M satisfies the specified predicate; a single-label
partition is a scoped convenience, not a required physical taxonomy.

A declared mathematical selection has a referent even when unknown or
uncomputable. Coverage evidence is needed to warrant extension to an additional
population, not to define a smaller problem. Missing data need not change
selection; representability alone does not select.

## AEM-2 — constructive profile closure and full fibers

Let C be a finite nonempty set of actual feasible reachable constructions.
Suppose pi(C) subset pi(A) subset N, with N a sound necessity relaxation in the
same ordered space, and every n in N weakly dominated by some pi(c), c in C.
Then

    Pareto(pi(C)) = Pareto(pi(A)) = Pareto(N) != empty.

Proof. A finite nonempty profile set has a minimal point (minimize the sum).
For any intermediate P with pi(C) subset P subset N, a minimal p in P is
weakly dominated by c in pi(C), forcing equality. Conversely, a strict
P-dominator of a minimal c would itself be weakly dominated by some c' in
pi(C), contradicting minimality. This proves equality and nonemptiness.

This identifies profiles, not a unique label. Collect **all actual fibers**
at those profiles. Label f is uniquely derived iff M is nonempty and all its
members have label f. For differently labelled a,b with pi(a)=pi(b)=(1,1),
C={a} satisfies coverage but neither single label is universally derived.
Given finite A with decidable exact rational profiles, enumerate its complete
frontier, fibers and labels. Infinite coverage remains a mathematical premise.

## AEM-3/4 — what missing information actually prevents

Let W be a nonempty set of complete models compatible with available evidence.
Each w supplies A_w, profiles and the same candidate identity/label interface;
write M_w and L_w for the selected realizations and labels.

**Identification criterion.** The label set is identified iff L_w is identical
for every w. A uniquely derived label f requires L_w={f} in every world.
A common optimal construction exists iff intersection_w M_w is nonempty.

Proof. Distinct compatible answers cannot be distinguished from the supplied
evidence. Conversely, constancy defines one set-valued answer. The remaining
clauses expose the required nonemptiness and common-witness quantifiers.
A finite W of finite rational registers makes all three tests exact by
enumeration; the algorithm does not discover W or certify physical coverage.

The old five-item list names possible failure mechanisms, not five independent
coordinates or universal vetoes. Missing coverage, development, preferences,
causal evaluation or tight costs **can** alter L_w. They need not: an unknown
rival cost in [2,3] cannot defeat a fixed feasible cost0 witness. Adding an
unknown dominated candidate or changing only its reachability also leaves
that winner fixed. Prove constancy over the compatible set rather than
requiring information irrelevant to its selected answer.

The inherited negative witnesses remain valid when they change selections:
costs(18,16) versus(18,20) share lower bounds(18,14) but reverse the winner;
opposite adequacy orders can select opposite actions on the same dynamics.
Unknown causal effects alone are not a selection counterexample unless the
uncertainty changes the relevant optimum.

## AEM-5 — size transport requires its cost contract

A verdict at one size supplies no general verdict at another by itself.
[The evidence correction](EVIDENCE_AND_TRANSPORT_CORRECTION_V1.md) repairs
the imported lower-bound-to-exact-crossover inference. Hypothetical exact
costs X_n=3n+2 and D_n=2n+7 differ by n−5, giving a crossover at5.
A mere native lower bound2n+1 supplies only D_n>=2n+7; it cannot prove a
tie or cheaper delegation. Formula evaluation is not a native measurement.
A proved size-uniform ordering is a positive transport certificate, not a
falsifier of the statement that transport needs a warrant.

## AEM-6 — a common constructive selection certificate

For this certificate, selection means argmin of a declared scalar objective J.
A scalar-family verdict does not automatically cover the whole product-Pareto
frontier: profiles(0,2) and(2,0) are both Pareto, but J(x,y)=2x+y selects only
the former. Retain the selected order in every reported family conclusion.

Suppose one common adequately feasible reachable candidate a of label f exists
in every compatible model, with J_w(a)<=U. Every other-label candidate in the
entire claimed universe has J_w(b)>=L>U. Then every attained global minimizer
has label f. If all A_w are finite nonempty with exact finite objective values,
minimizers exist and f is uniquely derived.

Proof. Candidate a supplies nonemptiness and beats every other-label candidate.
Finite enumeration supplies attainment. If every f-candidate additionally has
J_w>=ell, then 0<=J_w(a)−inf_b J_w(b)<=U−ell. This yields a common executable
approximation; exact common optimality still needs equality or another proof.
This is MSC3 with its original coverage, adequacy and cost premises.

For fixed finite nonempty A, Pareto selection exists. For a scalar objective,
strict increase under strict product domination makes Pareto pruning safe.
The Pareto order does not itself choose a scalarization or tie convention.
Evaluating/enumerating candidates consumes resources; decidability alone
does not establish economical physical synthesis.

## AEM-7 — feasibility, attainment and sampled failure

Empty A means no adequately feasible reachable realization in the declared
class. Nonempty A can lack a selected realization or an exact minimum:
costs1/n for n>=1 have infimum0 and no minimizer. Given eta>0, integer
n>=1/eta gives a witnessed eta-approximation; zero tolerance needs more.
This is an algebraic infinite example, not a finite-prefix inference.

A fully specified finite class whose every reachable member fails the exact
obligation is infeasible. A finite failed archive is not such a coverage proof.
A constructive repair can verify an adequate reachable candidate, justify an
additional development edge, or admit a certified approximation; each changes
the declared problem transparently. Finite reachability requires all relevant
development states/edges; its helper does not price or validate that graph.

In B6, incidence, DENSE→GRAD adjacency and an outgoing-edge count establish
neither trained-family ceilings nor causal failure explanations. The bound NAR
control changes parameter and response8→7 with **no outgoing GRAD edge**.
It verifies a state-update channel, not general learning or a campaign result.
Saved-cell failures remain observations of that saved cohort.

[Finite controls](test_architecture_emergence_v1.py) challenge full fibers,
compatible worlds and exact domination; [evidence controls](test_aem7_capability_v1.py)
read immutable NAR/census records. No new VM, search, training, ecology or
timing experiment is run, and no grand checker or aggregate is modified.
