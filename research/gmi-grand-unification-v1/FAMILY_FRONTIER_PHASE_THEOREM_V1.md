# Grand GMI Family-Frontier Phase Theorem V1

Status: **THEOREM / ROBUST FAMILY-SELECTION LAW + HYBRID DECOMPOSITION LAW + EXACT SYNTHETIC WITNESSES**  
Date: 2026-09-12

## 1. Gap closed

The NN/non-NN derivation certificate says what evidence is sufficient for a family verdict. A remaining formal bridge is to turn certified family-conditioned resource bounds into a phase law:

> For which registered task/substrate regimes is a neural, non-neural, hybrid, coexistence or undecided verdict forced?

This theorem supplies that bridge without inventing physical measurements. Real measurements instantiate the bounds; the phase law itself is symbolic.

## 2. Family-conditioned attainable sets

Fix a registered GMI problem `Sigma`, deployment tolerance `epsilon`, development budget and candidate universe. Partition adequate reachable realizations by operational family

`F in {NEURAL, NON_NEURAL, HYBRID, ...}`.

For task/substrate parameter `s`, let

\[
Y_F(s) \subseteq \mathbb R^d
\]

be the attainable resource/capability profiles of family `F` after all hard certificate gates are applied. Smaller registered coordinates are better.

The global reachable frontier is

\[
\operatorname{Pareto}\Big(\bigcup_F Y_F(s)\Big).
\]

A family is selected only through its members on that frontier or through a stronger registered total selection rule. Family names have no privileged status.

## 3. FP-1 — certified robust family exclusion

Suppose family `A` has a certified feasible witness with componentwise upper resource bound `U_A`, and every feasible member of family `B` obeys a proved componentwise lower bound `L_B`.

If

\[
U_A \preceq L_B
\]

with strict inequality in at least one registered coordinate, then every feasible `B` realization is dominated by the certified `A` witness in every evidence world compatible with those bounds.

Therefore `B` is robustly excluded from the Pareto-selected set at that scope.

### Proof

For the actual profile `y_A` of the witness, `y_A <= U_A`. For every actual `y_B in Y_B`, `L_B <= y_B`. Hence

\[
y_A \preceq U_A \preceq L_B \preceq y_B.
\]

At least one strict coordinate persists, so `y_A` dominates `y_B`. QED.

This theorem is stronger than comparing point estimates: it remains valid across the entire registered uncertainty set.

## 4. FP-2 — scalar interval phase law

Let a declared scalar selection functional reduce each family at parameter `s` to a certified optimum-cost interval

\[
J_F^*(s) \in [L_F(s),U_F(s)].
\]

If one family `A` satisfies

\[
U_A(s) < \min_{B\ne A} L_B(s),
\]

then `A` is the unique robust family winner at `s`.

If the best family intervals overlap, the family label is not identified by those bounds alone. The correct result is `UNDECIDED_FROM_CURRENT_EVIDENCE` unless some other registered hard constraint or selection coordinate resolves the overlap.

Thus a family phase diagram consists of:

- robust family regions where one interval lies strictly below all competitors;
- boundary/overlap regions where the current evidence does not identify one family;
- infeasible regions where no family survives hard gates.

No interpolation across an overlap region is licensed without an additional theorem or measurement.

## 5. FP-3 — crossover surface theorem

For two families with continuous certified scalar bounds, a change from a robust `A` region to a robust `B` region cannot occur without passing through a parameter set where the certified intervals touch or overlap:

\[
U_A(s) \ge L_B(s)
\quad\text{and/or}\quad
U_B(s) \ge L_A(s).
\]

Therefore candidate architecture transitions are not mysterious discontinuities in the theory. They occur where feasibility, reachability or comparative resource inequalities change sign.

The theorem does not assert that real resource laws are continuous; if hardware or developmental transitions are discontinuous, the registered model must represent that fact directly.

## 6. FP-4 — no universal neurality/non-neurality theorem from semantics alone

Assume two response-equivalent realizations `m_N` and `m_X` exist, one neural and one non-neural. If the problem specification does not fix a resource ordering that excludes either realization, then semantic adequacy alone cannot derive one family over the other.

Indeed, two legal substrate/resource models can assign opposite strict orderings to the same response-equivalent pair. Hence family identity is not invariant under response-preserving realization while physical resource vectors are allowed to deform.

This is a direct consequence of the Substrate Lifting, Realization Compilation and Morphology Selection layers.

## 7. FP-5 — hybrid decomposition upper bound

