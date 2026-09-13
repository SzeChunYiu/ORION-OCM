# Parity-3 V1 evidence custody and V2 instrument repair

V1 was executed. Its two historical hosted packets both report
`UNDECIDED_FROM_CURRENT_EVIDENCE`, winner `NONE`, and
`prospective_prediction_passed: false`. These outcomes remain unchanged. Their
opcode coordinate has a confirmed instrumentation defect, so neither packet can
support a repaired family verdict. V2 is a new instrument-repair experiment after
reading V1 outcomes, not an independent prospective prediction.

## Observed evidence

| Hosted execution | Frozen run head | Actual tested SHA | Artifact |
| --- | --- | --- | --- |
| [Main push 34721365666](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34721365666), 2026-09-12 | `c3fd59052edfbed6d657930c4ca70d68ac4234d2` | `c3fd59052edfbed6d657930c4ca70d68ac4234d2` | [10306253311](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34721365666/artifacts/10306253311) |
| [PR run 34721354946](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34721354946), 2026-09-12 | `d889b96b61befd15714d0adeda8fa6ba30dbe4c0` | `2f1da417caf756e4a9af789727ad68394fc01862` | [10306342301](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34721354946/artifacts/10306342301) |

Both packets identify CPython 3.12.14 and harness SHA256
`5e7b9c12e4aa44e47963f67a8608c88d2cf1f77816b879e9edfa54cba2511ee3`.
Both candidates pass 8/8 exact capability, and the constant-zero null passes 4/8.
Each run contains 31 measured blocks per candidate, with 160000 calls per block.
The reported opcode totals are neural **0** and XOR **88** in both runs.

The two `NN_NONNN_POINT_PARITY3_HOSTED_*_RESULT_V1.json` files preserve the exact
JSON printed in hosted job stdout, removing only timestamp prefixes and retaining
one final newline. `NN_NONNN_POINT_PARITY3_HOSTED_PROVENANCE_V1.json` preserves the
timestamped excerpts, source job URLs, tested SHAs, hashes and observed artifact
metadata. Artifact ZIP digests are reported by GitHub; ZIP bytes were not downloaded
or independently hashed. Historical packets are classified
`EXECUTED_WITH_PROTOCOL_DEFECT`. The original preregistration's frozen
`PREREGISTERED_NOT_EXECUTED` field describes its pre-execution snapshot, not the
current absence of measured outcomes.

## Exact defect and RED evidence

In `nn_nonnn_point_parity3_experiment_v1.py`, `count_candidate_opcodes` calls
`sys.settrace` before setting any frame's `f_trace_opcodes`. The target frame flag
is enabled only in the subsequent call event. [The CPython 3.12 documentation](https://docs.python.org/3.12/library/sys.html#sys.settrace)
requires a frame to request opcode events before tracing is enabled in this
version; see also [CPython issue 114480](https://github.com/python/cpython/issues/114480).

Fresh CPython 3.12.14 opcode-only microprocesses reproduce:

| Call order | First count | Second count |
| --- | --- | --- |
| Neural, XOR | 0 | 88 |
| XOR, neural | 0 | 472 |

The defect follows measurement order rather than candidate identity. No V1 timing
rerun was used. A positive-count expectation fails on the original first call.
The V1 self-test previously verified capability and schedule but never checked
whether the opcode instrument emitted events.

## Additive V2 repair

`nn_nonnn_point_parity3_experiment_v2.py` prearms its current frame before
`sys.settrace`, restores tracing state, and refuses an already active tracer. For
each of the eight candidate calls it checks the complete expected instruction
offset sequence and exact return value. The validator is deliberately restricted
to these straight-line candidates: it rejects jumps and generators. CPython 3.12
`RESUME` is not a trace opcode event, and inline `CACHE` entries are excluded.
Missing, reordered, extra, boolean or partial event witnesses fail validation.
Positive totals and identical forward/reverse order witnesses are required.

Any instrumentation failure produces `INVALID_RECEIPT_OR_PROTOCOL_VIOLATION`,
winner `NONE`, and no protected timed block. The corrected opcode diagnostics are
neural 472 and XOR 88 in either order. This is instrument validation only; it does
not supply a V2 timed comparison or retroactively change V1's result.

The candidates, capability gate, three resource coordinates, observed-envelope
semantics, 5000-sweep warmup, 31 blocks, 20000 sweeps per block, alternating order
and Pareto selection rule remain identical. Candidate code equality is checked
as Python syntax trees. V2 records `independent_prospective_prediction: false`
and a `registered_repair_expectation`; it does not re-label V1's failed prediction.

The V1 workflow is retired: its automatic triggers are removed and its remaining
manual job is permanently skipped, preventing the old wildcard path filter from
rerunning V1 when evidence or V2 files are added. The separate V2 workflow runs
timing only on a main commit affecting its own harness, preregistration or workflow.
The first such commit freezes V2 before the hosted measurement. Later instrument
changes after reading V2 outcomes require a new version. V2 packets bind both
harness and preregistration hashes and the actual GitHub SHA.

## Validation and remaining scope

The focused standard-library unittest suite passes **14 methods** normally and
**14 methods** under `python -O`, including
fresh-process first-call/order tests, incomplete-trace attacks, trace cleanup,
foreign-tracer refusal, failure before timing, optimized-Python self-test,
unchanged candidate/schedule checks, and byte-exact hosted-log custody checks.
Full research-directory unittest discovery passes **163 methods** on base
`2d65cb11d7f4880ff8f3a4fc41511d2f2e626814` with this additive iteration.
No protected V1 or V2 timing was executed locally while preparing this repair.

V2's hosted timing outcome is unavailable at this commit's pre-execution freeze.
A successful future outcome remains limited to these two preconstructed candidate
functions, this interpreter/runner execution and finite observed block envelopes.
Candidate expansion, population inference, cross-run generalization and a
universal neural/non-neural preference remain unproved. This repair closes a
specific measurement-integrity gap, not the Grand GMI research program.
