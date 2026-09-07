# ORION_CONCEPT_VALIDATION_ATLAS_V1

**GENERATED FILE — edit `atlas_data.py`, then run `python atlas.py`.**

Every ORION concept that could materially affect cognition is recorded here as a
*hypothesis under test*, never as a feature requirement. Three rules govern the table.

1. **Implementation is never scientific support.** `implementation_status` and
   `scientific_status` are separate columns. A concept may be fully built and still sit at
   `THEORY_ONLY` or `PARENT_SUFFICIENT`.
2. **Existing negative results survive.** `preserved_terminals` carries exact terminal strings
   already recorded elsewhere in the ORION repositories. New work may open a *new*
   pre-registered study. It may not reinterpret an old receipt.
3. **Every concept can die.** `falsifier` and `disposition` are mandatory. A concept a parent
   explains is merged. A concept with no measurable incremental value is dropped.

## Vocabulary discipline

`PARENT_SUFFICIENT` is a **successful** terminal, not a failure and not a statement that prior
published work suffices. In several ORION studies the parent federation holds ORION's own typed
modules, and its comparator class is recorded there as a ceiling control rather than prior work.

Saturation in ORION V1 and V2 always means **search coverage of a declared literature or donor
universe**. Cognitive saturation, meaning an agent's own reasoning ceasing to yield new
decision-relevant structure, is unclaimed in both repositories. It is introduced here as a new
concept and is not attributed to ORION.


## Summary

| disposition | concepts |
|---|---|
| **KEEP** | REUSABLE_METHOD_ACQUISITION, METHOD_COMPOSITION, REOPENING_LOCAL_REVISION, REPRESENTATION_CHANGE, SUBGOAL_FORMATION, NEGATIVE_TRANSFER_REFUSAL, CONSOLIDATION, SELF_MODEL_AND_FAILURE_DIAGNOSIS, AUTHORITY_NON_AMPLIFICATION, WARRANT_CONSERVATION, RESOURCE_RESPONSIBILITY, PERSISTENT_RESTARTABLE_COMPETENCE |
| **ADAPT** | SCOPED_FAILURE_KNOWLEDGE, SEARCH_MORE_VS_JUMP, FIBRES_MULTISCALE_TRANSPORT, SPARSE_ACTIVE_SUBSPACE, RECURSIVE_DECOMPOSITION, DISTINGUISH_DISCRIMINATING_QUERY, GOVERNED_SELF_REORGANIZATION, EPISTEMIC_HYSTERESIS, MULTI_GENERATION_IMPROVEMENT |
| **MERGE** | OBSTRUCTION_DIAGNOSIS, SHADOW_EVALUATION_AND_ROLLBACK, THOUGHT_EXPERIMENT_COUNTERFACTUAL |
| **DROP** | LOCAL_TO_GLOBAL_OBSTRUCTION, EPISTEMIC_TENSION_DETECTION, CONCEPT_OPERATOR_INVENTION |
| **SPLIT** | COGNITIVE_SATURATION |

| concept | disposition | scientific status | implementation | paper role |
|---|---|---|---|---|
| DISTINGUISH_DISCRIMINATING_QUERY | ADAPT | PARENT_SUFFICIENT | PARTIAL_IN_SRC_OCM | P5 transport vehicle |
| EPISTEMIC_HYSTERESIS | ADAPT | CANNOT_CHECK | IMPLEMENTED_IN_SRC_OCM | P3 supporting |
| FIBRES_MULTISCALE_TRANSPORT | ADAPT | PARENT_SUFFICIENT | PILOT_IMPLEMENTED_THIS_TRANCHE | P3 supporting; not a headline |
| GOVERNED_SELF_REORGANIZATION | ADAPT | CANNOT_CHECK | IMPLEMENTED_IN_SRC_OCM | P7 only if earned |
| MULTI_GENERATION_IMPROVEMENT | ADAPT | THEORY_ONLY | NOT_IMPLEMENTED | P7 only if earned |
| RECURSIVE_DECOMPOSITION | ADAPT | THEORY_ONLY | PARTIAL_IN_SRC_OCM | P3 supporting |
| SCOPED_FAILURE_KNOWLEDGE | ADAPT | IMPLEMENTED_UNTESTED | PILOT_IMPLEMENTED_THIS_TRANCHE | P2 primary discriminator |
| SEARCH_MORE_VS_JUMP | ADAPT | CALIBRATED | PILOT_IMPLEMENTED_THIS_TRANCHE | P2 flagship discriminator |
| SPARSE_ACTIVE_SUBSPACE | ADAPT | IMPLEMENTED_UNTESTED | PILOT_IMPLEMENTED_THIS_TRANCHE | P3 primary |
| CONCEPT_OPERATOR_INVENTION | DROP | THEORY_ONLY | NOT_IMPLEMENTED | none |
| EPISTEMIC_TENSION_DETECTION | DROP | THEORY_ONLY | PARTIAL_IN_SRC_OCM | none |
| LOCAL_TO_GLOBAL_OBSTRUCTION | DROP | THEORY_ONLY | NOT_IMPLEMENTED | none |
| AUTHORITY_NON_AMPLIFICATION | KEEP | CAUSALLY_SUPPORTED | IMPLEMENTED_IN_SRC_OCM | method section invariant |
| CONSOLIDATION | KEEP | THEORY_ONLY | PARTIAL_IN_SRC_OCM | P3 |
| METHOD_COMPOSITION | KEEP | THEORY_ONLY | GAME_FAMILY_READY_MECHANISM_PENDING | P2 primary |
| NEGATIVE_TRANSFER_REFUSAL | KEEP | CANNOT_CHECK | IMPLEMENTED_IN_SRC_OCM | P3 mandatory reported endpoint |
| PERSISTENT_RESTARTABLE_COMPETENCE | KEEP | CAUSALLY_SUPPORTED | TEMPLATE_EXISTS_IN_MATH_LANGUAGE_LEARNING_V1 | P1 method section |
| REOPENING_LOCAL_REVISION | KEEP | PARENT_SUFFICIENT | IMPLEMENTED_IN_SRC_OCM | P3 supporting |
| REPRESENTATION_CHANGE | KEEP | THEORY_ONLY | LANGUAGE_IMPLEMENTED_MECHANISM_PENDING | P2/P3 |
| RESOURCE_RESPONSIBILITY | KEEP | CAUSALLY_SUPPORTED | IMPLEMENTED_IN_SRC_OCM | method section invariant |
| REUSABLE_METHOD_ACQUISITION | KEEP | IMPLEMENTED_UNTESTED | PILOT_IMPLEMENTED_THIS_TRANCHE | P1 primary |
| SELF_MODEL_AND_FAILURE_DIAGNOSIS | KEEP | CANNOT_CHECK | IMPLEMENTED_IN_SRC_OCM | P7 only if earned |
| SUBGOAL_FORMATION | KEEP | THEORY_ONLY | NOT_IMPLEMENTED | P2 |
| WARRANT_CONSERVATION | KEEP | PARENT_SUFFICIENT | IMPLEMENTED_IN_SRC_OCM | method section constraint |
| OBSTRUCTION_DIAGNOSIS | MERGE | CALIBRATED | IMPLEMENTED_IN_SRC_OCM | P2 within the escalation study |
| SHADOW_EVALUATION_AND_ROLLBACK | MERGE | CAUSALLY_SUPPORTED | IMPLEMENTED_IN_SRC_OCM | P7 method section |
| THOUGHT_EXPERIMENT_COUNTERFACTUAL | MERGE | CANNOT_CHECK | PARTIAL_IN_SRC_OCM | P7 |
| COGNITIVE_SATURATION | SPLIT | CALIBRATED | PILOT_IMPLEMENTED_THIS_TRANCHE | P2 supporting mechanism |

## Immediately testable in the current exact-game apparatus

1. **SCOPED_FAILURE_KNOWLEDGE** — strongest parent: ATMS nogoods (de Kleer 1986).
2. **COGNITIVE_SATURATION** — strongest parent: abstract interpretation fixed points.
2. **SEARCH_MORE_VS_JUMP** — strongest parent: CEGAR abstraction refinement.
3. **FIBRES_MULTISCALE_TRANSPORT** — strongest parent: ordinary database index.

## Concepts

### SCOPED_FAILURE_KNOWLEDGE

*ADAPT* · scientific status **IMPLEMENTED_UNTESTED** · implementation `PILOT_IMPLEMENTED_THIS_TRANCHE` · paper role: P2 primary discriminator

