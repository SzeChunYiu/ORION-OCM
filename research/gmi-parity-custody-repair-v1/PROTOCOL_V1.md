# Version-preserving parity execution and evidence contract

## Authority and strongest matched parent

V5 is frozen at main commit 97bbda75ee56d740875a8929e350f26bc11d1e72
(PR #545 head 9f33757e28a29329c9e14660563beb7927f55a6b).
[FROZEN_INPUTS_V1.json](FROZEN_INPUTS_V1.json) binds its instrument, registration,
V4 parent source, original cross-envelope tool and mature V4 static auditor.
None of these files is edited.

The parent implementation is
[verify_parity3_hosted_v4.py](../gmi-grand-unification-v1/verify_parity3_hosted_v4.py).
Its strict JSON parsing, exact capability/trace/block checks, envelope
reconstruction and independent dominance calculation transfer directly.
Its GitHub first-push contract and fixed interpreter do not transfer.
Custody V1 and Cross Audit V6 replace those two assumptions explicitly.

[CPython dis documentation](https://docs.python.org/3.12/library/dis.html)
makes bytecode an implementation detail without cross-release stability.
Thus a recorded full interpreter version must match the static auditor;
for newly reserved attempts the executable hash must also match.
Compilation and disassembly do not execute candidate bodies or timing loops.

## Demonstrated failures

V5 main invokes run_experiment at line 585 before write_packet exclusively
opens the destination at line 565. A preexisting output therefore blocks the
write after the measurement has already run. An exclusive file open protects
old bytes but does not establish first-attempt execution.

The old cross-envelope tool selects valid rows from their terminal labels.
Two synthetic packets with false gates, empty timing tables and unbound
instrument/registration hashes still produce its stable-family terminal.
The [replay](countercontrols_v1.py) replaces the measurement function and
records zero actual measurement invocations. These are code counterexamples,
not empirical architecture outcomes.

## Custody V1

The caller selects one persistent registry for this host before the campaign.
All checkouts must use it; deleting it or selecting another directory defeats
that premise and cannot be certified by a local launcher.

The canonical key hashes the experiment, hashed Linux machine-id, interpreter
implementation and full version. A display-label, executable-path alias,
checkout or execution-surface change does not create another attempt.
Different interpreter versions are different registered envelopes.
This is machine-local uniqueness; machine-id is not independent hardware
attestation and copied/mutated host identities are outside the guarantee.

Atomic directory creation reserves the key before the V5 subprocess can start.
The reservation record binds the frozen source snapshots, correction code,
interpreter executable hash, display label and start time.
Source verification and copying occur after reservation and before execution.
The immutable V5 subprocess receives its own exact three-file source snapshot,
-I -B and a new packet destination; stdout and stderr are preserved separately.
The completion record binds every emitted output and the reservation.
Source/executable drift, launch failure and interruption leave the key reserved.
An incomplete directory is evidence of an unfinished attempt, never permission
to rerun. Empty/partial reservations require explicit custody investigation.

[Path.mkdir semantics](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path.mkdir)
and the underlying filesystem's atomic exclusive creation are the parent
mechanism. Assume a retained registry with coherent exclusive mkdir semantics.
Then two callers of this route with the same canonical identity cannot both
pass reservation: only the caller that creates the previously absent directory
can reach invocation. The collision test substitutes the invocation function
and proves the second launch performs zero invocations and changes no bytes.

Linux execution is enforced before reservation; Mac execution is refused.
No experiment was run while implementing or testing this contract.
An actual run remains an explicit operational action using the CLI.

## Cross Audit V6

For a new attempt, audit_custody_v1.py first checks reservation/completion
bindings, exact snapshot inventory, executable identity and stdout/packet byte
identity. A failed or interrupted process receives its own nonvalid state.

For a complete packet, packet_content_v6.py and resource_evidence_v6.py require:

1. Exact registered candidate identity, source/registration digests, family
   labels, schedule, scope, capability and null-baseline records.
2. All eight exact outputs per candidate; every forward and reverse frame
   equals the independently disassembled straight-line opcode sequence.
3. Every one of 32 blocks per candidate, correct rotation/reversal placement,
   exact checksum and positive integer wall/process durations.
4. Envelopes recomputed from those blocks, complete domination graph,
   frontier, family set, unique-winner field and terminal derived anew.

Strict JSON rejects duplicate keys, nonfinite values and Boolean/integer
substitution in scientific equality checks. A declared terminal cannot repair
missing or contradictory evidence. The V5 refusal schema preserves the
reported instrumentation failure without reconstructing the unrecorded
original failure trace; it yields no family comparison.

The cross tool invokes static audits only. Matching interpreter availability
is checked explicitly. UNVERIFIABLE, rejected, incomplete and refused attempts
are retained separately from complete evidence. A stable terminal means
agreement among the validated recorded envelopes; it does not mean every
attempt passed or that a general replication obligation is discharged.

## Historical evidence and provenance limits

PR #547 subsequently supplied three V5 packets at
2ea3a617283bbe0f854f11df2ec4afcd57cbd848. Exact bytes and hashes are imported
under raw/. audit_imported_v1.py admits only those hash-bound records.
It checks complete content on matching exact interpreter versions.
These packets predate Custody V1, so their first-attempt provenance remains
unverified by this correction. A successful content check does not fabricate
a retrospective reservation or independent host attestation.

The 3.11.15 and 3.12.3 packets yield XOR-only frontiers after reconstruction.
The 3.13.12 packet remains an instrument refusal. No timing is rerun.
See [the validation readout](VALIDATION_READOUT_V1.md) for precise evidence.

Hash consistency protects the declared bytes; it cannot establish honesty of
a host that fabricates a self-consistent packet and custody history.
The external trust boundary remains the retained repository/source records
and their actual collection. Historical interpreter build hashes were not
recorded by V5; matching release and trace checks cannot recover that field.

## Scientific and cost boundary

Candidate construction, acquisition and custody overhead remain excluded by
the frozen deployment-only registration. No lifecycle advantage is inferred.
The wrapper's timestamps describe custody stages; they are not added as
new candidate resource coordinates or represented as full acquisition costs.

Agreement concerns the same four hand-constructed parity-3 implementations,
their observed deployment envelopes and interpreter-relative opcode counts.
It does not prove a population timing interval, neural/non-neural universe
coverage, causal interpreter effects, unseen-host performance or intelligence.
The outcome-informed expectation and the invalid historical packet remain.
