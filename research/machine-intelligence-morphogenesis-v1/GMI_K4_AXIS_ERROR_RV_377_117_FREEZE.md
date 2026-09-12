# RV-377-117 — FREEZE: why the predictive part fails, localized to an axis

Frozen BEFORE the run. Outcomes appended only.

## The question

`RV-377-107`/`RV-377-109` established that the K4 property prediction fails structurally:
**0 of 264** cells recover their frozen target vector, invariantly under a tenfold budget
increase, with the discrepancy widening as compute grows.

"It fails" is not a diagnosis. Four causes are consistent with that result and they are
**distinguishable by evidence**:

| | hypothesis | signature |
|---|---|---|
| **H1** | the **cost model** is mispriced — the true minimiser differs from the predicted one because a cost channel is wrong | winners are coherent and differ from targets systematically on the axes that channel touches |
| **H2** | the **target vectors** are wrong — the hand assignment of property vectors to the 22 families is mistaken | winners are coherent, diverse, and family-specific, but offset from the key |
| **H3** | the **obligation** is wrong — it does not capture what the family is for, so its cheapest solution is not the family | winners collapse: many families share one winner vector |
| **H4** | **GMI is wrong** — no cost-minimisation principle picks out real architectures | winners are incoherent: high diversity, no axis predicted better than chance |

H1 and H2 are **repairable**. H3 is repairable but expensive. H4 is not repairable.

## Method

Re-run the full 264-cell grid at budget 20 000, capturing for every cell the **frozen target
property vector** and the **winner's measured property vector** over all 10 registered axes
(`state_scales_with`, `serve_scales_with`, `update_locality`, `routing`, `sharing`,
`retrieval`, `serve_iterations`, `stochastic_serve`, `verifier_gated`,
`external_authority`), then compute per-axis agreement and winner-vector diversity.

`name_key` is popped before the freeze reaches the engine, as always.

## Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| Y1 | **The disagreement is CONCENTRATED** — at least one axis disagrees on > 80 % of cells while at least one other agrees on > 80 %. | disagreement is uniform across axes |
| Y2 | **The winners collapse** — the 264 winners realize **fewer than 22** distinct property vectors, i.e. fewer than the number of families the obligation is supposed to separate. | ≥ 22 distinct winner vectors |
| Y3 | The single most-disagreeing axis is one of the two **resource** axes (`state_scales_with`, `serve_scales_with`). | the worst axis is a non-resource one |
| Y4 | **At least one axis is predicted essentially perfectly** (> 90 % agreement) — some of GMI's structure is right. | no axis exceeds 90 % |

**Y2 is the diagnostic that separates the hypotheses.** If the winners collapse onto very
few vectors, the obligation set does not discriminate families (H3) and the answer key was
never reachable. If the winners are diverse but wrong, the cost model or the key is at fault
(H1/H2) and the repair is local.

**Y4 is the one that decides whether the predictive part is repairable at all.** If no axis
beats 90 % — if nothing GMI says about these families is recovered — that is H4, and the
predictive claim does not have a local repair.

Y4 is stated as a prediction **for** GMI and is the one I most expect to be wrong.

## What a positive outcome would license

If Y1 and Y4 both hold, the failure is localized: some axes are right, one or two are wrong,
and the next step is to determine whether the wrong axes are mispriced (H1) or mislabelled
(H2) — both of which have concrete repairs that could turn 0/264 into a non-zero count.

Nothing is claimed here beyond the measurement.
