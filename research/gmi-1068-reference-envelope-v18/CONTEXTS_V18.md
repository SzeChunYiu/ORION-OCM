# V18 — declared decision and resource contexts

This detail file completes [THEORY_V18](THEORY_V18.md). The primitive interface
is immutable V15: P:H→Prop is admission; a context has independent ambient
domain E:H→Prop and an evaluator on E into a declared preordered codomain.
observe returns illegal when ¬P, undefined when P∧¬E, and the evaluator value
when P∧E. A value on E outside P stays unobservable.

## R3-A — finite expectations and lower envelopes

Fix n and a probability vector w in R^n: every w_i≥0 and Σ_i w_i=1.
For v in R^n set e_w(v)=Σ_i w_i v_i. If v≤u coordinatewise, each product
w_i(u_i-v_i)≥0, hence e_w(v)≤e_w(u). For the constant vector k·1,
e_w(k·1)=kΣ_i w_i=k. Thus expectation is monotone and constant preserving.
For n=0 the sum is0, so normalization would require0=1: no such vector exists.
These statements use declared weights; no process law infers them.

Given a finite nonempty family Γ of such vectors, define l_Γ(v)=min_{w∈Γ}e_w(v).
The minimum exists by finiteness/nonemptiness. Choose a minimizer w* at u.
For v≤u, l_Γ(v)≤e_w*(v)≤e_w*(u)=l_Γ(u). Every expectation of k·1 is k,
so its minimum is k. When Γ={w}, the minimum is exactly e_w. No strict-order
reflection is implied; weights may vanish, and minima may collapse differences.

Let f:E→R^n be an actual profile evaluator. Construct scalar contexts on the
same E by e_w∘f and l_Γ∘f, with the usual Real order and caller-supplied P.
Directly expanding observe proves the three tag laws: illegal stays illegal,
undefined stays undefined, and only the value case is mapped by the aggregator.
A profile comparison at two active histories is preserved by the inequalities
above. No constructor extends E, changes P or replaces a missing value by zero.
These are generic declared context specializations, not additional ontological
primitives. Finite rational implementations and kernel scalar structures have
their own exact interpretations; neither alone mechanizes these Real statements.

The two Dirac vectors give l(v)=min(v_0,v_1). For v=(1,0),u=(0,1),
l(v+u)=1 while l(v)+l(u)=0. Thus lower envelopes need not be linear or
representable by one fixed expectation. A restricted coordinate family also
need not reflect pointwise order: retaining only the first Dirac vector cannot
distinguish(0,1) from(0,0). Complete-family claims require their quantified family.

## R3-B — conditional lower expectations need additional structure

Let states be AC,AD,BC,BD, with first-stage partition A={AC,AD}, B={BC,BD}.
Declare priors p=(1/2,0,0,1/2), q=(0,1/2,1/2,0). Both assign mass1/2
to each branch, so every conditional used below exists without a null-event rule.
For act X=(1,0,1,0), both prior expectations are1/2, so its ex ante lower
expectation is1/2. At A the two conditional expectations of X are1 and0;
at B they are0 and1. The lower conditional value at either branch is therefore0.
Every prior's expectation of these lower conditional values is0, contradicting
equality with the original ex ante lower expectation1/2.

The constant act Y=(1/4,1/4,1/4,1/4) has value1/4 ex ante and at both
branches. Ex ante lower expectation prefers X to Y, whereas conditional lower
expectation prefers Y at each branch. This is an actual preference reversal,
not merely an unequal formula evaluated on different acts.

Allow each branch independently to select its C or D conditional while retaining
branch masses1/2. The four resulting priors are
(1/2,0,1/2,0), (1/2,0,0,1/2), (0,1/2,1/2,0), (0,1/2,0,1/2).
Their lower expectation of X is0 because the last prior puts all mass on D.
The conditional lower values remain0, restoring equality in this example.
Taking the convex hull changes no linear lower expectation and provides the
usual convex rectangular completion; branch probabilities remain positive.
Y remains1/4, so both evaluation stages now prefer Y.

This finite calculation is not a theorem that arbitrary lower-envelope control
is dynamically consistent. Epstein–Schneider's result involves a filtration,
rectangular prior sets, specified updating and preference assumptions. No such
assumptions follow from the one-shot context constructor. Its theorem is a
parent comparison, while the four-state countermodel and repair are direct proofs.

## R4-A — free conversion is a preorder with a complete Bool family

Let C be a lawful category. Declare Free on its actual arrows, assume each
identity is free and that the composition of two composable free arrows is free.
Write a≽b iff there exists f:C(a,b) with Free(f). The identity witnesses
reflexivity. Given witnesses f:a→b and g:b→c, their actual composition with
its closure proof witnesses transitivity. No antisymmetry is inferred: two
distinct objects can freely convert in both directions.

For a target z set M_z(a)=true iff a≽z, with false<true. If a≽b and M_z(b)
is true, compose the witnesses to get a≽z, so M_z(a) is true. This is exactly
M_z(a)≥M_z(b); if M_z(b) is false the inequality is automatic. Conversely,
if this inequality holds for every target, choose z=b. The identity gives
M_b(b)=true, so M_b(a)=true and hence a≽b. Thus
    a≽b iff for every z, M_z(a)≥M_z(b).

These are actual total Bool contexts on H=C.Obj, E=True, with evaluator M_z
and standard Bool order. Complete recovery on the whole object set uses P=True.
For an independently supplied endpoint evaluator x:E→C.Obj, composition
M_z∘x instead gives a partial Bool context preserving P/E and all three tags.
The object theorem applies to its evaluated endpoints; hidden illegal/undefined
objects cannot be recovered from absent observations. Nondecidable Free may
require classical logic to define the Bool characteristic map; no effective
reachability algorithm for arbitrary categories is claimed.

With the ordinary order false≤true, a conversion improves the indicator in the
source-to-target comparison M_z(a)≥M_z(b). Reversing this inequality reverses
the represented relation. If an API uses ascending preference instead, it must
explicitly dualize the order; changing words cannot change the equation.

CFS2014 Proposition5.2 already proves this complete target-indicator family.
Its free sub-SMC framework additionally supplies tensor compatibility. Here the
category and free predicate suffice; a resource tensor, free/paid boundary and
physical interpretation remain external choices. The proof supplies a family
of monotones, not a unique scalar, additive monotone, resource cost or prior.
For a finite preorder, its thin category (one arrow exactly when related) with
all arrows free gives the exact finite model used by the calibration corpus.
