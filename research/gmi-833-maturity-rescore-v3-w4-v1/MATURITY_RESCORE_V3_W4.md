# GMI #833 maturity rescore v3-W4 — correction of a headline claim on two closed rows

**Claim ceiling:** `AUDIT_RELABEL_ONLY`. **Closes no #833 row.** This package ships
`CORRECTION_NOTICE_V1.json`, deliberately not an `ISSUE_833_RECONCILIATION_*.json`.

## 1. What was wrong

Two already-closed rows of #833 contradicted each other about the same package.

| | row | closed by | says |
|---|---|---|---|
| A | `Identify assumptions introduced after observing outcomes` | #976 | `gmi-novel-intelligence-w4-v1` is `POST_HOC_SUSPECT (CONFIRMED, double-verified)`: its `RESULT_V1.json` was committed 89 minutes **before** the `FREEZE_V1.md` that claims to predate the search |
| B | `Re-score every major existing GMI result on the maturity ladder` | #938 / #948 | the same package's row `GMI833_V2_LEGACY_074_W4-C` is `M4 / EV3`, support `FROZEN_HELDOUT`, `individually_verified: false` |

`M4` on this ladder means *frozen held-out prediction*, and the only support kind that
licenses it — `FROZEN_HELDOUT` — is defined in the v2 freeze as *"freeze artifact precedes
outcome"*. Row A proves that precondition false for this package's freeze document. The v2
justification cited "Freeze seeded pre-search" — the *mitigating* fact about the seed
literal, which was indeed prospective — as though it discharged the requirement about the
frozen held-out predictions. It does not: the seed was prospective, the freeze DOCUMENT
carrying the family law, the held-out predictions and the non-claims was not.

Two further facts, reproduced here:

- No row anywhere in `THEOREM_SCORES_V2.json` mentions `POST_HOC`. The audit finding never
  reached the scores.
- `gmi-novel-intelligence-w4-prospective-v1`, the revival package that re-earned
  prospectiveness under a genuinely pre-committed freeze, is not scored at all. Substring
  `novel-intelligence-w4` over all 197 full rows returns exactly one hit, the parent's.

So the corpus's headline maturity claim credited an `M4` to a package whose held-out-
prediction freeze the corpus itself had disproved, while the package that legitimately
re-earned it was missing from the ladder.

**The rescore's arithmetic was never in question.** Its 197 rows distribute
`M0 48 / M1 30 / M2 89 / M3 6 / M4 23 / UNKNOWN 1`, summing to 197 and matching the
checklist line exactly; the M/EV cross-tab is diagonal and `M4` and `EV3` are the same 23
rows. This is a propagation failure, not a counting error.

## 2. What is NOT re-litigated

`research/gmi-novel-intelligence-w4-prospective-v1/FREEZE_V2_PROSPECTIVE.md` handles the
science correctly and this tranche agrees with it in full. It re-runs the family-member
search from the *same pre-existing frozen seed* under a new freeze committed before the
replication outcomes, and states plainly that *the commit-order defect is PERMANENT* and
that the *original commit-order gap remains on the parent package's record forever*. That
disposition stands. The job here was to carry it into the maturity ladder, not to reopen it.

## 3. The rule applied — imported, not invented

Everything below comes from `research/gmi-833-maturity-rescore-v2-v1/FREEZE_V2.md` §4,
unchanged. The operative rows:

| observed support | evidence_EV | maturity_M |
|---|---|---|
| `EXACT_FINITE_CERTIFICATE` (exhaustive checker, declared bounded universe) | EV2 | M2 (M3 only if the P3/P4 prior-free condition is itself evidenced) |
| `FROZEN_HELDOUT` (**freeze artifact precedes outcome**) | EV3 | M4 (**never M5**: intra-package != independent replication) |
| `SAMPLED_STATISTICAL` / `EMPIRICAL_UNFROZEN` | UNKNOWN, typed `UNFROZEN_SAMPLED_BELOW_EV3` | M0 |

No level here was hand-picked. Each is the table's output for an observed support kind, and
the executor raises rather than guesses if a support kind falls outside the table.

### The arrivals question, answered as written

The arrival is admitted through v2's own gap-handling convention, not through a new rule.
v2 §3 Gap 2 admits arrivals "per the v1 clause *a v2 refresh re-freezes the source SHA and
re-runs the inclusion rule mechanically*". But that rule filters by the directory-name glob
`gmi-833-*`, and `gmi-novel-intelligence-w4-prospective-v1` is not one — nor is it in the
census-frozen legacy population, which is frozen at `2fffb144`, long before the package
existed. It sits in a typed gap of the frozen inclusion rule, which is precisely why it went
unscored.

