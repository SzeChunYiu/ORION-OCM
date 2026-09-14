# The four continual-learning regimes, derived as moves on one frontier (B19)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/continual_regimes_witness.py`.
Receipt: `microscopes/results/STAGE_CONTINUAL_REGIMES_V1.json`.
Reproduced in CI by `test_gmi_derivation_witness_reproduction.py`.

`GMI_INTERFERENCE_STABILITY_PLASTICITY_V1.md` derived the stability-plasticity
frontier from CSR-1 alone and closed by noting that any remedy can only work by
changing one of three inputs: raise capacity, raise redundancy, or reduce what
must still be told apart.

The continual-learning literature names four method families. They are not four
ideas. They are those three moves, plus the one that changes nothing and pays
to hold the line.

| regime | what it does to the frontier |
|---|---|
| **expand** | buys capacity |
| **regularize** | reserves capacity for the old and accepts the lost distinctions |
| **modularize** | gives each task its own store, so nothing must be told apart *across* tasks |
| **replay** | changes none of the three, and pays to re-separate what is already held |

Nothing about gradients, weights or forgetting curves is assumed.

## Two failure modes, found by a gate refusing the first version

A first version of the witness could not make **replay** win anywhere, and the
non-vacuity gate refused it. That was not a finding but a missing ingredient.
With capacity as the only constraint, replay has no job: whenever it is legal —
that is, whenever what must be separated still fits — the capacity remedies are
already free.

Replay answers a *different* failure. On a substrate where writing new content
degrades what is already held, distinctions are lost **even when capacity is
ample**, and only re-presenting them restores the loss. So the ledger carries
two independent failure modes:

```
CAPACITY    more must be told apart than there are states for
OVERWRITE   the substrate degrades held distinctions as it writes new ones
```

## Each regime is the cheapest somewhere

| price regime | winner | why |
|---|---|---|
| cheap capacity | **expand** | capacity costs 1, so buy it |
| dear capacity | **regularize** | capacity costs 30; accept the loss instead |
| cheap storage | **modularize** | stores cost ½; isolate rather than share |
| interfering substrate, ample capacity | **replay** | nothing to expand; the damage is overwrite |

All four win somewhere and none wins everywhere. The witness aborts if any
regime never wins — a method that never wins is not a regime, it is a mistake.

## Replay is specific to the failure it repairs

The sharpest control. Take the price regime where replay wins and switch the
substrate to an addressed one — `overwrite: 0` — changing nothing else:

| substrate | winner | replay cost | expand cost |
|---|---|---:|---:|
| interfering (overwrite ½) | **replay** | 15/4 | 30 |
| addressed (overwrite 0) | **expand** | 15/4 | **0** |

Replay's own cost is unchanged at 15/4. What changed is that there is no longer
any damage for it to repair. Across the whole table, replay wins in **zero**
rows where overwrite is zero.

> **Capacity-driven loss takes a capacity remedy; overwrite-driven loss takes
> replay. Pairing the wrong remedy with the failure is strictly wasteful.**

That is a testable claim about which method to reach for, rather than a
preference among them.

## The crossover is a price ratio, not a task property

Holding the task sequence completely fixed and sweeping only the price of
capacity:

| capacity price | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| winner | expand | expand | expand | expand | **modularize** | modularize |

The winner changes between capacity price 8 and 16. **Nothing about the tasks
changed across that boundary.**

> Which continual-learning method is correct is a statement about prices, not
> about the task sequence.

This predicts that a method comparison run on one hardware and cost regime does
not transfer to another, and that reported method rankings should move with the
price of memory rather than with the benchmark.

## Redundancy dissolves the problem for three regimes at once

| shared | must separate | expand | regularize | modularize |
|---:|---:|---:|---:|---:|
| 0 | 16 | 32 | 160 | 64 |
| 2 | 10 | 8 | 40 | 64 |
| 3 | 7 | **0** | **0** | 64 |
| 4 | 4 | **0** | **0** | 64 |

At full redundancy the required quotient stops growing with the number of
tasks, and three of the four regimes cost nothing at all. There is no continual
learning *problem* to solve.

Only **modularize** still pays — for stores and routing it did not need.

> **A continual-learning method can be strictly harmful when the tasks already
> share structure.** Isolation in particular buys separation that was never
> required, and charges for it.

## Scope

- Prices are registered constants; the *orderings* they produce are the result,
  not the magnitudes. Every crossover moves with the prices by construction —
  that is the claim, not a caveat on it.
- `overwrite` is a single scalar damage rate. A substrate with structured
  interference (some distinctions damaged more than others) is not modelled.
- Replay is charged as re-presenting everything held. Selective replay of a
  chosen subset would cost less, and choosing that subset is itself work that
  is not charged here.
- Four regimes are priced. A hybrid that expands *and* replays is legal in this
  ledger and is not evaluated.
- No claim is made about any published method's empirical ranking; this derives
  which *kind* of remedy the accounting selects.

**Falsifier.** Exhibit a price regime and ecology where replay is cheapest with
`overwrite` zero — that would show replay is not specific to the failure it
repairs. Or exhibit a regime that never wins anywhere in a sweep of prices,
which would show it is not a distinct regime at all.
