# Global adaptive inference

This unit proves simultaneous statistical validity for countably many adaptively born, repeatedly visited claims over an unbounded discrete horizon. It does not prove that a learned state, physical access model, or conditional observation law is correct. Those are premises to establish separately. [Examples and counterexamples](ADAPTIVE-EXAMPLES.md) delimit the result.

## A1. Global protocol and premises

Fix a probability law P and filtration (F_t) for t=0,1,... containing the **entire** shared observation, action, communication and randomization history. Decisions affecting observation t are F_(t−1)-measurable; any additional selection randomization is revealed before that observation. All variables, kernels and events below are measurable. There are countably many row versions j, each with stopping-time birth τ_j∈{0,1,...,∞}; τ_j=∞ means never born. Countably many births at one time are allowed with a fixed measurable enumeration.

On {τ_j<∞}, freeze the row's observable, estimand μ_j∈[0,1], law contract and error allocation 0<α_j<1 at birth. They are F_(τ_j)-measurable; “measurable” does not mean the numerical value of an unknown estimand is available to the implementation. For example μ_j=P f_j is a measurable functional of a randomly selected f_j under fixed P. If an unobserved random environment parameter is used instead, the stated law must hold in the filtration enlarged by that parameter; this is an additional premise.

Set α_j=0 for never-born rows and require Σ_j α_j≤δ almost surely, for fixed 0<δ<1. Assignments can depend on birth history, but an assignment is never retrospectively increased, refunded or reused. The deterministic schedule α_j=δ/[j(j+1)] is one admissible instance.

For t≥1, the indicator I_(j,t) of including observation t in row j is F_(t−1)-measurable, and is zero unless τ_j<t. On {I_(j,t)=1}, the observation X_(j,t) lies in [0,1], is F_t-measurable, and satisfies

    E_P[X_(j,t) | F_(t−1)] = μ_j.                         (A1)

Equivalently require E[I_(j,t)(X_(j,t)−μ_j)|F_(t−1)]=0, defining the increment to be zero off selection. A shared fresh observation may update several rows simultaneously if each marginal conditional-mean contract holds. No independence between rows, observations, birth events, allocations or future decisions is assumed. (A1) does exclude arbitrary dependence that changes a selected row's conditional mean.

Let N_j(t)=Σ_(s≤t) I_(j,s), S_j(t)=Σ_(s≤t) I_(j,s)(X_(j,s)−μ_j), and T_(j,n)=inf{t:N_j(t)=n}. An infinite T_(j,n) denotes an unattained visit. At an attained visit define the empirical mean μ̂_(j,n)=μ_j+S_j(T_(j,n))/n.

## A2. Global confidence theorem

Define

    b_j(n)=sqrt{ log[2n(n+1)/α_j] / (2n) },
    C_(j,n)=[μ̂_(j,n)−b_j(n), μ̂_(j,n)+b_j(n)]∩[0,1].

Under A1, there is one event E with P(E)≥1−δ on which μ_j∈C_(j,n) for **every born j and every attained n**, simultaneously. This remains true under unlimited revisiting, outcome-dependent future births, compatible dependence across rows, arbitrary stopping/continuation, and any countable collection of downstream deductions valid whenever their input memberships hold.

### Proof: conditional bounded increments

For any random variable X∈[0,1] with conditional mean μ and real λ measurable before X, conditional Hoeffding's lemma gives

    E[exp{λ(X−μ)} | past] ≤ exp(λ²/8).                   (A2)

For completeness: let K(λ)=log E[e^(λX)|past]. Under exponential tilting, K''(λ)=Var_λ(X)≤1/4, because Var(X)≤E[(X−1/2)²]≤1/4 for every law on [0,1]. Taylor's integral identity with K(0)=0 and K'(0)=μ yields K(λ)−λμ≤λ²/8 for either sign of λ. Boundedness justifies differentiation. Apply this pointwise to conditional laws; birth-measurable λ is fixed after conditioning on birth.

Condition on any finite birth τ_j=s and its history F_s. For any F_s-measurable λ, the process, initialized at one at s,

    Z_t(λ)=exp{λ S_j(t)−λ² N_j(t)/8},  t≥s,

is a nonnegative supermartingale. If I=0 its multiplier is one; if I=1 its conditional expected multiplier is at most one by (A1)–(A2). Predictable selection is exactly what permits this calculation. Conditioning on a birth event in F_s preserves the subsequent conditional inequalities.

### Proof: attained visits without selection conditioning

For T=T_(j,n), bounded optional sampling gives E[Z_(T∧m)|F_s]≤1 for every m≥s. Conditional Fatou then gives

    E[1_{T<∞} Z_T | F_s]≤1.                             (A3)

No statement conditions on {T<∞}; that event can select favorable data. Put L=log[2n(n+1)/α_j], ε=sqrt[L/(2n)] and λ=4ε, all fixed by birth history. On {T<∞, μ̂_(j,n)−μ_j>ε}, Z_T>exp(2nε²)=exp L. Conditional Markov and (A3) bound this event by exp(−L)=α_j/[2n(n+1)]. Apply the same argument with −λ for the lower tail. Thus

    P(T_(j,n)<∞, |μ̂_(j,n)−μ_j|>b_j(n) | F_(τ_j))
      ≤ α_j/[n(n+1)]  on {τ_j<∞}.                       (A4)

