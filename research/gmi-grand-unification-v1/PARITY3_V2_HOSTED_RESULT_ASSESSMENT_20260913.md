# Registered parity-3 V2 hosted result

The first committed V2 main execution selects **`X_XOR2_V1`** with terminal
`DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE`. Its exact opcode count and both observed
timing envelopes strictly dominate those of the frozen neural threshold candidate
on this run. This is the registered two-candidate point verdict. It does not
establish a universal non-neural preference or independent prospective confirmation.

## Execution identity and custody

The V2 instrument/preregistration/workflow were committed before timing in
[PR #524](https://github.com/SzeChunYiu/ORION-OCM/pull/524), main SHA
`204d5c74754a2bec6d50d9a3129f5b519438f5ea`. The evidence worktree starts at this
same exact main SHA.

- [Run 34745072337](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34745072337), attempt 1, main push, created 2026-09-13 07:22:31 UTC.
- [Job 103691366884](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34745072337/job/103691366884): every step succeeded, including instrument preflight, registered timing, artifact upload and tracked-source integrity.
- CPython **3.12.14**, Linux x86_64, GitHub hosted runner, four CPUs.
- Harness SHA256: `c7415458c306a01f6db4182b521cae3b4392a086630f234f83b982b8901aee9a`.
- Preregistration SHA256: `c2dea4caddb548278a2770755eda9835205ac85226317288f45d63be4b1f095c`.
- [Artifact 10313931013](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34745072337/artifacts/10313931013), `grand-gmi-parity3-point-v2`, 4246 bytes, created 07:23:24 UTC. GitHub reports ZIP SHA256 `3625b6b417abcf0b08dee4438aac6c1a4cbd3ea66e8e792716af43f3b46aba67`.

`NN_NONNN_POINT_PARITY3_HOSTED_RESULT_V2.json` retains exact hosted stdout JSON,
removing only timestamp prefixes. `NN_NONNN_POINT_PARITY3_HOSTED_PROVENANCE_V2.json`
retains the timestamped excerpt, byte hashes, source identities, artifact metadata
and independent packet audit. The artifact ZIP was materialized by the GitHub
connector, but downloading its bytes into this workspace returned HTTP 403. Its
ZIP checksum is therefore reported metadata; it is not claimed as independently
recomputed. The locally retained measurement packet is checked against its
hosted-job stdout and exact excerpt custody; no ZIP byte comparison is asserted.

## Registered observations

Both candidates return exact parity on **8/8** inputs. The constant-zero null
returns **4/8**. Each candidate has **31** timed blocks, **160000** calls per block,
with the frozen alternating candidate order and checksum **80000** in every block.
This totals **62 blocks and 9,920,000 timed candidate calls** across both candidates.

| Registered coordinate | Neural `N_THRESHOLD_DNF4_V1` | Non-neural `X_XOR2_V1` |
| --- | ---: | ---: |
| Candidate-frame opcode events per eight-input sweep | 472 | 88 |
| Wall time per 160000-call block, observed min–max (ns) | 57,997,819–63,429,301 | 12,154,581–13,130,638 |
| Process time per 160000-call block, observed min–max (ns) | 58,001,308–63,423,878 | 12,155,813–13,131,470 |

For each of the three coordinates, the XOR candidate's upper endpoint is strictly
below the neural candidate's lower endpoint. Independently recomputing the Pareto
rule reproduces the recorded winner, terminal and
`repair_expectation_passed: true`.

The instrument packet contains all **32** candidate-frame traces: two candidates
times eight inputs times forward/reverse measurement order. Every trace contains
the complete expected straight-line opcode offset sequence and exact return;
forward and reverse witnesses are identical. Thus the repaired first-call tracer
defect is absent from this packet.

## Independent audit and limits

A separate static packet audit passes **60 explicit invariant checks**, covering
frozen source/preregistration hashes, environment, capability, all trace witnesses,
62 block identities/checksums, all six resource intervals, registered verdict and
byte-exact hosted-stdout custody. The audit reads and disassembles the frozen source
but does not call candidate or timing functions. The coordinator independently
recomputed the block/box/trace/winner checks as a second review. No experiment was
rerun to produce this evidence iteration.

The original V1 packets remain `UNDECIDED_FROM_CURRENT_EVIDENCE` with their original
failed prediction and recorded instrumentation defect. V2 remains explicitly a
post-V1 repair expectation, with `independent_prospective_prediction: false`.
Neither version's source, preregistration or workflow is changed by this evidence
iteration.

The time intervals are finite observed block envelopes for this execution, not
population confidence intervals. The candidate expansion attack remains
`NOT_YET_RUN`; optimized neural candidates, lookup tables, other interpreters,
other workloads, authoring/training cost and universal family preference are
outside the registered verdict. These limits remain open rather than being
converted into evidence by a green hosted job.
