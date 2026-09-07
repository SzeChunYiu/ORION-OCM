# Resource exit-code correction records

The current correction preserves a child's already observed exit code when a subsequent cleanup snapshot fails, including polls inside the cleanup loop. A measurement failure remains visible; the repair does not invent an exit code when none was observed.

## Current result and retained generations

- Current qualification: **23 frozen source files**, **12/12 authored profile cases**, **65/65 focused controls**; no skips. `RESULT.json` is the exact qualification summary; the matrix result, source snapshots, JUnit and raw process streams are in `final-qualification.tar.gz`.
- Prior successor: **22 files**, still bound to `../resource-successor-records/SEAL.json`. `prior-source/` contains exact archived bytes, including the earlier runner; `PRIOR-SOURCE.json` identifies each source member. These are historical data, not current runtime code.
- Original qualification: **19 files**, still bound to `../resource-records/SEAL.json`, recursively verified through its retained source copies. Both earlier packages and guards remain unchanged.

The new guard is `../resource_exitcode_evidence.py`. Run it with the selected Python 3.11 interpreter using `-I -S`; it checks the three generations separately and executes only pinned live audit helpers. Archived resource sources, binaries and external host-input paths remain data.

## Retention and cost

The deterministic archives retain **881 regular files / 5,812,553 raw bytes**: 496 final qualification files and 385 development files. Their total compressed size is **213,138 bytes**. Every original regular file was hashed before archival and rechecked afterward; every tar member was read back and matched to its map. `INDEX.json` binds both archives/maps.

`OMITTED-ALIASES.json` records all **55 symlink aliases** without following them. No regular file is omitted from either source root. `HOST-INPUTS.json` retains the original 11 external executable/library identities; the portable guard does not revalidate or reconstruct the host installation. The authored fixture/plugin binaries referenced there remain in the original resource development archive; this correction package is not a standalone runtime.

`COSTS.json` remains byte-identical: 13.019591085 seconds across recorded development and fresh qualification processes. Its phrase about no new native work means no new native mathematical proof/Lean or real-corpus work: **12 authored native C fixture/profile cases did execute**, and their wall time is charged. Packaging is separately measured in `PACKAGING.json` and `ARCHIVE-PROCESS.json`; CPU/RSS or unrecorded editing time is not inferred.

## Evidence and scope

- `SOURCE_FREEZE.json`: current freeze SHA256 `9930a83d492f146776911b39779a0142f81ed27206d244a03eaecf2c1db7b4c5`.
- `INDEPENDENT-AUDIT.json` and `.md`: exact independent raw/source/cleanup review; no reviewer resource reexecution.
- `development-history.tar.gz`: initial two-control RED, first repair, cleanup-loop RED and final repair history, all retained without relabeling.
- `SEAL.json`: recursive exact package inventory, using the existing successor sealed-container schema; `INDEX.json` explicitly identifies the exit-code correction layer.

This is an engineering evidence/custody correction. It establishes no corpus solving, Lean proof, learning, scaling, language capability or neural-absence result. No resource or corpus operation was executed during packaging or portable guard verification.
