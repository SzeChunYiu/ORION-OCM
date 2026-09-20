# Actual contexts, order maps and viability — V17

Authority: freeze026149d1eb10cba521c5be2911dd8dd17c1e0d04.
Notation: a V15 Context consists of E:H→Prop, ν:{h|E(h)}→W and a preorder≤W.
Admission P:H→Prop remains independent. Observable histories lie in D=P∩E.
Observe returns illegal when ¬P, undefined when P∧¬E, otherwise value(ν(h)).
Each assertion below is general mathematics under its stated premises.
FORMAL_SCOPE_V17 and the typed receipt determine its exact kernel realization;
finite tests and concrete Int examples do not by themselves prove Real claims.

## Q1-A — postcomposition and duals

Assumptions: declared source/target preorders and a total codomain map f:W→Z.
Dependencies: V15 Context/Outcome and elementary preorder definitions.
Falsifiers: constant monotone maps lose comparisons in the reverse direction;
injective monotone maps need not reflect order; nonmonotone maps can reverse it.
Strongest parents: V15 partial contexts; Stacks002Z Definition4.21.1.

Define f_*κ=(E,f∘ν,≤Z). This is a Context because≤Z is a preorder.
Define Outcome.map f to fix illegal/undefined and send value(w) to value(f(w)).
Case analysis on P and E proves observe(P,f_*κ,h)=Outcome.map f(observe(P,κ,h)).
Thus P/E are preserved separately, including evaluator values on illegal histories.
For identity f, evaluation is unchanged; for g:Z→Y, (g∘f)_*κ=g_*(f_*κ).
These equalities include the declared final preorder, not an arbitrary new order.

If ∀a b,a≤Wb→f(a)≤Zf(b), each active comparison survives postcomposition.
If ∀a b,f(a)≤Zf(b)→a≤Wb, the converse survives. Both together give equivalence.
A constant map on the two-element chain is monotone but loses its strict pair.
Identity from a two-element equality preorder to its chain order is injective
and monotone, yet the target's0≤1 has no source comparison. Injectivity is
therefore insufficient. Swapping0/1 on that chain witnesses nonmonotonicity.

Define the dual order a≤opb iff b≤a. Reflexivity is inherited; transitivity
uses source transitivity in reverse order. Keep E andν unchanged in the dual
Context. Active comparisons reverse and every observable value/tag stays the
same. Dualizing twice returns the original relation, E and evaluation.

## Q1-B — two different product domains

Assumptions: a finite index type and declared component preorders/evaluators.
Dependencies: Q1-A notation and V15 domain restriction.
Falsifiers: default-filled missing components; dropping E in a shared empty
product; retaining E in an empty independent product whose intersection is True.
Strongest parents: standard product preorders; immutable V15 Context.

For a common E andνi:E→Wi, define values (νi(h))i with pointwise order:
u≤v iff∀i,ui≤ivi. Reflexivity/transitivity hold at each coordinate.
The product Context retains E. Its observations are illegal for¬P, undefined
for P∧¬E, and the actual value tuple otherwise. Projections are monotone and
jointly reflect comparison: tuple comparison is exactly all coordinate comparisons.
For no coordinates there is one tuple and all value comparisons hold, but
shared E still determines whether an admitted history has any value at all.

For independent Contexts κi, instead set Eprod(h):=∀i,Ei(h), and define the
component value using the corresponding membership proof. Again this yields a
Context. The product is illegal exactly when¬P; for P it is undefined exactly
when some component is undefined (classically), otherwise it has the tuple.
On the product's domain, projections recover the component values/comparisons.
A component may have a value when the product does not: no stronger tag-equality
claim is made. An empty independent family has Eprod=True, so each admitted
history has its empty-tuple value. This differs from the shared-domain convention.
Neither construction invents a value for a missing component.

## Q2 — actual codomain specializations

Assumptions: externally declared evaluators on E and the orders specified below.
Dependencies: Q1, V15 Context; standard Int/Real order for the respective instance.
Falsifiers: scalarizing a Pareto pair, reversing cost orientation silently,
accepting empty uncertainty values, or confusing information precision with truth.
Strongest parents: elementary preorder/product/dual constructions, V15, V12.

Utility: take any declared ordered scalar W and actual u:E→W. The record
(E,u,≤W) is a Context. Int supplies a concrete instance; the same construction
with ordinary Real order is the mathematical Real specialization, not an
assertion that a new Lean Real instance has been constructed.
Acceptance: use Bool with a≤b iff a=false or b=true. Checking the four pairs
proves the preorder and a≤b iff e(a)≤Int e(b), where e(false)=0,e(true)=1.
Thus actual0/1 embedding preserves and reflects all acceptance comparisons;
it does not derive which histories should be accepted.

Vector utility: use finite tuples of declared ordered components and their
pointwise order. This is Pareto comparison, not another process primitive.
For ordinary two-dimensional utility, (1,0) and (0,1) remain incomparable.
Vector burden uses the same coordinatewise numerical order as a burden order.
If larger preference means better and lower burden is better, explicitly use
the dual: a≤preferenceb iff∀i,bi≤ai. Coordinate inequalities prove all laws;
no weighted sum or total ranking is selected. Zero-dimensional value vectors
all compare, with definedness governed by Q1-B's chosen domain convention.

