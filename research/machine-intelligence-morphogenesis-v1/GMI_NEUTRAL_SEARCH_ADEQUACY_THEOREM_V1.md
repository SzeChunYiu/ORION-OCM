# GMI neutral-search adequacy theorem v1

Status: **FORMAL SEARCH-DIAGNOSTIC LAW / B3, T9 NARROWING**

Date: 2026-09-12.

Purpose: distinguish a theory prediction failure from a grammar/search failure in zero-prior rediscovery.

## 1. Registered finite-cap search problem

Let a low-level grammar `G` induce a finite candidate set

\[
\mathcal R_C(G)=\{r:\text{description/resource generation cost}\le C\}
\]

under a frozen semantic evaluator and lifecycle meter. Historical family names/macros are absent.

Let `F` denote the prospectively predicted implementation-invariant property/mechanism class.

## 2. Theorem NS-1 — exhaustive finite-cap completeness

If search enumerates every element of `R_C(G)` and evaluates each exactly under the frozen objective, then the returned minimizer is globally optimal **within that registered grammar and cap**.

Consequences:

1. If an independently constructed witness `r_F in R_C(G)` has the predicted property and admissible semantics but exhaustive search returns a strictly better non-`F` realization, the protected result is evidence against the stronger claim that `F` is frontier-optimal at that cell.
2. If no admissible `F` witness exists in `R_C(G)`, failure to recover `F` is `INCONCLUSIVE_GRAMMAR`, not theory falsification.
3. If a witness exists but a non-exhaustive algorithm fails to find any comparably good known control realization, outcome is `INCONCLUSIVE_SEARCH`.

## 3. Theorem NS-2 — stochastic witness recovery bound

Suppose independent search draws have probability at least `p_min>0` of sampling some admissible witness set `W subset R_C(G)`. After `n` draws,

\[
Pr(\text{miss all witnesses})\le(1-p_{min})^n\le e^{-np_{min}}.
\]

Thus to bound witness-miss probability by `delta`, it suffices that

\[
n\ge \frac{\log(1/\delta)}{p_{min}}.
\]

Without a positive discoverability lower bound, finite stochastic search cannot certify adequacy.

## 4. Multi-encoding recurrence gate

For independent grammars/encodings `G_1,...,G_m`, each must have its own expressivity witness and search-adequacy audit. A property recurring across disjoint encodings is stronger evidence than repeated recovery under remints of one grammar, but recurrence cannot rescue a grammar that encoded the target as a privileged macro.

Required reporting per encoding:

```text
primitive inventory
description/candidate cap
constructive expressivity witness kept outside search ranking
search coverage or p_min claim
known-control recovery rate
best recovered objective
property/mechanism verdict
```

## 5. Protected classification table

```text
prediction wrong + adequate exhaustive/controlled search -> THEORY_RED
prediction right + witness exists + search controls fail -> INCONCLUSIVE_SEARCH
prediction not expressible -> INCONCLUSIVE_GRAMMAR
prediction recovered across independent encodings -> K4 evidence at registered scope
```

## Claim ceiling

This closes the logical attribution problem for B3/T9. It does not provide the broad grammars, independent encoders, million-candidate search runs or held-family K4 receipts themselves; those remain OPEN-BLOCKING.
