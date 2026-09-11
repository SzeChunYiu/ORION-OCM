# GMI Realization Signature Limits v1

Status: **FORMAL BOUNDARY — EXACT SIGNATURE SUFFICIENCY REQUIRES ENOUGH DISTINGUISHING CAPACITY**

Refs: `GMI_REALIZATION_DEMAND_SIGNATURE_V1.md`, #377, #233.

## 1. Purpose

The exact parity/majority collision shows that a coarse obligation signature can merge two obligations whose realization rankings differ.

This document records the general finite counting boundary so Track B does not respond by indefinitely adding vaguely defined coordinates and then calling the resulting object universal.

---

# 2. Ranking equivalence

Fix prospectively:

```text
obligation set O
candidate realization set M
semantic admissibility rule
capability comparison rule
raw resource semantics
price/utility rule if scalarized
horizon/development protocol
```

Let

\[
R(\Omega)
\]

be the resulting realization ranking/frontier identity for obligation `Omega`.

Define ranking equivalence

\[
\Omega_1 \equiv_R \Omega_2
\iff
R(\Omega_1)=R(\Omega_2).
\]

Suppose the finite registered obligation set contains

\[
K = |\mathcal O/\equiv_R|
\]

distinct ranking-equivalence classes.

---

# 3. Exact signature sufficiency

A signature

\[
\Xi:\mathcal O\to\mathcal S
\]

is **exactly ranking-sufficient** on the registered set only if

\[
\Xi(\Omega_1)=\Xi(\Omega_2)
\Rightarrow
R(\Omega_1)=R(\Omega_2).
\]

Equivalently, no signature cell may contain obligations from two distinct ranking classes.

Therefore:

\[
|\operatorname{im}(\Xi)|\ge K.
\]

This is an immediate pigeonhole argument.

---

# 4. Bit-capacity corollary

If the entire exact signature is encoded by a fixed `b`-bit code, then

\[
|\operatorname{im}(\Xi)|\le 2^b.
\]

Combining with exact sufficiency:

\[
2^b\ge K
\]

and therefore

\[
\boxed{
b\ge\lceil\log_2 K\rceil.
}
\]

This is ordinary counting mathematics, not a new machine-intelligence theorem.

---

# 5. Consequence: no tiny universally exact demand signature

If the class of registered obligations can generate arbitrarily many distinct realization-ranking classes, no fixed finite-bit signature can remain exactly sufficient across all such obligations.

This does **not** mean useful low-dimensional laws are impossible.

It means a compact GMI demand signature must be treated as one of:

```text
conditional sufficient statistic on a restricted ecology family
approximate predictor with measured error
bound / interval predictor
feature set whose residual failure is retained
```

not as a metaphysically complete coordinate system.

---

# 6. Stronger information does not automatically help scientifically

One can always make `Xi` sufficient by letting it encode the entire obligation or the ranking itself.

That is scientifically vacuous.

Therefore a useful cross-paradigm signature must simultaneously satisfy:

```text
PRE-OUTCOME
COMPACT relative to raw obligation description
SEMANTICALLY INTERPRETABLE
NOT an architecture/ranking label in disguise
PREDICTIVE on held-out obligations/families
CHEAPER to obtain than exhaustively evaluating every realization
```

This is a compression/generalization requirement, not merely injectivity.

---

# 7. Description-language dependence

The newly introduced `tau_L` structural-complexity coordinate can reduce collisions, but it creates another boundary:

\[
\tau_{\mathcal L}
\]

depends on the frozen constructive language `L`.

No practical experiment may silently choose `L` after observing which morphology wins.

At minimum:

```text
freeze L before protected outcomes
charge prior information in L
run an alternative-encoding sensitivity check where material
retain DESCRIPTION_LANGUAGE_DOMINATES if conclusions are unstable
```

An uncomputable representation-invariant ideal such as Kolmogorov complexity may guide theory but cannot be used as an exact empirical measurement oracle.

---

# 8. Demand/response separation boundary

An exact signature may also become vacuous by smuggling morphology response into obligation features.

Forbidden examples:

```text
"gradient usefulness" measured by training the neural model first
"retrieval usefulness" measured by running the library search first
"posterior concentration speed" measured after selecting the Bayesian model
```

These are realization responses or outcomes unless an architecture-independent pre-outcome quantity is separately defined.

The theory must preserve:

\[
\text{obligation demand}
\neq
\text{morphology response}.
\]

---

# 9. Approximate signature objective

For practical DS-E1/DS-E2 work, the target is therefore not exact universal sufficiency.

A scientifically useful signature should demonstrate something like:

\[
I(\Xi;R_{heldout}) > I(B_{trivial};R_{heldout})
\]

or another prospectively frozen predictive criterion, while family identity and protected outcomes are excluded.

The exact statistic/test must be chosen per study; this equation is only schematic.

The strongest control is each family's native predictor.

---

# 10. Registered theorem/boundary

`GMI-RP12 — exact realization-signature capacity bound`

For a finite registered obligation set with `K` distinct realization-ranking equivalence classes, every exact sufficient signature must take at least `K` distinct values. Any fixed `b`-bit exact signature therefore requires

\[
b\ge\lceil\log_2 K\rceil.
\]

Parent owner:

```text
pigeonhole / information-counting argument
```

GMI role:

```text
prevents overclaiming one tiny complete morphology-demand coordinate system
```

---

# 11. Terminals

```text
REALIZATION_SIGNATURE_CAPACITY_BOUND_REGISTERED_V1
REALIZATION_SIGNATURE_INSUFFICIENT__COLLISION
DESCRIPTION_LANGUAGE_DOMINATES
DEMAND_RESPONSE_BOUNDARY_VIOLATED
FAMILY_NATIVE_REALIZATION_THEORIES_SUFFICIENT
CROSS_PARADIGM_REALIZATION_SIGNATURE_SUPPORTED_AT_SCOPE
```

No finite-signature positive licenses:

```text
UNIVERSAL_COMPLETE_MORPHOLOGY_COORDINATE_SYSTEM
```
