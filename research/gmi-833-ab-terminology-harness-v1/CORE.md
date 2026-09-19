# CORE — `gmi-833-ab-terminology-harness-v1`

**Issue #833, section AB. 34 rows earned; AB02, AB08, AB25 deliberately open.**
Claim ceiling `REGISTERED_TERMINOLOGY_AUDIT_VERIFIED_V1`.

## What it establishes (exact numbers)

| result | statement | number |
|---|---|---|
| ABH-1 | every AB row's own named comparison terms are covered by the registered audit | **153/153** — **149 by the frozen parent crosswalk** (48 rows), **4 supplied here** (`algorithm class\|configuration class`, `possibility space`, `novel implementation`, `verifier feedback`); **34/34** rows EARNED |
| ABH-2 | audit clause vs corpus-state clause, both measured | **9703 banned-term sites in 1400 of 2572** flagship markdown files at `source_main` — disclosed, not absorbed; **AB02 stays open** |
| ABH-3 | blocking repo-wide ratchet (the parent workflow is path-scoped and `\|\| true`) | baseline frozen; 0 regressions, 0 new files; end-to-end hostile moves 0 → 3 hits and is named |

Two routes agree on every shared quantity. **Eleven hostiles**, each asserted
to have moved its own quantity — including two that feed the AB13 and AB28
evidence predicates decoys (a receipt that *talks about* grammar bias with
identical bias profiles; prose that *says* "operational criteria" and proves
nothing) and are rejected. Null: **0/200** randomized crosswalk tables earn a
row while the true table earns 34/34. 22 tests, both modes.

## Ratchet scope (deliberate, not implicit)

On `pull_request` the gate runs with `--owned-files` — the PR's own markdown
diff. A lane is failed for banned terms in files **it** added or grew, never
for another lane's; a new unowned file with hits is reported informationally.
On `push` to `main` the strict repo-wide rule applies. A gate that fires on
work you did not do is a gate that gets switched off.

## The guard that makes this honest

`test_every_required_term_occurs_in_the_row_text` asserts that **every**
required comparison term literally occurs in the AB row's verbatim text. A
requirement cannot be invented to make a row pass, and a row-named term cannot
be quietly dropped. It caught two of this package's own first-draft
requirements.

## Reproduce

```sh
python3 -I -B  research/gmi-833-ab-terminology-harness-v1/ab_harness_v1.py
python3 -I -B  research/gmi-833-ab-terminology-harness-v1/independent_ab_oracle_v1.py
python3 -I -B  research/gmi-833-ab-terminology-harness-v1/terminology_ratchet_v1.py
python3 -I -B  research/gmi-833-ab-terminology-harness-v1/test_ab_harness_v1.py
python3 -I -O -B research/gmi-833-ab-terminology-harness-v1/test_ab_harness_v1.py
python3 -I -B  research/gmi-833-ab-terminology-harness-v1/check_receipt_v1.py
```

Stdlib only; every reported quantity is an int.

## Re-baseline at main `b5193f32` — prose-only count semantics

The ratchet counts **prose** hits. Three non-prose classes are exempt
(`classify_hits` in `terminology_ratchet_v1.py`): verbatim issue-row
quotations (checkbox rows, also numbered or backticked), inline code spans and
fenced blocks, and identifier tokens (paths, `snake_case`, `gmi-<n>-` package
names, `-v<n>` suffixes, file extensions). A hyphenated or slashed prose
compound is not an identifier and still fires. On the same tree the old
semantics counted 9627 sites; the regenerated baseline holds **8797 in 1416 of
2740** files (10021 raw parent hits: 403 quoted rows, 798 code spans, 23
identifiers exempt). The frozen `9703 in 1400 of 2572` figure at
`source_main` is unchanged as a historical measurement.

## Immutable custody files — pinned bytes, not file names

A freeze and its amendments may never be edited after their receipt exists;
that is the custody property the #833 standard rests on, so a banned term in
one cannot be reworded. The ratchet therefore classifies every new file with
hits by `custody_state`: **PINNED_COMMIT** when a commit the package names
under a freeze/amendment/custody key (`freeze_commit`, `freeze_amendments`,
`custody_pins`, …) carries the same blob at the same path; **PINNED_HASH** when
the file's git blob sha, sha256 or md5 appears in a JSON record of its package
(a manifest, a receipt, a register, a reconciliation snapshot's
`*_md5_at_extraction`); **UNREACHABLE** when a named custody commit is not in
the object store — reported distinctly and still enforced, never silently
passed; **UNPINNED** otherwise. Only the two pinned states are immutable: such a
file is measured and listed under `immutable_files_with_hits` (informational)
but does not fail the new-file rule. Nothing is exempt by *name* — a
`FREEZE_V1.md` nobody pinned is an ordinary file and still fails, a pinned
`SNAPSHOT.md` is immutable — and the exemption dies with the bytes it rests on:
editing a pinned file breaks its pin and the file becomes UNPINNED, so a lane
cannot edit a freeze and keep it exempt. Count regressions are never relaxed.
On the tree at the time of writing: 103 freeze/amendment files PINNED_COMMIT,
10 PINNED_HASH, 80 UNPINNED, 1 UNREACHABLE; the baseline is unchanged.
