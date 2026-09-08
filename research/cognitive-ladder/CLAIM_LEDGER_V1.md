# CLAIM_LEDGER_V1

**GENERATED FILE — edit `claim_ledger.py`, then run `python claim_ledger.py`.**

PUB-D1 of #144. The load-bearing columns are the last two. Every result is recorded with the sentence it licenses and the sentence it does not, because the way a programme like this fails is not fabricated data but a real result described one level too strongly.

| claim | level | evidence | result |
|---|---|---|---|
| C1-SPARSE-LOOKUP | L0 | E1 | PARENT_SUFFICIENT |
| C2-EXACT-REVOCATION | L0 | E1 | The machine arm's cone is exact at every scale; local stays at 2 while the shared cone grows with N |
| C3-SCOPED-FAILURE | L1 | E2 | The governed store avoids all 640 avoidable work units with zero false exclusions, zero missed reopenings and zero broken-shut |
| C4-MINIMUM-ESCALATION | L1 | E2 | Calibration only |
| C5-RELEVANCE-DISCOVERY | L0 | E1 | INDEX_MAINTENANCE_DOMINATES |
| C6-CAUSE-DIAGNOSIS | L1 | E2 | ACCUMULATION_RESIDUAL_CONFINED_TO_PROBE_COST |
| C7-DEPENDENCY-DISCOVERY | L0 | E1 | LEAVE_ONE_OUT_DISCOVERY_INCOMPLETE |
| C8-ESCALATION-INDEPENDENT | L1 | E2 | GENERATOR_ARTIFACT_CONFIRMED, then PARENT_SUFFICIENT_WITHIN_REGISTERED_MARGIN |
| C9-PLANTED-DEFECT-BENCHMARKS-MISLABEL | L2 | E2 | The generator-intent label agrees with the independent oracle on only 53 |
| C10-WITNESS-ELIMINATES-FALSE-ESCALATION | L2 | E2 | Zero false escalations for both principled arms, against 232 for the saturation and refinement policies and 245 for the timeout policy |
| C11-ABLATION-ATTRIBUTION-INCOMPLETE | L2 | E1 | Between 16 |
| C12-RELEVANCE-KEY-DECAYS-WITH-SCALE | L1 | E1 | The hand-specified prefix goes from max bucket 1 and collision rate 0 at N=17 to max bucket 20 and collision rate 0 |
| C13-DEMAND-RESCUES-PERSISTENCE-NOT-EAGER-ACQUISITION | L1 | E2 | Crossovers are real but bounded |

## C1-SPARSE-LOOKUP

**Claim.** Task-relevant computation touches a small fraction of a growing store.

**Level.** L0 · **Evidence class.** E1

**Hypothesis.** k stays small while N grows, at matched answer correctness.

**Strongest parent.** an ordinary database index keyed on the supplied family identity

**Experiment.** `research/cognitive-ladder/run_scaling.py, scales 1x/3x/10x/30x` · **Replication.** none

**Result.** PARENT_SUFFICIENT. The index parent matches the machine arm exactly on k, k/N, query work and answered-correctly at every scale. The machine arm's persistent bytes are strictly larger, because its reverse-index edges are charged.

**Limitation.** The index key was supplied by the catalogue, so cheap lookup is a property of the key. Sparse execution on the real runtime is untested; its navigation still computes dense fixed points.

**Permitted wording.** An ordinary index reproduces the sparse-query behaviour exactly, so sparse lookup under a supplied relevance key is not evidence of cognition.

**Forbidden wording.** _The machine queries only a tiny fraction of its knowledge._

## C2-EXACT-REVOCATION

**Claim.** Withdrawing a support invalidates exactly the objects that depended on it.

**Level.** L0 · **Evidence class.** E1

**Hypothesis.** The observed cone equals the true cone; local revocation stays local while a genuinely global one does not.

**Strongest parent.** a truth-maintenance store, or an O(N) scan over declared supports

**Experiment.** `run_scaling.py revocation arms; local and globally-shared triggers` · **Replication.** none

