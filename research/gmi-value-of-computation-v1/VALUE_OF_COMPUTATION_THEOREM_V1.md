# Value of computation and exact stopping — corrected VOC-1–6

**Finite deterministic stopping interface with explicit feasibility.**
This repairs PR571 at [the preserved source](raw/pr571-743b9ded/SOURCE_BINDINGS_V1.json).
It does not supply a general stochastic, physical or acquisition-cost theorem.

## Primary parents and scope

[Bertsekas (2020), §§I–II](https://arxiv.org/html/1711.10129v2) distinguishes
termination, cost and the effective domain of proper policies. We use that
distinction in a finite deterministic shortest-path specialization, not his
infinite-state stochastic uniqueness theorem without its hypotheses.
[Hay et al. (2012), Theorem 5](https://arxiv.org/pdf/1207.5879) bounds expected
computation count in its metalevel model. Our path bound requires deterministic
transitions and policies, not merely deterministic per-step prices.
Russell–Wefald supplies the established nonmyopic decision perspective.
No ski-rental competitive theorem or new general metareasoning law is claimed.

## 1. Register

Let S be a finite nonempty state set encoding all decision-relevant registers.
Each state has finitely many certified terminal actions with rational cost
c>=0 and cognitive edges (s,t,e), with rational charge e>=0 and a deterministic
successor t. Policies are deterministic and may use full history. A successful
episode takes finitely many edges then a certified terminal action. Its cost
is the sum of all edge charges plus that terminal cost. Dead ends and infinite
nonserving paths are infeasible and have value +infinity, regardless of their
accumulated charge. Values take the extended **nonnegative** real range.

The declared prices account for these operations only. Search, verification,
synthesis, memory and platform costs require their own supplied accounting;
solving this model does not measure them or certify action adequacy.
The helper uses None exclusively for +infinity; it never treats failure as free.

## 2. VOC-1 — Bellman equality alone does not impose termination

For one state with terminal cost1 and a zero-cost self-loop, the bare equation
J=min(1,J) has every nonnegative solution J in [0,1]. The serving-policy value
is1. Choosing the self-loop forever does not serve the obligation.
Over unrestricted signed reals, every J<=1 solves the equation; the
nonnegative value domain is necessary for the stated exact interval.
This preserves the original ambiguity result.

## 3. VOC-2 — ranked recursion with a feasibility distinction

Augment the state by an integer k>=0. Each cognitive edge consumes exactly
one unit, and no edge is legal at rank0. The unique extended value is
J_0(s)=min A(s), and
J_k(s)=min(min A(s), min_(s,t,e)[e+J_(k-1)(t)]),
with min(empty)=+infinity.

Induction gives a unique value at every (s,k), since each successor has smaller
rank. When J_k(s)<infinity, a minimizing policy reaches a certified action
within k cognitive steps, and every optimal finite-cost policy does likewise.
When J_k(s)=+infinity, report INFEASIBLE; exhaustion alone does not serve.
The single rank-zero state with no action is the missing-premise countermodel.
If termination is required for every legal policy, every reachable rank-zero
state and earlier dead end must instead have a certified stopping action.

A cache must retain the complete state as well as rank. The old helper cached
only k: terminal10 at the root, zero-cost edges to terminal10 and terminal0,
and k=1 returned10 although the exact optimum is0. The corrected helper and
explicit state-table recursion distinguish those successors.

## 4. VOC-3 — positive costs on the viable domain

Require every cognitive edge charge e>=epsilon>0. Define V as the states
from which some finite path reaches a certified terminal action. Reverse
reachability computes V exactly. Set J(s)=+infinity outside V.

**Theorem.** On V the serving-policy optimum is finite, attained, and is the
unique finite nonnegative Bellman solution, with outgoing edges to S\V
assigned +infinity. An optimal path has no repeated state and hence at most
|V|-1 cognitive edges. For any initial state with a certified complete
serving-policy cost bound C, every optimal path has at most floor(C/epsilon)
cognitive steps. An immediately available terminal action is one such bound.

**Proof.** A serving path exists exactly on V. Removing a repeated-state
segment preserves its endpoint and remaining deterministic actions while
strictly decreasing cost. There are finitely many simple paths and terminal
choices, so their minimum is finite and attained. First-action decomposition
gives Bellman's equation. For any finite Bellman solution W on V, select a
minimizing action. A selected edge has W(s)=e+W(t), so a selected cycle would
give 0=sum e>0. The selected trajectory therefore terminates, and telescoping
shows W equals that policy's cost. Conversely, applying Bellman's inequality
along any serving path gives W no greater than its cost. Thus W=J.
Finally, m edges cost at least m epsilon and J<=C. These prove all assertions.

A local finite option does not give a bounded solution on the whole register:
state s has terminal1 and an edge to trap t; t has only a charge1 self-loop.
J(s)=1 but J(t)=+infinity, and J(t)=1+J(t) has no finite solution.
The corrected algorithm returns the finite value and the infeasible region.

**Stochastic boundary (not a counterexample to the deterministic theorem).**
At an unresolved state, stop costs3; each unit-cost trial succeeds with
probability1/2 and otherwise returns there; success permits terminal0.
Trials until success have expected cost2 and are optimal. Their step count
has P(N>m)=2^-m, so no finite path bound holds. In such an expected-cost model,
epsilon E[N]<=E[cost]<=C supplies an expected-count bound only.
A rule stopping after H failures costs2+2^-H, showing the distinction exactly.

## 5. Stopping, lookahead and safety — VOC-4/5

Use VOC2 with the decreasing rank included in the state, or VOC3 with positive
cognitive charges. These progress premises are required for a local minimizing
selector to define a globally serving policy.
Let A be the best immediate terminal cost and Q the best charged cognitive
continuation e+J(t). At a viable state, strict Q<A makes stopping suboptimal;
A<Q makes cognitive continuation suboptimal. If A=Q<infinity, both are optimal.
A declared **stop-on-ties** policy continues iff Q<A. This is an optimal
selection convention, not a claim that all optimal policies stop on ties.
The difference A-J(t) is used only when both values are finite; the direct
charged comparison also handles unavailable immediate actions.
Without progress, s can have zero-cost edges to itself and terminal0 at t.
The serving values are both0, but choosing the tied self-loop never serves.
The executable chooser requires certified VOC3 values and positive charges;
it does not validate an arbitrary supplied value table as a Bellman solution.
ranked decisions instead use their decreasing-rank successor values.

The myopic alternative replaces J(t) with the best immediate terminal cost.
For two probes costing1 each, initial and singly probed states have terminal10,
while the doubly probed state has terminal1. One-step terminal lookahead stops
at10; the full recursion pays3. This is VOC-4's valid nonmyopic witness.

For VOC-5, a common adequate action may cost10 while a cost1 probe followed
by a certified model-specific action costs1 in each of two possible worlds.
The probe policy costs2 in **both** branches. This pathwise feasibility and
cost comparison refutes “common safety implies economic optimality.”
The observation-branching example is not used to import stochastic Bellman
optimality into the deterministic theorem above.

## 6. VOC-6 — exact decisions need certified comparisons

The two rational action-cost rows (1,1+2^-42) and (1+2^-42,1) have opposite
singleton argmins. There is **one unordered** conflicting row pair (or two
ordered pairs). The original prose's count2 and its test's count1 used
different conventions. Both floating values are exactly representable, yet
relative tolerance1e-12 treats both rows as tied and loses that conflict.

Use exact rational comparisons, or outward error intervals with an explicit
NUMERICALLY_UNRESOLVED outcome for uncertified signs. Epsilon-optimal sets are
valid only when the protocol and claims consistently use that relaxed meaning.
This example does not establish an error in any separately frozen population.

## 7. Evidence ceiling

[The correction context](VOC_REPAIR_CONTEXT_V1.md) links original and new
controls. Exact stationary-policy and path enumeration independently challenge
the finite solver, including genuine dead ends and the original clean fixture.
These checks do not establish arbitrary-language or hardware optimality,
action verification, stochastic metareasoning, or full cognitive costs.
The unit remains outside the grand replay capsule.
