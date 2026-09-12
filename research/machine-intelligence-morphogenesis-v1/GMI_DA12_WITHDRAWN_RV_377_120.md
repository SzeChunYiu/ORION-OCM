# RV-377-120 — GMI-DA12 is WITHDRAWN, and what killed it found something worse

`GMI-DA12` was proposed in `RV-377-119` two hours ago: *the predicted object is
`(family, grammar)`, not `family`*. It was fitted on 228 development cells at seed
`0x4B345035`, with the fitted ceiling explicitly marked
`FITTED_ON_DEVELOPMENT_DATA__NOT_A_RESULT__FOR_PROSPECTIVE_SCORING_ONLY` and four
predictions frozen for out-of-sample scoring.

It has now been scored on a fresh seed. **It fails, and the manner of its failure is the
finding.**

## The out-of-sample result

Fresh seed `0x5A5A1234`, same 264 cells, 228 usable, 252 s.

| prediction | outcome |
|---|---|
| Z1 — within-(family,grammar) agreement > 50 % and ≥ 3× family-alone | **CONFIRMED** — 71.9 %, ratio 3.29× |
| Z3 — cell remains non-predictive | **CONFIRMED** — 0.59× lift |
| **Z2 — the frozen key beats the 32.9 % family-only ceiling** | **FALSIFIED — 0/216 = 0.0 %** |
| Z4 — GMI's original family-only key still 0 % on ten axes | **CONFIRMED** — 0/228 |

The decomposition **replicated almost exactly** — baseline 2.01 %, family 10.9×, grammar
2.67×, family+grammar **35.9×**. And the key fitted on that identical structure predicted
**nothing at all**: zero of 216 cells.

A structure that replicates while its fitted key predicts zero is not a structure about the
world. That contradiction has one resolution, and it is checkable.

## What killed it

| comparison | agreement |
|---|---|
| cross-seed, same `(family, grammar, cell)` | **1 / 216 = 0.5 %** |
| cross-seed, modal winner per `(family, grammar)` | **0 / 54 = 0.0 %** |
| within seed A, `(family,grammar)` groups with one winner across their 4 cells | 33 / 57 |
| within seed B, same | 30 / 57 |

Cross-seed agreement is **0.5 %**, *below* the 2.01 % baseline. Not one of the 54
`(family, grammar)` pairs keeps its modal winner when the seed changes.

> **The 47× lift was an artifact of the seed being held constant.** The four cells inside
> each `(family, grammar)` group share a seed. They agree because they are the same search,
> not because they are the same obligation. Change the seed and everything changes.

I built the grouping, measured a 47× lift, and read it as evidence of a law about
obligations. It was evidence that a deterministic search is deterministic.

## The actual finding, which is worse than the one it replaces

> **At budget 20 000, the recovered architecture is a function of the search trajectory, not
> of the obligation, the family, or the grammar.** The search does not converge. It finds *a*
> cheap machine, and which one it finds is decided by the random seed.

This explains everything previously observed, without any further hypothesis:

* **0 / 264 target-vector matches** — the search was never converging on anything to match.
* **76 distinct winner vectors across 22 families** — that is trajectory diversity, not
  family diversity.
* **the 1.67× independence ratio** (`RV-377-117`) — near-independent marginals are what noise
  produces.
* **verdicts invariant under a 10× budget while winner costs improved on 194/264 cells**
  (`RV-377-109`) — cheaper machines found, still not the same machines.
* **`GMI-DA12` failing out of sample while its structure replicated** — the structure is the
  seed, and the seed does not transfer.

## Consequence for the predictive claim

**A property-vector prediction is not merely wrong at this scope — it is not well-posed.**
Predicting which architecture cost-minimisation selects presupposes that cost-minimisation
selects one. At budget 20 000 it does not.

`GMI-DA12` is **WITHDRAWN**. The grammar is not a missing coordinate. No coordinate of that
kind can help, because the quantity being predicted is not a function of the inputs.

The two *other* diagnoses on record are untouched by this and remain live: the Codex lane's
`target_information_source` (F1) is a claim about what the evaluator cannot distinguish, and
its F3 (the vector is not frontier-complete) is a claim about sufficiency — neither asserts
convergence. And `m2p4`'s `C2_NOT_REPLICATED_IN_SECOND_GRAMMAR` remains a real preregistered
negative on its own terms.

## The right question, and it is testable

The question is no longer *"does GMI's key match?"* It is:

> **Does the search converge at all as budget grows?**

Operationally: does **cross-seed** agreement at fixed `(family, grammar, cell)` rise above
baseline as budget increases? Cross-seed agreement is the only measure that can distinguish
convergence from trajectory noise, and no previous run in this programme measured it.

* If cross-seed agreement rises with budget, the search is converging, a property-vector
  prediction becomes well-posed at sufficient budget, and the protected 10⁶ LUNARC run is the
  test of whether 10⁶ is sufficient.
* If it stays at baseline, **K4 as designed can never be predictive at any budget**, and the
  programme needs a different selection principle rather than a better key.

This reframes the dispatched LUNARC unit `U-A001`. Its value is no longer scoring a key; it is
measuring convergence. That is a strictly more informative use of the same run, and it costs
nothing to re-read it that way because the receipts already record the winners.

Registered as `RV-377-121`, frozen separately, and **not** claimed here.

## On the protocol

This error was made and caught inside two hours, by a test I froze against my own hypothesis
before running it. The freeze said: *"If it does not, then the structure seen here was
overfitting on 228 cells and GMI-DA12 is withdrawn."* It did not, and it is.

`RV-377-119` is **not** deleted. It stands in the corpus with this withdrawal recorded against
it, as the corpus requires — including its own correct warning that the 86.4 % was a fitted
ceiling and not a result.
