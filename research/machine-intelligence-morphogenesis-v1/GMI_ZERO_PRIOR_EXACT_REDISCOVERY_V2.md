# GMI zero-prior exact rediscovery v2

Status: **WIDENED EXACT PROPERTY BENCHMARK / ISSUE #434 PARTIAL K4 EVIDENCE**

Date: 2026-09-12.

Purpose: widen the original tiny neutral-property microscope with additional known mechanism families while keeping historical architecture names out of the runner and preserving matched negative twins.

The runner minimizes a frozen exact semantic-loss-plus-burden objective over generic low-level realization candidates. It is still a hand-registered finite grammar and therefore not broad K4 closure.

## 1. Added mechanism pairs

### A. Noisy-cue cleanup versus exact indexing

Positive ecology: stored bit patterns are queried after bounded corruption. An exact-key mechanism misses the corrupted cue; a similarity/cleanup mechanism recovers the nearest registered pattern and pays extra search burden.

Negative twin: cues are exact. Both are semantically adequate and the cheaper exact index wins.

Property recovered: **content-addressable/associative cleanup only when cue corruption makes exact keys insufficient.**

### B. Confidence-bearing state versus point state

Positive ecology: hidden-state actions include a safe outside option whose value depends on confidence, so two evidence states with the same point/MAP hypothesis require different optimal actions.

Negative twin: only symmetric guess actions exist; MAP state is sufficient and cheaper.

Property recovered: **probabilistic belief only when protected decisions require uncertainty distinctions.**

### C. Per-query frontier work versus precompiled answer state

Positive ecology: large answer space, few queries; per-query search is cheaper than materializing every answer.

Negative twin: high reuse; precompilation amortizes and wins.

Property recovered: **search/frontier state from query-specific computation and low reuse.**

### D. Checker-gated admission versus direct admission

Positive ecology: proposal errors are common and costly while checking is cheap/reliable.

Negative twin: proposals are nearly always correct, wrong-adoption loss is small and checking is expensive.

Property recovered: **verification/admission only when its risk reduction exceeds retry/check burden or a hard constitution requires it.**

### E. Aggregation versus single predictor

Positive ecology: multiple equal-quality errors are uncorrelated and aggregation cost is low.

Negative twin: errors are perfectly correlated, so aggregation adds cost without variance reduction.

Property recovered: **ensemble/portfolio aggregation from error diversity, not model count itself.**

### F. Reusable transition model plus online planning versus direct compiled policy

Positive ecology: many goals reuse one dynamics model; model acquisition amortizes.

Negative twin: very few goals; direct policy compilation is cheaper.

Property recovered: **world-model/planning state from counterfactual reuse, not planning as a universal preference.**

### G. Shared core plus explicit residual state versus core-only/full rewrite

Positive ecology: a stable core has frequent sparse volatile exceptions; core-only violates semantics and full rewrite pays global update burden.

Negative twin: no volatile exceptions; the core alone is sufficient and residual machinery is unnecessary.

Property recovered: **external/residual memory only when predictive-target residual distinctions are real and sufficiently local/volatile.**

## 2. Exact finite benchmark

`run_gmi_zero_prior_exact_rediscovery_v2.py` evaluates fourteen frozen ecology cells: seven positive regimes and seven matched twins.

Expected unique winners:

```text
noisy cue                   -> similarity cleanup
exact cue                   -> exact index
confidence-sensitive action -> belief state
MAP-only action             -> point state
low reuse                   -> per-query search
high reuse                  -> precompiled state
high adoption risk          -> checker-gated admission
cheap error/high proposal   -> direct admission
diverse errors              -> aggregate
identical errors            -> single predictor
many reused goals           -> model + planning
few goals                   -> direct policy
volatile sparse exceptions  -> shared core + residual
stable core                 -> core only
```

The benchmark uses only exact finite costs and semantics; every predicted winner is checked against all candidates in its registered microgrammar.

## 3. Relation to v1

Together with v1/remint/multi-grammar microscopes, the exact property coverage now includes:

```text
shared coefficients versus records
recurrent versus memoryless state
fixed versus dynamic routing
symmetry tying versus free state
low-rank versus full residual state
associative cleanup
belief versus point state
search versus precompile
verification versus direct admission
ensemble aggregation
model/planning versus direct policy
external residual memory
```

This is broader calibration of the derivation machinery, not recovery of complete historical implementations.

## 4. Kill conditions

- If a candidate wins only because the target property was encoded as a privileged macro, classify grammar bias and remint/replace the grammar.
- If a strong generic competitor has lower exact burden, the GMI property prediction is RED at that cell.
- If the property is absent from the grammar, result is INCONCLUSIVE_GRAMMAR.
- No result here promotes a whole family to K4/K5 without independent learning-scale encodings and held-out generators.

## Claim ceiling

Exact hand-registered property rediscovery only. Issue #434 remains open for broad leave-one-family-out learning-scale neutral search.
