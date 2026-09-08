# Machine Epistemics Cognitive Ladder — paper programme from exact worlds to language

Scientific thesis: #50  
Epistemic experience / lifelong reuse: #62  
Minimal cognitive vessel: #69  
Compact learned routers: #71  
Navigation / executive control: #72  
Integrated OCM vs strong neural systems: #73  
General Epistemic Field: #93  
Execution roadmap N1–N7: #42  
Mathematics route: #46–#48  
Independent acceptance / claims review: #38 / #49

## Status and role

**PAPER-PROGRAMME UMBRELLA. DOES NOT REPLACE #42, DOES NOT UNLOCK N4, DOES NOT OVERRIDE EXISTING FREEZE-BEFORE-OUTCOME OR CLAIM-BOUNDARY RULES.**

This issue defines the experimental and publication programme for establishing **Machine Epistemics** as an empirical field through a controlled complexity ladder:

```text
finite exact games
→ reusable cognitive methods
→ composition / failure / revision / representation change
→ planning / information gathering / sparse lifetime memory
→ cross-game transfer
→ formal mathematical reasoning
→ controlled compositional language
→ heterogeneous lifetime cognition
→ strongest matched neural / Transformer systems
```

The programme deliberately starts with environments where the complete state space, optimal policy, failure conditions and exact checker are available. Complexity is increased only after the previous rung demonstrates the intended mechanism under causal ablation and matched parents.

The purpose is **not** to show that symbolic systems beat neural networks on toy tasks. The purpose is to determine whether a persistent, explicit, warranted and revisable cognitive architecture exhibits a reproducibly different **lifetime learning and computation regime** as tasks become more complex.

---

# 1. Central scientific question

> **Can a single persistent machine acquire verified reusable cognitive methods, compose and revise them locally, transfer them across task families and eventually across domains, while maintaining task-quality parity with strong neural systems and reducing the marginal information, search, verification or maintenance required for future cognition?**

The strongest admissible programme-level claim, only after successful heterogeneous confirmatory studies, is:

> **Machine Epistemics organizes intelligence as persistent epistemically governed computational structure whose useful accumulated competence causally changes the cost and locality of later cognition under declared task ecologies, while preserving explicit authority, revision and resource accounting.**

This is narrower than AGI, “post-Transformer”, human equivalence or universal superiority.

---

# 2. Expert review structure

Every major rung, benchmark and paper must receive four independent reviews before protected execution:

### E1 — Cognitive-architecture reviewer
Owns:
- what exactly counts as a learned cognitive object;
- whether the mechanism is genuinely reusable rather than task memorization;
- operator/method/schema abstraction;
- composition and scope;
- representation change and subgoal formation;
- cross-domain mapping.

### E2 — Neural / continual-learning reviewer
Owns:
- strongest faithful neural baselines;
- Transformer / RL / meta-RL / memory / adaptation comparators;
- parameter, training-data and optimization fairness;
- catastrophic forgetting / continual learning controls;
- whether a neural system has been artificially weakened.

### E3 — Systems / measurement reviewer
Owns:
- wall / CPU / GPU / RSS / energy / IO accounting;
- storage / index / cache / rebuild cost;
- cold vs warm execution;
- hidden global preprocessing;
- persistence / restart / reproducibility;
- active-state measurement `k` versus total persistent state `N`.

### E4 — Skeptical top-tier reviewer
Owns:
- causal attribution;
- information leakage;
- pre-registration discipline;
- task-family and order effects;
- multiple comparisons;
- independent units and power;
- strongest-parent subtraction;
- paper wording and negative terminals.

**No headline result is accepted unless all four reviewers can state the treatment, strongest alternative explanation and falsifier.**

---

# 3. Non-negotiable scientific doctrine

