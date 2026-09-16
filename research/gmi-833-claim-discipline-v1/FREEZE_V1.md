# GMI #833 claim-discipline registration — freeze v1

**Parent:** #833 Section A row (line 34) "Require every result to state scope, quantifiers, assumptions, falsifiers, strongest parents, and forbidden extrapolations."
**Upstream authorities (read-only, unmodified):** `gmi-833-maturity-rescore-v1` (29 scored 833-family primaries), `gmi-833-maturity-rescore-v2-v1` (197 scored objects: 173 legacy census + 24 post-freeze arrivals; FREEZE_V2.md judgment protocol, typed gaps G1–G7), `gmi-833-corpus-census-v1` (frozen census, locators), `gmi-833-depgraph-adjudication-v1` (PR #949: DEPENDENCY_GRAPH_V2 real edges, duplicate/overstrong adjudication).
**Frozen scan source:** origin/main `f068ea19` at tranche start; re-verified at ship SHA (see §7).
**Status:** pre-registration freeze. Scan rule, universe, and status taxonomy fixed here BEFORE any registration is recorded.

## 1. Scientific question

Can every claim-bearing object in the #833 corpus be given a machine-readable, per-object statement of all six discipline fields — scope/quantifiers, assumptions, falsifiers, strongest parents, forbidden extrapolations — where every registered item is derived from the object's own statement, support, or proof (extraction with citation, or derivation with stated basis), with precisely-enumerated REGISTERED_GAP residuals and no boilerplate?

This is a registration tranche: it does not create evidence, re-prove anything, change any score in the rescore packages, or overturn any freeze. Its only scientific outputs are (a) the gap register (which fields were unstated where), (b) the registrations, (c) the re-score bridge for the seven G6 analytic proofs (in THIS package; the rescore-v2 package is untouched).

## 2. Universe (frozen inclusion rule, mechanical)

Every claim-bearing object on main at the scan SHA, enumerated as the union of:

- **U-V1 (29):** the 29 833-family primaries scored by `gmi-833-maturity-rescore-v1` (THEOREM_SCORES_V1.json).
- **U-LEGACY (173):** the 173 census-GREEN-EXPLICIT claim-bearing legacy objects across 25 non-`gmi-833-*` packages, at their census locators (FREEZE_V2 §11 table; census authority `2fffb144`).
- **U-ARRIVALS (24):** the 24 post-freeze 833-family packages scored by rescore v2 (FREEZE_V2 §3 Gap-2 frozen list).
- **U-NEW (7):** `gmi-833-*` packages that arrived on main after the rescore-v2 freeze SHA `d624c617` and before this tranche's scan SHA, each contributing its primary claim object: `af-barrier-context-v1`, `aj10-prospective-unknown-v1`, `aj11-bounded-completeness-v1`, `aj12-foundation-substrate-relativity-v1`, `aj13-stopping-rule-v1`, `aj9h-k07-k11-blind-recovery-v1`, `capability-ceiling-reaudit-v1`. (Mechanical rule mirroring FREEZE_V2 §3: `git diff --stat d624c617..<scan-sha> -- research/` for new `gmi-833-*` directories; enumerated, never silently dropped.)

Total: **234 objects**. Typed exclusions (listed, never silently dropped): `gmi-833-execution-controls-v1` (freeze-only, NO PRIMARY THEOREM — same typed reason as FREEZE_V2 §3), `gmi-833-claim-discipline-v1` (this tranche's own object), `gmi-833-depgraph-adjudication-v1`, `gmi-833-maturity-rescore-v1/-v2-v1`, `gmi-833-corpus-census-v1`, `gmi-833-tranche-ab-ac-lit` (audit/terminology objects, NO PRIMARY THEOREM — v1/v2 typed exclusions unchanged). The one rescore-v2 UNSCORED_WITH_REASON object (`V0.2`, SUPPORT_NOT_LOCATED) stays in-universe: an object with no located claim still gets its field-status recorded (its statement-derived fields are REGISTERED_GAP with that reason).

## 3. Scan rule (what counts as "stated" — applied uniformly, mechanically)

For each object × field, the field is **STATED** iff at least one of:

- **S1 (score record):** the object's record in THEOREM_SCORES_V1/V2 carries field-specific content (not a placeholder token). Placeholder tokens are exactly: `REGISTERED_IN_PACKAGE_DOCS`, `REGISTERED_IN_PROSE_AT_CITED_PATH`, `UNREGISTERED_IN_LEGACY_SOURCE`, empty.
- **S2 (package registration):** the object's own package docs, at its census/citation locator, carry an explicit registration of that field's content — a falsifier field or explicit falsification condition in the statement/ledger row, a premises/assumptions section the proof invokes, a parent-ledger or registry entry naming the parent, or ceiling/no-promotion language bounding the claim.

Otherwise the field is **UNSTATED** (a gap). The mechanical scan implements S1 over the score records; S2 is implemented per object with verbatim extraction and `file:line` citation (evidence files, §5). Scope/quantifiers are S1-stated for all 197 v2 objects and all 29 v1 objects; U-NEW objects are scanned fresh under S2.

## 4. Registration status taxonomy (output contract)

Every object × field lands in exactly one status:

- `CARRIED_SCORES_V1` / `CARRIED_SCORES_V2` — already S1-stated; carried verbatim with source record id.
- `EXTRACTED` — S2 registration, verbatim content with `file:line` citation.
- `DERIVED` — content derived from the object's own statement/support/proof (basis recorded; e.g. a falsifier as the concrete observable negation of the claim within its declared scope, an assumption as a premise the proof actually invokes).
- `REGISTERED_GAP` — the field cannot be registered without new analysis; one-line reason. A finding, not a failure.

**No-boilerplate contract:** a falsifier must be a genuine observable that would refute that object's claim; an assumption must be one the proof/support actually uses; forbidden extrapolations must name the boundary the proof does not cross. Identical generic text reused across unrelated objects is a defect; the assembler enforces a cross-object duplicate check (exact-duplicate DERIVED strings across different packages are flagged and must be justified or re-derived).

## 5. Method

- Mechanical S1 scan over both score files (script `scan_registers_v1.py`, stdlib, deterministic, counts printed).
- S2 evidence: verbatim per-object extraction at census locators (jsonl ledger rows scripted — all 29 revival-ledger rows verified at their exact census line numbers, zero mismatches; markdown/json/py locators extracted by read-and-cite passes).
- DERIVED registrations authored per object from the claim's own statement/proof (the seven G6 analytic proofs read in full by the tranche author; other derivations basis-noted).
- Assembly + hostile checks in `assemble_v1.py`: coverage assertion (233 objects × 6 fields, none absent), duplicate-boilerplate check, citation-path existence check, counts printed.

## 6. Falsifiers of this tranche

RED if: any of the 233 objects is omitted or silently skipped; any registration's citation does not exist at the scan SHA; any DERIVED falsifier is not an observable of its own claim (boilerplate); any REGISTERED_GAP lacks a one-line reason; the rescore packages are modified (they must remain byte-identical); or the #833 line-34 checkbox is ticked while a non-enumerated residual exists.

## 7. Custody

Scan SHA recorded at ship time in RESULT_V1.json; the tranche re-runs the mechanical universe enumeration at ship SHA and enumerates any post-freeze arrival as the next-arrivals boundary (typed, listed — never chased into scope mid-tranche). No source package is edited; all outputs live in `research/gmi-833-claim-discipline-v1/`.

## 8. Forbidden promotions

`BOILERPLATE_REGISTRATION`, `GAP_HIDDEN_AS_REGISTRATION`, `RESCORE_V2_EDITED_BY_BRIDGE`, `CHECKBOX_TICKED_WITH_UNENUMERATED_RESIDUAL`, `REGISTRATION_PROMOTED_TO_EVIDENCE` (a registered falsifier is not evidence FOR the claim; it is the stated condition under which the claim would be refuted), `COMPLETE_GMI`, `ONTO_COMPLETENESS_IMPLIED_BY_REGISTRATION`.
