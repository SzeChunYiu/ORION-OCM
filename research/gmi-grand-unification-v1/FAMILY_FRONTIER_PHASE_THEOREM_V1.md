# Grand GMI Family-Frontier Phase Theorem V1

Status: **THEOREM / ROBUST FAMILY-SELECTION LAW + HYBRID DECOMPOSITION LAW + EXACT SYNTHETIC WITNESSES**  
Date: 2026-09-12; corrected 2026-09-13

Correction authority: `FAMILY_PHASE_SOUNDNESS_CORRECTION_V1.md`. FP-3, FP-5 and
FP-6 below carry repaired hypotheses; the predecessor FP-3 condition was vacuous
and the predecessor §10 witness summed an upper bound into a lower bound.

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

then A has the uniquely smallest family infimum at s, assuming finite
bounds over nonempty adequate families. An **attained** robust winner
additionally requires the infimum of A to be achieved in every compatible
evidence world. A feasible witness of cost at most U_A robustly excludes
every competing family even without within-family attainment. If its family
lower bound is L_A, that witness has global regret at most U_A-L_A.
See `CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md` (MSC-3).
The candidate universe is the union of the registered family sets from
section 2; a claim over additional physical candidates needs a coverage proof.
All global infima and regret guarantees refer to that declared universe.
For a one-family register use min(empty)=+infinity.
The interval-ranking checker reports separation only; its finite synthetic
witnesses do not establish attainment for an infinite family.

Every registered interval must be well formed: `L_F(s) <= U_F(s)` in exact
arithmetic. Malformed bounds must be rejected, not compared. Two families
registered as `[5,0]` each satisfy the robustness test above, so an
unvalidated comparison can report two winners; validation and explicit
abstention are mandatory.

If the best family intervals overlap, the family label is not identified by those bounds alone. The correct result is `UNDECIDED_FROM_CURRENT_EVIDENCE` unless some other registered hard constraint or selection coordinate resolves the overlap.

Thus a family phase diagram consists of:

- robust family regions where one interval lies strictly below all competitors;
- boundary/overlap regions where the current evidence does not identify one family;
- infeasible regions where no family survives hard gates.

No interpolation across an overlap region is licensed without an additional
theorem or measurement. On a discrete scale register the regions are the
registered parameters themselves; nothing is claimed between them.

## 5. FP-3 — crossover surface theorem

The predecessor version of this section asserted that a change from a robust
`A` region to a robust `B` region must pass through a parameter where

`U_A(s) >= L_B(s)` and/or `U_B(s) >= L_A(s)`.

That disjunction is **vacuous**. Robust `B` means `U_B < L_A`, and a
well-formed interval satisfies `L_B <= U_B` and `L_A <= U_A`, so

`L_B <= U_B < L_A <= U_A`

already gives `U_A >= L_B` at every robust-`B` parameter. The stated set
contains the destination region and identifies no boundary.

> **FP-3a — pairwise crossover abstention.** Let the parameter domain contain
> a path from `s1` to `s2` on which every registered interval is well formed
> and `L_B - U_A` is continuous. If `A` is robust at `s1` and `B` is robust at
> `s2`, then some `s*` on that path satisfies `U_A(s*) = L_B(s*)`, and at `s*`
> neither `A` nor `B` is robust.

### Proof

Put `f = L_B - U_A`. Robustness of `A` at `s1` gives `f(s1) > 0`. At `s2`,
well-formedness and robustness of `B` give `L_B <= U_B < L_A <= U_A`, so
`f(s2) < 0`. The intermediate value theorem supplies `s*` with `f(s*) = 0`.
Then `U_A(s*) < L_B(s*)` fails, so `A` is not robust. And
`U_B(s*) >= L_B(s*) = U_A(s*) >= L_A(s*)`, so `U_B(s*) < L_A(s*)` fails and
`B` is not robust. QED.

Three hypotheses are load bearing.

1. **Well-formedness.** With `A = [1,2]` and a malformed `B = [5,0]`, `B`
   passes the robustness test while `U_A = 2 < 5 = L_B`, so the chain breaks.
2. **A connected domain.** On the registered scale set `{1,2}` with
   `A = [1,2]`, `B = [5,6]` at `s = 1` and `A = [7,8]`, `B = [3,4]` at
   `s = 2`, the verdict is robust `A` then robust `B` and no registered
   parameter abstains. A discrete phase register therefore may not claim an
   intervening boundary.
3. **Pairwise scope.** The conclusion is about the pair `{A,B}`, not the
   global verdict. At the witness root `s* = 3/10` below, a third family with
   interval `[1/2,1]` is robust, because `1 < 14/5` and `1 < 19/5`.

