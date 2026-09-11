# The benefit survives at d = 2 in the registered grammar — and the "obstruction" was an admission bound

[ARRANGEMENT_OBSTRUCTION.md](ARRANGEMENT_OBSTRUCTION.md) concluded `d ≥ 2` was not
testable at `P = 4`: zero configurations satisfied recovery, novelty and the depth bound
`2g ≤ b_min` together. That conclusion is **revised here**, by a run in the registered
grammar with the registered solver.

## The run

`ECO_K4_D2` — 12 length-2 motifs, `k = 4`, 120 training targets, **60 protected targets
every one of which is at Levenshtein distance ≥ 2 (in motif sequence) from every
training arrangement**, part coverage 1.0. Library selected by MDL from the solved
training corpus; served through the registered `M.solve`; every success externally
verified after a real process restart.

| arm | mean `B` at `d = 2` (n = 60) |
|---|---|
| `SHUFFLED_HISTORY` | 100 732 |
| `RESET` = `CONTINUED` (registered gate refuses) | 51 459 |
| **`CONTINUED_MDL`** = `PARENT_WITH_MDL` | **42 089** |

```text
reduction vs RESET at d = 2 :  18.2 %      strictly better : 30 / 60
```

**History reduces the work to acquire targets that are novel *arrangements* of known
parts.** That is the claim the hostile review said was untested and the feasibility map
said was unreachable. It is neither.

## What the map got wrong, precisely

The depth condition `2g ≤ b_min` is the condition for the registered **all-or-nothing
admission** to fire: every held-out target must be non-inferior, so the *cheapest* target
binds. It is a **worst-case admission bound**, and it is correct as such — the gate did
refuse (30 of 60 are worse-or-equal, and one is enough). But it says nothing about the
**mean benefit**, which is what a per-target gate would harvest. Compositions that rank
early in the guided stream are reached long before `b`; the map's error was to treat the
gate's veto as the substrate's ceiling.

A second correction: the hypothesis that MDL would pick "chunks of chunks" (length-4
motif pairs, cutting effective `k`) did **not** occur — the selected library is eleven
fragments, **all length 2**. The `d = 2` benefit arrived without hierarchical chunking.
The `mdl_response = +11/+9` on D1/D2 was real but its proposed mechanism was wrong;
recorded as such.

## Scope, stated exactly

- **Library level, not deployment.** `PARENT_WITH_MDL` is identical to `CONTINUED_MDL`
  to the slot. The registered gate refuses; the benefit is what the ungated parent gets.
  A deployable OCM arm needs the [probe gate](APPLICABILITY.md) on top — running now on
  these 60 targets.
- **One seed, one ecology shape.** `d = 1` on the matched mixed ecology (D1) is running,
  which gives the decay from `d = 1` to `d = 2` on the same library.
- **Not `d ≥ 3`** — still empty by counting at this `(m, k)`.

## Ladder consequence

`U2 / L2` moves from *"bounded at `d = 1` by the substrate"* to **"positive at `d = 2` in
the registered substrate at the library level, deployment pending the probe gate."** The
obstruction analysis stands as an analysis of the **admission rule**, which is exactly
where the mission's gap list already points: all-or-nothing admission is the bottleneck,
not `P = 4`.

## Fit-size sweep (oracle-feature ceiling, acquisition-cost shape is real)

For the fitted gate on the 670-target worlds, the marginal ledger against fit size:

| fit_n | 3001 break-even | 3003 break-even | pays (horizon ≈ 670) |
|---|---|---|---|
| 10 | 157 | 132 | ✓ ✓ |
| 20 | 309 | 261 | ✓ ✓ |
| 40 | 600 | 462 | ✓ ✓ |
| 70 | 846 | 763 | ✗ ✗ |
| 103 | 1 595 | 1 424 | ✗ ✗ |

Monotone: the gate's acquisition cost is the fit, and a small fit suffices. The **probe
gate needs no fit at all**, so for it this ledger collapses to "does probe-B beat RESET-B" —
which is what the 670-target probe run now measures.

