# Grand GMI Morphology Selection Theorem V1

Status: **THEOREM / CONDITIONAL ARCHITECTURE-DERIVATION CRITERION + EXACT FINITE WITNESS**  
Date: 2026-09-12

## 1. Gap closed

The Realization Compilation Theorem establishes that the same operational intelligence can have neural and non-neural realizations. The remaining question is stronger:

> Under what conditions can Grand GMI say that a morphology is *derived*, rather than merely compatible with the task?

This document defines that word operationally. The answer is not "when one architecture works." A morphology property is derived only when the registered problem, physical constraints, reachability conditions and selection rule force that property across the relevant optimum/frontier set.

## 2. Morphology descriptor

Let a candidate morphology be described by

\[
m=(G_m,\mathbf c_m,\mathbf k_m,\mathbf s_m,\mathbf u_m,\mathbf p_m),
\]

where:

- `G_m` is the process/interconnection graph;
- `c_m` gives cut/interface capacities and carrier types;
- `k_m` gives local transformation/kernel classes;
- `s_m` gives symmetry/equivariance or parameter-sharing structure;
- `u_m` gives update/development rules;
- `p_m` gives the substrate realization declaration.

The descriptor is operational: two source-code graphs that compile to the same protected process can belong to the same morphology class at the registered resolution.

## 3. Admissible morphology set

For a registered problem `G`, substrate declaration `P`, tolerance `epsilon` and developmental budget `B_dev`, define the admissible set

\[
\mathcal A(\mathcal G,\mathbf P,\epsilon,B_{dev})
\]

as the candidate morphologies satisfying **all** applicable constraints:

1. **obligation adequacy:** protected error is at most `epsilon`;
2. **semantic-cut feasibility:** each cut can support the required point of `kappa(C,epsilon_C)`;
3. **local transformation feasibility:** each region can support the required point of `tau(R,epsilon_R)`;
4. **process legality:** composition/interventions are legal in `P`;
5. **physical feasibility:** the Physical Resource Bridge maps the operational requirements to realizable substrate states/processes;
6. **declared structural constraints:** locality, topology, causal order, precision, robustness or other registered restrictions are met;
7. **developmental reachability:** the morphology is reachable from the registered initial morphology under admitted updates within `B_dev`.

A symmetry theorem may justify restricting attention to an equivariant representative when its hypotheses hold; it does **not** make every optimum syntactically symmetric unless necessity has separately been proved.

Likewise, a factorization theorem may guarantee a factorized optimum when exact product hypotheses hold; it does not license modularity when the obligation is coupled.

## 4. Resource/profile map

Let

\[
\pi(m)=(L_1(m),...,L_r(m),\rho_1(m),...,\rho_d(m))
\]

collect the registered loss/capability deficits and physical/resource coordinates to be minimized. Coordinates can include error, latency, energy, memory, communication, matter, precision burden, training cost, sample use, fragility or other declared quantities.

Define the **reachable morphology frontier**

\[
\mathfrak F_{\mathcal G}=\operatorname{Pareto}\{\pi(m):m\in\mathcal A\}.
\]

If the attainable profile image is compact and nonempty in finite dimensions, the existing Grand GMI compact-frontier result guarantees at least one Pareto point. Without attainment/compactness, replace minimum language by infimum language.

## 5. MS-1 — Pareto exclusion theorem

Let `m1,m2 in A`. If

\[
\pi(m_1)\preceq\pi(m_2)
\]

coordinatewise and the inequality is strict in at least one coordinate, then `m2` is not on the reachable morphology frontier.

### Proof

This is the definition of Pareto domination. Since `m1` is feasible and reachable, `m2` is dominated by another admissible morphology and therefore cannot be nondominated. QED.

This trivial-looking theorem is the exact point where implementation alternatives become *selectable* rather than merely realizable.

## 6. MS-2 — derived-property criterion

Let `P(m)` be any operational morphology property: for example finite memory, equivariance, a minimum communication width, recurrence, modular factorization, centralized state, a particular carrier class, neurality, non-neurality, or a hybrid decomposition.

Define

\[
\mathcal M_F=\{m\in\mathcal A:\pi(m)\in\mathfrak F_{\mathcal G}\}.
\]

Then `P` is **Pareto-derived at the registered scope** iff

\[
\boxed{\mathcal M_F\ne\varnothing\quad\text{and}\quad\forall m\in\mathcal M_F,\ P(m).}
\]

Nonemptiness is essential. Adequate scalar costs {1/n:n>=1} have no
Pareto point: 1/(n+1)<1/n improves every candidate. The universal predicate
alone would derive both P and its negation over the empty selected set.
Use NO_SELECTED_REALIZATION for proved nonattainment, distinct from an
empty feasible set and from unknown attainment. A finite nonempty covering
construction can supply attainment; see
`CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md` (MSC-1–3).

If there exists even one frontier morphology for which `P(m)` is false, `P` is not necessary under the registered Pareto criterion.

This gives an anti-handwaving test for claims such as "GMI derives a neural network": neurality must hold for every relevant frontier realization, not merely for one successful construction.

## 7. MS-3 — unique-selection theorem

Let the registered selection functional be a total preorder `preceq_*` on admissible morphologies—for example a declared scalarized resource objective, lexicographic order or externally supplied design constitution. Suppose an optimum exists and its protected morphology equivalence class is unique:

\[
[m^*]=\operatorname*{argmin}_{m\in\mathcal A} \preceq_* .
\]

Then every operational property invariant within `[m*]` is selected by the registered problem.

If multiple inequivalent minimizers remain, only their common properties are derived. Source syntax is still not identifiable unless it is itself registered as a protected property/resource.

## 8. MS-4 — constraint-origin theorem

Every derived morphology property must enter through at least one typed source:

