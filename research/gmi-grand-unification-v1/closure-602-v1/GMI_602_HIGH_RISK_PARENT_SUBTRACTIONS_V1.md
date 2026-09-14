# GMI #602 high-risk parent subtractions V1

Status: **NORMATIVE FORMAL SUPPLEMENT**  
Date: 2026-09-14.  
Trigger: the merged audit of the contributed #602 closure-pass R4 bundle preserved two high-risk parent-reduction lanes: universal/bias-optimal search versus morphogenesis, and active-inference/control-as-inference versus the Section-C update/control residual.

This document closes those *formal parent-subtraction* gaps. It does not close neutral-recovery, held-out morphology-selection, learning-law prediction, or real-scale evidence.

---

# T602-37 — universal / bias-optimal program-search parent subtraction [P1 + parent reduction]

## 37.1 Search object

Let a registered search problem be `(r,C,P,V)` where:

- `r` is the protected problem/obligation;
- `C` is the legal candidate-program space;
- `P(q|r)` is the prospectively frozen search bias/prior over candidates;
- `V(q,r)` is the verifier plus complete create/run/test burden `t(q,r)`.

A searcher's job is to allocate computation across `C` until a verified solution is found.

Schmidhuber's OOPS parent explicitly defines `n`-bias-optimal search relative to `P`: a candidate `p` with test time `t(p,r)` must be found within total budget on the order of `n t(p,r)/P(p|r)`. Levin-style universal search is the nonincremental parent; OOPS adds incremental exploitation of earlier solution programs; PowerPlay searches pairs of new tasks and solver modifications while preserving previously solved tasks and may optimize earlier skills.

These parents therefore already own:

```text
program-space search;
probability/description-length search bias;
near/bias-optimal scheduling relative to that bias;
incremental reuse of prior solution programs;
meta-search over search/solver code;
continual task + solver modification search.
```

A GMI claim that merely says "a generic search recovered a morphology/program/library/update rule" is parent-sufficient unless a further residual survives.

## 37.2 Bias-optimal burden bound

Using the OOPS definition, an `n`-bias-optimal searcher is guaranteed to solve `r` by total search time

\[
T \ge n\,t(p,r)/P(p|r)
\]

whenever verified solution `p` is in support. For a prefix-length prior with `P(p) proportional to 2^{-|p|}`, the familiar Levin-style burden is exponential in description length up to scheduler/normalization constants:

\[
T = O(2^{|p|}t(p,r)).
\]

Thus a shorter encoding or larger prior mass is itself a search-resource advantage. Search burden is not representation-neutral.

## 37.3 Finite exhaustive-selection theorem

Let `C_fin` be a finite admitted phenotype/candidate set, let every candidate be eventually evaluated exactly, and let frozen full lifecycle score `J(c)` have a unique minimizer `c*`. Then **final exhaustive selection** of `argmin J` is independent of enumeration order/search prior.

**Proof.** Exhaustive exact evaluation produces the same finite set of `(c,J(c))` pairs under any ordering; a unique minimum is therefore the same. ∎

However, **time-to-discovery, first accepted solution and any budget-truncated outcome remain search-bias dependent**. This is the correct separation between ecology/resource *selection* and morphogenetic *reachability*.

## 37.4 Encoding non-invariance at finite search horizons

Kolmogorov complexity is invariant across universal description machines only up to a machine-dependent additive constant. That constant can materially change finite description lengths and therefore prior masses/search order. More generally, for finite candidate sets one can prospectively re-encode candidates with different prefix code lengths while preserving their semantics.

Consequently:

> recovery rank, first-hit time, and finite-budget "emergence" are not architecture-independent facts unless the encoding/search bias is itself part of the registered ecology or robustness is shown across admissible re-encodings/searchers.

A universal-search parent cannot by itself identify which morphology should be cheapest after discovery; conversely, a morphology cost theorem cannot by itself establish reachable discovery time.

## 37.5 Exact GMI morphogenesis residual after parent subtraction

A registered morphogenesis claim survives Levin/OOPS/PowerPlay parents only if all relevant items are present:

1. **pre-search phenotype prediction** — obligation/ecology/resource descriptors predict a morphology-equivalence class or frontier property before search outcome;
2. **parent-owned search admitted** — Levin/OOPS/PowerPlay-like search is allowed as a searcher/baseline rather than treated as a GMI invention;
3. **full search burden charged** — failed proposals, execution, verification, retained-code maintenance and reuse are counted;
4. **support audit** — target has nonzero support/reachability under every searcher used to claim recovery;
5. **bias/encoding audit** — candidate prior/code length/search grammar is frozen and reported;
6. **cross-search or cross-encoding replication** — if the claim is ecology-determined rather than searcher-specific, corresponding phenotype selection survives a prospectively registered alternative bias/encoding, or the theory quantitatively predicts the difference;
7. **negative twin** — an ecology/resource change predicted to select a different phenotype actually does so;
8. **selection/reachability separation** — exhaustive-optimal phenotype and finite-budget first-hit morphology are never conflated.

If the only positive statement is that a general program search can eventually find/reuse/improve a solver, terminate `PARENT_SUFFICIENT_LEVIN_OOPS_POWERPLAY`.

## 37.6 What remains empirical

This theorem closes the R4 audit's *parent-reduction logic* but not the #602 Section-E evidence. Neutral cross-search/cross-grammar recovery, held-out morphology prediction and measured search-burden phase changes remain P2/P4.

---

# T602-38 — active-inference / control-as-inference parent subtraction [P1 + parent reduction]

## 38.1 Strongest parents receive first refusal

