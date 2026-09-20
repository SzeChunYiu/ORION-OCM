# V20 guarded maps and partial-context transport

Use the preorder and downward-closure conventions of THEORY_V20.md.

## T2.1 — necessary and sufficient pruning law

Let F:X→Option Y between preorders. Its defined image is
F[A]={y | ∃x∈A,F(x)=some(y)}. Call F guarded-monotone when

    x≤x' and F(x)=some(y) imply ∃y',F(x')=some(y') and y≤y'.

This includes upward closure of the domain. Merely comparing two already
defined outputs is insufficient.
If C⊆A is cofinal, guarded monotonicity gives ↓F[A]=↓F[C]. Indeed, for
z≤y with F(x)=y and x∈A, choose c∈C with x≤c. The guard gives F(c)=y'
and y≤y', so z∈↓F[C]. The reverse inclusion follows from C⊆A.
This proof works for arbitrary A,C; it needs no finiteness or chosen global selector.

Conversely suppose that equality holds for every finite A and every cofinal
C⊆A. Given x≤x' and F(x)=some(y), choose A={x,x'} and C={x'}.
Reflexivity and the given comparison make C cofinal. Since y∈↓F[A], equality
supplies y'∈F[C] with y≤y'. A defined output of this singleton can only come
from F(x'), proving the guard. Thus testing preservation on all finite cofinal
prunings already characterizes preservation for all cofinal prunings.

## T2.2 — observable goals and exact exclusions

For subsets U,V of a preorder, ↓U=↓V iff every upward-closed goal G has
U∩G nonempty exactly when V∩G is nonempty. Forward: if u∈U∩G, equality
supplies v∈V above u, and upward closure gives v∈G; reverse the roles for
the other implication. Conversely, choose G=↑u to get a dominating element
of V for every u∈U, and similarly with U,V reversed. This gives both closure
inclusions. Combining this fact with T2.1 yields the same necessary and
sufficient guarded condition for preservation of all existential upward goals.

The statement does not preserve arbitrary singleton goals, universal safety,
probabilities, multiplicities, exact attainable sets or history identities.
Even a total monotone map can discard a dominated value relevant to a non-upward
goal. Goal semantics is part of the declared observation, not inferred from a
bare attainable set.

## T2.3 — composition

For guarded F:X→Option Y and G:Y→Option Z define H(x)=F(x).bind G.
Suppose x≤x' and H(x)=some(z). The actual bind gives y with F(x)=some(y)
and G(y)=some(z). Guardedness of F gives F(x')=some(y') with y≤y'.
Guardedness of G gives G(y')=some(z') with z≤z'. Thus H(x')=some(z'),
proving guardedness of the composite including its definedness premise.
Identity x↦some(x) is guarded. Iterating this argument covers every finite
sequence of guarded partial updates and its actual failure propagation.

## T2.4 — actual partial postcomposition of V15 Context

For context k=(E,ν,≤_W), a declared target preorder and any partial F:W→Option V,
define a new Context k' with

    E'(h) iff ∃he:E(h), ∃v,F(ν(⟨h,he⟩))=some(v).

Its evaluator returns the unique v in this equation. Functionality of F and
proof irrelevance make the value independent of the domain witness. Admission
P is exactly unchanged. Construction of k' requires no monotonicity of F;
guardedness is required for the pruning theorem about its values.

When not P(h), the new outcome remains ILLEGAL regardless of E'(h).
When P(h) and not E(h), it remains UNDEFINED. When P(h),E(h), and F(ν(h))
is none, it becomes UNDEFINED. When P(h),E(h), and F(ν(h))=some(v), it is
VALUE(v). Hence

    A_x(k') = F[A_x(k)]

for the same P and H_x: each side's witness is exactly a selected admitted
history with E and the displayed successful F equation. This derivation retains
ambient evaluations on illegal histories; it does not put P into the new E'.
The unchanged-E rule for V17 total postcomposition does not apply to partial F.
If F is guarded, T1's cofinal frontier or representative set can be substituted
before F while preserving downward outputs and existential upward target goals.

## Parent mapping

This is the partial-map, maximization-preorder specialization of monotone
Pareto operations and safe constraints. Geilen et al. require dominance-preserving
operators; Doyen–Raskin derive closed-set preservation from simulation. Here the
Option domain guard is explicit and its necessity is established by actual
two-point tests. These are parent-owned mechanisms, not a new mathematical claim.
