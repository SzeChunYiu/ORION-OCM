# Finite-vector scalarization boundaries V12

Read FREEZE_V12.md first. The original target is GMI2-R2-006, not a unique
universal weighting or a complete intelligence measure. The results below are
classical order/scalarization mathematics, credited in PARENTS_V12.json.

## Definitions and scope

Let I be any finite index set, including the empty set. A vector x is a
function I→R, where R is the real numbers. All arguments also hold in a
linearly ordered commutative ring: a commutative ring with 0<1, total order,
addition preserving order, nonnegative products nonnegative, and products of
two positive elements positive. These are scalar algebra/order premises,
not assumed vector monotonicity, separation or scalarization conclusions.

Write x<=y for ∀i,x_i<=y_i, and w>0 for ∀i,w_i>0. Define
L_w(x)=sum_i w_i*x_i. Empty sums are zero. Finite distributivity gives
L_w(y)-L_w(x)=sum_i w_i*(y_i-x_i). Define |a|=max(a,-a);
then |a|>=0 and |a|+a>=0 by total order and translation invariance.
Vectors are incomparable when neither x<=y nor y<=x. In minimization,
y strictly dominates x when y<=x and y≠x. These conventions fix all signs.

## T1 — nonnegative scalarization preserves coordinate order

**Assumptions.** Finite I, the scalar laws above, x<=y, and every w_i>=0.
**Dependencies.** Finite distributivity and finite sums of nonnegative terms.
**Falsifiers.** An admitted input with x<=y but L_w(x)>L_w(y).
**Strongest parents.** Boyd–Vandenberghe [BV] §2.6.1 Example2.23 and §2.6.2,
printed pp52–53; specialization of nonnegative-orthant dual order.

For each i, y_i-x_i>=0, so w_i*(y_i-x_i)>=0. Inductively, a finite sum of
these terms is nonnegative: the empty sum is zero, and adding a nonnegative
term preserves nonnegativity. The displayed score-difference identity gives
L_w(x)<=L_w(y). No feasibility, convexity or probability premise is involved.

## T2 — a positively weighted strict improvement stays strict

**Assumptions.** T1's premises and some k∈I with x_k<y_k and w_k>0.
**Dependencies.** T1's nonnegative summands; strictly positive multiplication.
**Falsifiers.** Those premises with L_w(x)>=L_w(y).
**Strongest parents.** [BV] §4.7.4, printed p178, strict positive-dual pairing
in the proof that scalar minimizers are Pareto efficient.

The k-th difference term is positive. The sum of all other terms is
nonnegative by the finite-sum argument, hence the full difference is
positive. Therefore L_w(x)<L_w(y). If all weights are positive and x<=y
with x≠y, function extensionality and total order provide such a k. Thus
strict Pareto domination is preserved even when some coordinates are equal.

## T3 — the positive-weight family recovers exactly the coordinate order

**Assumptions.** Finite I and the declared scalar laws; quantification is over
ALL strictly positive vectors w in R^I, not a finite sampled weight list.
**Dependencies.** T1, finite distributivity, absolute-value bounds above.
**Falsifiers.** A pair outside coordinate order for which every positive
weighted comparison agrees with that order; or a nonpositive claimed witness.
**Strongest parents.** [BV] §2.6.2–§2.6.3, printed pp53–55, dual order and
strictly positive separating comparisons. The following division-free witness
is an elementary adaptation; no new separation principle is claimed.

We prove x<=y iff ∀w>0,L_w(x)<=L_w(y). The forward implication is T1.
If x<=y fails, choose k with d_k=x_k-y_k>0. Let
S=sum_{i≠k}|d_i|, w_k=S+1, and w_i=d_k for every i≠k.
S>=0 makes w_k>0, and all other weights are positive by the chosen k.
Also S+sum_{i≠k}d_i=sum_{i≠k}(|d_i|+d_i)>=0. Distributivity yields
L_w(x)-L_w(y)=w·d=d_k*(1+S+sum_{i≠k}d_i)>=d_k>0.
The weak inequality follows by multiplying a nonnegative excess by d_k;
the last inequality is the chosen coordinate gap. This contradicts the
universal weighted comparison, proving the reverse implication.

This construction uses no division, completeness, continuity or Archimedean
axiom. It applies to arbitrary real vectors and integer vectors alike. When
I is empty all vectors are the same function and both sides of the iff hold;
there is no coordinate to separate and none is falsely asserted to exist.

## T4 — every incomparable pair admits opposite positive rankings

**Assumptions.** Finite I, the scalar laws, and incomparable x,y.
**Dependencies.** T3's explicit separator applied to x-y and to y-x; T1.
**Falsifiers.** Either returned vector has a nonpositive coordinate or fails
its advertised strict ranking; opposite rankings for a dominating pair.
**Strongest parents.** [BV] §4.7.5, printed pp182–184, trade-off comparisons
and relative weights; original R2's two-coordinate reversal is a special case.

