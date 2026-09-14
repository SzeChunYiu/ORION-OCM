# ARC-6: countable adaptive creation and one global confidence event

Issue #655; parent ledger #602 M / #592 item 32. Date: 2026-09-14.

**Scope:** bounded scalar scores with a frozen conditional mean per created row;
countably many adaptively chosen row contracts, predictable sampling, arbitrary
finite attained visit counts. **Evidence:** P1 written proof, P3 conditional
probability bound, P2 exact numerical certificates and finite counterexamples.
**Claim ceiling:** G2 scoped mathematical mechanism, not G6 capability prediction.
There is no Lean/Coq proof of the general probability theorem in this unit.

## 1. Corrigendum and strongest parents

The [historical ARC-5 text](https://github.com/SzeChunYiu/ORION-OCM/blob/139a123d429d1a800f7fb3e071ec94d773630615/research/gmi-adaptive-creation-v1/ADAPTIVE_CREATION_AND_HORIZONS_V1.md)
contains three overclaims. They are retracted, not counted as negative discoveries:

| Historical claim | Correct statement / nearest counterexample |
| --- | --- |
| Every infinite sequence of positive row weights diverges. | For j >= 1, w_j=1/[j(j+1)] > 0 and sum_j w_j=1. |
| Diluted positive allowance imposes a nonzero limiting radius. | For every fixed j and alpha>0 the radius below tends to zero as its own visits tend to infinity. There is no uniform-in-j shrinking guarantee. |
| Overspending a union allocation proves all-method impossibility. | It invalidates that allocation's proof. Identical failure events have the same union probability no matter how often they are listed. Independent fixed-level errors, by contrast, accumulate. |

ARC-5a's finite-potential-register argument and ARC-5b(i)'s all-finite-sampling-
looks guarantee survive their premises. The old 11-test receipt is historical:
passing those tests did not prove the retracted general statements and does not
certify this corrected text. The frozen ARC-1–4 capsule is not modified.

The nearest internal parent is [ARC-1–4](../gmi-adaptive-row-confidence-v1/ADAPTIVE_ROW_CONFIDENCE_THEOREM_V1.md):
conditional Hoeffding supermartingales, attained-visit stopping and summable
error spending. ARC-6 supplies the missing countable birth-index argument and
an exact conservative scalar implementation. It claims no novel concentration
rate or new statistical paradigm. Stronger primary parents include:

- Howard, Ramdas, McAuliffe & Sekhon (2021), *Time-uniform, nonparametric,
  nonasymptotic confidence sequences*, Annals of Statistics 49(2), 1055–1080,
  [DOI 10.1214/20-AOS1991](https://doi.org/10.1214/20-AOS1991),
  [author manuscript, sections 1–2](https://arxiv.org/abs/1810.08240).
- Ramdas, Grünwald, Vovk & Shafer (2023), *Game-Theoretic Statistics and Safe
  Anytime-Valid Inference*, Statistical Science 38(4), 576–601,
  [DOI 10.1214/23-STS894](https://doi.org/10.1214/23-STS894).
- Dwork et al. (2015), *Generalization in Adaptive Data Analysis and Holdout
  Reuse*, [primary manuscript](https://arxiv.org/abs/1506.02629).
  Reusing a fixed holdout needs a separate valid mechanism; fresh post-birth
  sampling here does not implement their reusable-holdout guarantees.

## 2. Exact observation contract and quantifiers

Let (Omega,F,P) carry a discrete-time filtration (F_t) for all integer t>=0.
It includes every revealed outcome, controller choice and randomness already
used. Fix alpha in (0,1) before the campaign. Rows have unique, never recycled
creation indices j=1,2,... . Row j is born at a stopping time tau_j (possibly
infinite); only finitely many rows are born by any finite t. Its contract and
parameter mu_j in [0,1] are F_tau_j-measurable and frozen thereafter. The unknown
parameter can be a function of the adaptively chosen contract; it is not an
estimate selected after observing that row's future outcomes.

At step t>=1, select R_t from the already born rows or select no row, using
F_(t-1) only. If R_t=j, then tau_j<t and a score X_t in [0,1] is received with

    E[X_t | F_(t-1)] = mu_j    on {R_t=j}.

This conditional-mean premise is load-bearing. Global iid sampling, independent
row choices, and a finite potential set of row meanings are not required.
Nor does arbitrary dependence with only a fixed marginal mean suffice. Support,
score scaling, task law and evaluated object must be stable enough to justify
the conditional premise. A metadata field saying 'fresh' cannot prove it.

Define T_(j,n) as the time of row j's nth post-birth observation, possibly
infinite, and hat_mu_(j,n) as the mean of those n observations when attained.
No old observation is retrospectively assigned to a newly constructed row.
Register deterministic weights and per-look allowances

    w_j = 1/[j(j+1)],
    delta_(j,n) = alpha/[j(j+1)n(n+1)],  j,n >= 1.

A broader predeclared positive summable weight sequence also works; the code
implements this one exact sequence. The creation-order rule, not future row
names, is frozen in advance. Unused weights are not recycled.

## 3. ARC-6A: simultaneous countable-row theorem [P1/P3]

For every process obeying section 2, choose deterministic radii e_(j,n) in [0,1].
A radius of 1 is always valid; otherwise require

    2 exp(-2 n e_(j,n)^2) <= delta_(j,n).

Then the single event

    G = intersection over all j,n >= 1 of
        {T_(j,n)=infinity OR |hat_mu_(j,n)-mu_j| <= e_(j,n)}

satisfies P(G)>=1-alpha. The quantifier ranges over every finite attained visit,
not merely a finite set of looks or an iid sequence conditioned on being visited.

**Proof.** Condition on a finite birth history F_tau_j. After birth, set
S_t=sum_(tau_j<s<=t, R_s=j)(X_s-mu_j) and let N_t count these summands. For every
fixed real lambda, conditional Hoeffding's lemma for a [0,1] variable gives

    E[exp(lambda (X_t-mu_j)) | F_(t-1)] <= exp(lambda^2/8)

on selected steps. Hence M_t=exp(lambda S_t-lambda^2 N_t/8), initialized at 1
at birth and unchanged on skipped steps, is a nonnegative supermartingale.
Stop at the nth visit or m elapsed post-birth steps, whichever comes first.
The bounded stopping argument and conditional Fatou yield

    E[M_(T_(j,n)) 1{T_(j,n)<infinity} | F_tau_j] <= 1.

For the upper tail take lambda=4e. At an attained visit where S>ne,
M>exp(2ne^2); conditional Markov therefore bounds its joint probability by
exp(-2ne^2). Lambda=-4e handles the lower tail. Integrating over finite birth
histories bounds the unconditional joint failure probability by delta_(j,n).
If the row is never born or the visit never attained, it contributes no failure.
For e=1, failure is impossible by boundedness without a tail calculation.
Finally, countable subadditivity and telescoping give

    P(G^c) <= sum_j sum_n delta_(j,n)
           = alpha (sum_j 1/[j(j+1)]) (sum_n 1/[n(n+1)]) = alpha.

This proof never conditions attained prefixes to be iid. QED.

**Consequence.** On G every finite data-dependent stopping time, chosen row,
and comparison made solely from these simultaneously valid intervals can use
them together. Data-dependent transformations need their own deterministic
soundness argument but not an additional union over already covered choices.
No guarantee of eventual termination or eventual selection of every row follows.

## 4. ARC-6B: executable exact-radius certificate [P1/P2]

Let delta=delta_(j,n), n>=1. Let m be the least integer with 2*2^(-m)<=delta.
Let k be the least nonnegative integer with 2k^2>=mn, and set

    e_(j,n) = min(1, k/n).

If e=1 the interval is deterministically valid. Otherwise 2ne^2>=m and

    2 exp(-2ne^2) <= 2 exp(-m) <= 2*2^(-m) <= delta,

because exp(1)>2. Thus this rational grid radius satisfies ARC-6A. The code
uses integer bit lengths and integer square roots; its acceptance decision has
no floating-point logarithm, exponential or square-root rounding. The independent
certificate predicate checks the tail-budget and square inequalities, not merely
whether the certificate equals a regenerated object. QED.

For zero visits, report [0,1]. For n>0, clip [hat_mu-e,hat_mu+e] to [0,1].
For scores in a frozen [a,b], apply the theorem to (X-a)/(b-a); the original
radius is (b-a)e. A constant range needs no inference. Changing [a,b] after
outcomes is outside this contract.

## 5. ARC-6C: no fixed-row width floor [P1]

Fix any j>=1 and alpha in (0,1). Then

    m = ceil(log_2(2j(j+1)n(n+1)/alpha)) = O(log n),
    e_(j,n) <= min(1, sqrt(m/(2n))+1/n) -> 0.

The inequality follows from rounding k upward by less than one. QED. It asserts
a property of the deterministic radius as n increases, not that the sampler
will supply infinitely many visits. Arbitrarily large j can still have radius
1 at any fixed n. Adjacent rational-grid radii are not promised monotone.
The statistical penalty for row j grows logarithmically in j, not as a positive
limiting error radius. Count and arithmetic operand sizes grow with the bit
lengths of j,n,alpha; this is not a constant-memory infinite computation.

## 6. Counterexamples and exact boundaries

**Equal-level independent alarms.** If each newly created row independently
has failure probability p>0, the first J rows fail somewhere with probability
1-(1-p)^J -> 1. This refutes indefinitely reusing a fixed per-row confidence
level *in that construction*. It is not an impossibility theorem for all methods.

**Completely dependent alarms.** If every failure event is the same set A,
the union has probability P(A), even though sum_j P(A) diverges. This is the
nearest counterexample to treating a union-bound upper estimate as a necessary
lower bound. The summable allocation is a sufficient robust rule, not necessary
for every special dependence structure.

**Cached draw.** Draw Z~Bernoulli(1/2) once, then submit Z 1000 times. Both
possible records produce a tight interval excluding 1/2 if treated as 1000
fresh draws. After the first outcome, E[X_t|F_(t-1)]=Z, not 1/2. The premise
fails; the numerical certifier is not a data-authentication service.

**Post-selection and developmental changes.** A row chosen using its purported
scoring outcomes, an altered score function, a changed evaluated predictor,
an unaccounted drift in conditional means, or a reset/recycled identity cannot
inherit old samples under this theorem. Freeze a new contract and use a new
creation index with fresh post-birth evidence, or supply another valid theorem.

**Unlimited sampling is not unlimited deployment.** G covers all finite
sampling looks. It gives no sure safety, no nontrivial infinite-horizon risk
bound, no bound on an unbounded cumulative deployment cost and no empirical
calibration of a morphology/capability predictor. The finite-policy transfer
premises in ARC-2 remain separate. Uncountably many independently indexed rows
are not covered by this countable argument.

## 7. Verification, falsifiers and ledger disposition

`test_countable_rows_v1.py` has 24 controls: exact telescoping prefix/double sums,
integer inequalities, corrupt-certificate refusal, zero-visit/support boundaries,
fixed-row shrink and new-row non-shrink, independent and identical alarm events,
the cached-draw counterexample, exact binomial tail sums and the inherited
47/125 optional-monitoring counterexample. These are finite P2 checks; none is
advertised as an exhaustive proof over an infinite process.

A process satisfying section 2 with P(G^c)>alpha falsifies ARC-6A. An accepted
nontrivial certificate violating either integer inequality falsifies ARC-6B's
implementation. A fixed j,alpha with nonvanishing radius as n->infinity would
falsify ARC-6C. Invalid input acceptance or promotion of a cached draw to new
information falsifies the relevant operational claim, not the theorem's premises.

This unit supplies bounded-score mathematical evidence for #602 M's revisit,
adaptive-creation, all-finite-sampling-horizon, explicitly conditioned dependence,
and global-good-event requirements. It does not certify all real GMI decisions,
unknown model sufficiency, physical sampling, arbitrary drifting targets, or
any empirical G6/G7 claim. Further consumers must state how they discharge the
contract rather than treating the existence of this file as blanket approval.
