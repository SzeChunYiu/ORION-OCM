# Joint achieved-score niche frequency

This is an elementary correction of an applied inference, not a new probability
method. Read [source dispositions](SOURCE_DISPOSITIONS_V1.md) for the old claim.

## Parents and register

Probability monotonicity and the union bound give the event bounds below:
[MIT Laws of Probability, §2](https://courses.csail.mit.edu/6.042/past-devel/archive/spring03/handouts/lectures/lec2.pdf).
A marginal distribution is the pushforward of a specified law; it does not
determine the dependence between two measured quantities. These elementary facts
are applied faithfully. Existing AEM/FEE corrections separately require family
coverage/attainment and distinguish sample aggregates from population claims;
their exact texts are in raw/parents.

Let (Ω,μ) be a probability space with measurable achieved score S(e) and baseline
B(e), both in[0,1]. Fix0≤θ≤1 and0<δ≤1. Each pair refers to the SAME ecology,
scoring/intervention interface and deployed construction. Let
A={S≥θ and S−B≥δ}; F_B(t)=μ(B≤t). Scores may be rounded if that is the declared
interface; an unrounded MAE score is a different register. No independence,
unknown-dynamics, execution-provenance or empirical-validity premise is implicit.

## NFR-1 — The joint event is the frequency

The achieved construction's niche frequency is

    μ(A) = E[1{S≥max(θ,B+δ)}].

This identity is the definition of probability of the admissibility event.
Replacing S by a mean across other ecologies, a family label, or an unattained
supremum changes the event and is not licensed by that identity.

Even both separate marginals do not suffice. On two equiprobable ecologies, let
B=(0,1/2), S=(1/2,1), θ=1/2,δ=1/4: frequency1. Re-pair the same S marginal as
S=(1,1/2): frequency1/2. No data or marginal changes, only the pairing.

## NFR-2 — A uniform ceiling supplies an upper bound

If S≤c almost surely for a constant c∈[0,1], then

    μ(A) ≤ 1{c≥θ} F_B(c−δ).

Proof: A implies c≥S≥θ and B≤S−δ≤c−δ. If c≥θ, equality holds precisely when
the missing set {B≤c−δ}\A has probability0. Equivalently, baseline-eligible
ecologies must actually attain S≥max(θ,B+δ) almost surely.
The simple sufficient condition S=c almost surely recovers the exact CDF formula.

The upper bound can be strict, even0 versus1/2, for the same B and ceiling c:
B=(0,3/4), c=3/4, θ=1/2,δ=1/4, achieved S=0.
Using the admitted achieved S=c attains the bound. A historical mean is not a
uniform ceiling: a single observed score above it refutes that premise.

For a family supremum C(e), the same ceiling can bound an existential event.
It need not attain the boundary. Choose δ≤c≤1. On one ecology with B=c−δ and θ≤c, a family
of scores c−1/n (all valid for sufficiently large n) has supremum c but no
admissible member. Adding an admitted score c restores attainment. This is a
score-register countermodel, not a construction inside an unspecified native
family. Finite nonempty supplied families attain their maximum; general families
need the actual required same-task witness and measurable event/selection scope.

## NFR-3 — Quantitative approximation repairs the approximate law

Suppose G={|S−c|≤ε} has μ(G)≥1−γ, where ε≥0 and0≤γ≤1.
Without any independence assumption,

    L ≤ μ(A) ≤ U,

    L = max(0,F_B(c−ε−δ)−γ),  if c−ε≥θ; otherwise0.
    U = min(1,F_B(c+ε−δ)+γ),  if c+ε≥θ; otherwise γ.

Proof: when c−ε≥θ, G∩{B≤c−ε−δ}⊆A. Removing G can lose at mostγ mass.
On G, A implies B≤c+ε−δ; if c+ε<θ, A∩G is empty. Adding G's complement
costs at mostγ. Threshold equality uses ≥: c+ε=θ belongs to the first U case.
If ε=γ=0, this reduces to the constant-achieved-score identity with its θ gate.

Bounds are attainable on finite examples. With θ=1/2,δ=1/4,c=3/4,ε=1/4,γ=0
and B=(1/4,1/2), S≡1/2 attains L=1/2; S≡1 attains U=1.
The γ term is necessary: mass1/4 at(B,S)=(0,1), mass3/4 at(1,0), c=ε=0
gives frequencyγ=1/4 despite c+ε<θ.
An unspecified word such as “roughly” supplies neither ε nor γ. A finite sample
deviation bound does not by itself supply a population approximation guarantee.

## NFR-4 — The declared finite-grid baseline is computable exactly

For the NEW analytical register, choose k uniformly from{-8,…,8}^4, with no
rejection; there are17^4=83521 tuples. Use all16 Boolean inputs and the source
target y_k(x)=Σ_i k_i x_i in fixed-point integer units. Its coefficients are k/16.
All sums lie in[-32,32], inside the source's unsaturated[-128,127] interval.
Dyadic arithmetic is exact here. Singleton inputs give y_k(2^i)=k_i, so the full
target map is injective. Uniform tuples therefore induce uniform DISTINCT FULL
target functions on this image. A generic many-to-one warning would be wrong here.
This does not imply that baseline values themselves are uniformly distributed.

The unseen inputs have odd parity: four singletons and their four complements.
Writing T=Σ_i k_i, their targets pair k_i with T−k_i. For any integer constant a,

    Σ_{x unseen}|a−y_k(x)| ≥ D(k) := Σ_i |T−2k_i|.

The pairwise triangle inequality proves the lower bound. Every pair's interval
between its two integer endpoints contains floor(T/2), so that same integer
attains all four pair bounds. It is an admitted constant. Thus the exact best
unrounded constant capability is B*(k)=1−D(k)/192. Each |T−2k_i|≤32, so D≤128<192;
so the source's zero floor does not change this optimum.

This is the standard median/L1 minimization parent, also described by
[Boyd–Vandenberghe, Example8.4](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf).
The executable second oracle explicitly scans all49 constants[-24,24] against
the eight directly generated targets, without using the pair formula. All target
values on those inputs lie in[-24,24]; moving an outside constant to that interval
cannot increase any absolute error. The scan therefore covers the original
integer constant optimum, including the wider source range[-128,127].

The complete histogram computes F_B* exactly. A lookup at reported c−δ is a
conditional projection under S≡c, not a new family-performance measurement.
No interpolation between quartiles is needed or justified for this discrete CDF.

## NFR-5 — Sample and population remain different registers

Twelve task rows determine their twelve-task empirical frequency. Neither108
cells nor six interventions per task create108 or648 independent ecology draws.
A deterministic seed and a prior Git document do not authenticate hidden exposure,
the executed sampler, independence, registry rejection or omitted retries.

Under genuinely iid uniform tuple proposals and rejection ONLY of a fixed known
registry R, accepted draws with repeats allowed have the conditional uniform law
on Ω\R. Rejecting accepted duplicates would instead be sampling without replacement.
Both need the exact sampler; Python documents that choice/choices/sample can
produce different seeded sequences:
[Python random](https://docs.python.org/3.12/library/random.html).
This unit does not identify that historical sampling law or attach a confidence
interval to it. The complete new grid CDF needs neither sampling nor confidence
bounds, but it measures B*, not the unknown achieved S population.
