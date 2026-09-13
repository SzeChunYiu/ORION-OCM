# Constructive selection and attainment bridge — MSC-1–3

Status: **SCOPED SELECTION REPAIR AND SUFFICIENT CONSTRUCTIVE CERTIFICATE**
Date: 2026-09-13.

This corrects nonvacuous property/family selection in MS-2, FS-2, AR-1 and
FP-6, and separates interval exclusion from attained selection in FP-2/5.
The canonical master already preserves attainable sets and recognizes empty
Pareto sets. Its dependent property criteria had not propagated that boundary.

## MSC-1 — selection must exist before a property is derived

Let A be the adequately feasible reachable realization set, pi its finite
real vector of protected quantities to minimize, and
M* = {m in A: pi(m) in Pareto(pi(A))}.

A property P is Pareto-derived precisely when

    M* is nonempty and, for every m in M*, P(m).

The old universal predicate alone is insufficient. For adequate realizations
m_n with scalar cost pi(m_n)=1/n, n>=1, every m_n is dominated by m_(n+1).
Thus A is nonempty but M* is empty. Universal quantification over M* declares
both P and not-P true; neither is a realized architecture derivation.

Keep three boundaries separate: empty adequately feasible A means infeasible;
proved nonempty A with empty M* means NO_SELECTED_REALIZATION; unknown
attainment means unresolved evidence. A finite nonempty point-profile register
always has a Pareto point. A failed/partial selection procedure is not proof
of infeasibility. For evidence-robust claims the compatible evidence set W
must also be nonempty; inconsistent evidence licenses no universal verdict.

This is a correction to the operational meaning of "derived", not a claim
that universal quantification over an empty set is mathematically invalid.

MS-4's provenance sentence also required correction: holding every registered
object fixed cannot change a fixed mathematical selection, yet that invariance
does not make its proven properties inserted priors. Provenance requires an
entailment proof, not a counterfactual in which every derived invariant fails.

## MSC-2 — finite constructive coverage supplies an attained frontier

Suppose C is a **finite nonempty register of actual feasible realizations**
inside A. Prove the coverage condition

    for every a in A, there exists c in C with pi(c) <= pi(a).

Then

    Pareto(pi(A)) = Pareto(pi(C)) != empty.

No compactness of A is required.

Proof. A finite nonempty profile set has a Pareto point: choose a minimum of
the sum of all retained coordinates; any strict product-order dominator would
have a smaller sum. If p is Pareto in pi(A), coverage supplies c with pi(c)<=p,
so equality follows from nondominance and p is Pareto in pi(C). Conversely,
if p is Pareto in pi(C) and a in A strictly dominates it, coverage supplies
c in C weakly dominating a, contradicting nondominance of p in pi(C). QED.

This strengthens GG34's sufficient domination certificate by adding a finite
nonempty constructive register, which supplies the missing attainment.
It does not replace GG34's universal coverage premise by a finite search.

A useful noncompact exact sector is

    pi(A) = ((1,2) + R_+^2) union ((2,1) + R_+^2),

with feasible witnesses C at (1,2) and (2,1). Every profile is covered by its
branch's witness, and the frontier is exactly those two profiles. This can
model explicitly admitted nonnegative resource padding. It says nothing
about physical machines outside that proved candidate set.

### Complete fibers are still required

The selected realizations are ALL a in A with pi(a) in Pareto(pi(C)).
A good representative c does not make every equal-profile realization good.
A neural and a program implementation can share profile (1,1); if only the
neural representative is in C, coverage holds but neurality is not derived.

Therefore MSC-2 plus an architecture derivation additionally needs a proof
that every realization in each selected profile fiber has the property.
Alternatively, strictly dominate every counterproperty realization, while
MSC-2 supplies nonemptiness. Equal-profile competitors defeat strict exclusion.

For a finite registered A and decidable exact comparisons, compute the
frontier on C and collect its full fibers in A. Check coverage against the
entire declared A. For infinite A, supply a mathematical coverage map/proof;
the finite checker does not decide that universal premise.

