# REV-L46-TWO-ROUTE-PROGRAMME — Tranche 1 (frozen)

**Status: FROZEN (programme) — conversions execute only after this freeze.**
Ticket: `REV-L46-TWO-ROUTE-PROGRAMME`
(`research/gmi-833-corpus-passes-v2-v1/REVIVAL_TICKETS_V1.json`, frozen file —
current state moves in the baseline supplement manifest per house convention).
Population: the **75 SINGLE_ROUTE** packages of PASS-L46
(`research/gmi-833-corpus-passes-v2-v1/P3_SCREENS_V1.json`, `.L46.status ==
"SINGLE_ROUTE"`); 16 TWO_ROUTE / 75 SINGLE_ROUTE / 140 NO_COMPUTATION over 231.

**Doctrine:** conversions STRENGTHEN claims — two-route exact agreement upgrades
a claim's evidential standing (a second materially independent route is the M5
"independent replication" rung of the frozen maturity ladder). No narrowing of
any claim closes a gap; the gap closes only by conversion.

## 1. Prioritization (mechanical, reproducible)

Ranking key over the 75 packages, computed by `rank_population_v1.py` from
frozen artifacts only (`P3_SCREENS_V1.json`, `CORPUS_INDEX_V1.json`,
`THEOREM_SCORES_V2.json`; no judgment inputs):

1. **GREEN-mainline object count** desc — blast radius if the single route is
   wrong (`audit_disposition == "GREEN"` AND `id_kind == "EXPLICIT"` in the
   census; the 237-object mainline per `gmi-833-corpus-audit-close-v1`
   FREEZE_V1.md). A package with ≥1 mainline object outranks every package
   with none.
2. **comp_claims** desc (`P3_SCREENS_V1.json` L46 population count) — exposure.
3. **highest maturity_M then evidence_EV** of the package's census objects
   (`THEOREM_SCORES_V2.json`) — a stronger published claim resting on one
   implementation is more critical.
4. Alphabetical (stable total order).

Output: `RANKING_V1.json` (75 rows, tiered). Tranche-1 selection rule (mechanical
follow-through of the key): **the 8 highest-ranked packages that are neither
collision-excluded nor executor-less, plus the highest-exposure green=0
package (the ticket-named first, comp=20)**. Selection (8 packages):

| rank | package | comp | GREEN-mainline | effort |
|---|---------|------|----------------|--------|
| 1 | gmi-formal-proof-audit-v1 | 1 | **4** (T602-21/26/32/37, 2 COMPUTER_ASSISTED_EXHAUSTIVE) | S |
| 2 | gmi-developmental-uncertainty-transport-v1 | 5 | **3 CONFIRMED (DT-2A, DT-2B, DT-3B)** | S |
| 3 | gmi-analog-semantics-closure-v1 | 1 | 2 (ANALOG_SEMANTICS_THEOREM_V1, AS-1) | S/M |
| 5 | gmi-uncertainty-composition-v1 | 9 | 1 (REAL_WORLD_COVERAGE_PROVED) | S/M |
| 6 | gmi-dependency-aware-uncertainty-composition-v1 | 7 | 1 (DA-C4 exhaustive certificate) | S/M |
| 7 | gmi-capability-ceilings-v1 | 6 | 1 (F2-U) | S |
| 8 | gmi-structural-threshold-repair-v1 | 5 | 1 (N_SUM_THRESHOLD3_V3) | M |
| — | gmi-learning-law-selection-v1 | 20 | 0 | M |

Deferments to tranche 2, with reasons (mechanical, recorded):
- `gmi-novel-intelligence-w4-v1` (rank 4, green=1 M4/EV3): w4 family-cluster
  lane active; W4-C already has the prospective two-route replication package
  `gmi-novel-intelligence-w4-prospective-v1`.
