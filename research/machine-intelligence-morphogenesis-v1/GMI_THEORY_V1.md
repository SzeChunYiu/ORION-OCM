# General Machine Intelligence Theory v1 (GMI-v1)

Status: **formal synthesis / working theory**, subordinate to #233 (HST), #377 and #373. It is not a claim that ORION invented every ingredient. Parent theorems are adopted where they already solve a layer.

## 0. Central thesis

A general theory of machine intelligence should not identify intelligence with one implementation family (neural, symbolic, Bayesian, programmatic or OCM). It should explain all of them as realizations of a common abstract developmental object and state what can and cannot be compared across realizations.

GMI-v1 proposes:

> **Machine intelligence is the capacity of a resource-bounded adaptive system to reach externally verified outcomes over an ecology of tasks, and to transform its own future cognition-generation process from experience. Different intelligence morphologies are different factorizations / inductive biases / update geometries realizing task-relative sufficient developmental states.**

The theory has four layers:

```text
future cognitive obligation
        ↓
minimal sufficient developmental state
        ↓
resource-bounded morphology / factorization
        ↓
execution + learning + morphogenesis over an ecology
        ↓
verified capability/resource developmental frontier
```

This is a synthesis object. Its value must come from coherence, deductions, predictive use and empirical validation, not from renaming parent concepts.

---

# 1. External cognitive obligation

All intelligence statements are relative to an explicit obligation

\[
\mathcal O=(\mathfrak E,\mathcal A,\mathcal Y,V,C,\rho,H),
\]

where:

- `E` is a registered family/distribution of task ecologies;
- `A` is the set of legal machine actions/computations;
- `Y` is the externally visible outcome space;
- `V` is the verifier/evidence semantics;
- `C` is the external constitutional boundary (authority, evaluator identity, protected information, adoption rules);
- `rho` maps machine/environment events to a raw resource vector;
- `H` is a registered horizon or stopping condition.

There is no representation-independent scalar intelligence without choosing at least an ecology/evaluation measure. This is consistent with Universal Intelligence/AIXI-style environment-relative performance and with No-Free-Lunch limits on unrestricted optimization.

The verifier is separate from the learner's internal training objective. A loss, reward, heuristic, posterior score or utility estimate is not automatically truth/admissibility.

---

# 2. Histories and developmental sufficient state

Let

\[
h_t=(o_0,a_0,e_0,r_0,\ldots,o_t)
\]

be the complete legal interaction/development history visible under the registered constitution, including observations, actions/computations, evidence/feedback and resource receipts as required by the obligation.

## 2.1 Future developmental equivalence

For obligation `O`, define

\[
h \sim_{\mathcal O} h'
\]

when, for every admissible future intervention/action programme `\alpha` in the registered class, the conditional law of every future protected quantity is identical (or equal within a declared approximation relation):

