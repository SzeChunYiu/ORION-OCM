# GMI Probabilistic-State Derivation Theorems v1

Status: **FORMAL ZERO-PRIOR KNOWN-FAMILY HARDENING / PARENT THEORY INTEGRATION**

Status date: 2026-09-12.

Purpose:

> Derive several major probabilistic machine-intelligence families from conditional-independence and belief-state closure, without relying on historical family names.

---

# 1. Conditional independence implies factorized belief state

Let `Y` be a latent/class variable and observations `X_1,...,X_d` satisfy conditional independence given `Y`:

\[
P(x_1,...,x_d|y)=\prod_{i=1}^d P(x_i|y).
\]

## Theorem PB-1 — exact posterior factorization under conditional independence

Bayes' rule gives

\[
P(y|x_1,...,x_d)
\propto
P(y)\prod_{i=1}^d P(x_i|y).
\]

Thus exact posterior comparison among latent states needs only the prior plus the local conditional factors, rather than an unrestricted `d`-way joint observation table.

### GMI derivation consequence

When registered evidence has sparse/conditional factorization, GMI should derive a factorized probabilistic belief representation whose description/update burden tracks the factor graph rather than the full joint state space.

### Negative twin

If strong residual dependencies remain after conditioning on the proposed latent state, the factorized posterior is misspecified; the compression advantage is purchased with semantic error.

---

# 2. Finite hidden Markov belief is a recursive sufficient state

Let hidden state `S_t` take `m` values with transition matrix `T`, and observation `O_t` follow emission probabilities `B(o|s)`. Define belief vector

\[
b_t(s)=P(S_t=s|o_{1:t}).
\]

## Theorem PB-2 — HMM belief recursion

The next predictive belief before observing `o_{t+1}` is

\[
\tilde b_{t+1}=T^T b_t.
\]

After observation `o_{t+1}`, posterior belief is

\[
b_{t+1}(s)
=
\frac{B(o_{t+1}|s)\tilde b_{t+1}(s)}{\sum_{s'}B(o_{t+1}|s')\tilde b_{t+1}(s')}.
\]

Therefore the full observation history can be replaced exactly, for future prediction/decision under the model, by the `m`-component belief vector.

### Proof

Apply the Markov property and Bayes' rule. QED.

### GMI consequence

If hidden dynamics are Markov and uncertainty over hidden state matters, GMI derives **recurrent probabilistic state** rather than either raw-history memory or a single point state.

---

# 3. Belief necessity under decision-complete semantics

Combine PB-2 with the earlier posterior-separation theorem: distinct posterior beliefs can be separated by some utility decision. Therefore if the registered future decision family is rich enough, collapsing two distinct reachable beliefs can destroy exact decision sufficiency.

This supplies both:

```text
constructive upper bound: m-dimensional belief recursion
necessity principle: decision-distinguishable beliefs must remain separate
```

---

# 4. Linear-Gaussian closure gives a finite parametric belief state

Consider

\[
x_{t+1}=A x_t+w_t,
\qquad
w_t\sim\mathcal N(0,Q),
\]

and

\[
y_t=C x_t+v_t,
\qquad
v_t\sim\mathcal N(0,R),
\]

with Gaussian initial state.

## Parent theorem PB-3 — Gaussian filtering closure

If

\[
x_t|y_{1:t}\sim\mathcal N(m_t,P_t),
\]

then prediction remains Gaussian:

\[
m^-_{t+1}=A m_t,
\qquad
P^-_{t+1}=A P_t A^T+Q.
\]

After observation `y_{t+1}`, the posterior is Gaussian with Kalman gain

\[
K=P^- C^T(CP^-C^T+R)^{-1},
\]

mean

\[
m_{t+1}=m^-+K(y_{t+1}-Cm^-),
\]

and covariance

\[
P_{t+1}=(I-KC)P^-.
\]

Thus `(m_t,P_t)` is an exact finite-dimensional belief state under the registered linear-Gaussian model.

### GMI derivation consequence

The reason a Kalman-like state exists is not historical invention: Gaussianity is closed under linear prediction and conditioning. The carrier family is selected by **closure under the legal update operations**.

---

# 5. Closure principle for probabilistic carriers

The examples suggest a general GMI derivation criterion.

Let `B` be a parametric belief family. If every legal prediction and evidence-update operator maps `B` back into `B`, then the parameter vector of `B` is a recursively sufficient probabilistic state under the assumed model.

If closure fails, exact belief may require:

```text
larger parametric family
mixture state
particle/sample representation
nonparametric process
approximation/projection
```

This gives a zero-prior route from obligation/update geometry to different probabilistic kingdoms.

---

# 6. Approximation pressure

Exact belief state may be computationally large even when finite. GMI should compare:

\[
\text{belief approximation error/risk}
+
\text{update/serve burden}
\]

across parametric, particle, factorized and nonparametric realizations.

A narrow exact family should be abandoned when projection error exceeds the burden saved.

---

# 7. Gap update

```text
conditional-independence factorization                   CLOSED
finite HMM belief-state recursion                        CLOSED
belief necessity for rich decision families              CLOSED via prior theorem
linear-Gaussian finite belief closure                    PARENT-THEOREM CLOSED

latent structure discovery                              OPEN-BLOCKING
conditional-independence adequacy estimator              OPEN
nonlinear/non-Gaussian approximation-family selection    OPEN
particle count / approximation response law              OPEN
protected probabilistic-family rediscovery               OPEN
```

---

# 8. Claim ceiling

These results derive probabilistic carrier structure conditional on model assumptions. They do not solve zero-prior discovery of the correct hidden state, graph, emission law or approximation family in arbitrary real environments.
