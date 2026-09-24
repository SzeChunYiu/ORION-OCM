# AB terminology ratchet — amendment for issue #1049 (publication-aware custody)

**Observed defect.** On push to `main` the repo-wide ratchet failed with
"terminology debt increased". There were 14 new files with banned terms and no
regressions. None of the 14 was editable debt:

- Five `research/gmi-1068-r*/THEORY_V1.md` notes are sha256/blob-pinned by
  records of OTHER packages (for example the `gmi-1068-recursive-audit-v*`
  `SCOPE_SNAPSHOT_*.json` files and `gmi-1068-r6-genesis-repair-v2`). The old
  rule searched only the file's own package for pins, so it reported these
  files as `UNPINNED`.
- Nine freeze-bundle files (the `FREEZE_V1.md` or amendment documents of six
  packages, plus `gmi-833-h-realscale-four-family-v1/PRIOR_DISCLOSURE_V1.md`,
  whose manifest registers it as a freeze file "pinned here by custody commit so
  the terminology ratchet reports them as immutable") name a custody commit that
  squash publication removed from `main`. The old rule reported these as
  `UNREACHABLE` and enforced them.

**Repair.** Two custody facts, both checked on bytes and history and never on
file names:

1. **External hash pin.** When a JSON record in a different package carries the
   file's current sha256, git blob id or md5, the file is `PINNED_HASH`, with
   `pinned_by` naming that record. Editing the file breaks the pin, so the file
   becomes `UNPINNED` again.
2. **`PINNED_PUBLICATION`.** This state applies only when a named custody commit
   is unreachable AND all of the following hold:
   - the file was added in the first commit that ever touched its package;
   - that commit also added the package's `FREEZE*.md`;
   - the package directory did not exist in that commit's first parent;
   - the current blob equals the blob added there.

   Any edit after publication, any file added later, or a package that existed
   before its publishing commit stays `UNREACHABLE` and is enforced.

Immutable files are still measured and reported as informational. Count
regressions remain enforced everywhere.

**PR scope (item 3).** Pull requests already evaluate the new-file rule over
PR-owned paths only, and report other post-baseline files under
`unowned_new_files_with_hits` as informational. That rule is unchanged.

**Tests.** The unreachable-commit case in
`test_custody_pin_dies_with_the_bytes_it_pins` now asserts the publication proof
both ways. A freeze added by the root commit of a new package is
`PINNED_PUBLICATION`. An amendment added later stays `UNREACHABLE` and fails the
check. An edit after publication falls back to `UNREACHABLE`.

`test_external_pin_and_preexisting_package_hostiles` checks two further cases.
An external record pins a file, and the pin dies with an edit. A package whose
first commit carried no freeze is refused publication custody.

**Measured effect on `main` at `cc36a309`.** Before: 14 new files with banned
terms, FAIL. After: 0, PASS. Of those 14 files, 5 are now external `PINNED_HASH`
and 9 are `PINNED_PUBLICATION`.

**Claim ceiling.** This is gate custody only. `CORPUS_TERMINOLOGY_CLEAN` and
`MIGRATION_COMPLETE` remain forbidden.
