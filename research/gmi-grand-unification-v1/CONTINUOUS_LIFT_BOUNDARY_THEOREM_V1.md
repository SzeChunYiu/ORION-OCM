# Grand GMI Continuous Lift Boundary Theorem V1

Status: **V2 SCOPE REPAIR; CONSTRUCTIVE EPSILON AND ENCLOSURE CERTIFICATES**
Date: 2026-09-13. Current evidence is
`GRAND_GMI_CONTINUOUS_LIFT_BOUNDARY_RECEIPT_V2.json`; V1 is preserved unchanged.

## 1. Corrected transfer statement and parent mechanisms

Order-theoretic bounds, exact attainment, effective approximation, measurable
representation and physical calibration are different obligations. Neither a
finite example nor a Boolean declaration can establish all of them.

The parents are classical infimum/optimization and computable analysis.
[Loss, real-analysis problem 1](https://loss.math.gatech.edu/17SPRINGTEA/6337/HOMEWORK/practicemidtermsol.pdf)
gives the compactness/lower-semicontinuity attainment argument.
[Beeson, *Constructivity, Computability, and the Continuum*, pp. 4–6](https://www.cs.sjsu.edu/~beeson/Papers/ccc.pdf)
explains effective approximation and Specker/halting obstructions. We use
these established distinctions, not a new compactness or computability theorem.
Measurable selection is separately addressed in CL-5 below.

## 2. CL-1 — lower-bound transport is an order argument

Let F be a nonempty relaxed allocation set and a:F->R an accounting objective,
bounded below. For every admitted machine M require an allocation q_M in F
and the sound inequality a(q_M)<=c(M), with c the protected real resource cost.
Then

    L = inf_(q in F) a(q) <= a(q_M) <= c(M).

This proof needs neither finite cardinality, compactness, measurability nor
computability of L. It still needs allocation membership and sound accounting.
For vector accounts a monotone scalar valuation transports the corresponding
componentwise inequality. This does not turn a family-relative bound into an
unconditional global exclusion: competitive exclusion also needs an actual
retained comparator at the same task, valuation and joint feasibility scope.

The accounting premise may be proved for a mathematical model. A physical
application additionally needs justified calibration/error bounds connecting
that model to its instance. A field named measured_resource_contract neither
proves the inequality nor is a logical prerequisite to every abstract proof.

## 3. CL-2 — nonattainment allows constructive approximation

For A={1+1/n:n>=1}, inf A=1 and no member equals 1. Exact attained equality
at 1 is unavailable, but for every rational epsilon>0,

    N=max(1,ceil(1/epsilon)),    1 < 1+1/N <= 1+epsilon.

Thus a concrete epsilon-optimal construction always exists. This follows from
the infimum definition in general; the displayed formula supplies an effective
witness for this particular set. A cannot meet cost allowance b<=1; it can
meet every b>1. Against a competitor family with lower bound 2, the admitted
A member 3/2 supplies a strict exclusion margin 1/2 despite nonattainment.
V1's “no finite margin” and blanket inability to classify were false.

Compactness is sufficient with appropriate lower semicontinuity, not necessary:
x^2 on the noncompact domain R attains its minimum 0 at x=0. Compactness alone
is insufficient: on [0,1], set f(0)=1 and f(x)=x for x>0. Its infimum is 0
but is unattained because this objective is not lower semicontinuous at 0.

Attainment alone also does not imply tightness of a relaxed lower bound:
on {2,3}, the minimum 2 is attained, but a relaxed lower certificate 1 leaves
a positive gap. To certify exact tightness one needs both a sound lower
bound and an admitted construction with matching upper cost. Epsilon-tightness
instead requires their certified gap to be at most the declared tolerance.

Equal infima do not imply coexisting attained optima. A and B={1} share
infimum 1, but B strictly beats every A member. Nonattainment may itself be a
proved structural fact; it does not prohibit every epistemic/physical diagnosis.
Any particular classification must state whether it concerns attained minima,
infimal values, finite margins or a tolerance-level attainable region.

## 4. CL-3 — samples, effective descriptions and certified enclosures

For this tail, the first N members have minimum 1+1/N. These sample minima
strictly decrease while staying above 1. That is a fact about this ordered
example, not every infinite set or every enlarged sample. A sequence beginning
with its global minimizer can have a constant sampled minimum forever. Samples
supply feasible upper bounds; they supply global lower bounds only with an
additional exhaustive or analytic certificate.

An effective description alone does not give a uniform infimum algorithm.
Given machine e, define a computable rational sequence r_e(n)=0 if e halts
within n steps, and 1 otherwise. Its infimum is 0 if e halts and 1 if it never
halts. A uniform procedure computing this infimum within error <1/3 would
decide halting. This rules out a uniform infimum operator from such descriptions;
it does not assert that either individual number 0 or 1 is noncomputable.
Beeson's cited Specker construction also shows that an individual computable
bounded monotone sequence can have a noncomputable limit.

**Constructive revival.** Effective certified lower/upper enclosures suffice.
For f(x)=|x-1/3| on [0,1], the triangle inequality proves Lipschitz constant 1.
Let U_N=min_(0<=j<=N) f(j/N), with its explicit minimizing grid point. Every
x lies within 1/(2N) of a grid point, so

    L_N=max(0,U_N-1/(2N)) <= inf f <= U_N,
    U_N-L_N <= 1/(2N).

Both bounds and the feasible witness are computable exactly here. Choosing
N>=1/(2epsilon) gives a certified epsilon bracket. In a broader instance,
effective covering/modulus and evaluation-error bounds must actually be
provided. A declaration of effective_description is not a substitute for them.

## 5. CL-4 — underaccounting is the sound direction

A sound lower account may be smaller than real cost. On a singleton relaxed
instance, L=a=5/6 and c=4/3 give L<=a<=c and a valid transported lower bound.
Overaccounting instead breaks transfer: L=a=4/3 with c=5/6 yields L>c.
Allocation membership is independently essential: if F contains only accounted
value 4/3, a machine accounted at 5/6 does not belong to F even if c=1>=5/6.
One cannot use inf_F a=4/3 for that machine.

V1 subtracted 1/2 from 4/3 but retained the old lower bound 1. If the objective
on all tail members is changed from x to x-1/2, its infimum changes from 1 to
1/2. Falling below the old bound is not a refutation of sound underaccounting;
it changes the program whose infimum is being used. The checker now tests
valid undercharge, invalid overcharge and failed allocation membership separately.

## 6. CL-5 — declarations do not prove analytic or selector premises

Parsing the five historical Boolean fields is decidable. The parser now
returns DECLARED_UNVERIFIED or NOT_DECLARED; it licenses no mathematical result.
A true flag is neither an attainment construction, a matching lower/upper
certificate, an effective approximation modulus nor a measurable selector.
Admitted-operation declarations also require applicability and composition
hypotheses at the actual states. There is no universal one-field/one-result gate.

A set quotient by an equivalence relation always exists set-theoretically;
measurability or a representative selector is a further property. For a
concrete distinction, take the circle X=R/Z and E(x,y) iff x-y is rational
modulo 1. E is Borel, a countable union of closed rotation graphs. The jointly
Borel binary response kernel K(x,y)=delta_(1_E(x,y)) has row equivalence E:
equivalent x have identical rows, and y=x separates inequivalent rows.

There is no Borel representative selector constant exactly on E-classes.
If s were one, its range V={x:s(x)=x} would be Borel. The countably many
rational rotations of V are disjoint and cover X. Translation invariance and
countable additivity would force their common measure either to sum to zero
or to exceed 1, a contradiction. This is the classical Vitali argument;
[MIT's Vitali theorem material](https://openlearninglibrary.mit.edu/courses/course-v1%3AMITx%2B24.118x%2B2T2020/courseware/58ba76c828904fc3b3498b5dae07bd8c/8aeb80ed1f3b40da8ca7dfae09276a3b/)
is the measure-theoretic parent. The response index y here is uncountable;
this counterexample is not asserted for every finite/countable-test model.

For the admitted finite response tables, a positive construction is immediate:
map each row to its least equal-row index. This representative is idempotent
and identifies exactly equal rows; on finite discrete spaces it is measurable.
The checker verifies that construction on all 64 binary three-row/two-column
tables. It does not numerically establish the infinite non-selector theorem.

## 7. Evidence and remaining work

The V2 checker verifies 256 rational epsilon constructions, 64 Lipschitz-grid
brackets, accounting-direction controls, matching versus unmatched finite
certificates, 32 late-halting prefix controls, all 32 Boolean declarations and
64 finite selectors. The halting reduction and Vitali obstruction are analytic
proofs; finite countdown/loop examples are controls, not undecidability tests.
No physical continuum or substrate was measured. Instance-specific analytic
proofs can discharge mathematical premises; empirical interpretation still
needs its own evidence. Continuous/quantum realization and effective general
selection are not closed by these rational witnesses or schema validation.
