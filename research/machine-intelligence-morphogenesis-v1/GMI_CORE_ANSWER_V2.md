# GMI Core Answer v2 — current strongest theory of forms of machine intelligence

Status: **CANONICAL TRACK-B SYNTHESIS AT CURRENT EVIDENCE SCOPE — EXPLICITLY NON-FINAL**

Refs: #233, #377, #373, #369.

This file answers the foundational questions that motivated Track B as far as the current formal and empirical evidence permits.

It is written to be replaced when stronger mathematics, parent theory, or real-domain evidence contradicts it.

---

# 1. Original question

The motivating intuition was:

> If there is a general theory of machine intelligence, perhaps there is a minimum irreducible cognitive unit from which different forms of intelligence develop. Neural networks would be one form humans discovered; symbolic, probabilistic and other forms would be others. A sufficiently general theory should explain how these forms arise and perhaps predict new ones.

The current theory supports **part** of this intuition and rejects another part.

---

# 2. What has been rejected

## 2.1 No representation-independent local cognitive atom is established

A local computational unit can often be:

```text
split into smaller transformations
or
merged with neighbors into a larger transformation
```

without changing the registered external cognition.

Therefore unit granularity is generally not invariant under representation/compiler choice.

Current OCM `u2` remains a useful **Cognitive Asset Contract**, not a proven fundamental atom.

Terminal:

```text
UNIQUE_LOCAL_FUNDAMENTAL_COGNITIVE_ATOM_NOT_ESTABLISHED.
```

## 2.2 Turing/universal computation is too weak

A basis being able to simulate arbitrary programs says almost nothing about:

```text
learnability
resource efficiency
development
bias
plasticity
verification
morphology emergence.
```

Terminal:

```text
UNIVERSAL_COMPUTATION_ONLY = non-answer to intelligence form.
```

## 2.3 Semantic obligation does not uniquely imply neural/symbolic/etc.

A canonical semantic state does not tell us whether its efficient realization should be:

```text
neural
symbolic
Bayesian
programmatic
memory-centered
hybrid.
```

Additional realization and update assumptions are required.

## 2.4 Task demand alone cannot choose the winning morphology

The same semantic obligation can prefer different realizations when:

```text
hardware changes
resource prices change
reuse horizon changes
drift/retraining costs change
candidate realization family changes
morphogenetic search budget changes.
```

So there is no valid universal map

```text
Xi(task) -> architecture label
```

without realization-response/resource/search information.

---

# 3. What replaces the unique-atom picture

The strongest current architecture-independent hierarchy is:

\[
\boxed{
\Omega
\rightarrow
S_\Omega
\rightarrow
\mathfrak M_\Omega
\rightarrow
(Q_M,U_M,\rho_M)
\rightarrow
\text{development}
\rightarrow
\Gamma
}
\]

where:

## `Omega` — registered cognitive obligation

Defines:

```text
task/ecology
legal development/interventions
external verification/admissibility
constitution/authority
horizon
resource semantics.
```

No intelligence statement is obligation-free.

## `S_Omega` — semantic developmental quotient

Developmental situations are equivalent exactly when no registered future legal continuation can distinguish them in protected semantic consequence.

At finite exact scope this quotient is canonical.

Every exact realization must preserve every quotient distinction.

This is the closest current object to a representation-independent **minimal cognitive state**, but it is:

```text
task-relative
semantic
future/development-sensitive
not a local atom.
```

Parent mathematics: Myhill-Nerode, minimal sufficient/predictive state, epsilon-machines, bisimulation/state abstraction.

## `M_Omega` — machine realization

A machine form realizes the semantic obligation as

\[
\mathfrak M_\Omega=(Z,\kappa,Q,U,\Gamma,\rho).
\]

- `Z`: implementation state;
- `kappa`: interpretation into semantic state;
- `Q`: cognition/action/proposal generation;
- `U`: within-form learning/development;
- `Gamma`: structural/morphology change;
- `rho`: raw resource semantics.

