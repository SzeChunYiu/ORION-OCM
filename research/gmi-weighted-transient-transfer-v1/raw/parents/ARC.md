# Adaptive row confidence and policy transfer — ARC-1–4

Scope: a fixed finite sufficient-state/support/cost contract, predictable row
selection, stationary conditional row laws, adaptive sample counts and stopping.

## Parents and the missing sampling premise

[Howard et al. (2021), §§1–2](https://arxiv.org/pdf/1810.08240)
establish time-uniform concentration and explain why fixed-time inference
cannot be reused without adjustment under optional monitoring. The old
[FC-T7, §8.2](https://github.com/SzeChunYiu/ORION-OCM/blob/28bc6515/docs/spec/OCM_FOUNDATIONS_CLOSURE_V1.md)
already specializes the elementary error-spending construction to repeated
scalar observations. [FMT-1–4](../gmi-grand-unification-v1/FINITE_DATA_MODEL_TRANSFER_THEOREM_V1.md)
supplies finite-alphabet row confidence and uniform common-policy transfer at
fixed N, using the Weissman et al. finite-alphabet parent and a sharp
simulation-lemma coupling. These mechanisms are inherited.

ARC adapts them to variable row counts chosen by one history-dependent sampler.
It does not invent a confidence-sequence method, improve the strongest known
statistical rate, infer a sufficient state, or certify a physical sampler.

## Fixed observation contract

Register finitely many unknown rows r, each with a supplied finite alphabet
Z_r of size k_r containing the true support. At global step t, the sampler
either stops or selects r_t using only the available past and independent
randomness, before receiving Y_t. Conditional on that complete pre-outcome
history and selection r_t=r, Y_t has the same fixed law P_r on Z_r.
This is a conditional-law assumption, not a consequence of logging call IDs.
Rows need not be selected in any fixed order, equally often, or infinitely often.

Write N_r(t) for its visit count and P_hat_(r,n) for the first n visited
outcomes' empirical distribution when that visit exists. Fix alpha in (0,1)
and strictly positive row weights w_r with sum_r w_r <= 1 before observing data.
Known rows use their supplied exact law. An unknown one-symbol row is already
determined by the support contract. An unobserved multi-symbol row receives
radius 1 and any supplied distribution on its alphabet.

For n>=1 choose a deterministic radius e_r(n) in [0,1]. Radius 1 is always
valid. Otherwise require

    (2^k_r - 2) exp(-2n e_r(n)^2) <= alpha w_r / [n(n+1)].

The familiar clipped square-root-log radius suffices. Conservative rational
radii certified by a lower bound on exp also suffice. Data-dependent changes
to alpha, weights, alphabets or this predeclared radius rule require a new
valid simultaneous argument; renaming an attempt does not reset its error.

## ARC-1 — every row, every attained visit count

With probability at least 1-alpha, all empirical rows simultaneously satisfy
TV(P_r,P_hat_(r,n)) <= e_r(n) at every finite attained visit n.

Proof: fix row r and a nonempty proper subset A of Z_r. Let

    S_t = sum_(s<=t:r_s=r) [1[Y_s in A] - P_r(A)],
    M_t(lambda) = exp(lambda S_t - lambda^2 N_r(t)/8).

Predictable selection and the conditional Hoeffding bound make M_t a
nonnegative supermartingale starting at 1, including steps that skip r.
Let T_n be the time of its nth visit. Optional sampling at T_n wedge m and
Fatou give E[M_(T_n) 1[T_n<infinity]] <= 1. For fixed lambda=4e>0,

    Pr(T_n<infinity and S_(T_n)>ne) <= exp(-2ne^2).

Total variation equals the maximum positive empirical excess over subsets;
complements account for both signs. Union over the 2^k_r-2 nontrivial subsets,
then over visits n and rows r, uses sum_n 1/[n(n+1)]=1. The radius-1 and
one-symbol cases are deterministic. QED.

Crucially, conditioning on T_n being finite can bias the observed prefix.
The proof bounds the joint event of reaching n and failing there; it never
asserts that completed prefixes are iid after that selection conditioning.
It neither promises that T_n exists nor that sampling eventually terminates.

## ARC-2 — adaptive stopping and the existing transfer certificate

At any finite data-dependent stopping time T, construct a fitted row table
and put e=max({0} union {e_r(N_r(T)): r unknown}), including radius 1 for
unsampled unknown rows. An entirely known model therefore has e=0.
On ARC-1's one simultaneous event, every row is within e. Under FMT's fixed
fully observed sufficient-state, common start/legal/stop/success/cost contract,
its pathwise coupling therefore holds for every common history policy and
every finite horizon H, including choices of policy and H made from the data:

    Delta_t = 1-(1-e)^t,
    |p-p_hat| <= Delta_H,
    |J-J_hat| <= B_H = sum_(t=0)^(H-1) C_t Delta_t + D Delta_H.

Here C_t bounds pre-transition stage cost and D bounds once-only settlement.
After choosing H, use the same horizon and same cost contract for all compared
policies. Shared known policy fees enter both models identically. The FMT
buffered feasibility/2B_H comparator conclusion then applies unchanged to its
augmented cost. This is a consequence of one uniform model event, so choosing
a finite horizon or policy requires no second union over those decisions.

No infinite-horizon risk, sure safety or eventual nonvacuous certificate
follows. Missing rows can make Delta_H=1. A failed certificate does not prove
infeasibility. The policy, input law, fees and comparison margin must still
obey the inherited FMT contract; logging observations does not discharge it.

## ARC-3 — exact optional-monitoring failure and repair

For iid Bernoulli observations, consider two confidence sets, each uniformly
at least 3/4-valid at its fixed look. At n=2 return [0,1/2] if the first two
outcomes are 00, otherwise [0,1]. Failure is possible only for p>1/2, with
probability (1-p)^2 < 1/4. At n=3 return [5/8,1] if all outcomes are 111,
otherwise [0,1]. Failure is possible only for p<5/8, with probability
p^3 < 125/512 < 1/4.

Stop at look 2 on 00; otherwise use look 3. At the true p=3/5 the two
failure events are disjoint, with total probability

    (2/5)^2 + (3/5)^3 = 47/125 > 1/4.

Thus fixed-look validity alone cannot justify adaptive use. A constructive
two-look repair uses [0,2/3] at 00 and [1/2,1] at 111. The uniform union of
failure bounds is at most 1/9 + 1/8 = 17/72 < 1/4. ARC-1 supplies the analogous
preallocated guarantee over every finite look in a fixed row register.
These are exact confidence-set controls, not claimed optimal-width intervals.

## ARC-4 — accounting and the premises that remain

For fixed known per-draw charges a_r, sampling pays sum_r N_r(T) a_r;
any interface, reset, state-preparation, observation or sampler-control cost
must also be charged. Sufficient empirical counts need sum_r k_r integer
counters plus the known register; audit traces can require additional storage.
Confidence calculation, policy synthesis, model storage, private randomness,
controller representation and deployment are separate costs, as in FMT.

The primitive hypothesis is the conditional fixed row law. Replaying one
draw many times, revealing outcomes before selecting a row, drifting rows,
omitted support outcomes, or a hidden state that changes future laws violates
that hypothesis. Neither exact record parsing nor finite statistical checks
can certify its physical truth. This result closes adaptive sampling within
the supplied finite contract; learned state/support closure and physical
realization remain scientific work.
