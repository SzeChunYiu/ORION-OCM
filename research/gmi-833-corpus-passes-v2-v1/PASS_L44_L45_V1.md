# PASS-L44 / PASS-L45 — proof-mode identification (finite-enum vs analytic support)

## L44 — proofs relying on finite enumeration where an analytic proof is possible

**Population (frozen):** all 49 P2 rows with support_kind == EXACT_FINITE_CERTIFICATE.
Mechanical pre-screen flagged 31 (universal scope + enum-only justification + no analytic
sibling row); every row was then read and adjudicated (ledger requirement: verdict + reason
per object; full per-row list in VERDICT_REGISTER_V1.json L44 section).

**Result: 49 DECLARED_FINITE_ONLY / 0 ENUMERATION_SUBSTITUTED / 0 UNKNOWN.**

Every row's scope_quantifier_class (or its registered scope column / receipt ceiling)
explicitly declares the finite universe being censused — the frozen-#939 "declared
enumeration is fine" pattern, e.g. forall_fin_declared_universe (all 3^9 = 19,683 response
tables...). The four closest calls were resolved by file evidence:

- CLM-5 ("all factor sizes >=2"): claims-table Scope column declares "k=2..4, sizes 2..4
  exhaustive microscope"; sibling CLM-4 carries the construction theorem.
- TT-1: theorem doc states "DERIVED + EXHAUSTIVELY ENUMERATED AT FINITE SCOPE",
  task-universality "by construction" (analytic).
- PN-5: package carries TT-5's short analytic task-independent argument; n in 3..8 declared.
- X-TMT9: tmt.py:429 claim ceiling restricts to "implementation checks ... on enumerated
  finite scopes".

Arrival rows 20-23 explicitly pair "analytic theorem + exhaustive census" in the registered
scope; LEGACY_113's infinite case carries a written geometric-series proof.

**Claim:** at the rescore-v2 population, no undeclared enumeration substitutes for a
plausibly-available analytic proof. Census-side COMPUTER_ASSISTED_EXHAUSTIVE claim-class
objects share the declared-universe registration pattern by construction of the census
extractor; screen-covered at P1 scope.

## L45 — analytic claims supported only by computation

**Population (frozen):** all 63 P2 rows with support_kind == ANALYTIC_PROOF.
Mechanical pre-screen flagged 1 (no .md citation or computation-only justification).
Per-row verification reads each row's proof-bearing document (priority: the flagged row +
census-vs-observed disagreement rows where census said ANALYTIC_DEDUCTIVE). Per-row list
and verdict distribution in VERDICT_REGISTER_V1.json L45 section.

**Claim:** recorded per verdict distribution; any COMPUTATION_ONLY row is individually
quoted with the missing-proof evidence. The L45 identification at P2 scope covers all 63
rows; P1-side ANALYTIC_DEDUCTIVE rows outside P2 are screen-covered only.
