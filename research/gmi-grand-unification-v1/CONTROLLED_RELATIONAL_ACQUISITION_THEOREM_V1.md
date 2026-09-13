# Controlled relational acquisition theorem — CRA-1--3

Date: 2026-09-13. Status: exact finite deterministic constructive bridge.

ACL-1 correctly evaluates the coupled process, and ACL-2b checks an admitted
complete policy. Neither is a general synthesis algorithm. TDA-1 instead
solves fixed-world testing and explicitly excludes state-changing tests.
This module supplies the missing finite controlled synthesis law; it does
not invalidate those narrower statements or introduce a new planning parent.

## 1. Complete configurations and observation-conditioned control

Register finite nonempty configuration set `S`, finite control actions `U`,
finite observations `O`, and finite nonempty terminal actions `A`. For each
configuration/control pair, `T(s,u)` is a deterministic successor or undefined
(illegal); when legal, `obs(s,u)` is the emitted observation. The controller
knows its selected action and observation, not the latent configuration.

`Gamma(s) subseteq A` specifies the legal successful terminal actions and may
be empty at irrecoverable states. A terminal decision ends the process. A
policy must terminate successfully for every initial configuration. Every
configuration includes all variables needed to determine future transitions,
action legality, observations and obligations: protection flags, consumed
resources, deadlines or initial-state information cannot be silently omitted.
Finite-state monitors may encode protected history when they actually exist.

The required finite belief-controller, update and output tables and their
execution are admitted. Their computation, storage and physical resources
remain separate coordinates. The
exact step count below charges control actions; terminal action and controller
costs are not implicitly zero in a complete physical profile.

For a nonempty possible-current-configuration set `B subseteq S`, define

`Legal(B) = {u: T(s,u) is defined for every s in B}`,
`C(B) = intersection_{s in B} Gamma(s)`, and, for `u in Legal(B)`,
`B[u,o] = {T(s,u): s in B and obs(s,u)=o}`.

Retain only nonempty observed successors. A legal action always has at least
one. An illegal action is not certified by an empty set of successor branches.
If every intermediate state must obey a safety predicate, forbid an action
unless all its successors are safe and require the initial belief to be safe.

**CRA-1 — exact controlled information state.** `B[u,o]` is exactly the set
of configurations compatible with the extended action/observation history.

Proof. Each compatible pre-action state has the declared deterministic
successor, and it survives exactly when its emitted observation equals `o`.
Every included successor therefore has a witnessing compatible predecessor;
every compatible actual successor is included. Induction from the initial
belief proves equality at all histories. Complete configuration semantics
then make the same belief sufficient for future legality and success. QED.

Unlike TDA filtering, this update can change the states without reducing
their number. Initial-world labels alone need not determine the next problem.

## 2. Exact synthesis and finite termination

Let `Bset` contain all nonempty subsets of `S`. Define

`Win_0 = {B in Bset: C(B) nonempty}`,
`Win_(k+1) = Win_k union {B: some u in Legal(B) has every nonempty B[u,o] in Win_k}`.

**CRA-2 — controlled relational reachability.** `B in Win_k` iff an admitted
observation-conditioned policy guarantees a successful terminal decision in
at most `k` control actions. The least index `r(B)` containing `B` equals the
minimum worst-case control-action count; beliefs never admitted have value
infinity and no adequate terminating policy.

Proof. At zero steps, one terminal action must work throughout `B`, exactly
`C(B) nonempty`. At the next step a successful policy either stops or chooses
one action legal for every possible state. Each possible observation must
then admit a remaining policy within `k` steps, giving the predecessor rule.
Conversely choose the witnessing action and its successful child policies.
Induction proves both necessity and a constructed policy at every index.

There are `N=2^|S|-1` beliefs. If `Win_0` is empty no later set can grow,
because a legal action has a nonempty observation successor. Otherwise every
nontrivial iteration adds a belief, so ranks are at most `N-1`. A stationary
belief controller chooses a witnessing action whose successors have smaller
rank, and stops with an action in `C(B)` at rank zero. Every run terminates.
Any deterministic policy terminating for each of finitely many initial states
has a finite maximum trajectory length; the preceding induction therefore
covers every adequate terminating policy, not only a preselected horizon.
QED.

The least fixed point is essential. A losing one-state self-loop with empty
`Gamma` satisfies the predecessor equation if declared winning in advance.
It never enters the least fixed point and supplies no terminating policy.
No fairness assumption or probability-one interpretation licenses that loop.
This result concerns deterministic dynamics and success on every initial
state; stochastic or adversarial-transition extensions need their own proof.

## 3. Finite-horizon nonnegative cost law

Register finite nonnegative exact control costs `c(u)`, a finite integer
horizon `h>=0`, and a finite nonnegative allowance `q`. Set `V_0(B)=0` when
`C(B)` is nonempty and infinity otherwise. For successive horizons set

