# Idealized morphology phase theorem v1

Status: **elementary theorem from information theory + amortization; parent-owned mathematics used as a Track-B baseline.**

Refs #377, #233, #373.

## Setup

Let a registered ecology induce a distribution `P` over a finite target/hypothesis set `H`.

Let morphology `M_i` induce, before solving a fresh target, a normalized proposal/code distribution

\[
Q_i(h)>0,\qquad \sum_h Q_i(h)=1.
\]

Use the idealized per-target search/code burden

\[
b_i(h)=-\log Q_i(h).
\]

Let `B_i` be the morphology's one-time build/acquisition cost in the same prospectively frozen scalar cost unit, and let the lifetime contain `N` IID target draws from `P`.

Then expected lifetime burden is

\[
C_i(N,P)=B_i+N\,\mathbb E_{h\sim P}[-\log Q_i(h)].
\]

## Theorem 1 — entropy + mismatch decomposition

Using the standard cross-entropy identity,

\[
\mathbb E_P[-\log Q_i]
=H(P)+D_{KL}(P\Vert Q_i).
\]

Therefore

\[
\boxed{
C_i(N,P)=B_i+N\left[H(P)+D_{KL}(P\Vert Q_i)\right].
}
\]

### Proof

By definition,

\[
D_{KL}(P\Vert Q_i)
=\sum_h P(h)\log\frac{P(h)}{Q_i(h)}
=\sum_h P(h)\log P(h)-\sum_h P(h)\log Q_i(h).
\]

Since

\[
H(P)=-\sum_hP(h)\log P(h),
\]

rearranging gives the cross-entropy identity. Add `B_i` and multiply the per-target term by `N`. QED.

## Theorem 2 — exact two-morphology phase condition

Morphology `M_1` has lower expected lifetime burden than `M_2` iff

\[
\boxed{
D_{KL}(P\Vert Q_1)-D_{KL}(P\Vert Q_2)
<
\frac{B_2-B_1}{N}.
}
\]

The ecology entropy cancels.

Thus the winner depends on:

```text
how well morphology bias matches ecology
versus
relative build cost amortized over lifetime horizon.
```

## Corollary 1 — long-horizon limit

If build costs are finite and fixed,

\[
\lim_{N\to\infty}\frac{B_2-B_1}{N}=0.
\]

So asymptotically the lower expected-burden morphology is the one with smaller

\[
D_{KL}(P\Vert Q_i).
\]

In this idealized model, long-horizon dominance is inductive-bias/ecology alignment.

## Corollary 2 — short horizons can reverse the asymptotic winner

A morphology with better ecology alignment but larger build cost may lose for small `N`.

Hence training/build amortization is structurally part of the morphology phase law.

## Corollary 3 — there is no universally best fixed proposal prior over unrestricted ecologies

For distinct full-support distributions `Q_1` and `Q_2`, there are target/ecology distributions that favor each one under sufficiently long horizon. In particular, concentrating `P` on a target to which one proposal distribution assigns more mass makes that morphology's surprisal lower on that ecology.

This is a simple inductive-bias counterpart of broader No-Free-Lunch intuition; do not overstate it as a new NFL theorem.

## Why this matters to Track B

This theorem gives an exact answer to a restricted version of the user's question:

> Why can one form of intelligence dominate another?

In this idealized search/coding regime:

```text
because its inherited proposal geometry matches the target ecology better,
and the resulting savings repay its build/development cost over the available horizon.
```

But this is **not new GMI theory**. It is standard cross-entropy/KL plus amortization.

## The hard missing map

The theorem assumes `Q_i`.

The nontrivial Track-B problem is to derive/predict `Q_i` and its update law from the morphology's actual structure, learning rule, developmental history and resource realization:

\[
\boxed{
(M,U,H)\longrightarrow Q_M,K_M,c_M
}
\]

before observing protected future outcomes.

That is `STRUCTURE_TO_GEOMETRY_PROGRAMME_V1.md`.

## Generalization boundary

Real machine intelligence may involve:

- non-IID tasks;
- sequential action;
- partial observability;
- changing target distributions;
- non-normalized search allocations;
- verification and failed-attempt costs;
- retention/plasticity;
- multiple resource coordinates;
- active information gathering;
- changing morphology during life.

For those cases, use the full developmental Pareto / sequential-decision formulation. Do not force this simple theorem beyond its assumptions.

## Terminal

```text
IDEALIZED_MORPHOLOGY_PHASE_LAW_DERIVED__INFORMATION_THEORY_PARENT
```

The terminal is a **baseline to beat**, not an ORION novelty claim.