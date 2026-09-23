# Z3 freeze amendment 2 — `T2` and `T4` are made exhaustive, as the freeze said

Committed **before** the receipt carrying the exhaustive numbers.

## What was wrong

`FREEZE_V1.md` states that invariance verification is

> exhaustive over `60` worlds x `200` seeded `T1` permutations, plus `T2`, `T3`
> and `T4` applied to the **whole universe**.

`T3` was applied to the whole universe. `T2` was applied to a strided sample of
`4472` machines and `T4` to `400` random ones. The receipt reported the sample
sizes honestly, but nothing reconciled them against the freeze text, which is the
same freeze-versus-run mismatch class recorded for Z7's grid count.

## The repair

Rather than narrow the freeze, the run is widened to match it. A single extra
pass computes `sigma` at start state `1` for all `65536` one-state-bit machines,
after which both checks become lookups:

- `T2`: for every machine `u`, `sigma(T2 u, start=1) == sigma(u, start=0)`;
- `T4 = T2 . T3`: for every machine `u`,
  `sigma(T2(T3 u), start=1) == sigma(u, start=0)`.

`T1` contributes no `sigma` change by construction and is already covered
exhaustively by the multiset check over `200` permutations.

Both are now whole-universe: `65536` machines each, `0` breaks, reported as
`machines_checked` rather than as a sample size. The gate is unchanged; only its
coverage is.

## Nothing else in the freeze changes

The claim ceiling, the rows, the registry, the hostiles, the null and its
revival, and the forbidden promotions are unchanged.
