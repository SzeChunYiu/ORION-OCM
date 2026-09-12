# GMI Domain Discovery Identifiability Theorems v1

Status: **FORMAL CLAIM-BOUNDARY HARDENING**

Status date: 2026-09-12.

Purpose:

> State what domain-discovery data can and cannot identify. Prevent finite biosphere searches from being misreported as proof that all domains have been found.

---

# 1. Setup

A registered discovery process induces a distribution `P` over accepted irreducible domain classes, including possibly unseen classes. A sampling unit is an independent frozen search-encoding × ecology-family × seed block, not one candidate evaluation.

Let `n` sampling units have produced a finite observed set `S_obs`.

---

# 2. Theorem DI-T1 — distribution-free unseen-count non-identifiability

For any finite discovery history, any positive integer `M`, and any `epsilon in (0,1)`, there exists an alternative domain-discovery distribution containing at least `M` additional unseen domain classes whose probability of producing no unseen-domain observation in the next `n` independent samples is

\[
(1-\epsilon)^n.
\]

This probability can be made arbitrarily close to one by choosing sufficiently small `epsilon`.

### Construction and proof

Take any distribution `P_0` supported on the already observed domain classes and scale every observed probability by `1-epsilon`. Introduce `M` new domain classes, each with probability `epsilon/M`. The total unseen mass is `epsilon` regardless of `M`. The probability that one draw lands in the observed support is `1-epsilon`, hence the probability that `n` independent draws contain no new class is `(1-epsilon)^n`. For fixed finite `n`, this tends to one as `epsilon -> 0`, while `M` is arbitrary. QED.

## Consequence

There is no finite, distribution-free upper confidence bound on the total number of machine-intelligence domains from discovery counts alone.

Chao, Good-Turing, Pitman-Yor or other richness estimators therefore require an explicit sampling/discoverability model. They are diagnostics under assumptions, not ontological completeness proofs.

---

# 3. Material-domain saturation

Absolute richness may be unidentifiable while **material undiscovered mass** remains testable.

Define a `p_min`-material domain as a domain whose probability of being recovered in one independent registered search unit is at least `p_min`.

## Theorem DI-T2 — detection bound for a material domain

If an undiscovered domain has per-unit independent recovery probability at least `p_min`, then the probability of missing it in `n` independent search units is at most

\[
(1-p_{min})^n.
\]

Therefore to make this miss probability at most `delta`, it suffices that

\[
n\ge
\frac{\ln \delta}{\ln(1-p_{min})}.
\]

### Proof

Each independent unit misses the domain with probability at most `1-p_min`; multiply across `n` units and solve the inequality. QED.

## Interpretation

GMI can make a defensible statement of the form:

> Under the frozen search mixture, no still-undiscovered domain with recovery probability at least `p_min` is supported at confidence `1-delta` after `n` independent no-new-domain trials.

It cannot infer that arbitrarily rare domains do not exist.

---

# 4. Theorem DI-T3 — grammar incompleteness cannot be disproved from internal search

Let neutral grammar `G` generate realization set `L(G)`. If a valid domain requires a carrier/operator primitive outside `L(G)`, no amount of search restricted to `G` can recover it.

### Proof

Every candidate produced by the search lies in `L(G)` by definition. A domain with no semantics-preserving representative in `L(G)` is unreachable. QED.

## Consequence

Search saturation inside one grammar is not domain saturation.

A completeness programme must include **grammar expansion attacks**:

```text
new state types
new operator arities
new topology constructors
new precision models
new physical/nonclassical primitives
new interaction/development semantics
```

If every materially broader grammar repeatedly yields new irreducible domains, the registered domain universe is empirically open-ended.

---

# 5. Theorem DI-T4 — duplicate discovery does not imply domain identity

Repeatedly recovering implementations with the same benchmark outputs does not establish one domain when their future intervention/development response differs.

This follows directly from the developmental semantic-state criterion: identity must be tested on the registered intervention/history family, not only present outputs.

Hence richness estimation must use **accepted domain equivalence classes**, not architecture names or benchmark-equivalent candidates.

---

# 6. Estimator usage rules

Use richness estimators only after:

```text
R1 search sampling unit is frozen
R2 domain-equivalence classifier is frozen
R3 parent-reduction decision rule is frozen
R4 independent search encodings are represented
R5 ecology coverage is declared
R6 discoverability heterogeneity is modeled or sensitivity-tested
```

Report separately:

```text
observed accepted domain count
singleton/doubleton counts
estimated unseen discovery mass
model-based richness estimate
p_min-material saturation bound
grammar version / description budget
```

Never collapse them into one “total number of domains” scalar.

---

# 7. Claim ceiling

Allowed future claim:

> Domain discovery is saturated for domains above declared material discoverability `p_min` under the registered search/grammar/ecology scope, at stated confidence.

Not allowed:

> All possible machine-intelligence domains have been discovered.
