# GMI Machine-Intelligence Species Atlas v2

Status: **PROSPECTIVE DERIVATION / CANDIDATE ARCHETYPES — NOVELTY NOT ESTABLISHED**

Status date: 2026-09-12.

Purpose:

> Derive a large, open-ended space of possible machine-intelligence forms from orthogonal GMI mechanism axes rather than inventing architectures by analogy with current neural systems.

Nothing in this file is a claim that a named candidate is scientifically novel. Existing neural, symbolic, probabilistic, causal, database, compiler, multi-agent, program-synthesis, active-learning and open-ended-evolution parents receive first refusal.

---

# 1. Species-generating coordinates

Represent a morphology archetype by

\[
\Sigma=(B,T,R,U,A,V,H,M,I,C,G,S),
\]

with:

```text
B  state/computation basis
T  topology/factorization
R  routing/composition
U  adaptation timescale/update law
A  authority semantics
V  verification/admission
H  history/lineage semantics
M  memory organization
I  intervention/information acquisition
C  compilation/materialization
G  morphogenesis/architecture change
S  substrate placement/precision/distribution
```

A conservative illustrative discretization is:

```text
B: 6 values   parametric / symbolic / probabilistic / retrieval / program / hybrid
T: 5 values   monolith / fixed modular / routed modular / graph / hierarchy
R: 5 values   fixed / content-routed / search / market-allocation / verifier-routed
U: 5 values   frozen / execution-state / online-parametric / continual / meta-update
A: 4 values   implicit / explicit-source / constitutional / proof-carrying
V: 4 values   none / learned critic / external checker / exact verifier
H: 4 values   ephemeral / checkpointed / persistent lineage / branching histories
M: 5 values   weights / working / episodic / semantic store / stratified
I: 4 values   passive / active-query / experiment / embodied intervention
C: 4 values   none / cache / task-compile / substrate-specialize
G: 5 values   fixed / parameter-grow / module-grow / local family-switch / meta-Gamma
S: 4 values   fixed / heterogeneous / migratory / distributed
```

This finite toy discretization already has

\[
6\cdot5\cdot5\cdot5\cdot4\cdot4\cdot4\cdot5\cdot4\cdot4\cdot5\cdot4
=76{,}800{,}000
\]

raw mechanism vectors.

This number is **not** a species count. Many vectors are impossible, dominated, semantically equivalent or reducible to one another. The biosphere programme must discover viable equivalence classes and ecological niches.

---

# 2. Known-parent zone

Before candidate forms below receive any novelty credit, the biosphere must recover and benchmark known strong families:

```text
linear/kernel/statistical learners
MLP/CNN/RNN/Transformer/state-space neural systems
mixture-of-experts/modular networks
retrieval/memory-augmented neural systems
world models/model-based RL
active learning/experimental design/causal discovery
Bayesian/probabilistic programs
symbolic rule/program/proof systems
neuro-symbolic systems
planning/search/tool-using agents
continual-learning/NAS hybrids
multi-agent/collective systems
quality-diversity/open-ended evolutionary systems
compiler/database/persistent-state hybrids
```

A candidate below is scientifically interesting only where GMI predicts a stronger response law than these labels alone.

---

# 3. F1 — Residual Quotient Machine (RQM)

Core idea:

> Use a broad predictive representation for everything it already distinguishes; represent only target-semantic distinctions that remain aliased inside predictive fibers.

Formal driver:

\[
H(S_O\mid S_P)>0
\]

but small relative to total target information.

Predicted properties:

```text
stable reusable predictor
small separately mutable residual state
composition q_O approx g(q_P,r)
residual capacity tracks within-predictive target multiplicity
sparse target updates avoid full predictor replacement
```

Nearest parents: RAG, adapters, external memory, neuro-symbolic augmentation.

Unique discriminator: augmentation burden must scale with measured predictive-target residual, not simply task difficulty.

---

# 4. F2 — Versioned Residual Quotient Mesh (VRQM)

Core idea:

> Put locality, versioning, provenance and rollback around the small residual state rather than around the whole foundation model.

Ecology:

```text
broad predictor stable
residual facts/rules volatile
updates local
verification strong
retention/lineage strict
```

Predicted transition:

```text
weak residual retention -> mutable residual memory
strong rejectability -> shadow/verify/swap residuals
historical queries -> persistent residual lineage
```

Nearest parents: transactional RAG stores, modular continual learning, VLC, databases + LLM.

Unique discriminator: versioning should migrate specifically to the residual layer as residual volatility rises while predictive-core volatility remains low.

---

