# GMI Neural Semantic Proposal Geometry protocol v1

Status: **C1 FROZEN BEFORE REGISTERED GRID EXECUTION**

Refs: #233, #377, `GMI_SEMANTIC_PROPOSAL_GEOMETRY_V1.md`, `GMI_SPG_OCM_M2P1_EVIDENCE_V1.json`.

## 1. Purpose

Track B now has:

```text
formal SPG semantics
+ finite exact SPG calibration
+ one real OCM/program-search K1 SPG instance.
```

The next question is whether the **same semantic pre-solution geometry definition** works in a materially different machine-intelligence form: a gradient-trained neural representation learner.

This study does **not** test whether neural learning is novel, superior, or uniquely implied by GMI. Multitask representation learning, transfer learning, meta-learning and gradient-based inductive bias are parent territory.

The study asks only:

> Can developmental neural history produce a prospectively measured improvement in semantic proposal geometry on genuinely fresh target tasks, using the same K1 meaning as program/search SPG?

---

# 2. Pilot disclosure

A non-confirmatory local pilot was used only to calibrate feasible sizes and identify obvious failure modes.

Pilot identities included:

```text
development task seeds 100..111
related target seeds    200..219
cross target seeds      300..319
```

Those outcomes are **E2 exploratory only** and are not part of the registered C1 evidence.

The C1 study below uses disjoint development and target task seeds.

No C1 outcome was accessed before this protocol was committed.

---

# 3. Registered task family

Input:

\[
x\in\mathbb R^{20}.
\]

For latent family `A`, define a fixed row-orthonormal matrix

\[
A\in\mathbb R^{4\times20}.
\]

The shared latent representation is

\[
h_A(x)=\tanh(Ax).
\]

Each task `tau_v` samples a fresh normalized vector

\[
v\in\mathbb R^4
\]

and labels

\[
y=1[v^T h_A(x)>0].
\]

Thus tasks in the same family share a nonlinear representation but have distinct task heads.

Two disjoint latent families are frozen:

```text
A1 matrix seed = 17
A2 matrix seed = 23
```

The target task head vector and target examples are absent from developmental history by seed construction.

---

# 4. Neural realization

The learned representation is a one-layer neural trunk

```text
Linear(20 -> 4)
-> tanh
```

with task-specific linear-logit heads.

During developmental pretraining:

```text
trunk + development-task heads
```

are optimized jointly by Adam and binary cross-entropy.

During a fresh target task:

```text
trunk is frozen
new target head is initialized from the same seed for all compared arms
only target head is trained on the frozen SUPPORT examples
```

No QUERY label is used before the SPG probabilities are emitted.

This isolates inherited representation state as the developmental treatment.

---

# 5. Frozen C1 identities

```text
input dimension d               20
latent dimension k              4
development tasks per family    12
development task vector seeds   1000..1011
development examples/task       512
pretraining steps               1200
pretraining batch size          64
pretraining optimizer           Adam
pretraining learning rate       0.03

registered training replicates  4
trunk/init replicate seeds      41,42,43,44

fresh A1 target task seeds      2100..2111
fresh A2 target task seeds      3100..3111
support examples/target         16
query examples/target           512
target-head optimizer           Adam
target-head steps               300
target-head learning rate       0.05
target-head weight decay        1e-4
```

Input/example RNG streams are deterministic functions of the task seed and are disjoint between development and target tasks.

CPU execution is required for the registered reference run; `torch.set_num_threads(1)` and deterministic-algorithm mode are enabled.

---

# 6. Principal realization arms

For target ecology A1:

```text
MATCHED_HISTORY_NEURAL
  trunk pretrained on A1 developmental tasks

CROSS_HISTORY_NEURAL
  same initial trunk, pretrained on A2 developmental tasks

RESET_NEURAL
  same initial architecture/trunk seed, no developmental pretraining

RAW_LINEAR_PARENT
  target logistic head directly on raw 20D input

ORACLE_REPRESENTATION
  target head on the true evaluator-side h_A1(x)
```

For target ecology A2, swap A1/A2 roles.

The oracle is an upper/reference representation, not a realistic learner.

The raw linear arm is a simple non-neural parent. Broader representation-learning parent ownership is acknowledged from the literature and is not being rediscovered here.

---

# 7. Semantic Proposal Geometry mapping

For each query example, the semantic candidate set is:

