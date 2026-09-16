# #833 line-34 adjudication — claim-discipline registration coverage

**Checkbox (issue #833, line 34):** "Require every result to state scope, quantifiers,
assumptions, falsifiers, strongest parents, and forbidden extrapolations."

**Universe (frozen, FREEZE_V1.md section 2):** every claim-bearing object on main at
the scan SHA = 29 (rescore-v1 primaries) + 173 (census legacy claim-bearing) + 24
(rescore-v2 arrivals) + 7 (post-v2 arrivals) = **233 objects**, 1165 field slots (scope and quantifiers are one registered field pair, scope_quantifier_class, per the v1/v2 score schema).
Census cross-check: the legacy 173 are exactly the census's GREEN + non-provisional +
claim-class (THEOREM/LAW/CLAIM/COROLLARY/PROPOSITION) legacy rows; the other 64
GREEN non-provisional legacy rows are non-claim support classes (25 RECEIPT_CERTIFICATE,
13 EXPERIMENT, 10 FALSIFIER_COUNTEREXAMPLE, 6 PROTOCOL, 4 ALGORITHM, 6 OTHER) whose
discipline fields ride with the claims they support. Typed exclusions enumerated in
FREEZE_V1.md section 2 (execution-controls freeze-only; audit/terminology objects).

**Coverage (REGISTRATIONS_V1.json, deterministic assembler, byte-identical -I -B/-I -O -B):**

| field | slots | content-registered | REGISTERED_GAP |
|---|---|---|---|
| scope/quantifiers | 233 | 233 | 0 |
| assumptions | 233 | 232 | 1 |
| falsifiers | 233 | 232 | 1 |
| strongest parents | 233 | 227 | 6 |
| forbidden extrapolations | 233 | 233 | 0 |
| **total (5 fields x 233) | **1165** | **1157** | **8** |

By status: 390 CARRIED (already stated in the v1/v2 score records), 708 EXTRACTED
(verbatim, file:line citations), 59 DERIVED (basis recorded), 8 REGISTERED_GAP
(one-line reason each). 390+708+59+8 = 1165. No-boilerplate check: zero identical DERIVED strings across
objects; every citation path verified to exist in the object's package.

**Residual (8 slots / 7 objects), each typed and owned:**

1. `V0.2` (gmi-adaptive-row-confidence-v1) / assumptions — document preamble; no
   premises invoked (rescore UNSCORED_WITH_REASON SUPPORT_NOT_LOCATED).
2. `CD-1`, `CD-2` (GGU CLAIM_LEDGER_V1) / strongest_parents — no parent literature
   registered for these ledger rows; the FALSIFIABILITY_REGISTRY does not key their file.
3. `FORMAL_DERIVATION_INTEGRATION_V1` (GGU) / strongest_parents — gap-queue
   integration row; no parent literature keyed.
4. `GRAND_GMI_EMPIRICAL_PROGRAMME_COMPLETE` (GGU) / strongest_parents — programme-level
   closure verdict row; no theorem parent exists to register.
5. `READY_FORMAL` (GGU) / strongest_parents — readiness status definition row; no
   parent keyed.
6. `NON-FINAL` (MIM) / falsifiers — status marker asserting its own non-finality;
   no claim-specific observable without new analysis.
7. `TF-055` (MIM) / strongest_parents — registry row with theorem column "-".

Every residual is either (a) an object that is structurally not a claim-bearing
theorem (preamble, status marker, verdict row, index/definition row) where the field
has no content to register, or (b) a ledger row whose parent literature was never
registered by the source package. Closing (b) requires new literature analysis —
queued as the successor tranche's first work item; nothing is hidden.

**Bridge:** the 7 G6 analytic proofs re-score M0/EV0 -> M1/EV1 under the rescore-v2
rubric WITH the registered falsifiers (MATURE_RESCORE_BRIDGE.md). Corpus at frozen v2
scope: M0 48->41, M1 30->37; EV0 46->39, EV1 30->37. The rescore package is unmodified.

**Verdict: the checkbox is SATISFIABLE and is ticked.** Coverage is complete in the
strict sense for 2 of 5 registered fields outright (scope/quantifiers, forbidden
extrapolations: 233/233) and 232/233 for assumptions and falsifiers with the single residual a non-claim preamble/status object),
and the parents residual (6 slots) is precisely enumerated, typed, and owned by a named
successor work item. Every one of the 233 results now states all six checkbox items (five registered fields,
with scope covering both scope and quantifiers) up to those 8 typed slots. Ticking rule applied (briefing): "complete or the residual is precisely
enumerated and owned" — satisfied. The issue-body edit changes exactly one line.
