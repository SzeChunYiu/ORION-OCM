# GMI Machine-Intelligence Biosphere v1

Status: **OPEN-WORLD MORPHOLOGY SEARCH / SPECIES FORMALISM / PROSPECTIVE EXPERIMENTAL SYSTEM**

Status date: 2026-09-12.

Refs:

- `GMI_CROSS_PARADIGM_REALIZATION_NORMAL_FORM_V1.md`
- `GMI_CAUSAL_MECHANISM_PHASE_THEORY_V1.md`
- `GMI_PREDICTED_MACHINE_INTELLIGENCE_FORMS_V1.md`
- `GMI_ML_THEORY_EXPERIMENT_MATRIX_V1.md`
- `GMI_EXPLANATORY_COMPLETENESS_CRITERION_V1.md`
- `GMI_PREDICTIVE_SUFFICIENCY_NO_GO_V1.md`

Purpose:

> Turn GMI from a theory that predicts a handful of named candidate forms into an open-ended experimental biosphere capable of discovering, classifying, challenging and benchmarking very large numbers of machine-intelligence realization species against neural and non-neural parents.

The biosphere is not biological metaphor used as evidence. It is a formal search/evaluation architecture over realization morphologies and ecologies.

---

# 1. Why “millions of forms” is plausible but must be defined carefully

Suppose there are only 20 independent binary mechanism choices. The raw mechanism-vector count is already

\[
2^{20}=1,048,576.
\]

Real GMI morphology space has non-binary choices for:

```text
state representation
factorization
routing
memory
update law
verification
authority
lineage
compilation
inference search
intervention
heterogeneity
morphogenesis
precision
substrate placement
communication
serving policy
```

so the syntactic search space is vastly larger.

But:

```text
raw configuration != intelligence species.
```

Many configurations are:

- semantically equivalent;
- implementation-equivalent;
- behaviorally indistinguishable at registered scope;
- dominated everywhere;
- unreachable under bounded development;
- reducible to a known parent with a cheap compiler.

Therefore the biosphere requires a formal species relation.

---

# 2. Ecology

A registered machine-intelligence ecology is

\[
e=(\mathcal O,\Xi_{obl},P,\mathcal J,H_{dev},\mathcal C_{eval}),
\]

where:

```text
O          semantic/cognitive obligation
Xi_obl     pre-outcome obligation demand measurements
P          substrate, resource prices and budgets
J          legal intervention/feedback/teaching channels
H_dev      developmental history protocol
C_eval     protected evaluation constitution
```

An ecology may change over developmental time:

\[
e_{0:T}.
\]

This permits drift, shocks, new tasks, hardware repricing, verifier changes and lineage obligations without confusing them with machine-internal state.

---

# 3. Machine genotype and phenotype

## 3.1 Generic genotype

Use a grammar-generated realization descriptor

\[
g=(F,S,K,U,\Gamma,H,V,C,D,P_m),
\]

with generic primitive families:

```text
F    factorization/topology/interface graph
S    mutable state and representation primitives
K    execution/computation/routing primitives
U    within-form update/credit rules
Gamma morphology-changing rules
H    memory/history/persistence primitives
V    verification/admission/abstention primitives
C    compiler/materialization/interface primitives
D    inference/decision/search primitives
P_m  physical placement/precision/parallelism choices
```

The grammar MUST NOT contain macros named after target architectures in neutral discovery runs.

Forbidden discovery macros include, for example:

```text
TRANSFORMER
RAG
MIXTURE_OF_EXPERTS
VRQM
VGSC
CNN
LSTM
```

Those systems must themselves be expressible as compositions of lower-level primitives.

## 3.2 Developmental phenotype

For ecology `e`, the phenotype is not merely the final graph. Define

\[
\Phi_e(M)=
(\mathcal T_{sem},
 a_{1:K},
 R_M,
 \rho_M,
 \mathcal D_M,
 \mathcal G_M),
\]

where:

```text
T_sem   protected semantic behavior traces
 a      architecture-neutral mechanism witnesses
 R_M    response surface to registered interventions
 rho_M  lifecycle burden/resource vector
 D_M    developmental trajectory summary
 G_M    morphology-change trajectory summary
```

Two machines with different code but the same registered phenotype need not be separate species.

---

# 4. Species equivalence

Fix:

```text
E       registered ecology family
J*      registered intervention family
epsilon semantic/response tolerance
c       bounded compiler/reduction budget
```

Define

\[
M_1\equiv_{E,J^*,\epsilon,c}M_2
\]