Verifier/constitution remain external.

---

# 4. What known forms of machine intelligence are

Known forms are different **realization families** of the common obligation/state/development object.

## Neural/differentiable

Additional assumptions:

```text
continuous/tensor parameter state
differentiable compositional transforms
loss/feedback bridge
gradient or learned update.
```

Then ordinary neural learning/backpropagation is a specialization.

## Symbolic/production

Additional assumptions:

```text
discrete typed state
guarded rules/rewrites
matching/agenda/search
rule/chunk/schema update.
```

## Bayesian/probabilistic

Additional assumptions:

```text
probabilistic belief/model state
likelihood/generative model
posterior/decision kernel
conditioning/inference update.
```

## Programmatic/library learning

Additional assumptions:

```text
program grammar
interpreter/search
program prior/order
library/grammar update.
```

## Memory/skill systems

Additional assumptions:

```text
persistent episode/skill store
retrieval/ranking
memory/skill insertion/consolidation
index/applicability update.
```

## OCM-like explicit governed systems

Additional assumptions:

```text
explicit persistent epistemic field/operators/control
scope/warrant/lifecycle semantics
governed admission/revision
external constitutional authority.
```

No one family is assumed fundamental.

---

# 5. Can the general framework “derive” neural networks?

Yes, in several different senses, and they must not be conflated.

## D0 — embedding

A neural learner fits the common GMI realization/update object.

Established at formal mapping scope.

## D1 — constructive derivation

Given differentiable parametric primitives and gradient update assumptions, a neural network/backprop learner is constructible.

Parent-owned mathematics.

## D2 — blind rediscovery

A lower-level morphology search can rediscover neural/backprop-like algorithms without the objective saying “build a neural network”.

AutoML-Zero and NEAT-class work already provide important parent examples.

Therefore this is not ORION novelty.

## D3 — prospective phase prediction

Before search, the theory predicts an ecology/resource regime in which neural-like realization properties should occupy the frontier; blind search recovers them there and another predicted morphology elsewhere.

**D3 remains open and is the meaningful Track-B target.**

---

# 6. The current candidate common principle: semantic proposal / bias geometry

Architecture labels are not sufficient statistics for developmental intelligence.

Two identical architectures with different learned state can have very different future cognition.

Different architectures can induce the same useful structural bias.

The current candidate cross-paradigm object is therefore:

\[
\boxed{
\mathcal G_M^\Omega=(S_\Omega,Q_M,U_M,\rho_M)
}
\]

where `Q_M` is interpreted at the **semantic candidate level**.

---

# 7. Semantic Proposal Geometry

Every morphology has a native candidate space:

```text
neural output/action proposals
Bayesian hypotheses/actions
symbolic rules/agenda items
program candidates
retrieved skills/cases
proof premises/tactics
code files/repair hypotheses
OCM fragments/operators.
```

Map native candidates to a common obligation-relative semantic candidate space:

\[
\psi_{M,\Omega}:\mathcal C_M\to\mathcal C_\Omega.
\]

Then compare either:

## probability mass / surprisal

\[
\bar Q_M(A)=Q_M(\psi^{-1}(A)),
\qquad
I_M(A)=-\log_2\bar Q_M(A),
\]

or, for deterministic/ranked search,

## first-hit burden

\[
T_A^M
=
\text{resources until first candidate mapping into target semantic set }A.
\]

This gives a common language for pre-solution cognition across architecture families without pretending their internal representations are equal.

---

# 8. Developmental intelligence in this language

## K0 — solution capital

History contains useful solved objects/results.

## K1 — cognition-generation/search capital

History changes semantic proposal geometry before a fresh target succeeds:

\[
T_{A,t+1}<T_{A,t}
\]

or

\[
I_{t+1}(A)<I_t(A)
\]

