# Grand GMI Active Closed-Loop Intelligence Theorem V1

Status: **THEOREM / ACTIVE-SENSING AND CLOSED-LOOP MORPHOLOGY LAYER + EXACT FINITE WITNESS**  
Date: 2026-09-12

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

Then no passive/open-loop terminal policy can satisfy the obligation, while an active sensing policy can. Hence **active information gathering is morphology-derived** at that scope.

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

A `SENSE -> STORE -> ACT` architecture property is derived if every selected adequate morphology must:

1. take an admitted information-gathering action;
2. retain a protected distinction across a later cut;
3. condition a terminal action on that retained distinction.

This is a stronger statement than merely observing that a system happens to possess a sensor or memory. It says the closed-loop obligation logically requires those roles at the registered scope.

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

Therefore, under a zero-error obligation and a sensing budget that admits the probe,

\[
\boxed{\text{active sensing + one persistent bit is required}.}
\]

If the sensing budget is zero, the zero-error obligation is infeasible rather than magically solved by a more fashionable architecture.

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