**Result.** The machine arm's cone is exact at every scale; local stays at 2 while the shared cone grows with N. Every arm without dependency edges observes the empty cone.

**Limitation.** The dependency graph was built from the declarations that populated the store, so exactness is by construction. The gap over the index parent is a difference in default configuration, not achievability: an audited O(N) support scan recovers both cones and was not run. Protocol attack A9 is unanswered.

**Permitted wording.** Given a declared dependency graph, revocation is exact and its cost tracks the true cone rather than the store size.

**Forbidden wording.** _The machine discovers what its conclusions depend on._

## C3-SCOPED-FAILURE

**Claim.** Negative knowledge is scoped to assumptions, so it transfers and reopens correctly.

**Level.** L1 · **Evidence class.** E2

**Hypothesis.** Exclusions keyed on the assumption set avoid repeated dead ends without closing permanently shut.

**Strongest parent.** a full-strength nogood store with assumption-set keying and dependency-directed retraction

**Experiment.** `run_failure.py, seven worlds including five hostiles` · **Replication.** none

**Result.** The governed store avoids all 640 avoidable work units with zero false exclusions, zero missed reopenings and zero broken-shut. The nogood parent avoids the same 640 and ties exactly on four of seven worlds, separating only by four false exclusions on the three worlds where the failure's cause carries no information about correctness.

**Limitation.** Every arm was handed the correct cause by the world. Whether a machine can tell an evaluator defect from a genuine refutation is untested here; that is experiment E2.

**Permitted wording.** Filtering exclusions by the cause of a failure avoids false exclusions that a cause-blind nogood store makes, on worlds where the cause is known.

**Forbidden wording.** _The machine learns from failure better than truth maintenance does._

## C4-MINIMUM-ESCALATION

**Claim.** The machine escalates to the minimum sufficient level and refuses to escalate on exhaustion.

**Level.** L1 · **Evidence class.** E2

**Hypothesis.** Requiring an exhibited obstruction witness yields minimum-level accuracy with zero false escalations.

**Strongest parent.** an exact repair planner taking the cheapest repair that admits a fit; and, historically, a fully-resourced verified-regime-revision parent

**Experiment.** `run_escalation.py, nine registered worlds plus a commitment-derived draw` · **Replication.** none

**Result.** Calibration only. The governed policy separates from three naive parents and from the repair planner on the worlds where the evidence channel rather than the representation is binding.

**Limitation.** The world generator instantiates the defect the policy is built to detect, which is the failure-ledger pattern STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE. The binary jump decision is separately closed against a fully-resourced parent with a protected incremental gap of exactly zero.

**Permitted wording.** On worlds constructed to carry a known defect, a witness requirement prevents the false escalations that timeout and saturation policies make.

**Forbidden wording.** _The machine reliably diagnoses when its representation is insufficient._

## C5-RELEVANCE-DISCOVERY

**Claim.** The machine discovers which part of memory is relevant without being told.

**Level.** L0 · **Evidence class.** E1

**Hypothesis.** A discovered indexing feature keeps k small at matched correctness, and its adequacy degrades with N unless revised.

**Strongest parent.** a content-addressed inverted index on a hand-specified prediction prefix; nearest-neighbour retrieval

**Experiment.** `E1, run_subspace.py` · **Replication.** none

**Result.** INDEX_MAINTENANCE_DOMINATES. With the family key withheld, the hand-specified prediction prefix BEATS the discovering arm wherever it stays adequate (query work 3.8 vs 8.6 at 1x) because it pays no search. Its adequacy then breaks with growth: max bucket 1 at N=17 rising to 20 at N=481, collision rate 0 to 0.98. The discovering arm separates on k and query work only after the fixed key breaks, and its lifetime index bill is not repaid by the registered 50-query stream at 30x.

**Limitation.** The feature language, the world and the searching arm share an author, and the arm reproduces the scorer's own smallest-adequate-feature procedure. The index-cost reading is specific to a search that rescans the whole language on every re-index; an incremental search is not run. A colliding hand-specified key is slower, never wrong.