`V_(k+1)(B)=0` if `C(B)` is nonempty; otherwise
`V_(k+1)(B)=min_{u in Legal(B)} [c(u)+max_o V_k(B[u,o])]`.

Here `min(empty)=infinity`; infinity denotes impossibility, never an admitted
resource allowance. For executable exact comparisons use a decidable cost
representation, such as the rational/integer registers in the finite checks.

**CRA-3.** A successful policy within `h` controls and cost at most `q` exists
iff `V_h(B)<=q`. Every finite value is attained by an admitted finite policy.

The proof is the same first-action induction with a maximum over possible
observations and a minimum over finite legal choices. Stopping costs zero in
this *control-cost coordinate*, and nonnegative costs make it optimal whenever
possible. Zero-cost cycles cause no ambiguity because the horizon decreases.
This is not a claim that an arbitrary fixed point of an unbounded-cost Bellman
equation represents termination or an optimum.

TDA-1 is recovered when controls leave the world unchanged, legality is fixed
and observations merely filter candidates. Its strict-subset descent is then
valid; deleting an uninformative action in the controlled model is not valid.

## 4. Destructive information and its constructive revival

Let the hidden bit be `b`. Use six configurations `F_b` (fresh), `P_b`
(protected), `D_b` (destroyed), and initial belief `{F_0,F_1}`. Set
`Gamma(F_b)=Gamma(P_b)={a_b}`, `Gamma(D_b)=empty`. Every control costs one.

| Control | Fresh configuration | Protected configuration | Destroyed configuration | Observation |
|---|---|---|---|---|
| protect | `F_b -> P_b` | stays | stays | blank |
| probe | `F_b -> D_b` | stays | stays | `b` |

Probing first reveals `b` but leaves a destroyed configuration with no
successful terminal action or recovery. Without protection the initial
belief is losing. A frozen table retaining the initial `Gamma(F_b)` would
incorrectly predict one test suffices; that applies TDA outside its premises.

With protection available, `protect -> probe -> a_b` succeeds in two controls.
Protection yields no information and preserves uncertainty cardinality, but
changes the legal future of the process. A one-control solution is impossible:
protection leaves incompatible terminal actions, while probing destroys the
system. Hence `r({F_0,F_1})=2`, `r({P_0,P_1})=1`, and `r({D_b})=infinity`.
This attributes failure to irreversible transition effects, then repairs that
stage through an admitted protective action. The revived positive is scoped
to the stated process, not a universal recovery or physical-safety claim.

An opposite-direction control separates action from identification: if a reset
maps two initially incompatible configurations to one configuration with a
shared terminal action, it succeeds without any informative observation.
Initial-world filtering alone would miss that success as well.

## 5. Independent finite evidence

`grand_gmi_controlled_relational_acquisition_checks_v1.py` enumerates every two-state,
two-control partial deterministic transition table (including illegal actions),
every binary observation table, every two-action terminal relation (including
empty rows), and all three nonempty initial beliefs. Its oracle generates
complete depth-two policy trees with terminal actions at leaves, then executes
actual configurations and rejects illegal actions or unsuccessful terminals.
It does not use belief predecessors to determine policy success.

Depth two is complete for this declared universe: it has three beliefs, and
CRA-2 bounds every winning rank by two. The checker also directly executes
the six-state destructive/protected policies, illegal-action, losing-loop and
finite-cost controls. The receipt is
`GRAND_GMI_CONTROLLED_RELATIONAL_ACQUISITION_RECEIPT_V1.json`. Exact census agreement
checks the finite implementation; the induction above supplies the theorem.

## 6. Primary parents and the remaining boundary

[Rintanen, *Conditional Planning in the Discrete Belief Space*, IJCAI 2005, sections 2 and 5](https://www.ijcai.org/Proceedings/05/Papers/1084.pdf)
defines possible-current-state beliefs, action images, observations and finite
conditional plans; Theorems 11--12 give completeness and soundness. Its final
section-5 paragraph also permits observations depending on the last action.
[Cimatti, Roveri and Traverso, *Strong Planning in Non-Deterministic Domains via Model Checking*, AIPS 1998, pp. 40--41](https://cdn.aaai.org/AIPS/1998/AIPS98-005.pdf)
provides universally applicable actions and constructive backward strong
predecessors. These are direct planning parents, not GMI inventions.

The adaptation replaces a fixed goal set by a common legal terminal action
and explicitly binds the controlled update to GMI's relational obligation.
This is a synthesis and scope bridge, with no novelty claim for belief-state
planning, dynamic programming or least-fixed-point reachability. Unknown
dynamics, stochastic error guarantees, fair cyclic execution, unbounded
configuration registers and restricted controller memory remain outside this
finite theorem. The complete physical resource profile is still required.
