# GMI Domain Capability Identifiability Theorems v1

Status: **FORMAL CLAIM-BOUNDARY / PREDICTIVE HARDENING**

Status date: 2026-09-12.

Purpose:

> State when a domain's scaling law, capability ceiling, or weakness can actually be inferred. Prevent finite-resource curves from being mistaken for proofs of asymptotic capability.

---

# 1. Setup

Let a scalarized protected capability function for domain `D` be

\[
C_D(R)
\]

where `R` is one frozen resource coordinate and all other ecology/context variables are held fixed.

Assume only that capability is bounded and nondecreasing in `R` over the registered regime.

---

# 2. Theorem CI-T1 — finite scaling data do not identify the asymptote

For any finite set of observations

\[
(R_1,c_1),\ldots,(R_n,c_n),
\qquad R_1<\cdots<R_n,
\]

with nondecreasing `c_i`, and any two ceiling values

\[
L_a,L_b\ge c_n,
\]

there exist bounded nondecreasing continuation functions `C_a(R)` and `C_b(R)` that match every observed point exactly but satisfy

\[
\lim_{R\to\infty}C_a(R)=L_a,
\qquad
\lim_{R\to\infty}C_b(R)=L_b.
\]

### Proof

Interpolate the observed points monotonically on `[R_1,R_n]`. Beyond `R_n`, define for example

\[
C_a(R)=c_n+(L_a-c_n)(1-e^{-(R-R_n)})
\]

and analogously for `L_b`. Both are bounded, nondecreasing, and agree at all observed points, while having different asymptotes. QED.

## Consequence

Finite empirical scaling curves alone cannot prove that a domain has a hard capability ceiling or that it will eventually reach a high ceiling.

A “weak domain” asymptotic claim requires at least one of:

```text
formal impossibility/lower-bound theorem
mechanistic saturation law with independently measured bottleneck
registered response family justified before protected extrapolation
held-out resource-range prediction
cross-ecology replication of the same asymptote mechanism
```

---

# 3. Theorem CI-T2 — finite scaling data do not identify the exponent

For any finite positive observations compatible with monotone improvement, there exist multiple smooth monotone functions agreeing arbitrarily closely on the observed interval while having different asymptotic scaling exponents or even different qualitative forms beyond it.

### Constructive argument

Fit any baseline monotone interpolant `f(R)` on the observed compact interval. Multiply a late-activating smooth correction by a bump/switch function that is arbitrarily small on the observed interval but dominates for `R` above a chosen unobserved threshold. This produces functions that are observationally indistinguishable at current resources yet become power-law, logarithmic, thresholded, or saturating later.

## Consequence

Estimated neural-style power-law exponents must not be promoted to universal domain laws merely because the local fit is good.

---

# 4. Structural ceilings are identifiable when a theorem exists

Examples:

```text
local-field light-cone theorem:
    remote information cannot affect output before distance/radius rounds

pure-selection support theorem:
    a missing heritable type has zero discovery probability without novelty operators

strict-local-relaxation trap theorem:
    a non-global strict local minimum creates permanent failure from that state

finite-context theorem:
    histories with same visible suffix but different target state cannot be solved exactly
```

These yield genuine ceilings or latency lower bounds because they derive from the allowed state/operator law, not curve extrapolation.

---

# 5. Domain capability interval rather than point prediction

Before strong empirical closure, predict an interval or envelope

\[
C_D(R)\in[L_D(R),U_D(R)]
\]

where:

```text
L_D  constructive lower bound from an explicit realization
U_D  impossibility/resource upper bound from theory or strongest parent constraints
```

The interval narrows as theory improves.

A domain is quantitatively well explained only when protected outcomes fall inside the frozen envelope and unexplained residuals have no registered structure.

---

# 6. Crossover identifiability

Suppose domains `A` and `B` have burden/capability frontiers `F_A(R)` and `F_B(R)`. Observing `A` better than `B` over a finite range does not prove permanent dominance.

A predicted crossover at `R*` is scientifically stronger when `R*` is derived from independently measured mechanism terms rather than fitted directly from the same protected performance curves.

For example:

\[
R^*=\frac{C_{compile}}{c_{direct}-c_{serve}}
\]

is interpretable because the threshold arises from lifecycle accounting. A free breakpoint selected after seeing outcomes is not equivalent evidence.

---

# 7. Weak-domain admission rule

Classify a domain as structurally weak only with a declared mechanism:

```text
W1 semantic impossibility
W2 finite-speed/communication ceiling
W3 novelty-supply ceiling
W4 local-trap/search explosion
W5 precision/noise ceiling
W6 update/interference ceiling
W7 economic/lifecycle domination
W8 narrow-niche dependence
```

For W1-W6, prefer formal lower bounds. For W7-W8, require prospectively frozen resource/ecology response laws and matched negative twins.

---

# 8. Predictive hardening loop

For every domain capability claim:

1. type the capability coordinate;
2. identify the mechanism term that limits or improves it;
3. derive an exact bound if possible;
4. construct an explicit realization lower bound;
5. freeze competing response laws;
6. hold out resource ranges and ecology families;
7. test crossover and negative twin;
8. inspect structured residuals;
9. refine locally rather than replacing failures with post-hoc prose.

---

# 9. Claim ceiling

Allowed:

> GMI predicts a registered capability envelope and specific mechanism-limited failure modes for this domain.

Not allowed from finite scaling data alone:

> This domain will never become strong no matter how far it scales.

or

> This domain will eventually surpass all others.
