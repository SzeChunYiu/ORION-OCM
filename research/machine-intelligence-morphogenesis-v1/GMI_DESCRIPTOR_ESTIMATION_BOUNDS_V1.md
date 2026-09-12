# GMI Descriptor Estimation Bounds v1

Status: **ASSUMPTION-INDEXED PRE-OUTCOME ESTIMATION THEORY**

Status date: 2026-09-12.

Purpose:

> Convert several zero-prior latent structural coordinates into measurable estimators with explicit uncertainty under the weakest simple assumptions available. These results do not overturn the identifiability no-go theorems; they state which extra assumptions make useful prediction possible.

---

# 1. Dependency-edge frequencies

Let the registered universal dependency vocabulary contain `M` possible edges. For random legal input `X`, define indicator

\[
Z_e(X)=\mathbf 1[e\in E_X]
\]

and edge-use probability

\[
p_e=\mathbb E Z_e.
\]

From `n` IID development inputs, estimate

\[
\hat p_e=\frac1n\sum_{i=1}^nZ_e(X_i).
\]

## Theorem DE-1 — uniform edge-frequency concentration

For any `delta in (0,1)`, with probability at least `1-delta`, simultaneously for all `M` edges,

\[
|\hat p_e-p_e|
\le
\sqrt{\frac{\ln(2M/\delta)}{2n}}.
\]

### Proof

Hoeffding's inequality gives probability at most `2 exp(-2n eps^2)` for one edge. Union bound over `M` edges and solve for `eps`. QED.

## Corollary DE-1.1 — average dependency size estimate

Because

\[
\mathbb E|E_X|=\sum_ep_e,
\]

on the same event,

\[
\left|
\sum_e\hat p_e-\mathbb E|E_X|
\right|
\le
M\sqrt{\frac{\ln(2M/\delta)}{2n}}.
\]

This bound is conservative; direct concentration of total edge count can be sharper when dependence structure is known.

---

# 2. Recovering the dependency union requires a minimum-mass assumption

The union is

\[
U=\{e:p_e>0\}.
\]

The zero-prior identifiability theorem proves that finite samples cannot detect arbitrarily rare positive-probability edges distribution-free.

Assume instead:

\[
p_e\ge p_{min}>0
\]

for every edge in `U`.

## Theorem DE-2 — all active edges observed with high probability

The probability that some active edge is never seen in `n` IID inputs is at most

\[
|U|(1-p_{min})^n
\le
M e^{-np_{min}}.
\]

Thus it is sufficient that

\[
n\ge\frac1{p_{min}}\ln\frac{M}{\delta}
\]

to observe every active edge with probability at least `1-delta`.

### GMI consequence

Dynamic-routing opportunity can be prospectively estimated only after registering either:

```text
minimum active-edge probability
coverage/generative dependency model
or a confidence bound on unseen edge mass.
```

No observed union may be silently treated as complete without one of these.

---

# 3. Residual-event rate

Let frozen predictor produce residual event

\[
R=\mathbf1[S_O\ne g(S_P)]
\]

for a registered exact target distinction, with residual probability

\[
\rho=P(R=1).
\]

From `n` IID development cells, let

\[
\hat\rho=\frac1n\sum_iR_i.
\]

## Theorem DE-3 — residual-rate confidence interval

With probability at least `1-delta`,

\[
|\hat\rho-\rho|
\le
\sqrt{\frac{\ln(2/\delta)}{2n}}.
\]

### Zero-observation consequence

If no residual is observed (`hat rho=0`), this does **not** prove `rho=0`. A one-sided elementary bound is

\[
P(\text{zero residuals}|\rho)=(1-\rho)^n.
\]

Hence observing zero residuals implies at confidence `1-delta` only roughly

\[
\rho
\le
1-\delta^{1/n},
\]

not zero.

This directly guards RAG/adapter/full-update selection from false zero-residual claims.

---

# 4. Context heterogeneity under known observation noise

Use the exact shared-versus-specialized ecology:

\[
y_{jk}=\mu_j+\epsilon_{jk},
\]

