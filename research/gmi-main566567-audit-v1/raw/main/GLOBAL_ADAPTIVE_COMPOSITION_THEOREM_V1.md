# Global adaptive inference and composition theorem V1 — GAC-1–5

Status: **THEOREM AT DECLARED CONDITIONAL-VALIDITY SCOPE**  
Date: 2026-09-13

This theorem extends the system-level interface around ARC-1–4. The statistical mechanism is not claimed novel: it is an application of nonnegative supermartingales, Ville's inequality, confidence sequences, sequential e-values/e-processes and predictable betting. Relevant parents include Howard et al. (2021), Ramdas et al. (2023), Grünwald–de Heide–Koolen (2024), Vovk/Wang on sequential e-values, and Xu–Wang–Ramdas on adaptive bandit multiple testing.

The GMI contribution here is the explicit contract for repeated components, dependent components, dynamically born components, unbounded operation and typed system composition.

## 1. Global filtration contract

Fix a filtered probability space `(Omega,F,(F_t)_{t>=0},P)` and a null/environment class `N`. All statements below must hold for every `P in N`.

At step `t`, before the new outcome(s) are revealed, the scheduler may use the complete global past `F_{t-1}` to:

1. revisit any existing component/row;
2. activate several components;
3. create finitely or countably many new component identifiers;
4. choose a randomized allocation using randomness already included in `F_{t-1}`;
5. stop, continue, branch or change the future schedule.

Let `A_t` be the active identifiers at step `t`. Membership of `A_t` and all allocations below are `F_{t-1}`-measurable. A component can be active at arbitrarily many nonconsecutive steps.

For every active component `j`, let `L_{j,t} >= 0` be `F_t`-measurable and satisfy the **global conditional validity contract**

\[
\boxed{\mathbb E_P[L_{j,t}\mid F_{t-1}]\le 1.}
\]

The expectation is with respect to the complete global pre-step history, not merely the component's private history.

No independence between components, rows, outcomes or agents is assumed.

## 2. GAC-1 — predictable self-financing composition

Before observing step `t`, choose nonnegative `F_{t-1}`-measurable weights

\[
w_{0,t},\{w_{j,t}:j\in A_t\},\qquad
w_{0,t}+\sum_{j\in A_t}w_{j,t}=1.
\]

`w_{0,t}` is unbet reserve. Countably many active accounts are allowed when the nonnegative series is well defined.

Define

\[
G_t=w_{0,t}+\sum_{j\in A_t}w_{j,t}L_{j,t},\qquad
K_0=1,\qquad K_t=K_{t-1}G_t.
\]

> **GAC-1.** `(K_t)` is a nonnegative supermartingale under every `P in N`.

Proof. Predictability lets the weights leave the conditional expectation. Conditional monotone convergence handles a countable nonnegative sum. Therefore

\[
\mathbb E_P[G_t\mid F_{t-1}]
\le w_{0,t}+\sum_j w_{j,t}=1.
\]

Since `K_{t-1}` is nonnegative and `F_{t-1}`-measurable,

\[
\mathbb E_P[K_t\mid F_{t-1}]
=K_{t-1}\mathbb E_P[G_t\mid F_{t-1}]
\le K_{t-1}.
\]

QED.

Interpretation: the whole system may redistribute evidence capital among existing or newly created modules, but it cannot create capital by looking at the new outcome first or by duplicating already-spent capital.

## 3. GAC-2 — repeated visits, dependence and dynamic birth

GAC-1 already covers the three requested cases.

### Repeated revisiting

The same identifier `j` may occur in `A_t` at any sequence of times selected from the global history. There is no reset when it is revisited. The only requirement is that each new factor satisfy the global conditional validity contract at the time it is used.

### Dependence between rows/components

The vector `(L_{j,t})_{j in A_t}` may be arbitrarily dependent conditional on the past. Linearity of conditional expectation, not product independence, proves GAC-1. Cross-time dependence is also allowed whenever the declared null still supplies each factor's conditional expectation bound given the full global past.

This does **not** imply that a static row distribution can be estimated under arbitrary drift. If the scientific claim is `Y | row=j ~ P_j` for one fixed `P_j`, that fixed conditional-law premise (or a different valid dependent-data construction) is still required.

### Dynamic row/module creation

Let new identifiers be born at times decided from `F_{t-1}`. Before birth their allocation is zero. At and after birth they may receive predictable capital and emit globally conditionally valid factors.

A new name does not reset an error budget, support assumption, evidence lineage or resource charge. If the outcome used to justify birth is also reused as though it were unseen when constructing the first factor, global conditional validity must be re-proved; renaming alone gives no protection.

Thus a potentially unbounded registry is valid provided only countably many accounts receive positive allocation along a realized countable execution and the self-financing sum is well defined.

## 4. GAC-3 — unbounded operation and arbitrary stopping

By Ville's inequality for a nonnegative supermartingale starting at one,

\[
\boxed{
P\left(\sup_{t\ge0}K_t\ge 1/\alpha\right)\le\alpha
}
\]

for every `alpha in (0,1)` and every `P in N`.

Therefore monitoring can continue for an unbounded number of steps and the stopping time need not be fixed in advance. The result controls false rejection/evidence-threshold crossing; it does not guarantee eventual stopping, finite expected cost, power, learning convergence or nonvacuous confidence width.

The selected-row special case sets one `w_{j,t}=1` and all other weights to zero. Parallel composition uses several positive weights. A changing mixture is safe because the weights are chosen before the new factors are observed.