Failure of x<=y supplies k with x_k>y_k, and failure of y<=x supplies l
with y_l>x_l. T3's construction at k gives u>0 and L_u(x)>L_u(y).
Apply it to the reversed difference at l to obtain v>0 and L_v(x)<L_v(y).
Conversely such opposite rankings imply incomparability: x<=y contradicts
the u-ranking by T1, and y<=x contradicts the v-ranking. Thus this is an
exact characterization, not just one preselected two-dimensional example.
Equal vectors cannot meet its premises or conclusions.

## T5 — one total scalar cannot reflect an incomparable order

**Assumptions.** A domain D with an incomparable pair x,y, and a scalar
codomain S whose comparison is total. Reflection means f(a)<=f(b) implies
a<=b for every a,b∈D. No continuity or linearity assumption is needed.
**Dependencies.** Total comparison and the definition of incomparability.
**Falsifiers.** A map satisfying reflection on both orientations of an
incomparable pair into a total scalar order.
**Strongest parents.** Elementary partial-versus-total order logic, used in
[BV] §4.7.3–§4.7.5's distinction between Pareto and scalar comparisons.

For any f:D→S, totality gives f(x)<=f(y) or f(y)<=f(x). Reflection would
give x<=y or y<=x, respectively, contradicting incomparability. If scalar
values tie, both comparisons hold and both reflected conclusions fail; ties
do not evade the argument. This does not prohibit monotone scalar maps or
lossless arbitrary encodings without the claimed order-reflection property.

## T6 — an attained positive-weight minimum is Pareto efficient

**Assumptions.** F⊆R^I is any feasible vector set; w>0; x∈F; and
L_w(x)<=L_w(y) for every y∈F. The minimum is explicitly assumed attained.
**Dependencies.** T2 and the definition of strict Pareto domination.
**Falsifiers.** Such an attained minimizer with a distinct y∈F satisfying y<=x.
**Strongest parents.** [BV] §2.6.3, printed p55, and §4.7.4, printed p178;
this is the standard scalarization sufficient condition.

Suppose y∈F, y<=x and y≠x. Some coordinate is strictly smaller, and its
weight is positive. T2 yields L_w(y)<L_w(x), contradicting minimality.
Hence no such y exists. This proves efficiency, not uniqueness, existence
of a minimum, or recovery of every efficient point. Convexity is unnecessary.

## Boundary countermodels

**Assumptions.** Exact real/integer coordinates with the displayed weights
and minimization convention; this section attacks weakened hypotheses.
**Dependencies.** Direct arithmetic; T1–T6 specify which converse is invalid.
**Falsifiers.** Reversed arithmetic in any witness, or a positive weight
selecting the unsupported point in the final example.
**Strongest parents.** [BV] §4.7.4 pp178–180 and Figure4.9; original R2
reversal witness. The concrete integer examples are transparent calibrations.

A negative weight -1 sends 0<1 to 0>-1, so T1 needs nonnegativity.
Weights (0,1) give equal scores to (0,0) and (1,0); T2 needs positive
weight on a strict improvement. Incomparables (1,0),(0,1) score 2>1 under
(2,1) and 1<2 under (1,2), reproducing the original declared witness.

For F={(0,3),(2,2),(3,0)}, (2,2) is efficient: the first alternative has
larger second coordinate and the second has larger first coordinate. If
positive weights (a,b) selected (2,2), comparison with the other two points
would require 2a+2b<=3b and 2a+2b<=3a, hence 2a<=b and 2b<=a.
Adding gives a+b<=0, contradicting a,b>0. This proves nonselection over
ALL positive weights, not just a sampled grid. No convex converse is asserted.

## Evidence boundary

The proofs above establish the real-vector statements in full and explicitly
identify the scalar laws used for the ordered-ring generalization. Consult
FORMAL_SCOPE_V12.md for the actual Lean theorem domains and declarations.
A generic proof is conditional on its scalar-law interface; its concrete Int
instance does not instantiate the reals inside Lean. Any real interpretation
not constructed there remains a paper specialization, never a kernel claim.
Exact executable arithmetic and finite enumeration calibrate implementations;
they do not establish universal quantifiers or replace the mathematical proof.

Only GMI2-R2-006 is eligible for successor closure under the independent
adjudication. Choosing a weight remains additional declared information;
T3's family does not choose it. R2-007, nonlinear aggregation and V5's correction
of the measure-only assertion remain separate. No probability prior, empirical
prediction, architecture recovery or full GMI closure is earned.

[BV]: https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf
