# Exposed F0 development episode 2

Recorded terminal: **CANNOT_CHECK**.

The proposer returned FOUND and candidate compilation returned zero. Extra Lean linter diagnostics caused the strict axiom-output boundary to return CANNOT_CHECK. This preserved receipt is not retrospectively promoted.

`raw/source-snapshot/` preserves the actual contemporaneous host source snapshot captured by this episode. All 22 files match its recorded source inventory.

- `raw/` preserves original JSON, input, mounted worker and checker source bytes.
  All process fields and absolute paths remain unchanged.
- `ORIGINAL_FILE_INVENTORY.json` records every original regular file.
- `GENERATED_ARTIFACTS.json` records generated artifact names, sizes and hashes.
  No `.olean` binaries or full Lean runtime binaries are copied.
- `SHA256SUMS` binds all archived files except itself.

This is an exposed engineering record, not a paper finding or whole-OCM
no-neural qualification. No tests, search, kernel replay or top-level source
edits were performed for preservation; the original episode directory remains
byte-identical.