**Permitted wording.** A fixed relevance key degrades measurably as a store grows, and noticing that it has degraded costs more than the queries it saves at the scales tested.

**Forbidden wording.** _The machine knows what is relevant._

## C6-CAUSE-DIAGNOSIS

**Claim.** The machine infers why an attempt failed, from probes it chooses and pays for.

**Level.** L1 · **Evidence class.** E2

**Hypothesis.** Diagnosis accuracy at lower cumulative probe cost than a stateless policy, because a diagnosis once made is not re-paid within its scope.

**Strongest parent.** a fixed near-optimal decision tree over the same probes; exhaustive probing

**Experiment.** `E2, run_diagnosis.py` · **Replication.** none

**Result.** ACCUMULATION_RESIDUAL_CONFINED_TO_PROBE_COST. With the cause withheld, the governed policy, the exhaustive prober and the hand-authored decision tree all reach 59/59, against a constant-predictor baseline of 0.288 and a retry-once heuristic at 0.441. The governed greedy rule provably reproduces the decision tree's ordering, so probe ordering is parent-owned. The entire residual is 42 probe units of 573, 7.3%.

**Limitation.** The residual is memoisation of one boolean per checker and scope; giving the decision tree the same cache would close it, and this experiment does not claim the residual survives that. The response table is deterministic, so accuracy is not a live coordinate between the three sufficient arms. Probe semantics are authored, so this is table inversion under a cost constraint, not evidence that a machine can learn what a probe means.

**Permitted wording.** Inferring the cause of a failure from chosen probes is solved by a fixed decision tree; persistence buys only the cost of not re-establishing a cached fact within a scope.

**Forbidden wording.** _The machine understands its own failures._

## C7-DEPENDENCY-DISCOVERY

**Claim.** The machine discovers which evidence its conclusions actually rest on.

**Level.** L0 · **Evidence class.** E1

**Hypothesis.** A learned dependency graph reaches high precision and recall against a leave-one-out oracle, and its up-front discovery cost is repaid after a measurable number of revocations.

**Strongest parent.** full recomputation; a co-occurrence heuristic; the gifted declared-supports ceiling

**Experiment.** `E3, run_depend.py` · **Replication.** none

**Result.** LEAVE_ONE_OUT_DISCOVERY_INCOMPLETE. No parent was sufficient on all coordinates: the gifted declared-supports ceiling reaches only 0.61 to 0.74 precision and the co-occurrence heuristic misses about 8% of edges. But the learned arm is not a winner either: the cheap parents beat it on total work by two to four orders of magnitude at any realistic revocation count, and it crosses over against full recomputation only after 5 revocations and against the lazy learner after 27 to 39.

**Limitation.** Leave-one-out cannot see redundant support, which is a limitation of the discovery method and not of the measurement.

**Permitted wording.** Discovering dependencies eagerly by single-element ablation is incomplete at a measured rate and, among arms that meet matched correctness, is dominated by re-deriving them lazily on demand until roughly thirty revocations have accumulated.

**Forbidden wording.** _The machine knows what it believes and why._

## C8-ESCALATION-INDEPENDENT

**Claim.** Minimum-sufficient escalation holds on worlds not built around the policy's taxonomy.

**Level.** L1 · **Evidence class.** E2

**Hypothesis.** Accuracy survives blind perturbation with ground truth from exhaustive repair search rather than generator intent.

**Strongest parent.** the exact repair planner

**Experiment.** `E4, run_escalation_independent.py` · **Replication.** this IS the replication that C4 lacks

**Result.** GENERATOR_ARTIFACT_CONFIRMED, then PARENT_SUFFICIENT_WITHIN_REGISTERED_MARGIN. The same unmodified policy falls from 70/70 on the old generator to 1736/2000 (86.8%) on blindly perturbed worlds levelled by an independent repair oracle. Its lead over the fully-resourced repair planner collapses from 20 points to 0.7, inside the pre-registered 2% margin. Errors are almost entirely underreach: 261 under, 3 over.

