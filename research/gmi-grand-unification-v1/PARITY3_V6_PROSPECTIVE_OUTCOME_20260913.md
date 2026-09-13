# Parity-3 V6: recorded outcomes and corrected interpretation

Date: 2026-09-13. Registration: `NN_NONNN_POINT_PARITY3_PREREG_V6.json`.
Harness: `nn_nonnn_point_parity3_experiment_v6.py`.
Raw authority: PR #550, merge `243c2a12c0c385497b6ee43d5c60bfe8ebda270d`.
The three V6 result packets and `NN_NONNN_POINT_PARITY3_CROSS_ENVELOPE_V6.json`
remain byte-identical to that commit. This readout corrects its interpretation.

## 1. Registered claims and recorded outcomes

| Claim | Status at freeze | Recorded outcome |
|---|---|---|
| P1: primed gate passes on CPython 3.13 | prior diagnostic knowledge | held in the full recorded preflight; see self-test limitation below |
| P3: 3.13 opcode counts, XOR / lookup / sum / DNF | already known from static disassembly | 72 / 128 / 288 / 440 |
| P2: 3.13 returns the non-neural terminal, agreeing with 3.11 and 3.12 | declared unmeasured at freeze | held at the registered four-candidate observed-box scope |

P2 is the registration's only open outcome prediction. The registration merged
before these recorded timing packets. That chronology and the disclosed prior
knowledge support a narrow prospective reading; the packets do not independently
authenticate a global first-attempt history. This is one host, and the registration
explicitly disclaims independent prospective replication.

## 2. Six portable packets

| Instrument | Interpreter | Recorded terminal | Candidates not robustly dominated |
|---|---|---|---|
| V5 | 3.11.15 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` | `X_XOR2_V1` |
| V5 | 3.12.3 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` | `X_XOR2_V1` |
| V5 | 3.13.12 | `INVALID_RECEIPT_OR_PROTOCOL_VIOLATION` | none reported; refusal retained |
| V6 | 3.11.15 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` | `X_XOR2_V1`, `X_LOOKUP8_V3` |
| V6 | 3.12.3 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` | `X_XOR2_V1` |
| V6 | 3.13.12 | `DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE` | `X_XOR2_V1` |

The preserved aggregator reports
`STABLE_ACROSS_ENVELOPES__DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE`,
`family_support_stable: true`, `within_family_frontier_stable: false`, and
`replication_obligation_discharged: false`. Here stability means agreement of
these recorded classifications. The five valid packets span three interpreter
versions and two instrument versions on the same reported container.

## 3. Box overlap does not certify coexistence

On V6/3.11, XOR's observed wall interval `[10947182,18296565]` overlaps lookup's
`[14494114,16064526]`. Consequently the registered upper-versus-lower dominance
rule does not exclude lookup. XOR nevertheless has the unique strict minimum
opcode coordinate and survives every completion within those boxes. Lookup's
survival is possible, not necessary, under full rectangular interval uncertainty.
The packet therefore does not certify a two-member physical Pareto frontier.

A complete candidate frontier determines its family image; it carries more
detail than that image, which can remain unchanged when candidate membership
changes. These runs do not isolate why the observed intervals differ: interpreter,
priming, runtime state and uncontrolled run variation are not independently
identified by this comparison. See `EMPIRICAL_FRONTIER_IDENTIFICATION_THEOREM_V1.md`
for possible/necessary membership and transport premises. CLB-2 and CLB-3 in
`CONTINUOUS_LIFT_BOUNDARY_THEOREM_V1.md` distinguish attainment, approximation and
certified bounds; they do not imply that every finite window is unstable or that
all interval-based evidence is invalid. The channel claims retain their CL labels.

## 4. Margins recomputed from the raw boxes

Each wall ratio is the named neural candidate's observed minimum divided by
XOR's observed maximum; each opcode ratio compares exact full-domain counts.

| Instrument | Interpreter | DNF wall | DNF opcode | Shared-sum wall | Shared-sum opcode |
|---|---|---:|---:|---:|---:|
| V5 | 3.11.15 | 4.260 | 5.818 | 3.022 | 3.909 |
| V5 | 3.12.3 | 3.923 | 5.364 | 2.930 | 3.545 |
| V6 | 3.11.15 | 2.978 | 5.818 | 2.070 | 3.909 |
| V6 | 3.12.3 | 4.052 | 5.364 | 3.034 | 3.545 |
| V6 | 3.13.12 | 2.918 | 6.111 | 2.050 | 4.000 |