**Definition.** A record that a named method failed on a named task under a named assumption set, representation, evidence set and resource bound, together with the diagnosed responsibility, the exclusions that diagnosis justifies, the alternatives still live, the successes preserved, the scope, and the conditions under which the exclusion reopens.

**Explicitly not.** NOT a memory that an attempt failed. NOT impossibility. NOT a blacklist keyed on task identity. A failure under one method and budget is never promoted to impossibility.

**Strongest parents.** ATMS nogoods (de Kleer 1986); JTMS dependency-directed backtracking; CEGIS; Reflexion-style transcript summaries; nearest-neighbour failure retrieval; continual-learning replay

**Observable state.** FailureStore exclusions keyed on (method, assumption-set); reopen index over assumptions **Trigger.** a checked attempt terminates without a certified solution

**Mechanism.** diagnose the cause; create an exclusion only for REFUTED_BY_CHECKER or ASSUMPTION_VIOLATED; key it on the assumption set; reopen exactly when a depended-on assumption changes **Information available.** the attempt trace, the checker verdict, the assumption set in force, the budget consumed. Not the ground-truth label of unprobed positions.

**Positive family.** method learned on SUB(S1) fails on SUB(S2); a fresh S2 task avoids the same dead end

**Negative twin.** an unrelated family where the exclusion must not fire

**Hostile.** same failure label, different root cause; budget exhaustion; non-identifying probe; evaluator defect; changed assumptions; permanent broken-shut

**Ablation.** remove the failure store; replace with a task-ID blacklist; replace with cause-blind nogood exclusion

**Resource coordinates.** search_expansions; checker_calls; persistent_state_bytes; revision_work

**Cross-family test.** exclusion learned on subtraction families must not suppress a Nim family it does not scope **Cross-domain test.** diagnosis method frozen before language access, applied to clarification failure

**Interactions.** SATURATION; OBSTRUCTION_DIAGNOSIS; REOPENING_LOCAL_REVISION

**Falsifier.** a cause-blind nogood parent matches on repeated-work avoidance AND on reopening after regime change

**Disposition reason.** the failure-epistemology closure already froze the strongest-parent gap at 0/32 and assigned the mechanism to TMS/nogood plus responsibility. Its OWN stated falsifier is that ORION beats the strong parent on a scientifically meaningful protected coordinate. The pilot is therefore run as an attempt at that falsifier, with expectation PARENT_SUFFICIENT, and is narrowed to the one coordinate the closure did not fix: reopening keyed on assumptions after a regime change.

**Preserved terminals (do not re-litigate).**

- `FAILURE_MEMORY_USEFUL_BUT_STANDARD_METHODS_SUFFICIENT (ORION/research/extensions/orion-jump-recursive-atoms/failure_epistemology/FAILURE_EPISTEMOLOGY_CLOSURE_V1.md) - a subsumption result; the strongest-parent incremental gap was frozen at 0/32 BEFORE execution`
- `TMS_NOGOOD_PLUS_RESPONSIBILITY_SUFFICIENT (failure-to-scoped-negative-knowledge atom, FAILURE_ATOM_PILOT_CLOSURE_V1.md)`
- `P7_TRANSPORT_SUFFICIENT (negative-knowledge staleness atom, same file)`
- `MULTIPLE_FAILURE_SIGNAL_ATOMS_REQUIRED (silent-failure observability atom)`
- `MEG-16 checked exhaustively at n=3 (kso/nogoods.py)`
- `no lifetime failure-memory benefit has ever been measured`

**Signatures.** scoped_failure_learning; local_revision; safe_negative_transfer_refusal

**Reopen condition.** if a nogood parent matches, re-scope the claim to the reopening endpoint only

### COGNITIVE_SATURATION

*SPLIT* · scientific status **CALIBRATED** · implementation `PILOT_IMPLEMENTED_THIS_TRANCHE` · paper role: P2 supporting mechanism

**Definition.** For a registered representation R, operator/method space O, evidence E, allowed probe set A and resource bound B, the reachable search space has been validly closed under the registered contract. Terminal: SATURATED_WITHIN_REGISTERED_SPACE.

**Explicitly not.** NOT research/donor literature saturation, which is about coverage of a survey procedure. NOT PROBLEM_IMPOSSIBLE, which requires an independent proof. NOT authority to Jump. A plateau cannot establish that no solution exists.

**Strongest parents.** abstract interpretation fixed points; solver completeness certificates; equality saturation / egglog; exhaustive search with a closure certificate

**Observable state.** version space survivors; the set of probes that would split them **Trigger.** no allowed probe separates two surviving hypotheses

**Mechanism.** declare saturation scoped to (R,O,A,B) and pass it to obstruction diagnosis as one input among several **Information available.** the surviving version space and the permitted probe set only

**Positive family.** W8: two extensionally identical hypotheses survive every probe

**Negative twin.** W1: a splitting probe exists, so the space is not saturated

**Hostile.** W1H: budget spent while a splitting probe exists — exhaustion, not saturation

**Ablation.** treat saturation as authority to change representation (the saturation parent)

**Resource coordinates.** search_expansions; index_probes; checker_calls

**Cross-family test.** the same saturation test over Nim combiner languages and subtraction period languages **Cross-domain test.** saturation of a proof-tactic space under a fixed tactic vocabulary

**Interactions.** SEARCH_MORE_VS_JUMP; SCOPED_FAILURE_KNOWLEDGE

**Falsifier.** a solver-closure parent produces the same scoped terminal with the same accuracy

**Disposition reason.** research/donor saturation and cognitive saturation were one word for two mechanisms; they are separated here and only the cognitive one is a programme object

**Preserved terminals (do not re-litigate).**

- `'Open-ended cognitive saturation is not established' (research/programme/ORION_CONCEPTS.md)`
- `TARGETED_SEARCH_ONLY_NOT_SATURATION (RCL_NOVELTY_SEARCH_AND_RESIDUAL_V0.json)`
- `AUDIT FINDING: every operative sense of saturation in ORION V1 and V2 is search-coverage saturation of a declared literature/donor universe (FOUNDATION_SATURATION_PROTOCOL_V1.md). Cognitive saturation is UNCLAIMED TERRITORY in both repositories; introducing it here is a new concept, not an ORION term, and must not be attributed to ORION.`

**Signatures.** governed_representation_operator_evolution

**Reopen condition.** if an independent generator produces worlds the policy has not seen and accuracy holds

### SEARCH_MORE_VS_JUMP

*ADAPT* · scientific status **CALIBRATED** · implementation `PILOT_IMPLEMENTED_THIS_TRANCHE` · paper role: P2 flagship discriminator

**Definition.** SEARCH_MORE keeps representation, operator vocabulary and problem formulation fixed and adds budget, order or probes. A Jump changes representation, abstraction, operator vocabulary, problem formulation, measurement interface, control policy or framework, and requires incumbent closure, a witnessed obstruction, evidence that lower repair is insufficient, a candidate transformation, frozen predictions, preservation obligations, independent validation and external adoption authority.

**Explicitly not.** Timeout, low score, repeated failure, uncertainty and failed retrieval are NOT Jump witnesses. Saturation alone is not a Jump witness.

**Strongest parents.** CEGAR abstraction refinement; CEGIS vocabulary extension; version-space collapse policies; active learning probe selection; Soar impasse and chunking; architecture search

**Observable state.** diagnosed escalation level L0..L6 with an exhibited witness where one exists **Trigger.** the incumbent fails to identify

**Mechanism.** exclude every cheaper explanation in order before proposing a more expensive one; require an exhibited witness for any level at or above the Jump threshold **Information available.** observed evidence, surviving version space, permitted probes, remaining budget. Never the ground-truth level.

**Positive family.** W3 local repair, W4 operator insufficiency, W5 representation non-identifying, W6 formulation defect

**Negative twin.** W7: the incumbent already identifies and any escalation is overreach

**Hostile.** W1H budget exhaustion; W2 the evidence channel rather than the representation is binding

**Ablation.** timeout parent, saturation parent, CEGAR parent given identical visible state

**Resource coordinates.** search_expansions; checker_calls; revision_work

**Cross-family test.** subtraction period defects and Nim combiner defects in one suite **Cross-domain test.** the same level ladder over proof-tactic and controlled-language failures

**Interactions.** COGNITIVE_SATURATION; OBSTRUCTION_DIAGNOSIS; REPRESENTATION_CHANGE

