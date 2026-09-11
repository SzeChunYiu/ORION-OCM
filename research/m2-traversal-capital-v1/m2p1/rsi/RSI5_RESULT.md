# RSI-5 — the 33-case packet: L5 partly generalises, L6 still has no slope

The 9-case packet moved by one flipped case; the mission's remedy was more cases. The
LUNARC build labelled **24 further worlds mechanically** from evaluator-side facts
(admitted → C0; refused + incomplete recovery → C1; refused + complete recovery +
`2g > b_min` → C2; no motifs → C3) and computed every probe internally, including
`mdl_response` by re-mining and re-validating. Merged with the 9 originals: **33 cases** —
C0 × 9, C1 × 13, C2 × 9, C3 × 1, C5 × 1.

## A scoring defect, fixed before reading

The first run reported repair accuracy 0.21–0.27 — because the validated-repair table
covered only the 9 originals and every new case scored `False` unconditionally, capping
repair accuracy at 9/33. A mechanically-labelled case's validated repair is the one mapped
to its true cause, exactly as for the originals. Fixed; the numbers below are post-fix.

## Result

| gen | probes | exhaustive acc | exhaustive cost/verified | active acc | active cost/verified |
|---|---|---|---|---|---|
| G0 | 4 | 0.515 | 19.41 | 0.455 | **10.80** |
| G1 | 5 | 0.576 | 22.58 | 0.455 | 11.93 |
| G2 | 6 | 0.485 | 39.19 | 0.424 | 15.36 |
| G3 | 7 | 0.515 | 40.76 | 0.455 | 14.13 |
| G4 | 8 | **0.636** | 45.57 | 0.455 | 14.13 |

```text
TERMINAL: NO_IMPROVING_SLOPE   (both modes)      majority-class baseline: 0.394
```

The diagnoser that scored 9/9 on the original packet scores **0.64** on the expanded one
(exhaustive) and **0.46** under active probing — above the majority-class baseline, well
below its in-sample figure. L5 generalises only partly; L6's slope is absent again, and
this time the packet is large enough that the absence means something.

## Where it fails — the confusion at G4

| true | called |
|---|---|
| C0 healthy (9) | **C0: 9** |
| C1 incomplete recovery (13) | C1: 8, **C0: 5** |
| C2 arrangement depth (9) | **C1: 7**, C2: 2 |
| C3 unstructured (1) | C3: 1 |
| C5 shift (1) | C5: 1 |

Two confusions, each pointing at a probe the diagnoser lacks:

- **C2 → C1 (7 of 9).** The LUNARC C2 worlds have *full* recovery and shallow tilings;
  their depth failure is through `T` (16 tokens, `2g = 8 192 > b_min = 1 366`), not through
  a token count ≥ 4. The diagnoser's notion of depth was the D1/D2 kind only. The missing
  probe is **the depth bound itself**, `2·Σ_{i≤k} Tⁱ` vs `b_min`, computable from the
  library size and the targets' lengths.
- **C1 → C0 (5 of 13).** Refused worlds that are nonetheless better on most held-out
  targets look healthy on win-rate. The separator is the organism's **own gate verdict** —
  an internal fact the dev phase already computed, at zero probe cost.

Both are mechanism-derived and both are localised by a confusion class rather than
chosen by looking at answers. Registered before G5/G6 run: accuracy ≥ 0.85 at ≤ +2 cost
per case, so `cost_to_verified_improvement` falls below G4 for the first time.
