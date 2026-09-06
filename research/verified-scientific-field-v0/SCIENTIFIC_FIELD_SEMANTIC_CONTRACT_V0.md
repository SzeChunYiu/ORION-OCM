# SCIENTIFIC_FIELD_SEMANTIC_CONTRACT_V0

Status: **RESEARCH CONTRACT / NON-CONSTITUTIONAL CANDIDATE.**  
Owner: issue #93.  
Anchors: #50, #62.  
Runtime/navigation owners: #69–#72.

This document is a deliberately small semantic bridge between the existing KSO contracts and the broader Machine-Epistemics goal of a machine-checkable scientific field. It does not authorize a new runtime subsystem, a new ontology, a quantum-computing claim, or an autonomous-scientist claim.

The existing KSO remains the incumbent. In particular, `docs/spec/KSO_REPRESENTATION_ABSTRACTION_V1.md` already owns navigation lumpability, warrant measurability, summary authority, query-family sufficiency certificates, `REFINE_REQUIRED`, and refinement descent. This proposal **imports those laws rather than re-inventing them**.

---

## 1. Architectural placement

OCM remains:

```text
M_t = (F_t, O_t, Π_t, C)
```

where:

- `F_t` is the persistent epistemic/scientific field represented by KSO-compatible state;
- `O_t` is the operator library;
- `Π_t` is the small executive/router;
- `C` is the constitutional authority/check/commit boundary.

This proposal concerns the semantics of scientific state in `F_t`.

It does not add a fifth architectural component.

---

## 2. The theorem-DAG calibration case

A formal theorem-development graph is the cleanest special case of a scientific field:

```text
object    = formal statement / definition / proof obligation
relation  = exact dependency
checker   = proof kernel
liveness  = mechanically checkable
```

This case is important because it demonstrates that many workers can make progress against shared persistent, reusable, machine-checked structure.

But it is not the general case.

A general scientific field may also contain observations, measurement models, assumptions, uncertain evidence, alternative explanations, competing models, experiments, resource/error models and unresolved questions. These cannot all be converted into binary theorem status without laundering uncertainty or empirical applicability.

Therefore:

```text
THEOREM_DAG ⊂ VERIFIED_SCIENTIFIC_FIELD
```

is a research hypothesis about representational generality, not a claim that theorem DAGs are deficient on their native scope.

`THEOREM_DAG_PARENT_SUFFICIENT` is a required possible terminal for formal-mathematics tasks.

---

## 3. Minimal scientific context

The ORION-V2 structural-space work proposed context-relative equivalence rather than one global similarity score. OCM should test the smallest context object needed to make that principle executable.

Candidate:

```text
ScientificContext = (
    query_class,
    intervention_class,
    authority_regime,
    information_access,
    resource_budget,
    target_decision,
    tolerance,
)
```

No coordinate is frozen. Subtract any coordinate that does not change an admissibility, sufficiency, authority or decision result in the registered experiments.

The essential rule is:

> Any equivalence, quotient, sufficiency or dominance statement that depends on a context must bind the context identity/version into its certificate.

A context change invalidates reuse unless the new context is covered by the old certificate or a separate transport theorem.

---

## 4. Scientific objects: extend by typing, not by a universal mega-object

Do not create one `ScientificObject` class carrying every possible field eagerly.

Prefer existing KSO atom/relation identity and metadata mechanisms plus typed schemas where a domain proves a need.

Candidate semantic roles include:

```text
CLAIM
OBSERVATION
MEASUREMENT_MODEL
ASSUMPTION
HYPOTHESIS
MODEL
COUNTEREXAMPLE
METHOD
EXPERIMENT
PREDICTION
PROOF_OBLIGATION
REPRESENTATION
RESOURCE_RECEIPT
UNKNOWN
```

A role becomes first-class only if a frozen experiment requires different behavior for it.

The physical representation remains owned by #69 and must be measured in bytes, not object-count rhetoric.

---

## 5. Five semantic laws not reducible to ordinary relevance ranking

### SF-L1 — Context-bound equivalence

For structures `a`, `b` and context `C`:

```text
EQUIVALENT_UNDER(a, b, C)
```

must name a witness/certificate and the relation being asserted, e.g. observational, predictive, behavioral, decision-relative or exact structural equivalence.

Never infer authority from embedding similarity, nearest-neighbour distance or router probability.

The same pair may be equivalent under `C1` and distinguishable or incomparable under `C2`.

### SF-L2 — Preserve unresolved multiplicity

If two live scientific states/models cannot currently be distinguished under available probes, the field must represent:

```text
OBSERVATIONALLY_INDISTINGUISHABLE_UNDER(C)
```

or an equivalent scoped relation.

