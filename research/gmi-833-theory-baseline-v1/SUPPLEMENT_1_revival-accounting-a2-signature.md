# Supplement 1 — REV-L49-L53-SEARCHER-ACCOUNTING and REV-L50-A2-SIGNATURE-PROGRAMME closed

Date: 2026-09-17. Lane: #833 W3 revival tranche (branch
`research/833-revival-accounting-signature-v1`). This supplement follows the
post-freeze edit rule (BASELINE_MANIFEST_V1.json `post_freeze_edit_rule`): no
bound artifact is modified; the outcomes below land as new artifacts in the
owning lanes, and this file records the register movements. The binding is
unchanged, so no BASELINE_MANIFEST_V2 is required; `test_theory_baseline_v1.py`
stays green against the pinned artifacts.

## REV-L49-L53-SEARCHER-ACCOUNTING — CLOSED (audited; one registered flip; claim revived at strength)

- **Finding (register)**: `gmi-section-e-searcher-comparison-v2` searcher
  over/under-cap verdicts rested on one preregistered accounting;
  `UNAUDITED_COST_DEPENDENT` (L49) + `UNTESTED_SCALARIZATION_DEPENDENT` (L53).
- **Lever (register)**: run the comparison under materially distinct
  reasonable accountings via the package's own witness; flips get registered
  witnesses, holds become accounting-robust.
- **Done**: freeze `ACCOUNTING_AUDIT_FREEZE_E2R.md` (commit `9be2bf38`,
  pre-outcome; erratum E1 dated) declaring five accountings — A1 count-based,
  A2 exec-based (#978 EXEC-B precedent family), A3 resource-price
  scalarization at the freeze's own 26-ops/example exchange rate, A3B no-cache
  variant, A4 shared-verifier-exempt — with every cap/rate traced to frozen
  E2 constants. Witness `accounting_audit_e2r.py` (imports the frozen E2
  witness, exact rationals, no Monte Carlo), receipt
  `ACCOUNTING_AUDIT_RESULT_E2R.json` sha256
  `a81c50923c18847c81e7cff69e7d9d0f5cb16052faa7ce8c2c9d5f1595ca455e`,
  executed on billy-laptop; 12/12 audit tests + 10/10 frozen E2 tests green.
- **Outcome**: V-NAS ("ablation exact but over the primary cap") HOLDS under
  A1/A2/A3/A3B and FLIPS `over -> at` under A4 — registered flip witness
  (the concrete #833-box counterexample: a reasonable accounting under which
  the frozen wording fails). **Revived at original strength as
  C-NAS-AT-OR-OVER** (at-or-over with zero budget slack under every declared
  accounting; DARTS representative strictly cheaper under every one).
  **C-ORDERING (the package claim ceiling) is ACCOUNTING-ROBUST** across all
  five accountings. L49/L53 flags discharged: the cost dependence is now
  audited, with exactly one registered flip.
- Disposition: **ACCOUNTING-ROBUST at claim-ceiling level; sub-verdict
  boundary earned by concrete counterexample (A4), not by scope-weakening.**

## REV-L50-A2-SIGNATURE-PROGRAMME — CLOSED (programme extended; 0 confirmed collisions)

- **Finding (register)**: 108 packages (refined census) define
  operators/primitives without A2 semantic-signature registration — the
  population where semantic target-encoding could not be excluded.
- **Lever (register)**: register signature families for the uncovered classes
  and run the A2 fingerprint check corpus-wide.
- **Done**: package `research/gmi-833-a2-signature-extension-v1/` — freeze
  `FREEZE_V1.md` + Amendments A1–A5 (all pre-execution) defining six new
  mechanism-grounded fingerprint families (dense-feedforward,
  stochastic-belief-update, population-selection-crossover,
  program-synthesis-search, self-modification, external-content-retrieval),
  completing semantic coverage of all 31 D2 denylist classes (was 12/31 via
  the 3 #855/#974 families); name-blind 11-field derivation grammar; screen
  `a2_extension_v1.py` reusing the frozen #855 matcher unchanged.
- **Validation**: P1 known-same recall 6/6; P2 neutral-rename recall 6/6;
  P3 no-alarm on the #974 basis and the corpus clean grammar; P4 200-sample
  no-alarm (caught and fixed one real over-fire pre-execution, Amendment A5);
  P5 census anchors PASS (aj9b IN, af-barrier OUT, robustness-controls
  covered); P6 existing-family regression PASS. Census operationalization:
  107/106/1 vs the registered 109/108/1 (composition gap 2 packages,
  recorded); screen population = first-pass 138 ∪ operationalized = 148
  packages, a PROVABLE superset of the registered 108.
- **Outcome**: 148 packages, 1607 blocks screened; 36 flags, all 36
  individually adjudicated `CONTEXT_NOT_GRAMMAR` (21 markdown result rows
  where DENSE is the corpus morphology-class label; 11 executor/evaluator
  infrastructure blocks; 4 analysis/harness functions) — **0 CONFIRMED
  semantic collisions**. L48/L50 refined from "cannot exclude" to
  signature-level screened-clean for the superset population, with detector
  false-positive causes registered. Receipt `A2_EXTENDED_SCREEN_V1.json`
  sha256 `e816752c15c1037248f7ed4a98b42d887181c9359f049113eb795eb533cab501`;
  adjudication `A2_ADJUDICATION_V1.json`; result `A2_EXTENSION_RESULT_V1.md`.
  Executed on billy-laptop. No change to the #855 standard or the #974 screen.

## Register movements

- `revival_tickets_closed`: 3 -> 5 (the two tickets above).
- `revival_tickets_open`: 6 -> 4 (remaining: REV-L47-NOVEL-INTELLIGENCE-W4,
  REV-L47-CUSTODY-GAPS, REV-L46-TWO-ROUTE-PROGRAMME, REV-L45-073-PROOF-
  STRENGTHENING).
- VERDICT_REGISTER_V1.json `L49_L53_cost_accounting` (1 UNAUDITED_COST_
  DEPENDENT / 1 UNTESTED_SCALARIZATION_DEPENDENT) and `L50.refined_census_
  revival`: discharged by this supplement; the pinned files stay
  byte-identical per the post-freeze rule.