**Limitation.** Removing the generator circularity does not remove the ladder's authorship: the repair lattice and the escalation levels still share an author, so #144 §11's independently authored validation subset remains outstanding.

**Permitted wording.** The escalation policy's earlier advantage over a fully-resourced planner was an artifact of a generator that planted the defect the policy was built to detect; on independent worlds the two are equivalent.

**Forbidden wording.** _The machine's escalation policy generalises._

## C9-PLANTED-DEFECT-BENCHMARKS-MISLABEL

**Claim.** A benchmark generator that plants a defect type produces ground-truth labels that are frequently wrong about what the task actually requires.

**Level.** L2 · **Evidence class.** E2

**Hypothesis.** The label implied by which edit was applied diverges from the minimum repair that actually restores identifiability, and the divergence is large.

**Strongest parent.** None applicable: this measures a construction method, not a system. The check is exhaustive search over the repair lattice, which in a finite world is ground truth by definition.

**Experiment.** `E4, run_escalation_independent.py, generator-intent audit over 2000 worlds` · **Replication.** cross-checked against brute-force minimisation over the full 2^8 repair powerset

**Result.** The generator-intent label agrees with the independent oracle on only 53.4% of worlds. It OVERSTATES the required level 759 times and UNDERSTATES it 173 times. On two-perturbation worlds the true minimum lands strictly above both nominal intents 9 times and strictly below both once. Every disagreement is a world on which any arm would have been scored against a wrong answer.

**Limitation.** Shown for one perturbation menu on one family of exactly solvable worlds. The mechanism, that one repair can fix two defects or that neither defect alone determines the requirement, is general; the 53.4% is not a constant.

**Permitted wording.** In a benchmark whose worlds are built by planting a known defect, the planted defect is not a safe label for what the world requires: here it was wrong on nearly half of worlds, in both directions.

**Forbidden wording.** _Benchmark generators are unreliable._

## C10-WITNESS-ELIMINATES-FALSE-ESCALATION

**Claim.** Requiring an exhibited obstruction before escalating eliminates the false escalations the commonly used triggers make.

**Level.** L2 · **Evidence class.** E2

**Hypothesis.** Policies that escalate on timeout, on a stalled search, or on any counterexample escalate when they should not, at a rate a witness requirement drives to zero.

**Strongest parent.** an exact repair planner, which also reaches zero, by exhaustively testing repairs rather than by requiring a witness

**Experiment.** `E4, 2000 blindly perturbed worlds, independent repair oracle` · **Replication.** replicates the programme's known 0-vs-21 and 0-vs-14 asymmetry from two earlier studies, now at n=2000 on worlds built around no policy taxonomy

**Result.** Zero false escalations for both principled arms, against 232 for the saturation and refinement policies and 245 for the timeout policy. The principled arms are also 22 accuracy points ahead of all three. The naive policies collapse everything above L1 onto representation change.

**Limitation.** The exact repair planner reaches zero as well, so the witness requirement is not what buys this; being principled at all does. That planner needs an enumerable repair lattice, which real settings rarely provide, so the practically meaningful comparison is against the three heuristics.

**Permitted wording.** Escalating on exhaustion, on a stalled search, or on any counterexample produces a false escalation on roughly one world in eight; requiring either an exhibited obstruction or an exhaustive repair test drives that to zero at no cost in accuracy.

**Forbidden wording.** _The governed policy knows when to change representation._

## C11-ABLATION-ATTRIBUTION-INCOMPLETE

**Claim.** Discovering what a conclusion depends on by removing one piece of evidence at a time is structurally incomplete, at a measurable rate.

**Level.** L2 · **Evidence class.** E1

**Hypothesis.** Where two pieces of evidence each suffice alone, single-element ablation finds neither necessary and reports no dependency at all.

