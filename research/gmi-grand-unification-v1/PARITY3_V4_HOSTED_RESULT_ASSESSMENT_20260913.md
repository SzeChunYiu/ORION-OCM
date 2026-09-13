# Four-candidate parity-3 expansion: first V4 hosted result

**XOR is the sole registered robust-frontier survivor.** All four candidates
pass every parity input. XOR's upper endpoint is below every competitor's lower
endpoint in each of the three resource coordinates. The registered terminal is
`DERIVED_NON_NEURAL_AT_REGISTERED_SCOPE`, and the expansion expectation passes.

This is the four-implementation deployment result, not a universal family
preference or independent prospective replication. The improved neural candidate
does improve over the original neural implementation within this same execution,
but does not reach XOR's resource box.

## Source and execution

[PR #529](https://github.com/SzeChunYiu/ORION-OCM/pull/529) froze V4 before timing
at main `d6147f95e48b2e4e4afc2c3bd1dee8551527c2fc`. The complete candidate and
instrument identity controls passed before the run.

- [Run 34749100254](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34749100254), first attempt, main push.
- [Job 103702229052](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34749100254/job/103702229052), all steps successful.
- Harness SHA256: `d39961ffa6fe81a978c9d9a45e91be500e7dc52178de183f7699b9fec31a256e`.
- Registration SHA256: `7d0b4bc0cf6c2655694a08c9c1261f354519e005e92ed3ecfc435e97cedac54b`.
- Retained stdout-packet SHA256: `9fffd62abcbdda014464b16c586fc856e617e4caf54f88da3e77645f368a8196`.
- Artifact `10315471553`, `grand-gmi-parity3-point-v4`, 6536 bytes. GitHub reports ZIP SHA256 `83698c2fcf811a4291a0b5239ee83a5ae2f0d74611a4f576a98ac936a36d58fb`; these are metadata, not an independently recomputed ZIP digest.

`NN_NONNN_POINT_PARITY3_HOSTED_RESULT_V4.json` retains the exact stdout JSON
after removal of timestamp prefixes. Its provenance file retains the timestamped
excerpt, byte hashes and exact run/artifact metadata. The audit checks that
stripping the recorded excerpt reproduces the packet byte-for-byte. ZIP bytes
were not downloaded or compared; no artifact-ZIP custody claim is made.

## Observations

Every candidate passes 8/8 inputs; the constant-zero null passes 4/8. There are
32 timed blocks per candidate, 160,000 calls in each block, checksum 80,000 in
every block: **128 blocks and 20,480,000 timed candidate calls**. Each candidate
occupies each block position eight times. All 64 forward/reverse per-input
opcode traces contain the complete expected straight-line offsets and returns.

| Candidate | Family | Opcodes per full input sweep | Wall block ns, observed min–max | Process block ns, observed min–max |
| --- | --- | ---: | ---: | ---: |
| `N_THRESHOLD_DNF4_V1` | Neural | 472 | 71,198,649–77,576,546 | 71,200,228–77,566,746 |
| `N_SUM_THRESHOLD3_V3` | Neural | 312 | 54,421,845–56,454,579 | 54,423,176–56,456,795 |
| `X_LOOKUP8_V3` | Non-neural | 136 | 18,274,827–18,975,129 | 18,277,428–18,976,986 |
| `X_XOR2_V1` | Non-neural | 88 | 14,297,348–15,289,119 | 14,298,703–15,291,887 |

The static auditor independently reconstructs capability, disassembled trace
witnesses, schedule/checksums, every observed envelope, every domination edge,
the complete frontier and terminal. It imports function definitions but never
calls candidates, warm-up or timing. Hostile tests alter traces, schedules,
checksums, boxes, frontier, source custody and scope claims—even with rewritten
packet/log hashes—and require rejection. This is coordinator audit, not external
scientific review. No measurement was rerun for this evidence iteration.

## What this closes and what it does not

This supplies the missing measured comparison against the separately derived
three-threshold network and exact lookup competitor. It preserves V1's defective
outcomes, V2's two-candidate outcome, and unexecuted V3's registration. The V3 IDs
of the new candidate functions remain stable inside V4.

The algebraic neural reduction is not independently optimized by an external
party and is not proved globally optimal. Other neural realizations, more tasks,
substrates and independently held-out replications remain separate obligations.
Timing boxes are observed block envelopes, not population confidence bounds.
Construction/authoring/training costs are excluded, so the result supplies no
whole-lifecycle advantage. Knowing V1/V2 before registering the expansion also
precludes describing it as independent prospective scientific confirmation.