\[
\mathsf P(\text{verified future traces, future machine changes, resource receipts}\mid h,\alpha)
=
\mathsf P(\cdot\mid h',\alpha).
\]

The **developmental sufficient state** is the equivalence class

\[
z=[h]_{\sim_{\mathcal O}}.
\]

This is the strongest representation-independent candidate for the theory's primitive state distinction.

It is **not** a physical cognitive atom. It is task/future-obligation relative.

Parent instances include:

- Myhill-Nerode / Mealy-machine minimization in finite deterministic systems;
- predictive-state representations for controlled stochastic systems;
- computational-mechanics causal states / epsilon-machines for prediction;
- bisimulation / state-abstraction relations in MDPs.

## 2.2 Minimality

A state distinction is necessary at obligation `O` iff merging it with another class changes at least one admissible future verified outcome/development/resource distribution.

Thus the representation-invariant minimal object is:

```text
minimal sufficient developmental state for a declared future obligation
```

not:

```text
one universal smallest neuron/rule/operator.
```

Finite exact minimization is already calibrated in Track B. General stochastic/continuous approximations remain parent-heavy and technically open.

---

# 3. Machine-intelligence morphology

The abstract developmental state may admit many computational realizations.

Define a morphology

\[
M=(F,\Theta,K,U,\Gamma,\kappa,\rho_M),
\]

where:

- `F` — factorization / topology / program / graphical organization;
- `Theta` — mutable local parameters, rules, memory, beliefs or other configuration;
- `K` — execution/cognition kernel generating internal computations, proposals and external actions;
- `U` — within-morphology experience-driven update law;
- `Gamma` — optional structural/morphogenetic law that can change `F`, `K`, `U` or their allowed family;
- `kappa` — semantics/compiler map connecting the realization to the developmental-state/future-trace contract;
- `rho_M` — implementation resource semantics (description, compute, memory, communication, update, verification, maintenance, human input, etc.).

A morphology is valid at obligation `O` when `kappa` preserves the registered semantics within declared tolerance.

## 3.1 Morphology identity

Source syntax is not morphology identity.

Two realizations can be called equivalent only under a registered bounded developmental compiler relation that preserves:

```text
verified capability
future response to experience
retention/plasticity
revision/drift behavior
resource vector within declared bounds
verification semantics
```

Behavioral equivalence alone is insufficient; Track B has an exact counterexample where two machines have identical current behavior and diverge after the same teaching event.

---

# 4. Three time scales

GMI-v1 separates three processes.

## 4.1 Execution / cognition

For fixed morphology `M_t`, cognition/action is generated by

\[
(a_t,y_t,c_t,z'_{t})\sim K_{M_t}(\cdot\mid z_t,o_t,g_t).
\]

This includes forward inference, proof search, program search, retrieval, rule firing, planning, tool use, etc.

## 4.2 Within-form development

Experience changes the realization:

\[
M_{t+1}=U(M_t,e_t).
\]

Examples: SGD, Bayesian conditioning, rule induction/chunking, library learning, memory consolidation, OCM admission/revision.

## 4.3 Morphogenesis

The architecture/factorization/update law itself may change:

\[
M' \sim \Gamma(\cdot\mid M,E,R,H_{dev}).
\]

Examples: NAS, neuroevolution, program synthesis, modularity evolution, model-structure learning, architecture repair.

A fourth meta-level is possible when experience changes `Gamma` itself; that is meta-morphogenesis / strong RSI territory.

---

# 5. Verified developmental burden

For a task `tau`, capability threshold/contract `q`, history `h`, and morphology `M`, define the stopping time

\[
T_q=\inf\{t:\ V(\text{outcome}_t,\tau;C)\ge q\}.
\]

Define complete raw burden

\[
\mathbf B_M(\tau,q\mid h)
=\mathbb E\left[\sum_{t=0}^{T_q}\rho(t)\mid M,h,\tau\right].
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

No scalar is canonical. A scalar cost is allowed only after a prospective price/utility vector is declared.

---

# 6. Developmental feasible set and intelligence profile

For ecology `E`, define the reachable capability-resource set

\[
\mathcal A_M(E\mid h)
=\{(Q,\mathbf B): (Q,\mathbf B)\text{ reachable under legal development}\}.
\]

The **developmental frontier** is

\[
\mathcal F_M(E\mid h)=\operatorname{Pareto}(\mathcal A_M(E\mid h)).
\]

The most representation-neutral GMI object is the **intelligence profile**

\[
\mathcal I_M:\ E\mapsto\mathcal F_M(E\mid h).
\]

This is set-valued rather than one magic scalar.

It records both what the machine can eventually do and what it must spend to get there.

---

# 7. Generality

## 7.1 Partial-order generality

For registered ecology family `\mathfrak E`, define

\[
M_1\succeq_{\mathfrak E} M_2
\]

when `M1`'s frontier weakly dominates `M2`'s on every ecology in `\mathfrak E`, with strict improvement on at least one registered coordinate/ecology if strict dominance is claimed.

Because of No-Free-Lunch, speedup and resource-tradeoff limits, no unrestricted global total order is expected.

## 7.2 Distributional scalarization

If a task/ecology distribution `mu` and utility functional `u(Q,B)` are prospectively declared, define

\[
G_{\mu,u}(M)
=\mathbb E_{E\sim\mu}\left[\sup_{(Q,\mathbf B)\in\mathcal F_M(E)}u(Q,\mathbf B)\right].
\]

This turns the profile into a scalar for a declared question.

Universal-Intelligence/AIXI-style expected performance is a special limiting orientation of this construction when the ecology weighting and reward semantics are fixed and developmental/resource accounting is collapsed accordingly; GMI-v1 does not claim to replace UAI.

---

# 8. Capital hierarchy

Let `RESET` denote the matched system without the relevant developmental history, with the same external tools, evaluator, architecture family and protected information.

## K0 — solution capital

History stores a directly reusable answer/proof/program or object-specific solution.

Useful, but not evidence that future cognition-generation changed.

## K1 — cognition/search capital

History creates K1 on fresh task distribution `D` when:

1. protected target solutions are absent from history;
2. before target success, history changes the proposal/search/action distribution or representation/control;
3. this causally lowers future verified burden against matched reset/shuffle/library-only controls.

One measurable form is proposal-rank/surprisal change:

\[
\Delta I(\tau)
=\log_2\frac{\operatorname{rank}_{RESET}(m^*)}
{\operatorname{rank}_{H}(m^*)}.
\]

#323 currently supports K1/C2 at its authored grammar scope.

## K2 — developmental capital

History creates K2 only if it reduces the burden of **acquiring new K1** on fresh tasks/ecologies:

\[
\mathbb E[B^{acq}_{H}(K1_{new})]
<
\mathbb E[B^{acq}_{RESET}(K1_{new})]
\]

under a registered causal mechanism and complete cost accounting.

#323's retained-capital recombination C3 test ended `NOT_ESTABLISHED` at the current grammar (2/9 fresh seeds met the registered bar). Therefore ORION must not currently claim K2 from that lane.

## K3 — improvement/morphogenesis capital

History changes `Gamma`/`U` so that discovering or constructing future frontier-improving morphologies/learning procedures becomes cheaper or more reliable on fresh ecology families.

This is the natural bridge to governed RSI.

---

# 9. Adopted parent theorem modules

GMI-v1 intentionally imports parent theory rather than re-proving everything.

## P-UAI — general agent/performance layer

Universal Artificial Intelligence / Universal Intelligence establish broad formal environment-relative theories of intelligent action/performance and algorithmic environment weighting. GMI uses them as the strongest parent for claims about broad agent performance, not morphology emergence.

## P-STATE — minimal/predictive state layer

Automata minimization, predictive-state representations, computational mechanics and bisimulation/state abstraction provide parent mathematics for sufficient/minimal state and behavioral equivalence.

## P-INFO — information/resource layer

Information Bottleneck, rate-distortion and information-theoretic bounded rationality provide parent variational principles trading task-relevant information/performance against information-processing cost.

## P-FACT — factorization layer

Factored MDPs, DBNs, graphical models, software/program decompositions and modular systems provide compact representations of exponentially large global states and locality/communication tradeoffs.

## P-SEARCH — search/universal programme layer

Levin search, Solomonoff/Hutter universal induction, OOPS/PowerPlay and program synthesis own universal/incremental search-bias and reusable-program-search ideas.

## P-META — developmental transfer layer

Baxter, PAC-Bayes lifelong/meta-learning, MAML, learned optimizers and related theory own conditional learning-to-learn / learned inductive-bias results under explicit task-environment assumptions.

## P-MORPH — morphology emergence layer

AutoML/NAS/neuroevolution, modularly varying goals, facilitated variation, connection-cost modularity/hierarchy and quality-diversity/open-ended search own broad results in which task/resource structure produces architecture or evolvability.

## P-META-COMP — metareasoning layer

Algorithm selection, rational metareasoning, stochastic-shortest-path/control and drift analysis own much of cost-aware computational choice and hitting-time mathematics once the relevant state/potential is specified.

These modules are **part of the theory**. Parent ownership is not a defect.

---

# 10. Derived propositions / theory consequences

## GMI-T1 — no representation-independent implementation atom

Computation alone does not determine a unique unit boundary: units can often be split/refactored and finite networks flattened/merged. Therefore any irreducible implementation unit requires an explicit locality/physics/resource/equivalence contract.

Status: supported by Track-B finite flattening/granularity results + parent computability theory.

## GMI-T2 — task-relative minimal developmental state is well posed at finite deterministic scope

Quotient histories/configurations by equality of all registered future output/update traces. The resulting minimal Mealy/transducer representation is unique up to isomorphism.

Status: parent automata theorem; Track-B exact calibration present.

## GMI-T3 — factorization can matter exponentially without changing expressivity

A global minimal state may have exponentially many configurations while a factored realization has linear/shared local description and local update cost.

Status: parent factored-state principle; Track-B exact `3^n` calibration present.

## GMI-T4 — lifecycle morphology phase boundary

For fixed scalarized costs, if morphologies `i,j` have build costs `A_i,A_j` and expected per-use burdens `c_i(E),c_j(E)` over horizon `H`, then

\[
i\text{ beats }j
\iff
(A_i-A_j)+H(c_i(E)-c_j(E))<0.
\]

With vector resources use Pareto dominance instead.

Status: arithmetic / parent amortization & algorithm-selection principle; Track-B exact phase calibrations present.

## GMI-T5 — ecology-aligned factorization can reduce future development cost

When future tasks repeatedly reuse partially independent substructure, a morphology whose factorization aligns with those dependencies can reduce search/reconfiguration/update burden relative to an incompatible factorization, after build/coordination cost is charged.

Status: parent-owned in modularity/facilitated-variation/factored-model/library-learning families. Cross-paradigm quantitative law remains open.

## GMI-T6 — learned history need not help

Without relatedness/transfer assumptions, inherited state can impose acquisition, maintenance, interference and routing costs and may be harmful. No unconditional developmental-improvement theorem is permitted.

Status: immediate from cost accounting + NFL/harmful-transfer parents.

## GMI-T7 — exact universal burden predictor is impossible on unrestricted Turing-complete classes

A computable exact predictor of arbitrary target reachability / finite burden would solve halting/reachability in general. Useful predictive theory must restrict machine/ecology classes or provide probabilistic/empirical guarantees.

Status: P5 limit; formalized in Track B.

## GMI-T8 — generality is conditional, not one architecture

No morphology can be called universally superior without restricting ecology/resource semantics. The appropriate object is a profile/frontier or a declared distributional scalarization.

Status: NFL/resource theory.

---

# 11. Known machine-intelligence forms as specializations

The same GMI object accommodates multiple forms.

## Neural / differentiable

```text
F      layer/graph/module topology
Theta  weights, optimizer state, activations/memory
K      forward inference / sampling / planning through the model
U      SGD/Adam/meta-learned/plastic update
Gamma  NAS/neuroevolution/growth/pruning (optional)
rho    FLOPs, memory, data, communication, training/inference energy
```

## Symbolic / production

```text
F      predicates/rule graph/index/working-memory organization
Theta  rules, facts, agenda/preferences
K      match/fire/unify/search/operator selection
U      rule induction, chunking, revision, TMS update
Gamma  vocabulary/operator/representation restructuring
rho    matching/search/index/update/verification work
```

## Probabilistic / generative

```text
F      factor graph / graphical model / probabilistic program structure
Theta  priors/posteriors/latent state
K      inference/sampling/planning
U      conditioning/parameter learning/posterior update
Gamma  model-structure learning
rho    sampling/inference/normalization/data/verification work
```

## Programmatic / library-learning

```text
F      grammar/program/library/call graph
Theta  library, search priors, partial programs
K      enumeration/synthesis/execution
U      abstraction/library induction/search-prior update
Gamma  grammar/operator/library-structure growth
rho    proposal/execution/checking/storage/maintenance
```

## OCM-like explicit governed morphology

```text
F      warranted field + cognitive assets + dependency/provenance organization
Theta  facts/methods/applicability/control/self-model state
K      retrieval/search/composition/tool choice/controller
U      verified admission/revision/failure learning/consolidation
Gamma  representation/operator/control change under governance
rho    complete search/verification/acquisition/storage/revision ledger
```

No row is asserted to be fundamentally superior.

---

# 12. What makes a theory of machine intelligence 'general'?

GMI-v1 uses four requirements.

## G1 — realization breadth

The theory can represent the execution and development semantics of materially different morphology families without architecture-labelled escape hatches.

## G2 — invariant definitions

Capability, resource burden, sufficient developmental state, developmental frontier, K1/K2/K3 and generality use the same definitions across families.

## G3 — parent-consistent deductions

Known theorems/results from parent fields arise as special cases or imported modules rather than contradictions.

## G4 — predictive cross-paradigm content

At least one nontrivial quantitative prediction must transfer across materially different morphology families using pre-outcome information and beat the product of family-specific parent predictors.

G1-G3 can establish a coherent **framework/theory synthesis**. G4 is needed for a new scientific law.

---

# 13. Current evidence / non-evidence

Established at current Track-B / OCM scope:

```text
- no unique representation-independent cognitive atom established;
- task-relative developmental minimization is mathematically well posed at finite scope;
- factorized realizations can be exponentially more compact/local than flat state tables;
- ecology/resource-dependent morphology phase boundaries exist in exact toy systems;
- parent work directly demonstrates ecology/resource-driven modularity/hierarchy/evolvability;
- #323 shows real pre-solution history-induced proposal-rank improvement on 2741 fresh targets
  at one authored program-search grammar (C2/K1 evidence);
- #323 C3/K2 retained-capital acquisition claim is NOT_ESTABLISHED at that grammar.
```

Not established:

```text
- cross-paradigm predictive developmental law;
- universal useful morphology metric;
- unique basis;
- unknown machine-intelligence morphology;
- cross-domain K2 developmental capital;
- meta-morphogenesis / RSI improvement slope.
```

---

# 14. Scientific programme implied by the theory

The theory is established in layers rather than by one grand experiment.

### Layer A — mathematical coherence

- formalize developmental sufficient state/equivalence;
- prove finite exact properties;
- define approximate stochastic extension using parent bisimulation/predictive-state machinery;
- prove reduction/specialization maps to parent theories.

### Layer B — realization maps

For neural, symbolic, probabilistic, programmatic and OCM-like systems, provide explicit mappings into `(F,Theta,K,U,Gamma,kappa,rho)` and family-scale bounded compiler/resource analyses.

### Layer C — developmental measurement

Measure K1/K2/K3 with matched RESET/CONTINUED/history-shuffle/parent controls and complete resource ledgers.

### Layer D — cross-paradigm prediction

Freeze a compact pre-outcome structural/developmental signature and predict held-out burden/frontier in at least two materially different morphology families. Family-native predictors are strong parents.

### Layer E — real cognitive ecologies

Math (Lean) -> code/tools -> language-mediated mixed tasks -> science, using strongest donors and the same developmental definitions.

### Layer F — morphology discovery / RSI

Only after known-family phase prediction works: identify a parent-frontier hole, freeze its required properties, discover a candidate blindly, reduce it against all parents, and then ask whether the morphology-generator itself improves across fresh ecologies.

---

# 15. Current theory status

```text
GMI_V1_COHERENT_SYNTHESIS_PROPOSED
PARENT_THEOREMS_ADOPTED_AS_MODULES
REPRESENTATION_INDEPENDENT_ATOM_REJECTED_AS_REQUIRED_ASSUMPTION
TASK_RELATIVE_DEVELOPMENTAL_STATE_IS_CORE_ABSTRACT_OBJECT
MORPHOLOGY_IS_RESOURCE_BOUNDED_REALIZATION / FACTORIZATION
INTELLIGENCE_IS_VERIFIED_DEVELOPMENTAL_FRONTIER / PROFILE
GENERALITY_IS_ECOLOGY_FAMILY_RELATIVE
K1_K2_K3_DEVELOPMENTAL_CAPITAL_DEFINED
NEW_CROSS_PARADIGM_PREDICTIVE_LAW_NOT_YET_ESTABLISHED
```

This is intended as the first version that can be **used as a theory even if every individual mathematical component comes from parents**. The remaining research question is whether the synthesis yields new correct predictions and whether the same definitions survive real language/math/code/science systems.