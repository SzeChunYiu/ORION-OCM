# Finite stochastic proper stopping — SPS-1–4

Status: exact rational SSP specialization, with known finite law and observed
sufficient state. This is an application of the primary
[SSP parents](PARENTS_AND_SCOPE_V1.md), not a new SSP optimality theorem.
It extends the repository's positive-cost PCA and deterministic ZCS interfaces.

## Register and policy class

Supply finite nonterminal states S, absorbing adequate goal g, finite actions
A(s) (possibly empty), rational P(y|s,a)≥0 summing to1, and finite rational
c(s,a)≥0. Goal has no further cost. Stopping is an admitted action to g:
its registered implementation charge is paid and that transition counts once.
The stage cost is the specified conditional expected scalar charge; if actual
charges affect legality or future dynamics, include their relevant state.
All transition laws, legal actions, stopping adequacy and charges depend on the
complete observed state, not on unrepresented history. Private randomization
does not reveal future transition draws.

For any randomized history policy, let τ be the number of actions before g,
Tπ(s)=E_s τ, and Jπ(s)=E_s Σ_(t<τ)c(S_t,A_t). Proper at s means Tπ(s)<∞.
Bounded stage costs then imply Jπ(s)<∞. Almost-sure termination alone is
weaker for history policies. Improper policies are excluded from the proper
optimization, even if accumulated charge is zero. Values outside the proper
viable domain are +∞ by specification, not by assigning an infinite charge to
every path of a proper policy. Model acquisition, synthesis and runtime resource
costs remain explicit separate obligations in the parent/cost document.

## SPS-1 — compute the entire viable domain and a proper policy

Start W=S∪{g}. For a current W retain only W-safe actions, whose positive
support lies in W. Form the directed support graph of these actions and replace
W by the vertices with a graph path to g. Repeat until unchanged; g remains.
Call the final nonterminal set V. Then V is exactly the states from which
some history policy terminates almost surely, and exactly those admitting a
proper policy. One deterministic stationary policy is proper from every s∈V.

**Proof.** Any almost-sure policy must stay in the current W at each
positive-probability history: induction excludes states removed earlier.
Consequently every action used with positive probability is W-safe. A state
without a path to g under these actions cannot terminate, so deletion never
removes an almost-sure viable state. This also treats randomized choices by
their conditional action probabilities; finite histories form a countable set.

At the fixed point, each state has a shortest graph path to g. Select a safe
action with a positive successor one distance closer to g. Other successors
may increase distance, but remain in V∪{g}. The selected stationary support
graph has a goal path from every state: repeatedly choosing that decreasing
successor gives one. If n=|V|>0 and p is the minimum positive selected
transition probability, each surviving block of n actions terminates with
probability at least p^n. Thus Pr(τ>kn)≤(1−p^n)^k and T≤n/p^n<∞.
This proves both completeness and simultaneous properness. For V empty there
is no viable nonterminal start. ∎

This is not ordinary existential graph reachability: an action with one goal
successor and one unavoidable trap is not safe. Safe actions can still include
zero-cost self-loops; restricting support alone does not make every policy proper.

## SPS-2 — one stationary policy attains the joint cost/steps optimum

On V restrict to safe actions. There exists a deterministic stationary μ
proper on all V such that, for every s∈V and every history policy π proper
at s,
- Jμ(s)≤Jπ(s);
- if Jπ(s)=Jμ(s), then Tμ(s)≤Tπ(s).

Thus the statewise lexicographic minima are attained by **one common policy**.
They are not arbitrary coordinate minima pasted from incompatible policies.

**Proof.** Add δ>0 to every nonterminal action charge. Truncated-horizon
minimum expected charge, with zero tail value, increases to a finite vector
vδ: SPS-1 supplies a common proper upper bound. Finiteness of the action sets
permits passing the limit through each minimum, so vδ satisfies Bellman.

Choose a deterministic stationary minimizing action for vδ at every state.
Telescoping its Bellman equalities to τ∧k gives
δ E(τ∧k)≤vδ(s). Hence it is proper; bounded vδ makes the surviving remainder
vanish and its total perturbed cost equals vδ. Finite-horizon induction bounds
every randomized history policy below by the truncated values, so this policy
is optimal for the perturbed problem against that full class.