Uncertainty: let U be a possibility type and W={A:U→Prop|∃u,A(u)}.
Define A≤precisionB iff∀u,B(u)→A(u). Reflexivity is implication identity;
transitivity is implication composition. Any actual e:E→W gives a Context.
For example {a,b}≤precision{a}, while {a} and {b} are incomparable if a≠b.
Nonemptiness excludes an inconsistent empty possibility set; if U is empty,
no such value exists, rather than a default value being manufactured.
Precision can be wrong: narrowing to {a} says nothing about whether reality is a.
No probability law, frequency calibration, confidence level or coverage theorem
follows from the order. All specializations preserve independent P/E and tags.

## Q3-A — greatest safe postfixed set

Assumptions: any X, K:X→Prop, R:X→X→Prop. R advances one discrete time step.
Dependencies: powerset order and ordinary predicate reasoning, not compactness.
Falsifiers: a safe deadend, an inserted identity self-loop, or replacing an
existential successor by a universal condition over all nondeterministic successors.
Strongest parent: Tarski1955 Theorem1, powerset greatest-fixedpoint specialization.

Put T(A)(x)=K(x)∧∃y,R(x,y)∧A(y), and V(x)=∃I,I(x)∧I⊆T(I).
If A⊆B, a witnessing successor for T(A) witnesses T(B); hence T is monotone.
Every postfixed I is contained in V by its own witness. For x∈V, choose its
witness I: postfixedness gives K(x) and a successor y∈I⊆V. Therefore V⊆T(V),
and V⊆K. By monotonicity T(V)⊆T(T(V)), so T(V) is itself postfixed and hence
T(V)⊆V. Thus V=T(V) and V is the greatest postfixed set and greatest fixedpoint.
No choice principle is needed for this predicate-level proof.

R is not the set of all category morphisms or a reflexive reachability closure.
A category identity or empty path does not automatically advance time; a
self-loop counts only if explicitly present in R. With no outgoing transition,
a safe state is outside V; with an explicit safe self-loop it is in V.
A safe state with one safe-loop successor and one deadend can be viable.
The quantifier is existential controlled continuation, not robust safety against
an adversary choosing every successor. Dynamics and safety are declared inputs.

## Q3-B — infinite trajectories and actual viability contexts

Assumptions: Q3-A and classical choice for the forward trajectory construction.
Dependencies: greatest-postfixed property and recursion on Nat.
Falsifier: independent arbitrarily long finite trajectories without one infinite run.
Strongest parents: Tarski greatest postfixed principle; Coquelin–Martin–Munos
§I equation2 for the indefinitely-safe concept, with no continuous-time import.

If x∈V, the fixedpoint equation gives a successor within V for every z∈V.
Classical choice selects f:{z|V(z)}→{z|V(z)} with R(z,f(z)). Starting at x,
Nat recursion iterates f. Its projected trajectoryγ starts at x, stays in V⊆K,
and satisfies R(γn,γ(n+1)) at every n. If V is empty, this implication has no
starting x and requires no arbitrary inhabitant of X.
Conversely, given an infinite safe trajectory from x, let I be its range.
For z=γn, safety gives K(z) andγ(n+1) is an R-successor in I. Thus I is
postfixed, x∈I⊆V. This proves the infinite-run equivalence with its choice scope.

For an actual endpoint/state evaluator e:E→X, define b(h)=true iff V(e(h)).
Classical decidability supplies a Bool function even when it is not computable.
The record(E,b,Bool-order) is an actual viability Context. Observe uses P∩E:
illegal/undefined do not become failed viability and are not merged with false.
An executable finite implementation decides V only in its stated finite model.

## Q3-C — the horizon obstruction and finite computation

Assumptions: arbitrary branching for the obstruction; finite X for the algorithm.
Dependencies: Q3-A/B; elementary induction and finite pigeonhole reasoning.
Falsifiers: calling arbitrary finite-horizon intersection the general V, or
using safe reachability without a reachable safe cycle as an infinite-run test.
Strongest parents: classical fixedpoint/graph reasoning; direct countdown witness.

Take X={root}⊔Nat, K=X, and transitions root→n for every n and n+1→n.
There are no others. From root every finite number of transitions is possible
by choosing a sufficiently large n. An infinite run must choose some k at its
first step; induction forces state0 after k more steps, which has no successor.
So root has no infinite safe run and is outside V. For any countdown state the
same argument applies. In particular ∩n T^n(K) contains root but is not V.
This is why no finite-horizon interchange is used in the general proof.

For finite X of size n, A0=K and Ai+1=T(Ai) form a decreasing chain. Every
strict step removes a state, so after at most n strict decreases it stabilizes.
The stable set is fixed; every postfixed I⊆K lies in each Ai by induction,
so that set equals V. Independently, a state lies in V iff within K it can
reach a directed cycle: repeat the cycle for one direction; an infinite run
repeats a state by finiteness for the other. Singleton cycles need explicit loops.
A third exact oracle unions every safe postfixed subset. Agreement calibrates
the finite implementation; it does not establish the arbitrary-state theorem.

Only original R2-005 is adjudicated here. Parent mathematics remains classical.
No calibrated uncertainty, canonical objective, physical adequacy, continuous
viability approximation or complete machine-intelligence theory is inferred.
