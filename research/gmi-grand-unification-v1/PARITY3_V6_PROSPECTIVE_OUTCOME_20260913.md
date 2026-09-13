# Parity-3 V6 execution — the prospective 3.13 claim, and what the margins show

Date: 2026-09-13. Registration: `NN_NONNN_POINT_PARITY3_PREREG_V6.json`.
Harness: `nn_nonnn_point_parity3_experiment_v6.py`.
Adjudication: `NN_NONNN_POINT_PARITY3_CROSS_ENVELOPE_V6.json` over all six
frozen portable packets.

## 1. The registered claims, and their outcomes

| Claim | Status at freeze | Outcome |
|---|---|---|
| P1 — the gate passes on CPython 3.13 with priming | already settled by self-test | **held**; `priming_was_required` is `true` on 3.13 and `false` on 3.11 and 3.12 |
| P3 — 3.13 exact counts are 72 / 128 / 288 / 440 in the same order | already settled by static disassembly | **held** exactly |
| P2 — the 3.13 terminal is `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` and agrees with 3.11 and 3.12 | **unmeasured** | **held** |

P2 was the only genuinely prospective claim in the registration. It was
registered and merged before any CPython 3.13 timing existed, and it held.
That is one narrow prospective confirmation on one host, not the independent
prospective replication the audit still lists as open.

## 2. All six portable packets

| Instrument | Interpreter | Terminal | Frontier |
|---|---|---|---|
| V5 | 3.11.15 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` | `X_XOR2_V1` |
| V5 | 3.12.3 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` | `X_XOR2_V1` |
| V5 | 3.13.12 | `INVALID_RECEIPT_OR_PROTOCOL_VIOLATION` | — (retained) |
| V6 | 3.11.15 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` | `X_XOR2_V1`, `X_LOOKUP8_V3` |
| V6 | 3.12.3 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` | `X_XOR2_V1` |
| V6 | 3.13.12 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` | `X_XOR2_V1` |

Cross-envelope: `STABLE_ACROSS_ENVELOPES__DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE`
over five valid envelopes spanning three interpreter generations and two
instrument versions, with the V5 3.13 refusal retained.
`replication_obligation_discharged` remains `false`.

## 3. Family support is stable; the within-family frontier is not

The adjudication now reports these separately, because the V6 run on 3.11
produced a **two-member** frontier: `X_XOR2_V1` no longer robustly dominates
`X_LOOKUP8_V3` there, because XOR's observed wall envelope widened to
`[10,947,182, 18,296,565]` and overlaps the lookup table's
`[14,494,114, 16,064,526]`.

- `family_support_stable`: **true**, `[["NON_NEURAL"]]` on all five envelopes.
- `within_family_frontier_stable`: **false**, two distinct frontier sets.

Both frontier members are non-neural, so the registered family terminal is
unaffected. But the composition of the frontier is a strictly weaker fact than
the family verdict, and it moves with timing noise. This is the predicted
behaviour, not a surprise: by CL-2 and CL-3 of
`CONTINUOUS_LIFT_BOUNDARY_THEOREM_V1.md` an observed window is not a bound and
cannot certify tightness, so anything that depends on the width of a window is
not stable evidence.

## 4. What the margins actually support

| Instrument | Interpreter | Wall margin, DNF min / XOR max | Opcode ratio, DNF / XOR |
|---|---|---:|---:|
| V5 | 3.11.15 | 4.26x | 5.82x |
| V5 | 3.12.3 | 3.92x | 5.36x |
| V6 | 3.11.15 | 2.98x | 5.82x |
| V6 | 3.12.3 | 4.05x | 5.36x |
| V6 | 3.13.12 | 2.92x | 6.11x |

The exact coordinate is reproducible: the opcode ratio depends only on the
interpreter, and both V5 and V6 agree exactly on it for each interpreter.

The timing margin does not behave that way. It varies between **2.92x and
4.26x**, and the two runs of CPython 3.11 differ by more (4.26x against 2.98x)
than any two interpreters differ from each other. **No interpreter trend is
supported by this data.** In particular the 3.13 margin of 2.92x is not
evidence that the newer interpreter narrows the gap, because the 3.11 repeat
lands at 2.98x. Anyone reading a trend out of these five numbers would be
reading run-to-run variation on a shared four-core container.

What survives is the qualitative separation: on every valid envelope the
neural candidates' observed lower endpoints are above the cheapest non-neural
candidate's observed upper endpoint by a factor of at least 2.9, and the exact
opcode gap is at least 5.3x.

## 5. What the instrument repair is worth

V6's priming closes a real defect and extends the validated interpreter scope
from two generations to three. The repair is visible rather than absorbed: on
3.13 each discarded priming witness carries exactly one empty frame, and
`priming_was_required_on_this_interpreter` records that it mattered. On 3.11
and 3.12 priming changes nothing and the flag says so.

The defect was worth catching for a reason beyond coverage. On 3.13 an
unvalidated counter would have credited whichever candidate was traced first
with a complete count and undercounted every other candidate by one frame out
of eight, a 12.5% relative error applied selectively by measurement order. On
this instrument the first-traced candidate is `N_THRESHOLD_DNF4_V1`, the most
expensive one, so the error would have flattered the neural family. The V2
per-frame and forward/reverse checks are what made that unavailable.

## 6. What remains open, unchanged

- **Cross-host replication.** All six packets come from one container. Three
  interpreter generations on one machine is not independent hardware.
  `laptop-billy`, `old` and `lunarc` still have no packets;
  `parity3_v5_runners/` is the entry point.
- **Candidate-universe coverage.** Four registered candidates are a candidate
  list, not a proved structural cover, so by
  `CANDIDATE_UNIVERSE_COVERAGE_CORRECTION_V1.md` the reading stays
  `ROBUST_WITHIN_COVERED_CLASSES_WITH_OPEN_RESIDUE`. Nothing here excludes an
  unbuilt neural realization cheaper than `X_XOR2_V1`.
- **Timing coordinates are not bounds**, as section 3 and 4 make concrete.
- **Development and search costs remain excluded.**
- **One prospective claim is not a prospective programme.** P2 concerned a
  single interpreter on a single host, with P1 and P3 already settled before
  the freeze. The audit's independent-prospective-replication obligation is
  untouched.

Terminal for this execution set:
`PARITY3_V6_PROSPECTIVE_CLAIM_HELD_SINGLE_HOST_THREE_INTERPRETERS`.