# 5. F3 — Verifier-Gated Speculative Compiler (VGSC)

Core idea:

> Separate cheap proposal, authoritative admission and cheap repeated serving.

Lifecycle:

```text
proposal -> isolated candidate -> verifier -> authoritative state -> compiled serving state
```

Ecology:

```text
proposal cheap/high recall
false adoption expensive
verification possible
accepted result highly reusable
```

Nearest parents: program synthesis + tests, theorem proving + checker, generate-and-rank, scientific hypothesis testing.

Unique discriminator: phase boundaries must respond independently to proposal quality, verifier price, false-adoption loss and reuse horizon.

---

# 6. F4 — Interventional Quotient Learner (IQL)

Core idea:

> Act specifically to split target-semantic aliases that passive prediction cannot resolve.

Objective:

\[
IG_O(j)=\mathcal A(S_O\mid E_t)-E[\mathcal A(S_O\mid E_{t+1})\mid do(j)].
\]

Ecology:

```text
observational aliases substantial
legal interventions available
wrong causal state costly
experiment price below ambiguity burden
```

Nearest parents: active learning, Bayesian experimental design, causal discovery, exploration.

Unique discriminator: intervention policy should be better predicted by target-quotient ambiguity reduction than by generic predictive entropy.

---

# 7. F5 — Locally Morphogenetic Heterogeneous Mesh (LMHM)

Core idea:

> Different semantic/dependency factors may independently change realization family during life.

Example:

```text
factor A: neural approximation
factor B: exact program
factor C: retrieval store
factor D: Bayesian posterior
factor E: external experiment policy
```

`Gamma` acts locally rather than globally.

Nearest parents: MoE, dynamic modular networks, continual NAS, neuro-symbolic architectures.

Unique discriminator: under independent local ecology changes, only affected factors should switch family while unaffected factors remain stable, beating repeated global NAS/retraining after search cost is charged.

---

# 8. F6 — Self-Compiling Developmental Intelligence (SCDI)

Core idea:

> Preserve one rich authoritative developmental state and compile multiple disposable serving realizations for different workloads/substrates.

Examples:

```text
fast edge model
exact server-side solver
low-energy cache
high-throughput batch compiler
human-auditable symbolic view
```

Nearest parents: distillation, compiler specialization, model serving cascades, database materialized views.

Unique discriminator: compilation portfolio should track query distribution and resource prices while authoritative developmental semantics remain invariant.

---

# 9. F7 — Evidence-Tiered Memory Intelligence (ETMI)

Core idea:

> Memory is stratified by epistemic authority, not merely recency or embedding similarity.

State layers may include:

```text
unverified observations
source-attributed claims
cross-checked beliefs
formally verified facts
revoked/superseded history
```

Execution may retrieve all layers, but authority rules determine which may support protected actions.

Ecology:

```text
high provenance/authority burden
contradictory sources
facts change over time
false acceptance asymmetric
```

Nearest parents: provenance databases, truth-maintenance systems, RAG with metadata, knowledge graphs.

GMI prediction: increasing authority asymmetry should create sharper separation between retrieval relevance and admissible evidence.

Unique discriminator: a similarity-only memory should lose frontier position specifically when provenance/authority demand rises, even if predictive accuracy on static IID queries is unchanged.

---

# 10. F8 — Causal Residual World Model (CRWM)

Core idea:

> A broad observational world model supplies reusable dynamics, while a smaller causal/interventional residual represents distinctions not identifiable from passive trajectories.

Form:

\[
S_{causal}=g(S_{pred},R_{do}).
\]

Ecology:

```text
large passive-data stream
few costly interventions
many observational regularities reusable
small set of intervention-critical aliases
```

Nearest parents: model-based RL, causal representation learning, system identification, hybrid physics/data models.

Unique discriminator: intervention residual size/sample burden should track controlled observational equivalence classes, rather than total world-model size.

---

# 11. F9 — Branching Hypothesis Intelligence (BHI)

Core idea:

> Preserve several mutually incompatible but still-live developmental states instead of collapsing early to one belief/model.

State:

\[
\{(Z_i,w_i,provenance_i)\}_{i=1}^k
\]

with branch-specific predictions, interventions and verification.

Ecology:

```text
ambiguity persistent
premature commitment expensive
later evidence can sharply discriminate
historical explanation required
```

Nearest parents: Bayesian model averaging, particle filters, version control, hypothesis management, ensemble methods.

Unique discriminator: benefit should rise with delayed discriminative evidence and asymmetric irreversible commitment cost, while disappearing when immediate sufficient evidence is available.

---

