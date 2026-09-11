# RSI-3/4 — no improving slope across generations, and a correction to RSI-2

L6 requires **improvement of the improvement process itself**: a prospectively registered
improving slope in `cost_to_verified_improvement` across matched generations. One
successful self-change is not it. This runs the diagnoser for five generations, each
differing from the last by **exactly one mechanism-derived probe**, added in the order its
necessity was discovered from the previous generation's misses. Likelihoods are never
refit — that is what makes the generations matched.

| gen | probe added | why (the previous generation's miss) |
|---|---|---|
| G0 | — | RSI-1's mechanism-likelihood diagnoser, 4 core probes |
| G1 | `compression_gain` | RSI-1: C3 vs C1 unseparated → structure-existence test |
| G2 | `oracle_also_fails` | RSI-2: C2 outvoted → true-motif library also fails on D1/D2 |
| G3 | `drift_signal` | GAP_AUDIT: no cause class for ecology shift → adds C5 |
| G4 | `mdl_response` | G3: FOREIGN_M1 still wrong → does the cheapest repair move held-out? |

## Result — exhaustive probing (every available probe runs)

| gen | probes | cost | cause acc | repair acc | cost / verified improvement |
|---|---|---|---|---|---|
| G0 | 4 | 90 | 0.778 | 0.778 | **12.86** |
| G1 | 5 | 117 | **0.556** | 0.556 | 23.40 |
| G2 | 6 | 171 | 0.778 | 0.778 | 24.43 |
| G3 | 7 | 189 | 0.889 | 0.889 | 23.62 |

## Result — active probing (VOI policy, pre-registered in RSI-1)

| gen | probes available | cost spent | cause acc | repair acc | cost / verified improvement |
|---|---|---|---|---|---|
| G0 | 4 | 74 | 0.778 | 0.778 | **10.57** |
| G1 | 5 | 85 | 0.778 | 0.778 | 12.14 |
| G2 | 6 | 109 | 0.778 | 0.778 | 15.57 |
| G3 | 7 | 98 | 0.889 | 0.889 | 12.25 |
| G4 | 8 | 98 | 0.889 | 0.889 | 12.25 (probe unknown; pending) |

```text
TERMINAL: NO_IMPROVING_SLOPE   (both modes)
```

Accuracy rises G0 → G3 (0.778 → 0.889) but cost per verified improvement does not fall —
it is non-monotone in both modes, and never returns below G0. **L6 stays red.**

## Per-case calls across generations

| case | true | G0 | G1 | G2 | G3 |
|---|---|---|---|---|---|
| FOREIGN_M1 | C3 | C1 | C1 | C1 | **C1** — wrong in every generation |
| D1 / D2 | C2 | ✓ | **C1** | ✓ | ✓ |
| E3 / E7 | C1 | ✓ | ✓ | ✓ | ✓ |
| E5 / E8 / E6 | C0 | ✓ | ✓ | ✓ | ✓ |
| PLAST_shift | C5 | C1 | C1 | C1 | ✓ |

## A correction to RSI-2

[RSI2_RESULT.md](RSI2_RESULT.md) reported that adding the compression probe lifted the
diagnoser from 0.25 to 0.625. **That attribution was wrong.** The RSI-1 → RSI-2 step
changed two things at once — the likelihood tables *and* the probe — and this generation
sweep separates them:

- G0, with the mechanism tables and **no** compression probe, scores **0.778**;
- G1, adding the compression probe, scores **0.556** under exhaustive probing.

The entire RSI-1 → RSI-2 improvement was the **likelihood tables**. The compression probe
was net **negative** — it flips D1/D2 from the correct C2 to C1 by outvoting the depth
signal. `oracle_also_fails` then repairs precisely that flip. Under the active policy the
probe is simply not selected where it is uninformative, which is why G1 stops hurting there.

That is the same shape as HC-7 and the non-monotone dose-response: **accumulating probes
dilutes the diagnoser exactly the way accumulating fragments diluted the library.** The
RSI layer reproduces the failure mode of the layer beneath it.

## What is established and what is not

Established: the generation mechanic runs on real failures; each probe was justified by
a counterexample before being added; active selection prevents new probes from hurting.

Not established: **L6.** The slope is not improving. Two honest reasons the mission should
weigh:

1. The probes were selected by human/AI analysis of the misses. This is the improvement
   process being *improved by failure*, not the organism doing it autonomously — L5
   territory, not L6.
2. Nine cases. `cost_to_verified_improvement` moves by one case flipping. A slope needs a
   larger sealed packet; the LUNARC RSI-GENERATIONS campaign in the mission is the right
   instrument, and it should be frozen before any further generation is added here.

G4 is reported when the `mdl_response` probe lands; it does not change the L6 verdict
either way, because the slope is already non-monotone through G3.
