# GENERAL_EPISTEMIC_FIELD_CONTRACT_V1

Status: **canonical research contract candidate for #93; non-constitutional until adopted.**  
Architecture: `M_t = (F_t, O_t, Π_t, C)`.  
This document generalizes the earlier scientific-field framing. Science is a domain/view of `F_t`, not the owner of `F_t`.

## 0. Source-audit correction

The current repository already contains much of the substrate required for a general field:

- `KSO_CORE_V1.md`: one immutable typed directed-hypergraph object with extensible atom/relation registries, warrant, authority, scope, evidence identity, local reopening and resource accounting;
- `KSO_REPRESENTATION_ABSTRACTION_V1.md`: safe quotient/lumpability, warrant measurability, summaries, sufficiency certificates, `REFINE_REQUIRED`, descent and no authority from abstraction;
- `OCM_LANGUAGE_V1.md`: language meanings are typed hypergraph fragments; lexeme senses remain ambiguity sets; constructions are learned/warranted form→meaning procedures; language categories/roles/inventories are registry data rather than constitution;
- `OCM_DIALOGUE_V1.md`: utterance content, speaker commitment and machine warrant are distinct; clarification retains ambiguity; speaker assertion never becomes world truth by repetition;
- #52/#43/#44/#45: language is explicitly a learned communication domain over the general OCM substrate.

Therefore the hardening target is **not** to invent a new universal space. It is to state precisely what it means for these existing mechanisms to form one domain-general epistemic field, and to identify any residual missing behavior.

---

# 1. Canonical object

Use the existing KSO-compatible persistent state as the implementation candidate for the field:

```text
F_t := persistent typed machine-usable epistemic state
```

Do not add a fifth architecture component.

A domain contributes data/contracts around the field:

```text
DomainSpec_d = (
    type_registry_extension,
    representation interfaces,
    operators,
    checker / authority interfaces,
    query/action contexts,
    optional indexes
)
```

The core field laws remain domain-independent.

Science, language, mathematics, coding and planning are **typed views and operator families**, not separate cognitive substrates.

---

# 2. Domain views are logical projections, not copied worlds

For domain `d`, context `C_q` and obligation/query `q`, define a logical view:

```text
View_d(F_t, C_q, q) -> F_q
```

where `F_q` is the active/touched subfield required for the obligation.

Desired regime:

```text
k(q) = |F_q| << N = |F_t|
```

A domain view may filter, index, summarize, refine or materialize state, but it does not create a second truth store.

Physical caches/materializations are allowed only if:

- their bytes and maintenance are counted;
- they carry source/generation identities;
- revocation/update invalidates them locally;
- they cannot become independent authority sources.

---

# 3. Shared identity is earned, not assumed

A major benefit of one field is avoiding unnecessary duplication of the same referent/proposition across language, science and other domains.

However, the field must not assume a perfect universal interlingua.

Representations may be:

```text
exactly corresponding
query-sufficiently corresponding
partial
ambiguous
lossy with an explicit bound
context-dependent
unknown / CANNOT_CHECK
```

Use explicit `Representation` / correspondence objects and warrants.

Candidate rule:

```text
SHARE_IDENTITY(a,b)
```

is allowed only when identity/correspondence is externally given, mechanically established, or admitted under an explicit correspondence warrant.

Similarity, embedding proximity, matching strings or router confidence never establish shared identity.

---

# 4. Same substrate does not mean same semantics

The field generalizes machinery while preserving domain distinctions.

Examples:

```text
formal proof != empirical observation
speaker belief != world truth
utterance meaning != factual commitment
observational equivalence != causal/interventional equivalence
procedure success != theorem proof
high retrieval score != warrant
```

All domain objects may use common identity, dependency, warrant, scope, authority, revision and resource machinery while retaining different authority/checker contracts.

The strong principle is:

> **Generalize the substrate and operators; preserve semantic and authority distinctions.**

---

# 5. Language is a bidirectional field interface

Language does not own a separate cognition store.

## 5.1 Input

Candidate abstract interface:

```text
L_in(utterance, dialogue_context, language_scope)
    -> { FieldProposal_i }
```

A `FieldProposal` may contain:

```text
candidate meaning / relation structure
referent bindings
speaker commitment/report structure
warrant/evidence identities
ambiguity set
unknown lexical/construction obligations
```

Multiple LIVE/UNKNOWN candidates remain multiple until context/evidence licenses collapse.

The existing M3 behavior is incumbent: ambiguity sets are retained and top-1 ranking is not authority.

## 5.2 Output

Candidate abstract interface:

```text
L_out(F_active, communicative_intent, dialogue_context, language_scope)
    -> utterance candidate(s)
```

Surface realization may be rule-based, construction-based, recurrent/SSM/neural, or another learned system. Its size/learning cost are empirical questions.

Before external commitment:

```text
candidate utterance
-> reverse-read / interpret
-> recovered semantic obligations
-> compare to intended obligations
-> commitment gate
```

The renderer cannot invent evidence, authority, referents or propositions.

## 5.3 Fluency boundary

`LLM-like fluency` is an explicit capability target, not assumed from field semantics.