## The decay curve — benefit does not decay with distance

D1 is the matched mixed ecology (same 12 motifs, `k = 4`, same MDL library selection),
whose protected stream carries both grades. Joining each arm's per-target rows to the
ecology's `arrangement_distance_to_train`:

| ecology | distance | n | RESET | MDL library | reduction | strictly better |
|---|---|---|---|---|---|---|
| D1 | **1** | 34 | 48 361 | 45 832 | **5.2 %** | 15 / 34 |
| D1 | **2** | 26 | 49 963 | 43 506 | **12.9 %** | 12 / 26 |
| D2 | **2** | 60 | 51 459 | 42 089 | **18.2 %** | 30 / 60 |

**The benefit does not decay from `d = 1` to `d = 2`; it rises.** An interpolator over
stored solutions — the hostile review's alternative explanation — would show its largest
benefit at `d = 1` and collapse at `d = 2`. The observed direction is the reverse. The
transferable object is therefore a **compositional prior over parts**, indifferent to how
far the target's arrangement sits from any solved arrangement, not proximity to anything
already solved.

Claim ceiling for this sub-result: one library, one seed, `n = 34 / 26 / 60`. The rise
from 5.2 % to 12.9 % within D1 is inside sampling noise at these sizes; what is *not*
noise is the absence of the collapse that interpolation predicts. A replication of pure `d = 2` at the feasible window (`m = 12, k = 4, train_n = 90`) is
running across 9 seeds. Replicates so far, pure `d = 2`:

| seed | n | RESET | MDL library | reduction | better | **integrated arm** |
|---|---|---|---|---|---|---|
| D2 | 60 | 51 459 | 42 089 | 18.2 % | 30 | 22 685 (−56 %) |
| R401 | 60 | 56 386 | 49 884 | 11.5 % | 25 | — |
| R404 | 59 | 50 016 | 41 757 | 16.5 % | 33 | **22 265 (−55.5 %)** |

Same sign on every seed; shuffled ≈ 2× RESET on every seed.

## Deployment at d = 2 — two gates, complementary regimes

| gate on D2 (pure `d = 2`, n = 60) | served | RESET | parent (always serve) | gate | oracle |
|---|---|---|---|---|---|
| **observable** (task-statement features) | 70 % | 51 459 | 42 089 | **38 877** | 34 313 |
| probe (depth ≤ 3) | **0 %** | 51 459 | 42 089 | 55 074 | 34 313 |

The **observable-feature gate is positive at `d = 2`**: −24.5 % vs RESET and **−7.6 % vs
the parent with the same library**, leak-free. That is a deployable OCM-specific win on
novel arrangements in the registered grammar.

The **probe gate fails here for a mechanism-exact reason**: D2's targets are 4-token
compositions and the registered probe spans ≤ 3 tokens, so it never hits and pays only
`β` — the "β-overhead regime" the [probe-gate note](PROBE_GATE.md) said was untested.
It is now measured: −7.0 % vs RESET, the predicted overhead.

So the two deployable gate forms have **complementary regimes** — the probe wins at
composition depth ≤ 3 (FOREIGN_M1, the 670-target worlds), the task-statement rule wins
at depth 4 (D2), and neither is universal. The mechanism-derived next step is a probe
whose depth is **learned from history** (the tiling-token count of solved training
programs is observable). Registered prediction before the run: on D2 it hits ~50 % and
its expected `B` (~61 k) *exceeds* RESET — likely negative; the run measures the boundary
rather than rescues the gate.

## Replication complete — ten seeds, all positive

