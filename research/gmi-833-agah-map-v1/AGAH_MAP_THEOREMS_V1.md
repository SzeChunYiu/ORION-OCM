# AG/AH map — named results

Scope: the 75 open rows of issue #833 comments `5693520829` (sections AG, AG0–AG13) and
`5693590252` (sections AH, AH0–AH10), pinned byte-exact in `AGAH_ROWS_V1.json` at `source_main`
`91c6d287`, and the merged `main` corpus at that commit.

---

## RA-1 — parent-citation admissibility

**Statement.** Of the 55 rows closed in this tranche, **40** are closed by citing merged parents.
All 40 citations are admissible under a checker that verifies, per citation:

1. the cited package exists and its `RESULT_V1.json` git blob sha equals the pinned value —
   **0 pin failures**, 0 package failures;
2. every cited receipt field path resolves and its canonical JSON rendering equals the pinned
   value byte-exactly — **185 fields verified across 20 distinct parent packages**, 0 field
   failures, 0 value failures;
3. the row's `row_meaning_token` — what closing the row as a clean positive would assert — is not
   in the cited parent's forbidden set (the union of `forbidden_promotions`, `forbidden_promotion`,
   `forbidden_terminal`, `forbidden_terminals`, `forbidden_implications`,
   `forbidden_extrapolations`) — **0 forbidden conflicts**;
4. the parent's `status`/`verdict` is `GREEN` — 0 status failures;

and per replacement: `old` and `anchor` byte-exact against the pinned rows (0 failures), `new`
containing `old` verbatim (0 failures), each row appearing exactly once (0 duplicates), and the
bucket in the closed vocabulary (0 failures). Thirteen violation counters, all zero.

**What RA-1 does NOT claim.** RA-1 proves only that a citation is not a misreport of its parent. It
does not prove the cited row's scientific content, which remains owned by the cited parent.
`PARENT_CITATION_PROVES_ROW_CONTENT` is a registered forbidden promotion.

**Why criterion 3 exists.** A duplicate result under different terminology is a defect class this
corpus audits. The live case: AG3's row *"Require flagship 'fundamental primitive' claims to survive
replacement of the chosen generating presentation by an equivalent one"* would, closed as a clean
positive citing AJ5, assert `COMPILER_MAKES_SEARCH_BIAS_INVARIANT` — which AJ5 lists as forbidden.
The auditor refuses that citation (hostile `HA4`), and the row is instead closed
`EARNED_BY_COUNTEREXAMPLE` naming the four quantities AJ5 records as not invariant without the
resource map.

**Quantifiers.** For all 40 citations and all 185 pinned fields.

**Assumptions.** Receipts are the authority for their own numbers. Field presence plus value
equality plus blob pinning is the verification; parent mathematics is not re-derived.

**Falsifiers.** Any non-zero counter; a disagreement between the two routes.

**Hostiles (11, each with a moved counter).** corrupted pin; field absent from receipt; tampered
value; **row meaning is a forbidden promotion of the cited parent**; nonexistent package; duplicate
row; one-character row-text drift (isolated: caught by the row-text gate without tripping the
`new`-line gate); anchor drift; `new` line dropping the row; bucket outside the vocabulary; parent
receipt not `GREEN`.

**Null.** 200 randomized misdirections — a real replacement re-pointed at a different real parent
package with its field paths and pinned values kept — yield **0/200** admissible.

**Two routes.** Route A walks dot paths and reads a fixed forbidden-key list. Route B flattens each
receipt exhaustively into a `{dot-path -> canonical-json}` map and does plain lookup, and harvests
the forbidden set by collecting every string under any key whose name begins with `forbidden`.
Route B imports nothing from route A. All shared quantities agree.

---

## RA-2 — bucket classification of all 75 rows

**Statement.** All 75 rows are classified into the closed vocabulary
`{HARNESS, EXACT-FORMAL, DISCIPLINE-CONTRACT, NEW-SCIENCE, EXTERNAL-GATE}` with a stated reason and
an owner or a named next tranche. Distribution: `EXACT-FORMAL 32`, `DISCIPLINE-CONTRACT 16`,
`HARNESS 15`, `NEW-SCIENCE 11`, `EXTERNAL-GATE 1`. Disposition: `40` closed by verified parent
reconciliation, `15` closed by the two new packages in this tranche, `20` left open with a reason.

**`DISCIPLINE-CONTRACT` is a subtype of `EXACT-FORMAL`,** not a prose escape hatch: a prohibition
row closes only when the prohibition is a registered field in a merged receipt **and** some
configuration actually trips it. Two rows are held open for exactly this reason — `AG6`'s
`UNIVERSAL_COMPUTATION_ONLY` terminal, which appears only as a gap-kill condition in
`research/machine-intelligence-morphogenesis-v1/GAP_REGISTER_V3.json` and is not awardable by any
checker, and `AH4`'s "do not define intelligence by level membership", which is vacuous until the
levels exist.

**Assumptions.** Classification is a working plan, not a theorem;
`BUCKET_CLASSIFICATION_IS_A_THEOREM` is forbidden.

**Falsifiers.** A row unclassified; a bucket outside the vocabulary; a row appearing twice or not
at all.
