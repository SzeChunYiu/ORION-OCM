# AH7 — the data axis, isolated (START HERE)

The sibling result already on `main` shows requirements and pricing move the preferred form.
This shows **data** does, with the space, the pricing, the requirement and the horizon all held
fixed — and fingerprinted, so that "held fixed" is checkable rather than asserted.

## Headline numbers (exact integer comparison; no scalarization anywhere)

| quantity | value |
|---|---|
| possibility space, identical for every dataset | `260` systems (4 cell-free + 256 one-cell) |
| fixed-input fingerprint across all datasets | identical, `38c9ef94…` |
| registered datasets | `20` — five target behaviours × four coverages |
| distinct preferred sets | `7` |
| dataset pairs with disjoint answers | `162` of 190; `10` of them share one target behaviour |
| target behaviours whose answer moves on **coverage alone** | `2` — delay-by-one and running parity |
| answer is a function of the data (reordering) | `0` failures |
| narrowing is monotone under extension | `0` failures in `10` checks |
| informative null: realizable dataset pairs sharing an answer | `18 / 200`, across `93` distinct answers |

## The sharp case

For the **delay-by-one** behaviour, with the target fixed and only the observed words changing:

| observed words | preferred system |
|---|---|
| the two length-one words | `S000`, the constant-zero cell-free system |
| all words of length at most two | `M051` |
| the eight length-three words | `M043` |

Running parity does the same: `S001`, then `M066`, then `M064`. Same space, same price, same
requirement, same horizon — three different preferred forms, from data alone.

## Two measurements published although they do not support the row

- **Scalarizing the price changes nothing here.** Collapsing the four raw coordinates to their
  sum moves the answer on `0 / 20` datasets; the sum-minimal set never differs from the
  non-domination front. The preferred set is a singleton for every registered dataset. The
  no-scalarization rule is kept because it is the right general discipline, not because it bites
  at this scope.
- **An arbitrary-label null is uninformative here.** `200 / 200` datasets built from random
  outputs are consistent with no system at all, so such a null would compare empty answers with
  empty answers. The realizable null is the one that carries the finding.

## Evidence

- **2 materially independent routes.** Route A filters by re-running each system per
  observation and takes the front by all-pairs domination. Route B imports nothing from A: it
  precomputes one full response table per system and restricts it, and takes the front by a
  sort-and-sweep skyline. **13 published quantities and all 20 per-dataset answers agree, 0
  disagreements.**
- **10 hostiles, all detected, each with a clean control**: first-consistent instead of the
  front (differs on 16 of 20), a prefix-only consistency filter (admits more on 15 of 20), the
  answer removed from the space (moves all 20), one observation dropped (moves 3), a space that
  is not fixed (fingerprint differs), the empty dataset (admits all 260), a filter that breaks
  monotone narrowing, an arbitrary-label null (96 of 100 unrealizable), a single coverage (no
  within-behaviour move remains), and an order-sensitive rule (differs on 16 of 20).
- **No-alarm asserted**: zero order-invariance failures, zero monotone failures, stable
  fingerprint.

## Reproduce

```
python3 -I -B  research/gmi-833-ah7-data-varied-choice-v1/ah7_data_varied_choice_v1.py
python3 -I -B  research/gmi-833-ah7-data-varied-choice-v1/independent_oracle_v1.py
python3 -I -O -B research/gmi-833-ah7-data-varied-choice-v1/test_ah7_data_varied_choice_v1.py
```

Under 2 s each. Stdlib only.

## Files

`FREEZE_V1.md` (committed before any code) · `AH7_DATA_AXIS_THEOREMS_V1.md` (`AH7D-1` … `AH7D-3`)
· `PARENT_LEDGER.md` · `RESULT_V1.json` · `ORACLE_RESULT_V1.json` · `TEST_RESULT_V1.json` ·
`MANIFEST_V1.json`.
