# GMI Shared versus Specialized Learning Theorem v1

Status: **EXACT FINITE-DATA RESPONSE LAW / EXECUTABLE SYNTHETIC CALIBRATION**

Status date: 2026-09-12.

Purpose:

> Close a simple but important part of the shared-versus-specialized learning gap with an exact finite-data bias/variance law. This moves conditional specialization beyond static rank and local gradient interference into prospective generalization under noisy development data.

---

# 1. Registered ecology

There are `m` observable contexts/modes. Context `j` has true scalar target parameter

\[
\mu_j.
\]

For each context we observe `N` independent development samples

\[
y_{jk}=\mu_j+\epsilon_{jk},
\]

with

\[
\mathbb E[\epsilon_{jk}]=0,
\qquad
\operatorname{Var}(\epsilon_{jk})=\sigma^2,
\]

independent across `j,k`.

Protected semantic loss is mean squared error to the true context parameter, not noisy observed labels.

Define mean parameter

\[
\bar\mu=\frac1m\sum_j\mu_j
\]

and context heterogeneity

\[
\tau^2
=
\frac1m\sum_j(\mu_j-\bar\mu)^2.
\]

---

# 2. Separate-context estimator

Estimate each context independently:

\[
\hat\mu_j^{sep}=\frac1N\sum_{k=1}^N y_{jk}.
\]

## Theorem SS-1 — exact expected semantic error of specialization

\[
\mathbb E\left[
\frac1m\sum_j
(\hat\mu_j^{sep}-\mu_j)^2
\right]
=
\frac{\sigma^2}{N}.
\]

### Proof

Each context mean is unbiased with variance `sigma^2/N`; average over contexts. QED.

---

# 3. Fully shared estimator

Pool every context/sample into one shared parameter:

\[
\hat\mu^{share}
=
\frac1{mN}
\sum_{j,k}y_{jk}.
\]

Its expectation is `bar mu` and its variance is

\[
\frac{\sigma^2}{mN}.
\]

## Theorem SS-2 — exact expected semantic error of sharing

\[
\mathbb E\left[
\frac1m\sum_j
(\hat\mu^{share}-\mu_j)^2
\right]
=
\tau^2+rac{\sigma^2}{mN}.
\]

### Proof

Write

\[
\hat\mu^{share}-\mu_j
=(\bar\mu-\mu_j)
+(\hat\mu^{share}-\bar\mu).
\]

The noise term is zero mean and common across contexts. Squaring, averaging and taking expectation eliminates the cross term. The deterministic squared offsets average to `tau^2`, while estimator variance is `sigma^2/(mN)`. QED.

---

# 4. Exact sharing/specialization phase boundary

## Theorem SS-3

Full sharing has lower expected protected semantic error iff

\[
\boxed{
\tau^2
<
\frac{\sigma^2}{N}\left(1-\frac1m\right)
}
\]

and separate specialization is better when the inequality reverses.

At equality the two have identical expected semantic error.

### Interpretation

Sharing trades:

```text
bias from real context heterogeneity: tau^2
against
variance reduction from pooling: sigma^2(1-1/m)/N.
```

This is an exact finite-data response law, not an architectural heuristic.

---

# 5. Developmental consequences

The phase moves predictably:

```text
more data per context N:
    reduces the variance benefit of sharing -> specialization becomes easier to justify

higher observation noise sigma^2:
    increases pooling value -> sharing survives more heterogeneity

more contexts m:
    increases pooled sample count, with threshold approaching sigma^2/N

higher true heterogeneity tau^2:
    pushes toward specialization
```

This is the zero-prior bias/variance mechanism underlying many shared-versus-expert decisions.

---

# 6. Add routing/maintenance cost

Let specialization incur extra priced burden `C_spec` per protected prediction/development horizon relative to the shared model. Convert that burden into registered loss-equivalent units `lambda C_spec`.

Then specialization is preferred only when

\[
\frac{\sigma^2}{N}+\lambda C_{spec}
<
\tau^2+rac{\sigma^2}{mN}.
\]

Equivalently,

\[
\tau^2
>
\frac{\sigma^2}{N}\left(1-\frac1m\right)
+
\lambda C_{spec}.
\]

Communication/router/maintenance cost therefore shifts the specialization threshold upward.

---

# 7. Negative twins

## Identical contexts

If `tau^2=0`, sharing strictly improves expected semantic error for `m>1`, `sigma^2>0`.

## Noise-free sufficient data

If `sigma^2=0`, any nonzero context heterogeneity makes separate exact context parameters better under pure semantic error.

## Sparse observations

With small `N` and large noise, even genuinely different contexts can benefit from pooling because specialization variance dominates.

---

# 8. Relationship to MoE and multi-task systems

The theorem derives **whether context-specific parameter values should be statistically shared**, not a neural Mixture-of-Experts architecture.

A full MoE prediction additionally needs:

```text
high-dimensional/nonlinear mode structure
router learnability/error
partial sharing rather than all-or-nothing sharing
load balancing/communication
expert capacity/search/maintenance
```

But every broader theory should reduce to SS-3 in this simple noisy-context limit.

---

# 9. Executable calibration

`run_gmi_shared_vs_specialized_learning_v1.py` freezes a grid over:

```text
m in {2,4,8}
N in {2,4,8,16,32}
sigma in {0.1,0.5,1.0}
tau in {0,0.05,0.1,0.25,0.5,1.0}
```

For each of 270 cells, context means are constructed to have exact heterogeneity `tau^2`. The runner draws 3,000 independent noisy development replicates with a frozen seed, fits shared and separate sample means, and compares Monte Carlo semantic error to the exact theorem.

Acceptance:

```text
all non-tie cells must have the empirical mean winner predicted by SS-3;
theoretical tie cells are not scored by empirical sign;
empirical errors must remain close to the exact expectations under the registered Monte Carlo tolerance.
```

This is synthetic K3/K5-style calibration, not real neural MoE evidence.

---

# 10. Gap update

`GKF-06` / T5 gains:

```text
representation mode-rank law                         CLOSED
local gradient-interference law                      CLOSED
exact noisy finite-data share/specialize threshold  CLOSED
routing/maintenance threshold shift                  CLOSED

nonlinear partial-sharing estimator                  OPEN
router/load-balance/communication                    OPEN
protected neural dense-vs-MoE prediction             OPEN-BLOCKING
```

---

# 11. Claim ceiling

This theorem is exact for observable scalar contexts with independent homoskedastic noise and sample-mean estimators. It does not establish a general MoE phase law, but it provides a mandatory base case for one.
