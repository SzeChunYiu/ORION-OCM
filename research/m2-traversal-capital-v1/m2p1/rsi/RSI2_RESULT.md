# RSI-2 — the failure → diagnosis → repair loop closes, at 3.1× chance

[RSI-1](RSI1_RESULT.md) returned `CANNOT_CHECK_DIAGNOSER_UNCALIBRATED`: likelihoods were
guessed, the diagnoser answered `C1` for every case including all three healthy controls,
and the failure localised a missing probe — a **structure-existence test**, which is
`V_H(E) > 0` and `Ĉ_t` in internally computable form.

RSI-2 adds exactly that probe and nothing else.

## The added probe

**MDL compression gain**: how much shorter is the solved corpus when described through a
mined vocabulary rather than primitives? High gain means latent structure exists. It is
the same machinery that produced the [MDL selection rule](../MDL_SELECTION.md), reused as
a diagnostic — and it is computable by the organism, using no evaluator-side facts.

## Result

| case | true cause | diagnosed | proposed repair | independently validated repair | |
|---|---|---|---|---|---|
| E3_16motifs | C1 | **C1** | MDL_SELECTION | MDL_SELECTION | ✓ |
| E7_longhorizon | C1 | **C1** | MDL_SELECTION | MDL_SELECTION | ✓ |
| E5_healthy | C0 | **C0** | none | none | ✓ |
| E8_healthy | C0 | **C0** | none | none | ✓ |
| E6_healthy | C0 | **C0** | none | none | ✓ |
| FOREIGN_M1 | C3 | C1 | MDL_SELECTION | APPLICABILITY_GATE | ✗ |
| D1_m12k4 | C2 | C1 | MDL_SELECTION | REDUCE_K_OR_RAISE_P | ✗ |
| D2_m12k4 | C2 | C1 | MDL_SELECTION | REDUCE_K_OR_RAISE_P | ✗ |

```text
cause accuracy   0.625   (chance 0.200)
repair accuracy  0.625
no-alarm control 3 / 3
TERMINAL: FAILURE_TO_REPAIR_LOOP_CLOSED
```

The repair column is what makes this a *loop* rather than a classifier: each cause maps to
a pre-registered repair, and the repairs are ones **independently validated elsewhere in
this lane** — MDL selection took E7 from 5/7 recovery and refusal to 7/7 and admission;
the applicability gate beat the parent by 32 % on FOREIGN_M1. A match means the diagnosis
selected a repair that was separately shown to work on that case.

## The recursive step, measured

| | diagnoser | cause accuracy | healthy controls |
|---|---|---|---|
| RSI-1 | guessed likelihoods, 6 probes | 0.250 | **0 / 3** (called C1 on healthy runs) |
| **RSI-2** | mechanism-derived, + compression probe | **0.625** | **3 / 3** |

A failure localised a missing probe; adding that probe improved the next iteration of the
same diagnoser. That is the RSI mechanic operating on this lane's own history, not a
simulation of it.

## What is still wrong, and not tuned away

Three misses, both classes diagnostic rather than random:

- **C2 (arrangement depth) is outvoted, not unseen.** `guided_depth` fires correctly on
  D1/D2 (`tokens_needed = 4` → C2 at 0.65), but composability (0.77 → partial → C1 0.50)
  and win-rate (minority → C1 0.40) overwhelm it. The discriminator exists and is
  under-weighted.
- **C3 versus C1 remains unseparated** — the same pair RSI-1 could not split. Compression
  gain helps (FOREIGN_M1 at 0.05 is the lowest in the set) but is outvoted by the same two
  probes.

The likelihoods were **not** adjusted to fix these. Fitting five free tables against eight
known answers would manufacture a diagnoser that works on exactly these eight cases, which
is the outcome-driven tuning this programme forbids. The honest next step is the one RSI-1
demonstrated: find the probe that separates the confused pair, from the mechanism.

**The named next probe** is an *oracle-also-fails* signal — on D1/D2 the true-motif library
also failed (103 vs RESET 104), which is the deterministic signature of depth rather than
library quality. An organism can approximate it by observing that even its best
constructible library does not help.

## Claim ceiling

Eight cases from one lane's history, one cause taxonomy, one repair catalogue. **Not**
established: that the diagnoser transfers to failure classes outside this taxonomy, that
0.625 is stable under more cases, or that the repairs would have been discovered rather
than selected from a registered list. RSI-3 (reuse on new failure classes) and RSI-4
(does improvement history reduce future improvement cost) remain unstarted.