- [ ] Freeze hypotheses, task families, held-out splits, comparators, budgets and primary endpoints before protected outcomes.
- [ ] Pilot data may repair engineering or select feasible scales, but pilot tasks must not silently become confirmatory evidence.
- [ ] Same information, examples, corpora, checker access, tool access, feedback and persistent-memory permissions for OCM and matched parents unless the difference itself is the registered treatment.
- [ ] OCM hand-authored operators, schemas, code and seed representations count as prior information.
- [ ] Neural pretraining, adaptation data, replay buffers and external retrieval corpora count as prior information/resources.
- [ ] Approximate retrieval or learned scores may propose; they may not become epistemic authority without the registered check.
- [ ] A failure under one method/budget is never promoted to impossibility.
- [ ] Every claimed learned method must have an identity, scope, acquisition history and actual later-use witness.
- [ ] Similarity is not reuse. Presence in memory is not causal use.
- [ ] Every reuse claim requires an ablation/removal test.
- [ ] Every cross-domain claim requires the cognitive method to be frozen before access to the target-domain protected tasks.
- [ ] Every efficiency claim includes construction/training, indexing, storage, maintenance, verification, revision and recovery costs.
- [ ] Exact negative terminals are publication results, not failed engineering.
- [ ] Complexity advances only when the current rung earns its exit receipt.

---

# 4. What would constitute evidence for Machine Epistemics?

The field should be defined by **measurable signatures**, not architectural aesthetics.

## ME-S1 — Causal reusable-method acquisition

```text
verified experience
→ acquired method/schema
→ persistence
→ restart
→ fresh task
→ actual method invocation
→ lower work / new-information burden
```

Required counterfactual:

```text
remove or revoke the learned method
→ advantage disappears or materially weakens
```

## ME-S2 — Method composition

Two methods acquired independently should enable a fresh task requiring `A+B`, without the combined solution being present in training.

## ME-S3 — Scoped failure learning

A failed strategy should reduce repeated wasted work in its true scope without suppressing success outside that scope.

## ME-S4 — Representation / abstraction improvement

The system should discover or acquire a representation that measurably changes later search/verification cost, and the representation must survive held-out tasks where simpler competing representations fail.

## ME-S5 — Subgoal / information-gathering cognition

The system should learn when an intermediate objective or discriminating probe has higher downstream value than direct action.

## ME-S6 — Sparse lifetime cognition

For growing persistent competence `N`, useful task computation should touch a task-relevant set `k` where, at registered scopes:

```text
k << N
query work tracks k materially better than N
```

including index/maintenance cost.

## ME-S7 — Exact local revision

Withdraw or change one support/method/environment assumption; only the true dependency cone should reopen or invalidate. Count stale survivors and collateral invalidations.

## ME-S8 — Cross-family transfer

A method learned in one task family should reduce future work in a different family with matched difficulty and no solution leakage.

## ME-S9 — Cross-domain transfer

A domain-neutral method learned before target-domain access should causally improve a materially different domain.

## ME-S10 — Lifetime resource residual

At matched task quality, OCM should occupy a different Pareto region over:

```text
new information
training/acquisition work
query/search work
checker calls
persistent bytes
active bytes
revision work
maintenance work
wall/CPU/GPU/energy
```

No post-hoc scalar “OCM score”.

---

# 5. Complexity ladder and engineering milestones

The ladder is cumulative. Each rung gets a frozen task contract, exact receipt, strongest comparator and explicit kill criterion.

## CL-0 — Measurement and causal-learning substrate

Purpose: ensure later experiments can distinguish actual cognitive reuse from cached answers or hidden search.

### Tasks
- [ ] Define canonical machine-readable `CognitiveEpisodeV1`.
- [ ] Define `MethodRecordV1`: identity, source episodes, scope, preconditions, operator sequence/schema, checker evidence, costs, revocation state.
- [ ] Define `ReuseEventV1`: method id, fresh task id, applicability witness, actual execution trace, counterfactual arm.
- [ ] Define `FailureAttemptV1`: method/task/scope/budget/outcome; explicitly not impossibility.
- [ ] Define `RepresentationChangeV1`.
- [ ] Define `SubgoalEventV1` and `ProbeEventV1`.
- [ ] Define common resource vector.
- [ ] Instrument cold/warm work separately.
- [ ] Instrument persistent bytes, active bytes, `N`, `k`, index probes and invalidation work.
- [ ] Add replay/restart custody.
- [ ] Add removal/revocation ablation helper.
- [ ] Add per-run immutable manifest and environment identity.

