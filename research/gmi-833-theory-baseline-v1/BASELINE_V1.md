# GMI_THEORY_BASELINE_V1 — frozen audited theory baseline

Parent: SzeChunYiu/ORION-OCM#833 (Section B, line 59 — "Freeze an audited
`GMI_THEORY_BASELINE_V1` before further upgrades").
Pinned HEAD: `c4def870df287a476672e47219134832a0c2f380`
("research(#833): corpus identification passes v2 … L58 revival to universal CI-U (#976)").
Machine binding: `BASELINE_MANIFEST_V1.json` (this directory) — 132 artifacts across
11 component packages, each sha256-pinned (plus a self-binding of the freeze
package's own files); tamper-evident via this package's
`test_theory_baseline_v1.py`, which re-derives every hash from the live tree
and fails on drift.

**Claim ceiling:** `GMI_THEORY_BASELINE_V1_AT_PINNED_FROZEN_CORPUS_SCOPE`.
The baseline binds what the corpus *is* and what each audit *found* at the pinned
scope. It is an audited snapshot, not a truth proclamation.

## 1. What the baseline asserts (and where each assertion rests)

| # | Assertion (at pinned scope) | Rests on (bound artifacts) |
|---|---|---|
| A1 | The GMI corpus is enumerated: 22,553 scientific objects over 5,351 files, dispositions GREEN 237 / AMBER 18,396 / RED 3,920, census frozen at source `2fffb144` | corpus-census `CORPUS_INDEX_V1.json`, `AUDIT_V1.json` |
| A2 | A master RAG table covers the entire frozen corpus: 39 non-empty strata summing to 22,553; census dispositions never overwritten | depgraph `MASTER_RAG_TABLE_V1.json` |
| A3 | The dependency graph (v2, real cited edges: 357 = 140 file-local + 28 pointer-rollup + 60 parent-family-anchor + 73 external-literature + 56 corpus-package) is acyclic at stated-relation scope: 0 cycles, 0 self-loops (Tarjan, 239 union nodes) | depgraph `DEPENDENCY_GRAPH_V2.json`, `CYCLE_REPORT_V1.json` |
| A4 | Duplicates are adjudicated: 1,652 candidate groups → 1,586 DUPLICATE / 66 DISTINCT / 0 UNCERTAIN; content collapse 22,553 → 17,258 nodes | depgraph `DUPLICATE_ADJUDICATION_V1.json` |
| A5 | No unsupported overclaim remains: the FIN2UNIV population (283 flags) adjudicated 283 PROPER; the one confirmed OVERSTRONG (capability-interactions universal phrasing, #939) was revived, not narrowed (see §3) | depgraph `OVERSTRONG_ADJUDICATION_V1.json`, audit-close `FREEZE_V1.md`, passes-v2 `VERDICT_REGISTER_V1.json`, `PASS_L58_V1.md` |
| A6 | Maturity is scored corpus-wide under frozen rubrics: 197 rows (M0 48 / M1 30 / M2 89 / M3 6 / M4 23 / UNKNOWN 1); corpus fact: no M5/M6 — no EV4/EV5 evidence exists anywhere; the 7 G6 analytic proofs bridge M0/EV0 → M1/EV1 with registered falsifiers | rescore-v1 `FREEZE_V1.md`, rescore-v2 `FREEZE_V2.md` + `THEOREM_SCORES_V2.json`, claim-discipline `MATURE_RESCORE_BRIDGE.md` |
| A7 | Claim discipline is complete: all six fields (scope/quantifiers, assumptions, falsifiers, strongest parents, forbidden extrapolations) registered for all 235 claim-bearing objects — 1,175 slots, 0 REGISTERED_GAP at v2 | claim-discipline `REGISTRATIONS_V2.json`, `RESULT_V2.json`, `SUCCESSOR_TRANCHE_V2.md` |
| A8 | Corpus identification passes L42, L44–L56, L58 ran over frozen populations with per-verdict evidence; every CONFIRMED finding carries a revival ticket; SCREENED-NOT-ADJUDICATED remains an explicit gap state, never silence | passes-v2 `VERDICT_REGISTER_V1.json`, `FROZEN_PASSES_V1.md`, `PASS_L*.md` |
| A9 | The revival queue is live: 9 tickets, 3 DONE_IN_SWEEP, 6 open (§4) — obligations, not acceptable terminals | passes-v2 `REVIVAL_TICKETS_V1.json` |
| A10 | Terminology is migrated at paper-facing scope: 255 + 217 rule-attributed edits (tranches 1–2); non-aj obligation cleared; residual 69 hits = 35 aj-lane (their lane) + 34 acknowledged definitional-quote/citation sites | terminology `MIGRATION_LOG_V1/V2.md`, `ACKNOWLEDGED_FINDINGS_V1.json` |
| A11 | Blind-recovery protocol v2 closed every input channel (task, basis, fingerprint clauses, cost, thresholds, screen) pre-search, over coverage-complete batteries, with the A2 semantic screen; recovery boundary measured (XOR recovered, XNOR honestly fails); 6 open gaps registered | blind-recovery-v2 battery/basis/screen/posthoc/OPEN_GAPS artifacts |
| A12 | Grammar growth is green at registered scope: GRW-1, INV-1, REC-1, HLD-1, THR-1, NULL-1; held-out burden 50,052 → 1,307 (net −48,739, H− control regression preserved); 0/200 nulls; independent-oracle agreement | grammar-growth `MANIFEST_V1.json`, `RESULT_V1.json`, fixtures, oracle |
| A13 | The progress ledger's checkbox evidence map and remaining-work queue are current at its pin | ledger `CHECKBOX_EVIDENCE_V1.md`, `REMAINING_WORK_V1.md` |
| A14 | The CI-U universal theorem stands at re-earned full strength (§3) | passes-v2 `PASS_L58_V1.md`, `VERDICT_REGISTER_V1.json` |

## 2. Claim ceiling — what this baseline does NOT assert

- It does **not** assert any corpus theorem is *true*. Maturity scoring, adjudication
  verdicts, and RAG dispositions describe evidence states, not truth values.
  CONFIRMED ≠ true; M4 ≠ validated.
- It does **not** assert corpus completeness: 22,116 un-sampled AMBER+RED objects
  carry adjudication only at the #939 bounded-tranche scope; absence of a dependency
  edge is not independence; 86 name-only parent mentions are unresolved by design.
- It does **not** assert all gaps are closed: 6 revival tickets are open, aj-lane
  residuals and the L48 screen refinement belong to their lane, blind-recovery v2
  carries 6 registered gaps (2 critical), and SCREENED-NOT-ADJUDICATED populations
  are recorded gap states (L49/L53 37 packages; L54/L55 5+5; L52 census-side 1,336
  UNIVERSAL statement-side).
- It does **not** assert real-scale validation, parent exhaustion, or known-family
  derivation completeness.
- Forbidden promotions (binding, union of component lists):
  `ALL_GMI_THEOREMS_TRUE`, `ONTOLOGICAL_COMPLETENESS`, `ALL_PARENTS_EXHAUSTED`,
  `ALL_OVERCLAIMS_REPAIRED`, `KNOWN_FAMILY_DERIVATION_COMPLETE`,
  `REAL_SCALE_VALIDATION_COMPLETE`, `COMPLETE_GMI`,
  `BASELINE_IMPLIES_THEOREM_TRUTH`, `REVIVAL_OBLIGATION_CLOSED_BY_BASELINE`,
  `SILENT_EDIT_OF_BOUND_ARTIFACT`.

## 3. CI-U — the universal theorem at re-earned full strength

The corpus's one confirmed OVERSTRONG finding (#939: "for any two capabilities"
rested on unproven joint=sum / joint=max equalities) was **not closed by narrowing**.
Per the operator revival doctrine (2026-09-16: aim for the best claim, never
downgrade/narrow to close; work every open negative to green), the intermediate
27×27 downgrade (commit `b2b5a9d9`) was superseded by diagnosis and re-proof:

- **Theorem CI-U (universal, proven)** — capability-interaction accounting over
  channel-wise claim-set structure.
  - Lemma A: disjoint channels ⇒ joint = sum — *unconditional*.
  - Lemma B: shared channel ⇒ max ≤ joint ≤ sum with exact equality
    characterization (nested ⇔ max; disjoint ⇔ sum; partial overlap ⇔ strictly
    between) — *unconditional* (inclusion-exclusion).
  - Lemma C: no interference under the free-option premise — feasible-set inclusion.
  - Boundaries CE-1 (within-channel claim shareability) and CE-2 (free-option
    accounting) are labelled EARNED-BY-COUNTEREXAMPLE inside the theorem.
  - Corollary CI-A4: the original 27×27 classification is the registered
    fully-shareable *instance* — an instance, not the claim.
- Controls: witness GREEN; 9/9 new tests + 27/27 original tests. The universal
  claim is restored and *earned* — stronger than both the original overclaim
  (equalities now proven, premises named) and the intermediate narrowing.

## 4. OPEN-OBLIGATIONS register (the live queue, not acceptable terminals)

Every entry below is work the baseline documents as owed. None is closed by this
freeze; each closes only by its lane's revival chain landing as a supplement (§5).

**Revival tickets (6 open; full attribution/lever/owner in the manifest register):**

| Ticket | Failure attribution | Lever | Owner lane |
|---|---|---|---|
| REV-L47-NOVEL-INTELLIGENCE-W4 | custody stage: freeze doc lagged the outcome | prospective replication from the same frozen seed under a new pre-outcome freeze | #592/#796 lineage lane |
| REV-L47-CUSTODY-GAPS | custody stage: 18 non-demonstrable packages + 5 tight gaps | per-package prospective replication from frozen seeds, or freeze-text amendment to claimed custody | per-package lanes + RAG instance append |
| REV-L46-TWO-ROUTE-PROGRAMME | evidence stage: 75 SINGLE_ROUTE computational claims | per-package independent oracle (two-route pattern), highest-claim first | per-package lanes + L34 retrofit |
| REV-L45-073-PROOF-STRENGTHENING | proof stage: Theorem 1 definitional | prove Theorem 2 boundary-curve properties analytically; demote sweep to control | morphology-phase-rv lane |
| REV-L50-A2-SIGNATURE-PROGRAMME | registration stage: 108 packages lack A2 signatures | register 11-field Sigma signatures + A2 fingerprint check per package | L50/L34 lanes |
| REV-L49-L53-SEARCHER-ACCOUNTING | evidence stage: single preregistered accounting | re-run searcher comparison under ≥2 materially distinct accountings | section-E lane (#715) |

Closed in-sweep (3): REV-L58-CI-UNIVERSAL, REV-L42-CONTENT-NORM-DETECTOR,
REV-L56-COGNITIVE-RESIDUAL — each with executed chain, not paperwork.

**Lane-owned residuals:** aj-lane terminology residual — 35 hits across 12
`gmi-833-aj*` packages (owner: aj lanes; per-package table in MIGRATION_LOG_V2.md);
L48 screen refinement — AJ9 no-smuggling contract response, owner aj lane
(L48 unticked by the v2 sweep by design).

**Blind-recovery v2 gaps (6):** V2-DAG-COST (critical), V2-K05-K11 (critical),
V2-BASIS-NEUTRALITY-BOUND (high), V2-LEARNING (high), V2-PREDICTED-SELECTED
(medium), V2-REAL-SCALE (medium).

**Post-pin arrivals:** any claim-bearing arrival after the pinned SHA is **U-NEW**
until typed by the frozen mechanical re-run — enumerate via
`git diff --stat <pin>..<head> -- research/` restricted to new `gmi-833-*`
directories; census extraction → maturity scoring → discipline registration →
RAG strata → identification screens; listed, never silently dropped; absorbed by
a numbered supplement. Precedent: blind-recovery-v2 entered as the 235th
claim-discipline object under this rule (PR #974). At freeze time: **0 arrivals
since pin** (re-checked at ship; see manifest `arrivals_since_pin`).

## 5. Freeze governance

- **No silent edits post-freeze.** No bound artifact may be modified in place.
  Every change — a ticket closing, an arrival typed, a count moving — lands as a
  supplement: `SUPPLEMENT_<n>_<slug>.md` in this directory (plus the owning lane's
  new artifacts) and, when the binding itself changes, `BASELINE_MANIFEST_V2.json`.
  The pinned manifest and its 132 bound files stay byte-identical forever.
- **Tamper evidence.** `test_theory_baseline_v1.py` (package-local, stdlib-only,
  runs under `python -I -B` / `python -I -O -B`) re-derives every bound
  sha256 from the live tree, re-derives the headline counts from the bound JSONs,
  and cross-checks the manifest's revival-ticket register against the pinned
  `REVIVAL_TICKETS_V1.json`. Any drift fails the package tests.
- **Determinism.** `build_manifest_v1.py` is stdlib-only and byte-identical under
  `python -I -B` / `-I -O -B`; the manifest records the pin method (working-tree
  file verified byte-identical to the pinned git blob before sha256 binding).

## 6. Component inventory (all PRs merged on main at pin)

| Component | Package | PR |
|---|---|---|
| Corpus census (child #842) | research/gmi-833-corpus-census-v1 | #845 |
| Corpus audit close | research/gmi-833-corpus-audit-close-v1 | #939 |
| Dependency graph v2 adjudication | research/gmi-833-depgraph-adjudication-v1 | #949 |
| Maturity rescore v1 (rubric) | research/gmi-833-maturity-rescore-v1 | #938 |
| Maturity rescore v2 (197 rows) | research/gmi-833-maturity-rescore-v2-v1 | #948 |
| Claim discipline v1+v2 | research/gmi-833-claim-discipline-v1 | #972 / #975 |
| Corpus identification passes v2 | research/gmi-833-corpus-passes-v2-v1 | #976 |
| Terminology migration v1+v2 | research/gmi-833-terminology-migration-v1 | #940 / #947 |
| Blind-recovery protocol v2 (#833/#434) | research/gmi-833-blind-recovery-v2-v1 | #974 |
| G0 grammar growth (child #897) | research/gmi-833-g0-grammar-growth-v1 | #945 |
| Progress ledger | research/gmi-833-progress-ledger-v1 | #970 |
