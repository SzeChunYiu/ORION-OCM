# Parity-3 V5 cross-envelope execution — first frozen outcomes

Date: 2026-09-13. Registration: `NN_NONNN_POINT_PARITY3_PREREG_V5.json`.
Harness: `nn_nonnn_point_parity3_experiment_v5.py`.
Adjudication: `NN_NONNN_POINT_PARITY3_CROSS_ENVELOPE_V5.json`.

This is the first execution under the portable registration. Three envelopes
were run on one host, each once, and every outcome is retained including the
refusal.

## 1. Envelopes executed

The host is the ephemeral container of the session that produced this packet
set, registered as `claude-code-remote-container`: Linux 6.18.44, x86_64,
4 CPUs, Intel Xeon at 2.10 GHz, execution context `INTERACTIVE_OR_LOCAL`.

| Packet | Interpreter | Terminal |
|---|---|---|
| `..._CPython3.11.15.json` | CPython 3.11.15 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` |
| `..._CPython3.12.3.json` | CPython 3.12.3 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` |
| `..._CPython3.13.12.json` | CPython 3.13.12 | `INVALID_RECEIPT_OR_PROTOCOL_VIOLATION` |

Cross-envelope stability:
`STABLE_ACROSS_ENVELOPES__DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE`
over the two valid envelopes, with one invalid envelope retained.

## 2. Measured resource boxes

CPython 3.12.3, wall nanoseconds per block of 160,000 calls:

| Candidate | Family | Opcodes | Wall min | Wall max |
|---|---|---:|---:|---:|
| `X_XOR2_V1` | NON_NEURAL | 88 | 10,568,687 | 12,872,289 |
| `X_LOOKUP8_V3` | NON_NEURAL | 136 | 13,979,829 | 14,447,605 |
| `N_SUM_THRESHOLD3_V3` | NEURAL | 312 | 37,721,833 | 40,624,671 |
| `N_THRESHOLD_DNF4_V1` | NEURAL | 472 | 50,492,093 | 53,525,199 |

CPython 3.11.15:

| Candidate | Opcodes | Wall min | Wall max |
|---|---:|---:|---:|
| `X_XOR2_V1` | 88 | 10,914,736 | 12,452,881 |
| `X_LOOKUP8_V3` | 136 | 14,383,364 | 20,387,758 |
| `N_SUM_THRESHOLD3_V3` | 344 | 37,626,507 | 41,642,605 |
| `N_THRESHOLD_DNF4_V1` | 512 | 53,046,315 | 57,195,530 |

On both envelopes the observed boxes are disjoint in the order shown, so
`X_XOR2_V1` robustly dominates all three competitors and is the sole frontier
member. It dominates the other non-neural candidate too; the verdict is not a
tie inside the non-neural family.

## 3. What replicated

**The registered exact coordinate reproduced on a different machine.** V2 and
V4 registered 472 opcodes for `N_THRESHOLD_DNF4_V1` and 88 for `X_XOR2_V1` on a
GitHub-hosted runner. Both numbers reproduce exactly here on CPython 3.12
under a validated complete witness, on unrelated hardware. That is an
independent reproduction of the exact resource coordinate, not of the timing.

**Absolute opcode counts are interpreter dependent; their ordering is not.**
Between 3.11 and 3.12 the neural counts move — 512 to 472 and 344 to 312 —
while both non-neural counts are unchanged. The cheapest-to-costliest ordering
is identical on both envelopes:

`X_XOR2_V1 < X_LOOKUP8_V3 < N_SUM_THRESHOLD3_V3 < N_THRESHOLD_DNF4_V1`.

The verdict depends on the ordering, not the absolute values, which is why it
is stable across the two envelopes. The adjudicator reports both facts rather
than asserting a single registered count.

## 4. What refused, and why that is a result

CPython 3.13.12 failed the instrumentation gate with `incomplete or reordered
opcode events`, before any timing. The retained diagnostics are specific:

| Candidate | Expected per call | Frames | Complete | Events per call |
|---|---:|---:|---:|---|
| `N_THRESHOLD_DNF4_V1` | 55 | 8 | 8 | `[55, 55, 55, 55, 55, 55, 55, 55]` |
| `X_XOR2_V1` | 9 | 8 | 7 | `[0, 9, 9, 9, 9, 9, 9, 9]` |
| `N_SUM_THRESHOLD3_V3` | 36 | 8 | 7 | `[0, 36, 36, 36, 36, 36, 36, 36]` |
| `X_LOOKUP8_V3` | 16 | 8 | 7 | `[0, 16, 16, 16, 16, 16, 16, 16]` |