or registered stochastic dominance.

#323 provides real authored-program-search evidence at this rung.

The frozen coding K1 assay maps causal-fault localization into the same first-hit geometry.

## K2 — developmental capital

History reduces the burden to acquire useful new K1 geometry on fresh family identities.

Current #323 C3/K2 attempt is **not established** at its tested grammar/scope.

## K3 — improvement/morphogenesis capital

History reduces the burden to improve the process that acquires K2 or discovers useful realizations.

This is the bridge to governed RSI/meta-morphogenesis.

---

# 9. Exact finite cross-paradigm result now established

One finite concept-learning obligation was solved with four different realizations:

```text
EXEMPLAR_MEMORY
SYMBOLIC_THRESHOLD
BAYES_THRESHOLD_MIX
PARAMETRIC_PERCEPTRON.
```

Concept universe:

```text
32 Boolean concepts on five ordered inputs
6 monotone-threshold concepts
26 non-threshold concepts.
```

Let ecology parameter `p` be the probability that a target is sampled from the threshold subset.

Because the threshold subset fraction is

\[
\alpha=6/32=3/16,
\]

`p=3/16` makes the full ecology uniform over all 32 concepts.

Exact exhaustive result for all training sizes `m=1..4`:

```text
all four learners average exactly 1/2 at p=3/16.
```

For the three threshold-biased learners:

```text
threshold-concept performance > 1/2
non-threshold performance < 1/2.
```

Therefore their expected advantage changes sign exactly at

\[
p=3/16.
\]

The symbolic, Bayesian and perceptron realizations have different internal forms but share threshold-directed bias.

This is a finite NFL/inductive-bias parent result, not a universal GMI law.

---

# 10. General finite ecology-bias theorem

For finite target universe `F`, structured subset `T` of fraction

\[
\alpha=|T|/|F|,
\]

fixed learner scores `a_T` and `a_N` on the subset/complement, and full-universe baseline

\[
b=\alpha a_T+(1-\alpha)a_N,
\]

an ecology sampling `T` with probability `p` has expected score

\[
s(p)=p a_T+(1-p)a_N.
\]

Hence

\[
\boxed{
s(p)-b=(p-\alpha)(a_T-a_N).
}
\]

If `a_T>a_N`, the sign crosses at `p=alpha`.

No architecture label appears.

This is parent-owned algebra/NFL, but it is an exact finite prototype of the desired morphology/ecology phase law.

---

# 11. Why architecture still matters

The theory does **not** conclude that architecture is irrelevant.

A morphology constrains which semantic proposal/update/resource geometries are:

```text
representable
cheap to build
cheap to update
stable under drift
parallelizable
locally revisable
plastic
hardware-efficient
discoverable under bounded search.
```

So architecture should be understood as a **realization constraint on reachable bias-resource geometry**.

This is stronger than taxonomy and weaker than a claim of one universal architecture.

---

# 12. Normative frontier vs actual morphogenesis

Even if a realization is optimal in complete lifetime economics, a bounded developmental/evolutionary search may not find it.

Therefore keep two objects:

## Normative realization frontier

\[
\mathcal F_\Omega
=
Pareto\{B(M\mid\Omega):M\in\mathcal M_{avail}\}.
\]

## Bounded morphogenesis

\[
P(M_{found}\mid\Gamma,H,B_{discover},\Omega).
\]

This is a central correction to the original “evolve from the atom into the right architecture” picture.

Evolution/search is itself a computational process with bias and resource limits.

---

# 13. What is currently established

## Formal/synthesis

- GMI-v1 common machine/development definitions are coherent at F0-F3 scope.
- major known machine-intelligence families instantiate one realization normal form;
- exact finite semantic developmental quotient is canonical under registered assumptions;
- every exact finite realization refines that quotient;
- minimum exact semantic-state partition is unique up to isomorphism at the registered finite scope;
- semantic current-state information is not exponential merely because global state cardinality is exponential;
- normative realization quality is separate from bounded discoverability;
- demand alone cannot select morphology;
- known forms require conditional realization assumptions.

