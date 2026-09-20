# R11 control sufficiency and R12 claim-scope repair

This successor implements Round C of `../gmi-1068-recursive-audit-v3/FREEZE_V3.md`
(remote freeze commit `3a56e2d1fe83909a9fb9bed10dbd8d14d32d2b65`).
It supplies conditional control mathematics, a counterexample and an evidence
audit. It does not re-earn R11/R12 or their stale dependencies. Historical V1
files remain unchanged. Proofs below are mathematical proofs; the executable
checks are exact finite examples, not Lean verification of the general results.

## T1. Exact controlled quotient

Let S, Z and A be finite nonempty sets, with the same admissible action set A at
every state in both systems. Let phi:S->Z be onto. Let P and Q be normalized
nonnegative transition kernels, r and b rewards, and 0<=gamma<1. Suppose for all
s,a,z:

    r(s,a) = b(phi(s),a)
    sum_{s':phi(s')=z} P(s'|s,a) = Q(z|phi(s),a).

Then the process of abstract states and actions under any policy based on
abstract histories has the same finite-trace law as the abstract MDP, when its
initial law is the pushforward of the ground initial law. Expected discounted
reward is preserved. In particular, V*(s)=W*(phi(s)), and every optimal abstract
stationary policy lifts to an optimal ground policy.

Proof. Equality of initial abstract laws starts an induction on trace length.
Given an abstract history, the same policy uses the same action law. Conditional
on any ground state in its final fibre, the assumed aggregated next-state law
is Q. Mixtures over ground states therefore still give Q. Multiplying the common
next-action and next-state probabilities proves the next trace equality. Rewards
are equal on each state-action fibre. Boundedness of rewards on finite sets and
gamma<1 justify the limit of expected finite discounted sums.

For optimality against even ground-state-dependent policies, define Lw=w o phi
and the Bellman optimality operators T and U. The hypotheses give T L = L U.
Both operators contract sup norm with factor gamma: each stochastic expectation
is nonexpansive, and |max_a x_a-max_a y_a|<=max_a|x_a-y_a|. Their fixed points
are unique. Thus L W* is the unique fixed point V*. The same argument for any
fixed lifted stationary policy, and then an abstract optimal policy, proves the
policy assertion. Existence of deterministic stationary optimum follows here
by taking a maximizing action at each state of the unique Bellman fixed point;
finiteness guarantees an action attaining the maximum. QED.

These are sufficient conditions, not necessary conditions for preserving a
particular optimal policy. They preserve controlled reward information, not only
passive observations, a prediction loss, or representation variance.

## T2. Approximate quotient and explicit loss budget

Keep T1's finite spaces, common actions, stochastic kernels and discount. Assume
both |r(s,a)|<=R and |b(z,a)|<=R for a declared R>=0. Let

    TV(p,q) = (1/2) sum_z |p(z)-q(z)|,
    epsilon_r = max_{s,a} |r(s,a)-b(phi(s),a)|,
    epsilon_p = max_{s,a} TV(phi_*P(.|s,a),Q(.|phi(s),a)),
    B = epsilon_r/(1-gamma)
        + 2*gamma*R*epsilon_p/(1-gamma)^2.

Then

    ||V* - L W*||_infinity <= B,
    0 <= V*(s)-V^{lift(pi_bar*)}(s) <= 2B

for an exactly optimal abstract policy pi_bar*. The same B bounds the difference
between the values of any stationary abstract policy and its lift. All residuals
must hold uniformly over every ground state and action. Sampled-state averages
or errors under one behavior policy do not establish this premise.

Proof. For any p,q and real w, subtract min(w) from w to obtain
|E_p w-E_q w|<=span(w) TV(p,q). Every discounted value of either model lies in
[-R/(1-gamma),R/(1-gamma)], hence its span is at most 2R/(1-gamma).
Consequently, for any abstract value in this range,

    ||T Lw - L Uw|| <= delta,
    delta = epsilon_r + 2*gamma*R*epsilon_p/(1-gamma).

Apply this at w=W*. Insert and subtract T L W* in the fixed-point difference.
Contraction gives D<=gamma*D+delta, so D<=delta/(1-gamma)=B.
Replacing maximizing Bellman operators by policy operators proves the analogous
fixed-policy result. For pi_bar*, W^{pi_bar*}=W*. Insert L W* between V* and the
lifted policy value and use the two bounds to obtain 2B. Nonnegativity is the
definition of optimality. QED.

If a stationary abstract policy is only eta-optimal uniformly, the same insertion
gives 2B+eta. This is a value-approximation bound, not a sample-complexity, optimization,
model-identification or computation-cost theorem. It is conservative and no
tightness claim is made. gamma=1 is deliberately outside the theorem.

## C1. Perfect latent prediction plus noncollapse can lose control

At time t the full observation is S_t=(U,B_t), where U is a fair bit sampled once
at the start of an episode, and the B_t are fresh independent fair bits, also
independent of U. A_t is a bit and r(S_t,A_t)=1[A_t=B_t]. The full agent observes
the current B_t before acting. The compressed agent observes only
phi(S_t)=2U-1; it may retain its entire past latent/action/reward history.

The next-latent predictor f(z,a)=z has zero squared prediction loss. Under the
initial ensemble, E[phi]=0 and Var(phi)=1: this representation has not collapsed.
The full policy A_t=B_t receives reward one at every step. Conditional on the
compressed agent's information, current B_t remains an independent fair bit.
Even randomized history-dependent compressed policies therefore have expected
reward 1/2 at each step. Averaging over the declared initial distribution,

    full optimal value = 1/(1-gamma),
    best latent-history value = 1/[2(1-gamma)],
    gap = 1/[2(1-gamma)].

The expectation over initial states is essential: a fixed latent action can
accidentally match a particular initial B. The reward compatibility premise in
T1 fails within each phi fibre. Predicting reward too would expose this defect.
The counterexample concerns next-latent prediction, not prediction of the full
next observation. It does not refute JEPA experiments or their conditional
identifiability results.

A separate, non-finite extension takes persistent U~N(0,1) and independent fresh
B_t. phi=U then also has an exactly Gaussian marginal and perfect latent
prediction, while the same reward gap persists. This shows that marginal
Gaussianity alone does not imply control sufficiency. It is outside T1/T2's
finite-state setting and outside the OU/correct-dimension assumptions of the
LeJEPA identifiability theorem; it is not a counterexample to that theorem.

## T3. Rollout error: upper bounds and a parent-proof import restriction

For a fixed action sequence, suppose F_a is Lambda-Lipschitz and the residual on
the true state is at most d. With e_0=0, triangle inequality gives
e_{k+1}<=Lambda e_k+d, hence e_H<=d sum_{j=0}^{H-1} Lambda^j. This is an upper
bound; Lambda>1 does not establish actual exponential growth. For example, an
exact model has zero residual and zero rollout error at every horizon.

The inspected primary source Terver et al., arXiv:2512.24497v4, Appendix D,
Proposition 2(b), uses a single-point vector mean-value identity to infer a
lower distance bound from the minimum singular value of a Jacobian. That step
is not valid for general vector maps. An explicit counterexample to the step is

    F(x,y)=3 exp(x) (cos(y),sin(y)).

On the line segment x=0, 0<=y<=2*pi, J_F is 3 times an orthogonal matrix, so its
minimum singular value is 3 everywhere. Nevertheless F(0,0)=F(0,2*pi), despite
distinct endpoints. The correct vector formula integrates the Jacobian along
the segment, and cancellation can destroy expansion. This establishes a proof
step defect; it is not presented as a fully instantiated counterexample to
every additional trajectory premise of the source proposition.

A sufficient repair is to assume the finite-distance condition
||F_a(x)-F_a(y)||>=ell||x-y|| on all relevant true/predicted pairs. Then reverse
triangle inequality gives e_{k+1}>=ell e_k-d. If ell>1 and e_1>d/(ell-1), induction
yields

    e_H >= ell^(H-1)e_1 - d sum_{j=0}^{H-2}ell^j.

The additional finite-distance assumption must be independently verified;
pointwise singular values alone cannot discharge it. Upper-bound Proposition 1
can be imported at its Lipschitz scope; nonlinear lower-bound Proposition 2(b)
is held open pending repair. No source-wide rejection follows from this defect.

## Family reductions require explicit premises

`FAMILY_REDUCTION_SCOPE_V2.json` records representative reductions and their
imports. A simulation/encoding preserves chosen behavior only after an encoding
and decoder have been supplied. A claimed learning equivalence additionally
needs update preservation, including optimizer state and randomness. A resource
claim additionally needs measured or proved simulation overhead. Naming a
family after a finite witness does not meet these further requirements.

For example, given finite energies E_i, positive reference weights mu_i summing
to one and tau>0, minimizing sum_i p_i E_i + tau KL(p||mu) gives
p_i=mu_i exp(-E_i/tau)/Z. Indeed the objective equals
tau KL(p||p*)-tau log Z, so p* is its unique minimizer. This conditional identity
uses the chosen measure and energy. Dot-product attention further specifies
vector features, bilinear compatibility, mask, temperature and value readout.
Neither those choices nor a full Transformer follow from a multiplexer witness.
Likewise Bayesian conditioning requires a prior and likelihood; backpropagation
requires a specified differentiable computation graph and loss; stochastic
diffusion requires actual transition kernels and a training objective.

## Source ownership and remaining obligations

Finite MDP abstraction, Bellman contraction and simulation-style error bounds
are established parent mathematics, restated with a full proof for this GMI
application. See Givan, Dean and Greig (2003), Ferns, Panangaden and Precup
(2004), and Abel, Hershkowitz and Littman (2016) in `SOURCES_V2.json`.

Klindt, LeCun and Balestriero, arXiv:2605.26379v1, Sections 3, 5 and 7 and
Appendix D.2, separates encoder identification from action-conditioned dynamics
identification. Its guarantee depends on specified latent/world assumptions,
matched dimension and a population objective; it is not an assumption-free
world-model theorem. We do not import its formal verification as our own.

This successor does not estimate uniform residuals for a learned model, rerun
JEPA training, establish all 52 source findings as GMI consequences, prove unique
architecture discovery, or discharge the R4--R10 lineage. The 52-row audit is
exhaustive only over the frozen R12 registry. `PROGRAMME_COMPLETENESS=false`.
