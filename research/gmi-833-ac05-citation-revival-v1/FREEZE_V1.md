# FREEZE — `gmi-833-ac05-citation-revival-v1` (issue #833, section AC, row AC05)

Status: **PRE-IMPLEMENTATION FREEZE**. Committed before any edit to the
crosswalk, the addendum, the harness receipt, or any executor, test, receipt,
verification register or workflow of this package exists.
`git log --reverse -- research/gmi-833-ac05-citation-revival-v1/` must show
this file, alone, first; and the commit carrying this file must precede the
first commit that changes any file listed in section 6.

## 1. Source pin

- `source_main` = `b5193f32db01944774e9527b06e63dec2fac887d`
- issue comment under reconciliation: `5684607872`, anchor
  `### AC. Literature saturation / terminology authority`
- live comment bytes at freeze: 39218 (fetched 2026-09-19, read-only)
- frozen parents (blob sha at this pin):
  - `research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md` = `9f4d25a5f59cdf83f86bc484cda7efb46a8bc054` (the primary artifact; 48 rows)
  - `research/gmi-833-ac-lanes-harness-v1/AC_CROSSWALK_ADDENDUM_V1.md` = `46ebc61153184bb9077f69c18a56d785925781f7` (supplies parents for 8 rows; self-disclaims AC05)
  - `research/gmi-833-ac-lanes-harness-v1/RESULT_V1.json` = `7ef1fd587a60080192c044163bd0b034e161eb68` (records the parent's 15 VERIFIED / 29 CITE-TF / 4 UNMARKED split at blob `9f4d25a5`)
  - `research/gmi-833-tranche-ab-ac-lit/WHAT_IS_ACTUALLY_NEW_TEMPLATE_V1.md` = `e4f1116182d16e6e74f971510b0ef883aaf16d15` (the six contribution kinds; first stated at commit `acb38c8b95bbc6657ee3782f9d53162d5d8c8bc3`)
- prior proxy verdict being revived: route-B fresh-session proxy on AC05,
  `NOT_SATISFIED` — rows 16, 19, 21, 23, 34, 41, 47, 48 carry no externally
  checkable citation in place; addendum rescues 7 of 8 but is unmerged and
  self-disclaims AC05; row 48's rescue (Hempel & Oppenheim 1948; Popper 1959)
  does not support its definition; row 1's Harel venue is wrong.

## 2. Claim ceiling

`CITATION_BACKED_DEFINITIONS_IN_PLACE_VERIFIED_V1`

Every one of the 48 crosswalk definition rows carries, **in the crosswalk
table itself**, at least one citation that (a) resolves and (b) was checked
against the cited text on the recorded date. Nothing here claims that any
citation is the earliest parent, that the literature is saturated, or that
any definition is correct beyond what the cited passage states.

## 3. The eight rows this tranche revives

Rows 16 (theorem typing), 19 (predict), 21 (machine species), 23 (niche),
34 (carrier), 41 (unseen form), 47 (discover), 48 (derive-claim typing) of
`GMI_TERMINOLOGY_CROSSWALK_V2.md`. Plus the row-1 venue defect (Harel 1992,
"Biting the silver bullet", is *Computer* 25(1), not *IEEE Software*).

## 4. Verification rule for a citation (declared before any lookup is recorded)

A citation cell VERIFIES a row iff ALL of:

1. **Resolvable identifier.** It carries a DOI, or — where no DOI exists — a
   stable identifier (ISBN, arXiv id, standards number, or a persistent URL
   of the publisher/repository). Resolution is checked by an HTTP request to
   `https://doi.org/<DOI>` (or the URL) and the status code and date are
   recorded in `CITATION_VERIFICATION_V1.json`. `302`/`303` from doi.org,
   or `200` from a URL, count as resolved; `404`/`000` do not.
2. **Bibliographic match.** For DOIs, Crossref metadata (title, container,
   volume, pages, year) must agree with the cell text; a venue or year that
   Crossref contradicts is a defect and the cell must be corrected.
3. **Supporting passage.** The cited source must state the definition the
   row's definition cell gives (or the canonical term's meaning the row
   adopts). The passage is recorded as a quotation of **at most 15 words**
   with a locator (page, section, or "abstract"/"title"). A citation whose
   text does not state the definition — however real the work — does NOT
   verify the row (this is what retires Hempel & Oppenheim for row 48).
