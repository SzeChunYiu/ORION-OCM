# Objectives, planning and the value of computation

Status: exact finite dynamic programming and a discounted infinite-horizon
extension, conditional on a sufficient controlled state and explicit costs.

## AG1: an objective is additional information

Keep one environment and two legal actions \(a,b\). Utility \(u(a)=1,u(b)=0\)
selects \(a\); utility \(v(a)=0,v(b)=1\) selects \(b\). All facts about the
environment can be identical. Consequently truth-estimation axioms alone
cannot select the objective or optimal action. A viability predicate can supply
an objective when it is explicitly declared; its preferred trade-offs are not
deduced from probability normalization.

## AG2: finite planning from controlled consequences

Assume finite observed sufficient state \(s\), nonempty finite legal actions,
known controlled transition \(P_t(s'\mid s,a)\), finite horizon \(H\), and
bounded stage/terminal rewards \(r_t(s,a),g(s)\). A history-dependent reward
can be included by augmenting the state; this may increase memory substantially.
Define
\[
V_H(s)=g(s),\qquad
V_t(s)=\max_{a}\{r_t(s,a)+\sum_{s'}P_t(s'\mid s,a)V_{t+1}(s')\}.
\]
**Theorem.** A maximizing action at each \((t,s)\) forms an optimal policy,
even compared with all randomized history policies using the same information.
**Proof.** At \(H\) the reward is fixed. Assume the claim at \(t+1\).
Conditioning any policy's return on its first action and successor state bounds
its continuation by \(V_{t+1}\). A mixture of first-action values cannot exceed
their maximum. Choosing a maximizer and an optimal continuation attains that
maximum. Backward induction proves the assertion and constructs the policy.
Stored policy tables and Bellman computation are not free physical operations.

In partial observation, a correctly specified posterior over hidden state is
a sufficient controlled state when observations/transitions are known and the
belief update is retained. The resulting belief space is usually infinite;
finite-state solvability does not automatically carry over. Misspecified
state aggregation requires a simulation/error theorem, not this recurrence.

## AG3: infinite horizon with discount

For finite state/action spaces, stationary bounded reward and \(0<\gamma<1\),
let \((TV)(s)=\max_a[r(s,a)+\gamma\sum_{s'}P(s'\mid s,a)V(s')]\).
For every \(V,W\),
\(\|TV-TW\|_\infty\le\gamma\|V-W\|_\infty\): each action expectation
is a contraction and maxima preserve the common bound.
Thus iterating \(T\) has a unique bounded fixed point. If \(|r|\le R\),
truncation after \(H\) rewards has tail at most
\(R\gamma^H/(1-\gamma)\), proving that this fixed point is the supremum
of infinite discounted returns; finite-action greedy selection attains it.
This is discounted optimality, not a sure finite-time target guarantee.
Model-error transfer is [CMP5](COMPOSITION.md); undiscounted objectives require
additional recurrence, proper-policy, mixing or summability assumptions.

## RES1: exact finite resource feasibility

For a declared finite resource-state register, append remaining resources and
live allocations to \(s\). Admit only actions whose entire transition charge
is feasible; update the register using actual additive/max/scheduling rules.
AG2 then computes the best feasible reward. Alternatively, retain complete
attainable vectors and remove only componentwise dominated ones after every
backup. A coordinatewise minimum can be unattainable: alternatives \((1,3)\)
and \((3,1)\) do not yield a feasible \((1,1)\) alternative.

The state must include transient allocations and shared dependencies if they
affect feasibility. An expected charge below the allowance does not imply a
pathwise bound. Infinite model synthesis is not rendered computable by naming
its optimum; arbitrary program reachability still contains the halting problem.

## RES2: metareasoning is planning over paid computation

Assume a finite reachable metalevel state register, a finite legal computation
set at each state, finite costs and bounded stop values. Let \(z\) contain the
current executable decision information and resource
state. Stop value \(U(z)\) is the best *currently implementable* final decision
under that state. A legal computation/experiment \(c\) costs \(k(z,c)\ge0\)
in the declared scalarization and changes state through known kernel
\(K(z'\mid z,c)\). For at most \(m\) remaining computations,
\[
W_0(z)=U(z),\qquad
W_m(z)=\max\left(U(z),\max_c[-k(z,c)+\mathbb E_K W_{m-1}(Z')]\right).
\]
The AG2 induction proves optimality among these finite metapolicies. The
worth of the next computation is its continuation value minus its full cost
and the current stop value. Learning, experimentation and planning can share
this action interface while retaining different transition laws.

For a free, purely informational signal with no state change, the expected
optimal post-signal decision value is at least the pre-signal value: the old
decision remains available after every signal and has unchanged average payoff.
Subtracting a positive signal cost can reverse the choice. Information that
changes the world requires the full controlled kernel instead of this argument.

Myopic value is not generally sufficient. Example: hidden \(X\) is fair;
reward 1 for a correct final guess. Computation 1 produces an independent fair
key \(K\); computation 2, available only afterwards, produces \(X\oplus K\).
Each costs \(1/10\). Stop value is \(1/2\). After the first computation alone
the expected value is still \(1/2\), so a myopic policy rejects it. Both reveal
\(X\), giving net value \(1-2/10=4/5\), which the two-step recurrence chooses.
This is an exact failure and its constructive deeper-planning repair.

## RES3: no free metalevel or uniquely forced architecture

Evaluating \(W_m\), acquiring \(K\), storing the controller and calling
external tools themselves consume resources. An executable instance must
implement and charge them, or present the recurrence solely as an oracle bound.
Adding an uncharged optimizer one level higher does not solve this problem.
For finite candidate controllers one can enumerate their entire charged
profiles and choose the best, but enumeration cost must itself be included in
any end-to-end efficiency claim.

If implementations \(i,j\) have known one-off costs \(A_i,A_j\), per-use
costs \(c_i,c_j\), equal adequate behavior and known horizon \(H\), then
\(i\) is cheaper exactly when
\(A_i-A_j+H(c_i-c_j)<0\). The equality threshold follows by rearrangement
when \(c_i\ne c_j\). This is a conditional architectural prediction with a
falsifier: measured full costs violate the registered crossing. Changing the
ecology, precision, compiler or workload changes the premises and must be
recorded, not fitted after seeing the outcome.

## Parent relation

AG2/AG3 are Bellman dynamic programming and discounted contraction. RES2 is
decision-theoretic metareasoning, and RES3 retains its implementation issue:
[Russell and Wefald, *Principles of Metareasoning*](https://iiif.library.cmu.edu/file/Newell_box00014_fld01011_doc0001/Newell_box00014_fld01011_doc0001.pdf).
The GMI synthesis couples these parents to its obligation, access, development
and full-cost contracts. It does not invent utility from observations.
