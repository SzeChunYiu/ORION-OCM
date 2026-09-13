# Static V6 contract and scientific scope

## Authority and matched parents

The authority is the exact V6 harness, V6 registration, V5/V4 source parents and
three packets from [commit 243c2a12](https://github.com/SzeChunYiu/ORION-OCM/tree/243c2a12c0c385497b6ee43d5c60bfe8ebda270d/research/gmi-grand-unification-v1).
Their unmodified bytes are in `raw/frozen/`. Candidate bodies are bound by exact
source-segment digests across all three harness generations.

The mature parent is the V5 custody unit's independent full packet validator.
Its metadata/schema/scope checks are adapted here to V6. The strict JSON helper
and `resource_evidence_v6.py` are copied **unchanged**, with original hashes.
The latter independently derives native straight-line opcode offsets, validates
all measured traces, reconstructs block envelopes and derives the finite frontier.
The V6 harness's own measurement or adjudication functions are never called.

Closure's earlier partial V6 audit, three outputs and original bindings survive
unchanged in `raw/partial/`. Shared reconstructed fields must agree with them.
The new unit adds full schema, nested metadata, prerequisite, scope and priming
checks; passing the old partial audit alone did not discharge these obligations.
The old script contains historical absolute paths and is retained, not executed.

## Accepted records and exact-runtime contract

Only the three hash-bound valid V6 packets are archival entry inputs.
The pure content validator also accepts altered copies for adverse tests.
It checks the exact top-level and nested schemas, source/registration/AST
identities, parent availability and identity, all capability and null outputs,
registered universe, metadata literals, and Boolean prerequisite flags.

A matching **CPython major/minor/patch release** is required to reconstruct
version-dependent native AST and bytecode offsets. The current audit executable's
digest is recorded. This is a static comparison under that binary, not proof that
the historical measurement used an identical build or executable.
Absent, failed-to-start or mismatching interpreters are UNVERIFIABLE.
Contradictory evidence is REJECTED. Only three successful workers yield an
all-three pass. Unsupported refusal packets cannot acquire a valid-measurement
verdict through this unit.

The retained host/runtime/scheduler metadata have exact schemas and must be
internally compatible with the frozen record. Slurm context requires a nonempty
recorded job ID; a nonempty job ID requires Slurm or higher-precedence GitHub
context. GitHub context does not require its optional fields to be present.
These fields are self-reports. Ambient
GitHub, Slurm or CI variables on the audit host do not replace recorded metadata.
Registration status and expectation fields are checked as frozen literals.
This does not authenticate temporal priority, the expectation's scientific truth,
or an independent prospective prediction.

## Full measured-frame and resource reconstruction

The resource helper derives every expected opcode offset from the source-compiled
candidate definition without calling it. For both recorded candidate orders it
checks all 8 inputs for all 4 candidates: exact outputs, ordered offsets, counts,
and return flags. All frame diagnostics and duplicated opcode maps must agree.
Boolean/integer substitutions, missing returns, changed outputs and reordered
events are rejected. Static consistency does not authenticate that an event
stream originated on the reported machine or exclude coherent forgery.

Each candidate must retain all 32 blocks at its prescribed block/order index,
candidate identity and checksum. Wall/process durations must be positive integers.
Every interval endpoint is reconstructed from these blocks. Robust dominance
requires a candidate's upper bound to be no larger than another's lower bound
in every registered coordinate, strictly smaller in at least one. All dominators,
frontier IDs, families, terminal and winner are independently recomputed.
Here the packet's frontier field is the robustly-undominated candidate set,
not a unique point Pareto frontier. For 3.11.15 lookup is possibly, not necessarily,
Pareto-optimal under independent choices inside the observed intervals.

This validates finite **observed** envelopes for four preconstructed candidates.
It does not estimate population confidence, authenticate clock readings, recover
unrecorded warmup costs, charge acquisition/search, or demonstrate lifetime
superiority. Recorded timed calls total 20,480,000 per packet; the static audit
adds zero candidate, priming or timing calls. Static inspection/storage CPU costs
are ordinary verification work, not new candidate resource observations.

## Priming boundary

V6 emits only forward priming diagnostics. It discards forward raw priming
outputs, offsets and return events, and discards the reverse priming summaries.
The three retained records report either eight complete frames or a first empty
frame followed by seven complete frames. We validate these two retained patterns,
their sums, frame counts, Boolean return summary and the aggregate incomplete
flag against native expected event counts.

The field named `priming_was_required_on_this_interpreter` is interpreted only as
the harness's recorded predicate: some forward priming summary reports fewer
than eight complete frames. That name does not establish causal necessity.
Equal event counts cannot establish correct event order or outputs in an absent
trace. No full priming validation, universal version-specific tracing law,
repaired measurement semantics, or historical initial tracing state follows.

## Falsification and no-alarm controls

All three actual packets must pass before adverse results are used. Each undergoes
50 distinct alterations covering outputs/returns/opcodes, schedules and blocks,
durations and boxes, frontier/terminal, source parents, metadata, capability/null,
false prerequisites, scope, and priming contradictions. A separate test guard
fails if candidate or measurement code is entered during the full content census.
Other tests exercise strict JSON, archive tampering, unknown runtimes, failed
workers, ambient CI variables and relocation. Normal and optimized execution
must produce the same receipt, demonstrating that Python assertions are not
the enforcement mechanism.
