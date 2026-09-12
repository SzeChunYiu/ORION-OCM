# GMI Zero-Prior Identifiability Theorems v1

Status: **FORMAL CLAIM BOUNDARY / IMPOSSIBILITY HARDENING**

Status date: 2026-09-12.

Purpose:

> Prove which zero-prior derivation quantities cannot be identified exactly from finite observations without additional assumptions. These results convert vague empirical gaps into explicit assumption-dependent prediction problems.

A theory gap is not closed by requesting an impossible universal estimator.

---

# 1. Finite data cannot identify global compressibility distribution-free

Let the finite query domain be `X` with `|X|=N`, output alphabet size `q>=2`, and observed subset `S subset X` with `|S|<N`.

## Theorem ID-1 — unseen-extension ambiguity

For any observed labeling

\[
y:S\to[q],
\]

there are exactly

\[
q^{N-|S|}
\]

global target functions `f:X->[q]` consistent with the observations.

Consequently, unless a candidate shared-law family `H` contains every one of those extensions, finite observations alone cannot establish that the true target lies in `H`.

### Proof

Every unseen point in `X\S` may independently receive any of `q` values. QED.

## Corollary ID-1.1 — no perfect coefficient-vs-memory selector without assumptions

Suppose `H` is a strict subset of all functions on `X` and at least one `h in H` agrees with the observed data. If there is also an extension `g notin H` agreeing with the same data, then any selector that sees only the observed data must output the same decision in both worlds and is wrong in at least one.

Thus exact zero-prior selection between a compressed shared-law realization and arbitrary explicit memory requires at least one of:

```text
complete coverage of the relevant query domain
structural prior/model-class assumption
smoothness/regularity assumption
stochastic source assumption
bounded residual assumption
interventional information
```

### GMI consequence

`GKF-01` cannot have a distribution-free perfect finite-data estimator. Closure must be relative to declared regularity/coverage assumptions plus held-out calibration.

---

# 2. Finite observed inputs cannot identify full dependency geometry

Let observed inputs be `S subset X`, with exact required dependency sets `E_x` known only for `x in S`.

## Theorem ID-2 — unseen dependency ambiguity

If `x* in X\S` and the universal edge vocabulary contains an edge `e` not forced by the observed cells, then there exist two dependency worlds that agree on every observed `E_x` but differ on whether `e in E_{x*}`.

Therefore the global dependency union

\[
U=\bigcup_{x\in X}E_x
\]

and routing opportunity

\[
|U|-\mathbb E|E_x|
\]

are not exactly identifiable from the observed cells alone.

### Proof

Keep all observed dependency sets fixed. Define world `W0` with `e notin E_{x*}` and world `W1` with `e in E_{x*}`, leaving every observed cell unchanged. Any estimator depending only on observed cells receives identical input in both worlds. QED.

### GMI consequence

Attention/sparse-routing prediction requires an explicit generalization assumption for dependency geometry: coverage, locality, exchangeability, smoothness in input space, generative dependency model, or bounded unseen-edge mass.

`GKF-05` is therefore an assumption-dependent estimation problem, not a missing universal theorem.

---

# 3. Finite history horizon cannot identify infinite-horizon predictive-state dimension

Consider deterministic binary-input/output transducers evaluated only on continuations of length at most `T`.

## Theorem ID-3 — horizon extension ambiguity

For every finite `T`, there exist two transducers `M_0,M_1` such that:

1. they produce identical outputs for every input sequence of length at most `T`;
2. their exact infinite-horizon future-response quotients have different cardinalities.

### Construction

`M_0` outputs zero forever and therefore has one future-response class.

`M_1` outputs zero for the first `T` interaction steps. During those steps it records one hidden bit of history (for example the first input). Starting at step `T+1`, it outputs that recorded bit on a registered continuation query.

Every trace through horizon `T` is identical to `M_0`, but after that horizon histories with different recorded bits are future-distinguishable, so `M_1` requires at least two predictive states.

