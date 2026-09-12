# GMI Symmetry and Specialization Response Theorems v1

Status: **FORMAL ZERO-PRIOR HARDENING / EXACT LINEAR-FAMILY THEORY**

Status date: 2026-09-12.

Purpose:

> Replace two vague known-form derivation statements with exact structural variables: symmetry-deviation for shared/equivariant operators, and mode-span rank for shared versus specialized parameter states.

---

# 1. Approximate symmetry as distance to the equivariant subspace

Let a finite group `G` act on `R^n` by orthogonal representation matrices `R_g`. A linear operator `B` is equivariant under this action when

\[
BR_g=R_gB
\]

for every `g`.

For arbitrary target operator `A`, define the group average

\[
\Pi_G(A)=\frac{1}{|G|}\sum_{g\in G}R_g^T A R_g.
\]

## Theorem SE-1 — group average is the Frobenius projection onto equivariant operators

`Pi_G(A)` is equivariant and is the unique Frobenius-norm orthogonal projection of `A` onto the subspace of `G`-equivariant linear operators.

Therefore

\[
\min_{B:\,BR_g=R_gB\;\forall g}\|A-B\|_F^2
=
\|A-\Pi_G(A)\|_F^2.
\]

### Proof

For any `h in G`, conjugating the group average permutes the summands, so

\[
R_h^T\Pi_G(A)R_h=\Pi_G(A),
\]

which is equivalent to equivariance.

Now let `B` be any equivariant operator. Orthogonality of the representation gives

\[
\langle R_g^TAR_g,B\rangle_F
=\langle A,R_gBR_g^T\rangle_F
=\langle A,B\rangle_F.
\]

Averaging over `g` yields

\[
\langle\Pi_G(A),B\rangle_F=\langle A,B\rangle_F,
\]

so `A-Pi_G(A)` is orthogonal to the equivariant subspace. QED.

## Definition — symmetry-deviation energy

Define

\[
\delta_G(A)=\|A-\Pi_G(A)\|_F^2.
\]

This is an exact architecture-neutral measure of how much a linear obligation violates the registered symmetry.

## Corollary SE-1.1 — translation sharing

For the cyclic translation group on `n` coordinates, `Pi_G(A)` is circulant. Thus exact translation symmetry reduces an arbitrary `n^2`-parameter linear operator to an `n`-parameter circulant operator; additional locality can reduce the active kernel width further.

## Theorem SE-2 — resource/approximation crossover for enforced equivariance

Let the full operator have lifecycle burden `C_full` and the equivariant realization have burden `C_eq`. Let one unit of squared protected approximation loss carry registered penalty `lambda>0`.

Then the equivariant realization is preferred under the scalarized registered objective iff

\[
C_{eq}+\lambda\delta_G(A)<C_{full}.
\]

Equivalently,

\[
\delta_G(A)<\frac{C_{full}-C_{eq}}{\lambda}.
\]

### Negative twin

When `delta_G(A)` is large enough, exact parameter sharing is predictably harmful despite its lower resource burden. Thus GMI should not derive convolution/equivariance merely from surface geometry; it must estimate actual symmetry deviation.

### GMI consequence

`GKF-04 approximate symmetry` is reduced from an untyped gap to:

```text
exact response law: CLOSED for finite-group linear maps
remaining gap: pre-outcome estimation of task-relevant delta_G for nonlinear/noisy real obligations
```

---

# 2. Mode heterogeneity as minimal shared-basis rank

Let there be `m` observable modes. Suppose the mode-specific exact linear parameter vectors are

\[
\theta_1,\ldots,\theta_m\in\mathbb F^p
\]

for a field `F`. Stack them as rows of

\[
\Theta\in\mathbb F^{m\times p}.
\]

## Theorem SE-3 — minimal exact shared basis dimension

The minimum number of shared basis vectors required so that every mode parameter can be represented as a linear combination of the shared basis is exactly

\[
r=\operatorname{rank}(\Theta).
\]

### Proof

Any shared basis spanning every row of `Theta` must span the row space, whose dimension is `rank(Theta)`, so at least `r` basis vectors are necessary. A basis of the row space uses exactly `r` vectors and is sufficient. QED.

## Corollary SE-3.1 — constructive shared-state bound

An exact factorization

\[
\Theta=CB
\]

exists with `C in F^{m x r}` and `B in F^{r x p}`. A direct factorized description uses at most

\[
r(m+p)
\]

field symbols, compared with `mp` symbols for independent mode parameters.

Thus low `r` means high shareability; high `r` means genuine mode heterogeneity.

This factorization count is only a constructive upper bound because `(C,B)` is non-unique.

## Corollary SE-3.2 — exact finite-field information law

Over `F_q`, the number of mode-parameter matrices of rank exactly `r` is

\[
N_{m,p,r}(q)=
\prod_{i=0}^{r-1}
\frac{(q^m-q^i)(q^p-q^i)}{q^r-q^i}.
\]

Hence the exact target-identity information of the rank-at-most-`r` family is

\[
\left\lceil
\log_2\sum_{j=0}^rN_{m,p,j}(q)
\right\rceil.
\]

## Theorem SE-4 — specialization alone does not imply MoE

If modes are observable, a generic conditional program may select the appropriate mode-specific computation with the same asymptotic one-mode execution cost as a routed expert system.

Therefore high mode rank plus sparse mode activation derives the need for **conditional specialization**, but does not uniquely derive a neural Mixture-of-Experts architecture.

A MoE-specific prediction additionally requires quantitative assumptions about:

```text
optimization interference under sharing
router learnability/error
communication/load balance
expert maintenance/search burden
hardware execution granularity
```

### Negative twins

```text
rank(Theta)=1:
    all mode parameters lie on one shared direction; specialization has little state justification.

rank(Theta) near min(m,p):
    exact sharing opportunity is small; conditional specialization becomes structurally more plausible.
```

### GMI consequence

`GKF-06 conditional specialization` now has a precise synthetic heterogeneity coordinate:

\[
\chi_{mode}=\operatorname{rank}(\Theta)
\]

or an approximate/effective-rank analogue in real-valued systems.

The remaining empirical problem is to estimate the relevant mode-function span before protected evaluation and quantify optimization/communication effects.

---

# 3. Claim ceiling

These theorems derive exact response variables for linear finite-group symmetry and linear mode specialization. They do not prove that CNNs, GNNs or neural MoE are uniquely optimal in real systems.

The zero-prior prediction target is property-level:

```text
small symmetry-deviation + resource gain -> shared/equivariant realization
large symmetry-deviation -> relax/break sharing
small mode-span rank -> shared realization
large mode-span rank + sparse activation + cheap routing -> conditional specialization
```

Real nonlinear held-family prediction remains protected empirical work.
