# The cost pathology, quantified — and the one design change that would fix it

Date: 2026-09-13. Follows the root-cause diagnosis in
`GMI_B6_DEVELOPMENTAL_MORPHOGENESIS_RV_377_180_FREEZE.md`. States what the pathology is costing in this
campaign and names the lever, without applying it to anything already frozen.

## What it is costing right now

Measured processor time on units still running, every one with CPU time equal to elapsed time — they are
computing, not stalled:

| lane | unit | processor time |
|---|---|---|
| `RV-377-202` ablation | slowest still running | **76 083 s (21.1 h)** |
| `RV-377-202` ablation | second slowest | 71 007 s (19.7 h) |
| `RV-377-180` sources | `E_twin2 S2` | **42 082 s (11.7 h)**, of which > 11 h on its final 5 000 evaluations |

Against siblings that finished the *same* unit type in 1 135 s and 1 873 s. The ablation lane has been at
32 of 39 for hours; the B6 campaign is at 13 of 24 with three seed-2 twin arms unable to start until
`E_twin2` completes.

**So the blocked clause is `Z3`** — whether the structure-free twin reaches the coefficient cell on ≤ 1/3
seeds, which is what separates a residual belonging to this theory from one belonging to the warm-start
parents. It is blocked behind a unit whose remaining time cannot be estimated from its own history,
because its per-evaluation cost is still rising.

## Why waiting does not fix it

The mechanism is not load or contention. `morphgen.PARAM_CHOICES` draws `SEARCH`'s `budget` from
`(16, 64, 256, 2401)`; `SEARCH` runs an inner optimisation on every event of the charged lifecycle and
again under each of six interventions; and `core.Machine.op` charges every inner candidate. One draw
therefore spans **150×** in work at identical charged-evaluation cost. Selection then prefers the
largest value, because a bigger inner budget finds better programs and scores higher — three of the four
`SEARCH` nodes in the committed graphs carry 2401.

**The archive cannot resist this, because cost is not one of its descriptor axes.** The axes are carrier,
size and drift, so a cheap variant and a 150×-more-expensive variant of the same design land in the
**same cell** and compete on capability alone. The expensive one wins, the cheap one is discarded, and
the population ratchets toward maximum inner budget.

## The lever

**Add a cost axis to the archive descriptor.** With charged ops (or a bucketed log of them) as a fourth
axis, a cheap variant and an expensive variant occupy different cells and both survive. That is what
MAP-Elites is for — preserving stepping stones that lose on the objective — and the current descriptor
simply does not encode the dimension along which this population is degenerating.

Two weaker alternatives, recorded so the choice is visible rather than implied:

* **Cap `budget`.** Cheap and immediate, but it changes what the grammar can express, so every existing
  capability result would need re-reading against a smaller space.
* **Charge the search budget against the evaluation count.** Makes the 20 000 budget mean what people
  read it as, but penalises a machine for the parameter it was dealt rather than for its behaviour.

The descriptor change is preferable because it is **additive to the measurement and neutral to the
grammar**: no machine becomes unexpressible, no existing capability number moves, and the archive simply
stops throwing away the cheap half of each design.

## Not applied

No frozen protocol is changed by this note, and nothing in the running campaign is touched. Applying the
lever mid-campaign would make receipts inhomogeneous across arms, which is the same objection that kept
the genotype field out of `first_of_class` earlier today. It is registered as the named next change for a
successor run.