For a registered partially observed controlled process, standard POMDP theory already supplies the belief state

\[
b_t(s)=P(s_t=s\mid h_t)
\]

as a sufficient statistic for action-observation history under the declared model. Planning may therefore be performed in belief space rather than from raw history.

Control-as-inference parents introduce latent optimality/preference variables and convert reward/cost into trajectory likelihood factors. In the standard maximum-entropy construction, an optimality factor has form

\[
P(O_t=1\mid s_t,a_t) \propto \exp(r(s_t,a_t)/\alpha),
\]

and conditioning/variational inference over trajectories yields entropy/KL-regularized control under the corresponding assumptions.

Active-inference parents go further: action and perception are coupled through a generative model and expected free energy, whose standard decompositions contain pragmatic/extrinsic and epistemic/information-gain terms.

Therefore these parents already own, at their stated scopes:

```text
belief-state control under partial observability;
Bayesian/generative-model state inference;
control formulated as probabilistic/variational inference;
preference/optimality factors;
pragmatic/extrinsic action value;
epistemic/information-seeking action value;
habit / policy selection mechanisms described by active inference.
```

A GMI law that merely rediscovers those objects is parent-sufficient.

## 38.2 History-compression necessity

Let protected future decision target be `A*(h)`. Any state summary `q(h)`—belief state, predictive state, recurrent vector, symbolic state or otherwise—is decision-sufficient iff

\[
q(h_1)=q(h_2) \Rightarrow A^*(h_1)=A^*(h_2)
\]

at the registered exact scope, or satisfies the declared approximate decision-loss criterion.

POMDP belief state is one parent-sufficient construction when model assumptions hold. GMI does not own the existence of belief-state sufficiency.

## 38.3 Information-seeking value is parent-owned decision value

Let optional experiment/action `e` cost `c_e` and deliver observation `Z_e` before a later decision. Let `R_0` be optimal Bayes risk without it and `R_e` optimal risk after conditioning on `Z_e`, both under the frozen model/loss. Then acquisition is worthwhile only when

\[
R_0-E[R_e] > c_e
\]

(or the corresponding vector/Pareto condition without scalar prices).

This is ordinary value-of-information / experimental-design logic. Calling the left side "epistemic value" does not create a new GMI mechanism.

## 38.4 Generative-inference controller lifecycle comparison

Let `G` be a generative/belief/inference controller and `D` a direct/reactive/model-free/control baseline that satisfies the same protected obligation. Over a frozen horizon define complete lifecycle burdens

\[
C_G=K_{model}+K_{infer}+K_{plan}+K_{learn}+K_{verify}+L_G,
\]

\[
C_D=K_{direct}+K_{learn,D}+K_{verify,D}+L_D,
\]

where the `K` terms include state, computation, acquisition, update/revision and communication coordinates before any registered scalarization, and `L` is protected task loss/failure burden.

The inference controller enters the scalarized resource frontier only when `C_G<C_D`; in vector accounting it must be feasible and Pareto-undominated. Partial observability or epistemic value alone does not guarantee that result—the benefit must repay model learning, belief updating and planning.

## 38.5 Control-as-inference reduction test

A Section-C candidate update/control law is `PARENT_SUFFICIENT_CONTROL_AS_INFERENCE` when, at matched scope, its behavior can be represented by:

1. a declared dynamics/generative model;
2. declared preference/reward/optimality factors;
3. a declared inference/variational family and update;
4. a policy induced by inference under those objects;
5. no additional protected capability/resource residual after matching lifecycle charges.

It is `PARENT_SUFFICIENT_ACTIVE_INFERENCE` when the remaining distinctive claim is expected-free-energy policy evaluation with the standard pragmatic/epistemic generative-model machinery and no extra residual.

## 38.6 Exact GMI residual after subtraction

The only admissible generic residual in #602 C is therefore **conditional morphology/update-law selection**, not the inference mechanism:

\[
(E,R,V,H,O) \longrightarrow
\text{which sufficient state + parent update/control family is feasible/Pareto-optimal?}
\]

To earn a positive residual, #602 must prospectively predict at least one crossover in which, for example:

- reactive/direct control wins when observations are decision-sufficient and inference overhead cannot pay;
- belief/generative inference wins when hidden-state distinctions materially change future actions and the value exceeds model/inference cost;
- an information-seeking policy wins only where the expected value of acquired information exceeds its acquisition/latency/verification cost;
- a changed ecology/resource/verifier regime reverses the ordering as predicted.

Neutral search may rediscover active-inference-like machinery, but that rediscovery is evidence for reachability only after active-inference/control-as-inference parents are accepted as the mechanism owners.

## 38.7 What remains empirical

This closes the R4 audit's formal parent-subtraction lane for the common Section-C residual. Still open are #602's held-out, architecture-name-free learning/control-family selection prediction and neutral recovery under matched parents.

---

# 3. Claim boundary after both high-risk reductions

At registered formal scope, the two R4 high-risk parent lanes now terminate as follows:

```text
UNIVERSAL_SEARCH_MECHANISM             -> PARENT_SUFFICIENT_LEVIN_OOPS_POWERPLAY
ACTIVE_INFERENCE_CONTROL_MECHANISM     -> PARENT_SUFFICIENT_ACTIVE_INFERENCE_OR_CONTROL_AS_INFERENCE
GMI_RESIDUAL                           -> conditional ecology/resource morphology/update-law selection
MORPHOGENESIS_RESIDUAL                 -> predicted phenotype + charged reachable recovery robust/quantified across search bias
COMPLETE_EMPIRICAL_CLOSURE             -> NOT EARNED
```

No mechanism is renamed as GMI novelty.