v2 met the same situation for its own Gap 1 and recorded the convention: *name the gap, then
apply the closest typed rule* ("The v1 inclusion rule … does not cover legacy objects
(recorded gap G1). Closest typed rule: …"). That convention is what is applied here. The gap
is recorded as **G-NAME**, and the only package admitted under it is the one revival package
named in the freeze. The alternative — applying the glob literally — is recorded in MRW-4
with its own count (`M4 = 22`), and is worse: it leaves the ladder provably incomplete.

## 4. Parent ownership and the residual contribution of this tranche

Assimilation first. Everything of substance here was established by others, and this tranche
absorbs all of it:

- **`research/gmi-833-corpus-passes-v2-v1` (PR #976)** owns the L47 custody screen over 231
  packages, the CONFIRMED `POST_HOC_SUSPECT` verdict, the double verification, and — the
  part that is easy to lose — the *mitigating* seed finding. This tranche re-verified its git
  evidence independently and reproduced the verdict exactly; it claims no novelty in it.
- **`research/gmi-833-maturity-rescore-v1` (PR #938) and `-v2-v1` (PR #948)** own the M/EV
  ladders, the ceiling map, the support-kind table, the down-generation and verification
  protocol, and the closest-typed-rule convention. Every rule applied here is theirs,
  unchanged. Their 197-row census is sound and is carried through by reference.
- **`research/gmi-novel-intelligence-w4-prospective-v1` (PR #988)** owns the revival: the
  prospective re-establishment from the inherited seed, the extended held-out predictions,
  the independent route, the multi-host determinism receipt, the custody tags, and the
  correct disposition that the parent's defect is permanent.
- **`research/gmi-novel-intelligence-w4-v1`** owns the W4-C theorem and its exact finite
  certificate, neither of which this tranche disputes.
- **`research/gmi-833-capability-interaction-partition-v1`** owns the correction-notice
  convention (schema `GMI_CORRECTION_NOTICE_V1`) this package follows rather than reinvents.

Parent literature behind the ladders themselves — preregistration and held-out evaluation as
evidence grades — is the standard methodological corpus; nothing here is claimed novel about
it, and no DOI is asserted that the corpus does not already carry in
`research/gmi-833-maturity-rescore-v2-v1`.

**Residual contribution, and it is small on purpose:** carrying an already-CONFIRMED verdict
across a package boundary into a scoring artifact that depended on it; scoring an arrival the
frozen inclusion rule structurally could not reach; and a validated propagation checker that
makes the class detectable in future, together with the naming of the structural cause
(G-NAME) and of the squash-merge artifact behind the L47 `SINGLE_COMMIT_FREEZE_RESULT` and
`CUSTODY_NON_DEMONSTRABLE` classes.

## 5. Results

**W4R-1.** `GMI833_V2_LEGACY_074_W4-C` moves `M4/EV3` → **`M2/EV2`**, support
`FROZEN_HELDOUT` → `EXACT_FINITE_CERTIFICATE`, `delta_kind DOWN_GENERATING`,
`individually_verified` false → **true**. Reasons and refusals: MRW-1, MRW-2.

**W4R-2.** `gmi-novel-intelligence-w4-prospective-v1` is scored for the first time:
**`M4/EV3`**, support `FROZEN_HELDOUT`. Its custody was verified here, not taken on trust,
and the verification produced a real caveat that must be stated out loud: **on main's own
history the package arrives in a single squash commit, so the method #976 used cannot
demonstrate freeze-before-outcome for it.** The order is demonstrable on the PR-#988 branch,
which is anchored on origin by pushed tags, and the bridge to main is byte-identical freeze
blobs. Custody HOLDS. `M5` is refused despite the two-host bit-identical receipt: MRW-3.

**W4R-3.** Corrected distribution and exact delta:

| | M0 | M1 | M2 | M3 | M4 | UNKNOWN | total |
|---|---|---|---|---|---|---|---|
| published | 48 | 30 | 89 | 6 | 23 | 1 | 197 |
| corrected | 48 | 30 | **90** | 6 | 23 | 1 | **198** |
| delta | 0 | 0 | **+1** | 0 | **0** | 0 | **+1** |

Evidence side: `EV0 46 / EV1 30 / EV2 95 → 96 / EV3 23 / UNKNOWN 3`, total 198.

**The M4 total does not change. Its membership does.** `gmi-novel-intelligence-w4-v1`
leaves M4; `gmi-novel-intelligence-w4-prospective-v1` enters it. A headline that stays at 23
while becoming true is the good outcome, and it is reported as a swap, not as "no change":
the published 23 counted a package whose frozen held-out prediction had been disproved and
omitted the one that had re-earned it.

**W4R-4.** 30 adverse verdict entries checked across all five registers in
`research/gmi-833-corpus-passes-v2-v1`:

| outcome | n |
|---|---|
| `UNREFLECTED` | **3** (2 distinct packages) |
| `OUT_OF_SCORED_POPULATION` | 18 |
| `REFLECTED_OR_IMMATERIAL_TO_SCORE` | 8 |
| `NOT_ADVERSE` (register self-types it a screen false positive) | 1 |

The 3 `UNREFLECTED` are `gmi-novel-intelligence-w4-v1` (counted by two registers — the L47
confirmed entry and the REV-L47-W4 prior-verdict entry) and `gmi-833-g0-grammar-growth-v1`.
After the v3 delta, the W4 flags extinguish; the checker then flags zero for that package.

The `OUT_OF_SCORED_POPULATION` count is the number that would have been reported as defects
by a careless checker. #976 screened 231 packages; the scores cover 173 census objects plus
24 `gmi-833-*` arrivals, only 49 distinct packages in all. A package with an adverse verdict
and no score row is not a scoring defect, and the three outcomes are kept typed apart.

**The second flag was adjudicated, not just reported.** `gmi-833-g0-grammar-growth-v1` is
named in L47's `overclaiming_freeze_texts` (a class the register itself types "gap states,
not defects") and is scored `M4/EV3/FROZEN_HELDOUT`. Verified mechanically: on the origin
branch `research/833-g0-grammar-expansion-v1`, its freeze commit `10f0ef37` contains only
`FREEZE_V1.md` and `FROZEN_FIXTURES_V1.json` and strictly precedes the implementation commit
`65073060`; the only post-merge change to the freeze on main is the #947 terminology
migration, 2 lines added and 2 removed, two heading renames. **Its M4 score is sustained and
this tranche alters nothing about it.** The flag is a squash-merge artifact — which is the
generalisable finding: L47's `SINGLE_COMMIT_FREEZE_RESULT` (45) and
`CUSTODY_NON_DEMONSTRABLE` (18) classes are substantially artifacts of squash merging, and
the repair is the one the prospective package already used: push custody tags for the freeze
and results commits. Those 45 packages are UNCHECKED here, which is not the same as
checked-and-fine.

## 6. Validation of the checker, before any finding was reported

| control | requirement | result |
|---|---|---|
| H1 synthetic plant | an `M4`/`FROZEN_HELDOUT` row planted for a package with a CONFIRMED adverse verdict must be flagged | detected |
| H2 **real** plant | the checker must flag the W4 row in `THEOREM_SCORES_V2.json` *as published*, and flag zero after the v3 delta | detected; extinguished |
| H3 no-alarm, real | `gmi-capability-interactions-unified-v1` carries the L58 OVERSTRONG defect but is scored `M2` → must be `IMMATERIAL` | not flagged |
| H3b no-alarm, real | `machine-intelligence-morphogenesis-v1` is self-typed a screen false positive and holds 12 `M4`/`FROZEN_HELDOUT` rows; treating it as adverse would produce 12 false positives at once | classified `NOT_ADVERSE` |
| H4 arithmetic tamper | a distribution not summing to the row count must be flagged | detected |
| H5 custody hostile, real | the custody predicate must be able to return FALSE — proved on the parent package | returns `OUTCOME_PRECEDES_FREEZE` |
| name-resolution NULL | 200 seeded draws of a real package name plus a suffix no package carries | 0 flags — **but a miss is guaranteed by construction; this is not evidence of selectivity** |
| permutation NULL | 200 seeded draws re-pointing all 29 adverse entries at random *real* scored packages | true 3; permuted 0–9; **129 of 200 draws flag at least as many** |

**The permutation null is an honest negative and is reported as one.** The true flag count
does not beat it: about a fifth of the 49 scored packages hold an `M4`/`FROZEN_HELDOUT` row
mentioning no finding, so a random re-pointing hits one about as often as the real register
does. The flag *count* therefore carries no evidence on its own and is not offered as such.
What carries the evidence is *which* packages are flagged — H2 on real data, the two real
no-alarm cases, and the downstream adjudication of every flag against the artifact.

## 6b. What was actually read, and what was not

Read in full: the parent's `FREEZE_V1.md` (its L3 is verbatim *"Frozen **before**
family-member search on this branch."*, and it carries the family law, the held-out `k=5`
predictions and the explicit non-claims), `FORMALIZATION_V1.md` (theorems W4-A/B/C and the
eight-box ledger), `MANIFEST.json` and `CORE.md`; the arrival's `FREEZE_V2_PROSPECTIVE.md`
and `.json`, `independent_route_v1.py` (fiber refinement, first-occurrence canonical
labeling, pigeonhole bound, budgeted brute-force witness — it imports neither the V6 witness
nor the parent executor) and its test file; `FREEZE_V2.md` §§1–5; and all five verdict
registers.

Read structurally rather than line by line: `novel_intelligence_w4_v1.py` — its header was
read, and the exactness claim rests on a **mechanical** source scan for float
literals/casts, `random`, `numpy` and sampling, re-run by the executor and asserted by a
test. The two `RESULT_V1.json` files — every top-level key inspected, the large per-`k`
arrays not read element by element.

Not read, and therefore UNCHECKED rather than checked-and-fine: the other 45
`SINGLE_COMMIT_FREEZE_RESULT` packages of the L47 screen.

**MRW-1's falsifier (iv) is closed by enumeration, not spot check.** All 7 files of the
parent package on `source_main` were checked for first-add order: `CORE.md`,
`RESULT_V1.json`, the executor and its test at `08c4d206`; `FREEZE_V1.md`,
`FORMALIZATION_V1.md` and `MANIFEST.json` all at the later `7ce73e5d`. `CORE.md` carries no
held-out prediction — it lists artifacts and the claim ceiling, and it already cites
`FREEZE_V1.md` as "frozen before search" at a commit where that file does not yet exist.

## 6c. Self-disclosed refinements of the freeze

Neither widens any claim; both are strictly more conservative than the frozen text.

- **Outcome typing.** Freeze P6 names three outcomes; five are delivered.
  `REFLECTED_OR_IMMATERIAL_TO_SCORE` is defined in freeze §4 but not listed in P6;
  `NOT_ADVERSE__SELF_TYPED_SCREEN_FALSE_POSITIVE` is not named in the freeze at all.
  Both are strictly narrower than `REFLECTED`, which is itself empty (count 0). Without
  `NOT_ADVERSE`, `machine-intelligence-morphogenesis-v1` — which the register itself types a
  screen false positive — would be treated as adverse and all 12 of its `M4`/`FROZEN_HELDOUT`
  rows would flag. That is hostile H3b, the largest false-positive risk in this check.
- **Downstream adjudication.** A per-flag verification step was added (`W4R4_adjudication`).
  It does not alter the sweep's typing; it records whether a flag survives verification
  against the artifact. One of two flags did not survive, and the corresponding score was
  left untouched.

## 6d. Known fragility, disclosed

The g0 adjudication depends on the origin branch `research/833-g0-grammar-expansion-v1`,
which is **not** tag-anchored. If that branch is deleted the adjudication degrades to
`NOT_ADJUDICABLE__BRANCH_OBJECTS_UNAVAILABLE` and says so loudly; it deliberately does not
gate this package's exit code, because it changes no score. The corpus-level fix is the
repair this package recommends to others: push a custody tag anchoring `65073060`.

Git history queries run against `HEAD` rather than the `source_main` literal so the checks
also run on a PR head. That is sound exactly when `source_main` is an ancestor of `HEAD` —
asserted by the executor and by a test — and every pinned blob still matches, since the
first-add commits being read are historical and cannot move under a descendant ref.

## 7. Two materially independent routes

- **Route A** `rescore_v3_w4.py` — table-driven classifier; census by dict accumulation;
  delta by in-place row rewrite; blob ids reconstructed in pure Python
  (`sha1("blob <len>\0" + bytes)`); custody by `merge-base --is-ancestor`; adverse
  population by explicit enumeration of the registers' named sections.
- **Route B** `oracle_v3_w4.py` — imports nothing from route A; census by single-pass
  accumulation into a pre-declared fixed key list that raises on any unexpected value;
  delta by set algebra over `result_id`; blob ids by `git hash-object` plumbing; custody by
  `git rev-list --ancestry-path` in both directions; adverse population by a
  **schema-agnostic recursive walk** of every register file, finding package names and
  adverse tokens wherever they live.

Route B discovers 53 adverse package mentions to route A's 30 entries and finds the **same**
`UNREFLECTED` set. That is what justifies the claim that no register section was skipped:
route B never consults route A's section list. The routes agree exactly on both
distributions, both totals, the M4 membership swap, and all three custody states.

All arithmetic is integer. No float appears in any claim; the test suite scans the emitted
receipt recursively to prove it.

## 8. What this tranche did NOT do

- It closed no #833 row and edited no issue body.
- It modified no frozen artifact. `THEOREM_SCORES_V2.json` and every #938 / #948 / #976 file
  are untouched; `SCORES_V3_DELTA.json` supersedes by reference and by delta only, and a
  test asserts the branch touches nothing outside this package and its workflow.
- It did not re-open, soften or re-litigate the CONFIRMED L47 verdict.
- It did not check the other 45 `SINGLE_COMMIT_FREEZE_RESULT` packages, and says so.
