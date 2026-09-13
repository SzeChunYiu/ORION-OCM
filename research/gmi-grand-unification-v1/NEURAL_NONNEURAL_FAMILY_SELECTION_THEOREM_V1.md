# Grand GMI Neural / Non-Neural Family Selection Theorem V1

Status: **THEOREM / FAMILY-CONDITIONED FRONTIER LAW + EXACT INVERSION AND HYBRID WITNESSES**  
Date: 2026-09-12

## 1. Gap closed

The Realization Compilation Theorem proves that an operational GMI solution may have both neural and non-neural implementations. The Morphology Selection Theorem defines when a morphology property is genuinely derived from the reachable frontier.

This layer closes the next gap:

> How can the same Grand GMI problem select a neural, non-neural, or hybrid intelligence without privileging any implementation family in advance?

The answer is a family-conditioned attainable frontier followed by comparison in the declared substrate/resource model.

## 2. Realization families

Let `F` be a registered realization family. Examples include:

- `F_N`: neural parameterized networks;
- `F_P`: programs, Boolean/sequential circuits, decision structures and finite-state controllers;
- `F_A`: analog/control implementations;
- `F_Q`: quantum-process implementations;
- `F_B`: biological/process-network implementations;
- `F_H`: heterogeneous compositions of registered families.

These names are conveniences. The theorem acts on operationally defined family membership and resource maps, not historical labels.

For a GMI problem `G`, tolerance `epsilon`, substrate `P` and developmental budget `B`, define the family-conditioned admissible set

\[
\mathcal A_F=\mathcal A(\mathcal G,\mathbf P,\epsilon,B)\cap F.
\]

Its attainable profile image is

\[
Y_F=\{\pi(m):m\in\mathcal A_F\}.
\]

When an optimum is not known to be attained, all statements below use attainable points and Pareto sets rather than silently replacing infima by minima.

## 3. FS-1 — cross-family domination theorem

Let `F1` and `F2` be two registered families. If

\[
\forall y_2\in Y_{F2}\ \exists y_1\in Y_{F1}: y_1\preceq y_2
\]

and for every `F2` point at least one such comparison is strict in a registered coordinate, then no `F2` morphology lies on the global Pareto frontier of `Y_{F1} union Y_{F2}`.

### Proof

Every `F2` point is dominated by an attainable `F1` point, hence is not globally nondominated. QED.

This is the strongest family-level form of "Grand GMI selects neural" or "Grand GMI selects non-neural" under a Pareto criterion: the losing family is excluded because every attainable member is dominated, not because it was absent from the search space.

## 4. FS-2 — family derivation criterion

Let

\[
\mathcal M_F^*=\{m\in\mathcal A:\pi(m)\in\operatorname{Pareto}(\pi(\mathcal A))\}.
\]

A family property `Family_X(m)` is Pareto-derived iff

\[
\forall m\in\mathcal M_F^*,\ Family_X(m).
\]

Thus:

- **neural intelligence is derived** when every selected frontier morphology is neural at the registered operational resolution;
- **non-neural intelligence is derived** when every selected frontier morphology is non-neural;
- **hybrid intelligence is derived** when every selected frontier morphology requires components from more than one registered realization family;
- **family coexistence** is the correct verdict when multiple family types remain nondominated.

A scalar or lexicographic selection constitution can replace the Pareto rule, but the constitution must be declared rather than inferred from physics.

## 5. FS-3 — semantic family non-preference theorem

For every finite deterministic transformation, the Realization Compilation Theorem supplies both an exact threshold-network realization and an exact truth-table/circuit realization.

Therefore, from protected finite task semantics alone, neither neurality nor non-neurality is universally necessary.

More generally, if two families contain response-equivalent adequate realizations and no registered resource/intervention distinguishes them, then Grand GMI cannot select between those family labels.

This proves a negative but important result:

\[
\boxed{\text{semantics alone does not universally privilege neural or non-neural intelligence}.}
\]

Any family preference must enter through feasibility, resource physics, reachability, approximation class, robustness, intervention structure or an explicit selection rule.

## 6. FS-4 — substrate resource inversion theorem

Suppose one protected operational morphology has realizations `n in F_N` and `p in F_P`. Let two substrate declarations `P_A` and `P_B` preserve the same protected response but assign different valid physical resource profiles.

If on substrate `P_A`

\[
\rho_A(n)\prec\rho_A(p),
\]

while on substrate `P_B`

\[
\rho_B(p)\prec\rho_B(n),
\]

then the family selected by Pareto domination reverses across substrates while the semantic intelligence remains unchanged.

This is permitted by Substrate Lifting and the Physical Resource Bridge: semantic response can be substrate invariant while physical frontiers deform.

### Consequence

There can be no substrate-free theorem of the form "intelligence is fundamentally neural" or "intelligence is fundamentally symbolic" unless the family label has first been defined as a semantic property rather than an implementation property.

## 7. FS-5 — local family assignment theorem for factored morphologies

Let an operational morphology factor into regions `R_1,...,R_k` connected by registered cuts. Assume:

1. local adequacy/error budgets compose under a proved stability rule;
2. each region has a set of legal realizations from one or more families;
3. cut/interface conversion costs are explicitly included;
4. the declared resource composition law is known.

Then family selection can be performed over assignments

\[
a:\{R_i\}\to\{F_1,...,F_q\}
\]

by evaluating the composed attainable profile of each legal assignment.