### Exit
`COGNITIVE_LADDER_MEASUREMENT_READY`

Kill criterion: cannot separate learned-method use from answer cache/retrieval.

---

## CL-1 — Exact subtraction/Nim causal learning

Purpose: smallest completely interpretable demonstration of learn → persist → restart → reuse.

### Task families
- one-heap subtraction games;
- varying legal move sets;
- two/three-heap Nim for representation discrimination.

### Required experiments
- [ ] Learn a reusable winning/losing-state method from solved episodes.
- [ ] Independent method checker.
- [ ] Persist method through actual OCM/KSO lifecycle.
- [ ] Restart from disk/process boundary.
- [ ] Fresh unseen states.
- [ ] Exact-search ablation with method removed.
- [ ] Persistent DP/search parent.
- [ ] Small MLP baseline.
- [ ] RL baseline where feasible.
- [ ] Negative-transfer move-set hostile.
- [ ] Local rule revision.
- [ ] Interference: add unrelated learned methods before reuse.
- [ ] Multiple training-state selections/orderings.

### Primary endpoints
- exact task success;
- search states / move evaluations;
- method-use identity;
- cost reduction versus reset/ablation;
- stale/collateral errors after revision.

### Exit
`CAUSAL_METHOD_REUSE_SUPPORTED_EXACT_GAMES` or `PARENT_SUFFICIENT` / `NO_CAUSAL_REUSE`.

### Paper candidate P1
**Causal acquisition and persistent reuse of explicit cognitive methods in exactly solvable environments.**

P1 must not claim cross-domain intelligence.

---

## CL-2 — Method composition and failure memory

Purpose: go beyond one reusable trick.

### Tasks
- [ ] Acquire method A and B from disjoint training families.
- [ ] Freeze fresh tasks requiring composition `A+B`.
- [ ] Verify no combined solution appears in training.
- [ ] Remove A only; measure degradation.
- [ ] Remove B only; measure degradation.
- [ ] Remove both.
- [ ] Compare with neural/meta-learning parent.
- [ ] Store scoped failed attempts.
- [ ] Test later avoidance of repeated failure.
- [ ] Harmful-transfer family where failed method becomes useful under changed scope.
- [ ] Verify failure memory does not suppress recovered applicability.

### Exit
`METHOD_COMPOSITION_SUPPORTED` and/or `FAILURE_MEMORY_USEFUL_AT_SCOPE`.

Kill criterion: all improvement reduces to answer retrieval or task-ID lookup.

---

## CL-3 — Representation discovery / strategy invention

Purpose: test whether OCM changes *how* it represents a family, not merely which action it retrieves.

### Candidate environments
- multi-heap Nim/invariant families;
- parity/XOR/distinguishable invariant worlds;
- small algebraic state machines;
- adversarial families where an initially attractive representation fails.

### Tasks
- [ ] Register candidate representation/operator language before protected outcomes.
- [ ] Include at least one deliberately misleading representation.
- [ ] Require two representations to fit training but disagree on held-out worlds.
- [ ] Learn/select the representation using valid evidence rather than benchmark identity.
- [ ] Test fresh states outside training magnitude.
- [ ] Persist representation identity.
- [ ] Revision hostile: environment change invalidates representation scope.
- [ ] Compare to learned embeddings / neural representation learner.
- [ ] Charge representation search/construction cost.

### Exit
`REPRESENTATION_CHANGE_CAUSALLY_USEFUL` or `PARENT_SUFFICIENT` / `REPRESENTATION_PRIOR_DOMINATES`.

---

## CL-4 — Subgoal discovery and planning

Purpose: introduce sequential cognition where optimal immediate action is insufficient.

### Candidate tasks
- key-door grid worlds;
- small Sokoban-like puzzles;
- deterministic navigation with bottlenecks;
- compositional task graphs.

### Tasks
- [ ] Exact planner provides oracle only, not policy donor.
- [ ] Learn recurring intermediate objective from solved episodes.
- [ ] Persist/restart.
- [ ] Fresh layouts with same abstract structure but different geometry.
- [ ] Layouts where the old subgoal is unnecessary.
- [ ] Layouts where the old subgoal is harmful.
- [ ] Learn when to invoke versus refuse subgoal.
- [ ] Compare against BFS/A*/planning parent.
- [ ] Compare against model-based RL / neural planning parent.
- [ ] Count environment steps, search nodes, verifier calls and learned-state maintenance.

