# GMI PAC-Bayes Generalization Calibration v1

Status: **PARENT-THEOREM INTEGRATION / GENERALIZATION-MECHANISM HARDENING**

Status date: 2026-09-12.

Purpose:

> Add a distribution-dependent algorithmic-prior mechanism to the GMI generalization stack. This complements finite-family counting, stability, margin/robustness and implicit-development bias; it is not asserted to be the universal explanation of neural generalization.

---

# 1. Gibbs predictor setup

Let development sample `S=(z_1,...,z_n)` be IID from distribution `D`. Let hypothesis/parameter space be `H`, loss satisfy

\[
0\le\ell(h,z)\le1.
\]

Choose a prior distribution `P` over hypotheses **independently of the sample**. After seeing `S`, development may produce posterior distribution `Q`.

Define Gibbs risks

\[
\widehat L_S(Q)=\mathbb E_{h\sim Q}\frac1n\sum_i\ell(h,z_i),
\]

\[
L_D(Q)=\mathbb E_{h\sim Q,z\sim D}\ell(h,z).
\]

---

# 2. Parent PAC-Bayes-kl theorem

A standard PAC-Bayes-kl form (Seeger/Maurer-family bound) states that, with probability at least `1-delta` over the IID sample, simultaneously for all posteriors `Q`,

\[
\operatorname{kl}\!\left(
\widehat L_S(Q)\,\|\,L_D(Q)
\right)
\le
\frac{
KL(Q\|P)+\ln\frac{2\sqrt n}{\delta}
}{n},
\]

under the usual bounded-loss assumptions for this theorem variant.

Here `kl(a||b)` is binary relative entropy and `KL(Q||P)` is posterior-to-prior relative entropy.

This is established parent statistical-learning theory, not an original GMI theorem.

---

# 3. Simpler consequence through Pinsker-type inversion

Using

\[
\operatorname{kl}(a\|b)\ge2(a-b)^2
\]

for Bernoulli parameters, a conservative readable consequence is

\[
L_D(Q)
\le
\widehat L_S(Q)
+
\sqrt{
\frac{
KL(Q\|P)+\ln(2\sqrt n/\delta)
}{2n}
}
\]

whenever the right side is truncated to the legal `[0,1]` range as needed.

### GMI interpretation

Protected generalization can be favored when development finds a low-training-loss posterior that does not move too far, in information terms, from a sample-independent prior.

The structural variable is

\[
\frac{KL(Q\|P)}n,
\]

not raw parameter count alone.

---

# 4. Why this differs from finite-class counting

If `P` is uniform over a finite family of `M` hypotheses and `Q` concentrates on one hypothesis, then

\[
KL(Q\|P)=\ln M.
\]

Thus the PAC-Bayes complexity term recovers the same logarithmic family-size dependence that appears in the finite-class union-bound theorem.

But PAC-Bayes also applies to randomized/continuous posteriors and nonuniform priors, so it is a strict extension of the description-complexity idea at this level.

---

# 5. Developmental-state interpretation

A prior `P` can encode development-independent regularity such as:

```text
small norm / scale
symmetry or parameter sharing
pretrained but frozen-before-current-data state
hierarchical/module prior
physics/causal prior
```

A posterior `Q` describes uncertainty/noise around the developed state.

The KL term measures how much information/developmental displacement the current task forced relative to that prior.

This connects generalization to GMI's broader developmental-information accounting.

---

# 6. Data-dependent-prior firewall

If the prior is chosen after unrestricted access to the same protected sample, the KL term can hide target information and the bound's interpretation is invalid without an additional valid construction (for example a separate prior-building split or a theorem that explicitly permits the dependence).

Therefore GMI registers:

```text
prior source and timestamp
information available to prior construction
posterior construction information
sample split / dependence theorem
```

This is the statistical analogue of the D/V/P firewall.

---

# 7. Multiple generalization mechanisms are not interchangeable

GMI currently has formally distinct base mechanisms:

```text
finite-family/description complexity
algorithmic stability
margin/robustness geometry
PAC-Bayes prior/posterior information
implicit development bias selecting one interpolant
```

A valid theory should predict which descriptor is useful in a registered ecology rather than forcing all systems through one bound.

Two predictors can have the same:

```text
parameter count
training error
```

while differing sharply in stability, margin, posterior/prior KL, or source alignment.

---

# 8. Neural-network use and limitation

PAC-Bayes bounds can be instantiated for neural networks, but practical usefulness depends on:

```text
choice of valid prior/posterior
bound tightness
scale/parameterization invariances
stochastic versus deterministic prediction
optimization and source alignment
```

A numerically nonvacuous bound on one model is evidence for that registered mechanism, not proof that PAC-Bayes explains deep learning universally.

---

# 9. Zero-prior prediction target

For held-out learning families GMI should compare, before protected outcomes:

\[
\Psi_{gen}=
(
\text{description complexity},
\text{stability},
\text{margin/norm},
KL(Q\|P),
\text{spectral/effective dimension},
\text{feature/source alignment}
).
\]

Then fit/falsify a mechanism-selection law on development/validation families and predict which descriptors remain predictive on held-out families.

A theory that only reports the best post-hoc bound fails the zero-prior requirement.

---

# 10. Gap update

`GKF-03 modern generalization` now has:

```text
finite-family bound                                  CLOSED
uniform stability expected-gap law                  CLOSED
regularized convex stability                        CLOSED
margin/perturbation base                            CLOSED
linear implicit-development selection               CLOSED
PAC-Bayes KL mechanism                              PARENT-THEOREM CLOSED

distribution-free train-fit -> test-risk rule       IMPOSSIBLE
mechanism-selection law for modern nonlinear nets   OPEN-BLOCKING
held-family quantitative risk prediction            OPEN-BLOCKING
```

---

# 11. Claim ceiling

PAC-Bayes supplies a rigorous conditional generalization guarantee; it does not close deep-network generalization by itself. The remaining GMI task is to predict prospectively when this mechanism, stability, margin, compression or another registered mechanism controls protected risk.