**Falsifier.** a fully-resourced verified-regime-revision parent matches minimum-sufficient-level accuracy AND false-escalation rate on an independently generated draw. Note this parent has ALREADY tied on the binary decision, so only the seven-level version is open.

**Disposition reason.** the BINARY jump/no-jump decision is already closed against a fully-resourced parent (ORION V1 zero-error Jump: protected incremental gap exactly zero). What replicated across ME-X2 V1 and V3 is narrower: the FALSE-ESCALATION ASYMMETRY (M 0 versus B5 21, then 0 versus 14) while overall accuracy was a loss and then a parity. The concept is therefore re-scoped to minimum-sufficient-level selection across seven levels, with false-escalation rate as the primary endpoint, because that is the only coordinate on which a residual has ever survived replication.

**Preserved terminals (do not re-litigate).**

- `REGIME_INVENTION_WITHOUT_INCREMENTAL_VALUE (ORION/research/extensions/orion-jump-recursive-atoms/zero_error_jump/JUMP_PROGRAMME_CLOSURE_V1.md)`
- `REPRESENTATION_INVENTION_NO_INCREMENTAL_VALUE; VERIFIED_REGIME_REVISION_PARENT matched ORION on every protected metric; ORION's protected incremental gap is exactly zero (ZERO_ERROR_JUMP_CLOSURE_V2.md)`
- `ME-X2 PARENT_SUFFICIENT (B5_DOMINATES): M 0.963 vs B5 0.983, exact p=0.0032 - the parent WON`
- `ME-X2 V3 THRESHOLD_NULL: parity on a fresh seed (+0.0017, p=0.845); the V1 loss did not replicate as a loss`
- `ME-X2 and V3 replicated asymmetry: M false escalations 0 vs B5 21, then 0 vs 14`
- `M_ALWAYS_ESCALATE_WHEN_STUCK ablation: 848 false escalations, 115 specification damages`
- `M4_FINITE_GOVERNED_JUMP_GREEN, but the extension was AUTHORED not invented`
- `M11 S5/S6 SUPPORTED at n=1 only`

**Signatures.** governed_representation_operator_evolution; bounded_recursive_self_improvement

**Reopen condition.** a confirmatory result requires worlds generated by a process independent of the policy's author; the present generator shares the policy's theory of what the defect is, which is the FAILURE_LEDGER pattern STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE and is recorded as such

### FIBRES_MULTISCALE_TRANSPORT

*ADAPT* · scientific status **PARENT_SUFFICIENT** · implementation `PILOT_IMPLEMENTED_THIS_TRANCHE` · paper role: P3 supporting; not a headline

**Definition.** Overlapping local knowledge spaces with typed correspondences, where transport composes warrants: Lambda(transported) = Lambda(source) tensor Lambda(correspondence).

**Explicitly not.** NOT a mandatory topology. NOT retained because the mathematics is attractive. The V1 development fibre, the observational indistinguishability class and the OCM scope fibre are three different objects and must not be conflated.

**Strongest parents.** ordinary database index; flat graph; hierarchical graph / lumpability (Kemeny-Snell); graph partitioning and label propagation; modular planning; learned routing; neural memory / retrieval

**Observable state.** k touched objects per query, index probes, transport records, stale transports after revocation **Trigger.** a query scoped to a family

**Mechanism.** scoped local lookup with dependency links, so that revocation of shared support marks exactly the transports that went stale **Information available.** family identity and the dependency graph; never the answer

**Positive family.** local fibre competence with cross-fibre bridges and shared support

**Negative twin.** unrelated fibres that must be untouched and unaffected

**Hostile.** a globally shared support whose revocation must NOT look local; an index built by scanning all N

**Ablation.** global scan with no index; index parent with no dependency tracking; cache parent storing positions

**Resource coordinates.** N_persistent_objects; k_touched_objects; index_probes; index_bytes; index_maintenance_work; persistent_state_bytes; query_cpu_seconds

**Cross-family test.** query work under growing unrelated distractor competence **Cross-domain test.** transport of a DISTINGUISH method from games to counterexample selection

**Interactions.** SPARSE_ACTIVE_SUBSPACE; REOPENING_LOCAL_REVISION; CONSOLIDATION

**Falsifier.** an ordinary index matches k(N) and query work, and also matches stale-transport detection after revocation

**Disposition reason.** query-work sparsity is almost certainly PARENT_SUFFICIENT; the only defensible residual is stale-transport detection after revocation, so the claim is narrowed to that

**Preserved terminals (do not re-litigate).**

- `M8_PARENT_SUFFICIENT_AT_THIS_SCALE (docs/provenance/M8_RECEIPT_V1.json)`
- `M8 language stream: fibres answered 6/18, 12 REFINE_REQUIRED, 0 transports`
- `P6_METHOD_FIBRE_FORMALISM_NARROWED (ORION/research/extensions/p6-method-fibres/)`
- `TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED (ORION-02 FiberGuard): the lexical control matched or beat the registered geometry in BOTH revival rounds`
- `MEG-09 multiscale navigation reduces to parent lumpability and intertwining (ORION-V2 ME_FRONTIER_F2_MULTISCALE_PARENT_REDUCTION_V1.md)`
- `KSO_REPRESENTATION_ABSTRACTION_V1.md §7: every organisation candidate's valid terminal is PARENT_SUFFICIENT`

**Signatures.** sparse_relevant_cognition; local_revision

**Reopen condition.** only a new pre-registered held-out study may revisit M8; the old receipt is not reinterpretable

### SPARSE_ACTIVE_SUBSPACE

*ADAPT* · scientific status **IMPLEMENTED_UNTESTED** · implementation `PILOT_IMPLEMENTED_THIS_TRANCHE` · paper role: P3 primary

**Definition.** A query-conditioned working set K(q) whose whole-query cost tracks k rather than N after charging index build, maintenance, routing, materialisation, refinement, verification, storage and failed searches.

**Explicitly not.** A sparse stored graph with dense all-row iteration is NOT sparse cognition. k is instrumented at the point of touch, never inferred from result-set size.

**Strongest parents.** database indexes and materialised views; personalised PageRank local partitioning (Andersen-Chung-Lang); approximate nearest neighbour; neural retrieval

**Observable state.** k, k/N, index_probes, index build and maintenance work, crossover query count **Trigger.** any query against a grown store

**Mechanism.** scoped index with charged construction; report CANNOT_CHECK for any path that can scan uninstrumented **Information available.** family identity and index structure

**Positive family.** frozen probe families at scales 1x/3x/10x/30x

**Negative twin.** global-scan ablation whose k must track N

**Hostile.** index construction that scanned all N; storage growth hiding cheap queries

**Ablation.** global scan; unindexed store

**Resource coordinates.** N_persistent_objects; k_touched_objects; index_probes; index_bytes; index_maintenance_work; persistent_state_bytes

**Cross-family test.** frozen probes held constant while unrelated competence grows **Cross-domain test.** deferred to CL-10

**Interactions.** FIBRES_MULTISCALE_TRANSPORT; CONSOLIDATION

**Falsifier.** k grows near-linearly in N, or the crossover query count is never reached within the registered lifetime

**Disposition reason.** reframed around the crossover query count, which is the only form of the claim that survives the index-construction hostile

**Preserved terminals (do not re-litigate).**

- `navigation_sparse.py is adjacency-sparse but its fixed point still updates every state row; it is not yet evidence for O(k) task cost`
- `default exact solve computes four dense restart fixed points`

**Signatures.** sparse_relevant_cognition

**Reopen condition.** if the indexed parent matches, report PARENT_SUFFICIENT on k(N) and keep only the revocation endpoint

### REUSABLE_METHOD_ACQUISITION

*KEEP* · scientific status **IMPLEMENTED_UNTESTED** · implementation `PILOT_IMPLEMENTED_THIS_TRANCHE` · paper role: P1 primary

**Definition.** A method is an object satisfying CL-D1: it compresses its source episodes strictly, its verified scope strictly exceeds its training support with certification beyond training magnitude, and the certifying checker is independent of it.

**Explicitly not.** NOT an answer cache. NOT similarity retrieval. Presence in memory is not use; a reuse claim needs an execution-trace witness.

**Strongest parents.** persistent memoisation across restarts; DreamCoder / Stitch library learning; Soar chunking; skill libraries with embedding retrieval; small neural model checkpointed across restarts

