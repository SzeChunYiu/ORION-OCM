# Materializer-to-layout handoff successor

This is an authored filesystem/Git boundary repair. No acquired corpus tree,
registered row, build, resource profile or scheduling state was dispatched.
The original episode clock and scheduling records are unchanged.

## Repaired behavior

`materialize_git.materialize` explicitly sets the workspace root and tracked
Git directories to `0755`, independent of the caller's umask. It checks tracked
directory modes in the output audit and the workspace-root mode before success.
File modes remain the registered Git `100644`/`100755` modes; Git metadata keeps
its existing read-only normalization. Private output containers remain private.

`corpus_layout.snapshot` uses non-strict resolution for relative symlinks.
Safe dangling links are retained as exact link text, just as the materializer
already permits. Absolute links, resolved escapes, metadata links and cycles
still refuse. No target is created or substituted to make a link resolve.

Layout requires a `0755` input workspace root, normalizes copied workspace roots
and newly added empty overlay directories to `0755`, and verifies the final
workspace-root modes. The final source pass independently rechecks each original
workspace-root mode because recursive snapshots exclude their own root entry. Existing directory modes, including read-only `.git`
metadata directories, are copied unchanged. Host-only container/artifact modes
remain recorded under the caller's environment; they are not tracked Git modes.

## Separate execution limitation

The unchanged `build_profile_policy.inventory` still uses strict symlink
resolution. A layout containing a dangling link therefore passes this custody
handoff but cannot satisfy that execution-profile inventory. The targeted
controls explicitly observe this refusal.

**Queued caller requirement:** before any build profile uses dangling links,
qualify a separate profile-policy successor and its mount/containment behavior,
or retain the explicit profile refusal. Do not rewrite tracked links, invent
referents, or reuse an older profile receipt to bypass this boundary.
`LAYOUT_READY` and returned mount fragments are never execution authorization.

## Retained authored evidence

External root on billy-laptop:
`/home/billy/orion-director-work/20260907/materialize-handoff-qualification-v1`.
Each attempt has exact source before/after snapshots, command, streams, JUnit,
process costs and an explicit independent pytest temporary root.

| Generation | Actual outcome |
|---|---|
| `01-red` | Six failures and six passes, reproducing the two handoff defects and missing mode-drift checks |
| `02-green` | One collection error from an indentation mistake; no test executed despite the directory name |
| `03-repaired-green` | 12 passed, before the independent source-root postcheck finding |
| `04-source-root-red` | One failure/one pass, 12 deselected; late input-root mode drift incorrectly passed |
| `05-final-green` | 14 passed, zero skipped/errors/failures |

The final 14 controls cover four actual nested-Git handoffs (existing/dangling links
under umasks `022`/`077`), five prohibited-link forms, two materializer mode
mutations, one late copied-workspace-root mutation and a clean/changed original
workspace-root pair. Every changed umask is
restored in `finally`. Authored source and detached Git metadata are preserved.

The final test process took 0.616069505 seconds outer wall time; waited-child
user/system times were 0.401006/0.118219 seconds. These are targeted test-process
costs, not production materialization economics or a complete lifetime estimate.
No older full suite was rerun. Root's current integrated qualification is separate.

## Source succession

Current materializer SHA256:
`53e931d6a93899a6d68ffc4a111c780c0d0414585d731166ce87278e7e4993f5`.
Current layout SHA256:
`ccd43309d1a87eb3d206d5a7b4642b98f3516b66e118a38e6676f3389456b39c`.
New targeted controls SHA256:
`c71ff025436cc9f5a4bc52203338df95bca176b4535f47104ee7986c07682052`.

The older 26/47 materializer/entry and 21/7 layout qualifications, the original
PR137 sources, and all sealed archives remain historical and unchanged. The
[predecessor layout note](CORPUS-LAYOUT.md) describes those earlier
source generations; its recorded hashes do not qualify this successor.
