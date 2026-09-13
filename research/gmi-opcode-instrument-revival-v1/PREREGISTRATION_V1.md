# Opcode-only setter intervention: registered before execution

This is an instrument diagnosis, not another parity timing experiment.
Frozen V5 and its refused 3.13 packet remain historical evidence.

## Parent and intervention

Parent commit: `2ea3a617283bbe0f854f11df2ec4afcd57cbd848`.
Parent path: `research/gmi-grand-unification-v1/nn_nonnn_point_parity3_experiment_v5.py`.
The raw parent snapshot is byte-identical, SHA256
`5b6e4993a3592e9768c68c14ac5ccfddd19ce79190402f066af1c178bd3b03f0`.
Loading its definitions never invokes its benchmark entry point.
The original collector runs unchanged. The repaired collector is its exact
source with one added statement: `frame.f_trace = tracer` immediately before
`frame.f_trace_opcodes = True` in the target-frame call callback.
Candidate bodies, inputs, output obligations and collector loops are unchanged.

## Registered four-cell design

Use the laptop's explicit CPython 3.13.12, recorded by binary SHA256.
Run original/forward, original/reverse, repaired/forward, repaired/reverse
in four fresh, sequential subprocesses. Each cell executes every candidate
on all eight inputs, then repeats all candidates in the reverse order.
Thus every cell retains 64 candidate invocations across two passes.
No candidate executes before its first collected call; disassembly is read-only.
Never warm away, omit, replace, or retry a failed first call.

Before invocation, the exclusive freeze file binds interpreter, sources and
schedule. Before each subprocess, reserve its cell with exclusive creation.
Retain raw stdout, stderr and exit code, including unsuccessful executions.
A recorded failure does not stop collection of the remaining candidate rows.
Do not overwrite a reservation or execution packet.

## Falsifying checks and outcome rule

Independently disassemble the native code objects. Exclude CACHE and RESUME,
reject branches, exception tables and suspension; require a final return.
For each of eight frames require the exact complete offset sequence, integer
parity output computed as sum(input) modulo 2, and a return event.
Do not call the parent's opcode validator. Recompute all recorded verdicts.

The repair is established at this envelope only if all 128 repaired frames
are complete and the 128 original frames contain at least one incomplete
witness. If either condition fails, retain the registered negative result.
Predicted mechanism: the first instrumented call of each fresh code object
loses opcode events in the original; the second pass is complete. Both fresh
initial orders distinguish this from the previously claimed process-global
first-session effect. Prediction and intervention success are separate claims.

The CPython source suggests the cause; intervention evidence will constrain
the final attribution. No wall/process timings, warmup, benchmarking,
tracemalloc or new family adjudication occur. Opcode events are instrument
observations, not physical execution-time measurements. This is not a new
independent-host replication or a retroactive validation of V5.

## Primary mechanism parents

The documented explicit frame callback assignment is supported by
[sys.settrace](https://docs.python.org/3.13/library/sys.html#sys.settrace).
Pinned CPython 3.13.12 sources:
[frame setters](https://github.com/python/cpython/blob/v3.13.12/Objects/frameobject.c#L920),
[call trampoline](https://github.com/python/cpython/blob/v3.13.12/Python/sysmodule.c#L1051),
[legacy opcode enabling](https://github.com/python/cpython/blob/v3.13.12/Python/legacy_tracing.c#L175).
This adapts an established debugging API; no technical novelty claim is made.