Pure `d = 2`, `m = 12, k = 4, train_n = 90` (inside the feasibility window), 58–60
protected targets per seed (R403's ecology draw was the last to pass the gates), every target ≥ 2 motif substitutions from every training
arrangement, part coverage 1.0:

| seed | RESET | MDL library | reduction | better | **integrated arm** | reduction |
|---|---|---|---|---|---|---|
| D2 | 51 459 | 42 089 | 18.2 % | 30/60 | 22 685 | 55.9 % |
| R401 | 56 386 | 49 884 | 11.5 % | 25/60 | 26 087 | 53.7 % |
| R402 | 63 275 | 53 734 | 15.1 % | 32/60 | 26 867 | 57.5 % |
| R403 | 59 562 | 41 415 | 30.5 % | 43/60 | 21 012 | 64.7 % |
| R404 | 50 016 | 41 757 | 16.5 % | 33/59 | 22 265 | 55.5 % |
| R405 | 58 039 | 32 124 | 44.7 % | 45/60 | 16 062 | 72.3 % |
| R406 | 64 480 | 45 135 | 30.0 % | 36/60 | 22 651 | 64.9 % |
| R407 | 59 844 | 42 509 | 29.0 % | 35/60 | 22 942 | 61.7 % |
| R408 | 54 800 | 39 396 | 28.1 % | 38/60 | 20 562 | 62.5 % |
| R409 | 61 897 | 32 891 | 46.9 % | **58/58** | 16 446 | 73.4 % |

```text
library:        10 / 10 positive   mean −27.0 %   min −11.5 %
integrated arm: 10 / 10 positive   mean −63.4 %   min −53.7 %
shuffled:       worse than RESET on every seed (≈ 2×)
integrated / same-library parent:  0.500 – 0.540 on every seed (mean 0.514)
```

The integrated-over-parent ratio sits at the P1 bound on every seed: the probe serves
the guided stream alone, so a library hit at guided slot `g` costs `g` where the
interleaved parent pays `2g`. Nothing else in the controller moves at `d = 2` — the
task-statement rule and liveness never fire because the library keeps hitting.

**History makes novel arrangements of known parts cheaper to acquire, on every seed, in
the registered grammar.** The hostile review's interpolation reading is refuted with
replication, not a single run. `d ≥ 3` remains empty by counting at this `(m, k)`.

## Beyond the measured map: m = 14, k = 4 (registered 2026-09-11, seeds 504–506 launched after 501–502 were read)

Seeds 501–503 (`m = 14, k = 4, train_n = 90`, outside the feasibility table's measured
rows) were launched as an unregistered extension before any prediction was written; their
first two results are therefore **exploratory**: 501 library −1.0 % (17/59 better),
integrated −49.5 %; 502 library +27.1 % (36/60), integrated −60.3 %. Registered now, before
seeds 503–506 are read: the library-by-interleave benefit is **fragile** at m = 14 (its
sign may vary by seed, since per-motif support at train_n = 90 falls to ≈ 26 occurrences
and the 16-fragment library cannot hold every motif with its substrings), while the
integrated arm stays at **≤ 0.55 × the same-library parent and ≤ 0.65 × RESET on every
seed** — the probe serves the guided stream alone, so a partially-recovered library that
hits on a fraction of targets still pays. Falsifier: any seed with integrated ≥ 0.65 × RESET
or ≥ 0.55 × the parent.

**Seed 503 (read after the registration above):** library +0.5 % (27/60), integrated
33 341 = **0.571 × RESET, 0.574 × the same-library parent**. The RESET bound held; the
parent bound (≤ 0.55) **missed by 0.024**, and the miss is a derivation error, not noise:
the 0.50 ratio is the P1 bound against a parent that *benefits* from the library (parent
≈ 2g); when the library is worthless the parent sits at RESET and the ratio is simply the
controller's own probe benefit. Corrected registration for 504–506: **integrated ≤ 0.65 ×
min(RESET, parent)** on every seed — the same quantity in both regimes. Records
`records/DIST_SPLIT_M14_50{1,2,3}.json`.

| seed | library vs RESET | integrated / RESET | integrated / parent |
|---|---|---|---|
| 501 | −1.0 % | 0.505 | 0.500 |
| 502 | +27.1 % | 0.397 | 0.545 |
| 503 | +0.5 % | 0.571 | 0.574 |

