# Additive-potential transfer — APT-1–4

A conditional common-policy transfer corollary of additive drift and
nonnegative-cost comparison. No new general drift, DP, SSP or learning
principle is claimed. The measurable theorem is primary; finite controls
validate arithmetic, not its general quantifiers.

## 1. Common interface and separately certified potentials

Use standard Borel states S, measurable absorbing stopped set T, X=S\T,
a common measurable legal-action graph, and supplied measurable policy kernels
on complete histories. Every admitted model K has a Borel next-state kernel
and a nonnegative measurable conditional expected charge c_K(x,a) before
transition. All revealed policy-relevant signals, including observed random
charges and retained private randomness, belong to the common history/state
interface. Conditional next-state and charge laws must have the stated row
form given the complete global history. Sufficient observed state, legality,
initial law mu, stop/adequacy labels and private-randomization law are common.
Finishes/resets are real charged actions. Include a terminal settlement in
the expected charge on its entering transition (and its model error), or in
an explicit charged finishing state. Costs are zero after absorption.

Data D precedes deployment. For fixed true model P, a supplied procedure has
a measurable coverage event E={P in C_D} with Pr_D(E)>=1-alpha. Deployment
retains the stated conditional P law after D; no future-good-event conditioning
is allowed. Let F be the measurable event that all certificates and required
policy choices below are supplied. All data-dependent choices are measurable.
For each D in F, select nominal Q in C_D and a nonempty supplied class Pi_D
of common history policies using only a retained action graph A_D at every
possible represented history, including nominally unreachable branches.

Supply finite measurable potentials L,V,B:S->[0,infinity), zero on T, with
mu(L),mu(V),mu(B)<infinity, and a finite measurable r(x,a)>=0 on A_D.
For every K in C_D and every retained nonterminal row, require

    K L(x,a) <= L(x)-1,
    c_K(x,a)+K V(x,a) <= V(x),
    |c_K(x,a)-c_Q(x,a)| + integral_X V(y)|K-Q|(dy|x,a) <= r(x,a),
    K B(x,a) <= B(x)-r(x,a).                             (A)

Here Kf denotes the killed next-state integral over X. The signed variation
measure |K-Q| is absolute measure, not half L1. The inequalities include Q
and empirically unseen rows. C_D may be correlated; enforcing all rows is
sufficient but need not yield an exact robust optimum. It does not equate
fixed-model uncertainty with a switching adversary.
Existence, measurability and verification of supplied certificates are explicit
premises; no universal synthesis algorithm or automatically available F follows.

## 2. APT-1 — properness and expected work without geometric transversality

Fix D in F, K in C_D and pi in Pi_D. Put tau=inf{t>=0:X_t in T}. Then

    E_K tau <= mu(L),    J_K(pi):=E_K sum_(t<tau)c_K(X_t,A_t) <= mu(V),
    Pr_K(tau>H) <= min(1,mu(L)/(H+1))    for integers H>=0.             (1)

**Proof.** Average each row inequality conditional on the complete history
and chosen policy action. For every finite H, induction/telescoping gives

    E_K[min(tau,H)]+E_K L(X_(tau wedge H)) <= mu(L),
    J_(K,H)(pi)+E_K V(X_(tau wedge H)) <= mu(V).

All expectations exist: each nonnegative remainder is bounded inductively
by its finite initial expectation. Drop the nonnegative remainder and use
monotone convergence of the duration and accumulated charges. This proves
finite expected stopping and work, hence almost-sure stopping. The last
inequality follows from tau>=H+1 on {tau>H}. QED.

No equality requiring E_K V(X_H)1{tau>H}->0 was used or asserted. Each
policy's actual expected work tail tends to zero because its total work is
integrable. This supplies neither a uniform work-tail rate over Pi_D nor a
geometric lifetime bound or deterministic deadline.

## 3. APT-2 — uniform undiscounted transfer from error potential

For every common pi in Pi_D and every K in C_D,

    |J_K(pi)-J_Q(pi)| <= b := mu(B).                                  (2)

**Proof.** Truncate both accumulated costs at the same finite H, with no
new deadline settlement. At every fixed complete history ending in x, Q's
remaining truncated cost lies in [0,V(x)], by backward induction using (A).
One row replacement changes immediate expected charge plus this common
continuation by at most r(x,a). The finite common-policy replacement recurrence
therefore bounds the absolute H-step value difference by

    E_K sum_(t<H,t<tau) r(X_t,A_t)
      <= mu(B)-E_K B(X_(tau wedge H)) <= mu(B).

The first inequality only uses the same policy on the same history; all newly
revealed signals must be in the kernel. The second follows by finite
telescoping of B. By APT-1 the two nonnegative truncated expected costs converge
to finite J_K,J_Q. Taking their difference proves (2). There is no unjustified
exchange of an infinite signed series and expectation, and no vanishing
envelope-remainder assumption. QED.

## 4. APT-3 — separately priced terminal-event error

For measurable G subseteq T, additionally supply finite measurable A>=0,
zero on T with mu(A)<infinity, and finite measurable epsilon(x,a)>=0 such that

    full-row TV(K,Q) <= epsilon(x,a),    K A <= A-epsilon(x,a)         (3)

for every retained row/model. TV here is half L1 / supremum over events.
Then for every common policy,

    |p_K(pi)-p_Q(pi)| <= d := min(1,mu(A)),  p_K=Pr_K(X_tau in G).     (4)

**Proof.** For success reached by H, terminal-indicator continuation is in
[0,1]. Each full-row replacement contributes at most epsilon. Telescope A
to bound the expected cumulative epsilon by mu(A). Both models stop almost
surely by APT-1; bounded convergence as H grows gives (4). Killed error alone
cannot distinguish terminal labels. Properness does not certify adequate
success if some terminal labels are unsuccessful. QED.

## 5. APT-4 — data-selected policies, comparator and costs

On E intersect F, all conclusions apply simultaneously to the supplied class
Pi_D; no extra policy union is needed. Put J_K^sigma(pi)=J_K(pi)+sigma(pi)
with the same registered finite nonnegative policy setup/seed fee in both
models. A supplied xi-optimal nominal policy (xi>=0) in Pi_D satisfies

    J_P^sigma(pi_hat) <= inf_(pi in Pi_D)J_P^sigma(pi)+2b+xi.

If instead xi-optimal within {pi in Pi_D:p_Q(pi)>=q+d}, it satisfies
p_P(pi_hat)>=q and this same regret bound against
{pi in Pi_D:p_P(pi)>=q+2d}, provided that comparator is nonempty.
Each true comparator is nominally feasible by (4); two applications of (2)
and nominal xi-optimality prove the claim. The selected policy's own
J_Q^sigma(pi_hat)+b supplies a work allowance; separate minima cannot be joined.

Exact attainment, physical implementation and synthesis require additional
premises. Policies outside Pi_D are not covered comparators.
Coverage alone does not imply F. Obtaining a covered certified policy has
probability Pr(E intersect F)>=max(0,Pr(F)-alpha); conditional coverage given
F need not be 1-alpha. Uncertified abstention is not successful execution.
Even finite cost for every dataset does not imply a finite global expectation:
that requires an integrable data-averaged deployment bound and integrable
acquisition/setup charges. A fallback needs separate termination/cost warrant.
The [parent and charge register](PARENTS_AND_COSTS_V1.md) preserves all
acquisition, support, state identification, storage and synthesis obligations.