It must not silently merge them unless an existing KSO abstraction/sufficiency law licenses the quotient for the registered query class.

Underdetermination is not representational redundancy.

### SF-L3 — Formal validity is not empirical applicability

A formally checked result may establish:

```text
FORMALLY_VALID_WITHIN(model, assumptions)
```

without establishing:

```text
APPLIES_TO_WORLD(regime)
```

The latter requires a correspondence/measurement/model-validity warrant under the declared empirical regime.

This distinction is mandatory whenever a formal model is used to make an empirical claim.

### SF-L4 — Distinguishing-probe obligation

Given competing live states `H = {h1,...,hm}`, the machine may propose a query/proof/measurement/experiment `p` whose expected or exact outcome distinguishes members of `H`.

Candidate result:

```text
DISTINGUISHED_BY(H, probe_set, guarantee, cost, context)
```

The proposal mechanism may be approximate or learned. The claimed guarantee must be checked by the declared authority.

Failure to find a probe is not proof that no probe exists.

### SF-L5 — Resource-responsibility before local optimization

For an optimization target `J` and candidate layer/operator `x`, OCM should represent whether changes in `x` can materially affect the registered end-to-end objective under the current resource model.

Candidate control result:

```text
RESPONSIBLE_LAYER(x, J, witness)
NOT_RESPONSIBLE_AT_REGISTERED_SCALE(x, J, witness)
CANNOT_CHECK_RESPONSIBILITY
```

If a local proxy improves while the end-to-end objective is provably invariant or dominated elsewhere, the executive should stop widening that local search and escalate to the responsible representation/interface/operator layer.

This law is inspired by ORION-Q failure analysis but must be compared against ordinary causal attribution, sensitivity analysis, bottleneck analysis, algorithm selection and rational metareasoning.

---

## 6. Existing KSO abstraction is first-right-of-refusal

The scientific-field proposal must reuse the current abstraction contract wherever possible.

Existing incumbent capabilities include:

```text
is_lumpable
warrant_measurable
quotient_admissible
summarize
SufficiencyCertificate
answer_with_summary
REFINE_REQUIRED
descend
```

Therefore the scientific-field implementation should initially add **no new quotient engine**.

Instead test whether a `ScientificContext` can be compiled into the existing query-family / warrant / scope machinery.

Only if a prospectively frozen case cannot be represented faithfully should a new abstraction primitive be proposed.

Required negative terminal:

```text
CURRENT_KSO_ABSTRACTION_SUFFICIENT
```

---

## 7. Quantum-derived donors: transferable mechanisms, not quantum branding

The prior ORION/ORION-Q work suggests several candidate transfers.

### QD-A — syndrome / invariant compression

Treat as a search for sufficient statistics / safe quotients. Existing KSO abstraction gets first right of refusal.

### QD-B — bounded-defect localization

Test whether large reusable scientific structure can be represented as:

```text
regular schema/bulk + small residual/defect
```

and whether query/revision work can touch only the residual plus required shared structure.

Compare MDL, grammar/library learning, sparse residual coding and incremental database parents.

### QD-C — contextuality / local-to-global obstruction

Use only as a precise warning that locally compatible facts need not admit one globally valid object.

Test against CSP consistency, database join consistency, sheaf/local-global methods and graphical-model parents.

Do not use “quantum contextuality” as a metaphor when ordinary inconsistency theory explains the case.

### QD-D — active / robust probes

ORION-QG formulated exact distinguishing probes and one-corruption-resilient identification as test-cover / code-distance problems.

OCM may transfer the generic lesson:

```text
uncertain identity/state
→ choose a small discriminating probe set
→ add redundancy when evidence channels are unreliable
```

The classical donors — separating systems, active diagnosis, experimental design, group testing and error-correcting codes — own their mathematics.

### QD-E — resource responsibility

ORION-Q repeatedly found that a large win in an inner representation/proxy could disappear under implementation-grounded cost.

This is the strongest immediate transfer candidate because it is directly about scientific navigation: identify the layer that controls the final outcome before spending search budget.

### QD-F — alternative recovery/support families

Represent multiple live derivations/support routes so one revoked route does not kill a claim if another valid route survives.

Existing warrant/provenance/TMS parents and current KSO support semantics get first right of refusal.

### QD-G — physical QPU boundary

No structural transfer above licenses a physical quantum backend.

A QPU may enter only as an external operator with explicit access/oracle, state-preparation, implementation, measurement/error, verification and end-to-end resource accounting.

No “quantum cognition” claim is permitted by this contract.

---

## 8. Small field API candidate

This is a semantic interface sketch, not an implementation commitment:

