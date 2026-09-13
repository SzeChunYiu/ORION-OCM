# First-call opcode collection repaired at a registered envelope

The registered one-line intervention restored all 128 repaired opcode witnesses.
The unchanged original collector produced 120 complete witnesses out of 128:
each fresh candidate code object's first call had an empty opcode list, in
both forward and reverse initial orders. All outputs and returns were correct.
Every second-pass witness was complete. No invocation was warmed away or discarded.

The [portable receipt](OPCODE_REVIVAL_RECEIPT_V2.json) binds the raw execution records.
The [preregistration](PREREGISTRATION_V1.md) and
[freeze](OPCODE_REVIVAL_FREEZE_V1.json) precede the four child invocations.
All 256 calls, including eight incomplete originals, remain in the raw stdout.

## Exact intervention and evidence

In the target-frame call callback, add exactly one statement:

```python
frame.f_trace = tracer
frame.f_trace_opcodes = True  # Existing statement, unchanged.
```

The complete source diff is checked after extracting the collector from
the byte-pinned V5 parent. Candidate bodies, eight inputs and call loops
remain unchanged. Definitions are loaded without invoking V5's main,
preflight, capability passes, warmups, timing or memory measurements.

Each of four fresh processes runs two passes: initial forward/reverse order,
then its reversal. Both original cells show the same first-use defect;
both repaired cells have complete first and repeated calls.

| Candidate | Native events/call | Original first 8-call pass | Repaired first pass |
|---|---:|---:|---:|
| Threshold DNF | 55 | 385 of 440 | 440 of 440 |
| XOR | 9 | 63 of 72 | 72 of 72 |
| Sum thresholds | 36 | 252 of 288 | 288 of 288 |
| Lookup | 16 | 112 of 128 | 128 of 128 |

These numbers hold in both fresh initial orders. Across both passes and orders,
original has 3,480 observed events; repaired has all 3,712 expected events.
The oracle reconstructs each complete straight-line instruction sequence from
native disassembly, then checks every offset, integer parity output and return.
It never invokes a candidate or calls the parent's validator.

## Mechanism supported by the intervention

Pinned CPython 3.13.12 initializes a frame with no local trace callback.
Its opcode-flag setter enables instruction instrumentation immediately only
when a local callback already exists.
[Frame initialization and setters](https://github.com/python/cpython/blob/v3.13.12/Objects/frameobject.c#L920).

The global call trampoline invokes the Python callback first and stores its
returned callback afterward using direct field assignment. That later store
does not invoke the Python attribute setter.
[Call trampoline](https://github.com/python/cpython/blob/v3.13.12/Python/sysmodule.c#L1051).

Legacy event dispatch checks the opcode flag before invoking the Python
callback. In the original first call, enabling the flag inside that callback
therefore occurs too late for this pre-callback check; the return dispatch can
enable the code object's instruction events for later calls.
[Legacy trace dispatch](https://github.com/python/cpython/blob/v3.13.12/Python/legacy_tracing.c#L175).

The explicit callback assignment makes the subsequent opcode-flag setter
enable instrumentation before the candidate body executes. This is a supported
debugging API use.
[Documented explicit frame tracing](https://docs.python.org/3.13/library/sys.html#sys.settrace).

The source ordering predicts the observed per-code first-use failure and its
repair. The controlled insertion and both fresh orders support that mechanism
for this interpreter build. They do not establish every possible tracing defect
or an interpreter-independent language guarantee. This is assimilation of the
existing tracing API, without a technical novelty claim.

## Relation to the earlier refused packet

The #547 CPython 3.13.12 packet retained diagnostic traces produced after an
earlier preflight exception. Its complete diagnostic DNF witness and incomplete
later candidates cannot establish a process-global first-session rule.
The new experiment supports a code-object first-use account on the laptop;
the historical remote packet did not retain its failing preflight traces,
so this diagnosis does not reconstruct unrecorded events as observations.

Earlier unvalidated undercounts would cheapen XOR, sum thresholds and lookup
relative to fully counted DNF. The earlier prose's direction of bias was reversed.
This experiment preserves the original V5 source and refused raw packet.

## Scope, costs and replay

Recorded environment: CPython 3.13.12, Clang 21.1.4, Linux 5.15.0-139-generic,
x86_64, glibc 2.35; exact interpreter binary hash is in the freeze. This differs
from #547's Linux 6.18 remote-container envelope. It is an opcode diagnosis,
not completion of V5's timing or independent-host replication obligation.

The apparatus uses four child processes, 256 candidate invocations, static
disassembly and event recording. These are diagnostic work counts, not a
physical execution-cost or end-to-end developmental-cost measurement.
No benchmark clocks are invoked by the experiment. Reservation timestamps
establish local recorded chronology, not external time or host attestation.
Exclusive local records prevent this runner overwriting a reserved cell;
they do not establish a global no-retry guarantee under deleted/alternate stores.

Replay only `opcode_audit_v2.py` under the recorded CPython 3.13.12 with
`-I -B`; it rechecks evidence without candidate invocation. Running
`opcode_revival_v1.py --run` again is refused by existing reservations.
Native disassembly replay under another Python version is explicitly unsupported.

The 16 portable evidence/mutation tests pass normally and under optimization;
static replay was also checked after relocation. See [V2 replay correction](STATIC_REPLAY_V2.md).
