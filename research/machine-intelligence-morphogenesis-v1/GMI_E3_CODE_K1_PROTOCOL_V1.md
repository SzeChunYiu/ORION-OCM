# GMI E3 coding K1 protocol v1 — protected procedural-transfer assay

Status: **DESIGN FROZEN BEFORE PROTECTED H1 OUTCOME ACCESS**.

Refs #208 #369 #233 #377 #373.

This protocol is the first protected coding assay aimed specifically at GMI **K1 cognition/search capital**. It is deliberately smaller and more causal than a public software benchmark.

Parent sufficiency is a valid terminal. The objective is to establish whether verified history changes fresh coding cognition, not to force an OCM win.

---

# 1. Scientific question

> Does earlier verified coding experience cause a persistent change in **pre-solution localization / repair search** that lowers the complete externally verified burden of genuinely fresh coding tasks, beyond exact patch reuse and beyond a strong ordinary persistent parent with the same model, tools, verifier access and developmental history?

Required causal chain:

\[
\text{verified history}
\rightarrow
\text{changed pre-solution search geometry}
\rightarrow
\text{fresh protected repair is cheaper / more reliable}.
\]

A lower final cost without a frozen pre-solution mediator is not K1.

---

# 2. Execution scope

First H1a scope:

```text
language/toolchain        Python unless #208 owner freezes another single language before generation
repositories              small independently authored micro-repositories
network                   disabled on protected tasks
verifier                  build/import + public sanity + hidden protected functional/regression tests
foundation model          one frozen provider/checkpoint/service identity
gold repair               evaluator-only, never solver-visible
causal fault receipt      evaluator-only, frozen before any arm runs
task source               authored/generated after the frozen model identity is selected
```

DeepSWE / Terminal-Bench / public SWE-style sets remain later capability anchors. H1a is a causal-development microscope.

---

# 3. Controlled task construction — correct base → planted fault

Each task begins from a **correct base repository** that passes the full evaluator suite.

The evaluator then applies exactly one registered fault transformation and records a private mutation receipt:

```text
base_repo_digest
fault_operator_id
fault_source_file(s)
fault_source_region(s) / symbol(s)
mutation_patch_digest
mutated_repo_digest
public_test_digest
protected_test_digest
inverse/reference repair digest
```

The solving agent receives only:

```text
mutated repository
human-style task/failure description
allowed public tests/tools
```

It does **not** receive:

```text
fault operator label
causal fault location
mutation patch
reference repair
protected tests
procedure-family label
```

Why this matters: the primary localization mediator is scored against the **actual injected causal defect**, not against one chosen gold repair. Alternative valid repairs are therefore not penalized merely because they touch different files.

The inverse/reference repair is used for custody and sanity checks, not as the definition of the successful patch.

---

# 4. Procedural-transfer families

Tasks are grouped by a hidden latent procedure. Surface names/layouts must vary across development and target tasks.

## F1 — distributed interface/schema migration

Fault pattern:

```text
one interface/schema change leaves semantically coupled producers/consumers inconsistent
```

Reusable procedure can involve:

```text
identify authoritative boundary
trace producers + consumers
update coupled sites coherently
run focused + regression verification
```

## F2 — stale derived state / invalidation

Fault pattern:

```text
source state changes but a derived/cache/index value is not invalidated/recomputed
```

Reusable procedure can involve:

```text
locate source-of-truth mutation
identify dependency
restore invalidation/recompute invariant
exercise mutation then subsequent read
```

## F3 — lifecycle / cleanup under failure

Fault pattern:

```text
resource/registration/temp state is correct on success but leaks/remains inconsistent on an exception path
```

Reusable procedure can involve:

```text
identify acquisition / commit / cleanup phases
exercise failure path
restore correct/idempotent cleanup order
verify success + exceptional path
```

The family label never enters solver context.

These are procedure/search families, not code-template families.

---

# 5. Freshness / anti-leakage

For every protected target:

```text
exact mutated repository absent from developmental history
exact task statement absent from developmental history
mutation/reference repair absent from all solving contexts
protected tests absent from all solving contexts
protected target repository/path/function identifiers absent from developmental task text/artifacts except generic language/library vocabulary
```

Development and protected repos must use disjoint authored identifiers and layouts beyond permitted generic vocabulary.

Hash/identifier scans are run before execution.

Violation terminal:

```text
LEAKAGE_ALARM
```

The affected target is retained as invalid/cannot-check and not silently replaced after outcome access.

---

# 6. Task counts / custody

For each family freeze disjoint:

```text
DEVELOPMENT set
PROTECTED target set
```