```text
classify_relation(a, b, context)
    -> relation + witness | CANNOT_CHECK

answer_or_refine(summary, obligation, context)
    -> ANSWERED | REFINE_REQUIRED | CANNOT_CHECK

live_alternatives(target, context)
    -> support/model alternatives + liveness

propose_distinguishing_probe(alternatives, context, budget)
    -> probe proposal(s)

verify_probe_guarantee(probes, alternatives, context)
    -> certificate | reject

responsibility(target_objective, candidate_layer, context)
    -> responsible / not-responsible / cannot-check

apply_scientific_update(proposal)
    -> constitutional admission path only
```

The executive/router may choose among these operations but cannot manufacture their authority verdicts.

---

## 9. Required calibration worlds

### C1 — Formal theorem DAG

Binary exact checker, exact dependencies, reusable lemmas.

Expected possible outcome: current theorem-DAG parent fully sufficient.

### C2 — Same summary, different protected answer

Two detailed states share a coarse summary. `Q1` is summary-sufficient; `Q2` is not.

Required: answer Q1, return `REFINE_REQUIRED` for Q2.

### C3 — Underdetermined competing models

Two live models fit all current observations but predict different intervention outcomes.

Required: preserve both; propose/identify a distinguishing intervention where available.

### C4 — Formal/empirical mismatch

A theorem is valid in a model whose assumption/correspondence fails for the supplied empirical regime.

Required:

```text
FORMALLY_VALID_WITHIN_MODEL
EMPIRICAL_APPLICABILITY_NOT_ESTABLISHED
```

### C5 — Wrong-layer optimization trap

A candidate method strongly improves an internal proxy while a downstream dominant cost fixes the end-to-end objective.

Required: responsibility diagnosis and escalation.

### C6 — Unreliable evidence channel

One selected observation may be adversarially wrong.

Required: either a checked robust distinguishing scheme or explicit refusal to grant identity/authority.

### C7 — Local-to-global obstruction

Every local neighborhood is individually compatible, but no global object satisfies all registered constraints.

Required: preserve local validity while refusing the global claim and exposing an obstruction witness if the parent method supports one.

---

## 10. Measurements

Every experiment reports a non-compensatory vector containing at least:

```text
correct scientific outcome
false-authority count
correct UNKNOWN/CANNOT_CHECK count
persistent bytes
active bytes
N total field state
k touched field state
index/storage probes
refinement count
verifier/checker calls
scientific probes/experiments
false merges
unsafe quotient attempts
stale survivors after revision
resource-responsibility errors
query work
maintenance/consolidation work
```

A reduction in latency or bytes cannot compensate for a false-authority event.

---

## 11. Strong parents

Before any residual claim, compare the relevant slice against the strongest faithful parent or parent composition:

- theorem DAG / proof-dependency systems;
- knowledge graphs and relational databases;
- Datalog/provenance semirings;
- TMS/ATMS;
- abstract interpretation / CEGAR;
- sufficient statistics / lumpability;
- Bayesian/causal graphical models;
- Blackwell/Le Cam experiment comparison where applicable;
- active diagnosis / test cover / separating systems;
- optimal/Bayesian experimental design;
- CSP/local-consistency and local-to-global methods;
- rational metareasoning / algorithm selection;
- scientific workflow / persistent agent systems.

If a parent product gives the same behavior/cost curve, report `PARENT_SUFFICIENT`.

---

## 12. Research terminals

```text
CURRENT_KSO_ABSTRACTION_SUFFICIENT
THEOREM_DAG_PARENT_SUFFICIENT
CONTEXT_BOUND_RELATION_VALUE_SUPPORTED
UNDERDETERMINATION_PRESERVATION_SUPPORTED
FORMAL_EMPIRICAL_BOUNDARY_SUPPORTED
ACTIVE_PROBE_VALUE_SUPPORTED
ROBUST_PROBE_VALUE_SUPPORTED
RESOURCE_RESPONSIBILITY_VALUE_SUPPORTED
LOCAL_GLOBAL_OBSTRUCTION_VALUE_SUPPORTED
STRONGEST_PARENT_PRODUCT_SUFFICIENT
FIELD_STATE_SIZE_DOMINATES
CERTIFICATION_COST_DOMINATES
NO_CROSS_DOMAIN_VALUE
NO_INCREMENTAL_VALUE
CANNOT_CHECK_<reason>
```

---

## 13. Research claim boundary

The strongest eventual residual is deliberately narrower than “AI can formalize science”:

> A persistent machine can maintain query/context-relative scientific structure, preserve unresolved alternatives, request refinement or discriminating evidence when summaries are insufficient, separate formal validity from empirical applicability, and navigate toward the resource-responsible layer while keeping authority explicit and local.

Whether OCM adds value beyond a strong composition of existing formal-methods, database, diagnosis and scientific-inference parents is an experimental question.