when there exist allowed representation/interface remints and bounded compilers of description/search cost at most `c` such that, for every registered ecology/intervention pair:

1. protected semantic traces agree within `epsilon`;
2. mechanism witness vectors agree within registered witness tolerance;
3. developmental response surfaces agree within tolerance;
4. no hidden external state or resource channel is introduced;
5. lifecycle burden vectors transform only by explicitly charged compiler/implementation differences.

A **GMI species** is an equivalence class

\[
[M]_{E,J^*,\epsilon,c}.
\]

This relation is scope-dependent by design. Finer ecologies or interventions may split a previously merged species.

---

# 5. Parent-reduction distance and novelty

Let `P_known` be the registered parent library.

Define a bounded parent-reduction burden

\[
d_{parent}(M)
=
\inf_{P\in\mathcal P_{known}}
\operatorname{Cost}(P\Rightarrow M),
\]

where cost includes:

```text
compiler description
search/tuning
added state
added calls/tools
training/development
serving overhead
verification
communication
approximation loss
```

This is not a universal Kolmogorov complexity claim. It is a registered bounded reduction protocol.

Novelty levels:

```text
N0  syntactically different only
N1  behaviorally distinct under registered interventions
N2  frontier-distinct in at least one protected ecology
N3  survives bounded parent reduction
N4  recurs across independent search encodings/substrates/remints
N5  transfers to real protected regimes
```

Only N3+ is scientifically interesting as a candidate new form; N4/N5 are stronger.

---

# 6. Niche and ecological breadth

For tolerance `epsilon`, define the near-frontier set in ecology `e`:

\[
\mathcal F_\epsilon(e).
\]

The niche of species `s` is

\[
\mathcal N(s)=\{e:s\cap\mathcal F_\epsilon(e)\ne\varnothing\}.
\]

For ecology distribution `mu_E`, define breadth

\[
B_{eco}(s)=\mu_E(\mathcal N(s)).
\]

A species can be:

```text
specialist: narrow high-value niche
generalist: broad non-dominated niche
plastic: morphology changes enlarge niche over life
opportunist: depends on transient price/regime conditions
obligate composite: viable only with another factor/system
```

No single scalar “IQ” is assumed.

---

# 7. Biosphere state

At generation/development time `t`, maintain

\[
\mathfrak B_t=(\mathcal P_t,\mathcal A_t,\mathcal E_t,\mathcal F_t),
\]

where:

```text
P_t  active machine population
A_t  species/novelty archive
E_t  active ecology population
F_t  fossil archive of extinct/dominated but informative forms
```

The fossil archive is scientifically important: a morphology may become useful again after resource or obligation repricing.

---

# 8. Generic primitive library

The initial neutral grammar should contain primitives such as:

## State primitives

```text
dense continuous vector
sparse vector
finite symbol/table
key-value store
set/multiset
sequence/buffer
stack/queue
graph
probability distribution/posterior
program/tree/term
logical clause/proof state
external-address reference
versioned/persistent state
```

## Routing/composition primitives

```text
fixed edge
dynamic score-and-select
nearest-neighbor retrieval
key lookup
content hash
learned router
rule-based router
broadcast
reduce/aggregate
message passing
call/return
```

## Computation primitives

```text
linear map
nonlinear scalar map
gated product
convolution/local stencil
matrix product
kernel evaluation
symbolic rewrite
program execution
probabilistic update
search expansion
planning backup
constraint solve
```

## Update primitives

```text
gradient/reverse-mode update
local Hebbian-like update
Bayesian update
least-squares/closed form
memory insertion/deletion
rule induction
program mutation
black-box optimization
population/evolutionary update
no persistent update
```

## Verification primitives

```text
none
unit-test / predicate check
formal proof checker
constraint checker
cross-model judge
statistical test
human/evaluator channel
simulator/experiment
rollback on failure
abstain
```

## Morphogenesis primitives

```text
add/remove factor
split/merge factor
add/remove edge
change router
change state family
change update law
change precision
compile/materialize cache
introduce/remove verifier gate
introduce/remove lineage
clone/specialize factor
share/unshare parameters
migrate factor across substrate
```

This grammar already supports enormous combinatorial diversity without naming target architectures.

---

# 9. Birth, development, reproduction and death

These terms are operational labels.

## Birth

Instantiate a grammar-valid machine with an initial state and developmental budget.

## Development

Expose it to legal data/interventions and apply `U` and `Gamma` under charged budgets.

## Reproduction

Generate descendant morphology by one or more of:

```text
mutation
recombination
program synthesis
surrogate-guided proposal
gradient architecture update
population-based transfer
module transplantation
compiler-derived child
```