### Exit
`SUBGOAL_METHOD_REUSE_SUPPORTED`.

Kill criterion: subgoal label is effectively supplied by task representation.

---

## CL-5 — Information gathering / `DISTINGUISH`

Purpose: test cognition whose best action is to reduce uncertainty rather than immediately solve.

### Candidate tasks
- 20-questions partitions;
- Mastermind variants;
- diagnosis games;
- hidden-state grid worlds;
- exact experiment-selection fixtures.

### Tasks
- [ ] Register allowed probes and information costs.
- [ ] Learn a probe-selection strategy from prior episodes.
- [ ] Fresh hypothesis spaces and permuted labels.
- [ ] Compare with entropy/information-gain parent.
- [ ] Compare with Bayesian/active-learning parent.
- [ ] Compare with neural policy / meta-RL.
- [ ] Test misleading probes and unequal costs.
- [ ] Test budget exhaustion separately from structural ambiguity.
- [ ] Preserve `CANNOT_CHECK` / insufficient-information terminals.

### Exit
`DISTINGUISH_METHOD_SUPPORTED` only if stronger classical information-gain parents do not fully explain the result.

Likely scientific result may be `PARENT_SUFFICIENT`; that is acceptable.

---

## CL-6 — Lifetime memory growth and local revision

Purpose: test the architectural predictions of #50/#62/#72 directly.

### Scale axis
Prospectively freeze feasible points such as:

```text
1x / 3x / 10x / 30x / maximum feasible
```

### Tasks
- [ ] Grow persistent method/task/evidence state with unrelated competence.
- [ ] Hold target task family fixed.
- [ ] Measure `N`, `k`, active bytes, index probes, query work.
- [ ] Charge index construction and updates.
- [ ] Compare global-scan OCM ablation.
- [ ] Compare database/index parent.
- [ ] Compare neural memory/retrieval parent.
- [ ] Revoke one shared premise/method.
- [ ] Measure true dependency cone.
- [ ] Count stale survivors.
- [ ] Count collateral invalidations.
- [ ] Restore support and measure exact recovery.
- [ ] Include one genuinely global dependency cone so locality is not guaranteed by task design.

### Exit
`ACTIVE_SUBSPACE_SCALING_SUPPORTED_AT_SCOPE` and/or `LOCAL_REVISION_ADVANTAGE_SUPPORTED`.

---

## CL-7 — Cross-game / cross-puzzle cognitive transfer

Purpose: determine whether learned methods are domain-general even before mathematics/language.

### Freeze a domain-neutral method vocabulary
Candidates:

```text
DECOMPOSE
SELECT_RELEVANT
APPLY_METHOD
SEARCH_MORE
DISTINGUISH
FORM_SUBGOAL
CHANGE_REPRESENTATION
CHECK
REVISE
ABSTAIN
CONSOLIDATE
GENERALIZE_METHOD
REUSE_METHOD
DETECT_OBSTRUCTION
```

This vocabulary itself is an architectural prior and must be ablated / minimized.

### Tasks
- [ ] Learn a method in one game family.
- [ ] Freeze method representation before target-family access.
- [ ] Map only via declared typed correspondence, not task labels.
- [ ] Test on a materially different puzzle family.
- [ ] Compare with reset OCM.
- [ ] Compare with task-specific OCM.
- [ ] Compare with meta-RL / continual-learning neural parent.
- [ ] Test harmful-transfer cases.
- [ ] Test unrelated families where no benefit is predicted.

### Exit
`CROSS_FAMILY_COGNITIVE_TRANSFER_SUPPORTED`.

---

## CL-8 — Formal mathematics curriculum

Purpose: use formal proof as a high-complexity but mechanically checked cognitive domain.

Existing FLT/proof work is an apparatus and curriculum donor; **full FLT success is not a prerequisite**.

### Curriculum
- simple propositional/equality proof families;
- small algebra/number-theory theorem families;
- miniF2F-style checked tasks where governance permits;
- broad Lean proof corpora;
- progressively masked reconstruction;
- selected difficult FLT-derived families as stress tests.