Take δ_j↓0. There are finitely many deterministic stationary policies, so one
proper μ recurs infinitely often. On that subsequence, for every s and π proper
at s,

    Jμ(s)+δ_j Tμ(s) ≤ Jπ(s)+δ_j Tπ(s).

Taking the limit proves primary optimality; for equal costs, division by δ_j
proves secondary optimality. The same repeated μ works simultaneously at every
state. No finite user-chosen δ is asserted small enough for exact lexical
optimization. This specializes the established SSP perturbation argument. ∎

## SPS-3 — Bellman value, progress and exact finite construction

Write J=Jμ from SPS-2. On V,

    J(s)=min_(a safe) [c(s,a)+Σ_y P(y|s,a)J(y)],  J(g)=0.

It is the greatest **finite nonnegative** Bellman solution on V.
For another such solution w, its Bellman inequalities telescope along any
proper policy; the bounded terminal remainder vanishes, giving w≤Jπ.
Take π=μ. Bellman for J follows by taking the δ subsequence above.
The same inequality shows J is cost-optimal even against an almost-sure policy
with infinite expected τ; such a policy cannot improve the secondary time.

For a stationary safe policy, properness is equivalent to every support state
having a path to g. On proper policies let Q be the nonterminal matrix. The
geometric bound proves (I−Q) invertible and

    Jπ=(I−Q)^−1 cπ,       Tπ=(I−Q)^−1 1.

Enumerate finite stationary policies on V, reject improper ones, and solve
these rational systems exactly. Compute each state's lexicographic minimum;
return an enumerated policy attaining **all** of them, checking this equality.
SPS-2 proves such a policy exists. If V is empty return an explicit empty
viable set and infeasible outcomes. [Algorithms](ALGORITHM_AND_ORACLE_V1.md)
specifies independent occupancy-flow verification and operation accounting.

A compact independently checkable progress certificate consists of finite
nonnegative J,L on V, zero at g, with J(s)≤c+PJ for every safe action and
L(s)≤1+PL for every **cost-tight** action (J(s)=c+PJ).
The selected action must be tight in both equations. Telescoping the L equality
gives E(τ∧k)≤L(s), hence properness; the bounded remainder then vanishes and
the selected values equal (J,L). For a competing proper policy, the J
inequalities give its cost lower bound. If its cost equals J(s), the expected
sum of nonnegative Bellman slacks is zero, so it uses only cost-tight actions
at positive-probability histories. Telescoping the L inequalities there gives
its expected count at least L(s). Thus this finite certificate independently
checks the common policy's properness and lexical optimality. It requires all
safe actions, not merely those in a sampled search register. This is expected
drift, not a strictly descending pathwise rank.

A scalar Bellman minimizer is not enough: at a state with zero-cost wait and
cost1 stop, J=1, but choosing wait forever is improper. The repaired enumeration
returns stop, with (J,T)=(1,1). On the same graph every finite j∈[0,1] solves
the scalar equation, so uniqueness is not claimed.

Do not import ZCS's greatest **extended** solution claim: a zero-charge action
returning to itself with probability1/2 and reaching g otherwise has J=0,
T=2, yet w=+∞ also solves the extended equation. Finite/bounded comparison
functions on the viable domain are load-bearing.

## SPS-4 — exact boundaries and constructive controls

A geometric trial of cost1 and success1/2 has (J,T)=(2,2), and Pr(τ>k)=2^−k.
Its expectation is finite, but no deterministic pathwise length bound exists.
A deterministic zero-cost wait action plus a sure cost1 stop admits a history
policy that privately chooses finite N with Pr(N=n)=1/[n(n+1)], waits N times,
then stops. It is almost sure, has J=1 and T=∞. Our optimum stops immediately;
finite physical state does not force every history policy to be proper.

With a zero-cost half-success trial versus a cost1/4 immediate stop, the trial
is lexically better: (0,2)<(1/4,1). A finite perturbation δ>1/4 instead chooses
stop. Exact policy enumeration avoids treating a merely small δ as a proof.

Finiteness, nonnegative costs and the supplied complete kernel are premises.
Negative cycles can drive proper serving costs to −∞ without attainment;
unknown or partial state laws require another model/identification theorem.
The tests are exact finite mathematical controls, not native measurements,
new acquisition experiments or evidence for a universal physical optimum.
