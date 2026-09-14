# When a gradient update law pays, and why the corpus's measurement is about the substrate (B4, learning half)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/update_law_witness.py`.
Receipt: `microscopes/results/STAGE_UPDATE_LAW_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

`GMI_NEUTRAL_EMERGENCE_SELECTION_V1.md` measured gradient learning under
neutral selection and found it **depleted**: `GRAD` present in 10.4 % of
proposed genotypes and 5.0 % of survivors, **0.48×, selected against.**

That measurement is real and is not disputed here. What this document does is
ask what condition a gradient law needs, and then test two explanations for the
depletion — **one of which is mine, and is refused.**

An update law is retained machinery. Like everything else in this corpus it
must pay for itself. Nothing about neural networks is assumed: an update law is
a rule for choosing the next parameter setting given what has been seen.

## What each law buys, and where it can buy anything

Evaluations to reach the optimum. `none` means the law cannot get there at all
— not that it is slow.

| landscape | `d` | random | local | gradient |
|---|---:|---:|---:|---:|
| smooth | 3 | 65/2 | 34 | **3** |
| smooth | 4 | 257/2 | 57 | **3** |
| rough (needle) | 3 | 65/2 | **none** | **none** |
| rough (needle) | 4 | 257/2 | **none** | **none** |

> A gradient law is **not a better search**. It is a search that exchanges
> generality for a landscape assumption — and where the assumption fails it
> does not degrade gracefully, it stops working. Uniform search still finds the
> needle; the gradient law has no slope to follow and returns nothing.

## The break-even

A gradient evaluation costs 3 against 1, because slopes must be computed and
carried. Charged cost = evaluations × price:

| `d` | random | local | gradient | cheapest |
|---:|---:|---:|---:|---|
| 2 | **17/2** | 17 | 9 | random |
| 3 | 65/2 | 34 | **9** | **gradient** |
| 6 | 4097/2 | 121 | **9** | gradient |

The premium is fixed per evaluation while the saving grows with the number of
parameters, so a gradient law pays only once there are enough parameters to
amortize it. **That is PVR-3 again**, with the update law as the retained
machinery — the same break-even that governs consolidation, chunking, teaching,
culture, concept formation and retrieval.

## Which explanation of the 0.48× survives

**Hypothesis A — the horizon is too short.** The registered ecologies present
sixteen inputs over sixteen events, so sixteen is the whole update budget.

| `d` | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| gradient evaluations | 3 | 3 | 3 | 3 | 3 |
| fits in 16 | ✅ | ✅ | ✅ | ✅ | ✅ |

> **Refuted.** The gradient law needs three evaluations at every dimension
> tested against a budget of sixteen. The horizon is ample. This was my
> hypothesis and the witness refuses it.

**Hypothesis B — the substrate carries no slope.** A gradient law needs a path
from the parameter to the error and back. Where there is none it returns
`none`, at every dimension.

**Survives** — and the corpus's own numbers point the same way. Of 34
gradient-bearing archive cells, **33 wire the parameter block into the update
law and only 8 route it back out, none admissible.** A parameter that goes in
and does not come back is a gradient primitive with no return path:
structurally the same object this witness returns `none` for.

> **The depletion is consistent with a gradient primitive being *inert* in a
> discrete substrate, not with gradient learning being a poor strategy.** Those
> are different claims, and only the first is supported.

The named repair is an ecology with a slope-bearing parameter path — not a
longer horizon and not a different search. That is a gap in the **ecology set**,
the same kind the corpus already recorded for attention under item 5.

## What this does and does not close

**Closes**: what differentiable specialization assumes (a landscape where local
slope predicts improvement); when a gradient law beats local and random search
(above the parameter-count break-even, and only on a smooth landscape); and why
the measured depletion is not evidence against gradient learning.

**Does not close**: reverse-mode credit assignment is *not* derived here. This
witness reads slopes directly rather than propagating them, so it says nothing
about why reverse mode is the efficient way to obtain them. Neutral recovery of
an MLP morphology is also not attempted — that needs the slope-bearing ecology
this document names as missing.

**Scope.** Two landscapes and three laws, `K = 4` values per parameter, `d ≤ 6`.
The per-evaluation prices (3 against 1) are registered constants: the *ordering*
and the existence of a break-even are the result, the crossover's exact location
is not. The "rough" landscape is a needle, the extreme case; intermediate
roughness is not modelled. The corpus's 33-of-34 wiring figure is quoted from
`GMI_NEUTRAL_EMERGENCE_SELECTION_V1.md` and is corroborating evidence, not
something re-measured here.

**Falsifier.** Exhibit a gradient law that reaches the optimum on a needle
landscape; or a smooth ecology with a slope-bearing parameter path where `GRAD`
is still depleted under neutral selection — that second one would move the
explanation back from the substrate to the strategy.