**Observable state.** MethodRecordV1 with description_bits, admissibility verdict and bits accounting **Trigger.** a set of checked solved episodes

**Mechanism.** induce the shortest consistent hypothesis in the registered language; admit only under CL-D1 **Information available.** the checked episodes and the registered language; never held-out labels

**Positive family.** periodic Grundy rules over subtraction families

**Negative twin.** a decoy consistent with training and wrong beyond it

**Hostile.** a matched-byte answer cache; a structural placebo drawn from the decoy pool

**Ablation.** A_removed, A_revoked, A_placebo, A_cache; the primary estimand is placebo minus live

**Resource coordinates.** search_expansions; checker_calls; persistent_state_bytes; acquisition_cpu_seconds

**Cross-family test.** a rule learned on one move set applied to another **Cross-domain test.** deferred to CL-8

**Interactions.** CONSOLIDATION; SCOPED_FAILURE_KNOWLEDGE

**Falsifier.** the placebo arm reproduces the effect, or persistent memoisation matches on positions beyond training magnitude

**Disposition reason.** this is the programme's base signature; without it nothing above it means anything

**Preserved terminals (do not re-litigate).**

- `M9_CANNOT_CHECK_FOR_SUPPORTED_AT_THIS_N (n=9, OCM-authored environments)`
- `Stitch abstraction result was a checked primitive alias, not useful-operator acquisition`
- `inc/square search slots 35->15 and 37->19 is a small library-learning mechanism, not general cognitive growth`

**Signatures.** causal_reusable_method_acquisition; persistent_restartable_competence

**Reopen condition.** none; this is the entry gate

### METHOD_COMPOSITION

*KEEP* · scientific status **THEORY_ONLY** · implementation `GAME_FAMILY_READY_MECHANISM_PENDING` · paper role: P2 primary

**Definition.** Two methods acquired from disjoint training families enable a fresh task requiring both, with no combined solution present in training.

**Explicitly not.** NOT a single method that happens to cover both families.

**Strongest parents.** meta-learning; program synthesis over a learned library; hierarchical planning

**Observable state.** two ReuseEventV1 records with distinct method ids on one task **Trigger.** a task in the SUBNIM family requiring a per-heap rule and a combiner

**Mechanism.** acquire the per-heap rule on one-heap subtraction and the combiner on Nim, then compose **Information available.** the two training streams, kept disjoint by construction

**Positive family.** SUBNIM(S,k): needs the SUB(S) Grundy rule and the XOR combiner

**Negative twin.** a family solvable by either method alone

**Hostile.** training that leaks a combined example

**Ablation.** remove A only, remove B only, remove both

**Resource coordinates.** search_expansions; checker_calls

**Cross-family test.** new move sets not seen in either training stream **Cross-domain test.** deferred

**Interactions.** REUSABLE_METHOD_ACQUISITION

**Falsifier.** removing either method leaves performance unchanged, i.e. the task never needed the composition

**Disposition reason.** SUBNIM makes composition structural rather than staged: neither training family contains the combined solution

**Preserved terminals (do not re-litigate).**

- `M7 RQ3 compositional_reuse CANNOT_CHECK (n below pre-registered minimum)`

**Signatures.** method_composition

**Reopen condition.** none

### REOPENING_LOCAL_REVISION

*KEEP* · scientific status **PARENT_SUFFICIENT** · implementation `IMPLEMENTED_IN_SRC_OCM` · paper role: P3 supporting

**Definition.** On a support change, exactly the dependency cone reopens; REOPEN is the liveness-changed part, RECHECK survives through alternative support, UNAFFECTED is the no-alarm control.

**Explicitly not.** NOT global recomputation. Locality that is guaranteed by task design is not evidence of locality.

**Strongest parents.** JTMS (Doyle 1979); ATMS label update (de Kleer 1986); self-adjusting computation (Acar); differential dataflow; provenance semirings

**Observable state.** cone size, stale survivors, collateral invalidations, recovery work **Trigger.** revocation or reinstatement of a support

**Mechanism.** dependency-closed impact cone with three-valued liveness **Information available.** the dependency graph and the revoked set

**Positive family.** local support revocation with a small true cone

**Negative twin.** unrelated objects that must stay live

**Hostile.** a genuinely global dependency cone, so locality is not guaranteed by task design

**Ablation.** global recomputation; index parent with no dependency tracking

**Resource coordinates.** revision_work; recovery_work; index_maintenance_work

**Cross-family test.** revocation across families in one store **Cross-domain test.** deferred

**Interactions.** FIBRES_MULTISCALE_TRANSPORT; SCOPED_FAILURE_KNOWLEDGE

**Falsifier.** a TMS parent matches cone exactness and cost, or the global-cone hostile shows locality was benchmark-imposed

**Disposition reason.** mechanism is proved exact; what is unmeasured is whether it buys anything a TMS parent does not

**Preserved terminals (do not re-litigate).**

- `M7 RQ1 ocm-no_revocation PARENT_SUFFICIENT (52/54 vs 53/54)`
- `KS-P1 retraction law PARENT_PRODUCT_OWNED`
- `M12 F stale 0, dependents reopened 3/3 but DESCRIPTIVE`

**Signatures.** local_revision

**Reopen condition.** a new pre-registered study with the global-cone hostile included

### RECURSIVE_DECOMPOSITION

*ADAPT* · scientific status **THEORY_ONLY** · implementation `PARTIAL_IN_SRC_OCM` · paper role: P3 supporting

**Definition.** A decomposition must declare subproblem identities, interfaces, shared assumptions, couplings, a recomposition rule, global obligations, and order or non-commutation constraints. Total solve work includes recomposition.

**Explicitly not.** NOT rewarded for producing more subproblems. A macro cell is a routing accelerator, never an authority source.

**Strongest parents.** dynamic programming; AND/OR search; hierarchical planning; operads and hypergraph categories (Fong-Spivak); Soar chunking; neural planning

**Observable state.** subproblem records, recomposition cost, depth, fragmentation count **Trigger.** a task whose state space factors

**Mechanism.** decompose only under a declared interface with a recomposition obligation **Information available.** the declared interfaces; never the global solution

**Positive family.** independent multi-heap games where per-heap decomposition is exact

**Negative twin.** coupled worlds where decomposition is harmful

**Hostile.** local solutions that do not glue globally; over-fragmentation; unbounded recursion depth

**Ablation.** flat search on the same task

**Resource coordinates.** search_expansions; composition_work; checker_calls

**Cross-family test.** decomposition learned on Nim applied to SUBNIM **Cross-domain test.** proof decomposition at CL-8

**Interactions.** METHOD_COMPOSITION; LOCAL_TO_GLOBAL_OBSTRUCTION

**Falsifier.** total work including recomposition exceeds flat search, or a coupled world shows decomposition is harmful and the machine still decomposes

**Disposition reason.** must be scored on total work including recomposition, and must include a coupled world where the right answer is not to decompose

**Preserved terminals (do not re-litigate).**

- `'learned recursive organisation remains unproved' (research/programme/ORION_CONCEPTS.md)`

**Signatures.** method_composition; cross_family_transfer

**Reopen condition.** none

### REPRESENTATION_CHANGE

*KEEP* · scientific status **THEORY_ONLY** · implementation `LANGUAGE_IMPLEMENTED_MECHANISM_PENDING` · paper role: P2/P3

**Definition.** Adoption of a new representation or operator vocabulary with transport, preservation obligations, an independent check and a measured benefit, driven by evidence rather than by benchmark identity. Requires a held-out world where the old and new representations disagree and the new one is correct.

**Explicitly not.** NOT selection from a two-item hand-picked menu. NOT justified by a plateau.

**Strongest parents.** learned embeddings and neural representation learners; CEGAR; version-space learning; MDL model selection

**Observable state.** RepresentationChangeV1 with held_out_discrimination and construction cost **Trigger.** a witnessed non-identifiability of the incumbent representation

**Mechanism.** exhibit a colliding pair, then adopt the minimum representation that separates it **Information available.** observed labels and the registered representation menu with its size

**Positive family.** token-total representation collides on Nim; heap-tuple separates

**Negative twin.** a world where the incumbent already identifies

**Hostile.** a deliberately misleading representation that fits training and fails held-out

**Ablation.** charge representation search and construction cost; compare to a neural representation learner

**Resource coordinates.** search_expansions; acquisition_cpu_seconds; persistent_state_bytes

