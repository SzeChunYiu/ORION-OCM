# EXPERIMENT_PROTOCOL_V0 — verified scientific field calibration

Status: **prospective design; no outcome claim.**  
Owner: #93.  
Purpose: make the scientific-field idea falsifiable before introducing a large implementation.

## 1. Primary question

Does adding a small set of scientific-field semantics to the current KSO reduce whole-task/lifetime scientific work or false authority beyond the strongest parent composition?

Candidate additions under test:

```text
A = context-bound relation certificates
B = unresolved-alternative preservation
C = active/robust distinguishing probes
D = formal-validity / empirical-applicability separation
E = resource-responsibility escalation
```

Current KSO abstraction/warrant/navigation remains incumbent and is not counted as a new mechanism.

## 2. Baselines

- `B0`: flat task-local solver/controller, no persistent shared field.
- `B1`: theorem/knowledge DAG + exact dependency lookup.
- `B2`: knowledge graph / relational store + provenance + TMS/ATMS-style revision.
- `B3`: B2 + active diagnosis / experiment-selection parent.
- `B4`: B3 + algorithm-selection/metareasoning parent.
- `B5`: current OCM/KSO incumbent without A–E.
- `B6`: current OCM/KSO + the minimal subset of A–E that survives ablation.

The strongest fair parent product receives first right of refusal. Do not compare full OCM only against B0/B1.

## 3. Frozen calibration worlds

### W1 — theorem DAG

Generate/curate an exact finite theorem world with known dependencies, reusable lemmas and a binary checker.

Hidden task families require different lemma subsets.

Metrics:

```text
proof obligations expanded
nodes touched k
checker calls
reused theorem identities
wall/CPU work
```

Expectation: B1 or B5 may be sufficient. A–E should not win merely because the benchmark is formal mathematics.

Valid terminal: `THEOREM_DAG_PARENT_SUFFICIENT`.

### W2 — same summary, different defect

Plant detailed states `x1,x2` such that:

```text
summary(x1) = summary(x2)
answer_Q1(x1) = answer_Q1(x2)
answer_Q2(x1) != answer_Q2(x2)
```

Requirements:

- answer Q1 from the existing KSO summary certificate;
- return `REFINE_REQUIRED` for Q2;
- identify the discriminating residual after descent;
- never mint equivalence for Q2.

This is primarily an incumbent calibration. If current KSO passes, report `CURRENT_KSO_ABSTRACTION_SUFFICIENT`.

### W3 — underdetermined competing models

Create models `m1,m2` with identical visible observations under `O0`, but different predictions under a hidden available intervention `p*`.

Requirements:

- preserve both live models;
- do not randomly collapse to one;
- distinguish observational equivalence from representational equality;
- identify/propose `p*` or another valid discriminator under budget;
- update only the affected model/support state after receiving the result.

Negative control: no allowed probe distinguishes `m1,m2`; correct terminal is unresolved multiplicity / `CANNOT_CHECK`, not forced choice.

### W4 — formal/empirical applicability trap

Supply:

- a formally valid theorem in model `M`;
- an explicit assumption `a` required by `M`;
- observations showing the target regime does not establish `a`.

Required output:

```text
FORMALLY_VALID_WITHIN_MODEL
EMPIRICAL_APPLICABILITY_NOT_ESTABLISHED
```

Mutant system collapses the two and grants world-level authority.

### W5 — resource-responsibility trap

Build a two- or three-layer pipeline:

```text
representation/compiler layer -> implementation layer -> end objective
```

In visible development tasks, improving an inner proxy looks attractive. In protected tasks, either:

- `R1`: inner proxy is <1% of total cost and cannot change the winner;
- `R2`: inner proxy crosses a real end-to-end threshold and does change the winner.

Controller must:

- escalate in R1;
- continue optimizing the inner layer in R2.

This prevents a trivial always-escalate policy.

Primary metric: wasted search/operator budget before selecting the responsible layer, plus final end-to-end objective.

### W6 — one-corruption evidence robustness

Generate identity/hypothesis classes and a finite probe library. For each class, exact response words are known.

One selected probe response may be adversarially corrupted.

Compare:

- ordinary minimum test cover;
- robust multicover/code-distance solution;
- repeated independent check baseline;
- OCM proposal + exact verifier.

Required: no identity authority unless the declared corruption model is covered by a checked discriminator/decoder.