## MSC-3 — interval exclusion yields an executable approximate witness

Fix a nonempty set W of compatible evidence worlds and a finite family
register containing A. The claimed candidate universe in each world is
exactly the union of those registered family sets; extending it requires a
separate coverage proof. J*_w below is the infimum over that union only.
Set min(empty)=+infinity if there are no rivals.
In every w in W let one **same registered feasible construction**
a in family A have cost

    L_A <= inf_{m in A_w} J_w(m) <= J_w(a) <= U_A,

where all bounds are finite real numbers. Every rival-family candidate has
cost at least its registered L_B, and

    U_A < min_{B != A} L_B.

An omitted candidate of cost 0 would defeat a claimed global lower bound
L_A=1 even when the registered A witness costs 1 and rival B costs 2.
Thus family coverage is an essential premise, not an empirical inference
from an interval comparison.

The common construction must satisfy adequacy/reachability in every world
on the claimed evidence event; separately existing witnesses do not supply
one implementable evidence-robust machine.

Then every rival candidate is strictly worse than a in every world, and the
global infimum J*_w equals the family-A infimum. Moreover,

    0 <= J_w(a) - J*_w <= U_A - L_A.

Proof. Rival costs exceed U_A, whereas family A contains a with cost at most
U_A. Hence no rival has a smaller infimum. The lower bound L_A applies to
the global infimum and subtracting it from the witnessed upper bound gives
the inequality. The left inequality is the definition of an infimum. QED.

Thus U_A-L_A <= eta certifies an implementable eta-suboptimal morphology
even if no exact optimum exists. A family interval containing an infimum
without a feasible upper-bound witness does not itself supply that machine.
Exact family selection additionally requires attainment of the minimum in
every evidence world. One common optimal machine is a still stronger claim.

### Explicit nonattainment and revival

Take A={m_n:n>=1}, J(m_n)=1/n, and rival B={b}, J(b)=2.
The intervals A:[0,1] and B:[2,2] strictly separate, and m_1 excludes B.
Nevertheless no optimal machine exists. Merely calling A the unique
selected family would promote an infimum into an attained optimum.

For any registered eta>0, choose an integer n>=1/eta. Then m_n has regret
1/n<=eta, and still beats B. The construction reaches the approximation
target; no finite n reaches zero regret. At eta=0 an attainment proof is
indispensable. This repairs the failed exact claim with a positive,
quantitative approximate guarantee rather than discarding the instance.

## Exact finite evidence and its boundary

grand_gmi_selection_attainment_checks_v1.py independently compares the
covering certificate against a sorted dominance scan over every A/C
registration on a six-point two-dimensional grid. It retains equal-profile
fiber counterexamples, empty-selection abstention, missing-coverage rejection,
interval ties, a finite sequence-extension diagnostic and a rational
approximate witness. The negative infinite example is proved above; checking
finitely many sequence elements is not a proof of infinite nonattainment.

The separate unittest file challenges malformed dimensions/numbers,
incomplete coverage and representative-only property claims. Receipts
certify these registered finite calculations only. No real resource law,
universal physical candidate enumeration or empirical family winner follows.

## Parent assimilation and contribution boundary

[Boyd and Vandenberghe, Convex Optimization, §4.1.3 and §4.7](https://www.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf) separates optimal value,
attainment and epsilon-suboptimal points, and treats vector optimization.
[de Weck and Willcox, MIT ESD.77 Lecture 14](https://live.ocw.mit.edu/courses/ids-338j-multidisciplinary-system-design-optimization-spring-2010/f091204b62ab5bb46825829fdedc66cd_MITESD_77S10_lec14.pdf)
supplies the standard dominance/Pareto-filtering parent.

MSC-1 uses ordinary nonvacuous existence. MSC-2 is finite-poset descent plus
the already corrected GG34 coverage proof. MSC-3 is the standard feasible
upper/lower objective-gap certificate. No novelty is claimed for those parent
results. The contribution is their precise propagation into GMI architecture
derivation, retaining full realization fibers and common evidence-world
witnesses, plus a constructive revival where exact selection is unattained.
