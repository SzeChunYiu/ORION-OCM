# Offline corpus build layout

This helper prepares independent copies and mount descriptions for the existing
offline build profile. **Actual corpus layout and build are not dispatched by
this qualification.** It does not authorize acquired code, prove a theorem, or
establish a neural-free evaluator closure.

The [current handoff repair](MATERIALIZE-HANDOFF.md) and
[successor record index](materialization-handoff-records/CORE.md) supersede the
predecessor source authority below. Safe dangling links now survive layout custody;
the unchanged execution-profile inventory still refuses them before execution.

## Input and output contract

Call `corpus_layout.prepare_layout(materials, lock_record, new_output,
deadline_monotonic=<original whole deadline>)`.

Each trusted material binding is
`{name, commit, tree, receipt: {path, sha256, bytes}}`.
The public entry requires corpus first, then the nine exact names/revisions from
the existing pinned lock validator. The corpus commit is fixed. The caller
authenticates materialization receipt provenance, boot identity and the original
whole-episode deadline, and supplies aggregate execution supervision.

The helper verifies the exact consumed receipt bytes before using them for
source/output overlap decisions. It refuses expired or substituted receipts
before creating an output. Later failures preserve partial output and
`LAYOUT_REFUSED`; only complete final correspondence yields `LAYOUT_READY`.

The output contains ten independent copies, intended for read-only material mounts:
root at /workspace and dependencies at /workspace/.lake/packages/<lock-name>.
Source bytes, executable modes, safe relative symlinks and detached Git metadata
are preserved. Source workspaces are not modified; no hardlinks are reused.

Only empty default layout directories are added. Nonempty writable-overlay
subtrees, path aliases and package overrides refuse. Ordinary tracked assets
remain visible. There is no seeded-cache policy or altered lock/package override.

`material_mounts` follows the existing build_profile inventory schema.
`writable` contains 13 separate artifact paths: scratch, config, cache and ten
package builds. The scratch mount is first at /work. Add the separately qualified
executor/library mounts, exact Lake command and external code-audit record;
these returned fragments are not a runnable or approved execution profile.

Before/post source inventories, copied content, added directories and the exact
final output set are recorded. Late copied-file, inventory and artifact injection
are refused. Copying/hashing checks the supplied deadline; inner timings exclude
imports and final receipt persistence, which the outer caller must charge.
Logical bytes and free space are measured. No hard disk quota, speedup or
complete lifetime-cost result is implied.

## Authored qualification and source succession

| Record | Observed result | Scope |
|---|---|---|
| Initial missing helper | 16 expected failures | Test-first absence control |
| First implementation | 16 passed | Authored root plus two dependencies |
| Late-layout falsifiers | Three failed; 18 passed | Stale copied bytes/inventory/cache reached false readiness |
| Repaired predecessor | 21 passed, zero skips | Complete final layout correspondence |
| Consumed-receipt repair | Two failed/one passed, then three passed | Returned bytes and post-read deadline |
| Bound-preflight repair | One reproduced failure/one clean refusal, then seven passed | No output creation from substituted overlap metadata |

The seven predecessor checks are focused regressions, with 19 other cases deselected.
They are not added to the overlapping predecessor counts. The initial preflight
hostile used an ancestor decoy and reached the existing overlap refusal; its test
correction and the subsequent disjoint-decoy reproduction are both retained.

The historical 21-control run has its own nine-file source snapshot and took
1.817804088 seconds as an outer process. The final seven-control successor took
0.464884894 seconds and retains a new nine-file before/post snapshot.
The three-control intermediate run is retained separately.
These are authored test-process costs, not actual corpus-build economics.

The borrowed Git fixture changed from `cfb8e01c…` to the portable test successor
`1f3f71be…`; historical evidence is not rebound to the new fixture.
Pre-handoff layout module SHA256:
`9a56251c805d16e837547508ec360bce1e3f8bbb9d166585ac289b3cdded6930`.
Unchanged predecessor layout tests SHA256:
`b487cea800a6de7c4e916b0cc35be2706ad60ee873f5330d2f7f40b5cb8a96a1`.

That predecessor changed only the two layout-owned files. The current successor
also repairs materializer directory modes and adds a separate handoff test module.
It has 14 targeted passes; integrated v4 has 425 passes, seven skips and two
registrar deselections. These overlapping qualifications are separate records.
Current source identities and the copied/input workspace-root postchecks are
specified by the handoff note and its 138-file integrated source freeze.

## Retained evidence

The following archive describes the historical layout generations. It remains
byte-identical and does not qualify the changed current module.
Start with [the archive index](corpus-layout-records/INDEX.json),
[source bindings](corpus-layout-records/SOURCE-BINDINGS.json) and
[generation ledger](corpus-layout-records/GENERATIONS.json).

| Artifact | Exact retained content |
|---|---|
| [qualification.tar.gz](corpus-layout-records/qualification.tar.gz) | 6,190 regular files; 4,661,552 raw bytes |
| Archive size | 1,012,351 bytes |
| Archive SHA256 | df2bb693597c9a3bd4fd544a150859b53da3bb388095381897c16ac92fb64971 |
| [Complete member map](corpus-layout-records/MEMBERS.json.gz) | Gzip-compressed path → SHA256/byte mapping |
| [Entry metadata](corpus-layout-records/ENTRY-METADATA.json.gz) | Original modes, timestamps, directory names, link targets and hardlink groups |

Every archived regular member was read back and compared with its original.
The source roots and entry metadata were rechecked unchanged.
Tar metadata is normalized; original filesystem metadata remains in the separate
entry inventory. The archive is evidence data, not an executable installation.

[Omissions](corpus-layout-records/OMISSIONS.json) explicitly record 135 symlinks
that were not followed, and two externally hash-bound binaries that were neither
copied nor revalidated here. This is not a complete interpreter/dynamic-library
closure. Earlier default pytest temporary fixture bodies were not protected
snapshots; optional collection refused after one had been removed. Their logs,
JUnit and source lineage remain, together with complete permanent final and
successor fixture trees. No missing artifact was reconstructed.

The [byte readback](corpus-layout-records/VERIFY.json) and
[package seal](corpus-layout-records/PACKAGE-SEAL.json) bind only the stated
authored records. Real materialization, offline acquired-code review, corpus
coverage, masked reconstruction and learned reuse retain their separate gates.
