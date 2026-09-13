# Grand GMI Epistemic Acquisition Theorem V1

Status: **THEOREM + EXHAUSTIVE FINITE WITNESSES**  
Date: 2026-09-12

## 0. Why this is the next derived law

The Grand-GMI master theory already types causal discovery, active learning and exploration as development/control processes that change future semantic state. That is an ontology reduction. This document adds a quantitative law: **how much experimentation is required to identify only the part of the ecology that matters to the downstream obligation**.

No new primitive is introduced. Epistemic acquisition is a derived problem over the existing objects `(S*, Theta, D, rho)`.

---

## 1. Finite experiment problem

Let

- `W` be a finite set of possible worlds/models;
- `X` a finite set of legal experiments/interventions;
- `Y_x` the finite outcome alphabet of experiment `x`;
- `O(w,x)` the exact deterministic experiment outcome in world `w`;
- `sigma_Omega(w)` the **obligation-relevant world class** induced by Grand GMI: two worlds receive the same label when every declared downstream continuation has the same protected obligation-response profile.

Thus `sigma_Omega` is not an arbitrary architecture label. It is the ecology-side analogue of the exact semantic response quotient.

For a current candidate set `S subseteq W`, write

`S_(x,y) = {w in S : O(w,x)=y}`.

An adaptive experiment policy is successful when every terminal leaf contains worlds from only one `sigma_Omega` class.

## 2. Epistemic acquisition complexity

For unit-cost experiments define

\[
\eta_\Omega(S)=
\begin{cases}
0,& |\sigma_\Omega(S)|\le 1,\\
1+\min_{x\in X}\max_{y:S_{x,y}\ne\varnothing}\eta_\Omega(S_{x,y}),&\text{if a separating experiment exists},\\
\infty,&\text{otherwise}.
\end{cases}
\]

An experiment that leaves `S` unchanged on every possible outcome is not a separating choice.

For exact nonnegative experiment costs `c(x)`, replace the leading `1` by `c(x)`. The resulting quantity is a worst-case resource coordinate and needs no probability prior over worlds.

**EA-1 — Epistemic Acquisition Theorem.** For every finite deterministic experiment problem, `eta_Omega(W)` equals the minimum worst-case experiment cost of an adaptive policy that identifies the obligation-relevant world class exactly.

**Proof.** Any successful first experiment `x` pays its cost and must thereafter solve every nonempty residual candidate set `S_(x,y)`, giving the lower-bound recurrence. Conversely, choosing an experiment attaining the recurrence and recursively following the corresponding optimal subpolicy constructs a decision tree with exactly that cost. Finite descent closes the induction. If two obligation-distinct worlds have identical response rows under all experiments, no policy can separate them and the value is infinite. QED.

The theorem is parent-compatible with optimal decision trees/exact query learning. Grand GMI contributes the obligation-derived target quotient and its composition with the master semantic/resource theory, not the generic decision-tree recurrence.

---

## 3. Full-world learning is generally unnecessary

Let `~_X` be observational equivalence under the complete registered experiment family:

\[
w\sim_X w'\iff O(w,x)=O(w',x)\quad\forall x\in X.
\]

The finest learnable world description is `W/~_X`. If `sigma_Omega` is identifiable, it is constant on every `~_X` class and is therefore a coarsening of this maximum experimental resolution.

Let `eta_full` denote the acquisition depth for identifying `W/~_X`.

**EA-2 — Semantic Sufficiency Savings Theorem.** Whenever `sigma_Omega` is experimentally identifiable,

\[
\boxed{\eta_\Omega(W)\le \eta_{full}(W).}
\]

The inequality can be strict.

This is the key GMI consequence: a machine need not discover causal/environmental distinctions that cannot alter any protected downstream obligation response.

### Canonical exact witness

Four worlds have binary outcomes under experiments `A,B,C`:

| world | A | B | C | semantic class |
|---|---:|---:|---:|---:|
| w0 | 0 | 0 | 0 | 0 |
| w1 | 0 | 1 | 0 | 0 |
| w2 | 1 | 0 | 0 | 1 |
| w3 | 1 | 0 | 1 | 1 |

Experiment `A` identifies the obligation-relevant class in **one** intervention. Exact world identification needs adaptive depth **two**: after `A=0`, ask `B`; after `A=1`, ask `C`. Every fixed pair of experiments fails to identify all four worlds, so a nonadaptive panel needs **three**.

Therefore

\[
\eta_\Omega=1 < \eta_{full}^{adaptive}=2 < \eta_{full}^{fixed}=3.
\]

---

## 4. Adaptivity is a morphology/resource effect

A fixed experiment panel is a special case of an adaptive experiment tree. Hence

\[
\eta^{adaptive}\le \eta^{fixed}.
\]

The inequality can be strict because an early result can determine which later semantic cut remains unresolved.

**EA-3 — Adaptive Branching Advantage.** There exist finite experiment families for which no fixed panel of `d` experiments identifies the relevant classes but an adaptive depth-`d` policy does.

