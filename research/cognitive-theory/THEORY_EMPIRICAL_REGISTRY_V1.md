# THEORY_EMPIRICAL_REGISTRY_V1

**GENERATED FILE — edit `registry_data.py`, then run `python registry.py`.**

GUO-D1 of [#145](https://github.com/SzeChunYiu/ORION-OCM/issues/145). No theory claim may enter
manuscript prose without a row here, and every row names a concrete rung of #143 able to kill it.

This registry is written the unusual way round. Most are populated with statements someone hopes to
prove, and the status column stays `OPEN` for years. This one leads with the statements the
programme has already **refuted**, because those were the load-bearing ones and they turned out not
to be. A registry whose refuted rows are missing is a wish list.

Verification routes, per #145 §5: `V1_FORMAL_PROOF`, `V2_EXACT_COMPUTATION` over a complete finite
universe, `V3_PROSPECTIVE_EMPIRICAL`. Each row declares exactly one primary route.


## Status board

| theory | status | route | falsifying rung |
|---|---|---|---|
| TH-01-SPARSE-IS-COGNITIVE | **REFUTED** | V2 | #143 CL-6 / lane E-scaling |
| TH-03-FIXED-RELEVANCE-KEY-IS-SCALE-STABLE | **REFUTED** | V2 | #143 CL-6 / lane E1 |
| TH-04-LEAVE-ONE-OUT-IS-COMPLETE | **REFUTED** | V2 | #143 CL-6 / lane E3 |
| TH-06-PLANTED-DEFECT-LABELS-ARE-VALID | **REFUTED** | V2 | #143 CL-3 / lane E4 |
| TH-07-WITNESS-REQUIREMENT-IS-NECESSARY | **REFUTED** | V3 | #143 CL-3 / lane E4 |
| TH-09-FLAT-FRAGMENT-DISCOVERY | **REFUTED** | V2 | #143 CL-1 / research/math-language-learning-v1 |
| TH-11-FAILURE-LEARNING-IS-DERIVED | **PARENT_SUFFICIENT** | V3 | #143 CL-2 / lane failure pilot and E2 |
| TH-02-DECLARED-DEPENDENCY-LOCALITY | **PARENT_OWNED** | V1 | #143 CL-6 / lane E-scaling |
| TH-08-UNPRINCIPLED-TRIGGERS-FALSE-ESCALATE | **SUPPORTED_AT_SCOPE** | V3 | #143 CL-3 / lane E4 |
| TH-05-SUPPORT-FAMILY-DISCOVERY | **OPEN** | V2 | #143 CL-6 / lane E6 |
| TH-10-STEP-LEVEL-DISCOVERY | **OPEN** | V2 | #143 CL-1 / lane E5 |
| TH-13-FIELD-AFFECTS-DISCOVERABILITY | **OPEN** | V2 | #143 CL-1 to CL-3 / #145 GUO-D5 |
| TH-12-PRIMITIVE-PRESSURE-CONVERGES | **NOT_YET_TESTABLE** | V3 | #143 CL-7 through CL-10 |

## Rows

### TH-01-SPARSE-IS-COGNITIVE — REFUTED

> Touching a small fraction of a growing store, at matched correctness, is a signature of cognitive organisation rather than of ordinary filing.

**Scope.** finite competence stores addressed by a supplied family key, N up to about 2000

**Assumptions.** the relevance key is available at query time

**Field.** flat competence store, family-keyed · **Operator basis.** SELECT_RELEVANT

**Resource model.** instrumented per-object touches; index build and maintenance charged separately

**Predicted observable.** k, k/N and query work versus an ordinary index parent — **direction:** the machine arm separates from the index parent on at least one coordinate

**Route.** V2_EXACT_COMPUTATION · **Falsifying rung.** #143 CL-6 / lane E-scaling

**Strongest parent.** an ordinary database index keyed on the supplied family identity

**Causal ablation.** global-scan arm with k equal to N · **Negative twin.** cache parent, sparsest of all arms and unable to answer

**Falsifier.** the index parent matches on every coordinate

**Evidence.** results/SCALING_PILOT_V1.json: exact match on k, k/N, query work and correctness at every scale; the machine arm's persistent bytes are strictly larger

**Reopen condition.** only under a relevance key the machine had to discover, which is TH-03

### TH-03-FIXED-RELEVANCE-KEY-IS-SCALE-STABLE — REFUTED

> A relevance key adequate at one store size remains adequate as the store grows.

**Scope.** prediction-prefix keys over periodic rule stores, N from 17 to 481

**Assumptions.** the key is fixed at design time

**Field.** flat competence store, family-keyed · **Operator basis.** SELECT_RELEVANT

**Resource model.** collision rate, maximum bucket, query work, index build and maintenance

**Predicted observable.** collision rate of the hand-specified key across the scale sweep — **direction:** collision rate stays near zero

**Route.** V2_EXACT_COMPUTATION · **Falsifying rung.** #143 CL-6 / lane E1

**Strongest parent.** the same index rebuilt on a richer feature

**Causal ablation.** fixed-feature arm that never re-indexes · **Negative twin.** a store that grows only in already-distinguished directions

**Falsifier.** collision rate rising materially with N

**Evidence.** results/SUBSPACE_E1_V1.json: collision rate 0 to 0.98 and maximum bucket 1 to 20 from N=17 to N=481, while correctness never moved because a colliding key is slower and never wrong. Noticing the decay cost more than it saved at the largest scale

**Reopen condition.** an incremental re-index search, not run here, may change the cost side

### TH-04-LEAVE-ONE-OUT-IS-COMPLETE — REFUTED

> Removing one piece of evidence at a time identifies everything a conclusion depends on.

**Scope.** induced periodic rules over evidence blocks, N from 80 to 800

**Assumptions.** support is non-redundant

**Field.** typed object graph with declared support edges · **Operator basis.** REVISE / CHECK

**Resource model.** re-inductions charged; precision and recall against a powerset oracle

**Predicted observable.** fraction of methods whose support is invisible to single-element ablation — **direction:** near zero

**Route.** V2_EXACT_COMPUTATION · **Falsifying rung.** #143 CL-6 / lane E3

**Strongest parent.** joint-witness search over subsets; a co-occurrence heuristic

**Causal ablation.** simultaneous withdrawal of two individually redundant supports · **Negative twin.** a method with a single genuine support, where the method is exact

**Falsifier.** a measurable population of methods with redundant support

**Evidence.** results/DEPEND_E3_V1.json: between 16.3% and 25% of methods have support no single-element ablation can see. An arm at perfect precision and recall against its own leave-one-out oracle still left a stale survivor under multi-block revocation

**Reopen condition.** closed as stated; the successor statement is TH-05

### TH-06-PLANTED-DEFECT-LABELS-ARE-VALID — REFUTED

> In a benchmark whose worlds are built by planting a known defect, the planted defect is a valid label for what the world requires.

**Scope.** escalation worlds under a nine-item perturbation menu, n=2000

**Assumptions.** at most two simultaneous perturbations

**Field.** registered repair lattice over representation, operators and formulation · **Operator basis.** RE-REPRESENT / EXPAND

**Resource model.** not applicable; this is a construction-validity statement

**Predicted observable.** agreement between the planted-defect label and the minimum repair recovered by exhaustive search over the repair lattice — **direction:** high agreement

**Route.** V2_EXACT_COMPUTATION · **Falsifying rung.** #143 CL-3 / lane E4

**Strongest parent.** none applicable; exhaustive repair search is ground truth by definition in a finite world

**Causal ablation.** not applicable · **Negative twin.** zero-perturbation worlds, where both labels agree trivially

**Falsifier.** material disagreement between planted intent and minimum repair

**Evidence.** results/ESCALATION_INDEPENDENT_E4_V1.json: agreement on 53.4% of worlds, overstating the requirement 759 times and understating it 173 times. One repair can fix two defects; neither defect alone determines the requirement

**Reopen condition.** the mechanism is general; the percentage is menu-specific and would need re-measuring for a different perturbation menu

### TH-07-WITNESS-REQUIREMENT-IS-NECESSARY — REFUTED

> Requiring an exhibited obstruction is what prevents false escalation, as distinct from any other principled trigger.

**Scope.** 2000 blindly perturbed worlds levelled by an independent repair oracle

**Assumptions.** the repair lattice is enumerable

**Field.** registered repair lattice · **Operator basis.** RE-REPRESENT under CHECK

**Resource model.** false escalations and accuracy at matched information

**Predicted observable.** false escalation rate of the witness policy versus an exact repair planner — **direction:** the witness policy is strictly better

**Route.** V3_PROSPECTIVE_EMPIRICAL · **Falsifying rung.** #143 CL-3 / lane E4

**Strongest parent.** an exact repair planner testing each repair in cost order

**Causal ablation.** timeout, saturation and counterexample-refinement policies · **Negative twin.** worlds needing no escalation at all

**Falsifier.** the planner also reaches zero false escalations

**Evidence.** results/ESCALATION_INDEPENDENT_E4_V1.json: both principled arms reach zero false escalations. The witness requirement is not what buys it. What survives is the weaker and still useful TH-08

**Reopen condition.** in settings where the repair lattice is not enumerable, the planner is unavailable and the comparison changes

### TH-09-FLAT-FRAGMENT-DISCOVERY — REFUTED

> Reusable methods can be discovered by mining repeated flat surface fragments from solved episodes.

**Scope.** checked unary-language proof episodes

**Assumptions.** useful structure recurs at the surface level

**Field.** signed-clause proof DAG · **Operator basis.** CONSOLIDATE / GENERALIZE_METHOD

**Resource model.** candidate pool size, admitted methods, fresh-task search

**Predicted observable.** size of the admitted method pool — **direction:** non-empty

**Route.** V2_EXACT_COMPUTATION · **Falsifying rung.** #143 CL-1 / research/math-language-learning-v1

**Strongest parent.** anti-unification; Stitch-style corpus compression; DreamCoder library induction

**Causal ablation.** the repeated-support gate itself · **Negative twin.** episodes with genuinely no shared structure

**Falsifier.** an empty pool despite independently checked sound fragments

**Evidence.** research/math-language-learning-v1/ASSAY-ACQUISITION-DIAGNOSIS.md: 21 attempts, three independently checked essential fragments, all singletons, terminal NO_METHOD_ACQUIRED. The stated cause is that flat queried fragments differ while the intermediate dependency step recurs

**Reopen condition.** closed as stated; the successor statement is TH-10

### TH-11-FAILURE-LEARNING-IS-DERIVED — PARENT_SUFFICIENT

> Failure learning is not primitive: it decomposes into CHECK-failure, REVISE and CONSOLIDATE, and a truth-maintenance parent therefore reproduces it.

**Scope.** seven worlds with the failure cause supplied, and 59 episodes with it withheld

**Assumptions.** the cause taxonomy is registered in advance

**Field.** typed object graph with declared support edges · **Operator basis.** CHECK + REVISE + CONSOLIDATE

**Resource model.** repeated wasted work, false exclusions, missed reopenings, probe cost

**Predicted observable.** whether a nogood or decision-tree parent matches the governed store — **direction:** it matches

**Route.** V3_PROSPECTIVE_EMPIRICAL · **Falsifying rung.** #143 CL-2 / lane failure pilot and E2

**Strongest parent.** a full-strength nogood store; a fixed near-optimal probe decision tree

**Causal ablation.** cause-blind exclusion; task-identity keying · **Negative twin.** a checker defective in one scope and sound in another

**Falsifier.** a coordinate on which no parent reproduces the behaviour

**Evidence.** results/FAILURE_PILOT_V1.json: the nogood parent ties on four of seven worlds and avoids all 640 avoidable work units. results/DIAGNOSIS_E2_V1.json: the governed greedy rule provably reproduces the hand-authored decision tree ordering; the residual is 42 probe units of 573 and is memoisation

**Reopen condition.** a setting where probe semantics must be learned rather than authored

### TH-02-DECLARED-DEPENDENCY-LOCALITY — PARENT_OWNED

> Given declared dependencies, revocation cost tracks the true dependency cone rather than the store size, and a genuinely global withdrawal is not disguised as local.

**Scope.** declared support graphs, N up to about 2000

**Assumptions.** every dependency is declared at admission time

**Field.** typed object graph with declared support edges · **Operator basis.** REVISE / REOPEN

**Resource model.** cone size, revision work, index maintenance

**Predicted observable.** observed cone versus true cone for a local and a globally shared trigger — **direction:** cone exact in both cases; local constant in N, global growing in N

**Route.** V1_FORMAL_PROOF · **Falsifying rung.** #143 CL-6 / lane E-scaling

**Strongest parent.** truth maintenance; an audited O(N) scan over declared supports

**Causal ablation.** arm with dependency edges removed · **Negative twin.** revocation of evidence that was never load-bearing

**Falsifier.** a cone that stays small when the true dependency is global

**Evidence.** results/SCALING_PILOT_V1.json: exact at every scale, local cone constant at 2, shared cone growing 21/61/201/601. Exactness is by construction because the graph was declared; the audited O(N) scan parent recovers both cones and was not run

**Reopen condition.** under discovered rather than declared dependencies, which is TH-04 and TH-05

### TH-08-UNPRINCIPLED-TRIGGERS-FALSE-ESCALATE — SUPPORTED_AT_SCOPE

> Escalating on exhaustion, on a stalled search, or on any counterexample produces false escalation at a material rate that a principled trigger removes at no accuracy cost.

**Scope.** 2000 blindly perturbed worlds levelled by an independent repair oracle

**Assumptions.** ground truth is the minimum sufficient repair level

**Field.** registered repair lattice · **Operator basis.** RE-REPRESENT under CHECK

**Resource model.** false escalations, missed escalations, exact-match accuracy

**Predicted observable.** false escalation counts across five policies — **direction:** zero for principled policies, materially positive for the three heuristics

**Route.** V3_PROSPECTIVE_EMPIRICAL · **Falsifying rung.** #143 CL-3 / lane E4

**Strongest parent.** the exact repair planner, which also reaches zero

**Causal ablation.** the three heuristic policies under identical visible state · **Negative twin.** zero-perturbation worlds, where all five policies are perfect

**Falsifier.** a heuristic policy reaching zero false escalations

**Evidence.** results/ESCALATION_INDEPENDENT_E4_V1.json: 0 for both principled arms against 232, 232 and 245 for saturation, refinement and timeout, with 22 accuracy points on top. Replicates a 0-versus-21 and 0-versus-14 asymmetry recorded earlier in the programme

**Reopen condition.** an independently authored world family, still outstanding under #144 §11

### TH-05-SUPPORT-FAMILY-DISCOVERY — OPEN

> The correct object of dependency discovery is the family of minimal support sets, and it can be identified under a bounded intervention budget by adaptive selection more cheaply than by exhaustive group ablation.

**Scope.** small evidence sets where the powerset oracle is exactly computable

**Assumptions.** interventions are available and charged

**Field.** typed object graph with declared support edges · **Operator basis.** DISTINGUISH / PROBE + REVISE

**Resource model.** interventions spent to reach a given support-family precision and recall

**Predicted observable.** interventions versus adaptive, random and exhaustive selection — **direction:** adaptive selection approaches the exhaustive ceiling at materially lower cost

**Route.** V2_EXACT_COMPUTATION · **Falsifying rung.** #143 CL-6 / lane E6

**Strongest parent.** ATMS minimal-environment labelling, which is expected to be sufficient when handed the justifications and is parent-owned since 1986

**Causal ablation.** random group ablation under the same budget · **Negative twin.** a family where no evidence is load-bearing

**Falsifier.** ATMS given the same interventions matches the adaptive arm

**Evidence.** lane E6 in progress

**Reopen condition.** not applicable while open

### TH-10-STEP-LEVEL-DISCOVERY — OPEN

> Latent reusable structure that is invisible at the surface is recoverable at the level of proof steps, by anti-unification over normalised steps plus semantic-equivalence clustering, and survives persistence, restart and causal invocation.

**Scope.** propositional clause worlds where flat fragments are pairwise distinct by construction

**Assumptions.** the recurring object is a parameterised resolution step

**Field.** signed-clause proof DAG · **Operator basis.** CONSOLIDATE + RE-REPRESENT

**Resource model.** discovery cost, fresh-task search, checker calls, persistent bytes

**Predicted observable.** schemas admitted, and fresh-task work against the reset arm — **direction:** non-empty pool, and work reduction that disappears under method removal

**Route.** V2_EXACT_COMPUTATION · **Falsifying rung.** #143 CL-1 / lane E5

**Strongest parent.** DreamCoder-style library induction and Stitch-style compression, both of which can in principle find step-level structure if the traces expose it

**Causal ablation.** remove the discovered schema and re-run the fresh tasks · **Negative twin.** false-common-pattern schemas that recur by chance and do not help held-out tasks

**Falsifier.** library learning finds the same schemas, or no schema survives independent checking

**Evidence.** lane E5 in progress

**Reopen condition.** not applicable while open

### TH-13-FIELD-AFFECTS-DISCOVERABILITY — OPEN

> The choice of field organisation materially changes how easily reusable methods are discovered, how small an operator basis suffices, and what exact revision costs.

**Scope.** matched exact tasks under at least three field organisations

**Assumptions.** information is matched across fields

**Field.** flat store, typed graph, hypergraph, fibred field, TMS substrate · **Operator basis.** the same registered operator contracts across fields

**Resource model.** the full lifetime vector of #145 §9

**Predicted observable.** method discovery rate, operator basis size, revision cost per field — **direction:** no universal winner is assumed; a Pareto family is an admissible result

**Route.** V2_EXACT_COMPUTATION · **Falsifying rung.** #143 CL-1 to CL-3 / #145 GUO-D5

**Strongest parent.** a flat relational store, which is the simplest and must be beaten on total cost

**Causal ablation.** same tasks, same operators, field swapped · **Negative twin.** a task family where field structure is irrelevant

**Falsifier.** the flat store matches every field on every coordinate

**Evidence.** not started; this is the next tranche after E5 and E6

**Reopen condition.** not applicable while open

### TH-12-PRIMITIVE-PRESSURE-CONVERGES — NOT_YET_TESTABLE

> As materially different domains are added, the number of genuinely new primitive operators required trends toward zero while learned macros continue to grow.

**Scope.** not yet testable: the programme has one domain family

**Assumptions.** an operator basis has been frozen

**Field.** undetermined · **Operator basis.** undetermined

**Resource model.** new primitives admitted per domain versus new macros admitted

**Predicted observable.** the primitive-pressure curve of #145 §10 — **direction:** declining

**Route.** V3_PROSPECTIVE_EMPIRICAL · **Falsifying rung.** #143 CL-7 through CL-10

**Strongest parent.** production systems, ACT-R production compilation, library learning

**Causal ablation.** not yet designed · **Negative twin.** a domain that requires a genuinely new primitive

**Falsifier.** persistent non-zero primitive pressure across held-out domains

**Evidence.** none; recorded so that the curve is instrumented from the first real run rather than reconstructed afterwards, per #145 GUO-D7

**Reopen condition.** testable once a basis is frozen and a second domain family exists