The research question is:

> Once world knowledge, persistent memory, reasoning, authority and task procedures live in `F/O/Π`, how large/statistical must the language realization/interpretation machinery still be to reach strong natural-language quality?

A large Transformer-like language component is a valid reference and possible negative boundary. If it becomes the hidden cognition core, report `PARAMETRIC_LANGUAGE_CORE_DOMINATES`.

---

# 6. Science is another typed field interface

Science contributes object roles such as:

```text
Observation
MeasurementModel
Hypothesis
Model
Experiment
Prediction
Assumption
Counterexample
ResourceModel
CorrespondenceWarrant
```

Formal proof is one possible authority path; empirical applicability requires separate correspondence/evidence.

Required distinction:

```text
FORMALLY_VALID_WITHIN_MODEL
!=
EMPIRICALLY_APPLICABLE_TO_REGIME
```

Science therefore stresses parts of the field that ordinary dialogue may not: measurement uncertainty, alternative models, interventions, resource/error models and local-to-global obstruction.

---

# 7. Mathematics is the clean exact-checker view

Mathematics uses the same field with unusually strong authority conditions:

```text
Definition
Theorem
Lemma
ProofObligation
Proof
Counterexample
```

with proof-kernel checking and exact dependency/reuse.

A theorem DAG is therefore a special, cleanly typed subview of the General Epistemic Field.

No claim that the general field improves theorem-DAG-native tasks is assumed; `THEOREM_DAG_PARENT_SUFFICIENT` is a valid expected result.

---

# 8. Coding/tool use and planning are further views

Coding/tool use may contribute:

```text
API
Program
Invariant
Test
FailureSignature
Patch
EnvironmentVersion
Procedure
ToolContract
```

Planning/work may contribute:

```text
Goal
Action
Precondition
Effect
Constraint
Subgoal
Plan
Failure
ResourceEstimate
```

Again, these are registry/operator additions over the same substrate unless an experiment falsifies that sufficiency.

---

# 9. Cross-domain operator algebra

Candidate domain-general operator families:

```text
RETRIEVE
RELATE
COMPARE
COMPOSE
EXECUTE
CHECK
REFINE
DISTINGUISH
QUERY / OBSERVE
LEARN
REVISE / REOPEN
CONSOLIDATE
TRANSFER
SEARCH_MORE
JUMP
STOP / ABSTAIN
```

Domain-specialized operators remain allowed:

```text
language: INTERPRET, RESOLVE_REFERENCE, REALIZE, CLARIFY
science: MEASURE, EXPERIMENT, IDENTIFY, FALSIFY
math: PROVE, REWRITE, APPLY_LEMMA
coding: TEST, DEBUG, PATCH
```

The strong claim requires that the executive architecture `Π` remain the same while selecting among different domain operator/catalogue content.

---

# 10. `DISTINGUISH` as a cross-domain candidate

A particularly promising abstraction is:

```text
live alternatives
+ allowed probe/action space
+ cost/resource budget
-> discriminating action or CANNOT_CHECK
```

Instantiations:

```text
language ambiguity -> clarification question
science underdetermination -> experiment/intervention
math uncertainty -> proof obligation/counterexample search
coding diagnosis -> test/probe
```

This does not imply one identical algorithm should solve all cases.

The operator contract may be general while domain-native probe generators/checkers differ.

Strong parents — active diagnosis, optimal experiment design, test cover, active learning, value of information — receive first right of refusal.

---

# 11. Representation and compression law

Current KSO abstraction remains incumbent.

A domain may use a coarse representation only under a registered sufficiency/correspondence certificate for the relevant query/context.

Required behavior:

```text
coarse representation sufficient -> answer/use
not certified -> REFINE_REQUIRED
correspondence revoked -> reopen / invalidate
```

Do not promote a universal canonical meaning representation.

A successful field should support multiple overlapping representations with explicit transport warrants and choose the cheapest sufficient one for the current obligation.

---

# 12. Revision law across domains

A field update should propagate by actual dependency/support/correspondence structure, not domain boundaries.

Examples:

- revoking a lexical sense reopens dependent interpretations but not unrelated scientific facts;
- retracting a source observation reopens dependent scientific conclusions and any generated language answer relying on them;
- changing a theorem/definition reopens dependent proofs/procedures but not unrelated dialogue conventions;
- correcting a representation correspondence invalidates cross-view caches and derived claims that used it.

Target cost:

```text
revision work ~ true dependency/correspondence cone
```

not all field state.

---

# 13. Parent collision / novelty boundary

The unified-space idea is heavily parent-owned.

At minimum give first right of refusal to:

## OpenCog AtomSpace / Hyperon

Direct threat: typed hypergraph/metagraph intended to hold linguistic, mathematical, procedural, goal-related and other knowledge, with executable programs represented in the same space and multiple cognitive algorithms operating over it.

OCM cannot claim novelty for:

```text
one typed graph for many cognitive domains
procedures + data in one knowledge substrate
language and reasoning using the same store
```

## Soar

Direct threat: general cognitive architecture with working, semantic, episodic and procedural memory plus learned productions/chunking.

