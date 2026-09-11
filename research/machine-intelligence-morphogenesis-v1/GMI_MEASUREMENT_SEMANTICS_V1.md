# GMI Measurement Semantics v1

Status: **cross-domain metrology contract**. The theory is not general if “success”, “capability” or “cost” silently changes meaning between neural benchmarks, Lean proofs, code execution and science.

---

# 1. Task contract

A task instance is

\[
\tau=(x,g,\Gamma_\tau,V_\tau,R_\tau),
\]

where:

- `x` — legally supplied observations/context;
- `g` — externally specified goal/obligation;
- `Gamma_tau` — constraints/authority/tool conditions;
- `V_tau` — external evidence/verifier semantics;
- `R_tau` — task-specific resource limits/meters where applicable.

The task contract is external to the learner's internal objective.

---

# 2. Evidence receipt and admissibility

At time `t`, machine/environment interaction produces an evidence receipt

\[
e_t=(y_t,w_t,p_t),
\]

where schematically:

```text
y_t candidate/output/action result
w_t external verification/evidence receipt
p_t provenance/authority receipt
```

An external admissibility predicate

\[
A_\tau(e_t;V,C)\in\{0,1\}
\]

states whether the task contract has been satisfied at that point.

This supports different domains without redefining the theory:

```text
Lean theorem        kernel accepts proof term
code task           required tests/execution contract passes
finite exact task   exact checker accepts
retrieval task      provenance/source obligations satisfied
science task        preregistered evidence/reproducibility contract satisfied
unsafe action       authority/confirmation obligations satisfied or action refused
```

---

# 3. Partial capability

Binary admission is often insufficient for scientific comparison.

Define an externally specified capability vector

\[
Q_\tau(e_t)\in\mathbb R^k
\]

with coordinate direction declared in the obligation.

Examples:

```text
proof: [kernel_success, proof_length_quality]
code: [test_fraction, exact_pass, robustness]
interactive task: [goal_success, constraint_violations, clarification_quality]
science: [predictive fit, calibration, replication status, evidence strength]
```

The theory does not provide a universal list of capability coordinates. The obligation freezes them.

A candidate may have useful partial capability while not yet being admissible.

---

# 4. First-admissible burden

Let

\[
T_A=\inf\{t:A_\tau(e_t)=1\}.
\]

Raw burden is an extended nonnegative vector

\[
\mathbf B(\tau)=\sum_{t=0}^{T_A}\rho_t
\in[0,\infty]^m.
\]

If no admissible result is reached under the registered horizon/protocol, at least one of the following must be reported explicitly:

```text
RIGHT_CENSORED_AT_BUDGET
FAILED_VERIFICATION
ABSTAINED
CANNOT_CHECK
REFUSED_BY_AUTHORITY
INFINITE_OR_UNBOUNDED_IN_THEORY
```

Do not silently drop failed tasks from the mean. This rule directly reflects the survivorship defect already found and closed in #323.

---

# 5. Expected burden with nonzero failure probability

If a protocol has probability `<1` of eventual admissible success, unconditional expected first-success burden may be infinite.

Therefore studies must state which object is being measured:

### Unconditional burden

\[
E[B]
\]

with failures contributing infinite/censored mass as mathematically appropriate.

### Fixed-budget success profile

\[
P(A_\tau\text{ by budget }b)
\]

for one or more raw/scalarized budgets.

### Conditional-on-success cost

\[
E[B\mid success]
\]

allowed only when accompanied by success probability; never report it alone as if failures disappeared.

For practical GMI experiments the recommended primary object is often a capability/success-vs-resource frontier rather than one expected-cost number.

---

# 6. Resource vector semantics

A resource meter may include:

```text
external information / demonstrations / labels
model or library acquisition cost
candidate proposals / search nodes
runtime operations / FLOPs / tokens
wall time
CPU/GPU time
energy where available
memory / persistent storage
communication
external tool calls
verifier/checker calls
failed/rejected work
human intervention time
maintenance / revision / revalidation
morphology search / architecture build cost
```

Coordinates are registered before protected outcome analysis.

GMI does not claim these coordinates are universally commensurate.

---

# 7. Scalarization

A scalar cost is

\[
C_w=w\cdot\mathbf B
\]

only after weight/price vector `w` is declared.

A scalar utility may depend on both capability and resources:

\[
u(Q,\mathbf B).
\]

Changing `w` or `u` can reverse system rankings; such reversals are features of the decision problem, not contradictions in the raw frontier.

---

# 8. Ecology-level capability

For ecology/distribution `E`, define performance statistics from task-level externally verified receipts, for example:

\[
Q_M(E;b)=E_{\tau\sim E}[Q_\tau\text{ achieved under budget }b].
\]

The exact aggregation rule is part of the obligation.

Possible robust summaries include:

```text
mean with uncertainty
median/quantiles
tail-risk / worst-group
success probability
calibration
regret relative to registered comparator
```

No aggregate may erase failed/censored cases.

---

# 9. Developmental comparison

To claim that prior experience improves future cognition, compare matched deployed systems on fresh chronological targets.

Required distinction:

```text
starting capital supplied by researcher
vs
capital acquired by the machine during registered life
```

The acquisition cost of learned state belongs in the lifetime ledger unless the scientific question explicitly studies deployment-only performance.

---

# 10. Cross-domain invariant

The invariant GMI measurement language is:

```text
task contract
external evidence/admissibility
capability vector
raw resource receipts
first-admissible / budgeted success
chronological developmental situation
certified feasible/frontier points
```

Domain-specific verifiers differ; the measurement grammar does not.

That is the key requirement for using the same theory on:

```text
program-search ecologies
Lean mathematics
execution-verified coding
tool workflows
language-mediated tasks
scientific evidence workflows
```

Current terminal:

```text
GMI_CROSS_DOMAIN_MEASUREMENT_SEMANTICS_V1_REGISTERED
REAL_DOMAIN_VALIDATION_PENDING
```