4. **In place.** The identifier and status live in the row's own citations
   cell. A citation that lives only in another file verifies nothing.

**Programme-internal definitions.** Where a row's definition is the
programme's own coinage with no external parent that states it, the honest
in-place citation is to the primary source: the cell must say
"programme-internal definition; no external parent states it; first stated
in `<package>/<file>` @ `<commit>`", may name the nearest external parent
for the *practice* only, and must NOT dress the coinage in an external
citation that does not state it. Such a row is VERIFIED under this rule only
if the named commit/blob is reachable on `main` and the passage rule (3)
is applied to the named internal file.

Status marks written into the table: `VERIFIED-2026-09-19` (all four
clauses met on that date) — nothing else counts as verified. `CITE-TF`
marks may remain only on *secondary* anchors within a cell that already
carries a verified primary; a row whose every anchor is `CITE-TF` fails.

## 5. What will be measured (declared before the numbers are read)

- Structural check (stdlib, no network, CI-safe): for each of the 48 rows,
  the citations cell contains ≥1 resolvable identifier pattern
  (`doi:`/`10.<digits>/`, `arXiv:`, `ISBN`, `https://`), ≥1
  `VERIFIED-2026-09-19` mark, and a matching record in
  `CITATION_VERIFICATION_V1.json` whose `verdict` is `VERIFIED` and whose
  `resolved` is `true`. Reported as `n/48`; the row closes only at 48/48.
- Two routes: the structural checker and an independently written oracle
  that re-parses the table with a different tokenizer and re-derives the
  `n/48` count and the per-row identifier set; they must agree.
- Hostiles (each must be DETECTED): (H1) a row whose identifier is deleted;
  (H2) a row marked `VERIFIED-2026-09-19` with no register record; (H3) a
  register record with `resolved: false`; (H4) a register record whose
  passage exceeds 15 words; (H5) a citation that lives only in the addendum
  file (not in place); (H6) a wrong-venue cell (Harel/*IEEE Software*)
  against the frozen Crossref container. A hostile that cannot move the count
  fails the run (`applicable` flag).
- Null: 200 random deletions of one identifier each from a copy of the table
  must each reduce the count below 48 (0/200 pass).

## 6. Files this tranche may change outside its own directory

- `research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md` —
  citations cells only (rows 1, 16, 19, 21, 23, 34, 41, 47, 48 and any other
  row needing an identifier to satisfy rule 4.1); no term, match, definition
  or migration cell changes; row count stays 48; header note updated to
  record the verification date and rule.
- `research/gmi-833-ac-lanes-harness-v1/`: a numbered amendment
  `AMENDMENT_01_ADDENDUM_MERGED_V1.md` recording that Part 2 of the addendum
  is merged into the parent table and its AC05 disclaimer is retired for the
  merged rows; `RESULT_V1.json` regenerated by that package's own
  `check_receipt_v1.py --write` because it measures the live parent (its
  workflow runs on this path). The addendum file itself and that package's
  FREEZE are not edited.
- `.github/workflows/gmi-833-ac05-citation-revival-v1.yml` (new).

## 7. Rows this tranche may reconcile

Verbatim from comment 5684607872 under the anchor above:

    - [ ] Maintain citation-backed definitions rather than model-generated definitions.

**No neighboring row is earned here.** Explicitly NOT earned: AC02
("For every core GMI construct, collect canonical and modern parent
literature before naming it"), AC07, AC08, AC09, and no row of AA, AB or AD.
The row closes only if the fresh proxy returns `SATISFIED` and the
structural check is 48/48; otherwise the reconciliation records the residual
objections as the row's next targets and the row stays `- [ ]`.

## 8. Forbidden promotions

`LITERATURE_SATURATED`, `PARENT_IS_EARLIEST`, `ALL_PARENTS_EXHAUSTED`,
`DEFINITIONS_CORRECT`, `AC02_CLOSED`, `AC07_CLOSED`, `AC08_CLOSED`,
`AC09_CLOSED`, `WHAT_IS_ACTUALLY_NEW_COMPLETE`, `ROW_CLOSED_BY_NARROWING`,
`SECONDARY_QUOTATION_IS_PRIMARY_CHECK` (a passage verified only through a
secondary source is recorded as such and never as a primary check).

## 9. Compute and custody

Citation/derivation task: no compute; stdlib scripts only; network used only
for resolution/metadata lookups recorded by date and status. No worktree is
added; git runs from the worktree root with `/usr/bin/git`.