The exhaustive checker finds strict adaptive advantage in **576 of 4,096** binary `4-world x 3-experiment` response matrices when the target is the finest experimentally identifiable world partition.

Adaptivity is therefore not an extra intelligence primitive. It is a resource-efficient causal-process morphology for routing later experiments conditional on earlier semantic state.

---

## 5. Information lower bound

Suppose every experiment has at most `b` possible outcomes and the current candidate set contains `k` obligation classes that all must remain distinguishable in the worst case. A depth-`d` experiment tree has at most `b^d` leaves. Therefore

\[
\boxed{\eta_\Omega\ge \lceil\log_b k\rceil}
\]

whenever every class must occupy a distinct leaf.

**EA-4 — Epistemic Cut Lower Bound.** Experimentation is a sequence of semantic cuts. The total branching capacity of those cuts must be sufficient to separate the required obligation classes.

This lower bound may be loose because the legal experiment family can impose structural restrictions stronger than raw outcome capacity.

---

## 6. Causal discovery as obligation-relative experiment design

Let each `w in W` be a candidate causal process/model and each `x in X` a legal intervention. Standard causal discovery often targets full graph/model identifiability. Grand GMI instead permits the target quotient

\[
w\equiv_\Omega w'
\]

whenever the two causal models induce the same protected downstream response profile for the declared obligation.

**EA-5 — Obligation-Relative Causal Discovery Theorem.** In a finite exact causal-model class, the minimum worst-case number/resource of interventions required for task-sufficient causal discovery is exactly the epistemic acquisition complexity of the obligation quotient, not necessarily the complexity of full causal-model identification.

Thus two causal graphs may remain unresolved forever with no intelligence deficit if every distinction between them is Omega-null at the declared boundary.

This does not deny the value of full scientific identification; it distinguishes a scientific obligation that asks for the graph itself from an instrumental obligation that only requires downstream adequate action.

---

## 7. Prior-free active experiment selection

The recurrence in section 2 minimizes worst-case residual cost over the admitted world set. No distribution over worlds is required.

A Bayesian posterior, information gain, expected entropy reduction or other scalar acquisition function can be added as an optional selector when a source law/prior is declared. Those selectors are not foundational to the minimax GMI object.

**EA-6 — Prior-Free Experiment Design.** Finite robust active experiment design is well-defined from the admitted ecology set, obligation quotient, legal intervention family and resource costs alone.

---

## 8. Exhaustive microscope

`grand_gmi_epistemic_checks_v1.py` exhausts all `2^12 = 4,096` binary four-world/three-experiment response matrices.

For full experimentally accessible world identification:

- adaptive depth is no worse than minimum fixed-panel size in **4,096/4,096** matrices;
- the binary leaf-count lower bound holds in **4,096/4,096** matrices;
- strict adaptive advantage occurs in **576/4,096** matrices.

The checker then crosses every matrix with every binary obligation labelling of the four worlds: `4,096 x 16 = 65,536` exact instances.

- **44,592** obligation labellings are experimentally identifiable;
- **20,944** are impossible because experimentally indistinguishable worlds demand different semantic labels;
- **36,400** identifiable cases have a nontrivial two-class obligation;
- in **27,472** identifiable cases, obligation-relevant identification is strictly cheaper than identifying the finest experimentally accessible world class.

Aggregate terminal:

`GRAND_GMI_EPISTEMIC_ACQUISITION_TRANCHE_ALL_GREEN`.

---

## 9. Parent subtraction

Parent theory owns major components:

- exact learning from queries and query-complexity lower bounds;
- optimal/adaptive decision trees;
- active experimental design and active causal discovery;
- Bayesian and information-theoretic acquisition criteria when a probabilistic model is supplied.

Representative donors include Angluin's exact query-learning framework, Hauser–Buhlmann active causal intervention design, and modern causal active-learning work for intervention optimization.

The Grand-GMI residual is the typed synthesis:

\[
\boxed{
\text{obligation}\to\text{ecology semantic quotient}\to
\text{minimum experiment tree}\to\text{updated semantic state/reachability}\to
\text{downstream morphology frontier}.
}
\]

It specifically predicts when **not** learning the full world is optimal because the omitted distinctions are provably irrelevant to the protected obligation.

---

## 10. Scope and falsifiers

This V1 theorem is exact for finite deterministic experiment families. Stochastic observations require a declared error criterion and become a sequential experiment-design / hypothesis-testing problem; continuous model spaces require regularity and measurable-selection assumptions.

Falsifiers at the finite scope are direct:

1. an identifiable instance whose optimal adaptive depth differs from the recurrence;
2. a valid adaptive policy deeper than the best fixed panel while no equally good adaptive policy exists;
3. an identifiable obligation quotient requiring more experiments than its finest experimentally accessible world partition;
4. any mismatch in the exhaustive receipt counts.

None occurs in the frozen checker.