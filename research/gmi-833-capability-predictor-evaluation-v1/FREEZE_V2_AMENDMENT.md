# FREEZE_V2_AMENDMENT — registered revival of the real-system row

This document and `FROZEN_PREDICTIONS_V2.json` are committed **before any V2
training run exists**. `FREEZE_V1.md` and `FROZEN_PREDICTIONS_V1.json` are left
byte-identical; `heldout_universes_v1.py` is not touched. `SIGMA_SYN` and
`SIGMA_ARCH` are unaffected and their V1 results stand unamended.

## 1. The V1 outcome that triggered this

The V1 registered law `real_solved_law` was a falsifiable prediction about real
training outcomes, and real training falsified it on **13 of 32** systems
(truthfulness 19/32). Measured at the registered budget:

| task | V1 registered law | measured |
|---|---|---|
| `T0` last bit | solved whenever head 0 is trained | solved on **8/8** configurations — law confirmed |
| `T1` parity | recurrent **or** width ≥ 8 | exact accuracy only for `(GRU, 8, w=0)` |
| `T2` ones mod 3 | width ≥ 8 | exact accuracy only for `(GRU, 8, w=0)` |

## 2. Single-stage attribution

The failing stage is the **registration law**, not the training budget and not
`F`.

- Not the budget: `(GRU, 8, w=0)` reached *exact* accuracy on both parity and
  ones-mod-3 within the registered 400 epochs, so the budget is demonstrably
  sufficient for a system with the right structure. The amendment therefore
  leaves the training protocol completely unchanged — it cannot be a budget
  rescue in disguise.
- Not `F`: `F` was never consulted about training. It reads
  `(M,E,R,H,D,U)` and emits a point only when the registered image is a
  singleton. Its soundness on the truthfully-registered worlds is reported
  separately and is unaffected by the bridge failure; this is precisely the
  parent boundary **KP-1D** — soundness is unconditional over *consistent*
  worlds, and truthful registration is the premise that cannot be removed.

Two further facts sharpen the diagnosis. First, recurrence alone is not enough:
`(GRU, 2, ·)` fails both tasks. Second, the last-symbol skip feature *hurts*:
`(GRU, 8, w=1)` fails parity that `(GRU, 8, w=0)` solves exactly — a shortcut
feature the optimizer prefers over the accumulator.

## 3. The lever

Amend the registration law to require recurrence **and** width **and** the
absence of the skip shortcut:

```
T1 / T2 solved  iff  head trained and mech == GRU and size >= 8 and w == 0
T0      solved  iff  head trained                               (unchanged)
```

## 4. Re-tested on a NEW frozen held-out set, not on the set that revealed it

`SIGMA_REAL2` is 32 systems at widths **4 and 16** — the V1 outcomes contain no
system of either width. It is disjoint from `SIGMA_1`, `SIGMA_SYN`,
`SIGMA_ARCH` and `SIGMA_REAL` by the separating coordinate `rho[3] ∈ {7,8}`, and
the exhaustive pairwise check reports 0 descriptor collisions against all four.

Frozen here, before training: all 51,840 predictions
(sha256 `fd015ae2e8b220f8…`), 11,360 point emissions and 8,848 abstentions, the
per-case order class (17,242 order-free / 30,610 conjunctive / 3,988
no-crossing), the curves, and the per-system registered solved-sets. The
substantive prospective prediction is that **only `(GRU, 16, w=0)` solves parity
or ones-mod-3**; every other system solves at most the last-bit task.

## 5. Falsifiers

- any system at width 4 solving parity or ones-mod-3 exactly;
- `(GRU, 16, w=0)` failing either task;
- `(GRU, 16, w=1)` solving either task;
- any soundness violation on a truthfully-registered world.

## 6. What a second failure would mean

If the amended law is also falsified, the honest conclusion is that exact-accuracy
solvability of these tasks by SGD-trained systems is not predictable from the
registered structural coordinates at this budget. That would be reported as a
boundary earned by counterexample on the *bridge*, with the real-system row left
open, and it would still leave `F`'s soundness on truthfully-registered worlds
intact. The row is not closed on synthetic data under any outcome.
