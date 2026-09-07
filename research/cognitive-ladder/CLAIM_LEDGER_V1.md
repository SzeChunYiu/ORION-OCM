# CLAIM_LEDGER_V1

**GENERATED FILE — edit `claim_ledger.py`, then run `python claim_ledger.py`.**

PUB-D1 of #144. The load-bearing columns are the last two. Every result is recorded with the sentence it licenses and the sentence it does not, because the way a programme like this fails is not fabricated data but a real result described one level too strongly.

| claim | level | evidence | result |
|---|---|---|---|
| C1-SPARSE-LOOKUP | L0 | E1 | PARENT_SUFFICIENT |
| C2-EXACT-REVOCATION | L0 | E1 | The machine arm's cone is exact at every scale; local stays at 2 while the shared cone grows with N |
| C3-SCOPED-FAILURE | L1 | E2 | The governed store avoids all 640 avoidable work units with zero false exclusions, zero missed reopenings and zero broken-shut |
| C4-MINIMUM-ESCALATION | L1 | E2 | Calibration only |
| C5-RELEVANCE-DISCOVERY | pending | pending | _pending_ |
| C6-CAUSE-DIAGNOSIS | pending | pending | _pending_ |
| C7-DEPENDENCY-DISCOVERY | pending | pending | _pending_ |
| C8-ESCALATION-INDEPENDENT | pending | pending | _pending_ |

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

**Level.** pending · **Evidence class.** pending

**Hypothesis.** A discovered indexing feature keeps k small at matched correctness, and its adequacy degrades with N unless revised.

**Strongest parent.** a content-addressed inverted index on a hand-specified prediction prefix; nearest-neighbour retrieval

**Experiment.** `E1, run_subspace.py` · **Replication.** none

**Result.** pending

**Limitation.** pending

**Permitted wording.** pending

**Forbidden wording.** _The machine knows what is relevant._

## C6-CAUSE-DIAGNOSIS

**Claim.** The machine infers why an attempt failed, from probes it chooses and pays for.

**Level.** pending · **Evidence class.** pending

**Hypothesis.** Diagnosis accuracy at lower cumulative probe cost than a stateless policy, because a diagnosis once made is not re-paid within its scope.

**Strongest parent.** a fixed near-optimal decision tree over the same probes; exhaustive probing

**Experiment.** `E2, run_diagnosis.py` · **Replication.** none

**Result.** pending

**Limitation.** pending

**Permitted wording.** pending

**Forbidden wording.** _The machine understands its own failures._

## C7-DEPENDENCY-DISCOVERY

**Claim.** The machine discovers which evidence its conclusions actually rest on.

**Level.** pending · **Evidence class.** pending

**Hypothesis.** A learned dependency graph reaches high precision and recall against a leave-one-out oracle, and its up-front discovery cost is repaid after a measurable number of revocations.

**Strongest parent.** full recomputation; a co-occurrence heuristic; the gifted declared-supports ceiling

**Experiment.** `E3, run_depend.py` · **Replication.** none

**Result.** pending

**Limitation.** Leave-one-out cannot see redundant support, which is a limitation of the discovery method and not of the measurement.

**Permitted wording.** pending

**Forbidden wording.** _The machine knows what it believes and why._

## C8-ESCALATION-INDEPENDENT

**Claim.** Minimum-sufficient escalation holds on worlds not built around the policy's taxonomy.

**Level.** pending · **Evidence class.** pending

**Hypothesis.** Accuracy survives blind perturbation with ground truth from exhaustive repair search rather than generator intent.

**Strongest parent.** the exact repair planner

**Experiment.** `E4, run_escalation_independent.py` · **Replication.** this IS the replication that C4 lacks

**Result.** pending

**Limitation.** pending

**Permitted wording.** pending

**Forbidden wording.** _The machine's escalation policy generalises._
