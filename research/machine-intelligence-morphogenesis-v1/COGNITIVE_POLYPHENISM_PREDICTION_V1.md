# Cognitive Polyphenism — prospective missing-morphology prediction v1

Status date: 2026-09-11.

Status: **PROSPECTIVE GMI PREDICTION / CANDIDATE MISSING MORPHOLOGY. NOT YET ESTABLISHED AS A NEW FORM OF MACHINE INTELLIGENCE.**

Refs: #377, #233, #373, `GMI_THEORY_V1.md`, `GMI_CORE_ANSWER_V2.md`, `GMI_MORPHOLOGY_SELECTION_NO_GO_V1.md`, `PHASE_HOLE_AUDIT_V2.md`, `UNKNOWN_MORPHOLOGY_PROGRAMME_V1.md`.

This file freezes a risky prediction before any neutral morphology search is allowed to count as evidence.

---

# 1. Why GMI should make a morphology prediction

Track B already has two results that jointly create a nontrivial pressure:

1. the least implementation-dependent cognitive object is a **semantic developmental state**, not one architecture;
2. the realization that is resource-optimal can reverse when ecology, verifier, hardware, revision rate or horizon changes.

A persistent general machine therefore faces a problem that a fixed morphology does not solve cleanly:

```text
shared developmental meaning should persist
while
resource-optimal executable form changes across regimes.
```

A static hybrid can keep many forms alive simultaneously, but then every semantic revision risks synchronization/update cost across all of them. A single fixed form avoids synchronization but pays morphology-mismatch cost in regimes where another realization is much better.

GMI therefore predicts a third organization in sufficiently heterogeneous long-lived ecologies.

---

# 2. Predicted morphology: Cognitive Polyphenism (CP)

**Cognitive Polyphenism** is a machine-intelligence organization in which the persistent developmental state is separated from the transient executable morphology used in a particular regime.

A candidate CP system has the form

\[
\mathcal P=(Z,\Lambda,\mathcal R,\{\kappa_r\},U,\Gamma,\rho),
\]

where:

- `Z` is an authoritative persistent semantic/developmental state;
- `Lambda` is a version/dependency structure linking semantic state to derived realizations;
- `R` is a set of resource/verifier/ecology regimes;
- `kappa_r` compiles/materializes an executable phenotype for regime `r`;
- `U` updates the authoritative state from experience;
- `Gamma` may change the compiler family/factorization itself;
- `rho` measures complete build/compile/serve/update/verification/maintenance burden.

The executable phenotype for regime `r` is

\[
P_r=\kappa_r(Z).
\]

Phenotypes may be discarded, cached, invalidated, rebuilt or replaced. The **persistent identity of the intelligence is not any one phenotype**.

Examples of possible phenotypes include a dense numerical predictor, an exact program, a probabilistic circuit, a retrieval structure or a formally checkable explicit representation. These labels are examples only; the theory prediction is the source/phenotype organization, not a hand-coded list of architecture classes.

---

# 3. Distinguishing CP from ordinary hybrids

The prediction is **not** merely “combine neural + symbolic + memory.”

A CP candidate must satisfy all of the following registered properties.

## CP-1 — authoritative shared developmental state

There is a persistent state whose update does not require eagerly editing every executable phenotype.

## CP-2 — regime-conditioned phenotype materialization

At least two materially different executable organizations can be generated from the shared state under different registered resource/verifier regimes.

## CP-3 — lazy invalidation / recompilation

A semantic update may invalidate phenotype fragments, but inactive phenotypes need not be synchronously rebuilt. Recompilation can be delayed until use while preserving registered correctness/version semantics.

## CP-4 — semantic round-trip constraint

Different phenotypes must preserve the same registered semantic developmental distinctions within the declared compiler tolerance. Merely running unrelated specialist models behind a router does not qualify.

## CP-5 — developmental sharing

Experience acquired through one phenotype must be able to modify shared future cognition in another phenotype without re-learning the whole task from scratch.

## CP-6 — open phenotype family

The system is not limited to choosing among a frozen human-labelled portfolio. `Gamma`/compiler development may construct new executable realizations from a lower-level grammar.

A fixed MoE, fixed model selector or hand-written neuro-symbolic pipeline can be a parent control, but does not satisfy CP merely by containing multiple modules.

---

# 4. Exact phase argument

Consider an idealized ecology with `k` recurrent regimes. On each step:

- the next regime is sampled uniformly;
- an authoritative semantic update occurs independently with probability `q` before the query;
- a cached phenotype becomes stale after any semantic update until that phenotype is recompiled.

For a particular phenotype, the probability it is stale when next queried is

\[
\sigma(k,q)
=
\frac{q}{1/k+q-q/k}.
\]

Reason: the inter-arrival time for a regime is geometric with success probability `1/k`; averaging the probability of at least one update over that inter-arrival distribution gives the expression above.

Let:

- `s_P` = CP serving cost per query after materialization;
- `u_0` = authoritative-core update cost;
- `c` = phenotype recompile cost;
- `s_H` = eager static-hybrid serving cost;
- `e` = eager update/synchronization cost per maintained phenotype.

Then the expected CP cost per query in this exact toy model is

\[
C_P
=
s_P+q u_0+c\,\sigma(k,q),
\]

while an eager `k`-phenotype hybrid has

\[
C_H
=
s_H+qke.
\]

For fixed `q>0` and `e>0`,

\[
C_H=\Theta(k),
\]

whereas

\[
\lim_{k\to\infty} C_P=s_P+qu_0+c.
\]

Therefore, provided compilation is finite, there exists a heterogeneity level above which lazy phenotype materialization is cheaper than eagerly synchronizing every phenotype.

Against a single fixed specialist with matched serving cost `s_f` and average cross-regime mismatch penalty `m`, CP can additionally win when

\[
s_P+qu_0+c < s_f+m
\]

in the large-`k` limit.

This is not claimed as novel mathematics. It is the exact economic pressure that generates the CP prediction.

---

# 5. Prospective phase prediction

CP is predicted to move toward the developmental frontier when **all or most** of the following hold:

```text
many recurrent verifier/resource regimes
substantial semantic/developmental overlap across regimes
specialist realizations have genuine regime-specific advantages
semantic updates/revisions continue over the machine lifetime
recompilation can be deferred or localized
inactive phenotype count is much larger than simultaneously active phenotype count
reuse horizon is long enough to amortize compilation
cross-regime transfer is valuable
```

The strongest positive region is therefore:

\[
\boxed{
\text{high regime heterogeneity}
+\text{high semantic overlap}
+\text{ongoing revision}
+\text{sparse phenotype activity}
+\text{finite compilation cost}
}
\]

---

# 6. Negative-twin predictions

The theory must predict where CP should **lose**.

## N1 — homogeneous ecology

If only one or two stable regimes matter, an eager specialist/hybrid can dominate because source/compile machinery is overhead.

## N2 — phenotype compilation too expensive

If rebuilding a phenotype is comparable to full retraining and regimes recur frequently after updates, eager maintained models can dominate.

## N3 — little shared developmental semantics

If regimes share almost no reusable state, a common authoritative core adds indirection without transfer benefit.

## N4 — switching faster than materialization

If the active regime changes faster than a phenotype can be compiled/amortized, a broad fixed realization may dominate.

## N5 — semantic source becomes the bottleneck

If every phenotype query requires expensive traversal of the authoritative state, CP collapses into a slow interpreter rather than a compiled morphology.

A valid experiment must include at least one positive region and at least two of these negative twins.

---

# 7. Why this is a candidate *new form* rather than a renamed known architecture

The initial parent subtraction found strong partial parents but no direct parent matching the whole prediction.

### Fixed model switching / algorithm selection

Multi-model control and algorithm selection choose among pre-existing models. CP additionally predicts **shared developmental authority plus construction/reconstruction of phenotype realizations**, not only selection.

### MoE / modular systems

Mixture-of-Experts and modular continual learners route to persistent modules. CP permits the executable phenotype itself to be disposable and regenerated from shared developmental state; phenotype identity is not the machine's persistent knowledge identity.

### Neuro-symbolic / MRKL / agent-tool hybrids

These combine fixed heterogeneous components. CP predicts an **open phenotype family** and resource/verifier-conditioned re-realization from a common semantic authority.

### Hypernetworks / conditional neural computation

Hypernetworks generate parameters, but normally inside one neural realization family. CP requires cross-realization semantic equivalence and allows non-neural phenotypes.

### Materialized views / self-adjusting computation

Database materialized views, provenance and self-adjusting computation are extremely strong systems parents for lazy derived state and change propagation. CP explicitly imports this principle. The unresolved question is whether making it the developmental organization of an intelligence system across heterogeneous cognitive realizations yields a developmentally/resource-distinct morphology rather than an ordinary software product.

### DreamCoder / library learning / CoEvo

These learn reusable symbolic/program components and can use multiple representations. CP requires the stronger source-to-multiple-phenotype semantics plus regime-conditioned materialization and cross-phenotype developmental transfer.

### Modular memory / model editing / unlearning

SERAC, modular continual learning, exact/approximate unlearning and adapter isolation address local updates. They are mandatory controls. CP is stronger only if the same authoritative developmental state can regenerate materially different realization families and the lazy multi-phenotype scaling matters.

Current literature therefore supports only:

```text
NO_DIRECT_PARENT_MATCH_FOUND_IN_INITIAL_AUDIT
```

not:

```text
NEW_FORM_OF_INTELLIGENCE_DISCOVERED.
```

---

# 8. Frozen structural signature for neutral search

If a later neutral morphology search is allowed, the prediction is counted as correct only if high-frontier survivors independently exhibit most of this signature **without these structures being named as primitives**:

1. a small persistent substructure shared across many regimes;
2. regime-conditioned derived execution substructures;
3. materially different derived execution organization across at least two regimes;
4. low eager mutation of inactive regime-specific state after a shared update;
5. selective reconstruction/re-activation on later demand;
6. cross-regime transfer mediated by the shared persistent substructure;
7. version/dependency behavior sufficient to prevent stale derived state from silently certifying itself;
8. a negative-twin ecology in which the same signature becomes less favorable.

If search instead finds a fixed MoE, ordinary modular network, one universal interpreter or a hand-recognizable standard hybrid with equal/better resources, terminal:

```text
COGNITIVE_POLYPHENISM_PARENT_PRODUCT_SUFFICIENT.
```

---

# 9. Falsifiable theory claims

The prediction creates five concrete failure points.

```text
CP-P1  increasing regime diversity should increase CP relative advantage after a crossover
CP-P2  increasing semantic overlap should increase cross-phenotype developmental transfer
CP-P3  increasing compilation cost should eventually reverse the advantage
CP-P4  under positive-region pressure, neutral search should recover the frozen CP signature more often than in negative twins
CP-P5  if CP is truly distinct, strongest fixed-hybrid/model-switching/materialized-view parent implementations should not bounded-compile it with equal developmental/resource behavior
```

Failure of P1–P4 kills the predictive morphology claim at the tested scope. Failure of P5 kills novelty even if CP remains an engineering pattern.

---

# 10. Current terminal

This file upgrades Track B from “unknown morphology not predicted” to a **prospectively specified candidate morphology prediction**, while deliberately keeping discovery locked.

```text
MISSING_MORPHOLOGY_PROPERTY_VECTOR_PREDICTED_V1
COGNITIVE_POLYPHENISM_IS_THEORY_DERIVED_CANDIDATE
PARENT_FRONTIER_HOLE_NOT_YET_EMPIRICALLY_ESTABLISHED
NEUTRAL_UNKNOWN_MORPHOLOGY_SEARCH_NOT_YET_COUNTABLE_AS_DISCOVERY
NEW_FORM_OF_MACHINE_INTELLIGENCE_NOT_YET_ESTABLISHED
```

The next requirement is not more prose. It is a frozen parent-frontier experiment that tries to make this prediction fail.
