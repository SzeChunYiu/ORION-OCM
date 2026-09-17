# SUPPLEMENT 5 — REV-L45-073-PROOF-STRENGTHENING (proof strengthened to full support at stated scope)

Post-freeze supplement #5 to GMI_THEORY_BASELINE_V1 per the
post_freeze_edit_rule (BASELINE_V1.md §5). No bound artifact is edited in
place; this supplement + the new owning-lane package + the corpus-passes
verdict-register append land together with `BASELINE_MANIFEST_V4.json`
(supplement/binding numbering is sequential across lanes; #991 took
SUPPLEMENT_4 + BASELINE_MANIFEST_V3).

## What moved

- Ticket: **REV-L45-073-PROOF-STRENGTHENING** (open -> closed:
  `CLOSED_GREEN__PROOF_STRENGTHENED_TO_FULL_SUPPORT_AT_STATED_SCOPE`).
  Register counts after: 9 total / 6 closed / 3 open (post-#991 the register
read 5 closed / 4 open; this closure moves one more).
- Target: legacy claim object `GMI833_V2_LEGACY_073_MORPHOLOGY_PHASE_RV_THEO`
  — the corpus's single weakest-support adjudication (the L45
  borderline_caveat: Theorem 1 a definitional rearrangement, substantive phase
  content living in an 8x8 sweep witness).

## Diagnosis (confirmed by the revival)

The claim statement — "R/V-parameterized burden, 2-morphology phase condition,
corner regimes, held-out prediction protocol", census THEOREM / ANALYTIC_DEDUCTIVE —
was supported only by: a definitional equivalence (V1 Theorem 1), zero proofs
for V1 Theorem 2 + Corollaries 1-4 (computation standing in for argument), two
assertions false as printed (piecewise-LINEAR boundary with "up to 2
segments"; Corollary 2's R*(V) formula with a sign error and unstated branch
conditions), and a doc-model vs witness-model mismatch (divisor kernel +
unregistered cp·V term vs the boxed hinge kernel).

## Delivered (research/gmi-morphology-phase-rv-proof-v2-v1)

- `MORPHOLOGY_PHASE_RV_BOUNDARY_THEOREM_V2.md`: kernel-general full-rigor
  proofs at the claim's stated scope — Lemma K (kernel regularity), Lemma D
  (difference regularity), Lemma SC (single crossing), P1 (V1 Theorem 1,
  honestly relabelled), **T2** boundary structure (piecewise reciprocal-affine,
  at most 3 segments; V1 shape claim corrected earned-by-proof), **T3**
  R-axis monotonicity + crossing uniqueness + corrected two-branch R*(V),
  **C3** V-axis corrected V*(R), **C1'** corner regimes under explicit
  regularity R+ with explicit R_0, **T4** three-morphology envelope (exact
  region predicates, E3 crossing convexity, sandwich criterion, winner-sequence
  law), **P5** held-out determinism identity (honest: no discriminative power).
  Scope unchanged from the V1 claim — strengthened by proof, not narrowed:
  no counterexample was needed.
- `phase_rv_boundary_route2.py` (route 2: closed forms only, no argmin) +
  `test_phase_rv_proof_v2.py` (19 controls) + `RECEIPT_TWO_ROUTE_V1.json`
  (two hosts, bit-identical): 199,664 winner-agreement cells vs the V1 route-1
  witness, 0 disagreements; exact-fraction control targets all match;
  sandwich proven for ALL R > 0 in both instantiations (exact inf gaps
  11/40, 259/1164); bisection cross-checks at machine precision; 300 exact
  structural draws, 0 violations.
- The V1 8x8 sweep + 23 tests are DEMOTED to a declared control (regression
  pin of the registered parameter point), per the registered lever.
- Zero new arbitrary constants (registered parameters only; ladder/seed from
  the V1 registered sweep and seed 42).

## Register movements (append conventions; frozen files untouched)

- `research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_APPEND_REV_L45_073_V1.json`
  — resolves the L45 borderline_caveat and closes the ticket;
  VERDICT_REGISTER_V1.json / REVIVAL_TICKETS_V1.json stay byte-identical.
- `BASELINE_MANIFEST_V4.json` (this supplement's binding): binds the append
  record, the new package, and this supplement; anchors V1, V2 and V3
  manifests (all byte-identical).
- EV discipline: `evidence_EV` stays EV0 in the frozen THEOREM_SCORES_V2.json;
  the EV lift flagged in the ticket's retest note is AVAILABLE at the next
  maturity-rescore round (that lane owns the axis; no self-promotion here).

## Claim-ceiling note

No baseline assertion is altered by this supplement. The new package holds no
baseline assertion until typed by the frozen mechanical re-run (census
extraction, maturity scoring, claim-discipline registration) per the
arrival_absorption_rule, same as supplement #1's evidence lane.
