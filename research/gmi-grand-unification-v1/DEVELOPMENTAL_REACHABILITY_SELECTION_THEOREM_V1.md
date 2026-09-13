# Grand GMI Developmental Reachability Selection Theorem V1

Status: **THEOREM / TRAINING-AND-DEVELOPMENT PATH SELECTION LAYER + EXACT FINITE WITNESS**  
Date: 2026-09-12; lifecycle-accounting correction: 2026-09-13

Current executable authority: `GRAND_GMI_DEVELOPMENTAL_LIFECYCLE_RECEIPT_V2.json`.
The V1 receipt is historical: its budget-3 and budget-10 winners optimized
deployment alone, despite the life-cycle objective in DRS-1/3.

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

This is existential path reachability. It is not a guarantee that one controller
can find the path under an unknown ecology: such a claim must quantify over one
admissible observation-adapted developmental policy and its possible ecologies.
The graph node must include any history that changes available transitions or
future costs; otherwise a memoryless graph is not an adequate development model.

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

Increasing development budget can add new morphology families to the selected
set. If the budget is a componentwise cap on the same nonnegative path costs
retained in the life-cycle profile, and the graph/profiles stay fixed, the old
frontier persists: a newly feasible path cannot dominate an old frontier point.
Indeed, any dominator has development costs no greater than that old point,
so it already met the old budget, contradicting the old point's nondominance.
This proves inclusion of the old life-cycle frontier in the new one.

A budget-constrained deployment-only objective can reverse its family verdict,
because it projects away the very cost that excluded the new competitor.
Reversal of a full-profile verdict requires a different setup, such as changed
profiles/update dynamics or a budget coordinate not retained in the objective.
The declaration must identify that setup. Thus the development budget, update
dynamics and retained resource coordinates are all essential to a family claim.

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

A learning-rule property is selection-derived only when the selected protected
developmental-path set is nonempty and the property holds throughout that set
(MSC-1). Observing a path can identify which mechanism actually ran when the
registered history map distinguishes mechanisms. That does not by itself show
that the same mechanism was necessary across all selected alternatives.

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
3. the selected adequate realization/path set is nonempty, and every member uses a topology-changing developmental path;

then **architecture growth/self-modification is developmentally derived** at that scope.

The conclusion can apply to neural architecture growth, program synthesis, circuit rewiring, cellular differentiation or another substrate realization.

## 9. DRS-7 — finite exact developmental solver

For a finite memoryless morphology graph with nonnegative integral scalar
developmental costs and a finite budget, the reachable set and minimum cost to
every node are decidable by finite graph search. Simple paths suffice: deleting
a cycle preserves the endpoint and cannot increase cost. Zero-cost cycles do
not justify enumerating infinitely many histories. For vector costs there need
not be a single componentwise minimum; retain nondominated cost labels at each
node. Combining path-resource labels with deployment profiles yields an exact
life-cycle endpoint/family verdict. This statement does not identify or enumerate
all path histories when history is itself a protected observable.

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

`P_good` becomes reachable. The full profiles are `N_good=(2,2,2)` and
`P_good=(1,1,3)`, where the last coordinate is development cost. Neither
dominates the other, so the life-cycle verdict is neural/program coexistence.
Only the separately declared deployment-only projection selects `P_good`.

### Budget 10

`X_ideal=(0,0,10)` joins the two life-cycle tradeoffs. All three remain
nondominated. The deployment-only projection selects `X_ideal`.

### Static set

If developmental reachability and developmental cost are both ignored,
`X_ideal` dominates in deployment coordinates but is unavailable below cost 10.
Projecting out a charged resource can remove a real Pareto tradeoff.

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