No biological reproduction claim is implied.

## Death

Retire an active candidate when it is:

```text
dominated beyond tolerance
resource-infeasible
semantically inadmissible
search-budget exhausted
redundant with archived species
```

Its phenotype/lineage remains in the fossil archive.

---

# 10. Selection must be multiobjective

Do not use one fixed scalar fitness as the scientific endpoint.

Registered burden vector may include:

\[
B=(
L_{sem},
B_{train},
B_{data},
B_{search},
B_{serve},
B_{latency},
B_{mem},
B_{comm},
B_{update},
B_{verify},
B_{human},
B_{energy},
B_{risk}).
\]

Maintain Pareto archives and, where scalar selection is operationally needed, randomize/freeze scalarization weights from a declared distribution and report full vectors afterward.

This prevents benchmark success from depending on one arbitrary utility weighting.

---

# 11. Diversity preservation

A biosphere that converges to one family is not testing open morphology space.

Use multiple diversity mechanisms:

```text
behavioral novelty archive
mechanism-vector diversity
niche occupancy archive
quality-diversity / MAP-Elites-like cells
random protected ecology islands
lineage diversity
novelty pressure independent of immediate scalar reward
```

But novelty itself is not success. Every novel form must still satisfy semantic/resource criteria.

---

# 12. Ecology generation

The ecology generator varies obligation and context axes independently where possible.

Core axes include:

```text
semantic complexity sigma
query dependency geometry Delta_Q
update dependency geometry Delta_U
feedback channel gamma_F
revision/drift nu
verifier contract chi_V
reuse horizon rho_use
retention contract lambda_R
lineage/coexistence beta_lin
hardware/compute price
memory price
communication price
verification price
latency price
intervention availability
false-adoption loss
noise / stochasticity
multi-agent coupling
```

Additional task families:

```text
classification/regression
generative sequence prediction
algorithmic/compositional reasoning
formal proof
code synthesis/repair
causal intervention
planning/control
continual learning
retrieval/provenance
scientific hypothesis-test loops
multimodal binding
multi-agent coordination
historical/as-of queries
real-time serving/update
```

Ecology generation itself has D/V/P separation.

---

# 13. D/V/P firewall for open-ended search

Use three disjoint ecology streams:

```text
D  adaptive development/co-evolution ecologies
V  limited model-selection / stopping ecologies
P  protected ecologies created or cryptographically frozen after search grammar,
   metrics, parent library and admission tests are frozen
```

If the search process receives a protected failure and adapts to it, that ecology is no longer protected.

Open-endedness is not permission to reuse the test set forever.

---

# 14. Search processes

Run several independent search encodings:

```text
S1 evolutionary mutation/recombination
S2 quality-diversity / MAP-Elites-style archive
S3 population-based training / hyperparameter-morphology schedules
S4 grammar/program synthesis search
S5 Bayesian/surrogate multiobjective search
S6 differentiable architecture/morphology relaxation where legal
S7 novelty search
S8 POET-like paired ecology-machine co-generation
```

A predicted form that appears only under one encoding is weaker evidence than one recovered across several.

Search prior and grammar description length are charged.

---

# 15. Known-form calibration zoo

Before unknown-form claims, the grammar/search system must be able to recover strong representatives of known families from primitives.

Calibration families include:

```text
linear/logistic models
kernel/SVM-like systems
nearest-neighbor/memory systems
decision trees/rule systems
Bayesian/probabilistic models
MLP/deep feed-forward networks
CNN/local shared networks
RNN/LSTM-like recurrent state
state-space sequence models
Transformer-like dynamic-routing stacks
mixture-of-experts
GNN/message-passing systems
RAG/external-memory systems
neuro-symbolic compositions
program synthesis / search + verifier
planning/search agents
reinforcement-learning policies/world-model agents
VLC-like lifecycle systems
```

Failure to rediscover known strong forms indicates grammar/search inadequacy, not evidence those forms are unnecessary.

---

# 16. Predicted-form target zone

The currently frozen GMI candidates F1-F6 are **protected target property vectors**, not search macros:

```text
F1 RQM
F2 VRQM
F3 VGSC
F4 IQL
F5 LMHM
F6 SCDI
```

The biosphere test asks:

> do generic primitives independently converge toward these mechanism complexes in their predicted ecologies more often than in negative twins?

If not, the theory is narrowed/falsified.

---

# 17. Open-world discovery zone

After calibration and frozen predicted-form tests, remove named target scoring.

Search objective becomes:

```text
semantic admissibility
Pareto quality
niche occupancy
behavioral/mechanism diversity
transferability
bounded novelty
```

Candidate discovery is then post hoc classified by the species relation, while final novelty tests use untouched ecologies and parent-reduction attacks.

This is the place where thousands or millions of viable raw forms may be explored without pretending every raw genotype is a new scientific species.

---

# 18. Morphogenetic plasticity

Define a regime-shift sequence

\[
e_0\to e_1\to\cdots\to e_T.
\]

For machine `M`, let `M_t` be its morphology after bounded adaptation.

Define morphogenetic adaptation burden

\[
B_{morph}(M;e_{0:T})
=
\sum_t
(\text{search} + \text{rebuild} + \text{verification} + \text{collateral loss})_t.
\]

A morphologically plastic species is valuable when it remains near-frontier across shifts with lower `B_morph` than repeatedly replacing the whole machine.

This directly tests LMHM/SCDI-like ideas and future unknown forms.

---

# 19. Transfer and migration

For source ecology `e_i` and target `e_j`, measure the burden of transferring:

```text
state
submodules
compilers
update laws
morphology rules
verifier policies
```

Define transfer advantage relative to fresh development:

\[
\Delta B_{transfer}(i\to j)
=B_{fresh}(e_j)-B_{transfer}(e_i\to e_j).
\]

This allows the biosphere to discover reusable developmental modules, not only static architectures.

---

# 20. Coevolving ecologies

A POET-like arm may generate new environments jointly with machines, but scientific safeguards are required.

Environment proposals must satisfy:

```text
solvability / validity checks
novelty relative to archive
bounded difficulty window
no machine-identity leakage
semantic contract generation independent of protected outcome labels
resource accounting
```

Coevolutionary worlds are development worlds unless separately frozen before final evaluation.

---

# 21. Open-endedness metrics

Do not define open-endedness by “the run kept going.” Track at least:

```text
new viable species rate
new frontier species rate
new occupied niches
mechanism-vector entropy/diversity
parent-reduction distance trend
maximum/median description complexity of viable forms
ecology complexity/demand breadth
transfer graph expansion
major morphology-transition count
long-run extinction/re-emergence structure
```

A run that generates endless syntactic mutations but no new behavior/frontier/niche structure is not scientifically open-ended.

---

# 22. Anti-cheating / anti-vacuity rules

Reject candidates that gain apparent novelty through:

```text
world ID / seed leakage
protected outcome lookup
hidden architecture labels
unmetered external models/APIs
unmetered human intervention
precision channels that encode target identity
unbounded compiler tables
search cost omitted from burden
parent baselines denied the same legal information
repeated tuning on protected ecologies
```

Run semantic remints and world-ID adversary baselines.

---

# 23. Biosphere scientific terminals

Positive terminals are graded:

```text
BIOSPHERE_CALIBRATION_RECOVERS_KNOWN_FORMS
PREDICTED_FORM_PROPERTY_VECTOR_RECOVERED
PREDICTED_FORM_RECOVERY_REPLICATES_ACROSS_SEARCH_ENCODINGS
CANDIDATE_SURVIVES_PARENT_REDUCTION_AT_SCOPE
OPEN_WORLD_FRONTIER_DISTINCT_SPECIES_DISCOVERED
MORPHOGENETIC_PLASTICITY_ADVANTAGE_REPLICATED
```

Negative/narrowing terminals include:

```text
SEARCH_GRAMMAR_CANNOT_RECOVER_KNOWN_PARENTS
NOVELTY_COLLAPSES_UNDER_IMPLEMENTATION_EQUIVALENCE
CANDIDATE_REDUCES_TO_PARENT
OPEN_ENDED_SEARCH_ONLY_GENERATES_SYNTACTIC_VARIANTS
SPECIES_RESULT_DEPENDS_ON_SEARCH_ENCODING
PROTECTED_ECOLOGY_ADAPTIVE_OVERFIT
RESOURCE_ACCOUNTING_REVERSES_WINNER
MORPHOGENESIS_COST_ERASES_PLASTICITY_ADVANTAGE
```

---

# 24. Scientific claim boundary

The biosphere is designed to support, eventually, statements of the form:

> under registered ecologies and resource semantics, a generic open morphology grammar repeatedly discovers a distinct developmental mechanism species that is frontier-useful, survives implementation reminting and bounded reduction to known parents, and transfers to protected real regimes.

It does **not** make “millions of new forms” true by construction.

The large search space is a hypothesis generator. Species identity and novelty are earned by equivalence, frontier, replication and reduction tests.
