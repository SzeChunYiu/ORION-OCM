# AH4 — the L0–L8 organization ladder, measured (START HERE)

The issue states a nine-level hierarchy and calls it provisional. This tranche defines one
exactly computable invariant per transition, measures all eight over a registered universe,
finds the nearest system that fails each, and reports what the ladder actually is at that
scope — including three places where it is weaker than the wording suggests.

## Headline numbers (exact integer and rational arithmetic; no float enters any claim)

| quantity | value |
|---|---|
| registered systems rebuilt from the AJ4 definition | `260` = 4 cell-free + 256 one-cell |
| behavioural classes, by reachable product exploration | `148`, sizes `{1: 144, 29: 4}` — matching the merged AJ4 numbers |
| transitions separating on visible behaviour | `3 of 8` (`L1->L2`, `L2->L3`, and no others) |
| transitions separating only relative to a declared external boundary | `2` (`L5->L6`, `L6->L7`) |
| transitions separating only on the description | `3` (`L0->L1`, `L3->L4`, `L7->L8`) |
| intermediate layer between `L1` and `L2` | `112` systems hold a state cell whose distinction never reaches the word behaviour |
| systems that pass `I2` but fail `I1` | `14` — the ladder is **not** cumulative at its base |
| irreducible composites | `15,680` of `67,600` |
| nearest-negative edit distances | `I1` 2 · `I2` 1 · `I3` 1 · `I4` 7 · `I5` 1 · `I6` 1 · `I7` 1 · `I8` 1 |
| level order against capability order | `1,914` ordered pairs where the higher-level system is strictly dominated |
| prohibition checker | trips on a live configuration, admits when evidence is present, ignores a plain level statement |

## The three findings you must not drop

1. **`L2` conflates two clauses.** 144 systems hold a cell *and* are behaviourally
   history-dependent; **112 hold a cell whose distinction never reaches the external word
   behaviour**; 4 hold no cell; the fourth combination is empty. An intermediate layer belongs
   between `L1` and `L2`.
2. **The base is not cumulative.** 14 systems are history-dependent without reusing any local
   transition effect, so "at level `k`" cannot be read as "satisfies `I1 … Ik`". The ladder is a
   partial order at this scope. `LADDER_IS_TOTAL_ORDER` is forbidden for that reason.
3. **Five of the eight transitions are not behavioural.** `L3->L4` is exhibited to collapse: the
   adaptive witness is re-described as a plain transducer over `(state, experience)` and the
   re-description reproduces it on all 62 registered words. `L5->L6` and `L6->L7` separate only
   while the external value is held outside the visible input, and the exhibit is two runs with
   identical internal state and identical visible input whose outcomes differ. `L0->L1` splits
   2 of the 148 behavioural classes. `L7->L8` is stated on description length and search
   distance rather than expressive power, because a merged parent already proved a macro
   library adds none.

## Evidence

- **2 materially independent routes.** Route A: pairwise reachable product exploration, word
  signatures, and series composition through word-response tables. Route B imports nothing from
  A: Moore partition refinement over the whole set at once, and composite reducibility read off
  the minimized four-state product machine. **27 published quantities agree, 0 disagreements.**
- **13 hostiles, all detected, each with a clean control**: a motif key that ignores the state
  change, `I2` with its behavioural clause dropped, parallel instead of series wiring, no
  minimization, a length bound of 2, a non-adaptive system claimed adaptive, an internal
  adoption guard, a population with no channel, a renaming unit claimed as a new one, a checker
  that always refuses, a checker that never refuses, a monotone level/capability claim, a
  zero-radius nearest negative, and an erased intermediate layer.
- **Nulls.** `0 / 200` random predicates with the matched pass rate are constant on every
  behavioural class — so class-constancy is evidence, not an artefact. `0 / 200` random
  three-way level labellings reproduce the measured one.
- **No-alarm case asserted.** The empty clause combination is empty, no behavioural class is
  split by `I2`, and the class count is 148.

## Reproduce

```
python3 -I -B  research/gmi-833-ah4-organization-ladder-v1/ah4_organization_ladder_v1.py
python3 -I -B  research/gmi-833-ah4-organization-ladder-v1/independent_oracle_v1.py
python3 -I -O -B research/gmi-833-ah4-organization-ladder-v1/test_ah4_organization_ladder_v1.py
```

Under 5 s each. Stdlib only.

## Files

`FREEZE_V1.md` (committed before any code) · `AH4_LADDER_THEOREMS_V1.md` (`AH4L-1` … `AH4L-6`) ·
`PARENT_LEDGER.md` · `RESULT_V1.json` · `ORACLE_RESULT_V1.json` · `TEST_RESULT_V1.json` ·
`MANIFEST_V1.json`.
