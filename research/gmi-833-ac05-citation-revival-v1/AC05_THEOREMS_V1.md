# Named results — `gmi-833-ac05-citation-revival-v1` (issue #833, row AC05)

Claim ceiling: `CITATION_BACKED_DEFINITIONS_IN_PLACE_VERIFIED_V1`. Every
result below is an exact statement about the two committed artifacts
(`GMI_TERMINOLOGY_CROSSWALK_V2.md` at the blob pinned in `MANIFEST_V1.json`
and `CITATION_VERIFICATION_V1.json`) and about lookups performed on
2026-09-19 whose HTTP status is recorded per anchor. Nothing here is a
statement about the literature beyond what the cited passages say.

## AC05-1 — in-place verified anchor on every row (48/48)

- **Scope.** The 48 numbered rows of the crosswalk; the citations cell of
  each.
- **Statement.** For every row `n ∈ {1..48}`: the citations cell contains
  ≥1 resolvable-identifier pattern, ≥1 `VERIFIED-2026-09-19` mark, and the
  register holds exactly one primary anchor for `n` with `verdict =
  VERIFIED`, `resolved = true`, a passage of 1–15 words, a locator, and a
  resolution status in {200, 301, 302, 303} (internal pointers: the named
  commit hash present in the cell). Count: **48/48**, failing set **∅**.
- **Quantifiers.** ∀ rows; ∃ one primary anchor per row.
- **Assumptions.** The register records lookups performed on 2026-09-19;
  the structural check does not re-resolve anything. Passage routes of the
  48 primaries: 28 ABSTRACT, 13 PRIMARY_TEXT, 4 PUBLISHER_DESCRIPTION, 3
  SECONDARY_QUOTATION (rows 6, 23, 35 — the register names the quoting
  source and the primary's HTTP 403).
- **Falsifiers.** Any row whose cell loses its identifier (H1), whose mark
  has no register record (H2), whose record says `resolved: false` (H3),
  whose passage exceeds 15 words (H4), whose primary identifier lives only
  in another file (H5), or whose internal pointer drops its commit (H7) —
  each moves the count 48 → 47 and is detected; 122/122 primary-identifier
  deletions across 200 null draws are caught.
- **Strongest parents.** `gmi-833-ac-lanes-harness-v1` ACL-4 (parent-record
  presence at blob `9f4d25a5`, 15 VERIFIED / 29 CITE-TF / 4 UNMARKED, 8
  supplied off-table); the route-B proxy verdict that named the eight rows.
- **Forbidden extrapolations.** "The definitions are correct"; "the
  parents are earliest"; "the literature is saturated"; "resolution holds
  today" (it is dated).

## AC05-2 — the eight previously unbacked rows are backed in place

- **Scope.** Rows 16, 19, 21, 23, 34, 41, 47, 48.
- **Statement.** Each carries an in-place primary anchor with a supporting
  passage: 16 Hales 2008 p. 1372; 19 Stone 1974 (abstract); 21 Mayr 1942
  p. 120; 23 Hutchinson 1957 p. 416 (via PMC2780934; 1991 reprint DOI
  added); 34 Turing 1936 §1 p. 231; 41 Lampert et al. 2009 (abstract); 47
  Simon 1973 (abstract), Langley et al. 1987 as verified secondary; 48 the
  programme's own template @ `acb38c8b` as primary source, with the
  six-kind partition traced verbatim to issue row AC07 and Wobbrock &
  Kientz 2016 (p. 40) as the nearest external parent for the practice only.
- **Assumptions.** A programme-internal definition cites its primary
  source honestly; that is not a dodge but the rule's §4 clause.
- **Falsifiers.** An external work found to state the six-kind partition
  would demote the internal pointer to secondary (a strengthening, not a
  refutation); a passage shown not to appear at its locator falsifies that
  anchor.
- **Strongest parents.** `AC_CROSSWALK_ADDENDUM_V1.md` Part 2 (the parent
  choices for 7 of the 8 rows; Hempel & Oppenheim retired for row 48).
- **Forbidden extrapolations.** AC02, AC07, AC08, AC09 remain open.

## AC05-3 — Harel venue corrected

- **Statement.** Row 1's "Biting the silver bullet" anchor names *Computer*
  25(1):8–20, 1992, doi:10.1109/2.108047 (Crossref container-title
  "Computer"); *IEEE Software* was wrong. The DOI first tried,
  10.1109/2.108007, resolves 404 and is recorded as such. Harel 1987
  (Statecharts, SCP 8(3):231–274, doi:10.1016/0167-6423(87)90035-9) is
  added as a resolved secondary anchor.
- **Falsifier.** H6 plants *IEEE Software* back; the venue check flips
  1 → 0 and is detected.

## AC05-4 — two routes, hostiles, null

- **Statement.** Route A (`ac05_citation_check_v1.py`) and route B
  (`independent_ac05_oracle_v1.py`, different tokenizer, no import of A)
  agree on 48/48, the empty failing set, the Harel verdict and every row's
  identifier set (0 rows disagree). 7/7 hostiles are applicable and
  detected. Null: 200 single-identifier deletions, 122 hit a primary, all
  122 reduce the count, 0 missed; the true result (48) beats the null.
- **Assumptions.** The null draws with `random.Random(833)` (Mersenne
  Twister, full-width draws), never low bits of a small LCG.

## Not earned here

AC02 (collect parent literature before naming), AC07 (contribution
typing), AC08 (`WHAT_IS_ACTUALLY_NEW.md` surviving all lanes), AC09
(re-run before manuscript freeze). No row of AA, AB or AD.
