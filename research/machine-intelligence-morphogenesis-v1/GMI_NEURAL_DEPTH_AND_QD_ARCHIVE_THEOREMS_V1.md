# GMI Neural Depth and Diversity-Archive Theorems v1

Status: **PARENT-THEOREM INTEGRATION + FORMAL ZERO-PRIOR HARDENING**

Status date: 2026-09-12.

Purpose:

> Close two structural gaps: why layered nonlinear composition can be a genuine resource-saving realization, and when maintaining diverse niche-specialized solutions has positive developmental value.

---

# 1. Neural depth is a resource variable, not just syntax

A generic feedforward nonlinear realization composes maps

\[
f=f_L\circ f_{L-1}\circ\cdots\circ f_1.
\]

The question is whether depth can change representation burden rather than merely rewrite the same function.

## Parent theorem ND-1 — depth separation exists

Established depth-separation results (including Telgarsky 2016 and Eldan–Shamir 2016) construct function families for which:

```text
one deeper network family represents/approximates the target with polynomial or small size;
a shallower network family with the same broad gate class requires exponentially larger width/size to achieve the registered approximation accuracy.
```

One concrete Telgarsky result gives families represented by networks with depth growing polynomially in a parameter `k` and constant nodes per layer, while substantially shallower networks require `Omega(2^k)` nodes. Eldan–Shamir give a function represented by a small 3-layer network that requires exponential width in dimension for a 2-layer approximation at fixed accuracy.

These are parent theorems; GMI does not claim originality for them.

## GMI consequence

There exist obligations where the natural structural complexity variable is **compositional depth**, and forcing the computation into a shallow coefficient map causes an exponential representation burden.

Thus a zero-prior GMI derivation can legitimately predict layered nonlinear composition when measured target structure exhibits reusable hierarchical composition.

### Negative twin

Depth is not universally beneficial. Linear targets, low-degree simple functions, or ecologies with severe sequential latency can favor shallow realizations. Representation savings must be compared against development and serving burden.

---

# 2. Representation depth does not imply trainability

Depth-separation establishes an expressivity/resource possibility, not developmental reachability.

`GMI_NEURAL_REACHABILITY_MICROTHEOREMS_V1.md` already provides an exact nonlinear counterexample where a representable ReLU solution is unreachable from an entire initialization region under the registered gradient update.

Therefore GMI must separately model:

```text
representation burden
optimization/development accessibility
serving latency/parallelism
generalization
```

A deep representation can be structurally efficient yet developmentally nonviable.

---

# 3. Niche-specialized future ecology

Consider `K` mutually exclusive future ecology niches. Future niche `J` is drawn from probabilities

\[
p_1,...,p_K,
\qquad\sum_jp_j=1.
\]

Suppose candidate `s_j` is admissible/high-quality only in niche `j`, and using an inadmissible candidate incurs failure loss `L_j>0`.

An archive can retain a subset `A subset {1,...,K}` of niche specialists. Retaining specialist `j` costs `c_j>=0` over the relevant horizon.

If niche `j` occurs and `j notin A`, pay `L_j`.

Expected archive objective is

\[
C(A)=\sum_{j\in A}c_j+\sum_{j\notin A}p_jL_j.
\]

## Theorem QD-1 — independent niche-retention threshold

When archive costs and niche losses are additive as above, specialist `j` should be retained iff

\[
c_j<p_jL_j.
\]

### Proof

Adding `j` to an archive changes objective by

\[
\Delta C=c_j-p_jL_j.
\]

It helps exactly when this is negative. QED.

### Interpretation

Diversity has no intrinsic value in the theorem. It has value because distinct future ecologies select different realizations and advance retention avoids adaptation/failure burden.

---

# 4. Single-winner versus full archive

For uniform niches `p_j=1/K`, equal failure loss `L`, and equal archive cost `c`, compare:

```text
single retained specialist:
    C_1=c + L(1-1/K)

full K-specialist archive:
    C_K=Kc
```

## Corollary QD-1.1

The full archive beats a single specialist iff

\[
(K-1)c<L(1-1/K),
\]

or equivalently

\[
c<\frac{L}{K}.
\]

Thus increasing niche count does not automatically justify unbounded archive growth: per-niche retention burden must fall below the probability-weighted avoided failure/adaptation loss.

---

# 5. Adapt-on-demand comparison

Suppose instead of retaining niche specialist `j`, the species can adapt from a base form after niche revelation at cost `a_j` and delay/risk penalty `d_j`.

Then archive retention is favored iff

\[
c_j<p_j(a_j+d_j).
\]

### GMI consequence

This produces a direct phase relation among:

```text
one universal solution
pre-retained diversity archive
on-demand adaptation/morphogenesis
```

The relevant variables are niche probability, adaptation burden, delay/risk, and archive maintenance—not the label `quality-diversity` itself.

---

# 6. Descriptor validity is a theory variable

A practical diversity archive indexes solutions by a behavioral/feature descriptor. If two future-relevant niches collide into one descriptor cell, storing only one elite can lose the other necessary specialist.

## Theorem QD-2 — descriptor collision no-go

If two niches `i != j` require mutually incompatible specialists but descriptor map `phi` satisfies

\[
\phi(i)=\phi(j),
\]

and the archive stores at most one occupant per descriptor value, then no archive policy over that descriptor can guarantee retaining both specialists simultaneously.

### Consequence

QD success depends on the descriptor being sufficiently fine for the future semantic/ecological distinctions. This is a direct semantic-quotient condition.

---

# 7. Zero-prior derivation consequence

GMI should derive a diversity archive when:

```text
future ecology has multiple recurrent niches
no single realization is cheap/admissible across all niches
niche identity is revealed late enough that adaptation is costly
retention/maintenance is cheaper than probability-weighted adaptation/failure
available descriptors preserve future-relevant niche distinctions
```

It should predict collapse toward one solution when niches disappear, one form dominates all niches, or archive/maintenance cost exceeds adaptation value.

---

# 8. Gap update

```text
neural layered composition:
    depth can yield exponential representation advantage       PARENT-THEOREM CLOSED
    target compositional-depth estimator                        OPEN
    developmental reachability/generalization                   OPEN-BLOCKING

quality-diversity/archive:
    additive niche retention threshold                          CLOSED
    single-winner/full-archive crossover                        CLOSED
    adapt-on-demand crossover                                   CLOSED
    descriptor collision no-go                                  CLOSED
    real niche distribution/descriptor discovery                OPEN
    open-ended diversity stability                              OPEN
```

---

# 9. Claim ceiling

Depth-separation does not imply that deeper is universally better or trainable. The archive theorem does not prove MAP-Elites or any specific QD algorithm optimal. Both results identify architecture-neutral structural pressures that neutral search should recover when their assumptions hold.
