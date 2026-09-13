# Parity-3 portable replication — frozen V5, not executed

Date: 2026-09-13. Status: **PREREGISTERED, NOT EXECUTED**.
Registration: `NN_NONNN_POINT_PARITY3_PREREG_V5.json`.
Harness: `nn_nonnn_point_parity3_experiment_v5.py`.
Parent: `NN_NONNN_POINT_PARITY3_PREREG_V4.json`.

## 1. The defect this repairs

`RECURSIVE_GAP_AUDIT_20260913.md` carries independent replication as a standing
obligation, and the candidate-universe row requires "replication across tasks
and substrates". The instrument that produces the evidence cannot do it.

V1 through V4 hard-require hosted execution. From
`nn_nonnn_point_parity3_experiment_v4.py`:

```
if os.getenv("GITHUB_ACTIONS") != "true":
    failures.append("not_github_actions_hosted_execution")
if os.getenv("RUNNER_OS") != "Linux":
    failures.append("runner_os_not_linux")
for key, expected in (("GITHUB_REF", "refs/heads/main"),
                      ("GITHUB_EVENT_NAME", "push"), ("GITHUB_RUN_ATTEMPT", "1")):
```

A failure here yields `INVALID_RECEIPT_OR_PROTOCOL_VIOLATION` with no timing.
So on a laptop, a shared server or a compute node, the registered instrument
**cannot produce a valid packet at all**, and neither can a re-run on the same
hosted runner: the gate admits only a first attempt of a push to `main`. The
replication obligation was therefore unsatisfiable by construction, not merely
unsatisfied.

That gate was a reasonable custody choice for a single hosted point result. It
is the wrong contract for a replication.

A second, quieter defect blocks cross-interpreter comparison. V4 identifies
candidates by `ast_sha256`, computed from `ast.dump`, whose output changes
between CPython versions. Two runs of byte-identical candidate source on
different interpreters therefore disagree about candidate identity, and V4
rejects the packet as "registered candidate source changed".

## 2. What V5 changes, and what it must not

Changed, and only this:

- the hosted gate becomes a **recorded** host and interpreter envelope: host
  label, execution surface, interpreter version, platform, CPU, and SLURM job
  identity when present;
- candidate identity moves to the **exact source segment bytes**, which are
  interpreter independent. Each packet also records its local AST hash and
  proves byte-identity against the V4 harness;
- witness diagnostics are recorded per candidate, so an instrument refusal is
  explainable rather than just a failure string.

Unchanged, and asserted by the registration and by
`test_parity3_portable_replication_v5.py`:

- all four candidate bodies, byte for byte, verified against the V4 harness;
- the schedule: 5000 warmup sweeps, 32 timed blocks, 20000 sweeps per block,
  8 inputs per sweep, and the same rotating and reversing candidate order;
- the three registered resource coordinates;
- the robust-domination selection rule and its abstention on a mixed frontier;
- the development-cost exclusion.

What stays a hard gate is what protects the measurement, not what names the
machine: a CPython interpreter, exact capability on all eight inputs, candidate
sources byte-identical to the parent harness, and a complete validated opcode
witness for every candidate — forward and reverse — before any timing.

## 3. Interpreter scope is an empirical question, and was probed first

Before this freeze, the opcode-tracing prearm was probed outside the harness on
three interpreters. This is disclosed in the registration under
`prior_diagnostic_knowledge`, because it is knowledge held before freezing.

| Interpreter | Complete witness | Events per call, XOR candidate |
|---|---|---|
| CPython 3.11.15 | yes | 11 |
| CPython 3.12.3 | yes | 11 |
| CPython 3.13.12 | **no** | 9 expected, first frame reports none |

On 3.13 the first traced frame produces no opcode events, so a naive counter
would report `9 * 7 = 63` instead of `9 * 8 = 72`. That is precisely the V1
defect — tracing armed too late — reappearing on a newer interpreter. The V2
instrumentation repair catches it: `validate_opcode_witness` requires each
frame's offsets to equal the expected sequence, so 3.13 is expected to yield an
invalid packet rather than a wrong number. **That packet must be kept.** An
instrument refusal is a recorded result.

The exact opcode counts also differ between interpreters where the instrument
does work, so the registration treats the coordinate as envelope-relative and
the cross-envelope adjudicator reports the counts per envelope instead of
asserting one registered value.

## 4. Replication is a question about agreement

`parity3_cross_envelope_adjudicate_v5.py` reads frozen packets and:

- refuses to compare packets whose candidate sources are not byte-identical;
- reports each envelope's own terminal, and each invalid envelope's gate
  failures;
- classifies agreement as `SINGLE_ENVELOPE_NO_REPLICATION`,
  `STABLE_ACROSS_ENVELOPES__<terminal>`, `UNSTABLE_ACROSS_ENVELOPES` or
  `NO_VALID_ENVELOPE`;
- reports the opcode counts and their cheapest-to-costliest ordering per
  envelope, so interpreter dependence is visible rather than hidden;
- never pools or averages a resource envelope across envelopes, and never
  upgrades a per-envelope terminal into a substrate-level claim;
- carries the named outstanding hosts forward, and reports
  `replication_obligation_discharged: false` unconditionally.

## 5. Outstanding named hosts

The registration names three envelopes that this freeze does **not** execute:
`laptop-billy`, `old` and `lunarc`. They are not reachable from the session
that produced this freeze, which has no SSH client, no credentials for them and
HTTPS-only egress. `parity3_v5_runners/` provides the two entry points —
`run_local.sh <host-label>` and `run_lunarc.sbatch` for SLURM — so that each of
those envelopes can be executed by whoever has access, with the packet landing
in the registered schema and name.

Until those packets exist and are frozen, the replication obligation stays
open, and this document does not claim otherwise.

## 6. Boundary

This freeze contains **no timing measurement on any envelope**. It adds a
portable instrument, its registration, a cross-envelope adjudicator, runner
entry points and their regression tests. Nothing here is a family verdict, and
the V1, V2 and V4 packets, registrations and workflows are unchanged.

The epistemic status of the registered expectation is outcome-informed: the V1,
V2 and V4 outcomes were read, and the interpreter probe above was run, before
freezing. It is not an independent prospective prediction.
