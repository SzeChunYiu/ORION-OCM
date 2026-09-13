# A constructed learner: certified reusable executable structures

Status: proposed GMI synthesis with proved conditional guarantees; no priority, empirical superiority or universal self-improvement claim.
The known learner is Hedge in [L4](LEARNING.md). This note specifies a second, executable non-neural construction, abbreviated CRES.

## Construction and parents

Fix finitely many nonempty finite feature alphabets, a nonempty finite output alphabet, an integer maximum depth `d>=0`, and a nonnegative resource contract.
Programs are finite decision trees: leaves return an output constant; internal nodes test equality between an input coordinate and an alphabet symbol.
Tree evaluation is total by induction on depth; all syntax trees up to the depth bound form a finite effectively enumerable universe `G`.
If there are `a` distinct coordinate-symbol tests and `y` output constants, its syntax count obeys `T_0=y`, `T_d=y+a*T_(d-1)^2`; a tree uses at most `d` tests per evaluation and `2^(d+1)-1` stored nodes.
These are interpreter-level counts; input access, representation, equality arithmetic and physical memory charges remain in the explicit resource contract.
Birth can use breadth-first enumeration or an experience-selected next tree/edit; a fairness premise is required only for the convergence theorem below.
Generated trees, retained certificates, comparison statistics and the program that schedules their acquisition constitute persistent learned structure.
No neural model is used in candidate generation, selection, memory or execution.

