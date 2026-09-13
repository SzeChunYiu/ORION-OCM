# Grand GMI Active Closed-Loop Intelligence Theorem V1

Status: **ACTIVE-INFORMATION NECESSITY + CONDITIONAL WHOLE-POLICY SUFFICIENCY + EXACT WITNESSES**
Date: 2026-09-13

The finite deterministic synthesis extension is [CRA-1--3](CONTROLLED_RELATIONAL_ACQUISITION_THEOREM_V1.md): current-configuration belief updates, exact terminating-policy construction and finite-horizon cost. ACL-2b retains its conditional whole-policy scope.

## 1. Gap closed

A passive input-output map is not the general form of intelligence. In an embodied process, actions can alter physical state, future observations, communication opportunities, risk and the information available to later decisions.

The missing morphology question is:

> When does Grand GMI derive a sensor-controller loop, active information gathering and persistent internal state instead of a one-shot passive predictor?

This layer makes action-conditioned ecology and information acquisition explicit while remaining implementation-family neutral.

## 2. Controlled ecology

Let latent physical state be `h_t`, action `a_t`, observation `o_t`, and protected internal machine state `s_t`. A controlled process has kernels or deterministic maps of the form

\[
h_{t+1}\sim T(\cdot\mid h_t,a_t),
\qquad
o_{t+1}\sim O(\cdot\mid h_{t+1},a_t),
\]

with policy

\[
a_t\sim \pi(\cdot\mid s_t,o_t),
\qquad
s_{t+1}\sim U(\cdot\mid s_t,o_t,a_t).
\]

The ecology is therefore not merely a stream delivered independently of the machine. The machine and environment jointly generate the future protected trace.

## 3. ACL-1 — closed-loop adequacy theorem

When admitted actions change either future state transitions or future observation laws, adequacy must be evaluated on the induced closed-loop trace distribution/process.

A passive predictor that is evaluated only under a fixed exogenous observation stream is not response-equivalent in general, because replacing its actions can change the future evidence on which later obligations depend.

One may always encode an entire finite history into an enlarged state for analysis, but this does not erase the physical information, memory, sensing and action costs; those remain registered cuts/resources.

## 4. ACL-2 — active-sensing necessity criterion

Suppose before a terminal decision there are at least two latent hypotheses `h_0,h_1` that:

1. require different terminal protected actions;
2. cannot be distinguished from the passive observation available without an information-gathering action;
3. can be distinguished by an admitted sensing/probing action within budget;
4. the protected obligation requires correctness on both hypotheses.

Then no terminal policy restricted to that passive information can satisfy the obligation. The existence of an affordable distinguishing probe does **not** by itself establish an adequate active policy. The acquired distinction must still reach a legal terminal action through an admitted controller, and the complete sensing, retention and action process must meet the total resource and viability constraints.

**ACL-2a — acquisition necessity.** Conditions 1, 2 and 4 exclude the passive information boundary. Condition 3 identifies an available source of the missing information but supplies only acquisition feasibility.

**ACL-2b — complete-policy sufficiency.** An active policy is adequate if an admitted probe and controller jointly map every compatible sensing outcome to the required legal terminal action, preserve any needed distinction until use, and satisfy the complete budget and other protected constraints. For a finite immediate-response instance with an exact distinguishing probe, the observation still available at the terminal decision, and an admitted within-budget lookup from outcomes to required actions, this policy is constructed directly by that lookup. Delayed action additionally requires a feasible retention/decoder process, as in ACL-3.

### Counterexample to probe-only sufficiency

Let the hidden bit be `h in {0,1}` and require terminal action `a=h`. A probe of cost one reveals `h`, but its observation is removed before a forced blank step. Admit the probe within the sensing budget while allowing only one persistent controller state, with no other side channel. All four conditions above hold, yet every legal terminal controller receives the same state and blank observation in both worlds. Neither deterministic output is correct on both; randomizing cannot make both success probabilities one. An admitted two-state controller can store the bit and succeed. Probe affordability therefore does not imply complete-policy feasibility.

Active information gathering is morphology-derived for an adequate selected policy only after both the information necessity and complete-policy feasibility conditions have been established.

The sensing action may be a camera movement, query, experiment, memory lookup, diagnostic test, communication request, database read, physical probe or another intervention. Grand GMI derives the information-acquisition role, not a particular sensor technology.

## 5. ACL-3 — memory after sensing theorem

Assume a sensing step distinguishes `m` latent possibilities that later require pairwise incompatible terminal actions, and all distinguishing observations disappear before the terminal decision so that the downstream external observation is identical.

Then the temporal cut between sensing and acting requires at least `m` distinguishable exact persistent internal messages/states. For a binary logical carrier this requires at least

\[
\lceil\log_2 m\rceil
\]

logical bits.

### Proof

The `m` post-sensing histories are jointly compatible with the same later external observation but require distinct actions. They therefore form a semantic conflict set across the temporal cut. Any exact realization must encode them into distinct persistent states. The physical distinguishability bridge transports that requirement into carrier capacity. QED.