with `m` contexts, `N` samples/context, independent noise mean zero and variance `sigma^2`.

Let context sample means be

\[
\bar y_j
\]

and grand mean

\[
\bar y.
\]

Define observed between-context mean square

\[
S_B=\frac1m\sum_j(\bar y_j-\bar y)^2.
\]

True heterogeneity is

\[
\tau^2=\frac1m\sum_j(\mu_j-\bar\mu)^2.
\]

## Theorem DE-4 — unbiased heterogeneity correction

\[
\mathbb E[S_B]
=
\tau^2
+
\frac{\sigma^2}{N}\left(1-\frac1m\right).
\]

Therefore

\[
\widehat{\tau^2}_{unb}
=
S_B-
\frac{\sigma^2}{N}\left(1-\frac1m\right)
\]

is unbiased (though it can be negative in finite samples and may be truncated at zero for a nonnegative point estimate, introducing bias).

### Proof

Write `bar y_j=mu_j+e_j`, where independent `e_j` have variance `sigma^2/N`. Centering by the grand mean separates deterministic context offsets from centered noise. The cross term has zero expectation and average centered-noise variance is `sigma^2/N (1-1/m)`. QED.

---

# 5. Connection to the sharing phase boundary

The exact shared-versus-specialized theorem uses threshold

\[
\tau^2
\mathop{\lessgtr}
\frac{\sigma^2}{N}\left(1-\frac1m\right).
\]

DE-4 therefore gives a direct development-data estimator of the hidden phase coordinate under the registered noise model.

However, because estimator variance can be large near the boundary, GMI must attach uncertainty and may need an abstention zone rather than forcing a hard architecture decision.

---

# 6. Unknown noise variance

If `sigma^2` is unknown but repeated samples per context exist, estimate within-context variance

\[
S_W^2=
\frac1{m(N-1)}
\sum_{j,k}(y_{jk}-\bar y_j)^2.
\]

Under IID homoskedastic noise this is unbiased for `sigma^2`.

Plugging it into the heterogeneity correction gives a fully data-derived ANOVA-style estimator; finite-sample confidence intervals require distributional assumptions or concentration bounds.

---

# 7. Sparse residual support discovery

Suppose residual categories/keys form finite vocabulary of size `K`, and every truly active residual category occurs with probability at least `p_min`.

The same coupon/union argument as DE-2 gives sufficient sample size

\[
n\ge\frac1{p_{min}}\ln\frac{K}{\delta}
\]

for observing every active category with probability at least `1-delta`.

Without such a minimum-mass/coverage assumption, unseen rare residual types remain impossible to exclude.

---

# 8. Estimator-to-theory contract

Every descriptor estimate used for architecture prediction must report:

```text
latent structural quantity
observable data/interventions
assumptions used for identifiability
point estimate
uncertainty/confidence set
boundary distance to the predicted crossover
abstention rule if uncertainty overlaps the phase boundary
negative twin violating the assumptions
```

A point estimate without assumption/uncertainty is not zero-prior closure.

---

# 9. Gap update

```text
GKF-05 dependency geometry:
    edge frequency concentration                         CLOSED
    union recovery under p_min                           CLOSED
    arbitrary rare-edge recovery                         IMPOSSIBLE
    real intervention-defined dependency measurement      OPEN

GKF-08 residual complexity:
    residual-rate confidence law                         CLOSED
    zero-residual nonproof                               CLOSED
    residual-category coverage under p_min               CLOSED
    semantic multiplicity/entropy estimator               OPEN

GKF-06 context heterogeneity:
    unbiased scalar-mode heterogeneity estimator         CLOSED
    finite-data exact sharing phase                      CLOSED
    nonlinear function-space heterogeneity               OPEN-BLOCKING
```

---

# 10. Claim ceiling

These are simple IID finite-vocabulary/scalar-context estimators. They do not solve high-dimensional causal dependency discovery, nonlinear residual entropy, or neural mode geometry. They make the assumptions and uncertainty explicit so protected prediction can proceed honestly.
