# GMI #833 maturity rescore — freeze v3-W4 (correction delta, no row earned)

**Package:** `gmi-833-maturity-rescore-v3-w4-v1`
**Status:** pre-implementation freeze. This file is committed to this branch BEFORE any
executor, oracle, test, score record, receipt, or correction notice of this package exists
in git. The package CI re-checks that add-order mechanically and fails otherwise.

**Frozen source authority (`source_main`):** `5126041da7ce608f69157f281ca492ac9618c8e4`
(verified `origin/main` tip at freeze time; the local `main` ref in this clone points at
the older ancestor `6590cd998cdc7d60333d3c4ec446ae7757788a4b` and is NOT used anywhere —
every path citation in this package resolves against `5126041d` only).

**Claim ceiling:** `AUDIT_RELABEL_ONLY`. This tranche re-labels already-registered evidence
under an already-frozen rule. It creates no evidence, re-proves nothing, and overturns no
registered freeze.

## 0. No row is earned here

This is a CORRECTION of two rows of issue #833 that are **already closed**:

- Row A (closed by PR #976): `Identify assumptions introduced after observing outcomes`
- Row B (closed by PRs #938 / #948): `Re-score every major existing GMI result on the maturity ladder`

**No neighboring row is earned here. No row of issue #833 is claimed, closed, re-opened, or
edited by this tranche.** Accordingly this package deliberately ships
`CORRECTION_NOTICE_V1.json` (schema `GMI_CORRECTION_NOTICE_V1`, the convention established by
`research/gmi-833-capability-interaction-partition-v1/CORRECTION_NOTICE_V1.json`) **in place of**
item 9 of the #833 closure standard. The absence of an
`ISSUE_833_RECONCILIATION_*.json` in this package is intentional, not an omission.

## 1. The inconsistency being corrected

Two closed rows contradict each other about the same package, `gmi-novel-intelligence-w4-v1`.

**Row A's artifact.** `research/gmi-833-corpus-passes-v2-v1/VERDICT_REGISTER_V1.json`
(blob `a996877453bfdd8fd89b4254e3dc765d23403bae` at `source_main`), section `L47_post_hoc.confirmed[0]`:

> verdict `POST_HOC_SUSPECT (CONFIRMED, double-verified: reader + pass owner independent git verification)`;
> evidence: `RESULT_V1.json` (`"all_w4_boxes_green"`) added `08c4d206` 2026-09-15T16:54:44+02:00;
> `FREEZE_V1.md` added `7ce73e5d` 2026-09-15T18:23:27+02:00 (89 min later); `git merge-base --is-ancestor`
> confirms the result commit is a true ancestor of the freeze commit; `FREEZE_V1.md` L3 claims
> "Frozen **before** family-member search on this branch." — contradicted by custody.
> Mitigating: the freeze SEED literal + sha256 pre-existed inside the WIP executor
> (`novel_intelligence_w4_v1.py:29`), so the SEED was prospective; **the freeze DOCUMENT
> (family law, held-out predictions, non-claims) was not.**

**Row B's artifact.** `research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json`
(blob `0cfca31894960e24c1c12bb7bf05f9e13e63f4aa` at `source_main`), row
`result_id = GMI833_V2_LEGACY_074_W4-C`, `package = gmi-novel-intelligence-w4-v1`:
`maturity_M = M4`, `evidence_EV = EV3`, `support_kind = FROZEN_HELDOUT`,
`individually_verified = false`,
`justification = "FROZEN_PRE_OUTCOME: support=FROZEN_HELDOUT; census=THEOREM/ANALYTIC_DEDUCTIVE; Freeze seeded pre-search; RESULT_V1.json all boxes green incl held-out k=5"`.

`M4` on this programme's ladder is **"frozen held-out prediction"**, licensed only by the
support kind `FROZEN_HELDOUT`, whose defining parenthetical in the v2 judgment protocol is
**"(freeze artifact precedes outcome)"**. Row A proves that precondition false for this
package's freeze DOCUMENT. The v2 justification cites "Freeze seeded pre-search" — the
*mitigating* seed fact — as if it discharged the requirement about the frozen held-out
predictions, which it does not, and the row was never individually read.

**Root cause (recorded here before any judgment).** Two causes, one temporal and one structural:

1. *Temporal.* The rescore (#948) merged to main at commit `f4020d06`, 2026-09-16T14:58:50+02:00.
   The audit (#976) merged at `c4def870`, 2026-09-16T19:04:05+02:00 — about four hours later.
   The rescore literally could not have seen the verdict, and was never refreshed afterwards.
2. *Structural, and the reason this class recurs.* The v2 arrivals inclusion rule is typed by
   directory NAME (`gmi-833-*`). A revival package that re-earns a property for a non-`gmi-833-*`
   parent can never enter the scored population through that glob, no matter how long one waits.
   `gmi-novel-intelligence-w4-prospective-v1` is exactly such a package.

## 2. Ladders and rule — imported UNCHANGED, not re-derived

The rubric is taken verbatim from `research/gmi-833-maturity-rescore-v2-v1/FREEZE_V2.md`
(blob `7e3a055d00361ba6204e38db8a6be5c24d1a580a` at `source_main`), which itself imports v1
unchanged. Reproduced here for audit; **altered definitions are forbidden**:

- EV0 definition/protocol/registration · EV1 deductive theorem with explicit premises and
  falsifiers · EV2 exact/computer-assisted certificate at a bounded declared universe ·
  EV3 prospectively frozen held-out experiment · EV4 disjoint/independent implementation
  replication · EV5 real-scale prospective validation with calibrated uncertainty.
- M0 concept → M1 theorem (EV1+) → M2 exact witness (EV2+) → M3 architecture-prior-free
  relative recovery (P3/P4 prior-free condition) → M4 frozen held-out prediction (EV3) →
  M5 independent replication (EV4) → M6 real-scale prospective validation (EV5).
- Ceiling map: `EV0→≤M1, EV1→≤M2, EV2→≤M3, EV3→≤M4, EV4→≤M5, EV5→M6-possible`.
- Support-kind table (v2 §4), the operative rows for this tranche:

  | observed support | evidence_EV | maturity_M |
  |---|---|---|
  | `EXACT_FINITE_CERTIFICATE` (exhaustive/executable checker, declared bounded universe) | EV2 | M2; M3 only if the P3/P4 prior-free condition is itself evidenced |
  | `FROZEN_HELDOUT` (**freeze artifact precedes outcome**) | EV3 | M4 (**never M5**: intra-package ≠ independent replication, v1 rule 2) |
  | `SAMPLED_STATISTICAL` / `EMPIRICAL_UNFROZEN` | rubric gap G2 → `evidence_EV="UNKNOWN"`, typed `UNFROZEN_SAMPLED_BELOW_EV3` | M0 |

- Union rule: an object with multiple support kinds takes the union EV and the M grounded by
  the strongest *grounding* kind; maturity never exceeds the ceiling map.
- v1 rules 4–5 apply verbatim: never inflate, never guess; `maturity_M` may sit below
  `evidence_EV`; only an upward mismatch is a defect. Insufficient evidence →
  unscored-with-reason, never a guess.

**Arrivals rule, applied as written including its own gap clause.** v2 §3 Gap 2 admits arrivals
"per the v1 clause *a v2 refresh re-freezes the source SHA and re-runs the inclusion rule
mechanically*", and v2 §3 Gap 1 establishes this programme's own convention for a population
the typed rule does not reach: *name the gap, then apply the CLOSEST TYPED RULE* ("The v1
inclusion rule … is typed for 833-family packages and **does not cover legacy objects**
(recorded gap G1). Closest typed rule: …"). This freeze applies exactly that convention and
nothing else. The closest typed rule for a post-`source_main`-authority, result-bearing
package that carries the registered revival of an already-scored object is the Gap 2 arrivals
rule with the `gmi-833-*` name filter replaced by its evident intent — *result-bearing packages
of the 833 programme added to main after the frozen authority SHA* — since a revival ticket
registered in an 833 package (`REV-L47-NOVEL-INTELLIGENCE-W4`) is 833-programme work whatever
its directory is named. **This is recorded as gap G-NAME and is a finding of this tranche, not
a licence to widen scope**: the ONLY package admitted under it is the one revival package
named in §3.

## 3. Scope — frozen, exhaustive, and deliberately tiny

Exactly two score records may be produced by this tranche:

1. **RE-SCORE (correction).** `result_id = GMI833_V2_LEGACY_074_W4-C`,
   package `gmi-novel-intelligence-w4-v1`, theorem `W4-C` — the existing v2 row, re-scored with
   Row A's CONFIRMED verdict as an input.
2. **NEW SCORE (arrival admitted under the closest typed rule, gap G-NAME).**
   package `gmi-novel-intelligence-w4-prospective-v1`, one primary object.

Typed exclusions, listed and never silently dropped: every other row of
`THEOREM_SCORES_V2.json` is carried through **unchanged and by reference**; this tranche
supersedes v2 by delta only. No v2 artifact and no #938/#948 or #976 file is edited in place —
they are frozen, and this package writes only inside its own directory (plus its own CI file).

## 4. Registered predictions (falsifiable, written before the executor exists)

Each is a decision flag the executor must confirm mechanically and independently of this prose.

- **P1 — the parent's `FROZEN_HELDOUT` precondition is FALSE.** On `source_main`,
  `research/gmi-novel-intelligence-w4-v1/RESULT_V1.json` is first added at `08c4d206` and
  `FREEZE_V1.md` at `7ce73e5d`; `merge-base --is-ancestor result freeze` succeeds and the
  reverse fails. Therefore `FROZEN_HELDOUT` is not an available support kind for `W4-C`.
- **P2 — the surviving support kind for `W4-C` is `EXACT_FINITE_CERTIFICATE`, landing M2/EV2.**
  The W4 executor establishes every box, the held-out k=5 box included, by exact integer
  computation over a declared bounded universe (F(k), k∈{2,3,4}; fresh k=5; fixed budget B=3),
  with no floating-point and no sampling anywhere in the file. The G2 row
  (`SAMPLED_STATISTICAL`/`EMPIRICAL_UNFROZEN` → UNKNOWN/M0, applied by v2 to
  `G15_STEP_TWO_REACHED`) therefore does NOT apply: that row targets support which is *only*
  unfrozen and sampled, whereas the exactness of this package's certificate was never in
  question and is not what Row A falsified. M3 is REFUSED: the P3/P4 prior-free condition is
  not evidenced for this package (v2 expected that carve-out only for the `aj9*` family, and
  the W4 family F(k) is registered by the package itself, i.e. the search saw the target family).
- **P3 — the arrival's custody HOLDS, and holds only off-main.** On `main`'s own history the
  whole package arrives in one squash commit `103e4274`, so the main-only add-order method used
  by Row A's screen cannot demonstrate freeze-before-outcome for it. On the PR-#988 branch,
  `FREEZE_V2_PROSPECTIVE.{md,json}` are added at `56195abe` — a commit whose tree contains those
  two files and NOTHING else in the package directory — and `56195abe` is a strict ancestor of
  the executor commit `c1056b31` and of the results commit `81d1b9c3`, with the reverse false in
  both directions. The bridge that licenses reading the branch evidence onto `source_main` is
  blob identity: the freeze blobs are `ec68c133d35608b8632250944230ac5f930a481f` (`.md`) and
  `ae20c46f8895efea46da016697d1b0590647c702` (`.json`) at BOTH `56195abe` and `source_main`.
  **If any of these checks fails, P3 is falsified and this tranche must report the arrival's
  custody as NOT demonstrable — loudly — instead of scoring it M4.**
- **P4 — the arrival lands M4/EV3, never M5.** `RECEIPT_MULTIHOST_V1.json` shows two hosts and
  two Python versions producing a bit-identical result, which superficially resembles EV4. The
  frozen table forbids it in the same cell: *"never M5: intra-package ≠ independent replication"*.
  Same package, same authors, same code — M4/EV3.
- **P5 — corrected headline distribution.** `M0 48 / M1 30 / M2 90 / M3 6 / M4 23 / UNKNOWN 1`,
  total 198; EV `EV0 46 / EV1 30 / EV2 96 / EV3 23 / UNKNOWN 3`, total 198. Delta vs the
  published `48/30/89/6/23/1` (total 197): `M2 +1`, `total +1`, **`M4` unchanged at 23 with its
  membership swapped** — `gmi-novel-intelligence-w4-v1`/`W4-C` leaves M4,
  `gmi-novel-intelligence-w4-prospective-v1` enters it. This is the good outcome and must be
  reported as a swap, never as "no change".
- **P6 — propagation sweep.** Every adverse verdict in the `gmi-833-corpus-passes-v2-v1`
  registers is cross-checked against `THEOREM_SCORES_V2.json` and resolved into exactly one of
  three typed outcomes: `REFLECTED`, `UNREFLECTED` (the defect class), or
  `OUT_OF_SCORED_POPULATION` (the package has no row at all because it is outside the scored
  population — #976 screened 231 packages while the scores cover 173 census objects + 24
  `gmi-833-*` arrivals). Conflating the third with the second is the principal cry-wolf risk
  and is forbidden. **A count of zero `UNREFLECTED` is a valid and reportable result**, but only
  if the checker's recall is demonstrated first (§6).

**Operative definition of "reflected", frozen here.** An adverse verdict against package `p` is
`UNREFLECTED` iff `THEOREM_SCORES_V2.json` contains at least one row with `package == p` whose
`maturity_M` is `M4` or above, or whose `support_kind` is `FROZEN_HELDOUT`, AND no row for `p`
mentions the finding anywhere in `justification`, `verification_note`, `claim_evidence_gap` or
`forbidden_extrapolations`. If `p` has rows but none at M4+/`FROZEN_HELDOUT`, the verdict is
`REFLECTED_OR_IMMATERIAL_TO_SCORE` with that typed reason. If `p` has no rows at all, it is
`OUT_OF_SCORED_POPULATION`.

## 5. Two materially independent routes (required for every census)

- **Route A** — `rescore_v3_w4.py`: applies the frozen support-kind table as a data-driven
  decision procedure, recomputes the full 197-row distribution from
  `THEOREM_SCORES_V2.json`, applies the two delta records, and emits the corrected counts.
- **Route B** — `oracle_v3_w4.py`: an independently written oracle that **must not import
  route A**. It recomputes every census from the raw JSON by a different construction
  (single-pass accumulation into fixed-key integer counters plus set-algebra over row ids,
  rather than route A's table-driven classifier), and applies the delta as a set difference on
  `result_id` rather than as an in-place rewrite. Exact integer agreement is required.
- Arithmetic is exact: integers only. No floats appear in any claim of this package.

## 6. Hostiles that MUST be detected, and the null

The propagation checker is validated on REAL data before any of its findings are reported:

- **H1 (planted positive, synthetic).** Inject a score row at `M4`/`FROZEN_HELDOUT` for a
  package carrying a CONFIRMED adverse custody verdict. MUST be flagged `UNREFLECTED`.
- **H2 (planted positive, REAL).** Run the checker against `THEOREM_SCORES_V2.json`
  **as published**. It MUST flag the `W4-C` row. Run it against the v3-corrected scores;
  it MUST then flag zero. A real positive that the correction extinguishes is stronger
  evidence of recall than any synthetic plant.
- **H3 (no-alarm case).** A package with an adverse verdict whose rows all sit at M2 or below
  MUST NOT be flagged, and MUST carry the typed reason `REFLECTED_OR_IMMATERIAL_TO_SCORE`.
- **H4 (arithmetic tamper).** A distribution whose class counts do not sum to the row count
  MUST be flagged. A corrected total that does not equal 197 + (new rows) MUST be flagged.
- **H5 (custody hostile).** A freeze commit whose tree already contains the executor or the
  result MUST fail the custody check — i.e. the check must be capable of returning FALSE.
  Applied to the parent package `gmi-novel-intelligence-w4-v1`, the custody check MUST return
  FALSE; that is the real-data recall proof for P1/P3's machinery.
- **NULL.** Randomised pairings of register package names against score package names
  (seeded, exact, ≥200 draws) must produce a flag count the true result beats — expected 0
  flags under the null, since a random package name matches no adverse verdict.

## 7. Falsifiers of THIS tranche

1. This freeze is not a strict git ancestor of every other file in this package (CI-enforced).
2. Route A and route B disagree on any integer.
3. The corrected class counts do not sum to the corrected row count.
4. Any v2, #938/#948, or #976 artifact is modified by this branch.
5. Any float appears in any claim.
6. The propagation checker fails H1, H2, H3, H4 or H5, or the null yields a nonzero flag count.
7. Any score level here is chosen by hand rather than produced by the frozen table from an
   observed support kind.
8. This package claims, closes, re-opens, or edits any #833 issue row.
9. An absence claim is made from a single check, or from absent printed output.

## 8. Forbidden promotions

- Do NOT promote `gmi-novel-intelligence-w4-v1` back to M4 on the strength of the prospective
  child. The parent's commit-order defect is PERMANENT and stays on the parent's record forever
  (the child's own freeze says so, and this tranche agrees).
- Do NOT promote the arrival to M5/EV4 on the strength of the multi-host receipt.
- Do NOT re-open, re-litigate, or soften Row A's CONFIRMED verdict; it is an INPUT here.
- Do NOT edit `THEOREM_SCORES_V2.json` or any other frozen artifact in place.
- Do NOT widen the arrivals admission of §2 beyond the single package named in §3.
- Do NOT claim any #833 issue row from this tranche, and do NOT raise the claim ceiling above
  `AUDIT_RELABEL_ONLY`.