This derives recurrent/internal state from the closed-loop obligation independently of whether the implementation is an RNN, finite-state controller, program memory, latch, biological memory or another substrate.

## 6. ACL-4 — sensing/action tradeoff frontier

Information gathering is not free. Let sensing action `q` have registered resources `rho(q)` and change the achievable terminal loss from `L_passive` to `L_active`.

The resulting morphology comparison is a Pareto tradeoff between information quality/capability and sensing resources. If a hard capability threshold cannot be met without sensing, the active loop is feasible-necessary. If both passive and active forms meet the obligation, resource selection may retain either or both.

Thus Grand GMI does not universally prefer curiosity or active sensing; it derives it only when the obligation/resource frontier requires it.

## 7. ACL-5 — information and control can be coupled

A decomposition into an independent estimator followed by an independent controller is valid only when a parent separation/sufficiency theorem supplies the needed hypotheses.

In a general controlled ecology, an action can simultaneously alter reward/viability and future information. Therefore local optimization of "perception" separately from "control" can fail.

Grand GMI handles the general case as a coupled process network. Any estimator-controller factorization is itself a morphology claim that must survive the compositional/factorization criteria already registered.

## 8. ACL-6 — family-neutral realization theorem

The same protected active loop can have multiple realization families:

- neural policy plus learned recurrent state;
- exact finite-state controller;
- symbolic planner with memory;
- Bayesian/filtering controller under suitable parent assumptions;
- hybrid neural perception plus exact safety/control logic;
- distributed or biological feedback process.

Closed-loop structure therefore does not imply neurality. Family selection remains a question of realization feasibility, physical resources, development, generalization and the selected frontier.

## 9. ACL-7 — embodied architecture property derivation

A `SENSE -> STORE -> ACT` architecture property is derived if the selected
adequate morphology set is nonempty and every member must:

1. take an admitted information-gathering action;
2. retain a protected distinction across a later cut;
3. condition a terminal action on that retained distinction.

This says the closed-loop obligation requires those roles throughout an
actually nonempty selected set. Empty selection establishes no architecture
property; the existence premise follows [MSC-1](CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md).

## 10. Exact hidden-bit witness

Latent state `h` is uniformly one of `{0,1}`. The terminal obligation is to output action `a=h` with zero error.

### Passive/open-loop case

Without sensing, the terminal observation is the same null symbol for both hidden states. A deterministic policy can only always guess `0` or always guess `1`, so its success is exactly `1/2`.

### Active case

An admitted sensing action returns observation `o=h`. The observation is then removed and a blank step occurs before the terminal decision.

A controller with two persistent states stores the sensed bit and later outputs it, achieving success `1`.

A one-state controller cannot retain which observation occurred and therefore cannot achieve zero error.

The exact checker enumerates:

- both passive deterministic guesses;
- both one-state terminal output policies after the sensed observation has disappeared;
- all 16 binary encoder/decoder memory pairs, of which exactly two achieve perfect delayed reproduction.

Therefore, under a zero-error obligation, a sensing budget that admits the probe, and a registered feasible two-state retention/terminal-action implementation,

\[
\boxed{\text{active sensing + one persistent bit is required}.}
\]

If the sensing budget is zero, the zero-error obligation is infeasible rather than magically solved by a more fashionable architecture.

Likewise, if the probe is affordable but the complete budget admits only one persistent state, the delayed zero-error obligation is infeasible. The original witness fixes the two-state controller as available; it is not a theorem that the sensing budget alone determines feasibility. The additive sufficiency-direction checker freezes both budgets separately.

## 11. Relation to neural and non-neural intelligence

The witness can be realized by:

- a tiny recurrent neural machine that stores the sensed bit;
- a two-state non-neural FSM;
- a program variable followed by a branch;
- a physical bistable element and controller.

The operational architecture property is the same. Neurality or non-neurality is decided only after applying the realization/resource/reachability layers.

Thus Grand GMI can derive **why an intelligent morphology needs feedback and memory** without defining intelligence as a neural network.

## 12. Expanded Grand-GMI chain

For embodied tasks the chain becomes

\[
\text{controlled ecology + obligation}
\to \text{action-conditioned semantic distinctions}
\to \text{active information requirements}
\to \text{temporal cut memory bounds}
\to \text{closed-loop architecture properties}
\to \text{candidate neural/non-neural realizations}
\to \text{resource/reachability/generalization frontier}.
\]

## 13. Boundary

This theorem does not claim that every intelligent system must actively sense, nor that every control problem violates estimator-controller separation. It supplies an exact criterion for when passive morphology is inadequate and an explicit memory lower bound when acquired information must survive to a later decision.

Continuous-state POMDPs, nonlinear control, dual control and real robotics require their own parent control/inference results and empirical substrate models; Grand GMI imports those results when their hypotheses are established.
