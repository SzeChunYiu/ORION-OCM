# Learning: definitions, statistical guarantees and convergence

Status: conditional mathematical derivations; no universal improvement or new learning-theory claim.
Read [CORE](CORE.md), then [optimization](OPTIMIZATION.md) and the [constructed learner](LEARNER.md).

## L0 — what changes, what is learned, what improves

Write the machine state as `(s,K)`: `s` is episode state; `K` persists across the declared episode reset.
`K` includes executable structures, parameters, evidence/certificates, optimizer state and their dependency versions.
An acquisition transition is `K'=U(K,e)` together with its actual resource trace; `U` must itself be an admitted executable process.
It is experience-dependent when, holding initial state and internal randomness fixed, some admissible `e,e'` produce different retained states.
A change counts as operational learning when it also changes an admitted future output, resource profile or reachable update behavior after reset.
Renaming a state with identical future behavior and costs is not operational learning.
This is a counterfactual definition, not an assertion that a fitted parameter change demonstrates causal use of experience.

Fix externally an evaluation distribution `P` on tasks `Z`, a measurable loss `0<=ell(h,Z)<=1`, and deployment semantics for each retained executable `h`.
Population risk is `R_P(h)=E_P ell(h,Z)`; data do not get to redefine the scoring rule after selection.
Risk improvement means `R_P(h')<R_P(h)`; it does not mean improvement on every input or for every distribution.
For nonnegative declared resource prices `lambda`, define `q_P(h)=R_P(h)+lambda·c(h)`, where `c` is a fixed per-use resource profile.
The scalar lifecycle formula below uses additive expenditure or explicitly priced per-use rental; peak RAM is not summed across sequential uses.
Hard memory/time constraints define feasibility before minimization; a scalar price does not enforce them.
For a lifecycle with acquisition/verification/repair/retention overhead `A` and `H` future uses, its population-cost forecast is `A+H q_P(h)`.
Thus a transition improves that forecast exactly when `H[q_P(h)-q_P(h')]>A`; every comparison uses the same horizon and cost units.
If deployment costs are random, include them in a bounded measured loss or give them their own valid certificate; an unverified point estimate is insufficient.

## L1 — bounded-mean concentration, with the proof exposed

For `X in [0,1]`, put `phi(lambda)=log E exp(lambda(X-EX))`.
Under the exponentially tilted distribution, `phi''(lambda)=Var_lambda(X)<=1/4`: variance is at most `E(X-1/2)^2<=1/4`.
Since `phi(0)=phi'(0)=0`, integrating this second-derivative bound gives `phi(lambda)<=lambda^2/8` for either sign of `lambda`.
For independent bounded `X_i` with a common mean, multiplication of moment bounds yields

    Pr(mean(X_i)-EX_1 >= b) <= inf_(lambda>0) exp(-lambda*n*b+n*lambda^2/8)
                                = exp(-2*n*b^2),
    Pr(|mean(X_i)-EX_1| >= b) <= 2 exp(-2*n*b^2).

