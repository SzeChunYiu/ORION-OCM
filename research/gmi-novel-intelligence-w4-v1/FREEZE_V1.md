# Novel intelligence W4 freeze V1

Frozen **before** family-wide neutral search on this branch.

Authority targets: #592 item 39 (W4), #602 P4 residual novelty (morphology residual).
Upstream: #796 `gmi-unseen-form-prediction-v1` (V6 closed; W4 not claimed).

## Freeze seed

```text
sha256("GMI-NOVEL-INTELLIGENCE-W4-V1/RQM-FAMILY-RECURRENCE")
  = 57ddb8d1195e0eba61e0527828882bce1f9e0da24a4474ef3a69b7c6c71789c9
```

Upstream freeze (must remain intact; not re-owned here):

```text
sha256("GMI-UNSEEN-FORM-PREDICTION-V1/RQM-SPARSE-ALIAS")
  = d8e9eac97a9ce7ee3735efe5cc77bef40d6ab611712cd7bccd3fae3f2550030b
```

## Why upstream W4 was refused

#796 earned W2/W3 on a **single** registered exact ecology (plus remint + one
held-out). Novelty-ladder W4 requires a **recurrent**, parent-nonreducible
structural domain at registered scope. Single-scope recovery is not recurrence.

## Registered parametric family F(k)

For each integer `k ∈ {2,3,4}` construct sparse-alias ecology:

```text
fiber 0: k histories, predictive class 0, targets {0..k-1}     → m(0)=k
fiber 1: k histories, predictive class 1, targets {k,k+1} alt → m(1)=2
max_m = k
|S_P| = 2
|S_O| = k+2
C*    = 2+k
flat  = k+3
material gap vs flat = 1
```

Concrete members (property-first, before search):

| k | |H| | C* | flat | role |
|---|-----|----|------|------|
| 2 | 4 | 4 | 5 | family |
| 3 | 6 | 5 | 6 | family (= upstream primary shape) |
| 4 | 8 | 6 | 7 | family (= upstream held-out shape) |

## Property-first family law (C0) — stated before search

For every `k` in F:

```text
PVF1  exact target recovery on all histories
PVF2  predictive quotient fixed to registered q_P(k)
PVF3  residual alphabet size >= max_m = k (tight)
PVF4  composition decoder d(p,r) -> target
PVF5  zero-residual impossible under q_P(k)
PVF6  min cost C* = 2+k < flat = k+3
```

No architecture macro (`RQM`/`RAG`/`Transformer`) enters the search grammar.
Search remains conditional on registered `q_P(k)`.

## Fixed-budget parent (pre-registered kill)

```text
B = 3   # constant residual alphabet, independent of measured max_m
```

Prediction before search:

```text
k=2 < B : recovers but overprovisions (does not track max_m)
k=3 = B : locally matches (family recurrence must kill elsewhere)
k=4 > B : fails exact recovery
```

Therefore a single fixed budget is **not** the residual-quotient family law.

## Fresh residual-specific prediction (outside family)

Held-out `k'=5 ∉ {2,3,4}`:

```text
max_m' = 5
C*'    = 7
flat'  = 8
fixed-budget B=3 fails recovery
```

## Explicit non-claims

- Not J4 `NEW_DOMAIN` (no distinct primitive carrier / operator claim).
- Not atlas phase-hole occupancy (known-parent negative from open-niche stands).
- Not `NEW_FORM_OF_INTELLIGENCE_PROVEN`.
- Not P4 surviving-unseen-domain.

## Terminals allowed only after all W4 boxes

```text
W4_RESIDUAL_QUOTIENT_STRUCTURAL_DOMAIN_AT_REGISTERED_FINITE_FAMILY_SCOPE
NOVEL_INTEL_LADDER_W2_W3_W4_GREEN_AT_EXACT_RQM_FAMILY_SCOPE
```