# 12. F10 — Multi-Timescale Consolidating Intelligence (MTCI)

Core idea:

> Separate very-fast execution adaptation, medium-term episodic/adaptor state and slow consolidated semantic state.

Example timescales:

```text
working activation / scratch state
session memory / adapter
episodic store
slow parametric consolidation
verified long-term knowledge
```

Ecology:

```text
rapid local changes
recurrent patterns worth consolidation
strict retention
variable reuse horizons
```

Nearest parents: complementary learning systems, meta-learning, replay/continual learning, adapters, memory systems.

Unique discriminator: optimal transfer threshold between layers should move with recurrence/reuse and interference price, not merely elapsed time.

---

# 13. F11 — Contract-Directed Tool Ecology (CDTE)

Core idea:

> Tools/programs/solvers are not generic calls; they are typed realization modules chosen according to semantic contract, evidence need and resource price.

A router selects among:

```text
neural inference
retrieval
calculator/solver
program execution
search
proof checker
simulator
external experiment
human escalation
```

Nearest parents: tool-using LLMs, agent frameworks, algorithm selection, portfolio solvers.

Unique discriminator: routing should be predictable from obligation coordinates and tool guarantees, and should remap under substrate/tool repricing without retraining the entire semantic core.

---

# 14. F12 — Resource-Arbitrage Intelligence (RAI)

Core idea:

> The same semantic function migrates among representations/substrates when compute, memory, communication, energy or verification prices change.

Possible migrations:

```text
neural -> cached table
neural -> distilled model
symbolic -> compiled circuit
remote solver -> local approximation
exact -> approximate with abstention
```

Nearest parents: adaptive serving, edge/cloud partitioning, compilers, model compression.

Unique discriminator: morphology transition boundaries should be predicted from resource price ratios while semantic obligation stays fixed.

---

# 15. F13 — Collective Quotient Intelligence (CQI)

Core idea:

> No single node holds the full target-semantic state; the sufficient state exists only in the communication/consensus structure of a population.

Let local states be `Z_i`; collective sufficiency requires

\[
q_O(h)=g(Z_1,\ldots,Z_n,C_{comm})
\]

where no registered individual subset is sufficient.

Ecology:

```text
distributed private observations
communication expensive
specialized local competence
fault/Byzantine/authority constraints possible
```

Nearest parents: multi-agent systems, federated learning, distributed inference, swarm intelligence.

Unique discriminator: communication topology and message semantics become part of the cognitive state; performance should exhibit predicted transitions under information partition and communication price.

---

# 16. F14 — Multi-Resolution Quotient Ladder (MRQL)

Core idea:

> Maintain nested semantic representations at several abstraction levels and answer each query from the coarsest level sufficient for its obligation.

Suppose

\[
S_0 \twoheadrightarrow S_1 \twoheadrightarrow \cdots \twoheadrightarrow S_k
\]

are progressively coarser quotients.

A query-specific selector chooses minimal `i` preserving required distinctions.

Ecology:

```text
query precision requirements vary greatly
fine state expensive
coarse answers often sufficient
```

Nearest parents: hierarchical models, abstraction in RL, multi-resolution databases, cascades.

Unique discriminator: serving cost should scale with semantic resolution demanded by the query, not globally with maximum model resolution.

---

# 17. F15 — Proof-Carrying Adaptive Intelligence (PCAI)

Core idea:

> Updates that affect protected high-risk behavior are admitted only with machine-checkable evidence satisfying the constitution/verifier contract.

Update object:

\[
(candidate,proof/witness,dependency\ cone,rollback\ receipt).
\]

Ecology:

```text
exact/safety-critical obligations
strong local verifier
updates frequent enough to matter
false adoption very expensive
```

Nearest parents: proof-carrying code, certified learning/control, theorem-proving agents, shielded RL.

Unique discriminator: verified local adaptation can dominate both frozen certified systems and unconstrained adaptive systems when update locality is high and verifier burden is sufficiently low.

---

# 18. F16 — Elastic-Precision Intelligence (EPrI)

Core idea:

> Numerical/symbolic precision is itself a dynamically allocated cognitive resource.

Different factors may run at:

```text
binary/quantized approximation
low precision neural arithmetic
high precision numeric state
exact symbolic/rational arithmetic
proof-level exactness
```

Ecology:

```text
mixed error tolerance
large compute/energy price differential
some rare exactness-critical subproblems
```

Nearest parents: mixed-precision inference, anytime algorithms, adaptive precision arithmetic.

Unique discriminator: precision allocation should track semantic error sensitivity rather than layer identity alone.

---

# 19. F17 — Adaptive Portfolio Orchestrator (APO)