The retained **post-failure diagnostic pass** has eight complete DNF calls
and seven complete calls for each of the other three candidates. In the pinned
V5 source, `run_experiment` first invokes `instrumentation_preflight`; after
that raises, it traces the candidates again to produce these diagnostics.
They therefore do not describe the first trace session in the process. The
failed preflight calls are not retained, and the precise first-use or tracing
mechanism is unresolved by this packet.

Ignoring validation would count DNF at 440/440 expected events, XOR at 63/72,
sum-threshold at 252/288, and lookup at 112/128. That would artificially cheapen
the latter three candidates and disadvantage DNF relative to them. The original
claim that this would advantage DNF reversed the arithmetic. Per-frame and
forward/reverse validation correctly prevents using this incomplete witness
for an opcode comparison. The frozen invalid output remains unchanged.

No 3.13 timing was run and none should be, until the prearm is repaired for
that interpreter. The invalid packet is frozen as it was emitted.

## 5. What this does not establish

**It is not the replication the audit obligation asks for.** Three envelopes
were executed, but all three on **one host**, differing only in interpreter.
`replication_obligation_discharged` is `false` in the adjudication, and the
named hosts `laptop-billy`, `old` and `lunarc` have no packets. Cross-host
replication requires different hardware, not different interpreters on the
same container.

**It is a point verdict over four candidates, not a family verdict.** In the
vocabulary of `CANDIDATE_UNIVERSE_COVERAGE_CORRECTION_V1.md`, four registered
candidates are a candidate list and not a proved structural cover of the
physically legal parity-3 realizations. CU-2 does not apply, so the correct
reading is `ROBUST_WITHIN_COVERED_CLASSES_WITH_OPEN_RESIDUE` with the residue
entirely open. Nothing here excludes an unbuilt neural realization cheaper
than `X_XOR2_V1`.

**The timing coordinates are finite observations.** CLB-2 and CLB-3 of
`CONTINUOUS_LIFT_BOUNDARY_THEOREM_V1.md` distinguish exact attainment,
approximation and certified bounds. A finite sampled minimum is at least the
infimum of the same cost map, but need not strictly exceed it. These 32-block
wall/process envelopes have no independently supplied tightness certificate
or population/transfer guarantee; they do not establish a lower bound on all
executions or transfer to another machine. The opcode coordinate is exact
under its validated witness for the interpreter that produced it.

**Development and search costs remain excluded**, as in V1 to V4. All four
candidates are directly constructed frozen sources, so this says nothing about
what it would cost to find any of them.

**The registered expectation was outcome informed.** V1, V2 and V4 outcomes
were read and the interpreter probe was run before the freeze. The expectation
that a validating envelope would return a non-neural frontier, and that
envelopes would agree, held on both valid envelopes. The expectation that 3.13
would refuse also held. Neither is an independent prospective prediction.

The raw packets record source/preregistration hashes and interpreter envelopes
but lack execution timestamps and run IDs. Their contents alone do not certify
the reported run-once chronology; no actual violation is established here.
The original V5 cross-adjudicator trusts asserted validity fields. Q11 in
`SCIENTIFIC_GAP_QUEUE_V2.md` requires a separately versioned complete evidence
audit before that tool supplies validation authority. Reported observations
and raw packet bytes remain preserved.

## 6. Registered expectation outcome

| Registered element | Outcome |
|---|---|
| frontier contains only NON_NEURAL candidates on a validating envelope | held on 3.11.15 and 3.12.3 |
| per-envelope terminals agree across validating envelopes | held |
| CPython 3.13 fails the instrumentation gate | held, packet retained |
| falsifier: a surviving neural candidate, or disagreeing terminals | not triggered |

Terminal for this execution set:
`PARITY3_V5_CROSS_ENVELOPE_STABLE_NON_NEURAL_SINGLE_HOST`.

The obligation that remains is unchanged in kind: packets from independent
hardware. `parity3_v5_runners/` is the entry point for `laptop-billy`, `old`
and `lunarc`, and until those exist this document claims agreement between
interpreter envelopes on one machine and nothing wider.
