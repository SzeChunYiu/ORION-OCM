# Next integration boundary

Current source authority: [exit-code successor](resource-exitcode-records/CORE.md),
qualified on 23 source files with 12/12 profile cases and 65/65 focused controls.
The original 19-source and [prior 22-source](RESOURCE-SUCCESSOR.md) qualifications
remain historical; neither receipt authorizes the changed current runner bytes.

The resource controller and offline build profile have passed their authored
qualification; see RESOURCE-QUALIFICATION.md. The [pinned acquisition](ACQUISITION-RESULT.md)
and [authored two-package Lake build](LAKE-BUILD-QUALIFICATION.md) are now qualified.
The four registered corpus rows still await actual evaluator/source qualification.

## One production entry and exact envelope

Use the reviewed file entry, without ordinary imports of owned modules:

```text
<bound-python3.11> -I -S <frozen>/resource_boot.py run \
  --profile <bound-profile.json> --limits <bound-limits.json> \
  --output <new-supervisor-record-directory>
```

An existing source-only parent may source-load resource_boot.py and call
`resource_boot.load()["build_profile"].run(...)`. The parent must bind the actual
bootstrap bytes too. Do not place supervisor records inside any workload mount.
All writable artifacts must have their own host directories outside input trees.

For real registered rows, copy these exact settings from the frozen registration,
not the smaller authored controls:

| Setting | Value |
|---|---|
| memory_bytes / memsw_bytes | 21474836480 / 21474836480 |
| cpu_quota_us / cpu_period_us | 200000 / 100000 |
| pids | 128 |
| min_available_bytes | 25769803776 |
| min_free_bytes | 240518168576 |
| stop_free_bytes | 85899345920 |
| max_owned_bytes | 137438953472 |
| max_file_bytes | 8589934592 |
| poll_s / term_grace_s / reap_s | 1 / 5 / 10 |

Bind wall_s to the stage ceiling and remaining whole-dispatch allowance:
build 7200, export 900, prepare 900, final check 600 seconds; acquisition 3600 total,
whole dispatch 43200. The profile subtracts its own preparation time before the
controlled command. Cleanup continues afterward with measured cost. The
registrar must account for earlier acquisition, custody and completed stages,
and refuse dispatch once the whole allowance is exhausted.

## Acquired material handoff

The [acquisition entry](ACQUISITION.md) now supplies nine exact bare dependency
stores, with all command and material bytes retained. The original registered
corpus bare store and pinned Lean distribution remain separate inputs. The lower
resource_runner supplies aggregate supervision; the acquisition worker supplies
the Git transport/configuration policy. The offline build profile cannot fetch.

The successful V2 episode is still open. Verify its original boot identity and
whole deadline before every later phase; preparation, custody and waiting consume
that same clock. Reconstruct source trees from exact object identities, preserve
their Git HEADs and source bytes, and charge the shared cold work once. Never infer
that a bare-store acquisition receipt authorizes execution of acquired code.

The authored Lake fixture qualifies immutable source mounts and separate config,
build and cache artifacts. It does not qualify the acquired corpus/plugin closure.
The [exact materializer](MATERIALIZATION.md) and [layout helper](CORPUS-LAYOUT.md)
now have authored qualification. The real materializer has not dispatched; its
first scheduling window retained a headroom hold under the unchanged policy.
The layout helper returns verified mount fragments and requires an outer caller
to authenticate material receipts, preserve the original boot/deadline and supply
aggregate supervision. A helper result does not supply those caller guarantees.

Before the real build handoff, the orchestration adapter must charge all prior
episode-owned material and preparation bytes as well as new build artifacts.
The generic build runner currently counts its supervisor root and writable roots;
using it directly would omit earlier immutable owned copies. Implement and qualify
that accounting handoff before dispatch, preserving the registered total.

## Actual evaluator handoff

The native lane supplies the frozen exporter/association adapter and measured
Lean/Lake/compiler/plugin requirements. The acquisition lane supplies exact
read-only source/dependency trees. Generate complete directory inventories and
separate per-file x/m bindings for the required executable/library/plugin closure.
Include required public/private/server/IR metadata; do not thin source imports or
delete C artifacts required by Lake's registered route.

Review the allowed interpreted/source code for the no-neural requirement.
Newly built native plugins require explicit admission and a successor profile
before execution/mapping; a hidden writable-plugin fallback is not qualified.
Source-only kernel checking remains a separate profile from evaluator imports.

Only after registration audit, acquisition qualification and this actual code/
material profile are bound should the orchestration lane start the fixed rows.
This component provides conventional engineering controls; no OCM novelty,
learning, proof reconstruction or corpus semantic-coverage result follows.