### Tasks
- [ ] Bind exact theorem/environment/checker identities.
- [ ] Separate imported theorem knowledge from acquired proof method.
- [ ] Extract candidate methods from solved proofs.
- [ ] Independent method/schema checking where possible.
- [ ] Fresh theorem-family reuse.
- [ ] Causal method ablation.
- [ ] Failure-attempt reuse.
- [ ] Proof-state subgoal discovery.
- [ ] Representation changes / lemma introduction.
- [ ] Strong symbolic search / Aesop/tactic parents.
- [ ] Retrieval theorem-prover parent.
- [ ] Neural-guided theorem search parent.
- [ ] Transformer proof-attempt reference with same checker/tool budget.
- [ ] Full acquisition/search/checker/storage accounting.

### Exit
`CAUSAL_PROOF_METHOD_REUSE_SUPPORTED` before any broad mathematical-learning claim.

### Paper candidate P4
**Verified persistent method learning in formal reasoning.**

---

## CL-9 — Controlled compositional language

Purpose: cross the boundary from exact formal worlds to ambiguity-bearing communication without jumping to unrestricted English.

### Language progression

```text
typed unary statements
→ quantifiers / negation
→ binary relations
→ compositional chains
→ ambiguity sets
→ clarification
→ reference / discourse
→ simple generation + reverse-read
```

### Tasks
- [ ] Freeze minimal linguistic substrate manifest.
- [ ] Count every supplied grammar/construction as prior information.
- [ ] Use unseen vocabulary labels so lexical memorization cannot explain structural transfer.
- [ ] Use unseen construction combinations.
- [ ] Artificial/non-English order hostile.
- [ ] Meaning-preserving paraphrase variants.
- [ ] Ambiguity requiring `DISTINGUISH`/clarification.
- [ ] Correction/revocation of lexical or construction support.
- [ ] Generation with reverse-read before commitment.
- [ ] Compare with symbolic grammar/logic parent.
- [ ] Compare with small neural models.
- [ ] Compare with Transformer trained/fine-tuned on identical post-freeze information.
- [ ] Compare with Transformer + persistent memory / retrieval.
- [ ] Measure task quality, information required to threshold, training cost, inference cost and revision cost.

### Cross-domain treatment
Freeze selected cognitive methods **before** language protected-task access and test:

- [ ] decomposition;
- [ ] subgoal formation;
- [ ] information gathering;
- [ ] representation change;
- [ ] scoped failure memory;
- [ ] method composition.

### Exit
`MATH_OR_GAME_DERIVED_COGNITIVE_TRANSFER_TO_LANGUAGE_SUPPORTED` only if a pre-existing domain-neutral method causally improves language acquisition/reasoning.

### Paper candidate P5
**Cross-domain transfer of explicit cognitive methods from formal/exact environments to controlled language.**

This is likely one of the programme’s highest-risk/highest-value papers.

---

## CL-10 — Heterogeneous lifetime comparison against strongest neural systems

Purpose: integrate the programme into one persistent-machine study.

### Domains
At least three materially different domains, preferably:

```text
games/planning
formal mathematics
controlled language
```

Coding/tool use may replace or add a domain when mature.

### Neural comparator ladder

```text
N0 task-specific conventional algorithm
N1 small neural baseline
N2 RL / meta-RL where appropriate
N3 Transformer / sequence model
N4 Transformer + retrieval/RAG
N5 Transformer + persistent memory
N6 Transformer + tools/checkers
N7 Transformer + memory + tools
N8 reasonable adaptation / skill-memory / continual-learning route
N9 strongest domain-specialized parent
```

Not every arm applies to every domain, but the strongest plausible explanation gets first right of refusal.

### Required OCM ablations
- [ ] reset-between-task OCM;
- [ ] no learned methods;
- [ ] no explicit failure memory;
- [ ] no dependency/revocation graph;
- [ ] no sparse index / global scan;
- [ ] no representation change;
- [ ] no method composition;
- [ ] no compact learned router where one exists.

### Primary capability gate
Prospectively define non-inferiority margin `δ` per domain:

```text
Performance_OCM >= Performance_strong_parent - δ
```

No lifetime-efficiency claim if OCM fails the core capability gate for that domain.

### Lifetime endpoints
- [ ] marginal new information per acquired family;
- [ ] marginal search/reasoning work;
- [ ] method/schema reuse identities;
- [ ] active `k/N`;
- [ ] correction/revocation locality;
- [ ] harmful-transfer detection;
- [ ] persistent bytes;
- [ ] index/maintenance cost;
- [ ] training/acquisition compute;
- [ ] query inference compute;
- [ ] external tool/checker calls;
- [ ] CPU/GPU/RSS/energy where measurable;
- [ ] total lifetime Pareto frontier.

### Exit
`HETEROGENEOUS_MACHINE_EPISTEMICS_SIGNATURE_SUPPORTED` only if positive evidence appears in multiple materially different domains and is not fully reproduced by the strongest matched neural/persistent parent.

### Paper candidate P6
**Persistent epistemically governed intelligence across heterogeneous tasks: capability, transfer, revision and lifetime resource scaling versus strong neural systems.**

---

# 6. Paper sequence and claim ladder

## P1 — Exact causal method learning
Claim ceiling: explicit persistent reusable methods causally reduce future work in finite exact environments.

## P2 — Lifetime learning in sequential/planning worlds
Claim ceiling: reusable methods, subgoals, failure memory and local revision improve cumulative cognition under matched parents.

## P3 — Domain-general cognitive operators
Claim ceiling: selected method classes transfer prospectively across materially different game/puzzle families.

## P4 — Formal reasoning
Claim ceiling: mechanically checked proof experience yields reusable methods that causally change later proof search.

## P5 — Cross-domain transfer to controlled language
Claim ceiling: at least one pre-acquired cognitive method transfers prospectively into a language-learning/reasoning family and reduces required information/work.

## P6 — Integrated heterogeneous machine
Claim ceiling: one persistent OCM remains capability-competitive at registered scope while exhibiting a reproducibly different lifetime learning/revision/computation regime versus strongest matched neural systems.

**Do not combine papers merely to inflate scope. Each paper should have one decisive causal contribution and independent falsifier.**

---

# 7. Statistical and confirmatory design

Every paper beyond pure exhaustive finite proof must have a prospective analysis plan.

### Independent units
- task family / environment seed / theorem family / language construction family, not individual correlated decisions unless justified.

### Required design
- [ ] pilot set separate from protected confirmatory set;
- [ ] held-out family identities;
- [ ] multiple task-order permutations;
- [ ] multiple random seeds for stochastic parents;
- [ ] matched resource budgets;
- [ ] paired comparisons where appropriate;
- [ ] effect sizes with confidence intervals;
- [ ] non-inferiority intervals for capability;
- [ ] superiority tests only for prospectively named architectural endpoints;
- [ ] hierarchical / cluster-aware analysis where examples share a family;
- [ ] multiplicity handling for multiple primary claims;
- [ ] preregistered exclusion and timeout rules;
- [ ] report all registered negative terminals.

### Recommended evidence form
No “won 7 of 10 benchmarks” conclusion by itself. Prefer:

```text
capability non-inferiority
+
prospective effect on one or more architectural signatures
+
causal ablation
+
replication
```

---

# 8. Resource and information accounting

For every arm record:

```text
immutable source/code bytes
hand-authored domain prior
pretraining data identity/size where known
post-freeze examples/interactions
parameter count / parameter bytes
persistent mutable state bytes
replay/memory bytes
index bytes
active bytes/query
training/acquisition CPU/GPU/time/energy
query CPU/GPU/time/energy
checker/tool calls
search expansions
storage reads/writes
revision/retraining work
cache/index invalidation work
```

Do not claim OCM is “small” from parameter count alone. Do not claim neural systems are expensive while ignoring OCM’s explicit database/index/verification costs.

---

# 9. Strongest reviewer attacks that must be defeated

