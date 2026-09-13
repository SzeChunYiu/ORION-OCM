# Grand GMI Developmental Reachability Selection Theorem V1

Status: **THEOREM / TRAINING-AND-DEVELOPMENT PATH SELECTION LAYER + EXACT FINITE WITNESS**  
Date: 2026-09-12

## 1. Gap closed

Grand GMI already treats learning and morphogenesis as a lifted GMI problem and distinguishes static physical optimality from developmental reachability. The remaining derivation gap is operational:

> How does a neural, non-neural or hybrid morphology become selected because a particular training/search/evolutionary path can actually construct it within budget, rather than because the endpoint was simply placed in a candidate list?

This layer makes the **path to the morphology** an explicit selected object.

## 2. Developmental transition system

Let the registered morphology state space be `M`. A developmental transition is

\[
m \xrightarrow{u,e} m',
\]

where `u` is an admitted update operation and `e` is the developmental ecology/input available at that step.

Each transition has a registered developmental resource vector

\[
c_{dev}(m,u,e,m')
\]

covering coordinates such as update compute, samples, wall time, energy, communication, interventions, search evaluations or material change.

For initial morphology set `I` and developmental budget `B`, define

\[
Reach_B(I)=\{m:\text{there exists a legal developmental path from }I\text{ to }m\text{ whose composed cost satisfies }B\}.
\]

The admissible deployment set is then intersected with `Reach_B(I)` before morphology/family selection.

## 3. DRS-1 — reachable-endpoint derivation theorem

Let `A_static` be the adequate physically realizable morphology set and

\[
A_B=A_{static}\cap Reach_B(I).
\]

The correct developmental frontier is the Pareto frontier of the registered deployment/development profile over `A_B`, not over `A_static`.

Therefore an endpoint morphology can be physically superior yet irrelevant to the realized intelligence if it has no admitted path within the developmental budget.

This turns training, architecture search, evolution, synthesis and self-modification into causal components of the morphology derivation.

## 4. DRS-2 — developmental-budget phase change theorem

For budgets `B_1 <= B_2` under a monotone budget order,

\[
Reach_{B_1}(I)\subseteq Reach_{B_2}(I).
\]

Hence increasing development budget can add new morphology families to the selected set and can reverse a previous family verdict.

A statement such as "the task derives a neural network" is therefore incomplete unless the developmental budget and update dynamics are part of the registered scope. Under a larger budget, a non-neural or hybrid competitor may become reachable and dominate; under a tighter budget the reverse can happen.

## 5. DRS-3 — development cost must be charged

If two endpoint morphologies have identical deployment capability/resource profiles but require different registered developmental cost vectors, they are not resource-equivalent in a theory that counts development.

The full profile may be written

\[
\pi_{life}(m,p)=\big(\pi_{deploy}(m), c_{dev}(p)\big)
\]

for a legal path `p` ending at `m`.

When multiple paths reach the same endpoint, path resources may create distinct life-cycle Pareto points even though deployment behavior is identical.

## 6. DRS-4 — endpoint does not identify learning mechanism

Suppose two admitted developmental mechanisms `U_1` and `U_2` reach response-equivalent endpoints with the same protected life-cycle profile. Then observation of the final intelligence does not identify which developmental mechanism occurred.

A learning-rule property is derived only if it holds for every selected protected developmental path, or if path history itself is a protected observable.

Consequences:

- a trained neural endpoint does not prove gradient descent was necessary;
- a program endpoint does not prove symbolic search was necessary;
- an evolved morphology does not imply evolutionary history is recoverable from endpoint behavior alone.

This is developmental non-identifiability, parallel to realization non-identifiability.

## 7. DRS-5 — initial-condition/path-dependence theorem

In general

\[
Reach_B(I_1)\ne Reach_B(I_2).
\]

Therefore two systems with the same obligation, substrate and development budget can derive different realized intelligence forms solely because their initial morphologies differ.

This captures initialization dependence, inherited structure, pretraining, priors encoded in the starting machine, biological ancestry and bootstrapping constraints without treating them as mysterious exceptions to GMI.

## 8. DRS-6 — architecture growth criterion

Let `M_fixed` be morphologies with fixed topology/state structure and `M_grow` include admitted topology-changing updates. If

1. no `m in M_fixed cap Reach_B(I)` satisfies the obligation;
2. at least one `m in M_grow cap Reach_B(I)` does;
3. every selected adequate endpoint uses a topology-changing developmental path;

then **architecture growth/self-modification is developmentally derived** at that scope.

The conclusion can apply to neural architecture growth, program synthesis, circuit rewiring, cellular differentiation or another substrate realization.

## 9. DRS-7 — finite exact developmental solver

For a finite morphology graph with nonnegative integral developmental costs and a finite budget, the reachable set and minimum developmental cost to every node are decidable by finite graph search. Combining that result with the existing finite exact GMI selection pipeline yields an exact endpoint/family verdict.

This is a finite-sector theorem only. It does not imply a total optimizer for unrestricted continuous or Turing-complete development spaces.

## 10. Exact witness

The checker uses a finite morphology graph with two starting conditions.

From `S_neutral`:

- `S_neutral -> N_seed` costs 1;
- `N_seed -> N_good` costs 1;
- `S_neutral -> P_good` costs 3;
- `S_neutral -> X_ideal` costs 10.

Deployment profiles to minimize are:

- `N_good` (neural): `(2,2)`;
- `P_good` (program): `(1,1)`;
- `X_ideal` (exotic): `(0,0)`.

All three are adequate once reached.

### Budget 2

Only `N_good` is reachable among adequate endpoints. Neurality is therefore developmentally selected even though the static deployment optimum is not neural.

### Budget 3

`P_good` becomes reachable and strictly dominates `N_good`. The selected family flips to non-neural.

### Static set

If developmental reachability is ignored, `X_ideal` dominates both but is unavailable below cost 10. This is the exact failure mode of static-only reasoning.

### Different initial condition

From `S_program`, `P_good` is reachable at cost 1. Under the same budget 2 that selects neurality from `S_neutral`, the program start selects non-neurality.

### Path non-identifiability

`N_good` is also reachable through an alternate two-step path labeled with a different developmental mechanism but identical total protected cost. Endpoint behavior alone cannot identify which path produced it.

## 11. Expanded derivation chain

The realized-form derivation is therefore

\[
\text{initial morphology}
+\text{development ecology}
+\text{update law}
+\text{development budget}
\to Reach_B
\to \text{adequate reachable endpoints}
\to \text{life-cycle resource frontier}
\to \text{family and architecture-property verdict}.
\]

Neural and non-neural intelligence are not just endpoint implementation options; they can be consequences of which construction paths physics and development make available.

## 12. Boundary

This theorem does not claim that SGD, evolution, NAS, program synthesis or any other real optimizer reaches its global optimum. Reachability must be proved, enumerated, bounded or empirically certified for the registered update process.

Nor does it make the final morphology unique when multiple reachable endpoints remain nondominated. In that case Grand GMI must retain coexistence rather than invent a unique developmental story.
