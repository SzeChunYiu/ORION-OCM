# One E0 phase diagnostic: observed result

The unfinished interval is the invocation of command 7, `check-synth`.
Explicit grammar parsing, declaration, and constraint setup all completed before
that interval. This narrows the location of the timeout; it does not identify the
underlying solver cause.

## Bound execution

- Manifest: `d4e568d5a50ca45fe1fda3c8b2c3bc1c482c5a37e2c62ef82e75bbade42ffbb3`.
- Frozen source/review commit: `9f02b7d1a196e42d3f46f5d7b325d88c328b6b3d`.
- All 77 source, request, environment and manifest bindings verify.
- [Prospective registration](https://github.com/SzeChunYiu/ORION-OCM/issues/62#issuecomment-5561823393) was published
  at 20:04:46 UTC, before the recorded launch at 20:05:03.233509 UTC.
- The actual root launch matches the frozen command. Its capture wrapper exited
  0; the assigned native E0 process exited **124** under GNU timeout.
- The eight-file [raw seal](run-v1/seal.json) verifies. Its digest is
  `a180552ebeab4986f479ca0dcf3cad496e69bff859cc22729b2448e32a330f12`.

## Observation and cost

The 58 flushed events have one worker PID and ordered clock/CPU readings.
Commands 0–6 completed; command 7 parsed and reached `invoke.before`.
No `invoke.after(7)`, candidate, or completed-worker metrics were returned.

| Quantity | Observed value | Scope |
|---|---:|---|
| Capture wall time | 20.013979705 s | Native envelope through wait/cleanup |
| Main entry to final checkpoint | 0.022607983 s | Instrumented worker |
| Process CPU at final checkpoint | 0.049339652 s | Partial process lifetime |
| Peak RSS at final checkpoint | 44,724 KiB | Partial high-water mark |

The final checkpoint precedes symbol-manager retrieval and `command.invoke()`
for `check-synth`; the trace cannot distinguish work inside that interval.
The external 20-second envelope expired without a response. The trace does not
explain the native 5000-ms option's internal behavior. Complete timed-out worker
CPU/RSS and process-tree costs remain unknown. Instrumentation adds work, so
these observations do not establish a speed comparison.

## Cleanup and interpretation

Wrapper PID 1774167 and worker PID 1774168 are absent from
`/proc`. A full `ps` inventory, validated by finding the audit process itself,
contains no matching PID, process group or session; a zero-signal process-group
probe also reports absence. This is a current-state cleanup check.

No semantic checker, B trial, induction, retry, or source modification occurred
during this independent audit. The diagnostic does not establish a valid
candidate, learned-method consumption, benefit, or an internal B-route cause.
Any follow-up that instruments or changes synthesis internals requires a new
source-bound registration; grammar parsing is not the observed stalled stage.

The [independent audit record](INDEPENDENT_RECORD_AUDIT.json) binds these findings
to the preserved [raw receipt](run-v1/receipt.json) and
[phase stream](run-v1/E0/stderr).
