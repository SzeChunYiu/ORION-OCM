# Chunk-band feasibility — why a second *grammar* cannot be had by widening chunks alone

Feasibility measurement only. No authoring, no scored arm, no claim moves. Run on
laptop billy (never the Mac), against the **registered** compiler's own logic
(`m2p2_compile.decomposable`, its per-length hashed quotas and its viability floors),
so the numbers are that compiler's answers rather than a lookalike's.

## Why this was asked

The claim ladder names the limit itself: C3 would need *a different grammar or a
different acquisition mechanism*. Everything this lane has — C2, the d=2 replication,
guided-first, M2-P3 — lives in one grammar: four primitives, builders of length ≤ 8,
hidden chunks of length **2 or 3**.

A first candidate (a sibling substrate with five primitives, `triple`/`halve`) was
**rejected before it was built**. It changes what chunking *costs* (T 4 → 5, baseline
5⁸ vs 4⁸) but not what chunking *buys*: length-8 sequences still factor into 2–3-op
chunks, so the combinatorial skeleton the finding rests on is untouched. The tell was
that no prediction could be derived from it except "bigger T, bigger advantage" — a
monotone rescaling of the same mechanism, not a new test of it.

**That rejection must be read against what this lane has already done, not as a claim
that wider-primitive grammars are untried.** `m2p1/m2_ext_distance.py` runs exactly such
a substrate — `PRIMS6 = (inc, dec, double, square, triple, neg)` — and the **P = 6
analogue is complete**: 6 seeds, all `BENEFIT_SURVIVES_AT_D2`, with benefit not decaying
from d = 1 to d = 2 on any seed ([D2_REGISTERED_GRAMMAR.md](../m2p1/D2_REGISTERED_GRAMMAR.md),
records `m2p1/records/EXT_DISTANCE_*.json`). It is a research analogue, EXACT_MATCH-controlled
against the registered solver, not the registered grammar — which is precisely why it does
not by itself discharge C3. So the accurate statement is: a wider-primitive grammar has been
run and the d = 2 law held there; what is still missing is a variation carried through the
**registered, gated, authored-world** pipeline, which is what the chunk-band route below
would supply.

Widening the **chunk band** is the variation that does change the structure: with
chunks of length 3–4, reachable builder lengths are sums of {3,4} — 3, 4, 6, 7, 8 —
so **length 5 is unreachable**. And it needs no new substrate: the registered units
already admit fragments of length 2..8 (`methods.py` rejects only `len(p) < 2`), and
degree growth is unchanged, so the 257-coefficient and 4096-bit budgets and the
16-fragment cap all still hold.

## What was measured

400 sampled worlds per band, chunk count 4..8 and `min_builder_length` 4..8, against
the frozen floors (`members_min` 90, `initial_min` 15, `tuning_min` 6, `future_min` 20):

| band | viable | median members | max |
|---|---|---|---|
| 2–3 (registered control) | 60/400 (15.0 %) | 23 | 394 |
| **3–4** | **0/400** | 7 | 38 |
| 2–4 | 1/400 (0.2 %) | 10 | 102 |
| 4 only | 0/400 | 8 | 44 |

A sample of 400 misses is not a proof, so the ceiling was computed next.

## The result is structural, and the bound is exact

The **unbounded union** of every chunk in band 3–4 yields **19 809** members at
mbl = 4 — 220 × the floor. So the band is not the obstruction. The obstruction is the
spec's **chunk-count cap of 8**, and it is exactly quantifiable.

With `t` chunks of length 3 and `f` of length 4 (`k = t + f`), the only tilings of a
builder of length ≤ 8 are `4`, `3+3`, `3+4`, `4+3`, `4+4`. Hence

```text
members  ≤  f + t² + 2tf + f²  =  f + k²  ≤  8 + 64  =  72
```

The greedy search attains exactly **72**, so the bound is tight and the maximum is 72
— against a floor of 90. Clearing the floor needs `f + k² ≥ 90`, i.e. **k ≥ 10**.

The bound was validated before being relied on: 156 worlds across k = 4..16 compared
against exact compiler counts, **0 violations** (`records/band_k.log`).

## The niche the constraint names

Raising only the chunk-count cap makes the band viable, and the measurement agrees
with the bound — the first worlds clear the floor at exactly the predicted k:

| chunk count | max members (mbl 4) | viable / 60 |
|---|---|---|
| 8 | 59 | 0 |
| 10 | 77 | 0 |
| 12 | 89 | 0 |
| **13** | **103** | **3** |
| 15 | 173 | 8 |
| 16 | 140 | 15 |

So a second authored-world grammar is reachable as **band 3–4 with chunk count
10–16** — a new frozen spec over the *existing* substrate, not a sibling `methods.py`.
It is a re-registration (the spec is sha-bound at `6a25c7f3…` in `M2P2_FREEZE_V1.json`
and listed under `what_does_not_change` in M2P3-V2), and G-SURF would need
re-calibration, since its no-false-fire property was proven only on band-2–3 worlds.

## Two corrections to earlier readings in this lane

1. **"The floors are tight for every band" — wrong.** 15 % describes *random* draws.
   A deliberately chosen band 2–3 world reaches **3 272** members. Floors constrain
   careless authoring, not competent authoring.
2. **"Band 3–4 is infeasible" — too strong as first stated.** It is infeasible *under
   the chunk-count cap of 8*. The band itself supports 19 809 members.

## Raw records

`records/` — `BAND_PROBE.json`, `BAND_K.json`, the three scripts, `band_k.log`,
`HOST.txt`. Sampling seed 20260912.
