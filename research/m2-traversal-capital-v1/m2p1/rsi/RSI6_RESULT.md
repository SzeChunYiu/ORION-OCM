# RSI-6 — a zero-cost probe produces the first fall in cost-to-verified-improvement

Two probes were localised by the [RSI-5 confusion](RSI5_RESULT.md). One of them was
replaced before running, on inspection rather than on outcome.

## The probe that was discarded before it ran

`2g > b_min` — the depth bound — turned out to be violated for **nearly every world in
the packet, healthy ones included** (`T = 20` for every frequency library, `b_min` is the
cheapest target). A probe that reads the same on every case carries no information; a
mechanism likelihood that pretended otherwise would have pushed everything to C2. It was
replaced by the cost rule's own inner estimate, **`probe_pays_frac`**: the fraction of
solved validation targets a guided probe would reach before the baseline index they
actually paid. It is observable, and it *does* vary — 0.0 on D1/D2, ~0.5 on the LUNARC
lifetime worlds, 1.0 on the healthy E5/E8.

## Result (33 cases, exhaustive)

| gen | added probe | cost | accuracy | cost / verified improvement |
|---|---|---|---|---|
| G4 | — | 957 | 0.636 | 45.57 |
| G5 | `probe_pays` (cost 2) | 1 023 | 0.667 | 46.50 |
| **G6** | **`admitted` (cost 0)** | 1 023 | **0.758** | **40.92** |

`admitted` — the organism's own gate verdict — costs nothing and lifted accuracy by 0.12,
so `cost_to_verified_improvement` **fell** for the first time across generations on this
packet. Over G4 → G6 both measures improve together, which is the shape L6 asks for.

```text
TERMINAL: NO_IMPROVING_SLOPE   — over the full G0 → G6 sequence
```

The terminal stands because the early generations added expensive, weakly informative
probes (G1–G4 took the cost from 19 to 46 per verified improvement). A slope that is
improving over the last three generations and not over all seven is reported as exactly
that. **Registered prediction half met:** cost fell below G4 ✓; accuracy 0.758 < 0.85 ✗.

## Confusion at G6 — what the remaining miss says

| true | called |
|---|---|
| C0 (9) | C0: 9 |
| C1 (13) | **C1: 13** |
| C2 (9) | **C1: 7**, C2: 2 |
| C3 (1) | C1: 1 (regressed from G4) |
| C5 (1) | C5: 1 |

C0 and C1 are now perfect. The residual is the **LUNARC lifetime worlds labelled C2**:
full recovery, refused, `probe_pays ≈ 0.5` — the ambiguous band. Two honest observations
about them, recorded as the next gap rather than resolved by adjustment:

1. On observable probes they are genuinely between C1 and C2, and the mechanical label
   (`2g > b_min` with complete recovery) is itself the weak part of the labelling rule —
   it fires for almost everything.
2. The repair that *actually worked* on them was the [probe gate with cost-depth](../PROBE_GATE.md),
   which belongs to the applicability family, not `REDUCE_K_OR_RAISE_P`. The repair
   catalogue predates that result and should be revised: C2's canonical repair is now
   depth-aware per-target deployment.

Active mode: G5's `probe_pays` also produced its first cost fall (14.13 → 10.73) at flat
accuracy; G6 under the VOI stopping rule is reported in the JSON.