Core idea:

> Maintain a population of heterogeneous full solvers and learn which solver or composition is appropriate for each ecological region.

Unlike ordinary MoE, experts may be completely different paradigms and possess independent development histories.

Nearest parents: algorithm selection, hyper-heuristics, portfolio SAT/optimization, multi-agent orchestration.

Unique discriminator: portfolio membership itself should evolve with ecology distribution, and the gain must survive charging the cost of maintaining/tuning multiple solvers.

---

# 20. F18 — Self-Modeling Morphogenetic Scientist (SMMS)

Core idea:

> The system learns response models of its own mechanisms and uses them to decide what architectural/developmental change to try next.

Meta-state contains an approximate law

\[
\hat R:(X,P,A,H,\Delta M)\mapsto \Delta Y.
\]

It can choose:

```text
collect more data
run an intervention
change module family
change precision
compile a serving path
spawn/kill an expert
change verifier strategy
```

Ecology:

```text
long lifetime
many regime changes
morphology-search actions costly
regularities in how previous changes affected burden
```

Nearest parents: AutoML/NAS, meta-learning, self-adaptive systems, open-ended evolution.

Unique discriminator: learned morphology interventions must transfer to unseen ecology shifts and beat a comparably budgeted static search policy after meta-development cost is charged.

---

# 21. Composite species are expected

The most interesting biosphere organisms will likely combine archetypes.

Examples:

```text
CRWM + IQL:
    predictive world model plus active causal residual acquisition

VRQM + ETMI:
    versioned residual facts stratified by provenance/authority

VGSC + PCAI:
    speculative candidate generation with proof-carrying admission

LMHM + RAI:
    local modules both change family and migrate across substrates

MTCI + SCDI:
    multi-timescale developmental memory compiling workload-specific servants

CQI + BHI:
    distributed population maintains competing hypotheses across agents

MRQL + EPrI:
    abstraction level and numeric precision jointly match query obligation

SMMS + any of the above:
    system learns when to change its own morphology
```

A combinatorial biosphere should therefore recover recurring complexes rather than one flat species list.

---

# 22. Prediction: ecology partitions the species space

There is no universal best species.

GMI predicts ecological niches generated by interacting coordinates such as:

```text
predictive-target residual
causal alias burden
query/update locality
retention and lineage
verification availability
false-adoption asymmetry
history ambiguity
reuse horizon
intervention availability
resource prices
communication prices
exactness requirements
regime-change hazard
lifetime length
```

The scientific target is a conditional law

\[
Pr(\Sigma\in\mathcal F(e)\mid \Xi_{obl}(e),P(e),H_{dev}),
\]

not an unconditional leaderboard.

---

# 23. Species-discovery admission ladder

Use:

```text
S0 DERIVED ARCHETYPE
   property vector predicted before search

S1 NEUTRAL RECOVERY
   generic grammar recovers matching phenotype

S2 PROTECTED RECURRENCE
   recurs on fresh ecologies/remints

S3 ENCODING INVARIANCE
   independent search encodings recover equivalent phenotype

S4 PARENT NON-REDUCTION
   strongest known parent cannot reproduce frontier result at comparable burden

S5 REAL TRANSFER
   survives code/math/science/control or other registered real tasks

S6 SPECIES LAW
   ecology coordinates prospectively predict appearance/disappearance/frontier niche
```

Only S4+ warrants serious novelty discussion. S6 is the desired mature theory level.

---

# 24. Immediate high-information experiments

Prioritize candidates whose predictions sharply differ from strong parents:

```text
1. RQM / CRWM:
   residual capacity vs controlled target/predictive alias multiplicity

2. VRQM / ETMI:
   volatility x provenance x lineage -> location of versioned authority state

3. IQL:
   target-semantic ambiguity gain vs generic uncertainty criteria

4. LMHM:
   local regime shifts -> local family switching vs static MoE/global NAS

5. MRQL:
   query-required semantic resolution -> compute/state activated

6. RAI / EPrI:
   resource/precision repricing -> reversible morphology migration

7. CQI:
   private-information partition x communication price -> collective state topology

8. SMMS:
   transfer of learned morphology-response model to unseen ecology shifts
```

These experiments are more informative than simply scaling one neural architecture.

---

# 25. Claim ceiling

At present these are theory-derived **candidate archetypes**, not established new species.

The correct current statement is:

> GMI generates an enormous architecture-neutral morphology space and predicts multiple non-neural/hybrid developmental property complexes. The biosphere programme can test whether any such complex forms a reproducible, parent-nonreducible ecological species.
