# INCIDENT_INTAKE_V1

**GENERATED FILE — edit `incident_intake.py`, then run `python incident_intake.py`.**

Executable causal intake for the six development incidents of [#149](https://github.com/SzeChunYiu/ORION-OCM/issues/149), whose incident table is one for one the findings of this lane.

#149 warns that summary-only observations cannot certify a causal localization, that a prose claim about a cached parent is not a measured cached-parent trace, and that traces must never be fabricated from summaries. Every number below is read out of a receipt at run time and each receipt is bound by the sha256 of its bytes. Supplying a trace is not the same as certifying a diagnosis, so each binding carries a `does_not_certify` note.

**5 of 6 incidents have executable intake in this lane.**

| incident | challenge | status | receipt |
|---|---|---|---|
| **F1** | No reusable methods | NOT_SUPPLIED_BY_THIS_LANE | — |
| **F2** | Fixed keys become dense | EXECUTABLE_INTAKE_SUPPLIED | `SUBSPACE_E1_V1.json` |
| **F3** | Index maintenance fails to amortize | EXECUTABLE_INTAKE_SUPPLIED_WITH_SHARED_RECEIPT | `SUBSPACE_E1_V1.json` |
| **F4** | Redundant supports missed | EXECUTABLE_INTAKE_SUPPLIED | `DEPEND_E3_V1.json` |
| **F5** | Apparent diagnosis residual disappears | EXECUTABLE_INTAKE_SUPPLIED | `DIAGNOSIS_E2_V1.json` |
| **F6** | Authored labels disagree with independent checking | EXECUTABLE_INTAKE_SUPPLIED | `ESCALATION_INDEPENDENT_E4_V1.json` |

## F1 — Unary acquisition funnel and original checked traces

**Challenge (#149).** No reusable methods

**Status.** `NOT_SUPPLIED_BY_THIS_LANE`

**Why not supplied.** This lane planned an experiment to reproduce and extend F1 in a self-contained clause world; it was cancelled before producing a receipt. Nothing here should be read as intake for F1.

**Where the trace lives.**

- research/math-language-learning-v1/ASSAY-ACQUISITION-DIAGNOSIS.md (the funnel table: 21 attempts, three independently checked essential fragments, all singletons)
- research/math-language-learning-v1/CLAUSE-REVIVAL-RESULT.md (the clause donor, which acquires a method and still records NO_DEVELOPMENT_BENEFIT because every eligible development target is a Boolean tautology)

**What the clause revival changes.** It moves the bottleneck. Step-level abstraction does fix the discovery failure -- the pool goes from zero to one. The method then fires zero times because the task ecology contains no essential composite target. Any successor experiment must therefore control opportunity separately from discovery, and must include a tautological-ecology control on which a correctly discovered method is expected to show no benefit.

## F2 — Relevance-key growth and collision traces

**Challenge (#149).** Fixed keys become dense

**Status.** `EXECUTABLE_INTAKE_SUPPLIED`

**Receipt.** `research/cognitive-ladder/results/SUBSPACE_E1_V1.json`  
**sha256.** `5131e5dc1a8ea9c0ef5d6ccff6aaef0fc6911396c8327c70030a9b477f421a65`  
**Reproduce.** `python run_subspace.py --out results/SUBSPACE_E1_V1.json`

**Does not certify.** Correctness never degraded at any scale: a colliding key is slower and never wrong. So this is a cost observation, not a capability failure, and it cannot localize a capability fault.

## F3 — Feature search, rebuild and query work

**Challenge (#149).** Index maintenance fails to amortize

**Status.** `EXECUTABLE_INTAKE_SUPPLIED_WITH_SHARED_RECEIPT`

**Receipt.** `research/cognitive-ladder/results/SUBSPACE_E1_V1.json`  
**sha256.** `5131e5dc1a8ea9c0ef5d6ccff6aaef0fc6911396c8327c70030a9b477f421a65`  
**Reproduce.** `python run_subspace.py --out results/SUBSPACE_E1_V1.json`

**Shared receipt.** #149 is correct that F2 and F3 come from one receipt and are not two independent observations. They are separable in principle -- collision growth is a property of the key, amortisation a property of the repair procedure -- but no run here separates them.

**Does not certify.** The receipt's own limitation applies: the amortisation reading is specific to a search that rescans the whole feature language on every re-index, with no early exit. An incremental search was not run and would cost materially less. Treating INDEX_MAINTENANCE_DOMINATES as a property of re-indexing in general would overreach.

## F4 — Dependency interventions and revision traces

**Challenge (#149).** Redundant supports missed

**Status.** `EXECUTABLE_INTAKE_SUPPLIED`

**Receipt.** `research/cognitive-ladder/results/DEPEND_E3_V1.json`  
**sha256.** `21231aa98cd47e8b28d9a066e4894ffab07bcb3a1c984246f2def1ac963a3f08`  
**Reproduce.** `python run_depend.py --out results/DEPEND_E3_V1.json`

**Capability-gated re-analysis.** Restricting the work comparison to arms at precision and recall 1.0, as the publication constitution requires, leaves three arms. Under that gate the eager learned-dependency arm is dominated by the lazy learner that re-derives on demand, on both work and stale survivors. So the incident is not only that redundant supports are missed; it is that eager discovery is not yet worth its cost.

**Does not certify.** The learned arm's perfect precision and recall are arithmetic, not evidence: it runs the oracle's own leave-one-out procedure. The number measures how often redundancy occurs in this evidence stream, which is a property of the world, not a constant.

## F5 — Probe choices and matched cached-parent results

**Challenge (#149).** Apparent diagnosis residual disappears

**Status.** `EXECUTABLE_INTAKE_SUPPLIED`

**Correction to #149.** #149 lists F5 as lacking executable causal intake. This receipt supplies it: the cached-parent comparison is a measured trace with a per-arm cost table, not a prose claim.

**Receipt.** `research/cognitive-ladder/results/DIAGNOSIS_E2_V1.json`  
**sha256.** `6281fa42b06d9728421702cb51a4bec2140d64eaa8c138bdfa471f1e9e3c197f`  
**Reproduce.** `python run_diagnosis.py --out results/DIAGNOSIS_E2_V1.json`

**Does not certify.** The residual is memoisation of one boolean per checker and scope, and the receipt states that giving the decision-tree parent the same cache would close it. Probe semantics are authored, so this is table inversion under a cost constraint and not evidence that a machine can learn what a probe means.

## F6 — Per-instance escalation contracts and oracle comparisons

**Challenge (#149).** Authored labels disagree with independent checking

**Status.** `EXECUTABLE_INTAKE_SUPPLIED`

**Correction to #149.** #149 lists F6 as lacking executable causal intake. This receipt supplies it, and its oracle is cross-checked against brute-force minimisation over the full repair powerset rather than against another authored label.

**Receipt.** `research/cognitive-ladder/results/ESCALATION_INDEPENDENT_E4_V1.json`  
**sha256.** `f5290bb9b2fab324863ceaab9323990c07dc913130f1fa14295e5a90bb4bfe93`  
**Reproduce.** `python run_escalation_independent.py --out results/ESCALATION_INDEPENDENT_E4_V1.json`

**Does not certify.** Removing the generator's circularity does not remove the ladder's authorship: the repair lattice and the escalation levels still share an author, so this remains E2. It also does not show that the escalation policy is good; on independent worlds the fully-resourced parent ties it.
