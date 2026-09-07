# Resource post-dispatch successor

The controller and offline profile now preserve whether dispatch was never
attempted, attempted with no confirmed handle, or started with a returned PID.
Monitoring or custody failure after launch cannot be reported as a setup refusal.

Current qualification: **12/12 authored host profile cases and 62/62 focused
controls passed**, with no final failures or skips. This repairs infrastructure
accounting; it supplies no corpus coverage, Lean proof, learning or novelty result.

## Dispatch and failure contract

- Resource receipt v2 records dispatch.state: NOT_ATTEMPTED,
  ATTEMPTED_UNKNOWN, or STARTED, plus attempted/PID evidence.
- Before launch, ordinary failure is SETUP_REFUSED. A launch exception is
  DISPATCH_UNCERTAIN; missing reaping evidence may override the final terminal
  with CLEANUP_INCOMPLETE. It never establishes that no child executed.
- A started command's monitoring exception is MONITOR_FAILED. Missing or
  unreadable required raw output and failed final disk accounting are recorded
  as evidence errors; eligible final outcomes become EVIDENCE_FAILED.
- primary_outcome retains the first supervised outcome, phase and original
  error before cleanup/evidence overrides. An observed nonzero child exit is
  COMMAND_FAILED, including when later custody or cleanup fails. The final
  return code, raw errors and cleanup evidence remain separately available.
- The profile prepares command arguments before marking an attempt. No returned
  runner receipt gives DISPATCH_UNCERTAIN; failed custody after a returned
  receipt gives POST_DISPATCH_CUSTODY_FAILED.
- A loaded policy is retained after an uncertain attempt unless cleanup
  affirmatively proves the child reaped and controller membership empty.

## Exact source and retained evidence

The [successor index](resource-successor-records/INDEX.json),
[seal](resource-successor-records/SEAL.json),
[result](resource-successor-records/RESULT.json), and
[source freeze](resource-successor-records/SOURCE_FREEZE.json) bind this iteration.
The freeze is a4d30369035cd8d483293b8295418d1158d50772f6358875956e5fe1b1dcd758.
The successor seal is 3d900f8700445844c1b3c926a1ff150f702c43f841e94a208608ff171645d8c7
(32 retained files, 692,471 bytes including seal). These documentation additions
are outside the executed 22-source freeze.
The executed entry remains source-only python3.11 -I -S source/resource_boot.py.

Only two production files changed:
resource_runner.py SHA256
63f0348824a111835495e29d19c56e637e198a86cd64492cb3a43a531dc2c8c9;
build_profile.py SHA256
b20fc1e387fa30d813352c28e0e0e853ca16b3e8812a18db009db80c67e587e7.
One previous test expectation changed and three authored control files were added.

The final archive retains 475 regular files / 5,433,673 raw bytes in 163,865
compressed bytes. Development history retains 1,043 files / 1,269,285 raw bytes
in 186,413 compressed bytes. All regular source/packet/log/receipt bytes are
retained; 115 nonregular pytest/authored aliases are explicitly listed in
[OMITTED-ALIASES](resource-successor-records/OMITTED-ALIASES.json).
Host inputs remain externally bound; this is not a standalone archived runtime.

The [original records](resource-records/INDEX.json), original guard and
19-source freeze are unchanged. Their source bytes are copied exactly under
the successor's historical-source/ and remain tied to the original archive.
The additive resource_successor_evidence.py checks both historical custody
and the distinct current source/run bindings; it executes no workload.
Run it from any directory with python -I -S /absolute/path/resource_successor_evidence.py.
Its 23 portable controls and retained actual-data invocation passed; the
[independent guard review](resource-successor-review/GUARD_REVIEW.json) checks
those bindings without re-running any resource or native workload.

## Validation and costs

The fixed 12-case profile recipe was copied byte-identically from its predecessor.
Actual cases cover memory+swap, CPU, PID, offline/file/exec/plugin policy,
detached descendants, spool/file limits, wall stop and host interruption.
All 12 ended with reaped/empty/removed controllers and removed policy; source,
helper and raw-stream identities were checked after execution.
The [independent raw review](resource-successor-review/AUDIT.json) confirms these
bindings; its [reviewer correction](resource-successor-review/AUDITOR-CORRECTION.json)
is retained separately from the immutable qualification.

Twenty new focused cases cover clean and exit-7 children, launch uncertainty,
monitor/sample/disk/raw faults, missing raw output, outer lost receipt/custody,
argument preparation and cleanup overrides. Their short children really ran;
their authored in-memory controllers do not independently qualify aggregate
limits. Seven existing host-only controls were skipped in portable preflight,
then executed successfully in the final 62-control qualification.

The 20 GiB memory+swap / 2 CPU / 128 PID envelope was checked using a short
authored timing case, not the prospective corpus duration. Sampled spool
overshoot was **4,103,114 bytes**; sampled disk stop is not a hard disk quota.
Matrix outer wall was 3.822560 s; focused outer wall was 3.572956 s
(pytest reports 3.43 s). [COSTS](resource-successor-records/COSTS.json) retains
all recorded development attempts separately; CPU/RSS and editing/packaging
cost are not inferred from these wall measurements.

No actual corpus acquisition/build, row solving, native 47-control rerun or
neural absence claim was added. The registration, native adapter and
acquisition/real evaluator profile remain separate gates.
