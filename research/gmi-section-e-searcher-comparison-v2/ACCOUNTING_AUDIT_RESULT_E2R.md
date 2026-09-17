# E2R alternative-accounting audit result

Ticket: `REV-L49-L53-SEARCHER-ACCOUNTING` (#833). Freeze: `ACCOUNTING_AUDIT_FREEZE_E2R.md` (commit `9be2bf38`, pre-outcome; erratum E1 dated post-first-run). Witness: `accounting_audit_e2r.py`; receipt: `ACCOUNTING_AUDIT_RESULT_E2R.json` (sha256 `a81c50923c18847c81e7cff69e7d9d0f5cb16052faa7ce8c2c9d5f1595ca455e`, executed on billy-laptop 2026-09-17). Frozen E2 tests re-run green (10/10) beside the audit (12/12); no frozen file was modified.

## Accountings audited (each stated and justified in the freeze)

| id | accounting | unit / rule | cap (grounding) |
|----|-----------|-------------|-----------------|
| A0 | preregistered (reference) | 32 truth-touches per verification; discrete cache free; arithmetic separate | 320 (frozen) |
| A1 | count-based | 1 unit per complete candidate evaluation; cache kept; final verify charged | 10 (= frozen "ten full discrete candidate evaluations") |
| A2 | exec-based (#978 EXEC-B precedent) | 1 exec per single-example execution; no cache discount (EXEC-B's no-memoization rule) | 320 (frozen number read as example-executions) |
| A3 | resource-price (arithmetic-op-dominant) | `26*touches + arithmetic_ops`; 26 = derived per-example ops of the cheapest registered routine | 8320 (= 320*26, frozen identity) |
| A3B | resource-price, no cache | as A3; re-visited discrete masks charged (cache-dominant weighting removed) | 8320 |
| A4 | count-based, shared-verifier-exempt | as A1; final shared exact verifier charged to the ecology, not the method | 10 |

`26` is derived at audit time by instrumented run of the frozen `relaxed_loss` (832 ops / 32 examples), cross-checked against the frozen law; it is not hardcoded into any formula's meaning.

## Verdicts per accounting

Costs are exact rationals (full table in the receipt). Adjudication states:

| verdict | A0 | A1 | A2 | A3 | A3B | A4 |
|---------|----|----|----|----|-----|----|
| V-RAND (5/16 at cap) | at | at | at | at | at | at |
| V-STRICT (0, under cap) | within | within | at | within | at | within |
| V-DRIFT (finite < 1, under cap) | within | within | within | within | within | within |
| V-NAS (exact, OVER cap) | over | over | over | over | over | **at (FLIP)** |
| V-DARTS (exact, within cap) | within | within | within | within | within | within |

Success values are accounting-independent and reproduced exactly (5/16; 0/`STRICT_ELITIST_PLATEAU`; 12/125; 72696/390625; masks 21/21; 2122 ops).

## Claim-level outcome

- **C-NAS-OVER** ("ablation exact but over the primary cap") — **ACCOUNTING_SENSITIVE**, flip witness registered: under A4 (shared-verifier-exempt count accounting) the ablation sits exactly AT the cap (10 relaxed evaluations = 10 units) instead of over it (352 > 320 under A0). This is the concrete #833-box counterexample: a reasonable accounting under which the frozen wording of the sub-verdict fails.
- **C-NAS-AT-OR-OVER (revived at original strength)** — under every declared accounting the ablation method consumes the entire evaluation budget or more (`over` under A0–A3B, `at` under A4); it is never strictly within budget; the DARTS representative is strictly cheaper under every declared accounting (2/64/3786/3786/1 vs 11/352/17472/17472/10). The over-cap content is re-established as accounting-robust once the verdict is stated as "at-or-over with zero budget slack" rather than "strictly over".
- **C-ORDERING** (claim ceiling `FINITE_EXACT_SAME_WORLD_PARENT_SEARCHER_COMPARISON_E2`; finite-budget recovery is search-mechanism dependent; no universal dominance) — **ACCOUNTING_ROBUST**: under all five accountings the five searchers remain pairwise distinct in the (cost-state, success) projection (verified programmatically; detail in receipt `ordering_detail`).

## Disposition

The `UNAUDITED_COST_DEPENDENT` (L49) and `UNTESTED_SCALARIZATION_DEPENDENT` (L53) flags on `gmi-section-e-searcher-comparison-v2` are discharged: the cost/scalarization dependence is now audited under five materially distinct reasonable accountings, with exactly one registered flip (V-NAS under A4), a revived at-original-strength replacement claim (C-NAS-AT-OR-OVER), and the package-level comparison conclusion accounting-robust. Boundary earned by concrete counterexample (A4), not by weakening scope.