**Cross-family test.** the same menu across subtraction and Nim families **Cross-domain test.** controlled-language interpretation at CL-9

**Interactions.** SEARCH_MORE_VS_JUMP; CONSOLIDATION

**Falsifier.** prior_bits shows the menu was small enough that the answer was given, not learned

**Disposition reason.** the combiner language contains five decoys that are provably indistinguishable from XOR on binary Grundy values, so the discrimination is structural

**Preserved terminals (do not re-litigate).**

- `M4 finite ceiling was reached with a SUPPLIED conjunction feature`

**Signatures.** governed_representation_operator_evolution

**Reopen condition.** none

### DISTINGUISH_DISCRIMINATING_QUERY

*ADAPT* · scientific status **PARENT_SUFFICIENT** · implementation `PARTIAL_IN_SRC_OCM` · paper role: P5 transport vehicle

**Definition.** Given live alternatives, allowed probes, a target decision and a budget, return a discriminating probe or CANNOT_CHECK.

**Explicitly not.** NOT a clarification heuristic. The operator name DISTINGUISH is not implemented anywhere in src/ocm; the built things are clarification and experiment selection.

**Strongest parents.** Bayesian experimental design; value of information; active learning; entropy / information gain; test cover and active diagnosis

**Observable state.** ProbeEventV1 with the probe chosen and the version-space reduction achieved **Trigger.** more than one surviving hypothesis and a non-empty probe set

**Mechanism.** choose the probe maximising guaranteed elimination net of cost **Information available.** the surviving set and probe costs

**Positive family.** version spaces where one probe halves the survivors

**Negative twin.** a probe set that cannot discriminate at any cost

**Hostile.** misleading probes, unequal costs, budget exhaustion distinct from structural ambiguity

**Ablation.** random probe; greedy confirmation

**Resource coordinates.** checker_calls; search_expansions; tool_calls

**Cross-family test.** Nim and subtraction probe families **Cross-domain test.** counterexample selection in mathematics; clarification in language

**Interactions.** SUBGOAL_FORMATION; COGNITIVE_SATURATION

**Falsifier.** an entropy or Bayesian design parent matches

**Disposition reason.** expected to be PARENT_SUFFICIENT; retained only as the cross-domain transport vehicle, where the claim is that the same frozen method moves domains, not that it beats entropy

**Preserved terminals (do not re-litigate).**

- `M10: entropy parent ties OCM 4/4 on experiment selection`
- `M7 RQ1 ocm-no_clarification PARENT_SUFFICIENT (52/54)`
- `Bayesian experimental-design parent not built -> CANNOT_CHECK`

**Signatures.** cross_domain_cognitive_transfer

**Reopen condition.** only under a new pre-registered study against a built Bayesian design parent

### SUBGOAL_FORMATION

*KEEP* · scientific status **THEORY_ONLY** · implementation `NOT_IMPLEMENTED` · paper role: P2

**Definition.** A recurring intermediate objective learned from solved episodes, together with a learned refusal condition for when not to invoke it.

**Explicitly not.** NOT a subgoal label supplied by the task representation. A method that never declines is a suspicious method.

**Strongest parents.** BFS/A* and hierarchical planning; options and hierarchical RL; model-based RL; Soar subgoaling plus chunking

**Observable state.** SubgoalEventV1 including refusals, weighted equally with invocations **Trigger.** a task where the optimal immediate action is insufficient

**Mechanism.** mine recurring intermediate states from solved traces; learn the invocation precondition **Information available.** solved traces; the exact planner is an oracle, never a policy donor

**Positive family.** key-door and bottleneck layouts sharing abstract structure

**Negative twin.** layouts where the old subgoal is unnecessary

**Hostile.** layouts where the old subgoal is actively harmful

**Ablation.** remove the subgoal; compare to A* and to model-based RL

**Resource coordinates.** search_expansions; wall_seconds; checker_calls

**Cross-family test.** same abstract structure, different geometry **Cross-domain test.** proof decomposition at CL-8

**Interactions.** DISTINGUISH_DISCRIMINATING_QUERY; RECURSIVE_DECOMPOSITION

**Falsifier.** the subgoal is recoverable from state features alone

**Disposition reason.** the refusal endpoint is what distinguishes it from options discovery

**Signatures.** method_composition; cross_family_transfer

**Reopen condition.** none

### NEGATIVE_TRANSFER_REFUSAL

*KEEP* · scientific status **CANNOT_CHECK** · implementation `IMPLEMENTED_IN_SRC_OCM` · paper role: P3 mandatory reported endpoint

**Definition.** Refuse transport when the target role differs from the source role, when outside authority, when the source is revoked, or when short-horizon help causes final harm; require an adapter when a binding is missing.

**Explicitly not.** NOT refusing everything difficult. Abstention rate is a reported endpoint, not an exclusion criterion.

**Strongest parents.** case-based reasoning; skill libraries with embedding retrieval; continual-learning transfer gates

**Observable state.** REFUSE_TRANSFER and ADAPTER_REQUIRED decisions with the role mismatch cited **Trigger.** a candidate transport into a new family

**Mechanism.** typed correspondence check before transport **Information available.** declared roles and authority; never target labels

**Positive family.** superficially similar but role-incompatible families

**Negative twin.** genuinely compatible families where refusal would be a false negative

**Hostile.** short-horizon benefit with final harm

**Ablation.** similarity-only routing

**Resource coordinates.** search_expansions; checker_calls

**Cross-family test.** the M9 transfer matrix extended to game families **Cross-domain test.** game to language transport

**Interactions.** SCOPED_FAILURE_KNOWLEDGE; FIBRES_MULTISCALE_TRANSPORT

**Falsifier.** a similarity-routing parent achieves the same precision with no false refusals

**Disposition reason.** harmful-transfer rate is mandatory in any transfer abstract, so this must be measured whether or not it is a residual

**Preserved terminals (do not re-litigate).**

- `M9 transfer matrix 14/14 as expected but milestone terminal is M9_CANNOT_CHECK_FOR_SUPPORTED_AT_THIS_N`
- `M7 RQ6 CANNOT_CHECK (n<40)`
- `M12 A negative transfer 7/7 vs 5/7 DESCRIPTIVE`

**Signatures.** safe_negative_transfer_refusal

**Reopen condition.** n at or above the pre-registered minimum in a fresh study

### CONSOLIDATION

*KEEP* · scientific status **THEORY_ONLY** · implementation `PARTIAL_IN_SRC_OCM` · paper role: P3

**Definition.** Fast capture, replay and comparison, regularity discovery, consolidation into a schema, retention of surprising residuals, archival of detail. Hard invariant: compression may not launder an epistemic distinction.

**Explicitly not.** NOT lossy summarisation. NOT permitted to mint warrant.

**Strongest parents.** DreamCoder / Stitch / Babble; e-graphs and egglog; hash-consing; Soar chunking; MDL

**Observable state.** mdl_delta, consolidation cost, rare-exception retention **Trigger.** accumulated episodes with a repeated fragment

**Mechanism.** MDL-gated schema formation with residual retention **Information available.** stored episodes only

**Positive family.** repeated periodic structure across move sets

**Negative twin.** a family with no repeated structure, where consolidation must decline

**Hostile.** a rare exception that consolidation would erase

**Ablation.** no consolidation; unconditional consolidation

**Resource coordinates.** index_maintenance_work; persistent_state_bytes; acquisition_cpu_seconds

**Cross-family test.** consolidated schema reused on a new move set **Cross-domain test.** deferred

**Interactions.** REPRESENTATION_CHANGE; SPARSE_ACTIVE_SUBSPACE

**Falsifier.** consolidation cost exceeds the search it saves, or a rare exception is lost

**Disposition reason.** the rare-exception hostile is the part no library-learning parent currently reports

**Preserved terminals (do not re-litigate).**

- `#70 deliverables AC-D1..D10 all unchecked`
- `KS-T12 lifecycle-safe consolidation stays OPEN`

**Signatures.** amortized_future_reasoning; sparse_relevant_cognition

**Reopen condition.** none

### OBSTRUCTION_DIAGNOSIS

*MERGE* · scientific status **CALIBRATED** · implementation `IMPLEMENTED_IN_SRC_OCM` · paper role: P2 within the escalation study

**Definition.** A four-valued navigation outcome FOUND / GAP_NOT_FOUND / OBSTRUCTION_WITNESSED / CANNOT_CHECK, where an obstruction certificate requires every registered lower alternative to have been tried with live warrants and failed, plus a ceiling witness.