**Strongest parent.** joint-witness search over subsets, which finds it and costs exponentially more; a co-occurrence heuristic, which catches it by over-linking

**Experiment.** `E3, run_depend.py, leave-one-out oracle audited against a joint-witness oracle` · **Replication.** measured at four scales, N = 80, 160, 400, 800

**Result.** Between 16.3% and 25% of methods have support no single-element ablation can see. An arm scoring perfect precision and recall against the leave-one-out oracle still leaves a stale survivor under multi-block revocation, because its graph is not composable. The heuristic that understands nothing about dependency catches the case by over-linking.

**Limitation.** The rate depends on how much redundancy the evidence stream carries, which is a property of the world. The mechanism is general; the percentage is not.

**Permitted wording.** Leave-one-out attribution reports no dependency wherever support is redundant, and a graph built that way is not safe under simultaneous withdrawal.

**Forbidden wording.** _Dependency discovery does not work._

## C12-RELEVANCE-KEY-DECAYS-WITH-SCALE

**Claim.** Any fixed key for deciding what is relevant degrades as the store grows.

**Level.** L1 · **Evidence class.** E1

**Hypothesis.** A hand-specified retrieval feature adequate at small N develops collisions at larger N, so query work rises even though the index is unchanged.

**Strongest parent.** the same index rebuilt on a richer feature, which is what the discovering arm does and what any practitioner would do on noticing

**Experiment.** `E1, run_subspace.py, scales 1x/3x/10x/30x with the family key withheld` · **Replication.** none

**Result.** The hand-specified prefix goes from max bucket 1 and collision rate 0 at N=17 to max bucket 20 and collision rate 0.98 at N=481, with query work rising from 3.8 to 23.6. The fixed-feature ablation degrades further, k rising from 3 to 102 and query work from 8.6 to 207. Correctness never degrades: a colliding key is slower, never wrong.

**Limitation.** Four scales spanning N = 17 to 481 is a small range to read a trend from, and the feature language is authored. Noticing the decay and re-indexing cost more than it saved at the largest scale tested.

**Permitted wording.** A relevance key adequate at one store size is not adequate at thirty times that size, and the cost of the degradation appears in query work rather than in correctness.

**Forbidden wording.** _The machine adapts its representation as it learns._

## C13-DEMAND-RESCUES-PERSISTENCE-NOT-EAGER-ACQUISITION

**Claim.** Raising the density of tasks that essentially require earlier structure makes persistence pay, and does not make eager acquisition pay.

**Level.** L1 · **Evidence class.** E2

**Hypothesis.** If reuse opportunity is the binding constraint on amortization, a density sweep should produce a crossover against the strongest parent somewhere below density one.

**Strongest parent.** a deferred-induction parent: retains the evidence a derivation produced, and defers induction itself until demand is proven. It shares the machine's mechanism and differs only in trigger.

**Experiment.** `E7, run_rho.py, eleven densities, two discovery costs, six arms` · **Replication.** none; the density-zero row reproduces the prior negatives, which is an internal consistency check rather than a replication

**Result.** Crossovers are real but bounded. Against lazy re-derivation and against memoization the machine wins from density 0.05 upward, and the crossover point rises with discovery cost as predicted. Against the deferred-induction parent there is NO crossover at any density up to the realised maximum of 0.875, at either discovery cost. Density zero reproduced the negatives, so the sweep is valid rather than void.

**Limitation.** The density is set by hand and says nothing about the density of any real task ecology. The realised maximum is 0.875 rather than 1.0, because the donor tasks that make structure acquirable can never themselves be essential. The lazy gap saturates at one avoided derivation per family rather than compounding with the horizon. The deferred parent is cheap here only because evidence is perfectly retainable, which will not hold everywhere.

**Permitted wording.** Absent reuse opportunity explains why persisting was worthless, but not why acquiring eagerly was worse than acquiring on demand; the second is a question about acquisition policy rather than about the ecology or the architecture.

**Forbidden wording.** _Given enough reuse opportunity, the machine amortizes its structure._
