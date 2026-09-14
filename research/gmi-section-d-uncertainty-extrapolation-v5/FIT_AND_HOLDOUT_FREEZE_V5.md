# GMI Section D V5 — Fit + Held-out Prediction Freeze

Stage-1 authority: `FREEZE_V5.md` at commit `ab231d78aae98beb679ca0e0ce8c36c4651dc438`.

This is the **stage-2 pre-holdout authority**. It is committed after the legal tiny training measurements and before any scored execution at `n=17` or `n=31`.

Training receipt:

```text
research/gmi-section-d-uncertainty-extrapolation-v5/TRAIN_V5.json
numeric_receipt_sha256 = a559ca1ffcb6fded7bc9731ca273b7d04117bb462b7e57016e2e9d6dc477d016
training sizes = {2,3,4,5}
```

No size outside `{2,3,4,5}` was used to fit the laws below.

---

## 1. Frozen tiny measurements

```text
n    persistent    migration    key 3F/4R block    value 3F/4R block
2        2             4               11                  10
3        3             6               15                  13
4        4             8               19                  16
5        5            10               23                  19
```

The stage-1 fitting rule uses only n=2 and n=3 to determine an affine law and treats n=4 and n=5 as exact internal validation.

---

## 2. Frozen fitted coefficients

Using `a = y(3)-y(2)` and `b = y(2)-2a`:

```text
coordinate                              a       b       fitted law
persistent_cells_single_orientation     1       0       n
migration_ops                            2       0       2n
key_block_ops                            4       3       4n + 3
value_block_ops                          3       4       3n + 4
```

Every law predicts the n=4 and n=5 training measurements with exact zero residual. No higher-order model is activated or permitted.

The extrapolation predictor is henceforth frozen to these four affine laws. It may not be refit after held-out execution.

---

## 3. Held-out prediction: n=17

Before any n=17 execution, the frozen laws predict:

```text
persistent cells, either single orientation = 17
key->value migration ops                = 34
key 3F/4R block ops                     = 71
value 3F/4R block ops                   = 55
```

For inherited key orientation and `m` future blocks:

```text
stay key      = 71m
migrate value = 34 + 55m.
```

Continuous equality boundary:

```text
71m = 34 + 55m
16m = 34
m* = 17/8 = 2.125.
```

Frozen phase predictions:

```text
m=1: key orientation strictly cheaper
m=2: key orientation strictly cheaper: 142 < 144
m=3: value orientation after migration strictly cheaper: 199 < 213
first strict integer migration horizon = 3.
```

The held-out implementation must also be exact on all `2n = 34` distinct forward/reverse token obligations.

---

## 4. Held-out prediction: n=31

Before any n=31 execution, the frozen laws predict:

```text
persistent cells, either single orientation = 31
key->value migration ops                = 62
key 3F/4R block ops                     = 127
value 3F/4R block ops                   = 97
```

For inherited key orientation:

```text
stay key      = 127m
migrate value = 62 + 97m.
```

Continuous equality boundary:

```text
127m = 62 + 97m
30m = 62
m* = 31/15 ~= 2.066666...
```

Frozen phase predictions:

```text
m=1: key orientation strictly cheaper
m=2: key orientation strictly cheaper: 254 < 256
m=3: value orientation after migration strictly cheaper: 353 < 381
first strict integer migration horizon = 3.
```

The held-out implementation must also be exact on all `2n = 62` distinct forward/reverse token obligations.

---

## 5. Cross-scale prediction

The training worlds contain crossover horizons:

```text
n=2 -> first strict value-migration horizon 5
n=3 -> 4
n=4 -> 3
n=5 -> 3.
```

The fitted laws therefore predict that the strict crossover has stabilized at `m=3` for both out-of-scale holdouts n=17 and n=31, despite their sizes being 3.4x and 6.2x the largest fitted world.

The claim is only that this registered affine operation law extrapolates to these two held-out sizes. No arbitrary-n or real-hardware scaling claim is allowed from the held-out pass alone.

---

## 6. Held-out exactness/remint predictions

For each held-out size:

1. the generic key-index and value-index implementations must answer every distinct forward/reverse query exactly;
2. actual key->value reindexing must reconstruct the exact inverse relation;
3. independent token remint from stage 1 must preserve exact outputs and every measured operation count;
4. observed numeric coordinates must equal the frozen values above with zero tolerance;
5. the comparator must detect an intentionally altered frozen prediction.

Any mismatch is an extrapolation failure. Do not change coefficients, fit family, training set, or held-out predictions after this commit.

---

## 7. Claim ceiling if holdouts pass

```text
FINITE_PROSPECTIVE_OUT_OF_SCALE_PHASE_LAW_EXTRAPOLATION
PARENT_OWNED_INDEXING_AMORTIZATION
NO_ARBITRARY_N_UNIVERSAL_SCALING_OR_REAL_SCALE_CLAIM
```
