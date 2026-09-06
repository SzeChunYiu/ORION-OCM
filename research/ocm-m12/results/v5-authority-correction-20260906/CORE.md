# M12 current execution authority correction

All new V3/V4/V5 reports now identify engineering replay and retain the numeric
historical rule only as a diagnostic. Current scientific promotion is
`CANNOT_CHECK_CURRENT_SCIENTIFIC_PROMOTION`; protected reevaluation is `NOT_RUN`.
The V5 receipt command verifies archived custody only and refuses generation.

Owner: [#38](https://github.com/SzeChunYiu/ORION-OCM/issues/38#issuecomment-5556265815).
Scope: authority and custody. Comparator matching and independent evidence remain open.

- [Source bindings](SOURCE_BINDINGS.json) identify the final patch and shared PR80 verifier.
- [Raw inventory](SHA256SUMS.json) binds all packaged records.
- Initial test-first controls: 15 failures, 3 passes.
- Independently reviewed intermediate patch: 23 passes.
- Added all-mode wording/authority controls: 3 failures before correction.
- Final targeted run: 26 passes, zero skips, errors or failures.

The final executable command and read-only dependency configuration are in
[the command record](raw/authority-reviewed-command.json); raw JUnit and stdout are alongside it.
Tests use archived V5 phases to exercise the real report boundary, including
V3/V4 reporting. They do not execute lifetime machines or establish new outcomes.
Archive corruption controls operate in memory; seven original records were checked
byte-identical to base `68b444b094e26f35628eaa14a3dc2f42eda98ff8`.

PR80 was pending during this run: its verifier/archive were read from the isolated
support worktree. Normal integrated checks use the repository-local dependency.
This package is targeted engineering evidence, not a new current engineering
source receipt or a scientific promotion. Root owns integration and receipt generation.
