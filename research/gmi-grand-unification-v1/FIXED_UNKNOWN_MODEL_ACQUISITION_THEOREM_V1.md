# Fixed unknown models, adaptive acquisition and rectangularity — UMA-1–4

Date: 2026-09-13. Status: exact finite known-hypothesis extension of PCA.

## 1. Primary mechanisms and subtraction

[Duff (2001), §2](https://proceedings.mlr.press/r3/duff01a/duff01a.pdf) explicitly
identifies the finite-matrix Bayes-adaptive case with a POMDP: the unknown
transition matrix remains constant, and observed transitions update information
about it. Its finite-horizon policy-vector construction is the parent of UMA-1.
[Iyengar (2005), §2, Assumption 1](https://doi.org/10.1287/moor.1040.0129) specifies
rectangularity as closure under pasting conditional transition laws, enabling
robust Bellman recursion. Its robust game is the parent of UMA-3. Neither parent
mechanism is claimed novel. We apply them to charged acquisition/recovery and
repair the inference from a fixed unknown model to unrestricted row switching.

[PCA](PROBABILISTIC_CONTROLLED_ACQUISITION_THEOREM_V1.md)
assumes a known sufficient-state kernel or an independently supplied finite
belief closure. This unit instead registers finitely many candidate kernels
and a finite horizon. Finite latent models do not imply a finite infinite-horizon
belief closure, nor does this result inherit PCA's unbounded termination claims.

## 2. Complete finite register

Register finite observed physical states S, stopped successful state g, finite
state-dependent legal actions U(s), and k>=1 candidate rational kernels
P_theta(s'|s,u). All candidate rows sum to one; U(s) is common to every theta.
Exactly one hidden theta is selected before execution and remains fixed.
Each chosen control costs a known finite nonnegative rational c(s,u), common
to the models. Resources or observations affecting later laws belong in S.
The controller observes its entire action/state history and its private coins.
No experiment is assumed to identify theta unless its actual outcomes do so.

The finite integer horizon H>=0 counts chosen controls, including an explicit
finish control if successful output takes a step. Stopping at g costs zero
further work. A deadline or non-goal dead end aborts unsuccessfully, paying the
registered finite cleanup charge d(s); d(g)=0. That forced abort is the external
deadline protocol, not an additional available action. Its implementation cost
is included in d. Thus every admitted episode ends; success and mere termination
are distinct. A finite plan has at most H controls plus the charged abort rule.

The kernel *hypothesis register* is supplied. It is not a learned-model coverage
or confidence certificate. If the actual process lies outside it, the following
guarantees need not hold. A Bayesian prior w is another supplied declaration;
it is neither calibrated by this theorem nor required for worst-model analysis.

## 3. UMA-1 — exact common-policy vectors without changing the model

For a deterministic history policy pi, let f_theta be its probability of not
successfully stopping by H and J_theta its expected total registered work.
Let V_h(s) be its attainable vector set, ordered as (f_1,...,f_k,J_1,...,J_k).
At g use (0,...,0); at a deadline/dead end use (1,...,1,d(s),...,d(s)). Otherwise,
choose one common u and one common child vector v_(s') in V_(h-1)(s') for each
observable successor with positive probability in at least one model. Form

    f_theta = sum_s' P_theta(s'|s,u) f_theta^(s'),
    J_theta = c(s,u)+sum_s' P_theta(s'|s,u) J_theta^(s').

Take the union over all such choices. This computes the full attainable set;
componentwise pruning computes its exact Pareto frontier for monotone upper
bounds. Keep all theta coordinates, including models of zero likelihood on a
particular entering history. A shared child can succeed differently under them;
a zero transition coefficient, not an unjustified policy reoptimization,
removes an impossible model's contribution at its parent.

**Proof.** Every finite policy chooses a common first action and observes s'
before choosing its continuation. Conditional on fixed theta, first-step
conditioning gives the two expressions with that *same theta* in every child.
Conversely every listed child choice constructs one observation-contingent
policy. Induction on h proves completeness and attainability. A dominated child
can be replaced without increasing any parent coordinate because transition
weights are nonnegative. Hence pruning preserves all monotone feasibility and
optimum questions. Separate histories revisiting (h,s) may select different
members of V_h(s); this is not a restriction to a memoryless physical-state rule.

In particular, per-model failure bounds and expected-work bounds are decidable
by testing a *single common vector*. Expected cost under w is sum w_theta J_theta;
fixed-model robust expected cost is max_theta J_theta. Do not minimize each
model coordinate separately or replace this outer maximum by one at every step.
Expected-work bounds are not per-run bounds on the realized work.

For a supplied prior, the update after s,u,s' is
w'_theta proportional to w_theta P_theta(s'|s,u). A zero denominator signals an
impossible observation under that register. A reset that preserves theta does
not erase this posterior. The vector construction remains valid without a prior;
it supplies a precommitted fixed-model optimum, not a claim that static minimax
has a scalar, time-consistent Bellman law on physical state or surviving support.

## 4. UMA-2 — private randomization and constructive minimax

Suppose nature selects theta before an independent private policy seed; nature
knows the policy, not that seed. Fixing all private randomness yields a
deterministic finite history tree. There are finitely many such trees, so all
randomized profiles form their convex hull. Conversely sampling a tree realizes
any convex combination. Thus finite rational joint constraints are linear
programs; feasibility and finite optima have rational witnesses when nonempty.
Pruning dominated deterministic vectors still preserves these monotone questions.

For success probability one under every model, a mixture may put positive
weight only on deterministic vectors with every f_theta=0. Let their distinct
cost vectors be v_i. If this set is empty, such success is infeasible, even with
randomization. Otherwise the exact private-randomized minimax is

    min z subject to lambda_i>=0, sum_i lambda_i=1,
                     sum_i lambda_i v_(i,theta)<=z for every theta.

An optimal vertex has at most k positive weights: if r weights are positive,
normalization and r independent active model inequalities must determine those
r weights and z, so r<=k. Enumerating supports and active rows, solving their
rational linear systems and checking every inequality constructs a certificate.
The implementation uses precisely this complete vertex enumeration.

Random sampling is zero in that control-work coordinate only. If a declared
sampler charges a fixed initial work delta>=0 whenever a nontrivial mixture is
used, total optimum is min(D,R+delta), where D and R are deterministic and
private-randomized minimax control work. Setup is before the H-control episode
and is charged separately. This is an explicit sampler contract, not a universal
physical cost law. Controller storage, compilation and random-bit generation
beyond this contract require their own accounting.

## 5. UMA-3 — when the rectangular recursion describes a different problem

Now allow nature to select any candidate theta *after each realized action*,
using the current observed history. It may paste rows from different models
across time and states/actions. For policies that succeed within H under every
such choice, define R_0(g)=0 and R_0(s)=infinity for s!=g, with

    R_h(s)=min_u [c(s,u)+max_theta sum_s' P_theta(s'|s,u) R_(h-1)(s')].

Reject an action with any positive-probability infinite child; goal remains zero.
The ordinary finite-horizon robust induction proves this formula for that
rectangular game. Randomization cannot improve it when nature sees each action:
a mixture averages the action-wise worst responses and cannot beat their minimum.
Every fixed model is an admitted nature policy here. Thus its uncertainty class
contains the fixed-model class, but equality is a premise to prove, not assume.

The counterexample below violates global row coupling, not robust dynamic
programming itself. The rectangular hull also contains an always-failing *fixed*
probe kernel absent from the original two-model register. We therefore do not
claim that temporal switching always changes values for rectangular registers.

## 6. UMA-4 — reset preserves acquired model information

Use observed states M (ready apparatus), B (blocked), R (answer ready), g (finished).
Probe a costs 1 and goes to R under theta0, B under theta1. Probe b costs 1
and reverses those two destinations. At B an admitted reset costs 1 and returns
to M while preserving theta. Fallback from M or B costs 5 and reaches R.
The sole R/finish action costs 1 and reaches g. Deadline abortion costs 1 outside
g. All compared controllers have the full listed action set and H=4.

Probe a; on failure reset and probe b; then finish. This common history policy
has costs (2,4) and succeeds in both fixed models. Its symmetric peer has (4,2).
Every probe-first policy pays at least 2 in the model where it works and at
least 4 in the other: after failure, reset plus the opposite probe plus finish
is cheapest; fallback plus finish would add 6. Fallback-first costs (6,6).
These first actions exhaust all policies, proving successful Pareto costs
{(2,4),(4,2)}. Deterministic minimax is 4. A fair mixture costs (3,3), and the
sum-of-coordinates lower bound 6 proves randomized minimax 3. With sampler
setup delta=1/4, the optimum is 13/4, still below deterministic 4.

Without reset, probe-first costs (2,7) or (7,2), and direct fallback costs (6,6).
These exhaust successful useful policies. Deterministic minimax is 6; the fair
mixture gives the exact private-randomized minimum 9/2, or 19/4 including setup.
Thus reset improves the strongest admitted comparison under both policy classes.
With H=3, the two-probe repair cannot also finish; deterministic minimax is 6.

In the rectangular game, nature can make every probe fail. Any successful
policy must use fallback and finish on that branch, costing at least 6; direct
fallback attains it. Without fallback, fixed-model repair still succeeds while
the rectangular game's optimal guaranteed success probability is zero.
A failure of a identifies theta1 in the fixed register; reset preserves this
information. Replacing that conditional law by arbitrary row switching would
incorrectly erase the acquired knowledge and reject a feasible cheaper policy.

## 7. Representation, development and exact finite evidence

The register contains k times the number of legal state/action/next-state triples
in rational kernel entries, plus action and abort costs. Its acquisition, coverage
proof, native verification and description bytes are additional costs. Policy
vectors have 2k rational entries. There are at most (H+1)|S| DP subproblems, but
child-policy combinations can grow exponentially; no scalable synthesis claim
is made. The receipt counts generated common-tree candidates, weighted terms
and rational minimax bases, not total CPU instructions or bit complexity.

An independent oracle enumerates complete common history trees and executes
all stochastic terminal paths while holding theta fixed. A separate complete
nature-table enumeration checks the rectangular game. The finite census covers
all 81 two-model/two-action success-probability registers over {0,1/2,1} at H=3,
including infeasible, zero-likelihood and non-identifying cases. The apparatus
witness additionally charges resets, finish and aborted deadlines. No result
certifies a model learned from data or an unregistered infinite-horizon ecology.