Exploratory H1a minimum:

```text
3 families
>= 4 development tasks / family
>= 4 protected tasks / family
>= 12 protected targets total
```

Protected manifests are evaluator custody. Public repo may contain only schema/protocol and non-sensitive digests after execution as appropriate.

Preferred H1b confirmatory, if H1a supports continuation:

```text
fresh independently authored repos/tasks
>= 3 procedure families
>= 6 protected targets / family
```

H1b must be frozen separately before its outcomes.

---

# 7. Matched model / harness / tools

Every principal arm receives the same:

```text
foundation model/provider/checkpoint/service identity
system-prompt family except treatment-specific persistent-state insertion
mini-SWE-agent-style action surface or exact #208 frozen scaffold
shell/git/search/edit/test tools
repository/task input
public test information
protected verifier feedback bandwidth
network policy
context/token ceilings
wall/tool/verifier budget
retry / parallelism policy
```

Every deviation is a treatment difference and is recorded/charged.

---

# 8. Principal arms

## A0 `DIRECT_AGENT`

Frozen model + ordinary coding scaffold/tools, no cross-task persistent development state.

## A1 `STRONG_PERSISTENT_PARENT`

Same model/harness/tools with a strong ordinary persistent agent product. It may use:

```text
retrieval over successful + failed developmental traces
persistent reflection/failure summaries
explicit skill/procedure cards generated from development tasks
retrieval/ranking of those skills on fresh targets
same legal verifier/tool history available to OCM
```

Skill extraction/summarization calls and persistent storage/index maintenance are fully charged.

This parent should be at least as strong in spirit as persistent RAG + reflection + explicit skills / Repo-To-Skill-style procedure reuse.

## A2 `RESET_OCM`

Same OCM integration/model/tools, but registered H1 developmental state reset before target phase.

## A3 `CONTINUED_OCM`

Persistent governed developmental state from registered development tasks.

## A4 `CROSS_HISTORY`

Matched history volume/resources from the **wrong procedure family** where technically possible.

Purpose: test whether benefit depends on relevant inherited structure rather than generic extra memory/context.

If exact matching is infeasible:

```text
CANNOT_CHECK_CROSS_HISTORY_MATCHING
```

rather than omitting silently.

---

# 9. Development phase

All development tasks are externally verified under the same execution semantics.

Persistent objects may include:

```text
trajectory memory
failure constraints
procedure/skill summaries
OCM cognitive assets
retrieval/index state
applicability/value statistics
```

Every created object records:

```text
source receipt digests
construction model/tool cost
validation/admission work
storage/index work
scope/lifecycle metadata
```

OCM self-authored objects never gain external verifier authority by self-claim.

---

# 10. Primary pre-solution mediator — causal-fault localization

For target `t`, let evaluator-only set `G_t` be the source file(s) containing the **planted causal fault**, taken from the frozen mutation receipt.

`G_t` is never solver-visible.

Let ordered file-inspection events be:

\[
f_1,f_2,\ldots,f_n.
\]

Define event localization rank:

\[
L_t=\min\{k: G_t\subseteq\{f_1,\ldots,f_k\}\}.
\]

If not all fault files are inspected before termination/budget:

```text
L_t = event_budget + 1
localization_censored = true
```

Also report before full fault-file coverage:

```text
irrelevant_inspection_events
irrelevant_unique_files
repeated_inspection_events
commands_before_fault_cover
```

Primary paired history-induced localization shift:

\[
\Delta I_{loc}(t)
=\log_2\frac{L_{RESET}(t)+1}{L_{TREAT}(t)+1}.
\]

Positive means inherited state caused earlier localization of the actual injected defect.

This metric does **not** assume the reference repair is the only correct repair.

### Function/symbol-level localization

If instrumentation robustly records symbol-level inspections, report them descriptively in H1a. They become primary only in a future prospectively frozen revision.

---

# 11. Secondary pre-solution mediators

## Procedure/hypothesis order

Freeze a procedure taxonomy for F1/F2/F3 before execution. Family label remains hidden from solvers.

Logged hypothesis/plan events can be scored offline against the taxonomy using a frozen rubric.

Because this mapping is more subjective than causal-fault file localization, it is secondary in H1a.

## Descriptive search readouts

```text
candidate patches before first protected-pass patch
checker/test cycles before protected success
repeated failed hypothesis count
first fault-file inspection event
retrieved assets actually consumed before decisive edit
```

These do not replace the primary mediator post hoc.

---

# 12. Success / capability contract

A protected target is successful only when:

```text
build/import gate passes
all registered protected functional tests pass
all registered regression/invariant tests pass
no critical false-completion flag
all required checks accounted for
```

The claim remains relative to the test/specification strength.

Broken/underspecified evaluator:

```text
ASSAY_DEFECT
CANNOT_CHECK_TEST_VALIDITY
```

not model failure.

---

# 13. Raw burden / lifetime economics

Use `GMI_E3_RAW_RESOURCES_V1` unchanged.

At minimum report:

```text
verified success/coverage
model calls/input/output tokens
hypotheses/patches
file inspections / repository searches
shell/tool calls
public/protected verifier calls
failed attempts
CPU/GPU/wall/memory
persistent state reads/writes
index/skill maintenance
all development/skill acquisition work
```

Failed/censored targets retain their costs.

No success-only mean may be called overall burden.

Development cost is reported separately and included in lifetime/break-even analyses.

---

# 14. H1a exploratory acceptance screen

H1a is exploratory and cannot by itself earn the final coding K1 claim.

For `CONTINUED_OCM` vs `RESET_OCM`:

## Mediator screen

At least `8 / 12` protected targets must have:

```text
DeltaI_loc > 0
```

and paired median `DeltaI_loc > 0`.

This is a preregistered exploratory screen, not a confirmatory p-value.

## Verified burden screen

At fixed or higher protected verified coverage, continued must improve at least two registered serving coordinates:

```text
foundation-model output tokens
protected/public checker-test calls
tool/command calls
wall time
```

or Pareto-dominate RESET on the registered serving vector.

If coverage differs, use fixed-budget/coverage analysis rather than success-only cost.

## Parent screen

Before H1a execution, #208 owner must freeze a practical-equivalence tolerance based only on H0/calibration.

If `STRONG_PERSISTENT_PARENT` matches/exceeds the continued mediator + burden effect within that tolerance:

```text
CODE_K1_PARENT_PRODUCT_SUFFICIENT
```

## Cross-history screen

If wrong-family history matches continued:

```text
GENERIC_HISTORY_OR_CONTEXT_SUFFICIENT
```

No procedure-specific K1 interpretation.

---

# 15. H1a terminals

Potential continuation terminal:

```text
CODE_K1_MECHANISM_SIGNAL_SUPPORTED_H1A
```

Parent success:

```text
CODE_K1_PARENT_PRODUCT_SUFFICIENT
```

Negatives/boundaries:

```text
CODE_K1_NOT_ESTABLISHED_H1A
NO_CAUSAL_FAULT_LOCALIZATION_SHIFT
NO_VERIFIED_BURDEN_GAIN
HARMFUL_TRANSFER
GENERIC_HISTORY_OR_CONTEXT_SUFFICIENT
ADAPTER_DOMINATES
ASSAY_DEFECT
LEAKAGE_ALARM
CANNOT_CHECK_<reason>
```

Only a positive H1a authorizes H1b confirmatory design.

---

# 16. H1b confirmatory requirement

H1b uses fresh independently authored protected tasks and must freeze before outcome access:

```text
exact practical-equivalence tolerance vs strongest parent
exact paired/statistical localization test
exact coverage/burden success rule
multiplicity treatment for family-specific claims
full development/lifetime accounting
```

Only H1b may earn:

```text
CODE_K1_SUPPORTED_AT_REGISTERED_SCOPE_E3
```

This remains coding-domain K1, not cross-domain GMI.

---

# 17. Interpretation inside GMI-v1

### OCM residual positive

```text
relevant verified history
-> earlier causal-fault localization / changed search
-> lower verified burden
-> strongest persistent parent does not explain the effect
```

### Parent sufficient

```text
ordinary retrieval/reflection/skills reproduce the effect
```

This still supports GMI's general developmental-state/search-geometry framework; successful morphology is parent-owned.

### No K1

A mechanically valid negative means the current mechanisms do not create coding K1 at this scope. K1's definition is not changed afterward.

---

# 18. Execution gate

H1a may not execute until #208 has one real H0 source+episode satisfying:

```text
GMI_E3_CODE_H0_SOURCE_TRACE_GREEN
GMI_E3_CODE_H0_EPISODE_EXPORT_GREEN
GMI_E3_EPISODE_SCHEMA_GREEN
```

and freezes:

```text
model/service identity
scaffold/harness identity
protected task + mutation custody manifests
protected verifier identity
practical-equivalence tolerance vs strong parent
resource ceilings
```

Current terminal:

```text
GMI_E3_CODE_K1_H1A_DESIGN_FROZEN__EXECUTION_GATED_ON_H0
```