The inherited statistical mechanism is [time-uniform confidence inference](https://arxiv.org/abs/1810.08240), instantiated by [adaptive inference](ADAPTIVE.md).
The admission idea has a strong parent in [Thomas et al.'s high-confidence policy improvement](https://proceedings.mlr.press/v37/thomas15.html): confidence is used to decide whether to deploy a proposed policy.
CRES adapts that idea to paired supervised losses of frozen executable structures, dynamic registration and a ledger covering rejected proposals and amortized reuse.
It is not an off-policy RL guarantee, does not inherit the parent's trajectory estimator, and does not improve its statistical rate.
The cost and revision scope also adapts the repository's [certified reuse/invalidation](../gmi-grand-unification-v1/CERTIFIED_REUSE_INVALIDATION_THEOREM_V1.md) and [shared-memory reuse](../gmi-grand-unification-v1/SHARED_DEPENDENCY_MEMORY_REUSE_THEOREM_V1.md).
Combining these parents defines this proposed learner; a claim that the combination is globally new requires a broader priority investigation and matched experiments.

## C0 — executable state and observation contract

The retained state contains incumbent source `c`, frozen candidate sources, each source's dependency/law/loss/resource version, a row register and an unsettled-cost ledger.
Each pair row `j` identifies an immutable ordered pair `(c,h)` and its complete scoring contract; a digest is only an index, with source identity and dependencies checked separately.
At every operation, verify the declared memory/time constraints for the incumbent, challenger, counters, retained sources and transient evaluation workspace.
Infeasible candidates are not evaluated or admitted; deleting a counter prevents reuse of the deleted evidence unless it can be reconstructed from an authenticated retained record at charged cost.

For each executable `h`, let its bounded scored deployment cost be `q(h)=E g(h,Z)`, `0<=g(h,Z)<=B`, `B>0`, under one fixed external task law.
`g` includes loss and the specified per-use resources; hard feasibility remains separate.
Only additive charges or explicit per-use rent enter this scalar score; peak memory uses the maximum live allocation, never a sum of sequential peaks.
At each served task, before choosing its current private randomization, the deployment contract also requires `E[g(h,Z_t)|complete past]=q(h)` for every eligible frozen `h`.
After a pair is frozen and registered, draw fresh tasks and record `Y_(j,n)=g(c,Z)-g(h,Z) in [-B,B]`.
The complete pre-observation history must satisfy `E[Y_(j,n)|past]=Delta_j=q(c)-q(h)` whenever that row is next visited.
Predictable scheduling may revisit rows and use all prior evidence; comparisons may share the same fresh task if their joint conditional marginal means satisfy this requirement before its reveal.
Rows are not assumed independent. Fitting a candidate with an outcome before counting that outcome in its new row is forbidden by this contract.
Changing the incumbent, source, distribution, loss or resource semantics requires a new pair version; old rows remain usable only for their unchanged original targets.

Register birth index `j=1,2,...` before its first scored observation, with `alpha_j=delta/[j(j+1)]`, `0<delta<1`.
For attained visit count `n>=1`, define

    b_j(n)=min{2B, B*sqrt(2*log(2*n*(n+1)/alpha_j)/n)},
    lower_j=Ybar_(j,n)-b_j(n),       upper_j=Ybar_(j,n)+b_j(n).

Unobserved comparisons use `[-B,B]`.
The adaptive theorem, applied to `(Y+B)/(2B)`, gives one event `E_C`, `Pr(E_C)>=1-delta`, on which every `Delta_j` lies in its interval at every attained finite visit.
Indeed the two-sided tail at a registered visit is at most `2 exp(-n*b^2/(2B^2))`; summing `alpha_j/[n(n+1)]` over `j,n` gives `delta`.
The stopped-process proof is essential: conditioning a completed prefix on its existence can bias it, so it cannot simply be called IID.

## C1 — admission, including every unsuccessful acquisition

Choose a fixed deployment margin `gamma>0`. Begin with an admitted executable baseline `c_0` and zero learning overhead.
While serving external tasks with the incumbent, perform candidate generation, shadow evaluation and verification as additional, fully charged work.
For a proposed reuse horizon `H>=1`, let `C_k(H)>=0` be a known upper bound on all unsettled overhead since the previous completed settlement, plus this switch and its full horizon's auxiliary overhead.
This includes failed/rejected candidates, source generation, data access, paired execution, certificates, sampler control, counters, storage allocation/rent, retained unused sources, invalidation, repair, synchronization, cleanup and transient workspace.
Resources already included in `g` are not charged twice. A forecast for storage rent or switch work requires a valid bound, not an optimistic point estimate.
The horizon must be feasible as an actual stationary stream of future uses; merely writing a large number cannot create demand.

    if hard feasibility holds and lower_j > gamma + C_k(H)/H:
        admit h; freeze its deployment semantics for H uses;
        complete the H-use episode; settle its covered overhead;
        retain the full ledger; set incumbent c = h;
    otherwise:
        keep c; retain all paid overhead as unsettled debt;
        defer, reject, or revisit the candidate using the valid row.

No new incumbent switch occurs inside a committed episode. A stopped or invalidated episode receives credit only for the uses actually covered by its valid contract.
Future savings are never posted as realized savings at admission.
The algorithm is finite and executable per operation: tree generation/evaluation, counter updates, a computable conservative radius, comparison and a finite deployment loop.
Rational outward bounds for logarithms/square roots preserve the guarantee; numerical comparison ambiguity must defer admission or increase certified precision at charged cost.

## C2 — certificate and full-lifecycle forecast bound

This theorem applies within one unchanged scoring/dependency contract; transporting it across a changed world or resource model requires an additional bound, not a reset of the debt ledger.
On `E_C`, every admission satisfies

    q(c)-q(h) >= lower_j > gamma + C_k(H)/H,
    C_k(H)+H*q(h) < H*q(c)-H*gamma.                         (C2.1)

This is obtained by substituting the confidence lower bound; it is simultaneous over adaptive birth, scheduling, admission and chosen finite horizons.
Its subject is the true population-cost forecast of the frozen deployment, including the stated overhead bound.
It is not a deterministic guarantee about every realized task sequence, nor an expectation conditional on the entire future good event.
Actual cumulative deployment losses fluctuate; a separately allocated martingale confidence allowance is needed for a high-probability realized-cost claim.

Every accepted incumbent has `q(c)<=q(c_0)` on `E_C`.
For any finite lifecycle prefix ending between committed episodes, sum actual overhead plus the conditional mean of each task's scored cost, and subtract the original fixed baseline's corresponding population forecast.
Outside completed episodes the current incumbent contributes a nonpositive difference relative to the original baseline.
Inside each completed episode, its difference relative to the original baseline is no larger than its difference relative to that episode's previous incumbent.
Applying (C2.1) and adding disjoint settled overhead therefore proves

    lifecycle compensator difference <= D_pending - gamma*sum_(completed k) H_k.  (C2.2)

Here `D_pending` is every paid but unsettled learning charge in the prefix; auxiliary costs inside settled horizons were already included in their `C_k`.
This is a pathwise inequality between predictable population-cost forecasts on `E_C`; it is not a realized-noise bound or an unconditional expected-regret theorem.
If the learner stops after costly unsuccessful proposals, `D_pending` can be positive. CRES does not promise that safe admission makes exploration free or that every lifecycle prefix beats no learning.

## C3 — finite progress, and a finite feasible witness

Since `q` is one fixed objective in `[0,B]` and every switch reduces it by more than `gamma`, after `m` switches `0<=q(c_m)<q(c_0)-m*gamma`.
Hence the number of switches is at most `floor(B/gamma)`. This bound concerns accepted deployments, not births, samples, waiting time or all acquisition work.
If a pair's true gap is `Delta>gamma`, then on `E_C`, `lower_j>=Delta-2b_j(n)`.
Thus a sufficient finite progress condition is

    2*b_j(n)+C_k(H)/H < Delta-gamma,                         (C3.1)

with finite affordable `n,H` and available observations/uses. This displays the precise sampling-versus-amortization requirement.
If `C_k(H)>=H*(Delta-gamma)` for every feasible horizon, even exact knowledge of `Delta` cannot authorize that switch under this contract.

A fully declared formal witness uses two constant trees, binary labels with `P(Y=1)=3/4`, unit zero-one loss and `B=1`.
The zero tree has risk `3/4`, the one tree risk `1/4`; paired observations are `2Y-1`, with `Delta=1/2`.
Take `delta=1/20`, first-row `alpha_1=1/40`, `n=4096` and a conservative rational radius `b=1/8`.
The tail is `2 exp(-32)<2^-31<1/(40*4096*4097)`, since `e>2` and `40*4096*4097<2^31`; hence this rational radius is valid at that visit under the same error-spending schedule.
Specify acquisition charge `1/32` per paired observation and all other overhead `128`, so complete overhead is `C=256`; no omitted retention rent is allowed in this abstract witness.
With `H=4096` actual future uses and `gamma=1/8`, `C/H=1/16` and `lower>=1/4>3/16`, so admission follows on `E_C`.
The true net population saving is `H/2-C=1792`; this is exact arithmetic for the supplied abstract costs, not a measured hardware or sample-efficiency result.
Keeping the same acquisition bill but only `H=128` gives savings `64-256<0`: a sound statistical certificate alone does not repay acquisition.
The constructive revival is a longer valid reuse horizon, lower actual acquisition cost, or a different cheaper candidate; no positive verdict is earned by omitting the bill.

## C4 — convergence in one explicit long-running regime

Assume: one stationary scoring law and fixed `q in [0,B]`; a finite frozen feasible universe `G`; and a persistent `gamma>0`.
Each candidate is eventually born, and while the incumbent remains unchanged every challenger is visited infinitely often in a retained valid pair row.
All individual operations and deployment episodes terminate; available memory retains the necessary pair evidence after the final switch.
At the reconsideration times of each pair, feasible actual reuse horizons satisfy `C_k(H_k)/H_k->0`.
This last assumption includes all unpaid rejection costs and future retention costs; it can fail when continuing rent is positive or demand is finite.

On `E_C`, C3 implies finitely many incumbent switches, so there is a final incumbent `c*` after some finite operation index.
Suppose some `h in G` has `q(c*)-q(h)>gamma`, and call the excess over `gamma` `epsilon>0`.
Fairness makes its attained visit count tend to infinity, so `b_j(n)->0`; amortization makes `C_k(H_k)/H_k->0`.
Eventually `2b_j(n)+C_k(H_k)/H_k<epsilon`, so C3.1 forces another switch, contradicting finality.
Therefore

    q(c*) <= min_(h in G) q(h)+gamma                         (C4.1)

with probability at least `1-delta`. This is conditional approximate objective convergence; it is not exact identification or a finite-time termination theorem.
If the amortization term instead has limsup at most `r`, the identical argument gives `gamma+r` in (C4.1).
Lowering `gamma` in a sequence of complete fresh registered phases can refine accuracy under renewed feasibility assumptions, but the fixed-margin finite-switch bound no longer covers the combined phases.
For a finite stopping certificate, stop when every challenger in the entire finite `G` has a current-pair `upper_j<=gamma`; ungenerated/unsampled members keep their initial upper bound `B`.
On `E_C` this proves the incumbent is `gamma`-optimal within `G`; checking only the currently generated subset does not.
After an incumbent remains fixed, this condition is reached in finite samples when every gap is strictly below `gamma`, finite candidates are fairly revisited, and sampling remains affordable.
At an equality gap, shrinking confidence widths alone do not guarantee finite stopping; no claim of universal detection time is made.

## Claim-breaking tests and parent comparison

Reuse one noisy evaluation as many draws: the freshness premise fails; revive with distinct observations or a dependence-valid process.
Retrain a tree while retaining its old comparison row: target identity fails; revive by freezing/versioning and paying for a fresh row.
Let tasks drift, dependencies change or a proof invalidate: suspend the affected certificate, retain the cost debt and establish a new valid scoring contract before reuse.
Let search enumerate forever without enough evidence for one improving tree: fairness/affordability fails, so no progress theorem applies.
Exclude a useful tree from `G`: C4 remains only a comparison within `G`; it makes no claim of complete architectural search.
For prospective experiments, compare the same candidate births and paired data against ordinary confidence-based model selection and the strongest cost-aware admission parent; then ablate only persistent evidence reuse and debt accounting.
Report full lifecycle costs, false-admission frequency, terminal objective gap and acquisition regret separately. No experiment or comparative advantage is asserted by these proofs.
