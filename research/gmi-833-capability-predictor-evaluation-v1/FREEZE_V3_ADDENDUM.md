# FREEZE_V3_ADDENDUM — second registered revival of the real-system row

Committed **before any V3 training run exists**. `FREEZE_V1.md`,
`FREEZE_V2_AMENDMENT.md`, `FROZEN_PREDICTIONS_V1.json`,
`FROZEN_PREDICTIONS_V2.json`, `heldout_universes_v1.py` and
`heldout_universes_v2.py` are all left byte-identical. `SIGMA_SYN` and
`SIGMA_ARCH` are untouched; their results stand.

## 1. The V2 outcome, and which pre-registered falsifiers fired

Two of the four falsifiers registered in `FREEZE_V2_AMENDMENT.md` section 5
fired on the V2 population:

| system | task | V2 registered law | measured | verdict |
|---|---|---|---:|---|
| `(GRU, 16, w=0)` | ones mod 3 | solved | 1981/2000 | **falsifier 2 fired** |
| `(GRU, 16, w=1)` | parity | not solved | 1 (exact) | **falsifier 3 fired** |
| `(GRU, 16, w=0)` | parity | solved | 1 (exact) | law held |
| `(GRU, 4, ·)`, all `MLP` | parity, mod 3 | not solved | ≤ 991/1000 | law held |

The V2 law is refuted. It is refuted in *both* directions by the same
population, which is what makes the diagnosis sharp rather than a matter of
degree.

## 2. Single-stage attribution

Still the registration law — but now specifically its **measurement predicate**,
not its structural clause. `solved := exact accuracy 1 on the protected split`
sits inside the optimization noise band of these systems: `(GRU,16,w=0)` missed
exact by 19 items out of 2000 on ones-mod-3, while `(GRU,16,w=1)` and
`(GRU,16,w=0)` both hit exact on parity and `(GRU,16,w=1)` reached 197/200 on
ones-mod-3. A predicate that flips on 19 items out of 2000 cannot be a function
of four structural coordinates, and the V2 "no skip shortcut" clause was an
artefact of reading one such flip as structure.

Not `F`: `F` is never consulted about training, and its soundness on
truthfully-registered worlds is reported separately and is unaffected. This is
the parent boundary **KP-1D** operating exactly as stated.

## 3. The lever, two parts, both registered here

1. **Band the measurement away from the threshold.** A task counts as solved iff
   exact accuracy `>= 99/100`, compared as an exact `Fraction`. This is the
   banded-classification discipline of `gmi-833-real-transition-receipts-v1`
   (#903), imported rather than invented.
2. **Move the structural threshold to width `>= 16`.** V1 and V2 together place
   the accumulator SGD actually finds above width 8, not at it:
   `(GRU,8,w=1)` fails parity, `(GRU,16,w=1)` solves it exactly.

Amended law:

```
T0 (last bit)  solved iff head 0 trained
T1 (parity)    solved iff head 1 trained and mech == GRU and size >= 16
T2 (ones mod 3) solved iff head 2 trained and mech == GRU and size >= 16
```

## 4. Re-tested on a third population, frozen before training

`SIGMA_REAL3` is 32 systems at widths **12 and 32** — widths that appear in
neither earlier population. It is disjoint from `SIGMA_1`, `SIGMA_SYN`,
`SIGMA_ARCH`, `SIGMA_REAL` and `SIGMA_REAL2` by `rho[3] ∈ {9,10}`, with 0
descriptor collisions against all five.

Frozen here: all 51,840 predictions (stream sha256 `92ca4ab905fa73b7…`),
10,816 point emissions, 7,376 abstentions, 33,648 inconsistent, every threshold
non-degenerate. The substantive prospective prediction is that **the GRU systems
at width 32 solve parity and ones-mod-3 (to the 99/100 band) and nothing else
does** — in particular width 12 does not, and the skip feature `w` is predicted
to be irrelevant.

## 5. Falsifiers

- any width-12 system reaching the band on parity or ones-mod-3;
- any `(GRU, 32, ·)` system failing to reach the band on either task with its
  head trained;
- any `MLP` reaching the band on either task;
- `w` turning out to matter again at width 32;
- any soundness violation on a truthfully-registered world.

## 6. The standing terminal if this is also refuted

`Test predictor on real trained systems` is then **left open**, with the
obstruction reported as a boundary earned by counterexample on the *bridge*:
exact-band solvability of these tasks by SGD-trained systems at this budget is
not a function of the registered structural coordinates. It will not be closed
on synthetic data, and `F`'s soundness on truthfully-registered real worlds will
be reported as the separate, positive fact that it is.