### W7 — local-to-global obstruction

Plant local scientific constraints such that every small local view passes but no global assignment/model exists.

Compare CSP consistency / exact global checker / local-global parent methods.

Required:

```text
LOCAL_CONSISTENCY_ONLY
GLOBAL_MODEL_NOT_ESTABLISHED
```

and, where available, an obstruction/counterexample witness.

Do not credit “quantum contextuality” if ordinary CSP/global consistency already explains the case.

### W8 — lifetime sparse-field growth

Grow unrelated persistent competence from `N0` to `Nmax` while holding W2–W5 target families structurally fixed.

Measure:

```text
N total logical state
persistent bytes
k touched state
active bytes
storage/index probes
query work
index maintenance
consolidation work
revision work
```

A positive result requires useful task work to track relevant `k` materially better than `N` after charging all hidden maintenance.

## 4. Ablation ladder

Run at least:

```text
KSO incumbent
KSO + A
KSO + B
KSO + C
KSO + D
KSO + E
KSO + pairwise combinations where interaction is predicted
KSO + all surviving mechanisms
strongest non-OCM parent product
```

Do not assume all A–E belong in the final architecture.

The preferred endpoint is the **smallest Pareto-efficient subset**.

## 5. Quantum-donor-specific hypotheses

### H-Q1 — bounded residual

After consolidation, protected query/revision work can operate on schema + a small defect/residual support for planted families.

Falsifier: residual grows with total history or global scan/index maintenance dominates.

### H-Q2 — active discrimination

A checked active-probe policy lowers experiment/query count versus matched nonadaptive controls without increasing false authority.

Falsifier: standard active-diagnosis/experimental-design parent matches or beats it.

### H-Q3 — evidence reliability scope

Robust probe/certificate requirements prevent authority failures under the declared corruption model at acceptable overhead.

Falsifier: ordinary replication is cheaper/equally strong, or the model of corruption does not match the task.

### H-Q4 — responsibility routing

Explicit responsibility/resource state reduces repeated work on scientifically irrelevant sublayers and selects the correct layer on held-out traps.

Falsifier: generic metareasoning parent obtains the same result or OCM over-escalates R2 cases.

### H-Q5 — cross-domain research-operator transfer

At least one abstract operator learned/derived from quantum research — e.g. `find exact referee`, `search for safe quotient`, `probe competing states`, `escalate to responsible layer` — improves a reminted non-quantum held-out domain without transferring quantum constants.

Falsifier: benefit disappears under semantic reminting or requires target-specific feature engineering.

## 6. Authority invariants

Across all worlds:

```text
false-authority count = 0
revoked/stale authority survivors = 0
router/embedding score never grants truth
formal proof never grants empirical correspondence by itself
failure-to-find never becomes impossibility
```

A resource win cannot compensate for any violation above.

## 7. Resource receipt

Every run records:

```text
persistent bytes
active bytes
logical N
active/touched k
parameters and parameter bytes
training/update compute
index build/update work
storage reads
relations traversed
operator candidates
operator executions
checker/verifier calls
scientific probes/experiments
refinement descents
failed searches
revision/reopen cone
wall/CPU/GPU time
external tool/QPU calls
final outcome
terminal
```

## 8. Adoption gate

A mechanism enters an OCM implementation proposal only if:

1. it wins or gives a required correctness capability against the current KSO incumbent;
2. it survives the strongest faithful parent comparison;
3. its gain survives full maintenance/index/training cost;
4. it does not enlarge the executive into domain-specific cognition;
5. it preserves exact authority/revision semantics;
6. the same mechanism transfers to at least one materially different domain if a domain-general claim is made.

Otherwise retain the negative result and prefer the parent.

## 9. Intended first execution order

```text
W2  -> verify current KSO already covers safe coarse-to-fine behavior
W5  -> test resource-responsibility residual
W3  -> test unresolved alternatives + active probe
W6  -> test reliability-aware probes
W4  -> harden formal/empirical boundary
W8  -> scale lifetime field
W7  -> only then test local/global obstruction
W1  -> theorem-DAG parent calibration can run in parallel
```

Reason: W5/W3/W6 target the most plausible residuals; W2 prevents duplication; W7 is theory-heavy and should not be allowed to become decorative mathematics before simpler parents are exhausted.