- [ ] OCM’s hypothesis language already contains the answer family.
- [ ] OCM stores explicit task solutions rather than methods.
- [ ] OCM gets more memory/tool/checker access.
- [ ] Neural comparator is under-tuned or denied adaptation.
- [ ] Transformer pretraining is charged but OCM hand-authored code is treated as free.
- [ ] Later tasks are easier, creating fake amortization.
- [ ] Task ordering was selected after outcomes.
- [ ] Cross-domain mapping contains the target solution.
- [ ] Sparse query work hides global indexing/consolidation.
- [ ] Local revision looks exact because dependencies are incomplete.
- [ ] Failure memory is really a blacklist keyed by task identity.
- [ ] Representation discovery is selection from a tiny hand-picked menu.
- [ ] Subgoal learning is encoded in state features.
- [ ] Game results do not survive planning/math/language.
- [ ] Language result is only logical toy language and does not scale.
- [ ] OCM refuses difficult cases and therefore looks reliable.
- [ ] Whole-lifetime storage or verification cost dominates.
- [ ] A conventional symbolic/database/cognitive architecture explains the effect.
- [ ] A Transformer + persistent memory + tools reproduces the full signature.
- [ ] Positive results depend on one machine, seed, task order or benchmark family.

Every paper must include a table mapping each applicable attack → control → result → remaining limitation.

---

# 10. Required negative terminals / kill criteria

```text
CAUSAL_METHOD_REUSE_NOT_ESTABLISHED
METHOD_COMPOSITION_NOT_ESTABLISHED
FAILURE_MEMORY_NOT_USEFUL
REPRESENTATION_PRIOR_DOMINATES
SUBGOAL_PRIOR_DOMINATES
PARENT_SUFFICIENT
NO_CROSS_FAMILY_TRANSFER
NO_CROSS_DOMAIN_TRANSFER
NO_AMORTIZED_ACQUISITION
NO_AMORTIZED_REASONING
NO_SPARSE_EXECUTION
REVISION_NOT_LOCAL
HARMFUL_TRANSFER_LIMIT
STATE_SIZE_DOMINATES
INDEX_MAINTENANCE_DOMINATES
VERIFICATION_COST_DOMINATES
TRAINING_COST_DOMINATES
LLM_CAPABILITY_DOMINATES
PARAMETRIC_MODEL_DOMINATES
PROTOTYPE_SCALE_TOO_SMALL_FOR_CLAIM
CANNOT_CHECK_<reason>
```

A programme-level negative should change the architecture or narrow the field claim rather than trigger benchmark shopping.

---

# 11. Reproducibility and top-tier publication engineering

Each paper must ship or retain enough material for independent reconstruction.

### Before protected execution
- [ ] frozen source commit;
- [ ] environment/container/toolchain identities;
- [ ] dataset/task generator hash;
- [ ] public/private split manifest;
- [ ] comparator model/version/configuration;
- [ ] prompts where applicable;
- [ ] training/adaptation code and hyperparameter search policy;
- [ ] budgets and stopping rules;
- [ ] primary/secondary endpoints;
- [ ] statistical analysis script frozen;
- [ ] exclusion rules;
- [ ] randomization/order seeds.

### After execution
- [ ] raw outputs retained;
- [ ] machine-readable receipts;
- [ ] complete cost vectors;
- [ ] failed runs retained;
- [ ] negative terminals retained;
- [ ] exact ablation receipts;
- [ ] independent review of claim/result correspondence;
- [ ] clean rerun on fresh host for headline rows;
- [ ] second-seed/order replication;
- [ ] paper figure generated from immutable result tables;
- [ ] no manually transcribed headline values.

### Independent replication gate
Before a field-level claim:
- [ ] fresh host;
- [ ] fresh protected task-family draw where protocol permits;
- [ ] independent execution operator or script-only reproduction;
- [ ] reproduced primary endpoint direction;
- [ ] discrepancies published.

---

# 12. Programme milestones

## MP-0 — Canonical protocol
- [ ] finalize vocabulary and receipt schemas;
- [ ] freeze benchmark-generation rules;
- [ ] define neural comparator policy;
- [ ] define claim/terminal mapping.

## MP-1 — Real OCM exact-game integration
- [ ] migrate the existing standalone cognitive-ladder pilot into actual OCM/KSO persistence/runtime;
- [ ] run causal restart/ablation receipts;
- [ ] produce P1-ready pilot figures.

