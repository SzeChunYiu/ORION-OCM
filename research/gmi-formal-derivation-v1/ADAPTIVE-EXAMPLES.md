# Adaptive inference: sharp premises and finite controls

Read [the global theorem](ADAPTIVE.md) first. The examples below are exact probability calculations. They validate special instances and expose invalid premises; finite enumeration is not a proof of the infinite-horizon theorem.

## E1. Repeated visits and attained-sample selection

Let Z₁,Z₂,Z₃ be independent fair bits. Visit a row at t=1, skip t=2, and revisit at t=3 only if Z₁=1. The global history includes all three bits as they arrive. Every included fresh bit has conditional mean 1/2. The betting process multiplies by 2Z_t at each visit and is unchanged otherwise; it is a nonnegative martingale.

The second visit exists with probability 1/2. Its betting value is 4 on {Z₁=Z₃=1}, zero on {Z₁=1,Z₃=0}. Consequently

    P(T₂<∞, E_(T₂)≥4)=1/4,
    P(E_(T₂)≥4 | T₂<∞)=1/2,
    E[1_{T₂<∞}E_(T₂)]=1,
    E[E_(T₂) | T₂<∞]=2.

Thus conditioning on the existence of the nth visit loses the needed bound. A2 uses the first and third quantities, so repeated adaptive revisiting remains valid.

## E2. Conditional births with random allocations

Start a row at time zero with α₁=1/4 and multiplier 2Z_t on independent fair bits. Freeze its value once it reaches four. If its first failure is at t=1, create a child **after** observing that failure with α₂=1/4. If its first failure is at t=2, create the child after that observation with α₂=1/8. Otherwise never create the child. The child starts at one and uses only later bits. Observe through t=5.

Every birth is a stopping time; every child allocation is known at birth; the sum is at most δ=1/2 on every path. Conditional child crossings have probabilities 1/4 and 1/8 respectively. Their unconditional probabilities are (1/2)(1/4)=1/8 and (1/4)(1/8)=1/32. Parent crossing has probability 1/4. These three events are disjoint, so

    P(any crossing)=1/4+1/8+1/32=13/32,
    E[Σ_j α_j]=1/4+(1/2)(1/4)+(1/4)(1/8)=13/32≤1/2.

This finite system realizes the conditional-birth tower calculation exactly. Continuing it forever does not change those ever-crossing probabilities: a failed all-heads betting process stays at zero, and a surviving process reaches its fixed threshold after finitely many heads.

## E3. Dependent rows: valid coverage, invalid multiplication

Two rows can both use the same new bit at every time. Under the global history, each fresh bit still has conditional mean 1/2, so each row's process E_j is valid. With two visits, E₁=E₂=4 precisely on two heads. At α₁=α₂=1/4, their joint ever-failure probability is 1/4≤α₁+α₂=1/2. The coverage union needs no independence.

However E₁E₂=16 on two heads and zero otherwise, so E[E₁E₂]=4. Treating that product as an e-value and using threshold eight produces probability 1/4 at a claimed level 1/8. Multiplication requires a sequential conditional calibration argument or another sufficient premise; marginal e-validity does not provide it. Same-time updates may share evidence under A1, but cannot multiply it as if independent.

For a distinct hidden-history failure, reveal Z first to component A and later replay it to component B. B's own empty local history gives marginal mean 1/2, while the actual global history gives E[Z|Z]=Z. The global conditional law fails at B's observation, regardless of whether the components label their rows differently.

## E4. Evidence replay

Draw one fair bit Z and store it. Replaying that value three times gives the falsely compounded evidence (2Z)³=8Z. It crosses threshold four with probability 1/2, exceeding the claimed 1/4. Already on the second replay, the proposed fresh-increment premise is false: E[Z|F₁]=Z≠1/2.

The confidence-bound failure can be made exact without numerical logarithms. Replay the bit 32 times and set α=1/20. The A2 radius satisfies

    b(32)²=log(42240)/64 < 1/4,

because e¹⁶>16⁷/7!>42240. The replay mean is zero or one, at distance 1/2 from its purported population mean 1/2. The alleged interval therefore misses with probability one. This is an A1 violation, not a counterexample to A2.

