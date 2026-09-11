# GMI E3 coding K1 protocol v1 — protected procedural-transfer assay

Status: **DESIGN FROZEN BEFORE PROTECTED H1 OUTCOME ACCESS**.

Refs #208 #369 #233 #377 #373.

This protocol is the first protected coding assay aimed specifically at GMI **K1 cognition/search capital**.

It is not a generic software-engineering benchmark and does not claim that OCM must beat every parent to validate GMI-v1. A `PARENT_SUFFICIENT` result is scientifically valid.

---

# 1. Scientific question

> Does earlier verified coding experience cause a persistent change in **pre-solution cognition/search** that lowers the complete externally verified burden of solving genuinely fresh coding tasks, beyond exact patch reuse and against a strong ordinary persistent parent using the same model, tools, verifier access and developmental history?

The causal chain required for an OCM K1 positive is:

\[
\text{verified history}
\to
\text{changed pre-solution localization / repair search}
\to
\text{fresh protected patch becomes cheaper or more reliable}.
\]

A lower final cost without a frozen pre-solution mediator is not promoted to K1.

---

# 2. Scope

First H1 scope:

```text
language/toolchain: Python unless #208 owner freezes another single language before task generation
repository form: small independently authored micro-repositories
network: disabled during protected tasks
verification: build/import gate + public sanity tests + hidden protected functional/regression tests
gold patch: evaluator-only; never exposed to solving arms
task source: authored after the frozen foundation-model checkpoint/service identity is selected
```

This deliberately starts smaller than DeepSWE/Terminal-Bench. Those remain later external capability anchors after the causal assay works mechanically.

---

# 3. Procedural-transfer families

Protected tasks are grouped by **latent engineering procedure**, but the family label is not shown to solving agents.

The initial registered candidate families are:

## F1 — distributed interface/schema migration

Typical hidden obligation:

```text
an interface/schema change requires finding and coherently updating all semantically coupled uses
```

Task surfaces must vary:

```text
module names
function/class names
file organization
data fields
call graph shape
exact requested behavior
```

Reusable procedure may involve:

```text
identify authoritative boundary
trace producers/consumers
update all coupled sites
run focused + regression tests
```

## F2 — stale derived state / invalidation

Typical hidden obligation:

```text
mutation changes source state but one or more derived/cache/index values remain stale
```

Reusable procedure may involve:

```text
locate source-of-truth mutation
identify derived-state dependency
restore invalidation/recompute invariant
exercise mutation + subsequent read path
```

## F3 — lifecycle / cleanup under failure

Typical hidden obligation:

```text
resource/registration/temp state is cleaned on normal path but leaks or remains inconsistent on exceptional path
```

Reusable procedure may involve:

```text
identify acquisition/commit/cleanup phases
exercise failure injection
make cleanup idempotent / correctly ordered
verify both success and exception paths
```

These families are chosen because the reusable object is a **procedure/search bias**, not an exact code fragment.

A future protocol revision may replace a family only before any protected H1 outcome is accessed.

---

# 4. Anti-leakage / freshness constraints

For every protected target:

```text
exact repository snapshot absent from developmental history
exact task statement absent from developmental history
gold patch absent from all solving-arm contexts
protected tests absent from all solving-arm contexts
protected target patch hash absent from history
protected target repository/path/function identifiers do not occur in developmental task text or stored artifacts except generic language/library vocabulary
```

The evaluator may use the gold patch **after execution** to score frozen pre-solution localization mediators.

That is evaluation, not information supplied to the agent.

Required terminal on violation:

```text
LEAKAGE_ALARM
```

and the task is retained as invalid/cannot-check, never silently replaced after outcome inspection.

---

# 5. Task construction and custody

For each latent family construct two disjoint sets:

```text
DEVELOPMENT set
PROTECTED target set
```

Minimum exploratory H1a design:

```text
3 families
>= 4 development tasks per family
>= 4 protected targets per family
=> >= 12 protected targets total
```

The protected target task statements, gold patches and hidden tests are frozen before any arm sees them.

Preferred confirmatory H1b, only after H1a mechanics/predictor are frozen:

```text
fresh independently authored repositories
>= 6 protected targets per family
>= 3 procedure families
```

H1a is exploratory causal evidence. H1b is the first confirmatory coding K1 candidate.

---

# 6. Model / harness / tool matching

Freeze one foundation model/service identity before task generation/scoring.

Every principal arm receives the same:

```text
foundation model/provider/checkpoint or service version
system-prompt family except treatment-specific persistent-state insertion
mini-SWE-agent-style action surface or exact #208 frozen scaffold
shell/git/search/edit/test tools
repository/task input
public test information
protected verifier feedback bandwidth
network policy
context/token ceilings
wall/tool/verifier budget
retry/parallelism policy
```

Any difference is recorded as a treatment variable and charged.

---

# 7. Principal arms

## A0 — `DIRECT_AGENT`

Same frozen model + coding scaffold/tools, no persistent developmental history beyond ordinary within-task context.

Purpose: absolute model/harness reference.

## A1 — `STRONG_PERSISTENT_PARENT`

Same model/harness/tools plus a deliberately strong ordinary persistent agent product.

It may use:

```text
retrieval over prior successful/failed developmental traces
persistent failure/reflection summaries
explicit procedure/skill cards produced from development tasks
retrieval/ranking of those skills on a fresh task
same verifier/tool history legally available to OCM
```

Skill extraction/summarization model calls are allowed and fully charged.

This arm should be at least as strong in spirit as:

```text
persistent RAG + reflection + explicit skill library
Repo-To-Skill / ContinualSkillBench-style reusable procedures where feasible
```

Do not deliberately cripple this parent.

## A2 — `RESET_OCM`

Same OCM coding integration, model, tools and task information, but the registered developmental state relevant to H1 is reset before the protected target phase.

## A3 — `CONTINUED_OCM`

Same integration with persistent governed developmental state acquired from the registered development tasks.

## A4 — `SHUFFLED_OR_CROSS_HISTORY`

Preserve approximately matched history volume/resource where feasible but supply history from a different registered procedure family or shuffled relationship.

Purpose: distinguish useful structure from generic extra context/memory.

If this arm is technically infeasible without changing context length/format materially, report `CANNOT_CHECK_SHUFFLE_MATCHING` rather than omit silently.

---

# 8. Development phase

All developmental task outcomes are externally verified under the same execution semantics.

The development phase may create persistent objects such as:

```text
trajectory memory
failure constraints
procedure summaries / skills
OCM cognitive assets
retrieval/index state
applicability statistics
```

Every created object records:

```text
source task/receipt digests
construction model/tool calls
storage/index cost
validation/admission work
scope/lifecycle metadata
```

For OCM, self-authored skill/object admission cannot grant external verifier authority.

---

# 9. Frozen pre-solution mediators

A K1 claim requires at least one registered mediator that exists **before protected-test success**.

The primary mediator is gold-scored localization burden.

Let `G_t` be the evaluator-only set of gold-relevant files for target `t`, derived mechanically from the frozen gold patch before scoring but never exposed to the agent.

From the ordered `files_inspected` trace define:

\[
L_t = \min\{k: \text{the first }k\text{ inspected-file events contain every file in }G_t\}.
\]

If not all gold-relevant files are inspected before termination, set `L_t = censor+1` under the frozen budget and retain the censor flag.

Also report:

```text
I_t = number of inspected files not in G_t before all G_t are covered
```

Primary pre-solution geometry comparison:

```text
localization_rank_shift(t)
  = log2((L_RESET(t)+1)/(L_TREATMENT(t)+1))
```

Positive means relevant localization occurred earlier with inherited state.

### Secondary mediator — successful-method order

Before protected execution, freeze a small procedure taxonomy corresponding to F1/F2/F3 but **do not expose the family label**.

A hypothesis/plan event may be scored offline as instantiating the eventual successful procedure only when the mapping rule is fixed and an evaluator can decide it from the logged hypothesis text/action without reading future model reasoning.

Because this scoring is more subjective than file localization, it is secondary only in H1a.

### Additional descriptive signals

```text
patch candidates before first protected-pass candidate
checker/test cycles before success
repeated failed hypothesis count
commands before first gold-relevant file inspection
retrieved assets actually consumed before decisive edit
```

These are not alternative primary mediators unless frozen in a future protocol.

---

# 10. Outcome / capability contract

A protected code success requires:

```text
build/import gate passes
all registered protected functional tests pass
all registered regression/invariant tests pass
no critical false-completion flag
all required checks accounted for
```

The claim remains test-suite/specification relative.

Broken/underspecified evaluator terminal:

```text
ASSAY_DEFECT
CANNOT_CHECK_TEST_VALIDITY
```

rather than model failure.

---

# 11. Raw burden

Use `GMI_E3_RAW_RESOURCES_V1` unchanged.

Primary coding readouts include:

```text
verified success/coverage
foundation-model calls/input/output tokens
candidate hypotheses/patches
file/repository inspections
shell/tool calls
public/protected verifier calls
failed attempts
CPU/GPU/wall/memory
persistent read/write/index/maintenance work
development/skill acquisition work
```

Developmental cost is reported separately and included in lifetime economics.

No mean-over-success-only aggregate may be called overall burden.

---

# 12. H1a exploratory acceptance logic

H1a does **not** authorize a field-level coding K1 claim.

For the `CONTINUED_OCM` vs `RESET_OCM` comparison, record:

### Causal mediator condition

At least `8 / 12` protected targets must have positive primary localization shift, and the pooled/paired median shift must be `> 0`.

This threshold is a mechanics/exploratory screen, frozen before H1a protected outcomes.

### Verified burden condition

At fixed or higher protected success coverage, `CONTINUED_OCM` must have lower median target-serving burden on at least two preregistered serving coordinates:

```text
foundation-model output tokens
checker/test calls
tool/command calls
wall time
```

or Pareto-dominate RESET on the registered serving vector.

If success coverage differs materially, compare at fixed budget/coverage rather than success-only cost.

### Strong-parent condition

If `STRONG_PERSISTENT_PARENT` matches/exceeds the mediator and burden improvements within the preregistered practical-equivalence tolerance chosen **before H1a execution**, terminal:

```text
CODE_K1_PARENT_PRODUCT_SUFFICIENT
```

The tolerance must be filled/frozen by #208 owner during H0 calibration, not after H1a outcomes.

### History-content control

If shuffled/cross-history matches the continued effect:

```text
GENERIC_HISTORY_OR_CONTEXT_SUFFICIENT
```

No procedure-specific K1 interpretation.

---

# 13. Coding K1 terminals

Exploratory positives:

```text
CODE_K1_MECHANISM_SIGNAL_SUPPORTED_H1A
CODE_K1_PARENT_PRODUCT_SUFFICIENT
```

Negatives/boundaries:

```text
CODE_K1_NOT_ESTABLISHED_H1A
NO_PRE_SOLUTION_LOCALIZATION_SHIFT
NO_VERIFIED_BURDEN_GAIN
HARMFUL_TRANSFER
GENERIC_HISTORY_OR_CONTEXT_SUFFICIENT
ADAPTER_DOMINATES
ASSAY_DEFECT
LEAKAGE_ALARM
CANNOT_CHECK_<reason>
```

A positive H1a can only authorize a disjoint H1b confirmatory freeze.

---

# 14. H1b confirmatory rule

H1b must be frozen **after H1a analysis but before any H1b outcome access** using fresh independently authored tasks.

H1b should specify:

```text
exact practical-equivalence tolerance against strongest parent
exact paired/statistical test for localization shift
exact coverage/burden success criterion
family-wise multiplicity handling if separate family claims are made
full development/lifetime accounting rule
```

Only H1b can earn:

```text
CODE_K1_SUPPORTED_AT_REGISTERED_SCOPE_E3
```

and even that is coding-domain K1, not cross-domain GMI.

---

# 15. Relationship to GMI-v1

Three outcomes are all informative:

### OCM residual positive

```text
CONTINUED_OCM changes pre-solution localization/search
+ lowers verified burden
+ strongest persistent parent does not explain the effect
```

This is an OCM-specific K1 candidate at coding scope.

### Parent sufficient

```text
ordinary memory/reflection/skills reproduce the developmental effect
```

This still validates GMI-v1's coding-domain developmental-state/geometry semantics; it just says the successful morphology is parent-owned.

### No K1 effect

```text
no reliable mediator/burden improvement despite mechanically valid assay
```

This is evidence that the current developmental mechanisms do not transfer to coding at this scope. It does not permit changing K1's definition.

---

# 16. Execution gate

Do not execute H1a until #208 has one real H0 source+mapped episode satisfying:

```text
GMI_E3_CODE_H0_SOURCE_TRACE_GREEN
GMI_E3_CODE_H0_EPISODE_EXPORT_GREEN
GMI_E3_EPISODE_SCHEMA_GREEN
```

and the #208 owner freezes:

```text
model/service identity
scaffold/harness identity
H1a task custody manifests
protected verifier custody
practical-equivalence tolerance against strong parent
resource ceilings
```

Current terminal from this file alone:

```text
GMI_E3_CODE_K1_H1A_DESIGN_FROZEN__EXECUTION_GATED_ON_H0
```
