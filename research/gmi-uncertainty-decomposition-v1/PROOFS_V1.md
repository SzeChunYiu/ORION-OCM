# Proofs v1 — finite registered uncertainty decomposition

Issue: #750  
Parent ledger: #602 Section M

## UD-T1 — exact law of total variance [P1]

Let `Theta` and `Y` have finite supports. Let `pi(theta) >= 0`, `sum_theta pi(theta)=1`, and for
each `theta` let `K(y|theta) >= 0`, `sum_y K(y|theta)=1`.

Define

```text
m_theta = sum_y y K(y|theta)
v_theta = sum_y (y-m_theta)^2 K(y|theta)
mu      = sum_theta pi(theta) m_theta
A       = sum_theta pi(theta) v_theta
E_mean  = sum_theta pi(theta) (m_theta-mu)^2
T       = sum_theta pi(theta) sum_y K(y|theta) (y-mu)^2.
```

**Theorem.** For every such registered finite model,

```text
T = A + E_mean.
```

### Proof

For each fixed `theta`, write

```text
y - mu = (y - m_theta) + (m_theta - mu).
```

Squaring and taking the conditional expectation under `K(.|theta)` gives

```text
E[(Y-mu)^2 | theta]
 = E[(Y-m_theta)^2 | theta]
   + 2(m_theta-mu) E[Y-m_theta | theta]
   + (m_theta-mu)^2.
```

By the definition of `m_theta`,

```text
E[Y-m_theta | theta] = 0.
```

Hence

```text
E[(Y-mu)^2 | theta] = v_theta + (m_theta-mu)^2.
```

Multiply by `pi(theta)` and sum over `theta`:

```text
T
 = sum_theta pi(theta) v_theta
   + sum_theta pi(theta)(m_theta-mu)^2
 = A + E_mean.
```

No asymptotics, estimation, sampling approximation, or posterior-calibration assumption is used.
The result is an identity conditional on the registered latent semantics.

## UD-T2 — marginal non-identifiability of the split [P1/P2 witness]

Consider predictive marginal

```text
P(Y=-1)=1/2,
P(Y=+1)=1/2.
```

Construct two finite latent models.

### Model A — pure aleatoric at this registered semantics

There is one latent state `a`, `pi(a)=1`, with

```text
K(-1|a)=1/2,
K(+1|a)=1/2.
```

Then

```text
m_a=0,
v_a=1,
mu=0,
A=1,
E_mean=0,
T=1.
```

### Model B — pure epistemic mean at this registered semantics

There are two latent states `b-`, `b+` with equal weight, and deterministic kernels

```text
K(-1|b-)=1,
K(+1|b+)=1.
```

Then

```text
m_b-=-1,
m_b+=+1,
v_b-=v_b+=0,
mu=0,
A=0,
E_mean=1,
T=1.
```

Both models induce **exactly the same full marginal distribution of Y**, but their decompositions are
opposite. Therefore there is no function of the predictive marginal alone that uniquely recovers this
registered `A/E_mean` split on all finite latent models.

This is stronger than saying mean/variance is insufficient: even the complete marginal is insufficient.
A fortiori, predictive intervals, variance alone, or samples from the marginal cannot identify the split
without additional latent/model semantics.

## UD-T3 — `E_mean` is not all epistemic/model uncertainty [P1/P2 witness]

Take two equally weighted latent states with conditional kernels

```text
theta0: P(Y=0)=1
theta1: P(Y=-1)=1/2, P(Y=+1)=1/2.
```

Both conditional means are zero, so

```text
E_mean = Var_pi(m_theta) = 0.
```

Yet the conditional distributions are different: one is deterministic and one is noisy. Thus latent/model
uncertainty can remain while the scalar epistemic variance of the predictive mean is zero.

Consequently this v1 contract must be named narrowly as **epistemic variance of the predictive mean**,
not as a complete scalar measure of epistemic uncertainty.

## UD-T4 — fail-closed identifiability boundary [contract theorem]

The numerical decomposition above is a function of `(pi, K)` and the outcome values. If the artifact
contains only a predictive marginal and does not register latent semantics, multiple latent explanations
are possible by UD-T2. Therefore the implementation must return

```text
CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS
```

rather than manufacture a split.

Likewise malformed or non-exact weights/kernels are outside the theorem domain and are rejected rather
than silently normalized or rounded.

## Claim ceiling

These results establish exact finite algebra and a non-identifiability boundary only. They do not prove
that a chosen latent variable is ontologically correct, that a posterior is calibrated, that aleatoric
noise is physically irreducible, or that the split predicts capability/morphology errors in the real world.