```text
{LABEL_0, LABEL_1}
```

and the semantic target is the evaluator-known correct label.

The neural head emits Bernoulli probability

\[
p(y=1\mid x, support, history).
\]

The target semantic probability is

\[
p_*=
\begin{cases}
p,&y=1\\1-p,&y=0.\end{cases}
\]

The SPG surprisal is

\[
I=-\log_2 p_*.
\]

This is measured **before the query label is supplied to the learner**.

Per target task, primary SPG statistic:

```text
mean query semantic surprisal bits
```

over its 512 frozen query examples.

Secondary:

```text
query accuracy
median query surprisal
mean semantic target probability.
```

---

# 8. K1 paired shift

For a fixed replicate and fresh target:

\[
\Delta I_{matched}
=
I_{RESET}-I_{MATCHED}.
\]

Positive means developmental history moved semantic proposal probability toward the fresh correct target.

Cross-history control:

\[
\Delta I_{cross}
=
I_{RESET}-I_{CROSS}.
\]

The target head/task/query identity is absent from developmental history.

---

# 9. Registered C1 finite-grid predictions

There are

```text
4 replicate initializations x 12 fresh target tasks = 48 paired rows
```

per target ecology.

No population-general p-value is required for C1. The complete registered finite grid is the independent object being certified.

## P1 — matched-history positive SPG shift

For **each** of target ecologies A1 and A2:

```text
>= 40 / 48 paired target rows have DeltaI_matched > 0
AND
median DeltaI_matched >= 0.25 bits.
```

## P2 — history specificity

For each target ecology:

```text
median DeltaI_matched - median DeltaI_cross >= 0.25 bits.
```

## P3 — cross-history does not masquerade as generic history benefit

For each target ecology:

```text
median DeltaI_cross <= 0.10 bits.
```

A materially positive cross-history result narrows the interpretation toward generic optimization/context effects.

## P4 — oracle headroom

The oracle representation should have lower aggregate mean surprisal than the matched learned trunk in both ecologies.

Failure does not invalidate SPG, but indicates an assay/optimization anomaly requiring diagnosis before a neural-learning claim.

---

# 10. Terminals

If P1-P4 hold:

```text
NEURAL_K1_SEMANTIC_PROPOSAL_GEOMETRY_SUPPORTED_AT_REGISTERED_SYNTHETIC_SCOPE
```

This means only:

> related neural developmental history changed pre-query semantic proposal probabilities on fresh tasks under the registered finite study.

If P1 fails:

```text
NEURAL_K1_NOT_ESTABLISHED_AT_REGISTERED_SCOPE
```

If P2/P3 fail:

```text
HISTORY_SPECIFICITY_NOT_ESTABLISHED
```

Other valid terminals:

```text
OPTIMIZATION_INSTABILITY
ORACLE_HEADROOM_ASSAY_DEFECT
CANNOT_CHECK_<reason>
```

---

# 11. Claim ceiling

A positive C1 does **not** establish:

```text
new neural-learning theory
K2 developmental capital
modern deep-network generality
cross-domain GMI
neural superiority
resource superiority
new morphology.
```

It would establish the first materially different realization family using the same SPG/K1 semantics already bound to #323 program search.

That would authorize a stronger family-held-out/cross-paradigm prediction study.

---

# 12. Parent subtraction

Parent families include:

```text
multitask representation learning
transfer learning
MAML/meta-learning
PAC/PAC-Bayes environment/bias learning
neural implicit-bias literature
low-dimensional representation learning
```

A positive result is expected under those parents and is **not novelty**.

The GMI scientific value is only the invariant semantic measurement:

```text
history
-> changed pre-solution semantic proposal geometry
-> fresh-target cognition changes
```

under the same definition used in a non-neural/program-search realization.

---

# 13. Resource boundary

The reference run records:

```text
pretraining gradient steps
target-head gradient steps
parameter counts
wall time where observed
```

C1 does not claim lifetime resource dominance.

The next resource-corrected phase study must charge all development/training cost before comparing morphology frontiers.

---

# 14. Frozen execution artifact

The registered executable is:

```text
gmi_neural_spg_c1.py
```

The result is valid only if the executable source identity, protocol constants and emitted receipt agree with this protocol.

Current pre-execution terminal:

```text
GMI_NEURAL_SPG_C1_PROTOCOL_FROZEN
```
