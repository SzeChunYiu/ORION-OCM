# GMI Biosphere Scaling and Multi-Fidelity Triage v1

Status: **EXPERIMENTAL SYSTEMS HARDENING / SEARCH-COST CONTROL**

Status date: 2026-09-12.

Refs: `GMI_MACHINE_INTELLIGENCE_BIOSPHERE_V1.md`, `GMI_BIOSPHERE_EXPERIMENT_PROTOCOL_V1.md`.

Purpose:

> Make exploration of millions of raw morphology candidates computationally possible without turning cheap proxy selection into a hidden bias that predetermines the species discovered.

---

# 1. The scaling problem

If morphology grammar yields candidate set `G` with millions or more elements, full training/evaluation cost

\[
\sum_{g\in G}B_{full}(g)
\]

is infeasible.

But aggressive early stopping can erase exactly the developmental phenomena GMI wants to study:

```text
slow generalization / grokking
expensive verifier setup with cheap long-run serving
high initial compilation with long reuse
morphologies whose advantage appears only after regime change
specialists in rare niches
```

Therefore triage itself is part of the scientific protocol.

---

# 2. Fidelity ladder

Use staged fidelity levels.

```text
F0 STATIC VALIDITY
   type checking, semantic interface validity, obvious resource lower bounds,
   duplicate/canonical-equivalence elimination

F1 EXACT MICROSCOPES
   tiny finite tasks with exhaustive or near-exhaustive correctness checks

F2 CHEAP PROXY ECOLOGIES
   small state/data/model budgets, short horizons, synthetic tasks

F3 DEVELOPMENT ECOLOGY SUBSET
   real learning with a subset of D ecologies and partial lifecycle horizon

F4 FULL DEVELOPMENT + LIMITED VALIDATION
   complete D and bounded V evaluation

F5 PROTECTED CONFIRMATION
   frozen full-fidelity P ecologies; one-shot claim evaluation

F6 REAL-REGIME / PARENT-REDUCTION
   expensive code/math/science/control transfer and closest-parent attacks
```

Promotion cost is charged to `B_search`.

---

# 3. Static elimination rules

F0 may eliminate a candidate only for architecture-neutral reasons such as:

```text
invalid type/interface
semantic impossibility proved by quotient/no-go theorem
hard resource budget violation
exact duplicate under canonicalization
strict dominance by implementation-equivalent realization with proof
```

F0 MUST NOT eliminate a candidate merely because it lacks a familiar architecture pattern.

---

# 4. Canonicalization and duplicate collapse

Compute canonical fingerprints over:

```text
typed graph structure
state primitive multiset
routing/update/verifier/memory mechanism vector
registered invariances
exact small-world response signature
```

Use semantic remints before fingerprint comparison where feasible.

Candidate collisions are then checked by stronger developmental probes before permanent merge.

This converts raw genotype count into a smaller set of provisional phenotype classes.

---

# 5. Diversity-preserving promotion

Naive top-k promotion from F2/F3 is forbidden.

Maintain promotion strata by:

```text
mechanism vector
behavioral novelty cell
niche/ecology signature
resource profile
lineage
```

Reserve promotion budget for:

```text
highest quality per cell
highest novelty per cell
uncertain candidates with high value-of-information
slow-starting candidates selected by developmental diagnostics
random audit sample of apparently weak candidates
```

This permits estimation of false-negative bias in the triage process.

---

# 6. Slow-development protection

Each candidate declares or inherits a maximum development horizon class.

Promotion uses learning-curve descriptors rather than only endpoint score:

```text
slope
curvature
representation/mechanism transition indicators
verification/compilation amortization forecast
stability/plasticity trend
```

A candidate may receive a horizon extension if registered diagnostics predict a delayed mechanism transition.

The extension rule is frozen on D/V and charged.

Protected evaluation does not grant ad hoc extensions based on desired outcome.

---

# 7. Multi-fidelity surrogate

A surrogate may estimate

\[
\hat Y_{F5}(g,e)
\]

from low-fidelity descriptors, but:

```text
surrogate training uses D/V only;
uncertainty is reported;
feature inputs exclude protected outcome/world identity;
promotion reserves random exploration to detect surrogate blind spots;
search cost for surrogate training is charged.
```

A candidate's scientific claim is based on measured F5/F6 outcomes, never surrogate predictions alone.

---

# 8. Value-of-information promotion

For candidate `g`, define a registered acquisition score schematically:

\[
A(g)=
\frac{
\text{expected reduction in frontier/species uncertainty}
}{
\text{expected next-fidelity burden}
}.
\]

This is a search heuristic, not a theory truth criterion.

Useful uncertainty targets include:

```text
is candidate actually non-dominated?
is it a new species or implementation duplicate?
does it distinguish two competing GMI mechanisms?
does it test an unoccupied ecology niche?
```

---

# 9. Search islands

Partition massive search into partially independent islands:

```text
I1 gradient-friendly differentiable forms
I2 symbolic/program forms
I3 memory/retrieval forms
I4 verifier/search forms
I5 probabilistic/Bayesian forms
I6 heterogeneous composites
I7 unrestricted mixed grammar
```

Periodic migration transfers generic subgraphs/modules, not architecture labels.

This reduces premature monoculture and improves coverage of qualitatively different realizations.

---

# 10. Search encoding replication

A high-value species receives independent rediscovery attempts under at least three substantially different search encodings before strong novelty language.

Evidence order:

```text
one search encoding -> candidate
second encoding -> recurrence
third encoding + remint -> stronger recurrence
fresh protected ecology -> confirmation
parent reduction -> novelty residual
```

---

# 11. Audit of triage bias

Periodically sample candidates rejected at each fidelity and promote them anyway.

Estimate:

```text
false-negative rate for eventual frontier membership
false-negative rate by mechanism family
false-negative rate by development horizon
false-negative rate by resource profile
```

If triage disproportionately eliminates a family, either correct the proxy or lower the claim ceiling for biosphere completeness.

---

# 12. Massive-run accounting

Report at least:

```text
raw genotypes generated
canonical provisional classes
F1/F2/F3/F4 promotions
F5 protected confirmations
F6 real-regime candidates
search compute
failed-candidate compute
surrogate compute
archive size
species count by novelty tier
```

Do not report “millions of species” when the actual number is millions of raw genotypes.

---

# 13. Stopping criteria

A biosphere campaign may stop for a registered budget when:

```text
frontier hypervolume improvement saturates
new niche/species discovery rate falls below threshold
triage-audit false-negative rate is bounded
multiple search encodings converge on similar species archive
remaining high-value uncertainties exceed available budget
```

This is budgeted closure, not proof of exhaustive search.

---

# 14. Claim boundary

Multi-fidelity triage supports scalable discovery only if its bias is measured.

A species found after triage is not stronger evidence because many candidates were searched; a missed species cannot be ruled out unless search completeness/bias is itself bounded.