The minimizer is `lambda=4b`; the lower tail uses `-lambda`.
Conditional moment bounds give the martingale version; adaptive row visits and births require the stopped-process construction in [adaptive inference](ADAPTIVE.md).
This is the classical [Hoeffding concentration mechanism](https://repository.lib.ncsu.edu/items/3f47dae6-2e27-4a2c-9935-54aa9390ffaf), reconstructed here for the learning interface.

## L2 — finite/countable learning with one explicit generalization certificate

Let `H={h_1,h_2,...}` be a fixed countable collection of measurable executables, with pre-data masses `p_h>0`, `sum p_h<=1`.
Let `Z_1,Z_2,...` be IID from `P`; the same observations may score every member.
The class, masses, evaluation law and losses are fixed before these observations; no independence between different members' losses is required.
Set `Rhat_n(h)=n^-1 sum_i ell(h,Z_i)`, choose `0<delta<1`, and define

    b_h(n) = min{1, sqrt(log(2*n*(n+1)/(delta*p_h))/(2*n))}.

At a fixed `(h,n)`, L1 bounds the failure probability by `delta*p_h/[n(n+1)]` whenever the radius is below one; radius one is deterministically valid.
Summing over countably many `h,n`, using `sum_n 1/[n(n+1)]=1`, proves

    Pr(E_L)>=1-delta,
    E_L := { forall h,n>=1: |Rhat_n(h)-R_P(h)|<=b_h(n) }.

This controls any later data-selected member and finite sample size, since all displayed inequalities hold together.
Let `c(h)` be known, finite and nonnegative, and `qhat_n(h)=Rhat_n(h)+lambda·c(h)`.
Choose `hhat_n` within optimization error `xi_n>=0` of minimizing `qhat_n(h)+b_h(n)` over a nonempty finite admitted set `H_n subset H`.
On `E_L`, for each `h in H_n`,

    q_P(hhat_n) <= qhat_n(hhat_n)+b_hhat_n(n)
               <= qhat_n(h)+b_h(n)+xi_n
               <= q_P(h)+2*b_h(n)+xi_n.                         (L2.1)

For a fixed finite class of size `N`, uniform masses make `b` common, so ordinary empirical minimization has excess deployment cost at most `2b+xi_n`.
At one prespecified sample size, replacing `n(n+1)` by `1` gives the sharper fixed-look bound; it cannot be reused at optional stopping without a simultaneous argument.
With `c=0`, (L2.1) is a finite/countable agnostic PAC guarantee relative to the admitted class, not a realizability claim.
For prefix-free code lengths `L(h)`, Kraft's inequality permits `p_h=2^-L(h)`; the confidence penalty then contains `L(h) log 2`.
This is a precise description-length/generalization connection, not a theorem that the shortest program has minimum execution cost or is computably discoverable.
The parent is [Blumer et al.'s Occam/PAC program](https://www.sciencedirect.com/science/article/pii/0020019087901141); this note uses a bounded-loss union bound, not their original consistent-learning theorem.

## L3 — strong consistency, and the extra cost condition it needs

Assume `H_n` eventually contains each fixed `h in H`, `xi_n->0`, every loss is measurable, and some admitted `q_P(h)` is finite.
These sets may grow adaptively within the fixed countable universe, provided the displayed eventual-inclusion condition holds.
At sample size `n`, failure of at least one confidence inequality has probability at most `delta/[n(n+1)]`.
The sum is finite, so the first Borel–Cantelli lemma implies that almost surely only finitely many sample sizes fail; independence of failures is unnecessary.
Fix `h`. Eventually it is included and (L2.1) applies, while `b_h(n)->0`; hence `limsup q_P(hhat_n)<=q_P(h)` almost surely.
Intersecting these probability-one statements over the countable class and taking the infimum gives

    q_P(hhat_n) -> inf_(h in H) q_P(h)    almost surely.

The lower bound follows because every selected member belongs to `H`; an attained minimizer is unnecessary.
This concerns objective values, not convergence of parameters, model syntax, predictions at every input, or discovery of a true world model.
With known lifecycle overhead `A_n` and realized-use horizon `H_n^use`, the amortized forecast converges to the same infimum only if `A_n/H_n^use->0`.
Otherwise risk consistency can coexist with permanently negative net value: spending `n^2` to save at most `H_n^use=n` units never pays.
Executable finite selection additionally needs effective certified bounds for evaluated losses, resource costs, prior masses and the resulting penalties, not merely terminating member execution.
Either exact score comparisons must be decidable, or use a positive optimization tolerance `xi_n` and refine certified score intervals until `U_selected <= min_h L_h + xi_n` for their upper/lower endpoints.
For finitely many effectively approximable finite scores, interval widths tending to zero ensure this positive-tolerance condition eventually holds, including ties; charge all precision/refinement work and require it to fit the declared resources.
Arbitrary exact ordering of computable real scores and arbitrary countable infimum search have no such general executable guarantee.

## L4 — a known online learner, derived and proved

For finite experts `j=1,...,N`, initialize positive masses `p_j` summing to one, and retain cumulative losses `L_(t-1,j)`.
At round `t` choose

    w_(t,j) = p_j exp(-eta*L_(t-1,j)),
    pi_(t,j) = w_(t,j)/sum_k w_(t,k),
    L_(t,j) = L_(t-1,j)+ell_(t,j),         0<=ell_(t,j)<=1.

All expert losses are revealed after the decision; they may depend on the entire past and on the published mixture.
The algorithm follows the entropic local update derived in [O2](OPTIMIZATION.md); its retained loss/weight vector is explicit non-neural learned knowledge.
Define `W_t=sum_j w_(t,j)` and mixture loss `m_t=sum_j pi_(t,j) ell_(t,j)`.
Applying L1's single-variable exponential bound to the finite distribution `pi_t` gives

    log(W_(t+1)/W_t) <= -eta*m_t + eta^2/8.

Since `W_1=1` and `W_(T+1)>=p_j exp(-eta*L_(T,j))`, summation and rearrangement prove, for every realized loss sequence,

    sum_(t<=T) m_t - L_(T,j) <= log(1/p_j)/eta + eta*T/8.       (L4.1)

For uniform masses and known `T`, `eta=sqrt(8 log(N)/T)` gives regret at most `sqrt(T log(N)/2)` for `N>1`; `N=1` has zero regret.
A mixture prediction has loss at most `m_t` if the prediction domain is convex and its loss is convex.
A sampled expert has conditional expected loss `m_t` only when the environment cannot condition that round's loss vector on the current private sampled choice.
Realized sampled-expert deviations require a separate martingale bound; (L4.1) itself concerns mixture losses.
Repeated doubling epochs with fresh uniform weights yield an unknown-horizon bound of order `sqrt(T log N)`: epoch bounds form a geometric series, and summing regrets against the same expert preserves comparison.
All expert evaluation, full-information feedback, weight updates and retained storage are charged; a small regret bound does not make a large expert pool cheap.
This is established [weighted majority](https://homepages.math.uic.edu/~lreyzin/papers/littlestone94.pdf) / [Hedge](https://www.sciencedirect.com/science/article/pii/S002200009791504X), not a GMI-invented learner.

## L5 — where learning does not follow

Unobserved distinctions block universal improvement. Let two worlds agree on every acquired observation but assign opposite labels to a future input `x*`.
Changing the prediction probability of label one at `x*` helps one world and harms the other by the same amount under zero-one loss.
Leaving predictions unchanged cannot give strict risk improvement; positive acquisition costs make a strict universal net-improvement claim even less possible.
Thus no axiom requiring only executable updates and evidence can ensure that every update improves every admissible world.
IID stationary sampling and class coverage are sufficient assumptions in L2–L3; neither follows from the existence of a memory store.
Fitting an unrestricted data-dependent candidate on its evaluation examples breaks L2 unless it is covered by the fixed prior/class bound; fresh post-registration evaluation repairs the separate-candidate setting.
Changing losses or resource prices changes the objective; changing the task law invalidates the old population-risk target.
Revision, forgetting and new structures may improve a new task law while increasing old-task risk; a single monotone knowledge order cannot silently identify both objectives.
The [certified structure selector](LEARNER.md) makes these premises operational and keeps every unpaid acquisition charge visible.
