# GMI E3 math ↔ code validation protocol v1

Status: **DESIGN FROZEN / EXECUTION GATED BY DOMAIN OWNERS**.

Refs #369 #46 #47 #208 #233 #377 #373 #165.

This is the first empirical test of whether the established GMI-v1 formal synthesis survives two materially different real validation regimes **without changing its definitions**.

It does not create a new theorem prover, coding agent, cognitive core or benchmark.

---

# 1. Central E3 question

> Can one common GMI/HST theory object describe and measure developmental cognition in both formal mathematics and execution-verified coding—using the same semantic-state, morphology, burden, verification, K1/K2 and generality semantics—while domain-specific mature parent systems supply the actual theorem/coding capabilities?

The first E3 success does **not** require OCM to outperform every parent.

A useful positive can be:

```text
same GMI semantics fit both domains
+ parent systems instantiate the theory faithfully
+ developmental effects/negatives can be compared without redefining intelligence
```

A stronger OCM result requires causal benefit beyond the strongest matched parent product.

---

# 2. Authority / no-fork rule

```text
#233  HST formal-theory authority
GMI-v1 state/morphology/generality refinement under #233
#369  real-capability integration owner
#46   mathematics-I execution owner (currently LOCKED)
#208  coding-agent execution owner
#38   proof-route / statement-correspondence gate where applicable
```

This protocol **does not unlock #46**. Until its lock is discharged, only schema/infrastructure/calibration work that does not consume protected #46 outcomes is authorized.

Do not open a competing math or coding core lane.

---

# 3. Shared episode object

Every run uses:

`GMI_E3_REAL_COGNITION_EPISODE_V1.json`

with identical top-level semantics:

```text
task contract
starting developmental situation
morphology realization
external verifier contract
pre-solution cognition trace
outcome / capability vector
raw resource vector
ending developmental situation
developmental attribution
```

Domain-specific additions may be raw receipts or verifier metadata only.

Forbidden:

```text
math-specific K1 definition
code-specific intelligence scalar
special OCM-only success semantics
post-hoc resource coordinates
hidden domain state attributed to the machine
```

---

# 4. Shared arms

Freeze the conceptual ladder before protected execution.

## `DIRECT_REFERENCE`

Strong current domain-specific model/agent/prover reference using the same allowed verifier/environment.

Purpose: capability calibration, not necessarily developmental attribution.

## `STRONG_PERSISTENT_PARENT`

Strongest faithful ordinary developmental parent product available under matched information/tools.

Math candidate composition:

```text
same frozen language/model donor where used
+ LeanDojo-v2/Pantograph infrastructure
+ retrieval/premise selection
+ proof/tactic search
+ persistent theorem/proof memory
+ LeanAgent-style continual retriever/database adaptation where feasible
```

Code candidate composition:

```text
same frozen language/model donor
+ standard coding harness
+ persistent retrieval/trajectory memory
+ reflection/failure feedback
+ explicit skill/method library
+ same shell/git/test tools
```

## `RESET_OCM`

Same OCM/harness/tool/verifier powers as continued arm, but the registered relevant developmental state is reset before target phase.

## `CONTINUED_OCM`

Persistent governed developmental state carried from registered acquisition history.

## `SHUFFLED_OR_CROSS_HISTORY`

Where scientifically meaningful, preserve history quantity/resources but break the registered history↔target relationship.

## Mechanism ablations

Only after a residual exists. Do not run a combinatorial ablation suite before there is something to attribute.

---

# 5. Information matching

All causal arms must bind:

```text
foundation model/provider/checkpoint or service identity
system prompt family
language/formalization donor
repository/theorem context
allowed tools
timeouts
network policy
retrieval corpus
verifier access
protected feedback bandwidth
resource budget
persistent-memory permission
parallelism/retry policy
```

If a parent uses a different mechanism internally, that is allowed. If it receives less information/power solely to make OCM win, the comparison is invalid.

Every extra OCM preprocessing/update/index step is charged.

---

# 6. Mathematics specialization

## 6.1 Infrastructure

Reuse `research/proof-replay-v1/` for the already pinned fixed-kernel/replay semantics where compatible.

For broader Lean interaction, adopt LeanDojo-v2/Pantograph-class tooling rather than writing another Lean REPL/tracer.

Bind exact:

```text
Lean release/toolchain
mathlib/repository commit
imports
allowed axioms
statement digest
checker command
search/tracing package versions
```

## 6.2 Mathematical task ladder

Execution is gated by #46, but the intended progression is:

### M0 — fixed replay/calibration

Existing known proofs and exact composition fixture.

Purpose:

```text
verifier plumbing
correspondence-support plumbing
resource meter
receipt schema
```

No learning/generalization claim.

### M1 — known reconstruction

Fresh execution identity, known theorem statements, proof absent from active target context.

Purpose: prove the end-to-end prover/harness works.

### M2 — disjoint composition

Targets require composing known lemmas/methods in combinations not replayed directly.

### M3 — prospective proof-method reuse

Chronological theorem family where earlier verified proofs may create methods/schemas/premise priors useful on fresh targets.

### M4 — novel-premise / repository shift

Use disjoint dependencies/repository families or LeanDojo Benchmark 4 `novel_premises`-style splits for calibration; confirmatory evidence requires protected/fresh targets.

### M5 — higher-difficulty reference

TheoremBench / FormalProofBench / Putnam-style estates may be used as capability calibration. Public/saturated estates are not sufficient for developmental claims.

## 6.3 Math capability coordinates

Prefer a vector rather than one score:

```text
formal target correspondence accepted
full target theorem kernel-verified
registered subgoals/lemmas kernel-verified
proof dependency closure valid
forbidden axiom/sorry count = 0
```

Optional efficiency coordinates:

```text
proof-state expansions
premise retrievals
candidate tactic/proof proposals
kernel calls
wall/CPU/GPU/model tokens
proof trace length
persistent library/index bytes
maintenance/revalidation cost
```

## 6.4 Math K1 mediator

Prospectively prefer one or more of:

```text
rank of eventually consumed useful premise before target proof success
rank/order of eventual successful tactic/proof step where identifiable
proof-state nodes expanded before successful path
pre-solution proposal probability/rank of successful proof skeleton
```

If no causal mediator can be defined prospectively, report solved-cost improvement only and do **not** promote it to GMI K1.

## 6.5 Math K2

K2 requires history to reduce cost of acquiring a **new reusable proof method/search asset**, not simply to solve another theorem with existing memory.

Candidate future assay:

```text
regime A proofs -> acquired K1_A
new theorem family B -> acquire K1_B
continued history versus reset/parent
measure complete burden to first prospectively useful K1_B
```

Do not reuse #323's failed C3 mechanism as evidence; it is only a design lesson.

---

# 7. Coding specialization

## 7.1 Infrastructure

#208 remains execution owner.

Reuse existing ORION/ORION-V2 task isolation, trace, resource and debugging machinery where possible.

Bind:

```text
repository commit/container image
toolchain versions
shell/git/edit/search commands
network policy
public/protected tests
build command
timeouts/resource ceilings
model/harness identity
```

## 7.2 Coding task ladder

### C0 — infrastructure micro-pilot

Mechanics only; no superiority claim.

### C1 — protected debugging / repair

Paired tasks with executable protected tests and frozen repository state.

### C2 — repeated procedure family

Tasks share a reusable engineering procedure but not a target patch/answer.

Examples may include:

```text
API migration pattern
debugging pattern
configuration repair
schema migration
repeated test/diagnostic procedure
```

The family must be registered before target outcomes.

### C3 — repository/family shift

New repository where earlier task-specific patches are useless but higher-level procedures may transfer.

### C4 — serious long-horizon reference

Terminal-Bench-style or audited SWE-style workloads for capability calibration. Public contaminated/broken tasks are not protected developmental evidence.

## 7.3 Code capability coordinates

```text
build/import success
protected functional tests passed
regression/invariant tests passed
critical false completion count
registered requirements discharged
```

When tests are incomplete, the semantic claim remains test-suite relative.

Resource coordinates include:

```text
model tokens/calls
repository reads/searches
commands/tool calls
patch candidates
compile/test runs
failed hypotheses
wall/CPU/GPU
persistent state reads/writes
skill/index maintenance
```

## 7.4 Code K1 mediator

Prospectively register family-appropriate pre-solution mediators, e.g.:

```text
rank/order of eventually correct localization hypothesis
rank/order of eventually successful repair method
candidate patches before accepted patch
repeated-failure count avoided by prior failure knowledge
checker cycles before accepted result
```

A model simply recalling the exact public patch is K0/leakage, not K1.

## 7.5 Code K2

Requires history to reduce the burden of acquiring a **new reusable engineering method/skill** on a fresh family, beyond ordinary persistent skill parents such as Repo-To-Skill/ContinualSkillBench-style systems.

---

# 8. Cross-domain invariance test

The primary E3 theory test is not that numeric values match between math and code.

It is that the following definitions do **not change**:

```text
semantic developmental situation/state
morphology realization
external verifier separation
raw burden vector
capability-resource frontier
RESET vs CONTINUED causal comparison
K0/K1/K2/K3 criteria
negative-transfer / harmful-history terminal
generality profile semantics
```

A theory revision is required if one domain needs a materially different meaning for any of these objects.

Allowed domain differences:

```text
verifier mechanics
raw resource coordinate availability
family-native pre-solution mediator
capability coordinates
adapter syntax/tool vocabulary
```

---

# 9. Prospectively registered theory outcomes

## E3-S0 — semantic transfer

Positive iff both domains can instantiate `GMIRealCognitionEpisodeV1` without changing theory-field meanings and with verifiers externally bound.

Terminal:

```text
GMI_SEMANTICS_TRANSFER_MATH_CODE_SUPPORTED
```

or

```text
GMI_THEORY_REVISION_REQUIRED_<field>
```

## E3-S1 — developmental measurement transfer

Positive iff RESET/CONTINUED/parent arms can be expressed under the same burden and capital semantics in both domains.

Does not require positive OCM transfer in both domains.

## E3-K1 — empirical developmental effect

Domain-specific positive requires:

```text
fresh targets
solution absent from relevant history
pre-solution causal mediator
lower externally verified burden
matched reset and strongest-parent controls
full development/maintenance cost
```

Report per domain. Do not pool incompatible domains into one significance test by default.

## E3-X — heterogeneous lifetime

Locked until at least one mechanically sound developmental assay exists in both domains.

Future question:

> Can one persistent OCM carry governed developmental state across math and code while preserving domain-specific semantics and reducing future burden without hidden core forks?

---

# 10. Parent-success outcomes are theory successes

If LeanAgent-style theorem learning fully explains the math developmental result:

```text
MATH_PARENT_PRODUCT_SUFFICIENT
```

If memory+reflection+skill coding parent fully explains code:

```text
CODE_PARENT_PRODUCT_SUFFICIENT
```

These outcomes do not invalidate GMI-v1. They show that known parent mechanisms are successful morphologies inside the theory.

A distinct OCM architecture claim survives only where a causal residual remains.

---

# 11. Hostile controls

Math:

```text
protected proof imported or memorized
formal statement mismatch
forbidden axiom / sorry
hidden LLM tactic generation in claimed non-LLM arm
retriever index contains target proof
stale compiled cache
checker version mismatch
proof accepted for weaker/different theorem
```

Code:

```text
public gold patch/model memorization
hidden test leakage
broken/underspecified test
adapter contains solution policy
repository version mismatch
false pass from skipped tests
learning update consumes target search budget incorrectly
failed target omitted from aggregate
```

Cross-domain:

```text
different meaning of K1/K2 by domain
unmatched donor/tool access
unpriced verifier/model calls
post-hoc proxy construction
claim ceiling stronger than verifier supports
```

---

# 12. Execution order

```text
E3-0 common schema + verifier semantics                    DONE by this tranche
E3-1 static math/code specialization validator             NEXT
E3-2 math fixed-replay / code micro-pilot instrumentation  allowed only under domain owners
E3-3 public capability calibration against strong parents  no developmental claim
E3-4 protected within-domain K1 assays                      gated/frozen separately
E3-5 cross-domain semantic/measurement comparison          after both assays mechanically valid
E3-6 heterogeneous persistent lifetime                     gated on E3-5
```

No protected math execution while #46 remains locked.

---

# 13. Claim ceiling

Best result available from the present design tranche:

```text
GMI_E3_MATH_CODE_COMMON_PROTOCOL_FROZEN
```

No empirical cross-domain intelligence claim is earned until domain-owner executions are completed.