## MP-2 — Sequential cognition
- [ ] planning/subgoal;
- [ ] information gathering;
- [ ] failure memory;
- [ ] local revision;
- [ ] strong RL/classical parents.

## MP-3 — Cross-family transfer
- [ ] freeze domain-neutral cognitive-method vocabulary;
- [ ] run game→puzzle transfer;
- [ ] harmful/unrelated controls;
- [ ] meta-RL comparator.

## MP-4 — Formal proof curriculum
- [ ] connect current proof-corpus/Lean infrastructure;
- [ ] acquire and causally reuse proof methods;
- [ ] strongest symbolic/neural theorem-proving parents.

## MP-5 — Controlled language bridge
- [ ] expand current unary checked language;
- [ ] ambiguity/clarification/revision/generation;
- [ ] freeze pre-language transferred methods;
- [ ] strongest Transformer + memory/adaptation parents.

## MP-6 — Heterogeneous lifetime benchmark
- [ ] one persistent OCM;
- [ ] 3+ domains;
- [ ] multiple orderings;
- [ ] capability non-inferiority gates;
- [ ] lifetime Pareto analysis.

## MP-7 — Independent replication
- [ ] fresh host;
- [ ] frozen rerun;
- [ ] independent claims review;
- [ ] publication artifact bundle.

---

# 13. Immediate next implementation tranche

The next work should stay small enough to preserve causal clarity.

- [ ] Port the existing exact subtraction/Nim pilot into real OCM/KSO objects.
- [ ] Represent solved episode, learned method, scope and verifier evidence as first-class persistent state.
- [ ] Require restart before the first scored reuse.
- [ ] Add exact method-removal ablation.
- [ ] Add persistent DP parent and one small neural baseline.
- [ ] Add changed-rule negative-transfer condition.
- [ ] Add one method-composition task.
- [ ] Emit common lifetime resource receipt.
- [ ] Freeze the first protected game-family draw before execution.
- [ ] Treat the existing standalone 9-level synthetic ladder as **pilot/design evidence only**, never confirmatory evidence for the real OCM implementation.

No language or FLT result is required before this first causal OCM paper can be evaluated.

---

# 14. Relationship to N1–N7 and current FLT work

This programme does not replace the capability roadmap.

- Games/puzzles are an **experimental microscope** for cognitive mechanisms.
- Formal mathematics is the first high-complexity exact-checker domain.
- Controlled language is the first deliberate cross-domain ambiguity/communication bridge.
- N1–N3 remain the open-language capability stack.
- N4–N6 remain the mathematics/frontier stack under their existing gates.
- N7 remains proof-of-function.

The cognitive ladder should feed mechanisms and evidence into N1–N7, not bypass milestone ordering.

Current FLT/proof infrastructure should be treated as a rich worked-example / verification curriculum and difficult stress test. Full FLT reconstruction is **not** a prerequisite for testing causal method learning, cross-family transfer or controlled language transfer.

---

# 15. Field-definition criterion

Do not declare “Machine Epistemics” established as a distinct empirical field merely because OCM exists or because one benchmark is favorable.

A field-level empirical case requires, at minimum:

- [ ] explicit formal vocabulary for persistent epistemic/cognitive objects;
- [ ] working machine implementation;
- [ ] causal reusable-method evidence;
- [ ] local revision evidence;
- [ ] lifetime resource accounting;
- [ ] prospective cross-family transfer;
- [ ] prospective cross-domain transfer or a principled negative boundary;
- [ ] comparison to strongest faithful neural and conventional parents;
- [ ] independent replication;
- [ ] at least two materially different domains with positive architectural signatures;
- [ ] clear falsifiers and negative terminals.

Only then is the ambitious statement admissible:

> **Machine Epistemics is an empirically testable organization of intelligence in which knowledge, methods, evidence, uncertainty, dependencies, scope, learning and revision are persistent governed computational objects, yielding distinctive causal signatures in lifelong acquisition, reuse, sparse cognition and local revision under declared environments.**

Until then, this issue is a research programme designed to determine whether that statement survives contact with strong alternatives.

