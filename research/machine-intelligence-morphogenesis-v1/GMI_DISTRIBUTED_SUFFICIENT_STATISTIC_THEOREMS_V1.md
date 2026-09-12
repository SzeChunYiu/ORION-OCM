# GMI Distributed Sufficient-Statistic Theorems v1

Status: **FORMAL ZERO-PRIOR DISTRIBUTED/FEDERATED HARDENING**

Status date: 2026-09-12.

Purpose:

> Derive when distributed/federated development can reproduce a centralized model exactly using composable sufficient statistics, and when raw-data distribution is therefore a resource/legal topology issue rather than a semantic limitation.

---

# 1. Partitioned linear-regression data

Suppose development data are partitioned across `K` sites:

\[
(X_k,y_k),\qquad k=1,\ldots,K.
\]

The centralized squared-error loss is

\[
L(\theta)
=
\sum_k\|y_k-X_k\theta\|_2^2.
\]

Each site defines local sufficient statistics

\[
A_k=X_k^TX_k,
\qquad
b_k=X_k^Ty_k,
\qquad
c_k=y_k^Ty_k.
\]

---

# 2. Exact additive composability

## Theorem DS-1 — global sufficient statistics are sums of local statistics

\[
X^TX=\sum_kA_k,
\qquad
X^Ty=\sum_kb_k,
\qquad
y^Ty=\sum_kc_k.
\]

Therefore the exact centralized objective can be reconstructed as

\[
L(\theta)
=
\sum_kc_k
-2\theta^T\sum_kb_k
+
\theta^T\left(\sum_kA_k\right)\theta.
\]

### Consequence

Any optimizer/decision that depends only on these statistics can be reproduced exactly after aggregating the local summaries. Raw examples need not be centralized for semantic equivalence in this registered family.

---

# 3. Communication scaling

For `d` coefficients, each site sends:

```text
A_k: d x d symmetric matrix
b_k: d-vector
c_k: scalar
```

so exact summary size is `O(d^2)` numbers per site, reducible to `d(d+1)/2+d+1` independent scalars using symmetry.

Raw-data transfer instead scales with total examples:

\[
O(n_k d)
\]

features per site plus labels.

## Corollary DS-1.1 — exact summary communication can be asymptotically smaller

If local sample count `n_k` grows while `d` stays fixed/moderate, communication of sufficient statistics is independent of `n_k`, whereas raw-data movement grows linearly in `n_k`.

This is a true lifecycle advantage under the registered linear family.

---

# 4. Privacy/legal topology and semantic equivalence are distinct

DS-1 says the statistics are semantically sufficient for the declared objective. It does **not** guarantee privacy: `A_k,b_k,c_k` can still leak information about local data.

Therefore federated/distributed GMI accounting separates:

```text
semantic sufficiency
communication burden
privacy leakage / legal constraints
secure aggregation / cryptographic burden
fault/adversary tolerance
```

A summary can be semantically exact yet legally inadmissible without privacy protection.

---

# 5. Exact aggregation for additive count models

The same principle applies whenever the centralized sufficient state is additive across records/sites.

Examples include finite categorical count models:

```text
class counts
feature/class co-occurrence counts
multinomial event counts
```

If global posterior/estimator depends only on summed counts, sites can contribute local counts and recover the exact centralized sufficient state.

This provides a zero-prior derivation route for distributed Naive-Bayes-like or exponential-family learning under compatible sufficient statistics.

---

# 6. When exact finite summaries fail

Suppose target development rule depends on arbitrary pairwise relations between examples stored at different sites or on a non-additive global search over raw records.

Then a fixed local summary may not preserve all relevant cross-site distinctions.

### Collision principle

If two local datasets have the same transmitted summary but induce different correct global outcomes under some legal remote-site data, the summary is not globally sufficient.

This is the distributed version of the semantic-quotient collision theorem.

---

# 7. Iterative distributed optimization

Even when no one-shot finite sufficient statistic exists, a distributed algorithm can exchange gradients/parameters iteratively.

For differentiable objective

\[
L(\theta)=\sum_kL_k(\theta),
\]

exact full gradient decomposes as

\[
\nabla L(\theta)=\sum_k\nabla L_k(\theta).
\]

Thus synchronized gradient descent can reproduce centralized full-gradient steps exactly if all local gradients are computed on the same `theta` and aggregation is exact.

### Cost

Each optimization round now incurs communication and synchronization; heterogeneity/staleness can break exact equivalence.

This gives the distributed-learning phase:

```text
one-shot sufficient-statistic aggregation when available
iterative gradient/message aggregation otherwise
local/federated approximation when communication is expensive
```

---

# 8. Negative twins

## Highly heterogeneous local objectives

If sites have different target distributions and one global parameter is semantically inadequate, exact aggregation can still faithfully optimize the wrong shared family. GMI may need personalization/specialization rather than better communication.

## Communication expensive, local tasks independent

If each site serves only its own independent obligation, global aggregation adds burden without semantic benefit.

## Cross-site exact lookup

If arbitrary remote records must be queried exactly, small fixed additive statistics are insufficient; explicit distributed memory/retrieval may be required.

---

# 9. GMI derivation consequence

Distributed/federated form is predicted when:

```text
relevant information/resources are physically or legally partitioned
central raw-state movement is expensive/illegal
semantic sufficient state composes through low-burden messages
or iterative distributed optimization is cheaper than centralization
```

It is not predicted merely because multiple machines exist.

---

# 10. Gap update

Collective/distributed registry now has:

```text
exact additive sufficient-statistic aggregation           CLOSED
exact distributed full-gradient aggregation               CLOSED
communication-vs-raw-data scaling in linear family        CLOSED
semantic/privacy distinction                              CLOSED

non-IID/local heterogeneity response law                  OPEN
privacy/security lifecycle costs                          OPEN
asynchronous/stale optimization                           OPEN
strategic/adversarial multi-agent settings                OPEN-BLOCKING
```

---

# 11. Claim ceiling

These theorems cover additive sufficient statistics and synchronized gradient sums. They do not prove modern federated learning converges under non-IID data, privacy constraints, dropouts or asynchronous communication.
