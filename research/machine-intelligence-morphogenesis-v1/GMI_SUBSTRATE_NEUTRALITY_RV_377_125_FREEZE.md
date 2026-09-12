# RV-377-125 — FREEZE: neural and non-neural intelligence under one capability law

Frozen BEFORE the run. A pilot is disclosed in §3.

## 1. The claim being tested

The laws of `RV-377-123`/`RV-377-124` bound `F(P, D, Q, A, R)` **without ever naming a
mechanism**. If that is substantive rather than rhetorical, then a **gradient-trained neural
machine** and a **symbolic lookup program** must sit on the *same* ceiling given the same
channels, and neither may exceed it.

That single statement is a derivation covering neural and non-neural intelligence together:

> **At equal channel access, neural and non-neural machines have equal capability. Whatever
> distinguishes them is cost, not capability.**

This is the sharpest form of GMI's substrate-neutrality commitment, and it is falsifiable in
one run: exhibit a neural machine that beats a symbolic one at equal channels, and it is dead.

## 2. The three machines

| machine | substrate |
|---|---|
| `neural_perceptron` | real SGD: one-hot index → sigmoid, 60 epochs, lr 0.5, trained on the revealed pairs, **including a trained bias term** |
| `symbolic_program` | explicit conditional lookup, no numeric parameters |
| `exemplar_table` | stored cases, nearest match |

No weight sharing across indices in the perceptron — that is the honest encoding for a world
whose bits are independent, since there is no structure to share.

## 3. Disclosed pilot, and the mechanism it exposes

```
L = 32, r = 16, 800 queries, seed 1, bound = 0.7500
  neural_perceptron   0.8113
  symbolic_program    0.7588
  exemplar_table      0.7588
```

The perceptron is **0.06 above the bound and above both symbolic machines on the same world.**
That demands an explanation before any prediction is frozen, and there is one:

**the trained bias term estimates `W`'s global bit-imbalance from the revealed sample.** The
table uses `D` only for exact index lookups; the perceptron additionally uses `D` to estimate
which bit value is more common in `W`, and guesses that on unrevealed indices. Both are
legitimate uses of `D` — the perceptron simply extracts more of it.

Whether this breaks the bound turns on a subtlety the corpus has already been burned by. For
`W` uniform over all `2^L` strings, `H(W_unrevealed | D) = L − r` bits exactly: conditional on
`D`, the unrevealed bits **are** fair coins, so no gain is possible **in expectation over `W`**.
But on a **fixed** `W` with a bit-imbalance, a random revealed subset does estimate the
unrevealed majority, and the gain is real for that draw.

This is the same fixed-`W` effect that produced 80 spurious violations in `RV-377-123`. The
predicates below are therefore stated over the **expectation across independent `W` draws**.

## 4. Frozen predictions

`L = 32`, `r ∈ {0, 4, 8, 16, 24, 32}`, **80 independent `W` draws**, 800 queries each.

| id | prediction | falsifier |
|----|-----------|-----------|
| **S1** | **No machine exceeds `½ + r/(2L)` in expectation** — the perceptron included, despite the pilot. | any machine above bound + 3 s.e. |
| **S2** | **Neural and symbolic agree within 3 s.e. at every `r`.** Equal channels, equal capability. | a gap beyond 3 s.e. at any `r` |
| **S3** | The perceptron's pilot advantage **vanishes in expectation** — its mean over 80 draws sits on the bound, not above it. | mean above bound + 3 s.e. |
| S4 | At `r = 0` all three sit at ½ ± 3 s.e. — no machine invents information. | any above |
| S5 | At `r = L` all three reach 1.000 — full development is fully usable by every substrate. | any below 0.999 |

**S2 is the substrate-neutrality claim proper.** If a neural machine systematically beats a
symbolic one at equal channel access, GMI's substrate neutrality is false and the capability
laws are incomplete — they would be missing a mechanism coordinate after all.

**S3 is the honest risk.** The pilot says the perceptron wins on one draw. If that survives
averaging, the bound is wrong as stated for machines that estimate global statistics from `D`,
and the law needs a term for it. That would be a real defect in my own result, found by a
machine built to attack it.

## 5. Scope

One obligation type, one world family, `L = 32`. This tests capability parity, not cost parity
— GMI's separate claim that the substrates differ in lifecycle burden is untouched here.