Therefore candidate architecture transitions are not mysterious
discontinuities in the theory: on a connected parameter path they occur where
feasibility, reachability or comparative resource inequalities change sign.
The theorem does not assert that real resource laws are continuous; if
hardware or developmental transitions are discontinuous, or the register is
discrete, the registered model must represent that fact directly and the
abstention conclusion is withdrawn.

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

If every pure-family realization has certified lower bound strictly above
this hybrid upper bound, those pure families are robustly excluded under that
scalar criterion. A selected hybrid optimum additionally needs a nonempty
attained selected set; exclusion does not establish within-hybrid attainment.

Two directional hypotheses are mandatory when that exclusion is applied.

> **FP-5a — lower bounds sum lower bounds.** A lower bound on a pure family's
> regional total is `sum_i L_F(R_i)`. A registered **upper** bound for a region
> may never appear as a term of a pure-family lower bound. If a regional lower
> bound is unregistered, only non-negativity may be assumed for it.

> **FP-5b — decomposition-closed candidates.** `sum_i L_F(R_i)` lower bounds
> only those realizations that factor through the registered regions with
> additively charged costs. Excluding a pure family requires that every
> admissible member of it be decomposition closed, or that the bound be proved
> directly for the whole obligation. A monolithic realization that never
> instantiates the registered cut is not bound by the regional sum.

The additive regional law is declared in order to **compose** a hybrid upper
bound. Reusing it as a **necessity** for competitors without FP-5b is the same
direction error that `SUFFICIENCY_DIRECTIONS_AUDIT_V1.md` repairs elsewhere.

This is not a claim that hybridization is always beneficial. The cut cost can erase the advantage, coupled obligations can invalidate the decomposition, and a non-additive substrate needs its own valid composition law.

## 8. FP-6 — hybrid necessity criterion

At registered scope, hybrid structure is **derived** rather than merely available if the selected set is nonempty and all selected morphologies contain at least two operationally distinct family realizations assigned to different required regions/cuts.

A constructive hybrid witness alone is insufficient. Pure neural and pure non-neural competitors must be excluded by hard feasibility, reachability or certified resource bounds, and any exclusion that uses a regional sum inherits FP-5a and FP-5b. Where either fails, the verdict is `UNDECIDED_FROM_CURRENT_EVIDENCE`.

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

Let an obligation decompose into a continuous/statistical region `R_s` and an
exact symbolic region `R_x`, joined by a bridge of certified scalar upper cost
`1`.

The predecessor version of this section registered

- neural `R_s` **upper** bound `4`;
- neural `R_x` lower bound `8`;
- non-neural `R_s` lower bound `9`;
- non-neural `R_x` **upper** bound `3`,

and then asserted pure-family lower bounds `4 + 8 = 12` and `9 + 3 = 12`. Both
sums violate FP-5a by using a registered upper bound as a term of a lower
bound. With non-negativity alone the sound pure-neural bound is `0 + 8 = 8`,
which does not strictly exceed the hybrid upper bound `8`: the evidence world
with neural smooth cost `0` and neural exact cost `8` satisfies every
registered bound and ties the hybrid. The predecessor verdict was therefore not
robust. The non-neural exclusion survives, because its smooth-region **lower**
bound was registered and `9 + 0 = 9 > 8`.

Repaired registration:

- neural `R_s` lower bound `4`, upper bound `4`;
- neural `R_x` lower bound `8`;
- non-neural `R_s` lower bound `9`;
- non-neural `R_x` lower bound `3`, upper bound `3`;
- bridge upper bound `1`.

Then the hybrid witness has

\[
U_H \le 4+3+1=8,
\]

while every **decomposition-closed** pure neural realization costs at least
`4 + 8 = 12` and every decomposition-closed pure non-neural realization at
least `9 + 3 = 12`.

So the hybrid is robustly selected in this declared synthetic scope, over the
decomposition-closed candidate class only. Dropping FP-5b breaks the verdict:
a monolithic pure-neural realization of total cost `6` is compatible with a
substrate model that never instantiates the registered cut, and it defeats the
hybrid selection, returning `UNDECIDED_FROM_CURRENT_EVIDENCE`.

The witness verifies the logic of hybrid derivation. Real use requires real or
parent-theorem bounds for the regions and bridge, in the correct direction, and
a proof that the candidate class is decomposition closed.

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

- proved complexity/physics bounds, each in the direction it is used;
- benchmark measurements with calibration and uncertainty;
- reachability/training/search evidence;
- deployment/generalization evidence;
- an explicit candidate universe.

At that point Grand GMI can compute a scope-relative family phase verdict. Without those inputs, the correct result remains `UNDECIDED_FROM_CURRENT_EVIDENCE` rather than an invented architecture preference.
