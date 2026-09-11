# S2G-2 OCM prospective structure → geometry protocol v1

Status: **prospective protocol. No outcome from any future scored world may change this file.**

Refs #377, #323, #233, #373.

## Scientific question

Can legal pre-target controller/library statistics predict the magnitude and direction of the OCM developmental-geometry shift on a fresh world **before any protected target is solved**?

This tests the first non-toy instance of:

\[
\text{structure/history}\to\widehat{\mathcal G}_M\to\text{future search burden}.
\]

It does not test cross-paradigm generality yet.

## Frozen predictor — no fitted model

After the normal #323 development + validation phase and before protected target execution, read only quantities already legal to the deployable controller:

```text
chosen library identity
library token count T
chosen probe depth D
beta_D
validation baseline paid ranks b_i
validation tiling count d_i / guided position g_i
validation hit/miss status against the chosen library/depth
```

For each validation row define the controller-cost proxy exactly as the existing expected-cost rule:

```text
c_i(D) = guided_position_i          if validation solution tiles within D
       = beta_D + b_i               otherwise
```

Define the pre-target scalar geometry predictor

\[
\widehat{\Delta I}_{val}
=
\operatorname{median}_i\left[\log_2\frac{b_i}{c_i(D)}\right].
\]

No parameters are fitted.

Also record:

```text
h_val = validation hit fraction
r_val = median_i c_i(D) / median_i b_i
```

These are diagnostics, not alternate primary predictors.

## Protected outcome

After the fresh protected world is complete, compute using the already registered behavioural receipt:

\[
\Delta I_{test}
=
\operatorname{median}_t\left[\log_2\frac{rank_0(t)}{rank_H(t)}\right].
\]

and

```text
f_test = fraction of targets with rank_H < rank_0.
```

## Primary prediction

For each prospectively admitted fresh world:

```text
sign(DeltaI_test) = sign(DeltaIhat_val)
```

with exact convention:

```text
positive  > +0.05 bits
neutral   in [-0.05,+0.05] bits
negative  < -0.05 bits
```

This is a deliberately modest first test of transfer from validation geometry to protected search geometry.

## Secondary quantitative prediction

Report absolute error

\[
|\Delta I_{test}-\widehat{\Delta I}_{val}|
\]

without an initial pass/fail tolerance. The first disjoint batch calibrates error scale; any later confirmatory tolerance must be frozen using only that development batch.

This avoids choosing a favorable error margin from the same protected data.

## Batch-level test

First prospective batch requires at least 6 independent fresh worlds if available under the existing lane protocol.

Primary batch terminal:

```text
OCM_STRUCTURE_TO_GEOMETRY_SIGN_TRANSFER_SUPPORTED_EXPLORATORY
```

iff:

```text
>= 5 / 6 independent worlds have the correct registered sign
AND no world has DeltaIhat_val > +0.25 but DeltaI_test < -0.25.
```

This threshold is frozen here before future protected outcomes.

If fewer than six new independent worlds become available, report descriptive rows only and `CANNOT_CHECK_BATCH_SIZE`.

## Strong parent controls

The same fresh worlds must report at least:

1. **constant parent:** predict the historical pooled median `1.91 bits` for every world;
2. **ecology/family-only parent:** predict the development-set median for the declared world-family label, when such label was fixed independently of target outcomes;
3. **simple baseline-rank parent:** if legal pre-target validation median baseline rank is used, predict from it alone using a development-only rule frozen before protected outcomes;
4. **SHUFFLED/RESET controls:** their protected geometry must not be retrospectively used to construct the predictor.

No learned regression is permitted in V1. A later V2 can add regression only after a complete development batch and must be frozen on a disjoint next batch.

## Attribution

A positive V1 result means only:

> the controller's own pre-target validation geometry contains transferable information about its later proposal-rank shift.

It does **not** establish a new cross-paradigm invariant.

If the family-only or constant parent matches the sign/quantitative prediction equally well, report:

```text
PREDICTIVE_PARENT_SUFFICIENT
```

## Negative terminals

```text
OCM_STRUCTURE_TO_GEOMETRY_SIGN_TRANSFER_FAILS
VALIDATION_GEOMETRY_NOT_PREDICTIVE
FAMILY_LABEL_PARENT_SUFFICIENT
CONSTANT_PARENT_SUFFICIENT
CANNOT_CHECK_BATCH_SIZE
CANNOT_CHECK_<reason>
```

## Data custody

- This protocol must be merged/frozen before the first world counted toward the V1 prospective batch is executed or inspected.
- Worlds/outcomes already visible before this freeze are calibration/history only and may not count.
- Every attempted world is retained, including controller refusal, regression, crash or null.
- No threshold/predictor change after outcome access; modifications create `S2G_OCM_PROSPECTIVE_V2` and require a new batch.

## Claim ceiling

Best possible V1 terminal:

```text
STRUCTURE_TO_GEOMETRY_PREDICTION_SUPPORTED_AT_OCM_SCOPE_E2
```

Cross-paradigm and field-level claims remain locked.