**Explicitly not.** A timeout is never an obstruction. A missing retrieval is never an obstruction.

**Strongest parents.** JTMS/ATMS composed with spreading activation; CEGAR spurious-versus-real counterexample analysis

**Observable state.** ObstructionCertificate with the tried alternatives enumerated **Trigger.** failure to identify after lower alternatives are exhausted

**Mechanism.** require an exhibited witness before certifying an obstruction **Information available.** tried alternatives and their warrants

**Positive family.** the L4/L5 escalation worlds

**Negative twin.** the budget-exhaustion world

**Hostile.** an untried alternative; a dead warrant on the path

**Ablation.** certify obstruction on timeout instead

**Resource coordinates.** search_expansions; checker_calls

**Cross-family test.** across the escalation suite **Cross-domain test.** proof search obstruction

**Interactions.** SEARCH_MORE_VS_JUMP; COGNITIVE_SATURATION; SCOPED_FAILURE_KNOWLEDGE

**Falsifier.** a CEGAR parent distinguishes spurious from real with equal accuracy

**Disposition reason.** merged into SEARCH_MORE_VS_JUMP; it is that concept's witness condition rather than a separate mechanism

**Preserved terminals (do not re-litigate).**

- `KS-T19 checked; M11 KS-T98 SUPPORTED (exact)`
- `discrimination benchmark NAV-E5 not built`

**Signatures.** governed_representation_operator_evolution

**Reopen condition.** none

### LOCAL_TO_GLOBAL_OBSTRUCTION

*DROP* · scientific status **THEORY_ONLY** · implementation `NOT_IMPLEMENTED` · paper role: none

**Definition.** Local solutions consistent on overlaps that admit no global section; a global section requires an independent witness.

**Explicitly not.** NOT a claim that sheaf language adds power; the terminal for every organisation candidate is PARENT_SUFFICIENT by rule.

**Strongest parents.** CSP local consistency; ATMS nogoods; presheaves and sheaves (Robinson; Hansen-Ghrist)

**Observable state.** overlap consistency records with no admissible global assembly **Trigger.** pairwise-consistent local solutions

**Mechanism.** detect the obstruction and refuse the global claim **Information available.** local solutions and overlap constraints

**Positive family.** a decomposable game world with a genuine gluing failure

**Negative twin.** a world where local solutions do glue

**Hostile.** a world where CSP arc-consistency already finds the failure

**Ablation.** global search

**Resource coordinates.** search_expansions; composition_work

**Cross-family test.** deferred **Cross-domain test.** deferred

**Interactions.** RECURSIVE_DECOMPOSITION

**Falsifier.** ordinary CSP consistency parents find every obstruction the mechanism finds

**Disposition reason.** dropped from the executable programme for now: #93 requires CSP parents to be exhausted first, and no positive case is yet distinguishable from arc consistency. Retained as theory backlog under the §19 decision filter.

**Preserved terminals (do not re-litigate).**

- `KSO_REPRESENTATION_ABSTRACTION_V1.md §7: nothing in that document may be cited as a residual`

**Signatures.** none

**Reopen condition.** a positive case that arc consistency provably cannot detect

### SELF_MODEL_AND_FAILURE_DIAGNOSIS

*KEEP* · scientific status **CANNOT_CHECK** · implementation `IMPLEMENTED_IN_SRC_OCM` · paper role: P7 only if earned

**Definition.** A distribution over responsible cognitive layers D0-D8 from counterfactual evidence, plus the minimum sufficient layer; self-statements carry self-model authority only and never raise object authority.

**Explicitly not.** NOT metacognitive narration. The ablation channel is currently oracle-provided, so this is not yet the machine's own counterfactual reasoning.

**Strongest parents.** parameter search over router and revocation; reflection-retry over skills; a learned failure classifier over traces with the same candidate channel (named, not yet built); fault localisation; interventional causal inference

**Observable state.** layer distribution, minimum sufficient layer, obstruction certificate **Trigger.** a diagnosed cognitive failure

**Mechanism.** counterfactual ablation over layers with a minimum-sufficient rule **Information available.** ablation run outcomes

**Positive family.** S0-S7 planted causes

**Negative twin.** a failure with no architectural cause

**Hostile.** historical failures replayed rather than re-executed

**Ablation.** parameter search only; reflection-retry only

**Resource coordinates.** wall_seconds; search_expansions

**Cross-family test.** all three M9 environments **Cross-domain test.** deferred

**Interactions.** SEARCH_MORE_VS_JUMP; GOVERNED_SELF_REORGANIZATION

**Falsifier.** a learned trace classifier reaches the same layer accuracy

**Disposition reason.** kept but explicitly gated: the oracle-provided ablation channel must be replaced by the machine's own counterfactual runs before any claim

**Preserved terminals (do not re-litigate).**

- `M11 diagnosis 7/7 but head-to-head row is DESCRIPTIVE (n=7, no pre-registered rate test)`
- `diagnostic accuracy on real historical failures CANNOT_CHECK`
- `M11_MIXED_CLAIM_BY_CLAIM`

**Signatures.** bounded_recursive_self_improvement

**Reopen condition.** machine-generated counterfactual channel, n>=40, all three environments

### GOVERNED_SELF_REORGANIZATION

*ADAPT* · scientific status **CANNOT_CHECK** · implementation `IMPLEMENTED_IN_SRC_OCM` · paper role: P7 only if earned

**Definition.** A self-change proposal at class C0-C6 with a pre-outcome prediction digest, shadow execution, independent assurance, external adoption, migration of affected state, monitoring and rollback. C6 is a recommendation packet only.

**Explicitly not.** Self-modification is NOT itself success. The machine may propose C6 and may never self-authorize it. One successful edit is adaptation, not recursive improvement.

**Strongest parents.** AutoML and NAS; meta-learning; program repair; evolutionary search; Soar chunking; parameter search; reflection-retry

**Observable state.** proposal records with adopted flag, assurance outcomes, rollback artifacts **Trigger.** a diagnosed obstruction at an architectural layer

**Mechanism.** minimum-sufficient change class with frozen predictions and external adoption **Information available.** its own failure records; never the held-out suite

**Positive family.** planted architectural faults

**Negative twin.** faults repairable at C0 where a broad rewrite must be refused

**Hostile.** a proposer that has seen the held-out tasks; self-approval

**Ablation.** AutoML-style configuration search with the same budget

**Resource coordinates.** acquisition_cpu_seconds; revision_work; recovery_work

**Cross-family test.** deferred **Cross-domain test.** deferred

**Interactions.** SELF_MODEL_AND_FAILURE_DIAGNOSIS; SEARCH_MORE_VS_JUMP

**Falsifier.** an AutoML or NAS parent with the same budget produces the same improvement

**Disposition reason.** reframed as a LATE-STAGE DEPENDENT hypothesis requiring at least two generations F0->F1->F2 with disjoint development, acceptance, future-transfer and successor task sets; a single edit is explicitly not evidence

**Preserved terminals (do not re-litigate).**

- `M11_MIXED_CLAIM_BY_CLAIM`
- `adopted 7/7 and broad rewrites refused 2/2 but n=7 descriptive`
- `C6 constitutional self-change NOT ATTEMPTED by design`
- `#38 reopens all seven historical adoption cells`
- `'Our recursive research process is not evidence that OCM can improve itself'`

**Signatures.** bounded_recursive_self_improvement

**Reopen condition.** two generations with protected evaluation and an AutoML parent

### SHADOW_EVALUATION_AND_ROLLBACK

*MERGE* · scientific status **CAUSALLY_SUPPORTED** · implementation `IMPLEMENTED_IN_SRC_OCM` · paper role: P7 method section

**Definition.** Object-level non-interference during shadow execution, verified on the ledger head as well as the object state hash; rollback restores the component table exactly and revokes stamped evidence while leaving the object digest unchanged.

**Explicitly not.** NOT a canary that merely observes. Non-interference is checked, not assumed.

**Strongest parents.** shadow and canary deployment; transactional rollback; sham-surgery controls

**Observable state.** assurance outcomes, ledger head equality, rollback exactness **Trigger.** a self-change proposal awaiting adoption

**Mechanism.** shadow run with head-and-state comparison and an owned rollback cache **Information available.** the proposal and the shadow environment

**Positive family.** S1-S7 proposals

**Negative twin.** a proposal that should be rejected

