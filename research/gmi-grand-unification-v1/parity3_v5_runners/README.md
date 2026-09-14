# Parity-3 replication runners

These are the two entry points for the envelopes that are not reachable from
CI. Both select the harness by version and **default to V6**, which is the one
whose opcode instrument is repaired for CPython 3.13; V5 refuses that
interpreter by design. The directory keeps its original name so that existing
references stay valid.

| Target | Command |
|---|---|
| laptop registered as `billy` | `./run_local.sh laptop-billy` |
| machine registered as `old` | `./run_local.sh old` |
| LUNARC compute node | `sbatch -A <project> run_lunarc.sbatch` |

Pick the interpreter explicitly when a host has several, for example
`./run_local.sh laptop-billy /usr/bin/python3.12`. Each interpreter version is
its own envelope and gets its own packet.

Pick the harness explicitly with a third argument, or with
`PARITY3_HARNESS_VERSION`, which is also how the LUNARC script takes it:

```sh
./run_local.sh laptop-billy /usr/bin/python3.12 v5
PARITY3_HARNESS_VERSION=v5 sbatch -A <project> run_lunarc.sbatch
```

The packet name carries the harness version, so a V5 and a V6 run on the same
host and interpreter are separate envelopes and neither can overwrite the
other. An unknown version fails immediately and lists what is available,
instead of running the wrong harness.

## What the run does

1. Validates the instrument on that interpreter with `--self-test`, before any
   timing. A complete validated opcode witness is a hard gate.
2. Runs the frozen schedule: 5000 warmup sweeps, then 32 timed blocks of 20000
   sweeps over all 8 inputs, per candidate, in a balanced rotating order with
   garbage collection disabled.
3. Writes one packet named after the host label and interpreter.

## Rules that matter

- **One packet per envelope.** The harness opens the output with `x` mode and
  refuses to overwrite, so a second attempt fails rather than replacing the
  first outcome.
- **Keep invalid packets.** Under V5 on CPython 3.13 the opcode instrument is
  expected to refuse, because the first traced frame reports no opcode events.
  That refusal is a recorded result, not a failed run to retry until it passes —
  and switching to V6 to make it pass is a *different envelope*, not a retry of
  the same one. V6 primes the tracer and is expected to complete on 3.13.
- **Do not edit the harness or the registration to make a run succeed.** A
  changed source needs a new version.
- Prefer an otherwise idle machine. The wall and process envelopes describe
  whatever else the CPU was doing.

## After the run

Commit the packet, then adjudicate all envelopes together:

```
python3 ../parity3_cross_envelope_adjudicate_v5.py \
    ../NN_NONNN_POINT_PARITY3_RESULT_V[56]_*.json
```

The adjudicator accepts both the V5 and V6 packet schemas and reports family
support and the within-family frontier separately.

The adjudicator refuses to compare packets whose candidate sources are not
byte-identical, reports each envelope's own terminal, and reports whether the
terminals agree. It never pools timing across envelopes.