## 5. GAC-4 — countably many dynamically born confidence sequences

Testing/evidence composition is not the same object as simultaneous parameter estimation. A separate error-budget corollary handles dynamically born confidence sequences.

Enumerate rows/modules in birth order `j=1,2,...`. At the predictable birth time `B_j`, choose an `F_{B_j-1}`-measurable budget `alpha_j >= 0` such that, pathwise,

\[
\sum_{j\ge1}\alpha_j\le\alpha.
\]

For row `j`, suppose its confidence sequence `(C_{j,n})` satisfies the conditional guarantee

\[
P\left(\exists n\ge1:\theta_j\notin C_{j,n}
\mid F_{B_j-1}\right)\le\alpha_j.
\]

The visit count `n` may be reached at arbitrary adaptive global times; the row procedure must itself be valid for those visit times under the full filtration.

> **GAC-4.** With probability at least `1-alpha`, every confidence sequence covers its target at every attained visit count, simultaneously over all dynamically born rows.

Proof. Let `F_j` be row `j`'s eventual failure event. By the tower property,

\[
P(F_j)=E[P(F_j\mid F_{B_j-1})]\le E[\alpha_j].
\]

For the first `m` births, the union bound gives

\[
P(\cup_{j\le m}F_j)\le E[\sum_{j\le m}\alpha_j]\le\alpha.
\]

Let `m -> infinity`; continuity from below yields the countable result. No row independence is used. QED.

A deterministic choice such as `alpha_j = alpha/2^j` is always admissible. Predictable data-dependent budgets are also admissible when the pathwise sum constraint and each conditional row guarantee are preserved.

ARC-1–4 supplies one possible row-level construction when a row has a fixed supplied finite alphabet/support and a fixed conditional law. GAC-4 does not infer those premises and does not turn empirical absence of an outcome into a support theorem.

## 6. GAC-5 — typed correctness composition

Statistical validity is only one meaning of “valid pieces.” For semantic/system correctness, give component `i` an assume-guarantee contract

\[
A_i \Longrightarrow G_i
\]

on its declared input/output/history interface.

For an acyclic wiring, suppose:

1. every component is invoked inside its proved scope;
2. every local assumption `A_i` is implied by the external premises plus guarantees of predecessor components;
3. the wiring preserves types, timing and declared state/resource effects;
4. the conjunction of the local guarantees implies the global obligation `O`.

Then the composed system satisfies `O` by topological induction over the wiring graph.

For recurrent/cyclic systems, replace topological induction with a supplied invariant `I`: initialization establishes `I`; `I` plus the wiring establishes every step's local assumptions; the local guarantees preserve `I`; and `I` plus the terminal condition implies `O`. Induction over time then yields the global guarantee.

Probabilistic local guarantees do not combine by multiplying confidence levels. They require a joint proof, a valid error allocation such as GAC-4, or a globally conditionally valid evidence composition such as GAC-1.

Therefore the defensible composition statement is

\[
\boxed{
\text{valid pieces + discharged interfaces + valid evidence/cost composition}
\Rightarrow \text{valid whole}.
}
\]

“Valid pieces” alone is false.

## 7. Four exact failure modes

### C1. Private-history validity is insufficient

Let a hidden fair bit `Z` be visible to the scheduler but absent from each row's private history. Define

- `L_1 = 2` if `Z=1`, else `0`;
- `L_2 = 2` if `Z=0`, else `0`.

Each factor has unconditional expectation one. If the scheduler chooses row 1 when `Z=1` and row 2 when `Z=0`, the selected factor is always two. Local/unconditional validity did not survive adaptive selection. Under the global filtration containing `Z`, the selected factor visibly violates `E[L|F_0] <= 1`.

### C2. Retroactive reweighting is not self-financing

Let `E_1,E_2` independently equal `2` on heads and `0` on tails. Each has mean one. Choosing `max(E_1,E_2)` after seeing both gives expectation `2*(3/4)=3/2`. Predictable weights are essential.

### C3. Dynamic names cannot reset alpha

If each freshly named row runs an independent level-`alpha` failure event and receives a fresh full budget, familywise failure after `m` births is

\[
1-(1-\alpha)^m\to1.
\]

GAC-4 prevents this by requiring one globally summable budget.

### C4. Dependence does not imply static-row stationarity

A row whose Bernoulli success probability alternates between `1/4` and `3/4` as a function of global history has no single fixed conditional law `P_j`. A confidence sequence proved for one stationary `P_j` cannot be applied merely because the row name is unchanged.

## 8. Resource accounting

Every visit, observation, reset, state preparation, factor computation, confidence update, scheduler decision, row birth, memory allocation and inter-component message is charged according to the registered resource ledger. GAC-1 is a statistical self-financing theorem, not a statement that execution is physically free.

## 9. Falsifiers and boundaries

GAC-1–3 are mathematically falsified by a process satisfying every stated premise for which the threshold-crossing probability exceeds `alpha`. GAC-4 is falsified by a family satisfying its conditional row guarantees and pathwise budget constraint but exceeding familywise error `alpha`. GAC-5 is falsified by a typed composition satisfying all four interface premises while violating `O`.

The theorem does not establish:

- correctness of a physical sampler or freshness mechanism;
- learned support/state semantics;
- a static parameter under arbitrary drift;
- power or sample efficiency;
- finite expected stopping time;
- infinite-horizon control performance from a finite-horizon simulation bound;
- semantic correctness when local assumptions are mutually inconsistent;
- architecture optimality.

Those remain separate GMI obligations.
