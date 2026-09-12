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

---

# RV-377-117 — ADJUDICATION (appended; nothing frozen above was edited)

264 cells at budget 20 000; **228 usable** (36 are `INCONCLUSIVE_GRAMMAR` and carry no measured
vector); 228 s.

## Per-axis agreement

| axis | agree | of | % |
|---|---|---|---|
| `state_scales_with` | 2 | 228 | **0.9 %** |
| `serve_scales_with` | 1 | 228 | **0.4 %** |
| `update_locality` | 64 | 228 | 28.1 % |
| `sharing` | 114 | 228 | 50.0 % |
| `retrieval` | 114 | 228 | 50.0 % |
| `serve_iterations` | 114 | 228 | 50.0 % |
| `routing` | 126 | 228 | 55.3 % |
| `stochastic_serve` | 139 | 228 | 61.0 % |
| `verifier_gated` | 183 | 228 | 80.3 % |
| `external_authority` | 186 | 228 | **81.6 %** |

| id | outcome |
|----|---------|
| Y1 | **CONFIRMED** — sharply concentrated: worst 0.4 %, best 81.6 % |
| Y2 | **FALSIFIED** — **76** distinct winner vectors against 22 families; winners are diverse, not collapsed |
| Y3 | **CONFIRMED** — worst axis is `serve_scales_with`, a resource axis |
| Y4 | **FALSIFIED** — best axis is 81.6 %, below the 90 % bar |

## H3 is eliminated

Y2 falsified rules out the obligation-collapse hypothesis. **76 > 22**: the search produces
more distinct property vectors than there are families, so the obligation set does discriminate
and the answer key was not unreachable by construction. That was the cheapest available excuse
and it does not hold.

## A real, repairable instrument defect — found, and then found not to be the cause

The two resource axes are not merely wrong. They are **unmeasured**:

```
state_scales_with : UNCLASSIFIED_STATE_LAW on 216/228 = 94.7 %
serve_scales_with : UNCLASSIFIED_SERVE_LAW on 186/228 = 81.6 %
```

`UNCLASSIFIED_*_LAW` is `measure_state_law`/`measure_serve_law`'s fallback when a candidate's
integer resource expression matches **none** of the preregistered reference laws. The DG-10 fix
— recover the label by executing the expression rather than copying it from the token — is
correct in design and I verified its panel separates all 22 state and all 21 serve laws
(`RV-377-106`). But **the search's expression space is far larger than the 25-law reference
table**, so nearly every candidate lands outside it and the axis cannot agree with anything.

Two of ten axes are therefore structurally incapable of matching. That is a genuine defect with
a concrete repair: either widen the reference table to cover the generator's expression space,
or restrict the generator to expressions the table classifies.

**It is not why K4 fails.** Removing both broken axes entirely and requiring only the remaining
eight:

```
cells matching ALL EIGHT non-resource axes : 3/228 = 1.3 %
cells matching all ten axes                : 0/228
```

> **The instrument repair moves the result from 0/228 to 3/228. The predictive failure survives
> it.** I will not claim the repair rescues the prediction, and the record says so before anyone
> can read it that way.

## The axes carry no joint structure

If the eight non-resource axes were statistically independent, the conjunctive match rate would
be the product of the marginals:

```
product of the 8 marginals = 0.776 %
observed conjunctive match = 1.3 %
ratio observed / independent = 1.67x
```

A factor of 1.67 over pure independence, on 228 cells. GMI's property vector is therefore
**barely more than the product of its axes** — the theory is not capturing joint structure among
the properties it names, which is precisely what a predictive theory of architecture would have
to do. Getting `external_authority` right 82 % of the time while getting the ten-way conjunction
right 0 % of the time is the signature of ten weakly-informative marginals, not of a model of
architecture.

## Hypotheses, adjudicated

| | hypothesis | verdict |
|---|---|---|
| H1 | cost model / instrument mispriced | **PARTIALLY TRUE and repairable** — the resource-law measurement is genuinely broken (94.7 % / 81.6 % unclassified). Repairing it yields 3/228, not a passing rate. |
| H2 | target vectors wrong | **NOT SUPPORTED as a whole-key error** — two axes are predicted at ~81 %, which a wrong key would not produce. A per-axis key error on `update_locality` (28.1 %, the worst non-resource axis) remains live. |
| H3 | obligation wrong, winners collapse | **ELIMINATED** — 76 distinct winner vectors > 22 families. |
| H4 | GMI is wrong | **NOT ELIMINATED.** Y4 falsified: no axis is predicted essentially perfectly. The conjunction is at 1.67x independence. |

## What would make the predictive part work — concrete and ordered

1. **Repair the resource-law measurement.** Widen the reference table or restrict the generator.
   Necessary, demonstrably insufficient alone (0 → 3 of 228). *Registered, not run.*
2. **Audit `update_locality`.** At 28.1 % it is the worst non-resource axis and is plausibly a
   key error (H2) rather than a theory error. A three-valued axis predicted at 28 % is worse than
   naming the mode. *Registered, not run.*
3. **Decide whether GMI's claim is conjunctive at all.** Requiring all ten axes simultaneously is
   a very demanding criterion, and the 1.67x independence ratio says the conjunction carries
   almost no information beyond the marginals. Either GMI must predict joint structure — and
   currently it does not — or the claim should be restated per-axis, in which case
   `external_authority` and `verifier_gated` at ~81 % are real results and the ten-way vector is
   not the right object. **This is a question about what GMI claims, not about the instrument,
   and it cannot be settled by running anything.**

Item 3 is the one that matters. The measurement is fixable; the independence ratio is the finding.