## Finite exact phase evidence

- resource-price/horizon/discovery-cost phase reversals;
- exact multi-form inductive-bias ecology crossover;
- exact bias-ecology algebraic phase theorem.

## Empirical developmental evidence

- real OCM/authored-program K1 search-geometry evidence exists at registered scope;
- real historical Lean verification receipts fit the common GMI episode but do **not** establish K1/K2;
- coding E3 K1 protocol is frozen but execution waits on a real #208 H0 episode;
- math E3 remains locked under #46;
- K2 developmental-capital evidence remains unestablished at the current tested grammar.

---

# 14. What remains open

## O1 — cross-paradigm predictive SPG

Does the same semantic proposal-geometry quantity prospectively predict developmental gain in materially different real families?

## O2 — resource-corrected morphology phase law

Can obligation-side demand + realization response predict frontier movement before outcomes across at least two morphology families?

## O3 — neural family validation

Can a controlled neural learner show the same pre-solution semantic proposal-geometry shift on fresh tasks under a frozen definition?

## O4 — real math/code validation

Can the same K1/K2 semantics survive Lean proof and execution-verified coding?

## O5 — endogenous blind recovery

Can a frozen phase prediction be made before architecture search, followed by label-free search that recovers the predicted known form?

## O6 — missing-form prediction

Only after known-form phase laws work: is there a registered demand/resource region not occupied by known parent morphologies?

## O7 — meta-morphogenesis / RSI

Can the process discovering/improving useful bias-resource geometries itself improve on fresh ecologies?

---

# 15. Current answer to “what is general machine intelligence?”

The current theory does **not** identify machine intelligence with one architecture.

The strongest working answer is:

> **A machine intelligence is a resource-bounded realization of the future-relevant semantic distinctions required by a cognitive obligation, together with a mechanism that generates candidate cognition, a law by which experience changes that generation process, and—where permitted—a process that changes the realization itself. Different machine-intelligence forms are different realizations of these semantic and developmental obligations. Their usefulness is conditional on how their induced cognition-generation bias aligns with the task ecology and on complete lifetime resource economics.**

This is a synthesis hypothesis with exact finite supporting theorems/calibrations and limited empirical developmental evidence.

It is **not yet** a new universally validated law of machine intelligence.

---

# 16. Current answer to “what is the fundamental cognitive unit?”

At present:

```text
UNIQUE LOCAL ATOM: not established and probably not representation invariant.
```

The strongest canonical object is instead:

```text
TASK-RELATIVE FUTURE-DISTINGUISHABLE SEMANTIC DEVELOPMENTAL STATE.
```

A useful local unit/factor is then a resource-efficient coordinate/module realizing transitions among these semantic states.

Whether there exists a stronger physically/causally irreducible basis common to all efficient machine intelligence remains open.

---

# 17. Current upward hypothesis

The strongest next scientific statement worth trying to establish is:

> **Across materially different machine-intelligence realizations, developmental advantage is prospectively predictable from the alignment between semantic proposal geometry and structured task ecology, together with complete realization/update/verification resources, more directly than from architecture labels alone.**

If this fails and family-native theories explain everything, terminal:

```text
FAMILY_NATIVE_BIAS_RESOURCE_THEORIES_SUFFICIENT.
```

GMI would remain a coherent synthesis/metrology theory rather than a new predictive law.

If it survives real neural/program/math/code families and disjoint replication, Track B moves from formal synthesis toward a genuinely general machine-intelligence principle.

---

# 18. Current terminal

```text
GMI_CORE_SYNTHESIS_V2_HARDENED
PROSPECTIVE_CROSS_PARADIGM_BIAS_RESOURCE_LAW_NOT_YET_ESTABLISHED
```
