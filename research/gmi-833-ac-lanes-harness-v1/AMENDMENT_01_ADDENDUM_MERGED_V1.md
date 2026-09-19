# AMENDMENT 01 — addendum merged into the parent table; harness re-pinned to its frozen blob

Date: 2026-09-19. Authored by `research/gmi-833-ac05-citation-revival-v1`
(freeze `FREEZE_V1.md` §6 of that package). This file amends; it edits neither
`FREEZE_V1.md` nor `AC_CROSSWALK_ADDENDUM_V1.md` of this package.

## 1. What changed in the parent

`research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md` moved
from blob `9f4d25a5f59cdf83f86bc484cda7efb46a8bc054` (the blob this package
froze) to a revised citations column in which every one of the 48 rows carries
an in-place anchor marked `VERIFIED-2026-09-19` under the four-clause rule in
`gmi-833-ac05-citation-revival-v1/FREEZE_V1.md` §4. The eight rows this
package's `AC_CROSSWALK_ADDENDUM_V1.md` Part 2 supplied parents for (16, 19,
21, 23, 34, 41, 47, 48) now carry those parents — or an honest replacement —
in the parent table itself:

| row | addendum parent | merged into the parent table as |
|---|---|---|
| 16 | Hales 2008 | Hales 2008, p. 1372 (verified) |
| 19 | Stone 1974; Geisser 1975 | both, with DOIs and abstract passages (verified) |
| 21 | Mayr 1942; Rice 1976 | Mayr p. 120 (verified, archive.org full text); Rice via secondary quotation |
| 23 | Hutchinson 1957; Rice 1976 | Hutchinson p. 416 via secondary quotation (PMC2780934) + 1991 reprint DOI; Rice as above |
| 34 | Turing 1936; HMU 2006 | Turing §1 p. 231 (verified); HMU ISBN (Open Library record) |
| 41 | Vapnik 1995; Lampert et al. 2009 | Lampert abstract (verified); Vapnik resolved, secondary |
| 47 | Langley et al. 1987 | Simon 1973 abstract (verified primary); Langley 1987 publisher description (verified secondary); non-privilege clause declared programme-internal |
| 48 | Hempel & Oppenheim 1948; Popper 1959 | **retired** — real works whose text does not state the six-kind partition; replaced by the programme-internal primary source (template @ `acb38c8b`) with Wobbrock & Kientz 2016 as nearest parent for the *practice* only |

The addendum's sentence "AC05 … is therefore not earned by this file and is
not claimed" stays true of the addendum file. For the eight merged rows the
AC05 firewall of this package is retired: their citations are now verified
and in place in the parent, and AC05 is reconciled by
`gmi-833-ac05-citation-revival-v1/ISSUE_833_RECONCILIATION_AC05_V1.json`, not
by this package.

## 2. What changed in this package

`ac_lanes_harness_v1.py` (route A) and `independent_ac_oracle_v1.py` (route
B) read the crosswalk **at the blob this package froze** instead of at the
live path: route A takes the sha from `MANIFEST_V1.json` `parent_pins`
(parsed value), route B from the addendum's own pin line, and each
re-hashes the bytes (`blob <len>\0…`) before use. The blob is
content-addressed, so a squash merge cannot break it; if git or the blob is
unreachable the run stops in a distinct `PINNED_PARENT_UNREACHABLE` /
`PINNED_PARENT_MISMATCH` state — it never silently measures the live file
and never passes.

Why: this package's ACL-4 statement ("15 VERIFIED / 29 CITE-TF / 4
UNMARKED; 8 supplied by the addendum") is a measurement of the parent at
that blob, and its test `ac06_verification_split_disclosed` and hostile
`H5_cite_tf_never_promoted_to_verified` presuppose that split. Read against
the revised parent they would fail for a change this package did not make
(the corpus-wide-quantity trap). Pinning restores the measurement to the
object it was always declared over.

Consequence: `RESULT_V1.json` of this package is **byte-unchanged**
(`check_receipt_v1.py` reports "receipt matches the live two-route run"
against the pinned blob); no receipt was regenerated. The ACL-4 sentence in
the issue remains a correct statement about blob `9f4d25a5`; the live
parent's current split (48 VERIFIED-2026-09-19 primaries) is recorded by the
AC05 package, not here.

## 3. Not changed

`FREEZE_V1.md`, `AC_CROSSWALK_ADDENDUM_V1.md`, `AC_LANES_THEOREMS_V1.md`,
`RESULT_V1.json`, `MANIFEST_V1.json`, the test file, and the workflow.