## NARS

Direct threat: domain-independent knowledge representation, semantics, inference, memory and control designed explicitly for insufficient knowledge/resources and continual experience.

## Blackboard / production-system architectures

Direct threat to shared workspace/state plus heterogeneous operators.

## Knowledge graphs / Datalog / provenance / TMS

Direct threats to typed shared state, dependency/revision and inference.

## Cognitive/Construction Grammar and semantic representations

Direct threats to learned form↔meaning structure, grammar-as-network and language-general learning mechanisms.

Therefore the candidate residual is not `GENERAL_FIELD_EXISTS`.

A plausible Machine-Epistemics residual, only if evidence survives, is the coupled behavior:

```text
one typed persistent field
+ exact warrant/authority/scope separation
+ alternative support / local revocation
+ context-certified representation/quotient use
+ unresolved-alternative preservation
+ discriminating probes
+ resource-responsibility escalation
+ sparse lifetime activation k << N
+ learned bidirectional communication over the same state
+ immutable external constitutional authority boundary
```

The strongest parent **composition** must be built before claiming this residual.

---

# 14. Quantum-derived transfers under the general field

Quantum origin does not define a domain boundary. Candidate transfers become general field operators/representation lessons:

```text
safe quotient / syndrome -> context-sufficient representation
bounded defect -> schema/bulk + residual
anti-overcompression -> preserve distinguishing coordinates/counterexamples
adaptive measurement -> DISTINGUISH/probe
robust probe code -> evidence-reliability scope
resource responsibility -> route to end-to-end controlling layer
alternative support -> multi-route warrant/recovery
phase/regime maps -> operator-selection regimes
```

Each loses to a classical parent if that parent reproduces the target behavior.

Physical QPU use remains an external-operator question and is not implied by this field contract.

---

# 15. Hard falsifiers

The strong General Epistemic Field claim fails or contracts if any of these survive best engineering:

```text
DOMAIN_CORE_FORK_REQUIRED
```
A materially different domain requires changing constitutional/core algorithms rather than registry/operator content.

```text
UNIVERSAL_INTERLINGUA_ORACLE
```
The architecture works only because a hand-authored/perfect semantic compiler maps everything into an ideal canonical representation.

```text
FIELD_STATE_SIZE_DOMINATES
```
Unified state becomes too large relative to domain-local alternatives.

```text
HIDDEN_GLOBAL_WORK_DOMINATES
```
Every query/update scans or rebuilds broad `N`.

```text
PARAMETRIC_LANGUAGE_CORE_DOMINATES
```
Strong language requires a large model that carries the cognition attributed to the field.

```text
PARENT_PRODUCT_SUFFICIENT
```
A faithful cognitive-architecture/KG/TMS/language parent composition gives the same capability, lifecycle and resource curve.

```text
NO_CROSS_DOMAIN_OPERATOR_RESIDUAL
```
Apparently general operators are merely same-named domain-specific implementations with no reusable contract/value.

```text
AUTHORITY_COLLAPSE
```
Shared field causes speaker/model/proof/empirical authority to leak across domains.

---

# 16. Required terminals

```text
CURRENT_KSO_ALREADY_GENERAL_ENOUGH
GENERAL_EPISTEMIC_FIELD_SUPPORTED_AT_REGISTERED_SCOPE
SAME_CONTROLLER_CROSS_DOMAIN_SUPPORTED
SHARED_STATE_WITH_TYPED_VIEWS_SUPPORTED
BIDIRECTIONAL_LANGUAGE_FIELD_INTERFACE_SUPPORTED
LANGUAGE_FLUENCY_BOUNDARY_MEASURED
CROSS_DOMAIN_DISTINGUISH_OPERATOR_SUPPORTED
CONTEXT_CERTIFIED_REPRESENTATION_SUPPORTED
LOCAL_CROSS_DOMAIN_REVISION_SUPPORTED
ACTIVE_FIELD_SCALING_SUPPORTED
PARENT_PRODUCT_SUFFICIENT
DOMAIN_CORE_FORK_REQUIRED
UNIVERSAL_INTERLINGUA_ORACLE
PARAMETRIC_LANGUAGE_CORE_DOMINATES
FIELD_STATE_SIZE_DOMINATES
HIDDEN_GLOBAL_WORK_DOMINATES
NO_CROSS_DOMAIN_OPERATOR_RESIDUAL
AUTHORITY_COLLAPSE
CANNOT_CHECK_<reason>
```

---

# 17. Architectural freeze rule

Until falsified, use:

```text
F_t = one typed persistent epistemic field
O_t = learned / composed / donor operator algebra
Π_t = small domain-general executive
C   = external constitutional boundary
```

New language/science/math/coding requirements should first be classified as:

```text
FIELD_TYPE_OR_RELATION
REPRESENTATION_OR_CORRESPONDENCE
OPERATOR
EXECUTIVE_FEATURE
CONSTITUTIONAL_INVARIANT
PHYSICAL_INDEX_STORAGE
DOMAIN_EXPERIMENT
```

Do not open another core architecture concept unless the current factorization cannot represent the requirement without violating its invariants or resource targets.
