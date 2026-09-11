# General Machine Intelligence Theory v1 (GMI-v1)

Status: **formal synthesis / working theory**, subordinate to #233 (HST), #377 and #373. It is not a claim that ORION invented every ingredient. Parent theorems are adopted where they already solve a layer.

## 0. Central thesis

A general theory of machine intelligence should not identify intelligence with one implementation family (neural, symbolic, Bayesian, programmatic or OCM). It should explain them as different realizations of a common abstract developmental object and state what can and cannot be compared across realizations.

GMI-v1 proposes:

> **Machine intelligence is the capacity of a resource-bounded adaptive system, from a declared developmental situation and under a declared development protocol, to reach externally admissible verified outcomes across a registered ecology family and to transform its own future cognition-generation process from experience. Different intelligence morphologies are different computational factorizations / inductive biases / update geometries realizing task-relative sufficient developmental states.**

The theory has four layers:

```text
future cognitive obligation + development protocol
        ↓
minimal sufficient developmental state
        ↓
resource-bounded morphology / factorization
        ↓
execution + learning + morphogenesis
        ↓
verified capability/resource developmental frontier
```

This is a synthesis object. Its value must come from coherence, deductions, predictive use and empirical validation, not from renaming parent concepts.

---

# 1. Cognitive obligation and development protocol

Every intelligence statement is relative to an explicit contract

\[
\mathcal O=(\mathfrak E,\mathcal A,\mathcal Y,V,C,\rho,H,D,J),
\]

where:

- `Eset` / `\mathfrak E` — registered family/distribution of task ecologies;
- `A` — legal machine actions/computations/tool calls;
- `Y` — externally visible outcome/evidence space;
- `V` — verifier/evidence semantics;
- `C` — external constitutional boundary: evaluator identity, protected information, authority/adoption rules;
- `rho` — raw resource-metering coordinates;
- `H` — registered horizon/stopping regime;
- `D` — **development protocol**: initialization, supplied pretrained state, permitted information, machine/external updates, tools/donors, resets/continuation, human input and charging;
- `J` — registered external intervention/probe/teaching class used when defining future distinguishability.

There is no representation-independent scalar intelligence without choosing at least an ecology/evaluation/resource/development contract.

## 1.1 Development protocol is part of the system being evaluated

`D` must explicitly declare at least:

```text
initial machine state / pretrained capital
permitted training/development streams
whether task answers/labels are available and when
which tools/donors are preinstalled vs acquired
which updates may be machine-proposed
which updates may be externally imposed
human intervention and its meter
morphology-change permissions
reset / continuation semantics
maintenance / revision obligations
```

A human engineer installing a solution is not free machine intelligence. A pretrained model can be evaluated as a deployed system, but its supplied capital must be declared; a claim about acquisition efficiency must charge or otherwise control that capital.

Different development protocols define different scientific comparisons and cannot be silently pooled.

## 1.2 External verification is separate from internal optimization

The verifier `V` and constitution `C` remain external to the machine's internal objective.

```text
low loss != truth
high reward != admissible evidence
high confidence != verification
```

This distinction allows the same GMI language to cover Lean kernel verification, execution/tests, empirical evidence and explicit `UNKNOWN/CANNOT_CHECK` terminals.

---

# 2. Developmental situations and sufficient state

A history alone may not determine the future of a learning machine: identical external histories can leave different optimizer, memory, random-state, posterior, replay-buffer or structural configurations.

Let

\[
h_t=(o_0,a_0,e_0,r_0,\ldots,o_t)
\]

be the registered interaction/development history and let `chi_t` denote the current machine configuration relevant to future protected behavior/development at theory level.

Define the **developmental situation**

\[
d_t=(\chi_t,h_t,\xi_t),
\]

where `xi_t` contains current registered public/experimental context that can affect protected futures.

Hidden environment variables unavailable to the machine are **not free machine information**. They are integrated over the registered ecology/environment law conditional on legal observations. If an ontic hidden state is used in a theorem, it must be distinguished from the machine information state and cannot be consumed by `K/U/Gamma` unless legally observed.

## 2.1 Future developmental equivalence