**Hostile.** a runner that admits evidence during the shadow run

**Ablation.** no shadow; adopt directly

**Resource coordinates.** wall_seconds; storage_writes; recovery_work

**Cross-family test.** deferred **Cross-domain test.** deferred

**Interactions.** GOVERNED_SELF_REORGANIZATION

**Falsifier.** ordinary transactional rollback provides the same guarantee at the same cost

**Disposition reason.** merged into GOVERNED_SELF_REORGANIZATION as its assurance step; it has no independent scientific endpoint

**Preserved terminals (do not re-litigate).**

- `assurance 7/7 across S1-S7`
- `rollback exact 7/7 and in M12 phase G in all three orderings`

**Signatures.** bounded_recursive_self_improvement

**Reopen condition.** none

### AUTHORITY_NON_AMPLIFICATION

*KEEP* · scientific status **CAUSALLY_SUPPORTED** · implementation `IMPLEMENTED_IN_SRC_OCM` · paper role: method section invariant

**Definition.** Without an additional bridge certificate, the sound authority scope of a composition is contained in the intersection of the component scopes; the meet never raises object authority.

**Explicitly not.** NOT a security property. It is an epistemic conservation statement.

**Strongest parents.** Blackwell sufficiency; ATMS scoped justifications; access-control lattices

**Observable state.** authority lattice meets; refusal of self-approval **Trigger.** any composition or self-statement

**Mechanism.** lattice meet with an explicit bridge requirement **Information available.** component authorities

**Positive family.** composition chains

**Negative twin.** a bridge certificate that legitimately widens scope

**Hostile.** a self-description asserted as object authority

**Ablation.** allow the join instead of the meet

**Resource coordinates.** none

**Cross-family test.** n/a **Cross-domain test.** n/a

**Interactions.** WARRANT_CONSERVATION

**Falsifier.** none; this is an invariant, not a hypothesis

**Disposition reason.** an invariant the programme must not violate, not a competitive claim; it earns no paper of its own

**Preserved terminals (do not re-litigate).**

- `'Self-statements never carry object authority' SUPPORTED (exact); mutant_self_description_as_authority caught`

**Signatures.** none

**Reopen condition.** none

### WARRANT_CONSERVATION

*KEEP* · scientific status **PARENT_SUFFICIENT** · implementation `IMPLEMENTED_IN_SRC_OCM` · paper role: method section constraint

**Definition.** Any saving from holding a coarser representation is a relocation of state into later access, never a free reduction. Aggregation, majority, similarity and compression never mint warrant.

**Explicitly not.** NOT a claim that coarsening is useless; a claim that its cost reappears.

**Strongest parents.** minimal sufficient statistic (Fisher; Lehmann-Scheffe; Blackwell); partition lattice (Birkhoff); Hartley 1928

**Observable state.** resource vectors before and after coarsening **Trigger.** any abstraction or summarisation

**Mechanism.** charge deferred access cost at the point it is incurred **Information available.** the resource ledger

**Positive family.** summarised stores re-queried at detail

**Negative twin.** a query family that genuinely needs no detail

**Hostile.** reporting query savings while omitting later descent cost

**Ablation.** omit the descent charge and observe the apparent free lunch

**Resource coordinates.** persistent_state_bytes; active_bytes_per_query; index_maintenance_work

**Cross-family test.** n/a **Cross-domain test.** n/a

**Interactions.** CONSOLIDATION; SPARSE_ACTIVE_SUBSPACE

**Falsifier.** none; L4 already refutes the matched-resource reading

**Disposition reason.** this is a constraint the scaling study must respect, and it is the reason the crossover query count exists

**Preserved terminals (do not re-litigate).**

- `OCM_LANE_201_TERMINAL_V1.md PARENT_SUFFICIENT; CERTIFIED_REPRESENTATION_RESIDUAL NOT_EARNED; L4 conservation refutes the matched-resource reading`

**Signatures.** none

**Reopen condition.** none

### RESOURCE_RESPONSIBILITY

*KEEP* · scientific status **CAUSALLY_SUPPORTED** · implementation `IMPLEMENTED_IN_SRC_OCM` · paper role: method section invariant

**Definition.** A non-compensatory resource vector compared only by Pareto dominance, never collapsed to a scalar inside the core; cognitive productivity is reported per coordinate with the worst coordinate disclosed alongside any favourable one.

**Explicitly not.** NOT a weighted score. There is no scalar OCM score and no scalar productivity score.

**Strongest parents.** multi-objective dominance; time-bounded Kolmogorov complexity / Levin's Kt

**Observable state.** the full resource vector per arm per query **Trigger.** every measured comparison

**Mechanism.** Pareto reporting with mandatory worst-coordinate disclosure **Information available.** the meter

**Positive family.** any arm comparison

**Negative twin.** an arm that wins one coordinate and loses another

**Hostile.** one favourable coordinate hiding losses elsewhere

**Ablation.** scalar collapse (planted mutant)

**Resource coordinates.** all

**Cross-family test.** n/a **Cross-domain test.** n/a

**Interactions.** none

**Falsifier.** none; an invariant

**Disposition reason.** the worst-coordinate disclosure rule is the structural answer to the strongest presentation-level attack

**Preserved terminals (do not re-litigate).**

- `OCM_LANE_202_TERMINAL_V1.md TRADEOFF_FRONTIER_ONLY; TRANSFORMER_EQUIVALENT_UNDER_MATCHED_RESOURCES CANNOT_CHECK`
- `mutant_scalar_collapse planted and caught`

**Signatures.** none

**Reopen condition.** none

### EPISTEMIC_HYSTERESIS

*ADAPT* · scientific status **CANNOT_CHECK** · implementation `IMPLEMENTED_IN_SRC_OCM` · paper role: P3 supporting

**Definition.** Restoring withdrawn support restores exactly what is justified, and reinstatement at a lower layer is preferred to a rewrite that would also pass assurance.

**Explicitly not.** The term hysteresis does not occur in the repository; the mechanism is reinstatement-versus-relearning and is named as such here to avoid importing a metaphor.

**Strongest parents.** ATMS label recomputation; belief revision (AGM)

**Observable state.** reinstatement layer chosen versus the minimum available **Trigger.** restoration of a previously revoked support

**Mechanism.** prefer the minimum layer that restores justification **Information available.** the dependency graph and the restored support

**Positive family.** revoke then restore a shared premise

**Negative twin.** a case where relearning genuinely is minimal

**Hostile.** a D7 rewrite that passes assurance but is not minimum

**Ablation.** always relearn

**Resource coordinates.** recovery_work; revision_work

**Cross-family test.** across game families in one store **Cross-domain test.** deferred

**Interactions.** REOPENING_LOCAL_REVISION; SCOPED_FAILURE_KNOWLEDGE

**Falsifier.** an ATMS parent recomputes labels at the same cost

**Disposition reason.** renamed away from the hysteresis metaphor to reinstatement-versus-relearning, which is what is actually measured

**Preserved terminals (do not re-litigate).**

- `M11 S5 SUPPORTED at n=1`
- `M12 A relearned 6/6 vs parent 3/6 DESCRIPTIVE`
- `M7 RQ3 relearned CANNOT_CHECK (n<40)`

**Signatures.** local_revision

**Reopen condition.** n at or above the pre-registered minimum

### EPISTEMIC_TENSION_DETECTION

*DROP* · scientific status **THEORY_ONLY** · implementation `PARTIAL_IN_SRC_OCM` · paper role: none

**Definition.** Query-specific reaction surprise relative to a background fixed point, so that generic hubs do not dominate.

**Explicitly not.** NOT novelty seeking. The PROPAGATED model is registered but NOT adopted; the default stays UNIFORM.

**Strongest parents.** Andersen-Chung-Lang contribution vectors; inverse document frequency; Bayesian surprise

**Observable state.** per-query surprise scores **Trigger.** a query against a background

**Mechanism.** query-conditioned surprise excluding teleport mass **Information available.** the graph and the query seeds

**Positive family.** the 12/50 EXTRACT misses in M2

**Negative twin.** hub-dominated queries where surprise must not fire

**Hostile.** a generic hub masquerading as a surprise

**Ablation.** uniform background

**Resource coordinates.** navigation_work; index_probes

**Cross-family test.** deferred **Cross-domain test.** deferred

**Interactions.** DISTINGUISH_DISCRIMINATING_QUERY

**Falsifier.** IDF reproduces the ranking

