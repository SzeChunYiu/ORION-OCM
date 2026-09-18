# gmi-833-ae-ae7-prediction-to-control-v1

Section AE7, all seven rows: what changes when a representation has to **act**
rather than merely **predict**.

**Scope.** `8` latent states, uniform exact prior `1/8`, every one of the
`Bell(8) = 4140` sensors (set partitions), `6` registered prediction targets,
`4` registered utilities over `4` actions, a `33`-point exact rational sensing
price ladder. `Fraction` and `int` only — the test rejects a float literal or a
logarithm anywhere in either route.

| result | numbers |
|---|---|
| `PC-1` same predictive, different control | **10,980** sensor pairs with identical predictive profiles and different control value; **712** distinct profiles over 4140 sensors; named witness `1` vs `1/2`; the contrast case reports exactly **0** |
| `PC-2` control sufficiency | **225 / 225 / 208 / 221** control-sufficient sensors; coarsest unique for two utilities, **3** and **8** minimal elements for the others; criterion matches the exact value function with **0** mismatches |
| `PC-2` Helly failure | **1** pairwise-compatible triple `(0,1,2)` with empty common optimum — mergeability is not a pairwise property |
| `PC-3` parent subtraction | **5** crosswalk entries, every one with a DOI; **3** `PARENT_SUFFICIENT` terminals recorded as successes |
| `PC-4` value of information | **163,754** comparable pairs; **26,790** with `VoI = 0`, **136,964** positive; **71** exact break-even prices in `[0, 9/64]`; the probe gives strict win below, exact tie **at**, strict loss above |
| `PC-5` free merges | **12 / 12 / 13 / 14** free state pairs against **16 / 16 / 15 / 14** costly ones |
| `PC-6` control-relevant, predictively invisible | **4** pairs invisible to all 6 targets; **4 of 4** control-relevant under the hidden-coordinate utility (`V: 1 → 7/8`), **0** under the visible one |
| `PC-7` frozen predictions | `R1`–`R5` written into the freeze **before** any executor existed; **all five HELD** |

**The prospective part.** `R1`–`R5` are in `FREEZE_V1.md` at commit
`65b45210`, and the workflow proves the ordering by asserting that no executor,
oracle, test, receipt or reconciliation path resolves at that commit. They are
recorded with verdicts and numbers, and the ladder is proved non-vacuous —
every problem moves its selection at least once, two move twice — so `R1` is not
holding by having nothing to say.

**The boundary that was measured rather than rounded.** `PC-6`'s witness rests
on a registered target suite that cannot see the third coordinate. Enlarging
the suite does **not** uniformly destroy it: `Y_b2` and `Y_parity` kill it
outright, `Y_majority` leaves **2** of the 4 pairs alive. The asymmetry is
reported.

**Two routes.** Route A builds sensors as restricted-growth strings and values
them by per-block aggregate maximisation over `Fraction`s. Route B builds
sensors by an insert-into-a-block recursion over frozensets and values them by
enumerating **every** deterministic policy measurable with respect to the
sensor, in integers scaled by the exact common denominator `32`; it decides free
merges by comparing values before and after the merge rather than by
intersecting optimal-action sets. The test parses route B's AST and asserts its
whole import set is `{fractions, json, sys}`. They agree on every headline
number.

**Hostiles.** Five, each proved to move its target quantity before it is proved
detected: a sensor leak (a policy that reads a distinction the sensor hides,
inflating `V(blind)` from `1/2` to `1`); the pairwise-Helly trap; a truncated
target suite that makes distinguishable sensors look predictively identical; an
inverted sensing cost that breaks the coarsening ladder; a freeze-provenance
tamper.

**Null.** The detector fires iff some predictively redundant state pair has no
common optimal action. Controls are **matched to the claim** rather than drawn
at large: **200** utilities measurable with respect to the registered target
suite — which provably cannot make the hidden coordinate control-relevant —
give **0/200** false alarms, and **200** planted utilities that read the hidden
coordinate give **200/200** recall. An earlier unmatched control family fired
200/200 and was discarded as useless before anything was reported.

## Reproduce

```bash
python3 -I -B  research/gmi-833-ae-ae7-prediction-to-control-v1/test_ae7_prediction_to_control_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae7-prediction-to-control-v1/test_ae7_prediction_to_control_v1.py -v
python3 -I -B  research/gmi-833-ae-ae7-prediction-to-control-v1/ae7_prediction_to_control_v1.py > /tmp/ae7.json
cmp /tmp/ae7.json research/gmi-833-ae-ae7-prediction-to-control-v1/RESULT_V1.json
python3 -I -B  research/gmi-833-ae-ae7-prediction-to-control-v1/independent_control_oracle_v1.py
```
