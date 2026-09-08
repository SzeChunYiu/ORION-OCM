# Fixed phase cost receipt v1

This is a data-only accounting supplement. It never changes the retained semantic analysis.
Full CPU/lifetime economics remains ECONOMICS_CANNOT_CHECK: cgroup CPU, outside own CPU,
and GNU time waited CPU are separate observations with unresolved overlap/helper scope.
The earliest crossing is UNAVAILABLE. No complete-cost boolean is supplied to the analyzer.

## Exact receipt

Write canonical unary_method_plain.raw JSON (no trailing newline).
Each receipt has exactly these fields:

- schema: "ocm.unary-phase-process-cost.v1"
- phase: "PREPARATION" or "LAUNCH"
- argv: actual nonempty string array, first argument absolute
- cwd: actual absolute working directory
- wrapper: {path, sha256, bytes}, the same prebound fixed wrapper source for both phases
- sources_before, sources_after: exact unary_method_outer.sources() maps, matching PLAN.sources
- returncode: actual integer; error: null on normal completion, otherwise retained observation
- child_reaped: actual boolean
- started_monotonic_ns, ended_monotonic_ns: actual ordered integer observations surrounding phase command
- gnu_time, stdout, stderr: exact retained regular-file {path, sha256, bytes} bindings
- products: the exact map below

GNU time raw output must be:
```
wall_s=12.34
user_s=1.23
system_s=0.45
```
Use /usr/bin/time -f 'wall_s=%e\nuser_s=%U\nsystem_s=%S' -o TIME.txt -- COMMAND...
Keep LC_ALL=C. Resolution is 0.01 s; no exact residual equality with nested high-resolution spans.
Nonzero GNU time diagnostics remain raw evidence and may make the strict measurement unavailable.
GNU time encloses command product persistence and exit. It does not include the observer's
own receipt persistence, between-phase work, or every namespace descendant's CPU.
No nested CPU/wall addition is permitted.

PREPARATION products exactly:
```json
{"PREPARED":{"path":".../PREPARED.json","sha256":"...","bytes":123}}
```
LAUNCH products exactly: OUTER, STARTED, BOOTSTRAP, BUILD_PROFILE, ANALYSIS.
Paths respectively:
prepared/OUTER.json; prepared/STARTED.json; prepared/work/BOOTSTRAP.json;
prepared/controller/build-profile-receipt.json;
prepared/work/coordinator/ANALYSIS.json.
All bindings use host paths. BOOTSTRAP's internal /assay/work analysis path is mapped
only to the fixed prepared/work counterpart and its exact bytes are checked.

## Concrete existing invocation

Preparation command is a fixed source-bound Python script adding only project/src,
research/math-language-v1 and research/math-language-learning-v1. It calls:
```python
P.prepare(prepared_root, runtime_snapshot, run_id=frozen_run_id,
          mode="REGISTERED", duration_ns=L.DURATION,
          cpu=frozen_lowest_allowed_cpu, input_value=None, review=frozen_review_binding)
```
Use the exact default Python with -I -S -B. No generic callback/import-root interface.
Preparation must finish before launch; this call does not issue STARTED or draw tasks.

Launch command:
```
PINNED_PYTHON -I -S -B PROJECT/research/math-language-learning-v1/unary_assay_launch.py PREPARED_PATH PREPARED_SHA256
```
It issues the original clock and invokes the existing resource controller exactly once.
Root freezes wrapper source, preparation arguments/review and launch recipe before unused seal.
No scientific call has occurred during this engineering qualification.

After both observed commands, call the source-bound data-only function:
```python
unary_assay_cost_closure.close(prepared_binding,
    {"PREPARATION": preparation_receipt, "LAUNCH": launch_receipt},
    wrapper=frozen_wrapper_binding)
```
It rereads/binds retained products, returns measured phase-process wall when available,
and always leaves full CPU/lifetime economics unavailable. Persist its result additively.
Missing receipts/products, malformed time, source drift, failed exit or incomplete cleanup
never establish complete wall observation. Reached measurements remain partial observations.
No semantic solver, generator, analyzer rerun or result-dependent selection is performed.
