# V6 unseen-form prediction freeze V1

Frozen **before** neutral search execution on this branch.

Authority targets: #602 V6 (6 boxes), #592 item 39 (W2/W3/W4 ladder).

## Freeze seed

```text
sha256("GMI-UNSEEN-FORM-PREDICTION-V1/RQM-SPARSE-ALIAS")
  = d8e9eac97a9ce7ee3735efe5cc77bef40d6ab611712cd7bccd3fae3f2550030b
```

(The executable recomputes this digest and refuses to run if it disagrees.)

## Predicted ecology (W1 sparse fixed predictive alias)

Histories `H = {0,1,2,3,4,5}`.

```text
q_P = (0, 0, 0, 1, 1, 1)     # two predictive classes
q_O = (0, 1, 2, 3, 4, 3)     # five target classes
```

Fiber multiplicities: `m(0)=3`, `m(1)=2`. Therefore

```text
max_m = 3
B_res_wc = ceil(log2 3) = 2
|S_P| = 2
|S_O| = 5
predicted min cost C* = |S_P| + max_m = 5
flat-table parent cost = 1 + |S_O| = 6
```

## Property-first prediction (C0) — stated before search

Any exact realizing machine on this ecology must realize the property vector

```text
PV1  exact target recovery on all |H|=6 histories
PV2  uses a predictive quotient with >= |S_P|=2 classes (or a refinement)
PV3  carries a separately mutable residual alphabet of size >= max_m = 3
PV4  has a composition decoder d(p, r) -> target
PV5  zero-residual (R=1) machines are impossible
PV6  cost coordinate C = |P_used| + |R_used| is minimized at C* = 5
```

This is the Residual Quotient Machine (RQM) property vector from
`GMI_PREDICTIVE_RESIDUAL_QUOTIENT_THEORY_V1.md` / `GMI_PREDICTED_MACHINE_INTELLIGENCE_FORMS_V1.md`.
No architecture macro named RQM/RAG/Transformer enters the search grammar.

Neutral search is **conditional on the registered predictive quotient**: `P_assign`
is fixed to `q_P` and only residual assignments are enumerated. Machines that
abandon `q_P` are parent morphologies, not RQM recoveries.

## Negative twin (pre-registered)

```text
q_P_twin = q_O = (0, 1, 2, 3, 4, 3)
```

Prediction: residual augmentation is unnecessary; pure predictor with `|R|=1` wins;
`max_m = 1` and `needs_residual = false`.

## Fresh residual-specific prediction (pre-registered, held-out)

Held-out ecology `H'={0..7}`:

```text
q_P' = (0,0,0,0, 1,1,1,1)
q_O' = (0,1,2,3, 4,5,4,5)
```

Fiber multiplicities: `m'(0)=4`, `m'(1)=2`. Predict **before** measuring:

```text
max_m' = 4
min residual alphabet = 4
C*' = 2 + 4 = 6
flat-table parent cost = 7
zero-residual impossible
```

## Parent first refusal

Parents allowed as comparison arms only (not search macros):

```text
pure predictor (R fixed to 1)
pure flat table (P trivial, R = |H|)
history-keyed retrieval / RAG-like table
```

Novelty language withheld unless parent reduction leaves a material residual on the
registered cost coordinate.

## Explicit non-claims (phase-hole honesty)

This freeze does **not** claim an atlas morphology phase-hole occupant.
Prior open-niche work (`GMI_OPEN_NICHE_PREDICTION_V1.md`) failed because the
occupant was a known parent. The present attack targets property-first residual
augmentation at exact finite scope, not a hole in the K4/atlas phase diagram.

## Terminals allowed only after all six V6 boxes

```text
UNSEEN_FORM_PREDICTION_SUPPORTED_AT_REGISTERED_SCOPE
NOVEL_INTEL_LADDER_W2_W3_GREEN_AT_EXACT_RQM_SCOPE__W4_NOT_CLAIMED
```

Forbidden until stronger evidence:

```text
NEW_DOMAIN
NEW_FORM_OF_INTELLIGENCE_PROVEN
COMPLETE_THEORY_OF_MACHINE_INTELLIGENCE
```
