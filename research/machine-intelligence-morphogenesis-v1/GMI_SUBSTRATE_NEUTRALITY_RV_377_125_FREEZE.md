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

---

# RV-377-125 — ADJUDICATION: neural and non-neural sit on the same ceiling

`L = 32`, 80 independent `W` draws × 800 queries, 6 values of `r`, 3 substrates.

| `r` | bound | `neural_perceptron` | `symbolic_program` | `exemplar_table` |
|---|---|---|---|---|
| 0 | 0.5000 | 0.5000 ± 0.0019 | 0.5000 ± 0.0019 | 0.5000 ± 0.0019 |
| 4 | 0.5625 | 0.5452 ± 0.0080 | 0.5637 ± 0.0020 | 0.5637 ± 0.0020 |
| 8 | 0.6250 | 0.6068 ± 0.0081 | 0.6242 ± 0.0023 | 0.6242 ± 0.0023 |
| 16 | 0.7500 | 0.7445 ± 0.0072 | 0.7499 ± 0.0017 | 0.7499 ± 0.0017 |
| 24 | 0.8750 | 0.8734 ± 0.0048 | 0.8752 ± 0.0013 | 0.8752 ± 0.0013 |
| 32 | 1.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 |

| id | outcome |
|----|---------|
| S1 | **CONFIRMED** — 0 violations; no substrate exceeds `½ + r/(2L)` in expectation |
| S2 | **CONFIRMED** — 0 gaps; neural and symbolic agree within 3 s.e. at every `r` |
| S3 | **CONFIRMED** — the perceptron's pilot advantage vanishes entirely in expectation |
| S4 | **CONFIRMED** — all three sit at exactly 0.5000 with no development |
| S5 | **CONFIRMED** — all three reach exactly 1.0000 at full development |

## The result

> **At equal channel access, a gradient-trained neural machine has no capability advantage
> over a symbolic lookup program.** Both sit on `½ + r/(2L)`; neither exceeds it; both reach
> exactly ½ with no development and exactly 1.0 with full development.

This derives neural and non-neural intelligence **under one law**. The capability ceiling is a
function of the information channels alone, and the substrate does not enter it. Whatever
distinguishes a neural machine from a lookup table at this scope, it is **not what it can
achieve** — it is what it costs.

## S3 was the honest risk, and it resolved against the pilot

The disclosed pilot showed the perceptron at **0.8113 against a 0.7500 bound** — above the
ceiling and above both symbolic machines on the same world. Had that survived averaging, my own
capability law would have been wrong as stated, missing a term for machines that estimate
global statistics from `D`.

It did not survive. Over 80 draws the perceptron sits **on or below** the bound at every `r`.
The pilot was the fixed-`W` effect: on one draw, the revealed sample's bit-imbalance does
estimate the unrevealed majority; averaged over `W`, `H(W_unrevealed | D) = L − r` exactly and
the gain is zero. The machine built to attack the law confirmed it instead.

## Flagged rather than waved through

The perceptron is **below** the symbolic machines at `r = 4, 8, 16, 24` — **four of four**
non-trivial values, consistently one-sided. Each individual gap is inside 3 s.e. (at `r = 4`,
diff 0.0185 against a tolerance of 0.0247, which is not comfortable), but a one-sided run of
four is not what symmetric noise produces.

The reading is that the perceptron **pays a real optimizer cost**: 60 epochs of SGD does not
perfectly memorize the revealed pairs, and its trained bias adds variance (its standard error
is 3–4× the symbolic machines' at every `r`). That is a *capability shortfall from imperfect
optimization*, not a substrate advantage, and it points the same way as the main result — the
neural machine never does better, only sometimes slightly worse.

This does not affect S1, S2 or S3 as scored. It is recorded because a consistent one-sided
deviation deserves a stated explanation rather than a passing p-value, and because a
larger-draw re-test would settle whether the shortfall is real or four coincidences. Registered,
not claimed.

## Scope

One obligation type, one world family, `L = 32`, one neural architecture with one training
budget. This tests **capability parity only**. GMI's separate claim that substrates differ in
*lifecycle cost* is untouched here and is not evidence for or against.
