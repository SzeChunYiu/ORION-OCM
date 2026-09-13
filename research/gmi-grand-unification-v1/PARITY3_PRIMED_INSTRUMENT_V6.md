# Parity-3 primed instrument — frozen V6, not executed

Date: 2026-09-13. Status: **PREREGISTERED, NOT EXECUTED**.
Registration: `NN_NONNN_POINT_PARITY3_PREREG_V6.json`.
Harness: `nn_nonnn_point_parity3_experiment_v6.py`.
Parents: `nn_nonnn_point_parity3_experiment_v5.py`, `..._v4.py`.

## 1. The defect V5 found

The V5 execution refused CPython 3.13.12 at the instrumentation gate. The
retained diagnostics were specific: the first candidate traced in a process had
a complete witness and every later candidate lost exactly its first frame.

Isolating it further gives a sharper rule. On CPython 3.13.12, with four
never-before-traced code objects:

| Trace | Witness |
|---|---|
| first ever, per code object | `[0, 9, 9, 9, 9, 9, 9, 9]` |
| immediately again, same code object | `[9, 9, 9, 9, 9, 9, 9, 9]` |

So it is not "the first session in the process". It is **the first-ever trace
of each code object** that loses its first frame. CPython 3.12.3 shows no such
effect. V5's earlier reading, that the prearm works only for the first session
per process, was an artifact of the candidates being traced in a fixed order.

## 2. The repair, and why it does not weaken the gate

V6 runs one **discarded priming trace** per candidate before the recorded
witness. That is the whole change.

- Per-frame validation is untouched. The recorded witness must still equal the
  expected instruction sequence for every one of the eight frames, forward and
  reverse. If priming ever stops working, the packet is still refused.
- Priming is harmless where the defect never existed, and each packet records
  the priming witness diagnostics plus `priming_was_required_on_this_interpreter`,
  so the effect stays visible rather than being silently absorbed.
- Timing happens after the registered warmup and is unaffected.
- Candidate identity is now bound against **both** earlier portable harnesses,
  so V6 candidates are proved byte-identical to V5's and V4's.

Everything else is unchanged and asserted directly against the V5 registration
by `test_parity3_primed_replication_v6.py`: the candidates, the schedule, the
resource coordinates, the development-cost exclusion and the selection rule.
The same test also checks that V6, V5 and V4 adjudicate an identical box set
identically.

## 3. Instrument status at freeze time

The self-test times nothing, and was run on all three interpreters before this
freeze:

| Interpreter | Gate | Priming required | Recorded witnesses | Opcode counts (XOR / lookup / sum / DNF) |
|---|---|---|---|---|
| CPython 3.11.15 | pass | no | 8/8 complete | 88 / 136 / 344 / 512 |
| CPython 3.12.3 | pass | no | 8/8 complete | 88 / 136 / 312 / 472 |
| CPython 3.13.12 | pass | **yes** | 8/8 complete | 72 / 128 / 288 / 440 |

On 3.13 each priming witness shows exactly one empty frame, which is the defect
being absorbed where it can be seen.

## 4. What is prospective and what is not

The registration separates the three registered claims, because they do not
have the same status:

- **P1** — the gate passes on 3.13 with priming. Already confirmed at freeze
  time by the self-test above. Retained as a record of the reasoning.
- **P3** — the 3.13 exact counts are 72, 128, 288, 440 in the same
  cheapest-to-costliest order. Also already confirmed, from static
  disassembly and the self-test. Requires no timing.
- **P2** — the 3.13 terminal is `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` and
  agrees with 3.11 and 3.12. **Genuinely prospective.** No timing measurement
  has ever been executed on CPython 3.13 under any registration, so its wall
  and process envelopes, and therefore its verdict, are unmeasured at freeze
  time.

The audit has repeatedly recorded "not independent prospective replication" as
a limitation of this evidence line. P2 is a narrow but real prospective claim:
it is registered, falsifiable, and unmeasured. Its falsifier is a surviving
neural candidate, an abstention, or disagreement between validating envelopes.

## 5. Boundary

This freeze contains **no timing measurement**. It does not touch cross-host
replication: every envelope executed so far shares one container, and
`laptop-billy`, `old` and `lunarc` still have no packets. It does not convert a
four-candidate point verdict into a family verdict, and it does not make an
observed timing envelope into a bound. The V5 packets, including the retained
3.13 refusal, are unchanged.