**Disposition reason.** dropped from the executable ladder: the seed-count lemma proved a no-op, the default model is unadopted, and no positive case is distinguishable from IDF. Theory backlog under the §19 filter.

**Preserved terminals (do not re-litigate).**

- `the seed-count lemma proved a NO-OP; the lever the M2 receipt named changes nothing (check_seed_count_lemma)`
- `PROPAGATED model registered but not adopted`

**Signatures.** none

**Reopen condition.** a positive case IDF provably cannot rank

### THOUGHT_EXPERIMENT_COUNTERFACTUAL

*MERGE* · scientific status **CANNOT_CHECK** · implementation `PARTIAL_IN_SRC_OCM` · paper role: P7

**Definition.** One-layer counterfactual ablation runs used as the evidence channel for diagnosis.

**Explicitly not.** The channel is currently ORACLE-PROVIDED, not machine-generated. That is the whole gap.

**Strongest parents.** interventional causal inference; fault localisation; ablation studies

**Observable state.** ablation outcomes and the layer distribution they induce **Trigger.** a diagnosed failure

**Mechanism.** the machine designs and runs its own ablations **Information available.** its own architecture description

**Positive family.** planted causes

**Negative twin.** a failure with no single responsible layer

**Hostile.** the machine choosing ablations that confirm a prior diagnosis

**Ablation.** oracle channel versus machine-generated channel

**Resource coordinates.** wall_seconds; search_expansions

**Cross-family test.** deferred **Cross-domain test.** deferred

**Interactions.** SELF_MODEL_AND_FAILURE_DIAGNOSIS

**Falsifier.** machine-generated ablations do not reach oracle-channel accuracy

**Disposition reason.** merged into SELF_MODEL_AND_FAILURE_DIAGNOSIS as its evidence channel; the open question is identical

**Preserved terminals (do not re-litigate).**

- `M11 §5: the ablation channel is oracle-provided`

**Signatures.** bounded_recursive_self_improvement

**Reopen condition.** machine-generated channel built

### CONCEPT_OPERATOR_INVENTION

*DROP* · scientific status **THEORY_ONLY** · implementation `NOT_IMPLEMENTED` · paper role: none

**Definition.** Proposing an operator or concept not present in the registered basis.

**Explicitly not.** Selecting from a registered menu is NOT invention. L5 is currently a level label with no mechanism.

**Strongest parents.** DreamCoder library learning; anti-unification and grammar induction; program synthesis

**Observable state.** none; not implemented **Trigger.** operator insufficiency witnessed at L4

**Mechanism.** deferred **Information available.** deferred

**Positive family.** deferred

**Negative twin.** deferred

**Hostile.** an invented operator that is a renaming of an existing primitive

**Ablation.** deferred

**Resource coordinates.** none

**Cross-family test.** deferred **Cross-domain test.** deferred

**Interactions.** SEARCH_MORE_VS_JUMP

**Falsifier.** every invented operator is expressible as a composition of registered primitives

**Disposition reason.** deferred by the programme's own parents document until a distinct obstruction, mechanism and parent-exceeding result exist; classified as a contingent extension not needed for a first paper

**Preserved terminals (do not re-litigate).**

- `MULTIPLE_CONCEPT_ATOMS_REQUIRED (ORION/research/extensions/orion-jump-recursive-atoms/JUMP_ATOM_PILOT_CLOSURE_V1.md): 'system proposes a new named primitive' is not an ORION-specific discriminator`
- `MULTIPLE_TENSION_ATOMS_REQUIRED and MULTIPLE_IMAGINATION_ATOMS_REQUIRED (same file)`
- `RECURSIVE_ATOM_STUDY_CALCULUS_FROZEN: the programme ended with FEWER claimed primitives than it began with`
- `'autonomous representation invention has not been demonstrated'`
- `the Stitch result was a checked primitive alias`
- `PARENTS.md defers representation invention`

**Signatures.** governed_representation_operator_evolution

**Reopen condition.** an L4 witness the registered basis provably cannot repair

### PERSISTENT_RESTARTABLE_COMPETENCE

*KEEP* · scientific status **CAUSALLY_SUPPORTED** · implementation `TEMPLATE_EXISTS_IN_MATH_LANGUAGE_LEARNING_V1` · paper role: P1 method section

**Definition.** A scored reuse is admissible only after the acquiring OS process exited, a new process with a different PID read the serialized state, and the state digest matched.

**Explicitly not.** In-process simulated restart is design evidence only and is never confirmatory.

**Strongest parents.** checkpoint-and-reload of any learner, including a neural one; crash-consistency testing in storage systems

**Observable state.** pid before and after, state digest before and after, exit status **Trigger.** any reuse claim

**Mechanism.** hardened subprocess boundary with digest comparison **Information available.** the serialized state only

**Positive family.** acquire in process A, reuse in process B

**Negative twin.** a no-invoke arm reaching the same status with zero reuses

**Hostile.** an in-memory cache surviving the boundary; a fixture import in the reusing process

**Ablation.** reset-between-task arm

**Resource coordinates.** storage_reads; storage_writes; wall_seconds

**Cross-family test.** every rung **Cross-domain test.** every rung

**Interactions.** REUSABLE_METHOD_ACQUISITION

**Falsifier.** a checkpointed neural learner shows the same acquire-restart-reuse profile

**Disposition reason.** the custody discipline is what makes every other claim in the programme legible; a neural parent gets exactly the same boundary

**Preserved terminals (do not re-litigate).**

- `test_unary_method_restart.py asserts pid difference, reaping, group absence, and zero prior uses`

**Signatures.** persistent_restartable_competence

**Reopen condition.** none

### MULTI_GENERATION_IMPROVEMENT

*ADAPT* · scientific status **THEORY_ONLY** · implementation `NOT_IMPLEMENTED` · paper role: P7 only if earned

**Definition.** F0 learns from failures and proposes F1; F1 is evaluated on protected tasks and operates on fresh tasks; F1 then receives new failures and proposes F2, over disjoint development, acceptance, future-transfer, successor-generation and successor-acceptance task sets.

**Explicitly not.** One successful architecture edit is adaptation, NOT recursive improvement. The research process that produced OCM is not evidence that OCM improves itself.

**Strongest parents.** AutoML and NAS; meta-learning; evolutionary search; recursive-improvement systems; the matched WholeSystemParent

**Observable state.** per-generation task quality, information required, search work, revision locality, k/N, failure recurrence, false-jump rate **Trigger.** accumulated failures at an architectural layer

**Mechanism.** the governed self-reorganization lifecycle, iterated **Information available.** its own failure records; never the acceptance or successor-acceptance sets

**Positive family.** two generations with measured improvement

**Negative twin.** a generation that should not change anything

**Hostile.** configuration search dressed as cognition

**Ablation.** AutoML parent with the same budget and the same task sets

**Resource coordinates.** acquisition_cpu_seconds; query_cpu_seconds; persistent_state_bytes; revision_work

**Cross-family test.** deferred **Cross-domain test.** deferred

**Interactions.** GOVERNED_SELF_REORGANIZATION; SELF_MODEL_AND_FAILURE_DIAGNOSIS

**Falsifier.** an AutoML or NAS parent matches the generation-over-generation curve

**Disposition reason.** promoted to an explicit late-stage endpoint with a two-generation minimum and five disjoint task sets; not attemptable before Phases A-G produce stable measurements

**Preserved terminals (do not re-litigate).**

- `INTERACTION_ONLY_RESIDUAL_FROZEN (ORION/research/extensions/meta-orion-recursive-scientific-evolution/): the residual is interaction correctness plus future value, NOT self-improvement`
- `RSE.T2 FINITE_INFORMATION_CEILING_VERIFIED: a current-summary-only policy is capped at 1/2; full history and compact typed lineage reach 1.0`
- `Self-ORION P5 NO_TERMINAL_UNDER_FROZEN_RULES: FULL_T7 at 12/96; ADAS, DGM and ADIAS unavailable and correctly NOT replaced by weak proxies`
- `FULL_OCM_RESIDUAL_SUPPORTED is scoped to one inferential family (A conversations, n=54); every other residual is descriptive`
- `CANNOT_CHECK_MATCHED_PARENT against a frontier foundation-model parent`
- `#143 §13: the standalone synthetic ladder is pilot/design evidence only`

**Signatures.** bounded_recursive_self_improvement

**Reopen condition.** Phases A-G complete with stable measurements