Repair: count the original draw once. Later uses are deterministic computations on that existing evidence. They may reuse its valid coverage event, but cannot create additional sample information.

## E5. Data-dependent new claims and historical postselection

For a fair bit Z, the two fixed e-values e₀=2(1−Z) and e₁=2Z each have expectation one. After observing Z, select e_Z. The selected historical value is identically two. A newly named claim that counts it as fresh rejects at level 1/2 with probability one.

Repair: freeze the selected observable f_Z(y)=1{y=Z}, then obtain an independent fresh fair bit Y. Conditional on each birth history Z, E[2f_Z(Y)|Z]=1. Alternatively, prove simultaneous validity for both original targets before selecting one and pay the corresponding joint error allocation. Random target selection itself is allowed; uncalibrated historical evidence reuse is the defect.

## E6. Fixed-time validity is insufficient for optional stopping

Let E_t=2Z_t for independent fair bits and t∈{1,2}. Each fixed-time expectation is one. Stop at the first value two, or at t=2 if no such value appears. Then P(E_T≥2)=3/4 and E[E_T]=3/2. These fixed-time e-values are not an e-process. A5 explicitly requires conditional validity at all stopping times, not just each deterministic time.

## E7. Changed target versus past conditional average

Observe 32 deterministic zeroes, followed by 32 deterministic ones. The first epoch has mean zero; the second has mean one. Treating all 64 observations as a stationary row of mean zero violates A1 after the change. Calling the pooled mean 1/2 an estimate of the current mean one also fails: at α=1/20 its radius obeys

    b(64)²=log(166400)/128 < 1/4,

because e³²>32⁵/5!>166400. The pooled interval excludes the current mean one with certainty. The same interval **does** cover the average past conditional mean 1/2, exactly the distinct target justified by A4.

Repair: freeze the old epoch's claim, register the new regime before using new observations, and justify its new conditional law. If a regime change is detected only later, assigning old points to a selected boundary additionally requires a valid change-point/selection argument. Merely restarting a counter after an alarm does not validate retrospective assignments.

## E8. Bounded paired-loss adaptation

Let B>0 and Y_(j,t)∈[−B,B] be the fresh paired loss difference for a frozen learner/incumbent pair, with E[Y_(j,t)|F_(t−1)]=Δ_j. (For B=0 the difference and target are identically zero.) Apply A2 to X=(Y+B)/(2B). On one event of probability at least 1−δ,

    |Δ̂_(j,n)−Δ_j|≤B sqrt{2 log[2n(n+1)/α_j]/n}

for every born comparison and attained sample count. A radius clipped at 2B is equivalent for coverage because no two values in [−B,B] are farther apart. The pair, loss definition and target law remain fixed within a row; new fitting or a changed incumbent needs a new version. Candidate training can use the whole birth history, while the subsequent loss increments must satisfy the global conditional mean contract.

## E9. An unadapted process defeats the crossing argument

On a three-point probability space let U be uniform on {1,2,3}, but give the process the trivial filtration at every time. Set E₀=1, E_t=3·1{U=t} for t=1,2,3, and E_t=0 thereafter. Every finite stopping time for this filtration is deterministic, and E[E_T]≤1 for each one. Nevertheless max_t E_t=3 with probability one, so crossing the threshold two has probability one, exceeding α=1/2. The first crossing U is not a stopping time in this filtration: E_t is unadapted.

Repair: require adaptedness to the actual global history as in A5. If U is revealed instead, the associated larger filtration admits the first crossing as a stopping time, and the alleged e-process premise fails because E[E_U]=3. One cannot keep an unrealistically small filtration while operationally reading hidden values to decide when to stop.

## Executable controls

[tests_adaptive.py](tests_adaptive.py) enumerates the finite fair-bit trees and the three-point hidden-variable model using exact `Fraction` weights. It checks predictable revisits, attained-time selection, conditional dynamic births, the global allocation calculation, perfectly dependent rows, replay, hidden global-history dependence, postselection, optional stopping, adaptedness and target drift. Exponential series lower bounds certify the two logarithmic inequalities using rational arithmetic. No Monte Carlo estimates or claims of general mechanized verification are used. Run this unit on the designated laptop with `python3 research/gmi-formal-derivation-v1/tests_adaptive.py`.
