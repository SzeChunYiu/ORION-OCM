# RV-377-119 — GMI-DA12: the predicted object is `(family, grammar)`, not `family`

**A candidate repair of the predictive part.** The exploratory analysis is recorded as
exploratory; the prospective test is frozen below and has **not** been run.

## What the data says

`RV-377-117` left the question: does cost-minimising search produce *any* stable structure,
or is it noise? Decomposing what determines the winner's property vector, over 228 development
cells (8 non-resource axes; the two resource axes are excluded because `RV-377-117` measured
them as **unmeasured**, 94.7 % / 81.6 % `UNCLASSIFIED`):

| pairs drawn from | share a winner vector | lift over baseline |
|---|---|---|
| random (baseline) | 1.60 % | 1.00× |
| the same **cell** (`w1`…`w8`) | 0.60 % | **0.37×** |
| the same **grammar** | 4.46 % | 2.78× |
| the same **family** | 20.57 % | **12.83×** |
| the same **family AND grammar** | **75.44 %** | **47.04×** |

Three facts, in order of importance:

1. **The family genuinely determines the winner** — 12.8× baseline. Cost-minimisation is not
   noise and it is not grammar-chasing. GMI's core intuition, that the obligation selects an
   architecture, is **supported**.
2. **The grammar co-determines it.** Fixing family alone gives 20.6 %; fixing family *and*
   grammar gives 75.4 %. Most of the residual variance is the grammar.
3. **The cell determines nothing** (0.37×, *below* baseline). Width is not a predictor.

## Why the predictive part was failing

Fit the best possible key to the development data and ask what it could score:

```
CEILING, key indexed by (family, grammar) : 86.4 % of cells
CEILING, key indexed by family alone      : 32.9 % of cells
```

**GMI's answer key is indexed by family alone.** So GMI's predictive form is capped at
**32.9 %** *by construction* — before any question of whether its particular labels are right.
A grammar-free key cannot describe a grammar-dependent minimiser; it can agree with at most one
grammar and must disagree with the other two.

> **The 0-of-264 result is not principally a wrong-labels failure. It is a
> wrong-type-of-object failure.** The theory predicts `family → property vector`. The world
> (this world, at registered scope) supplies `(family, grammar) → property vector`.

This also explains DG-11 exactly. The grammar is **verdict-inert** — all three grammars agree
on the verdict for 88 of 88 combos — while being **winner-determining**. The grammar does not
change *whether* you hit the frozen target; it changes *which* cheap machine you find instead.
Those two facts looked contradictory and are now one fact.

And it explains the 1.67× independence ratio: a misspecified key produces marginals that are
individually weak and jointly uninformative, which is what was measured.

## The rule-40 analogue, which corrects an earlier overstatement

Per-axis agreement against a **majority-class control** (predict the modal target value for
every cell), rather than against nothing:

| axis | GMI | constant | Δ | |
|---|---|---|---|---|
| `verifier_gated` | 80.3 % | 64.5 % | **+15.8** | beats |
| `serve_iterations` | 50.0 % | 36.0 % | **+14.0** | beats |
| `retrieval` | 50.0 % | 38.6 % | **+11.4** | beats |
| `routing` | 55.3 % | 50.0 % | +5.3 | beats |
| `external_authority` | 81.6 % | 76.3 % | +5.3 | beats |
| `update_locality` | 28.1 % | 26.3 % | +1.8 | beats, marginally |
| `sharing` | 50.0 % | 49.1 % | +0.9 | beats, marginally |
| `serve_scales_with` | 0.4 % | 0.0 % | +0.4 | both ≈ 0 |
| `state_scales_with` | 0.9 % | 1.8 % | **−0.9** | **LOSES** |
| `stochastic_serve` | 61.0 % | 73.2 % | **−12.3** | **LOSES badly** |

> **Correction to `RV-377-117`.** I wrote there that GMI gets `external_authority` right 82 % of
> the time, presenting it as the theory's best axis. Against the constant control it is worth
> only **+5.3 points** — most of that 82 % is the base rate. The genuine signal is concentrated
> in `verifier_gated` (+15.8), `serve_iterations` (+14.0) and `retrieval` (+11.4). And GMI
> **loses to a constant** on `stochastic_serve` by 12.3 points.

## GMI-DA12, stated

> **GMI-DA12.** The cost-minimal architecture selected by an obligation is a function of the
> obligation **and the generative grammar jointly**. A property-vector prediction that does not
> name its grammar is not merely imprecise — it is a prediction about the wrong object, and is
> capped at the fraction of cells its single implicit grammar covers.

## The prospective test — frozen, NOT run

The 86.4 % above is a **fitted ceiling on the data that generated the hypothesis**. It is not a
result and is not claimed. `GMI_GRAMMAR_INDEXED_KEY_RV_377_119.json` records the key fitted on
the development sweep, marked
`FITTED_ON_DEVELOPMENT_DATA__NOT_A_RESULT__FOR_PROSPECTIVE_SCORING_ONLY`.

It will be scored against **fresh, untouched data**: the beacon-gated protected LUNARC run at
budget 10⁶ (unit `U-A001`, dispatched, not yet returned), whose seeds depend on future public
entropy this session cannot influence.

| id | prediction | falsifier |
|----|-----------|-----------|
| Z1 | On the protected run, within-(family, grammar) winner agreement is **> 50 %**, and at least **3× the** within-family-alone agreement. | ratio below 3×, or agreement ≤ 50 % |
| Z2 | The frozen grammar-indexed key predicts the protected winners on **> 32.9 %** of cells — strictly above the family-only ceiling. | ≤ 32.9 % |
| Z3 | The cell axis remains non-predictive (lift < 1.5×). | cell lift ≥ 1.5× |
| Z4 | GMI's **original** family-only key still scores **0 %** on the ten-axis conjunction. | any cell matches all ten |

**Z2 is the one that matters.** If the grammar-indexed key beats 32.9 % out of sample, the
predictive part of GMI is repairable and the repair is named. If it does not, then the
structure seen here was overfitting on 228 cells and GMI-DA12 is withdrawn.

## What this does not claim

The two resource axes are excluded, not solved — `RV-377-117`'s `UNCLASSIFIED` finding stands
and the reference table still needs widening. Nothing here rescues the ten-axis conjunction:
even the fitted grammar-indexed ceiling is over **eight** axes. And a theory that must name its
grammar is a weaker theory than one that does not — GMI-DA12 is a **repair of the claim's type**,
not a restoration of its original strength.