QED.

## Corollary ID-3.1

No estimator using only bounded-horizon behavior can universally recover the exact unbounded-horizon predictive-state quotient without additional assumptions such as:

```text
known finite memory horizon
known finite-state bound
ergodic/stationary source model
analytic/parametric dynamics class
controlled intervention revealing hidden distinctions
```

### GMI consequence

`GKF-07` must report a horizon- and assumption-indexed predictive-state dimension, not an unqualified exact hidden-state dimension from finite data.

---

# 4. Finite residual observations cannot identify unrestricted future residual complexity

Let a frozen predictor produce zero residual on all observed protected-development cells.

## Theorem ID-4 — residual extension ambiguity

If at least one semantically legal future target cell is unobserved, two worlds may agree on every observed residual yet differ arbitrarily on that future cell.

Therefore neither

\[
H(S_O|S_P)
\]

nor worst-case within-predictive target multiplicity is distribution-free identifiable from finite observed residuals without source/coverage assumptions.

### Consequence

A RAG/adaptation/full-rewrite selector must quantify uncertainty about residual mass instead of treating an empirical zero residual as proof of zero future residual.

---

# 5. Finite mode observations cannot certify future mode shareability

Suppose all observed modes have parameter vectors lying in a rank-`r` subspace.

## Theorem ID-5 — unseen-mode rank ambiguity

Unless future mode vectors are constrained to the observed span, an unseen mode can increase the stacked mode-parameter rank by one (up to the ambient dimension) while leaving all observed modes unchanged.

Hence finite observed mode rank is only a lower bound on future heterogeneity absent a mode-generation assumption.

### GMI consequence

MoE/conditional-specialization prediction must attach uncertainty to effective mode rank and test held-out modes. Training-mode rank alone cannot certify future specialization need.

---

# 6. Unified zero-prior identifiability rule

Let `Z` be a proposed pre-outcome descriptor and `D` the finite observed development information. If there exist two legal worlds `w,w'` such that

\[
D(w)=D(w')
\]

but

\[
Z(w)\ne Z(w'),
\]

then no deterministic estimator from `D` alone can be universally exact for `Z`.

This is the basic collision criterion for zero-prior derivability.

The correct response is not to add a world identifier. It is to expose the missing assumption or acquire a legal intervention that separates the worlds.

---

# 7. Revised closure contract

For every empirical zero-prior descriptor, the theory must now register:

```text
observable development information D
latent target descriptor Z
collision family showing what D cannot identify
additional assumption/intervention A used to break the collision
estimator Z_hat(D,A)
uncertainty/calibration law
negative twin violating A
protected held-family test
```

A descriptor is not considered theory-complete merely because an estimator works on one benchmark.

---

# 8. Impact on current gap ledger

The following gaps are now structurally typed:

```text
GKF-01 shared-law compressibility:
    universal exact finite-data identification IMPOSSIBLE without assumptions

GKF-05 dependency geometry:
    full unseen dependency union IMPOSSIBLE without coverage/regularity assumptions

GKF-07 recurrent state dimension:
    infinite-horizon exact dimension IMPOSSIBLE from fixed finite horizon without model assumptions

GKF-08 residual complexity:
    unrestricted future residual mass IMPOSSIBLE from finite residual observations without assumptions

GKF-06 conditional specialization:
    future mode rank IMPOSSIBLE to certify from observed modes without a mode-generation assumption
```

The remaining work is therefore to discover and validate the weakest assumptions sufficient for useful protected prediction.

---

# 9. Claim ceiling

These are impossibility theorems, not excuses for weak prediction. They sharpen the scientific target:

> GMI must make assumption-indexed, uncertainty-calibrated predictions and prospectively test those assumptions on held-out worlds.

The goal is no longer an impossible distribution-free oracle. The goal is the weakest falsifiable conditional law that predicts the known-family frontier and survives semantic remint.
