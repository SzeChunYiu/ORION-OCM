# Probabilistic controlled acquisition — PCA-1--4

Date: 2026-09-13. Status: exact finite known-kernel extension of CA/CRA.
No novelty is claimed for belief-state control, graph reachability or dynamic programming.

## Primary parents and the adaptation

[Cimatti, Pistore, Roveri and Traverso, 2003](https://doi.org/10.1016/S0004-3702(02)00374-0)
separate strong planning from cyclic trial-and-error planning. Possibility of
eventual success does not make every support execution terminate. Here a
registered stochastic kernel supplies probabilities; fairness alone supplies
neither a numerical deadline guarantee nor an expected resource cost.

[Bertsekas and Tsitsiklis, 1991](https://www.mit.edu/~jnt/Papers/J034-91-berts-SSP.pdf)
provide the stochastic shortest-path parent. [Bertsekas's MIT Lecture 17,
pp. 3--6](https://ocw.mit.edu/courses/6-231-dynamic-programming-and-stochastic-control-fall-2015/d70106b7f8fd529d2976a360eb395425_MIT6_231F15_Lec17.pdf)
states proper-policy and Bellman conditions. We use their finite positive-cost
regime; this avoids improper zero-cost cycles. The adaptation makes the
controlled-acquisition obligation, persistent observation state and recovery
charges explicit. These are parent-assisted GMI scope repairs, not new SSP laws.

## Complete observed state and exact scope

Register finite states S with stopped successful goal g, finite nonempty legal
action sets U(s) for s != g, known rational kernels P(s'|s,u), and exact costs
0 < c_min <= c(s,u) <= c_max < infinity. Goal stops with zero additional
cost in this control-cost coordinate. A state includes every observed
configuration, sufficient posterior belief, resource and monitor variable
needed for its future law and legal successful stopping. The controller sees
this sufficient state, not a hidden state by fiat.

If the primitive system is partially observed, constructing a correct belief
update and a *finite closed sufficient-state set* is an additional premise.
A generic POMDP can have infinitely many reachable beliefs. Neither finite
latent state nor a surviving support set alone supplies this premise.
No unknown kernel, learned probability, unbounded resource or universal
physical-cost guarantee is claimed. An absorbing g means an adequate terminal
decision has actually been made under the registered obligation.

Let T be the number of controls before g. A deterministic policy is **sure**
if every execution following positive-probability transitions reaches g in
finite time, including infinite support paths of probability zero.
It is **almost sure** if Pr(T < infinity)=1. Its expected work is
E[sum_(t<T) c(s_t,u_t)], possibly infinity. Its horizon-H success is Pr(T<=H).
These are different specifications. Controller memory, compilation, arithmetic,
belief updates, terminal implementation and physical execution remain separate
resource coordinates; neither the table checker nor its runtime measures them.

## PCA-1 — stationary support and expected-work certificate

Fix a deterministic stationary policy, or a finite controller whose memory is
included in S, and an initial state. Let R be its reachable support states.

1. It is sure exactly when its reachable nonterminal support graph is acyclic.
2. It is almost sure exactly when every s in R has a support path to g.
3. In this finite stationary scope, almost-sure termination implies finite
   expected T and work. With n=|R minus {g}|>0 and minimum positive reachable
   transition probability p_min, put delta=p_min^n. Then
   Pr(T>kn) <= (1-delta)^k and E[T] <= n/delta.
4. If the policy is almost sure, its value is the unique finite solution
   V=c+QV on reachable nonterminal states, with Q their submatrix and V(g)=0.

**Proof.** A reachable nonterminal cycle can be followed indefinitely;
otherwise a path visits each nonterminal at most once. For (2), a reachable
state without a goal path gives positive probability of never succeeding.
Conversely every reachable state has a simple path to g of at most n steps,
of probability at least delta. Conditional on any surviving block of n steps,
the same lower bound applies. Iteration gives (3), and summing its tail gives
the expectation bound. Costs are bounded by c_max*T. First-step conditioning
gives (4); the geometric tail makes Q^k tend to zero and sum Q^k finite, proving
existence and uniqueness. For start g all quantities are zero. QED.

A verifiable optimality certificate is a finite nonnegative vector V with
V(g)=0, V(s)<=c(s,u)+sum P(s'|s,u)V(s') for every legal u, and equality for
a policy certified almost sure from every state. Its expected work equals V
and no history-dependent policy has smaller expected work. Indeed a competing
finite-cost policy has E[T]<infinity by c_min>0. Telescoping the inequalities
to T wedge k and letting k grow removes its bounded terminal remainder.
An infinite-cost competitor cannot improve V. This also covers randomized
competitors; deterministic policies already attain the certificate.

## PCA-2 — separate finite-horizon constructive laws

Set p_0(g)=1, p_0(s)=0 for s!=g, and J_0(g)=0, J_0(s)=infinity otherwise.
For h>=1, hold goal values fixed and define

p_h(s)=max_u sum_s' P(s'|s,u) p_(h-1)(s'),
J_h(s)=min_u [c(s,u)+sum_s' P(s'|s,u) J_(h-1)(s')].

For J discard an action with any positive-probability infinite child.
Then p_h is maximum horizon-h success, while J_h is minimum expected work
among policies guaranteed to succeed within h controls. They optimize
different constraints. Finite choices attain every finite optimum.

**Proof.** Condition on the first action and next observed sufficient state.
The remaining horizon decreases; independent optimal child policies can be
chosen for each observed successor. Induction proves both bounds and constructs
time-indexed Markov policies attaining them. Thus enumerating every such table
is a complete finite oracle for arbitrary history-dependent optima. QED.

## PCA-3 — persistent observation failure and constructive recovery

A probe seeks an exact reading of a fixed hidden bit. Its apparatus mode is
initially good/bad with equal probability, independent of that bit. Good mode
returns the bit and terminates correctly; bad mode returns failure and persists.
Observed sufficient states are M (fresh fair mode belief), B (known bad mode),
and g (reading or fallback already certified). Goal outcomes can be collapsed
after their adequate terminal decision. A reset redraws the mode independently
without changing the hidden bit. This independence is a stated process law.

| State/action | Next-state law | Charged control work |
|---|---|---:|
| M/probe | g with 1/2, B with 1/2 | 1 |
| B/probe | B with probability 1 | 1 |
| B/reset, when admitted | M with probability 1 | 1 |
| M or B/certify, when admitted | g with probability 1 | 5 |

**Failure stage.** Without reset or fallback, repeated probes succeed with
probability 1/2 and have infinite expected work. M and B cannot be merged into
an iid probe state: conditional success after a failure is zero, not 1/2.

**Recovery.** Admit and charge reset. Probe at M and reset at B yields
T=2K-1, with K geometric(1/2), hence success probability one, E[T]=3,
and Pr(T<=H)=1-2^(-ceil(H/2)). The all-failure support execution remains
infinite, so this policy is not sure. The actual expected values (M,B,g)=(3,4,0)
satisfy the optimality certificate even when cost-5 certification is available.
Thus the comparison uses the same legal action set as the strongest SSP parent.

**Sure recovery.** Probe at most k>=1 times, resetting between failures, then
certify after the kth failure. Every execution stops within 2k controls.
Expected work is 3+2^(-k), and worst work is 2k+4. In the full action model
J_(2k)(M)=J_(2k+1)(M)=3+2^(-k); J_1(M)=5. This follows by substituting the
two states into PCA-2 (or induction on the remaining horizon).
The independent checker executes latent modes and every small policy table.

The infimum expected work among deterministic sure policies is 3, but no such
policy attains it. A sure policy must eventually use certification on its
all-failure branch, which has a finite prefix of positive probability.
Certification has strictly positive Bellman slack (2 at M, 1 at B);
failed B/probe steps also have positive slack. The telescoping identity gives
expected work strictly above 3, while the k-cutoff policies approach 3.
Direct certification minimizes worst work at 5; the expected-cost cutoff
policies do not minimize that different objective.

## PCA-4 — the controller boundary is load-bearing

Finite physical state alone does not make every almost-sure history policy
have finite expected work. After the ith failed acquisition probe, execute
2^i additional failed B/probes before resetting, then retry. Each delay is
finite, so successful acquisition still occurs almost surely. The probability
of reaching delay i is 2^(-i); its expected work is one. Summing all delays
gives infinite expected work. This policy uses an unbounded failure counter
and is outside PCA-1's finite stationary/controller-state premise.

The constructive remedies are the admitted stationary reset controller for
finite expected work, or a finite retry counter plus certification for sure
termination. A missing reset/fallback cannot be inferred into existence.
Acquisition of their descriptions and full relevant lifetime costs must be
charged before translating these control-coordinate results to a GMI profile.

## Independent finite evidence

The model/checker/test filenames share stem grand_gmi_probabilistic_acquisition.
The checker enumerates all 6^4=1296 two-nonterminal/two-action kernels with
probabilities in {0,1/2,1}, fixed action costs 1 and 2, at horizon two.
Its oracle executes every time-indexed policy table along actual stochastic
paths. It separately checks all 49 three-state stationary support graphs at
all three starts, full recovery/fallback tables through horizon four, latent
mode persistence and cutoff costs, and eight growing-delay prefix controls.
The receipt GRAND_GMI_PROBABILISTIC_ACQUISITION_RECEIPT_V1.json binds finite
outputs; the proofs establish the general laws. This advances Q1 only within
the explicitly registered finite known-kernel, admitted-controller scope.

The finite-horizon [UMA-1–4 extension](FIXED_UNKNOWN_MODEL_ACQUISITION_THEOREM_V1.md)
handles a supplied finite family of fixed hidden kernels. Its common-policy
vectors preserve information through resets and distinguish fixed uncertainty
from rectangular row switching; learned coverage remains a separate premise.