\[
\boxed{
\text{obligation}
\;|\;
\text{ecology}
\;|\;
\text{cut/transform lower bound}
\;|\;
\text{symmetry/coupling theorem}
\;|\;
\text{substrate physics}
\;|\;
\text{developmental reachability}
\;|\;
\text{declared selection rule}.
}
\]

Every claimed property needs a proof from the registered feasible/selected
set and the relevant source assumptions. Invariance when the specification
is unchanged is expected, and does not indicate an inserted prior. Nor must
a derived invariant cease to hold in another specification. A property
supported only by a chosen source implementation or historical name, without
that selected-set entailment, has not been derived at the claimed scope.

This is a provenance criterion, not a claim that deriving the frontier is computationally easy.

## 9. MS-5 — architecture-name boundary

Let `A_name` be a named implementation family such as CNN, Transformer, GNN, RNN, MLP, MoE, decision tree, program, finite-state controller or cellular automaton.

Grand GMI **derives the named family at scope S** only if all of the following hold:

1. the family is operationally defined at scope `S`, rather than only by historical/source-code convention;
2. at least one adequate reachable realization in that family exists;
3. an attainment theorem justifies optimum language if optimum is claimed;
4. every selected optimum/frontier member belongs to the registered operational equivalence class of that family, or the selection rule uniquely chooses it;
5. competing families are excluded by proved feasibility, response, resource or reachability constraints—not by omission from the candidate set.

Therefore a theorem deriving translation equivariance and local weight sharing may derive a **convolution-like operational property** without uniquely deriving the historical software category "CNN." A non-neural stencil program or cellular automaton may implement the same operational property.

## 10. MS-6 — reachability can reverse static selection

Let `F_static` be the Pareto frontier over all physically realizable morphologies and `F_reach` the frontier over morphologies reachable under the registered developmental dynamics/budget.

In general

\[
F_{reach}\ne F_{static}.
\]

A statically superior architecture may be absent from `F_reach` if no admitted update path reaches it. Conversely, a worse static design can be developmentally selected because it is reachable.

This is the formal place where training, architecture search, evolution, self-modification and path dependence affect the derived realized form.

`DEVELOPMENTAL_UNDERDETERMINATION_THEOREM_V1.md` distinguishes what static
summaries identify from what an additional development model supplies.
Different compatible development laws can yield different reachable frontiers
(DU-1). A chosen schedule and existential reachability across all admitted
schedules are distinct objects (DU-2). Feasible-set restriction preserves
lower bounds; comparative exclusion survives only when its supporting
construction remains feasible in the same scope (DU-3). Finally, a finite
observed prefix alone need not settle an unbounded verdict, while a finite
exact reachable-set closure certificate can settle it (DU-4). These results
leave constructive research under registered development laws open.

## 11. Exact finite witness

Consider five adequate implementations of one protected Boolean obligation. All have exact response error zero after compilation.

| Morphology | family | energy | memory | latency | reachable | property `shared-local` |
|---|---|---:|---:|---:|---|---|
| `N_shared` | neural | 4 | 3 | 2 | yes | yes |
| `P_shared` | program | 3 | 5 | 1 | yes | yes |
| `N_dense` | neural | 8 | 8 | 4 | yes | no |
| `T_table` | table | 2 | 16 | 1 | yes | no |
| `X_ideal` | exotic | 1 | 1 | 1 | no | yes |

On the reachable set:

- `N_dense` is dominated by `N_shared` and is excluded;
- `N_shared`, `P_shared` and `T_table` are mutually nondominated;
- `X_ideal` would dominate everything but is unreachable and therefore cannot determine the developmental frontier.

Consequences:

1. exact task semantics do not derive neurality: both neural and non-neural families remain on the frontier;
2. adding a registered memory budget `memory<=6` excludes `T_table`, but neurality is still not derived because `P_shared` remains;
3. adding `memory<=4` **and** `latency<=2` leaves `N_shared` as the unique reachable candidate among this declared finite set;
4. deleting the reachability constraint would select `X_ideal`, demonstrating that static physical optimality and developmental selection differ.

The witness is not evidence that these numbers describe real hardware. It verifies the selection logic and makes every assumption visible.

## 12. Operational derivation patterns

### 12.1 Local translational task

If the obligation/ecology is translation symmetric and substrate communication is local, the symmetry and physical-cut layers can justify repeated local equivariant transformations. This narrows morphology toward convolution-like or stencil-like computation.

It still does not uniquely select a CNN: a shared-kernel neural implementation, a finite-difference stencil, a cellular automaton or specialized circuit can realize the same operational structure.

### 12.2 Exchangeable set/graph task

Permutation symmetry plus coupled local relations can justify permutation-equivariant local updates and invariant/equivariant aggregation. Neural message passing is one realization; a classical distributed algorithm is another.

### 12.3 Exact symbolic controller

If the semantic quotient is small and finite, exact transition rules are required, and verification/memory resources make a finite-state controller nondominated while approximate neural alternatives are dominated or infeasible, a non-neural morphology can be derived at that registered scope.

These are theorem schemas. The actual family choice requires measured/proved resource profiles.

## 13. What this closes

Before this theorem the chain ended at "these operational constraints exist." It now continues to:

\[
\text{constraints}
\to \mathcal A
\to \pi(\mathcal A)
\to \text{reachable Pareto/selected set}
\to \text{properties common to selected morphologies}.
\]

That is the formal criterion for saying a morphology property was derived.

## 14. Remaining gap

The criterion is family neutral. It still does not tell us when the **neural**, **non-neural**, or **hybrid** realization family wins under a declared substrate.

The next layer must compare family-conditioned attainable frontiers and prove selection, coexistence, inversion and hybrid decomposition results without assuming that one implementation paradigm is universally privileged.