If every globally selected assignment uses at least two families, hybrid morphology is derived at that registered scope.

This is not an assertion that local independent minimization always gives the global optimum. Interface conversion, shared resources, nonlinear resource composition and coupled error can make the assignment problem nonseparable.

## 8. FS-6 — separable hybrid optimum theorem

Under the stronger conditions that:

- the obligation factorizes across regions;
- local realization errors are independently bounded within their allocated tolerances;
- there is no cross-family interface penalty beyond already counted fixed cuts;
- the resource vector composes componentwise additively;

then the attainable resource vector of an assignment is the sum of its local vectors.

If for every region `R_i` there is a unique locally dominating family realization `f_i^*`, the assignment formed from those local winners dominates every assignment that substitutes a locally dominated implementation in any region.

Hence if at least two distinct families occur among the `f_i^*`, the globally dominating realization is hybrid.

### Proof

Replacing a locally dominating implementation by a dominated one weakly increases every additive resource coordinate and strictly increases at least one. Summing with unchanged regions preserves domination. Repeating this argument for every differing region shows the all-local-winner assignment dominates every alternative. QED.

The factorization assumptions are load-bearing. Coupled obligations or shared hardware can invalidate local-to-global optimality.

## 9. Exact resource-inversion witness

Take one exact protected transformation with a neural realization `N` and a program realization `P`.

On substrate A:

\[
\rho_A(N)=(2,2),\qquad \rho_A(P)=(5,3).
\]

`N` strictly dominates `P`.

On substrate B:

\[
\rho_B(N)=(5,3),\qquad \rho_B(P)=(2,2).
\]

`P` strictly dominates `N`.

Protected behavior is identical. Only substrate resource accounting changed. The selected family therefore flips without any change in the definition of intelligence.

## 10. Exact hybrid witness

Consider a two-region operational morphology with additive resource coordinates `(r1,r2)` and exact local obligations.

For region A:

- neural realization: `(1,2)`;
- program realization: `(5,5)`.

For region B:

- neural realization: `(5,5)`;
- program realization: `(1,2)`.

The four assignments have total profiles:

| A | B | profile |
|---|---|---|
| neural | neural | `(6,7)` |
| neural | program | `(2,4)` |
| program | neural | `(10,10)` |
| program | program | `(6,7)` |

The neural/program hybrid `(2,4)` strictly dominates every homogeneous assignment and the opposite hybrid. Under the stated separability assumptions, hybrid intelligence is therefore derived.

Again, the numbers are a proof witness for the selection law, not an empirical hardware claim.

## 11. Conditional diagnostic for neural selection

A neural family can become selected when the registered facts jointly establish, for example:

- the required local kernel lies in an approximation class efficiently realized by the chosen network family;
- the substrate supplies favorable parallel primitive operations, memory locality or accelerator structure;
- training/development can reach the required realization within budget;
- robustness/generalization coordinates are explicitly measured and favorable;
- competing exact/programmatic families are infeasible or resource dominated.

None of these is universal. Each must be demonstrated for the declared ecology, substrate and resource vector.

## 12. Conditional diagnostic for non-neural selection

A non-neural family can become selected when registered facts establish, for example:

- the semantic quotient is small/discrete and an exact controller/table/program realizes it compactly;
- zero-error, formal verification or bounded worst-case latency is a protected requirement;
- a symbolic/algorithmic implementation has a proved lower resource profile;
- training/sample cost makes a learned family dominated;
- developmental constraints directly construct the non-neural controller while neural alternatives are unreachable within budget.

Again these are conditional selection routes, not universal statements about symbolic systems.

## 13. Conditional diagnostic for hybrid selection

Hybrid selection is natural when the operational decomposition exposes regions with qualitatively different transformation/resource structure—for example perception plus exact safety logic, learned estimation plus symbolic planning, classical control plus quantum sensing, or neural local kernels plus an exact protocol layer.

Grand GMI does not call such a machine "less unified." The intelligence is the protected process network; implementation-family boundaries are internal morphology choices constrained by cuts, transformations and physics.

## 14. Why architecture names still do not automatically follow

Even after family selection, a neural winner does not imply a unique CNN/Transformer/GNN/RNN/MLP/MoE syntax. The same family can contain many response-equivalent and resource-incomparable morphologies.

Deriving a finer architecture requires repeating the Morphology Selection criterion inside the neural family using properties such as locality, recurrence, equivariance, routing, state retention, communication pattern and developmental reachability.

Likewise, selecting the non-neural family does not uniquely choose a table, circuit, program, automaton or classical controller.

## 15. Relation to the Grand GMI chain

The expanded derivation is now

\[
\mathcal G
\to S^*
\to \kappa
\to \tau
\to \text{symmetry/coupling}
\to \mathcal A
\to \{Y_F\}_F
\to \text{cross-family frontier}
\to \text{neural/non-neural/hybrid verdict}
\to \text{within-family morphology selection}.
\]

This is the first layer in the Grand GMI stack that states exactly what evidence is required to claim that an implementation paradigm, rather than merely an operational behavior, has been derived.

## 16. Remaining gap

The formal family-selection logic is now closed, but an explanatory gap remains for humans and for empirical use:

> Can the full chain be executed end to end on concrete obligations so that one can see semantic quotient, cut requirement, local computation, symmetry/coupling, realization and family selection in a single derivation trace?

The next round supplies worked neural, non-neural and hybrid derivations and marks exactly where each conclusion is theorem-forced versus resource-model conditional.