- `gmi-morphology-phase-rv-v1`: w1 lane (open PR #993) adjacent.
- `gmi-main566567-audit-v1` (rank 9, green=1): no in-package route-1 executor
  (source-bound review package; conversion requires source-binding
  archaeology) — first tranche-2 item.
- `gmi-current-program-assay-v1` (ticket-named), `gmi-developmental-predictions-v1`,
  `gmi-theory-foundations-v1`, `gmi-capability-predictor-v1`: green=0; head of
  tranche 2 after the remaining green=1 packages (`gmi-threshold-task-frontier-v1`,
  `gmi-useful-descendant-evolvability-v1`, `gmi-capability-contract-v1`).

## 2. Two-route conversion template (independence stated mechanically)

Per converted package, ADD (never edit bound artifacts; route-1 executors and
committed receipts stay byte-identical):

- `independent_oracle_v1.py` — **route 2**. Written from the CLAIM
  SPECIFICATION (the package's FORMALIZATION/CORE/theorem markdown and the
  committed receipt's value structure as the only interface). Imports NO
  module of the package or any `research/` package — stdlib only (asserted by
  AST audit). Exact integer/`Fraction` arithmetic; no floats; no network.
- `l46_crosscheck_v1.py` — the agreement artifact: runs route 2, loads
  route 1's **committed** receipt JSON (not route-1 code), compares per
  claimed quantity, writes `ORACLE_RESULT_L46_V1.json`.
- `ORACLE_RESULT_L46_V1.json` — the two-route receipt (schema below).
- `test_independent_oracle_v1.py` — self-contained assertions incl. the
  agreement gate, run by CI.

**Materially independent — mechanical criteria (the #932 anti-pattern is the
rejection rule; `gmi-833-execution-controls-v1` FREEZE_V1.md D-X3):**

1. **Shared-code audit (AST):** route 2's import graph contains zero nodes
   from the route-1 package or any `research/` tree package; stdlib +
   nothing else. Recorded in the receipt as the audited module list.
2. **Algorithm-class difference table:** route 1 vs route 2 differ on **at
   least two declared axes** from the registered set — *representation /
   exploration order / pruning / acceptance-termination / completeness
   argument / search cost profile*. One algorithm in two encodings
   (identical canonical traces up to a bijection) is rejected as
   `SEARCHERS_NOT_MATERIALLY_DISTINCT`; the receipt records the table.
3. **Author lineage:** route 2 is derived from the claim spec, not from
   route-1 source; route-1 source is read only to (a) classify its algorithm
   class for the difference table and (b) name its committed receipt as the
   cross-check target. Stated in the receipt.

**Agreement rule:** every claimed quantity gets one row — `claim_id`,
route-1 committed value, route-2 value, `agree` (exact `==` on int/Fraction/
bool/string; a tolerance is allowed only where the route-1 receipt itself
declares one). Fail-closed: any mismatch flips the terminal boolean to false
and is a FINDING, never adjudicated away — a disagreement may be an
original-implementation defect (attribute → verify → fix-or-file as a revival
chain; fixes to route-1 files are forbidden in this tranche — file instead).

## 3. Acceptance gate (what closes a package's gap)

A package's SINGLE_ROUTE gap closes at tranche scope iff ALL hold:

- G1 route 2 exists in-package, passes the shared-code AST audit (criterion 1);
- G2 the difference table shows ≥2 differing axes with a one-line mechanism
  justification each (criterion 2), pre-registered in `FREEZE_L46_TWO_ROUTE_V1.md`
  BEFORE any route-2 execution;
- G3 every computational claim in the package's committed receipt has an
  agreement row; terminal boolean `exact_agreement_everywhere` (or
  `agreement_within_declared_tolerances` where frozen) is true;
- G4 negative control: at least one check where route 2 must NOT agree with a
  perturbed/counterfactual value (proves the comparison is not vacuous);
- G5 receipt records `source_sha256` over BOTH route files + crosscheck +
  the claim-spec doc, and the run environment (host, python, `-I -B`).

Verdict vocabulary: `TWO_ROUTE_CONVERTED` (G1–G5, all agree) /
`TWO_ROUTE_WITH_FINDINGS` (G1–G5, ≥1 disagreement registered as findings) /
`CONVERSION_BLOCKED` (a G-gate cannot be met at current scope — must say why
and route a finding). All three count as *disposed*; only the first two close
the gap.

## 4. Effort model (expected, per package)

- **S** (finite exact math, ≤6 receipt claims, stdlib recomputation): 1
  route-2 module + crosscheck + test; ~2–3 h. Tranche-1: formal-proof-audit,
  developmental-uncertainty-transport, capability-ceilings-v1.
- **M** (multi-claim receipts, staged or multi-file route 1): route-2
  re-derives all staged quantities; ~4–6 h. Tranche-1: analog-semantics,
  uncertainty-composition, dependency-aware-composition,
  structural-threshold-repair (7 route-1 modules), learning-law-selection.
- **L** (ecology/population campaigns, ≥9 claims or cross-package binds):
  tranche 2; may need LUNARC.

Tranche 2 (remaining 67 after tranche-1's 8): `gmi-main566567-audit-v1` first
(no in-package executor — needs source-binding archaeology), then the
green=1 remainder (threshold-task-frontier, useful-descendant-evolvability,
capability-contract), then current-program-assay (ticket-named, M systems),
developmental-predictions, theory-foundations, capability-predictor, then
descending `RANKING_V1.json`; `gmi-novel-intelligence-w4-v1` and
`gmi-morphology-phase-rv-v1` re-enter once their lanes close.

## 5. Execution discipline

- Freeze order: this programme → per-package route-2 declarations
  (`FREEZE_L46_TWO_ROUTE_V1.md`) → remote execution → receipts → registers.
- NOTHING executes on the authoring Mac: implementations and receipts run on
  `billy-laptop` (Linux, CPython 3.8 — route-2 code is 3.8-safe stdlib-only),
  transferred with rsync/scp + sha256 verification both sides.
- Register updates are append-only NEW files in
  `research/gmi-833-corpus-passes-v2-v1/` (bound registers stay
  byte-identical); current-state ticket movement is carried by the baseline
  supplement manifest (next version after any in-flight one).