For fixed `O,D,J`, define

\[
d \sim_{\mathcal O,D,J} d'
\]

when for every admissible future intervention/probe programme `j\in J` and every legal continuation policy/process under `D`, the conditional law of every registered future protected quantity is the same (or equal under a declared approximation relation):

\[
\mathsf P(
  \text{verified future traces, machine changes, resource receipts}
  \mid d,j,D
)
=
\mathsf P(\cdot\mid d',j,D).
\]

The **developmental sufficient state** is

\[
z=[d]_{\sim_{\mathcal O,D,J}}.
\]

This is the theory's strongest representation-independent primitive **state distinction**.

It is not a physical cognitive atom and not necessarily computable.

Parent instances include:

- Myhill-Nerode / Mealy-machine minimization;
- predictive-state representations;
- computational-mechanics causal states / epsilon-machines;
- bisimulation / state abstraction.

## 2.2 Minimality

A state distinction is necessary iff merging it changes at least one future protected distribution under the registered future intervention/development semantics.

Therefore the meaningful minimal object is:

```text
minimal sufficient developmental state relative to (O,D,J)
```

not a universal smallest neuron/rule/operator.

Approximate/stochastic versions require parent predictive-state/bisimulation/statistical machinery and explicit tolerances.

---

# 3. Machine-intelligence morphology

The abstract developmental process can have many computational realizations.

Define a morphology

\[
M=(F,\Theta,K,U,\Gamma,\kappa,\rho_M),
\]

where:

- `F` — factorization/topology/program/graph organization;
- `Theta` — mutable parameters, rules, memories, beliefs/configuration;
- `K` — execution/cognition/proposal/action kernel;
- `U` — within-morphology experience-driven update law;
- `Gamma` — structural/morphogenetic law changing `F`, `K`, `U` or their family;
- `kappa` — semantics/compiler map into the registered developmental-state/obligation semantics;
- `rho_M` — implementation resource semantics.

A morphology is valid at scope when `kappa` preserves the registered protected semantics within declared tolerance.

## 3.1 Morphology identity

Source syntax is not morphology identity.

Two realizations can be called developmentally equivalent only under a registered bounded compiler relation preserving, within tolerance:

```text
verified capability
future response to experience
retention/plasticity
revision/drift behavior
resource vectors
verification semantics
```

Behavioral equivalence alone is insufficient; Track B contains an exact witness where two machines have identical current behavior and diverge after the same teaching event.

---

# 4. Three timescales

## 4.1 Execution / cognition

For fixed morphology:

\[
(a_t,y_t,c_t,z'_{t})\sim K_{M_t}(\cdot\mid z_t,o_t,g_t).
\]

This covers inference, proof/program search, retrieval, rule firing, planning and tool use.

## 4.2 Within-form development

\[
M_{t+1}=U(M_t,e_t).
\]

Examples include SGD/Adam, Bayesian conditioning, rule induction, chunking, library learning, memory consolidation and OCM admission/revision.

## 4.3 Morphogenesis

\[
M'\sim\Gamma(\cdot\mid M,E,R,H_{dev}).
\]

Examples include NAS, neuroevolution, program synthesis, model-structure learning, growth/pruning and architecture repair.

When experience changes `Gamma` itself, the process enters meta-morphogenesis / K3 / strong-RSI territory.

---

# 5. External admissibility and verified developmental burden

A universal scalar verifier threshold is not assumed.

For task `tau`, let the external constitution define an admissibility contract

\[
A_\tau(y,e;V,C)\in\{0,1\}
\]

or a declared partially ordered evidence/capability contract whose admissible region is fixed before protected outcome access.

Define first-admissible stopping time

\[
T_A=\inf\{t:A_\tau(y_t,e_t;V,C)=1\}.
\]

For morphology `M`, developmental situation `d`, and development protocol `D`, define complete raw burden

\[
\mathbf B_M(\tau\mid d,D)
=\mathbb E\left[
\sum_{t=0}^{T_A}\rho(t)
\mid M,d,D,\tau
\right].
\]

Coordinates may include:

```text
information supplied / labels / demonstrations
candidate generation/search
execution/inference
verification/checker calls
failed/rejected attempts
learning/update work
memory/storage
communication
maintenance/revision
human intervention
CPU/GPU/wall/energy/IO
```

No scalar is canonical. Scalar cost requires a prospectively frozen price/utility mapping.

---

# 6. Developmental feasible set, frontier and intelligence profile

For ecology `E`, morphology `M`, current developmental situation `d` and protocol `D`, define the **semantic feasible set**

\[
\mathcal A_M(E\mid d,D)
=\{(Q,\mathbf B): (Q,\mathbf B)\text{ reachable under }M,D,E\}.
\]

Its Pareto developmental frontier is

\[
\mathcal F_M(E\mid d,D)
=\operatorname{Pareto}(\mathcal A_M(E\mid d,D)).
\]

The **intelligence profile** is

\[
\mathcal I_{M,d,D}:E\mapsto\mathcal F_M(E\mid d,D).
\]

It is set-valued rather than one magic scalar.

## 6.1 Semantic vs certified frontier

For rich systems the semantic frontier may be uncomputable.

Therefore distinguish:

```text
semantic frontier        theory-level reachable Pareto set
certified inner frontier externally verified/proved/observed points
outer/inner bounds        theorem/statistical bounds where available
```

Experiments establish certified points or bounded regions, not universal enumeration of all reachable intelligence.

## 6.2 Starting capital matters

The primary object is a deployed system `(M,d,D)`, not architecture `M` in isolation.

Claims about a morphology family must either:

- match initialization/development protocols;
- charge acquisition of starting capital; or
- explicitly state that the comparison is between deployed systems rather than innate architecture-only intelligence.

---

# 7. Generality

## 7.1 Partial-order generality

For a registered ecology family `\mathfrak E`, define

\[
(M_1,d_1,D_1)\succeq_{\mathfrak E}(M_2,d_2,D_2)
\]

when the first certified/semantic frontier (as explicitly stated) weakly dominates the second on every ecology in `\mathfrak E`, with strict improvement somewhere if strict dominance is claimed.

This is naturally a partial order. Tradeoffs across ecologies are not hidden.

## 7.2 Distributional scalarization

If an ecology distribution `mu` and utility functional `u(Q,B)` are prospectively declared,

\[
G_{\mu,u}(M,d,D)
=\mathbb E_{E\sim\mu}
\left[
\sup_{(Q,\mathbf B)\in\mathcal F_M(E\mid d,D)}u(Q,\mathbf B)
\right].
\]

Different `mu`, `u`, starting states or development protocols can reverse rankings.

Universal-Intelligence/AIXI-style expected performance is a powerful parent orientation when its environment/reward/complexity measure is adopted; GMI-v1 does not claim to replace it.

---

# 8. Developmental capital hierarchy

Let `RESET` denote a matched counterfactual that lacks the relevant inherited developmental state while retaining the same declared external tools/evaluator/protocol information.

## K0 — solution capital

A directly reusable answer/proof/program/object-specific solution is retained.

K0 is useful but does not establish changed future cognition-generation.

## K1 — cognition/search capital

Inherited developmental state creates K1 on fresh targets when:

1. protected target solution is absent from the relevant history;
2. before target success, inherited state changes proposal/search/action distribution or representation/control;
3. that change causally lowers future verified burden against matched reset/history controls.

A measurable mediator is

\[
\Delta I(\tau)=
\log_2\frac{rank_{RESET}(m^*)}{rank_H(m^*)}.
\]

#323 currently supports K1/C2 at its authored grammar scope.

## K2 — developmental capital

Inherited state creates K2 only if it reduces burden of acquiring **new K1**:

\[
\mathbb E[B^{acq}_{H}(K1_{new})]
<
\mathbb E[B^{acq}_{RESET}(K1_{new})].
\]

#323's retained-capital C3 test ended `NOT_ESTABLISHED` at the current grammar (2/9 fresh seeds met the registered bar).

## K3 — improvement / morphogenesis capital

Inherited state changes `Gamma/U` such that discovering or constructing future verified frontier improvements becomes cheaper or more reliable on fresh ecology families under fixed external governance.

This is the natural bridge to governed RSI.

Capital labels require causal counterfactual evidence; they are not assigned by inspection.

---

# 9. Adopted parent theorem modules

Parent ownership is foundational, not a defect.

## P-UAI — general agent/performance

Universal Artificial Intelligence / Universal Intelligence provide broad environment-relative theories/measures of intelligent action/performance and algorithmic environment weighting.

## P-STATE — minimal/predictive state

Automata minimization, predictive-state representations, computational mechanics and bisimulation/state abstraction provide mathematics for future-sufficient/minimal state.

## P-INFO — representation/resource tradeoff

Information Bottleneck, rate-distortion and information-theoretic bounded rationality provide variational compression/performance/information-cost principles.

## P-FACT — structured factorization

Factored MDPs, DBNs, graphical models and structured programs provide compact factorizations of huge global states.

## P-SEARCH — universal/incremental search

Levin/Solomonoff/Hutter, OOPS/PowerPlay and program synthesis provide universal/incremental search and reusable bias machinery.

## P-META — learning-to-learn

Baxter, PAC-Bayes lifelong/meta-learning, MAML, learned optimizers and related theory provide conditional future-task transfer under explicit relatedness assumptions.

## P-MORPH — morphology generation

AutoML/NAS/neuroevolution, modularly varying goals, facilitated variation, connection-cost modularity/hierarchy and QD/open-ended search provide broad morphology/evolvability mechanisms.

## P-META-COMP — computational resource allocation

Algorithm selection, rational metareasoning, stochastic-shortest-path/control and drift analysis provide cost-aware computational choice and hitting-time theory.

These are components of GMI-v1.

---

# 10. Core consequences

## GMI-T1 — no representation-independent implementation atom

Computation alone does not determine a unique unit boundary: units can be split/refactored and finite networks can be flattened/merged. Any irreducible implementation unit therefore requires extra locality/physics/resource/causal assumptions.

## GMI-T2 — task-relative minimal developmental state is well posed at finite deterministic scope

Quotient complete developmental situations by equality of all registered future traces under the allowed event/intervention semantics; the minimal deterministic representation is unique up to isomorphism.

## GMI-T3 — factorization can matter exponentially without changing expressivity

A global sufficient state can grow exponentially while a factored realization remains compact/local. Track B's exact construction yields `3^n` minimal global states with `n` local cells and one shared local rule.

## GMI-T4 — lifecycle morphology phase boundary

For fixed scalarized build/per-use costs:

\[
C_i=A_i+Hc_i(E),
\]

and morphology `i` beats `j` exactly when

\[
(A_i-A_j)+H[c_i(E)-c_j(E)]<0.
\]

## GMI-T5 — ecology-aligned factorization can lower future developmental burden

Repeated partially independent substructure can favor a matching reusable factorization after build/coordination costs. This is already strongly parent-owned by modularity/factored-model/library-learning theory.

## GMI-T6 — inherited history need not help

Without relatedness/transfer assumptions, inherited state can impose maintenance/interference/routing costs and hurt future performance.

## GMI-T7 — no universal exact burden predictor for unrestricted Turing-complete systems

An exact computable predictor of arbitrary finite reachability/burden would decide halting/reachability in general. Predictive theorems must restrict the class or become probabilistic/empirical.

## GMI-T8 — generality is conditional

No morphology is expected to be universally superior across unrestricted ecologies/resources. The natural object is a profile/frontier or explicitly declared scalar measure.

---

# 11. Known forms are specializations

The same morphology tuple accommodates:

### Neural / differentiable

```text
F      layer/module topology
Theta  weights, optimizer/recurrent state
K      forward inference / model-based cognition
U      SGD/Adam/plastic/meta-learned update
Gamma  NAS/evolution/growth/pruning
```

### Symbolic / production

```text
F      predicates/rule/index/workspace organization
Theta  rules/facts/preferences
K      match/fire/unify/search
U      rule induction/chunking/revision
Gamma  vocabulary/operator/representation restructuring
```

### Probabilistic / generative

```text
F      factor graph / graphical model / probabilistic program
Theta  posterior/latent/model parameters
K      inference/sampling/planning
U      conditioning/parameter learning
Gamma  model-structure learning
```

### Programmatic / library-learning

```text
F      grammar/program/library graph
Theta  library/search priors/partial programs
K      enumeration/synthesis/execution
U      abstraction/library/search-prior update
Gamma  grammar/operator growth
```

### OCM-like governed explicit

```text
F      warranted field + cognitive assets + provenance/dependencies
Theta  facts/methods/applicability/control/self-model state
K      retrieval/search/composition/tool/executive control
U      verified admission/revision/failure learning/consolidation
Gamma  governed representation/operator/control change
```

No specialization is assumed fundamental.

---

# 12. What makes GMI general?

GMI-v1 has four tests.

## G1 — realization breadth

Materially different machine-intelligence families fit the same core definitions without architecture-specific semantic escape hatches.

## G2 — invariant definitions

Admissibility, resource burden, developmental state, frontiers, K0-K3 and generality keep the same meanings across forms.

## G3 — parent consistency

Established parent theorems appear as special cases/modules rather than contradictions.

## G4 — predictive cross-paradigm content

At least one quantitative pre-outcome prediction transfers across materially different forms and beats the product of family-native parent predictors.

G1-G3 can establish a coherent synthesis theory. G4 is required for a new general scientific law.

---

# 13. Current evidence

Supported now:

```text
no unique representation-independent implementation atom established
task-relative finite developmental minimization is well posed
factorized realizations can be exponentially more compact/local than flat state tables
ecology/resource morphology phases exist in exact systems and parent literature
#323 provides C2/K1 pre-solution search-geometry evidence at one authored grammar
```

Negative/locked:

```text
#323 K2/C3 retained-capital acquisition NOT_ESTABLISHED at current grammar
no cross-paradigm predictive developmental law yet
no unique basis
no theory-predicted unknown morphology
no meta-morphogenesis / RSI improvement slope
```

---

# 14. Scientific programme

### Layer A — mathematical coherence

- finish obligation/situation/equivalence semantics;
- import exact parent assumption maps;
- prove finite exact consequences;
- define stochastic/approximate extensions using parent machinery.

### Layer B — realization maps

Complete family-scale neural, symbolic, probabilistic, programmatic and OCM mappings into the same tuple and resource contracts.

### Layer C — developmental measurement

Measure K1/K2/K3 using matched causal controls and complete ledgers.

### Layer D — cross-paradigm prediction

Freeze a compact pre-outcome structural/developmental signature and predict held-out burden/frontier in at least two materially different forms against family-native parent predictors.

### Layer E — real cognitive ecologies

Math (Lean) -> code/tools -> language-mediated mixed tasks -> science, with the same GMI definitions and strongest donor systems.

### Layer F — morphology discovery / RSI

Only after known-family prediction works: predict a parent-frontier hole, freeze required properties, search blindly, reduce candidate against parents, then ask whether `Gamma` itself develops.

---

# 15. Current theory status

```text
GMI_V1_COHERENT_SYNTHESIS_UNDER_ACTIVE_HOSTILE_REVIEW
PARENT_THEOREMS_ARE_FOUNDATIONAL_MODULES
REPRESENTATION_INDEPENDENT_ATOM_NOT_REQUIRED
TASK_RELATIVE_DEVELOPMENTAL_SUFFICIENT_STATE_IS_CORE_ABSTRACT_OBJECT
MORPHOLOGY_IS_RESOURCE_BOUNDED_REALIZATION / FACTORIZATION
INTELLIGENCE_IS_VERIFIED_DEVELOPMENTAL_FRONTIER / PROFILE
GENERALITY_IS_ECOLOGY_AND_PROTOCOL_RELATIVE
K0_K1_K2_K3_DEVELOPMENTAL_CAPITAL_DEFINED
NEW_CROSS_PARADIGM_PREDICTIVE_LAW_NOT_YET_ESTABLISHED
```

GMI-v1 is intended to be usable even if most individual mathematics comes from parent fields. The theory becomes scientifically stronger as it survives reductions, exact hostiles and real math/code/language/science validation.