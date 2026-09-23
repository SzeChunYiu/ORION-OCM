# gmi-833-ae-ae3-compression-learning-v1

Section AE3, all eight rows: *compression is not automatically learning*.

**Registered scope.** Domain `{0,1}^3`, all `256` targets, training set
`{x : x2 = 0}`. A finite, Kraft-checked prefix-code family in which "shortest
description" is a decidable integer computed by exhaustive enumeration —
`K` itself is never computed, and saying so is enforced by a guard rather than
asserted in prose.

| result | numbers |
|---|---|
| `AE3-1` three notions | all **six** ordered pairs non-determining: `A→B` **17,406** conflicts of 25,636, `A→C` **14,258**, `B→A` **2,050** of 10,280, `B→C` **5,568**, `C→A` **3,854** of 15,232, `C→B` **10,520** |
| `AE3-2` compresses but useless | `O = x0` and `O = x1 XOR x2` both cost **6** bits against a **9**-bit literal; task usefulness `1/2` (blind) versus `1` |
| `AE3-3` useful ≠ shortest | target `01111000`: shortest consistent program **6** bits, **unique** argmin, out-of-sample accuracy **0**; shortest perfect generalizer **7** bits |
| `AE3-4` memorize ≠ generalize | 16 perfect-training hypotheses spanning out-of-sample `{0, 1/4, 1/2, 3/4, 1}`; **6,094,848** of **8,386,560** equal-training pairs differ out of sample |
| `AE3-5` MDL / Bayes | MDL argmin has **2** members at **6** bits with out-of-sample `1/2` and `1`, so MDL selects a strictly worse hypothesis than the risk optimum; four parents mapped with DOIs, Occam's direction left to its parent |
| `AE3-6` Kolmogorov boundary | three forbidden promotions registered and a guard that alarms **0** times on this receipt while detecting **2 of 2** planted claims |
| `AE3-7` surrogates | `\|K_L1 − K_L2\| ≤ 1` on **242** of 256 targets, **0** strict order flips of **32,640** pairs; `\|K_L1 − K_L3\| ≤ 3` |
| `AE3-8` invariance boundary | **refused as unqualified**: over **200** Kraft-feasible independent regenerations of the code-length vector AE3-2 holds on **162** with the exact predicate `min(rule, xor) < literal` matching **200/200**, AE3-3 holds on only **170** with all **30** exceptions enumerated, AE3-4 is language-independent |

**The finding that matters most.** Row 8 asks whether the predictions survive
independent regenerations of the coding language (the row's own word is
`remints`) *up to the actually justified invariance boundary*. They do not survive
universally. Two of the three verdicts are conditional inside the prefix-code
family, the conditions are stated exactly where a closed form exists and
enumerated where it does not, and `UNIVERSAL_MACHINE_INVARIANCE_PROVED` remains
a registered forbidden promotion.

**Two routes.** Route A decides code lengths by structural membership tests;
Route B materialises every program of the language and minimises by enumeration,
rebuilding the rule basis and every accuracy independently. They agree on every
table in every registered language.

**Hostiles.** Five, each proved potent before proved detected: rule-basis
tamper, Kraft-violating language, planted uncomputable-quantity claim,
suppressed MDL tie set, parent blob tamper.

**Null.** The compresses-but-useless detector fires on the planted witness,
`0` of `2` known-clean controls, and `25` of `200` random corpora — base rate
reported, not suppressed.

## Reproduce

```bash
python3 -I -B research/gmi-833-ae-ae3-compression-learning-v1/test_ae3_compression_learning_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae3-compression-learning-v1/test_ae3_compression_learning_v1.py -v
python3 -I -B research/gmi-833-ae-ae3-compression-learning-v1/ae3_compression_learning_v1.py > /tmp/ae3.json
cmp /tmp/ae3.json research/gmi-833-ae-ae3-compression-learning-v1/RESULT_V1.json
```