The original >=2.9 wall and >=5.3 opcode claim applies to DNF, not both neural
candidates. Across both registered neural candidates and all five valid packets,
the minimum ratios are 2.050419 wall and 3.545455 opcode. These are observed
run ratios and interpreter-specific exact counts, not population speed bounds.
Both neural boxes are robustly dominated by XOR in all five packets, including
process time; this finite comparison survives the numerical correction.

DNF wall margins range from 2.918352 to 4.259762. The two 3.11 runs differ by
1.281868, less than the 1.341410 difference between cross-interpreter extremes.
The earlier opposite numerical comparison was false. Moreover those two 3.11
runs use different instrument versions; this design identifies neither a pure
repeat variance nor a causal interpreter trend. V5/V6 exact opcode counts do
agree within each of their two shared interpreter versions.

## 5. Priming evidence and the earlier bias direction

The V6/3.13 packet reports one empty frame in each forward priming diagnostic,
followed by complete recorded forward and reverse witnesses. The 3.11/3.12
forward priming diagnostics report complete frames. Their false
`priming_was_required_on_this_interpreter` flags do not establish that adding
tracing leaves timing values or distributions unchanged.

The retained V5/3.13 refusal diagnostics are a later pass after the failed
preflight had already traced DNF. Their counts are DNF 440/440, XOR 63/72,
shared-sum 252/288 and lookup 112/128. Undercounting the latter three by 12.5%
makes them artificially cheaper relative to DNF. It does not flatter DNF or
uniformly favor the neural family: shared-sum is neural and is also undercounted.
This is not the first-candidate-in-process chronology. The actual V5 gate
refused before timing; no unvalidated deployment comparison was executed.

## 6. Static validation and remaining custody obligations

A matching-release static review of all three V6 packets recomputed source and
registration hashes, native AST/opcode offsets, 32 recorded capability cases,
64 complete recorded frames, all 128 timing blocks, schedule/checksums, observed
boxes and dominance results per packet. It called no candidates and reran no
timing. Wrong trace output, missing return, negative duration and wrong-frontier
countercontrols were rejected on each release. Source bytes match the frozen V6
harness hash `8a91ccfab5fd7fa914ced8738c251863e1e32f6e902e317e108172e1adb95b7c`.
This checks recorded evidence consistency; it does not authenticate remote clocks,
binary builds, host identity or an exhaustive attempt log.

Residual source limitations remain explicit:

- V6 checks an existing output path after running the experiment. Future execution
  needs a V6-bound reservation-before-execution custody route with failed attempts
  retained. The separately versioned V5 custody route does not authorize V6.
- The self-test emits GREEN even when its support Boolean is false, and does not
  fully validate recorded parity outputs/return flags. Actual measurement preflight
  does perform those checks; the retained successful witnesses pass the static review.
- Only forward priming summaries are retained, not full priming traces or reverse
  priming summaries. Failure diagnostics retrace instead of preserving every failed
  original trace. This limits tracing custody, not the validated recorded frames.
- The multi-schema aggregator compares asserted hashes and terminals. Its new
  instrument labels and separate family/candidate sets are useful summaries, but
  it does not derive packet validity from complete evidence or prove candidate
  identity against an external source anchor. Its output schema remains V5 even
  in the V6-named historical file. Future complete auditing needs versioned authority.

These limitations require versioned operational repairs; they do not, by themselves,
invalidate the consistent measured packets. Frozen harness/preregistration and raw
outputs have not been retroactively changed.

## 7. Remaining scientific scope

Cross-host replication (`laptop-billy`, `old`, `lunarc`), independently optimized
candidate coverage, developmental/lifetime accounting and independent prospective
replication remain open. `parity3_v5_runners/` is a V5 route only. Four candidates
do not establish a structural family cover; candidate-coverage and EFI premises
still govern any extension. Observed timing envelopes enclose the recorded blocks,
not all future runs. The recorded execution label remains
`PARITY3_V6_PROSPECTIVE_CLAIM_HELD_SINGLE_HOST_THREE_INTERPRETERS` at this scope.
