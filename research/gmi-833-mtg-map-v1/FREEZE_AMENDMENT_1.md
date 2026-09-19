# FREEZE_AMENDMENT_1 — gmi-833-mtg-map-v1 (numbered amendment; `FREEZE_V1.md` is not edited)

Governing clause: `FREEZE_V1.md` § "Order discipline" and § "No neighboring row is earned here." This amendment is
committed **before** any executor, oracle, test, receipt, theorem note or workflow of this package exists (only
`FREEZE_V1.md`, `MTG_ROWS_V1.json`, `PARENT_PINS_V1.json`, `adjudication_v1.py`, `build_map_v1.py` precede it).
It changes no row text, no pin, no claim ceiling and no forbidden promotion. It records four facts found while
re-reading fresh `main` (`0a64368e`) before implementation, each with the clause it governs.

## A1. Freeze-commit reachability after the tranche-1 squash merge

The four tranche-1 freezes were committed at `fdd7255e` (tree for this package: `FREEZE_V1.md`, `MTG_ROWS_V1.json`,
`PARENT_PINS_V1.json` only). PR #1061 was squash-merged as `5f7c1168`; `fdd7255e` is **not an ancestor of `main`**
(`git merge-base --is-ancestor` exit 1; no remote branch carries it). At `5f7c1168` this package's directory holds
exactly `FREEZE_V1.md`, `MTG_ROWS_V1.json`, `PARENT_PINS_V1.json`, `adjudication_v1.py`, `build_map_v1.py` — no
implementation, receipt, theorem note or workflow — so `5f7c1168` is the freeze commit this package's `MANIFEST_V1.json`
pins and its CI custody step checks. The FRZ-1 census reports the three tranche-1 packages' `freeze_commit`
(`fdd7255e`) in the distinct state `UNREACHABLE_ON_MAIN_AFTER_SQUASH` — never as a pass and never as a failure of
the five programme packages, whose freeze commits (`fea6549a`, `b48d236d`, `8af45335`, `39894c4b`, `302ad7fe`) are
merge-reachable on `main` and each hold only `FREEZE_V1.md`. Row 47's frozen evidence sentence about `fdd7255e` is
kept verbatim; the receipt records it as `verified_pre_squash_in_lane_worktree` with the tree listing above.

## A2. Row 51 frozen count is not reproducible: 22 → 26 (19 distinct)

`adjudication_v1.py` row 51 cites this package's own field `counts.succ1_open_successor_entries: 22` and its evidence
sentence says "22 entries in all". The exact census over the five programme manifests is **26** entries
(7 + 4 + 4 + 5 + 6), **19** distinct strings. Neither reading gives 22. Under the governing clause the executor
reports the exact numbers; RA-1 evaluates the row-51 self-citation against the amended expected value `26` and
records `s6_instruction_followed: false` and `audit_shape_disclosed: POST_HOC_SUSPECT` **for row 51 only**; the
reconciliation line for row 51 states "26 entries (19 distinct; the frozen text said 22 — amended, A2)". No other
row is affected; every other cited field is verified against its frozen value unchanged.

## A3. Rows already reconciled live are not re-issued

Rows 0, 8, 10, 11, 12, 15, 16, 23, 24 were reconciled by their own tranche-1 packages and are checked on the live
comment (fetched 2026-09-19, 13,567 chars, 9 checked). The freeze delegated them; their `old` lines no longer exist
live. `build_map_v1.py` places them under `delegated_already_reconciled` (verbatim `new` from the tranche-1
receipts, for the map only) and emits `replacements` only for rows whose `- [ ]` line is live. No neighboring row
is earned here.

## A4. Own-receipt citations are evaluated in-process

Rows 47 and 51 cite `gmi-833-mtg-map-v1` fields. The executor evaluates those against the result dictionary it is
computing (same run), so `RESULT_V1.json` never depends on a prior copy of itself; `build_map_v1.py` then pins the
committed receipt's blob sha into `CITATION_TABLE_V1.json`, and the route-B oracle re-verifies that pin from bytes.