Suppose the protected operational obligation decomposes into regions `R_1,...,R_k` connected by registered semantic cuts, and the declared substrate resource composition law is additive for the chosen scalar resource `J`.

For a family assignment `f_i` to each region, if certified realizations give upper bounds `U_{f_i}(R_i)` and the required bridges/cuts have upper cost `U_bridge`, then the composed hybrid has

\[
J_{hybrid} \le \sum_i U_{f_i}(R_i) + U_{bridge}.
\]

If every pure-family realization has certified lower bound strictly above this hybrid upper bound, then the hybrid family is robustly selected under that scalar criterion.

This is not a claim that hybridization is always beneficial. The cut cost can erase the advantage, coupled obligations can invalidate the decomposition, and a non-additive substrate needs its own valid composition law.

## 8. FP-6 — hybrid necessity criterion

At registered scope, hybrid structure is **derived** rather than merely available if all selected morphologies contain at least two operationally distinct family realizations assigned to different required regions/cuts.

A constructive hybrid witness alone is insufficient. Pure neural and pure non-neural competitors must be excluded by hard feasibility, reachability or certified resource bounds.

## 9. Exact synthetic phase witness

Consider one scalar registered cost and task scale `s=1,...,8`. The following intervals are synthetic theorem witnesses only:

\[
J_N(s) \in [4+s,5+s]
\]

for the neural family,

\[
J_X(s) \in [1+2s,2+2s]
\]

for a non-neural exact family, and a hybrid family unavailable for `s<6` but, once a valid decomposition exists,

\[
J_H(s) \in [3+\lfloor s/2\rfloor,4+\lfloor s/2\rfloor].
\]

The exact checker verifies:

- `s=1`: non-neural is robustly selected (`U_X=4 < L_N=5`);
- `s=2,3,4`: current intervals overlap/touch, so the family label is not identified;
- `s=5`: neural is robustly selected (`U_N=10 < L_X=11`);
- `s=6,7,8`: hybrid is robustly selected once admissible, with its upper bound below both pure-family lower bounds.

This is an existence witness for all three family phases plus an underidentified boundary. It is not a claim about real machine costs.

## 10. Exact hybrid witness

Let an obligation decompose into a continuous/statistical region `R_s` and an exact symbolic region `R_x`, joined by a bridge of certified scalar upper cost `1`.

Registered bounds:

- neural `R_s` upper bound: `4`;
- neural `R_x` lower bound: `8`;
- non-neural `R_s` lower bound: `9`;
- non-neural `R_x` upper bound: `3`.

Then a hybrid witness has

\[
U_H \le 4+3+1=8,
\]

while any pure neural realization costs at least `4+8=12` under the declared additive region model, and any pure non-neural realization costs at least `9+3=12`.

So the hybrid is robustly selected in this declared synthetic scope.

The witness verifies the logic of hybrid derivation. Real use requires real or parent-theorem bounds for the regions and bridge.

## 11. Relation to neural architecture names

The phase law selects operational families only as finely as they are registered. If the neural region itself contains CNN-, Transformer-, GNN-, RNN- or MoE-like realizations, a second refinement step applies the same frontier logic inside the neural family using derived locality, symmetry, memory, routing and communication properties.

Likewise the non-neural family can refine into finite-state controllers, decision trees, programs, lookup tables, logic circuits, cellular automata, analog controllers, quantum processes or biological mechanisms.

Family selection and named-architecture selection are therefore recursive applications of the same admissibility/frontier law at different morphology resolutions.

## 12. What this adds to the master derivation

The end-to-end chain now has an explicit comparative phase step:

\[
\text{GMI obligation}
\to S^*
\to (\kappa,\tau)
\to \text{operational morphology constraints}
\to \{Y_F(s)\}_F
\to \text{certified family inequalities}
\to \text{family phase/verdict}
\to \text{within-family refinement}.
\]

This explains both NN and non-NN intelligence without declaring either universal.

## 13. Remaining external boundary

The theorem does not manufacture the functions `L_F(s)` and `U_F(s)` for real substrates. Those require:

- proved complexity/physics bounds;
- benchmark measurements with calibration and uncertainty;
- reachability/training/search evidence;
- deployment/generalization evidence;
- an explicit candidate universe.

At that point Grand GMI can compute a scope-relative family phase verdict. Without those inputs, the correct result remains `UNDECIDED_FROM_CURRENT_EVIDENCE` rather than an invented architecture preference.
