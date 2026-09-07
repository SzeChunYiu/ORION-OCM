# Next integration boundary

Current source authority: [post-dispatch successor](RESOURCE-SUCCESSOR.md),
qualified on 22 source files with 12/12 profile cases and 62/62 focused controls.
The original 19-source qualification below and its sealed archives remain historical;
they are not a receipt for the changed runner/profile bytes.

The resource controller and offline build profile have passed their authored
qualification; see RESOURCE-QUALIFICATION.md. This does not dispatch any of the
four registered corpus rows. The registrar, acquisition profile, actual evaluator
code closure and native adapter remain separate gates.

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

## Acquisition-specific profile is still absent

The lower resource_runner supplies aggregate supervision but no network,
filesystem, executable or Git endpoint policy. It is **not sufficient by itself**
for qualified acquisition. The offline build profile deliberately cannot fetch.

First prefer the existing verified bare corpus and already pinned dependency/
toolchain stores when they have the required objects. Verify exact immutable
object IDs before reuse and charge materialization plus verification separately.
This still requires a registered read-only input and create-only output route.

For missing sources, the next bounded implementation is one acquisition profile
owned by the registrar/acquisition lane, reusing the reviewed resource controller:

1. Bind the exact Git executable/helper/library closure and the frozen public
   repository URLs/commit IDs from the lock registration. No branch/tag following,
   recursive submodule fetches, hooks, arbitrary shell, or executable source files.
2. Use new owned bare stores, explicit no-prompt/no-credential settings and a
   cleared environment/config search. Bind the necessary HTTPS resolver/CA inputs.
   Do not inherit user Git config, agent sockets, HOME caches or credentials.
3. Register and test the allowed fetch endpoints/transport behavior, including
   redirects if permitted; do not equate generic network access with a URL policy.
4. Keep all Git descendants under the same 20 GiB/2 CPU/128 PID controller and shared
   acquisition deadline. Preserve partial output, failed attempts, object counts,
   transfer bytes and exact refs; verify each received object/pin before handoff.
5. Qualify the network/profile controls on harmless authored/public metadata
   before the first real registered dependency fetch. Any policy/setup failure
   remains CANNOT_CHECK, with unreached rows retained. No unbounded fallback.

This note does not implement or qualify that acquisition profile.

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