The stopping-time form follows by assembling the argument on the disjoint finite events {τ_j=s}. The sum Σ_(n≥1)1/[n(n+1)]=1 gives a conditional bound α_j for the row's ever-failure event B_j. Intersecting with any birth-history event preserves the bound, which is why a history-dependent α_j is permitted.

### Proof: all births and all times

By the tower property P(B_j)≤E[1_{τ_j<∞}α_j]. Countable subadditivity and Tonelli yield

    P(⋃_j B_j) ≤ Σ_j E[α_j] = E[Σ_j α_j] ≤ δ.           (A5)

Set E=(⋃_j B_j)^c. The entire proof uses the single global filtration, so a component's hidden information cannot silently invalidate another component's local filtration. Infinite horizon requires neither a terminal time nor infinitely many visits to every row. Every finite-time readout inherits E. Any limit statement additionally requires the asserted limit to exist and the deduction to remain valid under that limit. ∎

## A3. Global transfer and adaptive composition

At time t let C_t contain all current row intervals, and let D_t be any measurable adaptive deduction with the pathwise property

    [∀(j,n) used, μ_j∈C_(j,n)] ⇒ D_t is true.

Then P(∀t, D_t is true)≥1−δ, including deductions chosen from previously seen intervals, and readouts at stopping times. **Proof:** E implies every premise used at every time, hence every deduction; no additional statistical union is needed. Selecting a different already-covered row is allowed. A new empirical claim needs its own coverage premise. Separately valid modules with failure allowances δ_k compose by the same union argument when Σ_kδ_k≤δ and every module's law is valid for the actual shared protocol.

For random hypotheses created from historical data, this theorem covers **future** observations satisfying the frozen new conditional law. Historical evidence cannot be inserted as new increments merely because a row has been newly named. Such evidence is reusable when a previously proved simultaneous statement already covers the selected target, or when a separate selective-inference proof supplies the missing premise.

## A4. Changing estimands and nonstationarity

If the observable, population, conditioning state or target changes so that (A1) ceases to hold, the old interval is not an interval for the new target. Keep it attached to its old version and register a new row with a new allocation before obtaining evidence for the new version. Versioning does not itself make the replacement law valid; that law remains a proof obligation.

A distinct valid extension replaces μ_j by the predictable conditional means m_(j,t)=E[X_(j,t)|F_(t−1)]. The same exponential proof covers the attained-visit average m̄_(j,n)=n^(-1)Σ_(t≤T_(j,n))I_(j,t)m_(j,t), simultaneously for all j,n. This follows because the centered increments obey (A2); no fixed μ was otherwise needed. The covered object is the average past conditional mean, which need not equal a current population mean, a future mean, or the value of a current policy. Those identifications require separate stationarity/transport premises.

## A5. Conditional e-process replacement

The global birth-allocation proof also accepts conditional e-processes. For a null family H_j selected at birth, assume its truth event A_j={P∈H_j} is F_(τ_j)-measurable under fixed P. This measurability, or an explicitly equivalent conditional-on-birth null-family contract, is required for random nulls. Require a nonnegative process E_(j,t), **adapted to the global filtration**, initialized at one at birth. For every finite s, on {τ_j=s}∩A_j require E[E_(j,T)|F_s]≤1 for every finite stopping time T≥s of the post-birth protocol. This eventwise formulation imposes no impossible requirement T≥∞ on never-born paths. The process need not be a supermartingale.

Let T be the first post-birth crossing of 1/α_j; adaptedness makes T a stopping time. Condition on τ_j=s and a true-null birth history. For m≥s, apply the premise at T∧m to obtain P(T≤m|F_s)≤α_j, then take m↑∞ and assemble over finite s. Define the error event B_j=A_j∩{τ_j<∞, T<∞}. Its conditional probability is at most 1_(A_j)α_j≤α_j, so (A5) controls the probability of **any true-null crossing** by δ. Crossings of false nulls are not errors. A merely unconditional e-value, an unadapted process, or validity in a smaller component filtration does not supply this premise.

## Parent methods and scope

The exponential-supermartingale and confidence-sequence method is an adaptation of [Howard, Ramdas, McAuliffe and Sekhon (2021)](https://doi.org/10.1214/20-AOS1991); our explicit n(n+1) union boundary is deliberately elementary, not their sharper mixture/stitching boundary. Birth-conditioning and countable row allocation are proved above, not claimed as a new concentration inequality.

The distinction between nonnegative supermartingales and general e-processes follows [Ramdas, Grünwald, Vovk and Shafer (2023)](https://doi.org/10.1214/23-STS894). A5 requires validity conditional on the actual birth history and for stopping times of the actual global protocol, which cannot be inferred from a fixed-time marginal guarantee.

These theorems close adaptive **validity conditional on declared laws**. They do not imply identifiability, causal access, sufficient learned state, useful interval width after finitely many visits, optimal efficiency, or a universal architecture.
