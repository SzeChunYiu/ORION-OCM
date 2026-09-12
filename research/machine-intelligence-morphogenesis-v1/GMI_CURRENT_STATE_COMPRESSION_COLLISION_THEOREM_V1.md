# GMI current-state compression collision theorem v1

Status: **FORMAL DISCRIMINATION THEOREM / B1 NARROWING**

Date: 2026-09-12.

Purpose: prove that current representation/compression alone is insufficient to predict lifecycle-optimal machine morphology when future update and lineage obligations differ.

## 1. Two realizations

Consider one present semantic function `f` with two exact realizations:

- `P`: compact shared/parametric state of present description burden `d`;
- `M`: explicit record state of present description burden `N`, with `d<N`.

For `R` present/future ordinary queries let per-query serving prices be `c_P,c_M`. Define current-horizon costs

\[
C_P^0=d+Rc_P,
\qquad
C_M^0=N+Rc_M.
\]

Assume `C_P^0<C_M^0`, so a current-state compression/resource rule selects `P`.

Now let each future local semantic revision impose:

\[
u_P=C_{rewrite}+C_{lineage,P},
\qquad
u_M=C_{local}+C_{lineage,M}.
\]

Suppose `u_P>u_M` because the compact realization requires a global rewrite or expensive version retention while the record realization can update/version locally.

## 2. Theorem CC-1 — exact lifecycle phase flip

After `U` registered revisions,

\[
C_P(U)=C_P^0+Uu_P,
\qquad
C_M(U)=C_M^0+Uu_M.
\]

Let

\[
\Delta_0=C_M^0-C_P^0>0,
\qquad
\delta=u_P-u_M>0.
\]

Then the explicit/local realization becomes cheaper exactly when

\[
U\delta>\Delta_0.
\]

At equality the two are tied.

This is not an asymptotic claim; it is exact finite accounting under the registered cost model.

## 3. Theorem CC-2 — current-state predictor no-go

Construct two worlds `W0,W1` that have the same current semantic function `f`, current realization descriptions, current prices and current observations, but:

- `W0`: no future revisions (`U=0`);
- `W1`: `U` future local revisions with `U delta>Delta_0`.

Any deterministic predictor whose input contains only the current semantic state/description and current prices receives identical input in `W0` and `W1`, so it must output the same morphology. Yet `P` is uniquely cheaper in `W0` and `M` is uniquely cheaper in `W1`. Therefore the predictor is wrong in at least one world.

A randomized current-only predictor cannot achieve zero error on both worlds for the same reason: its output distribution is identical while the unique optimum differs.

## 4. GMI consequence

A sufficient morphology predictor must type future-development variables such as:

```text
revision rate / count
revision locality
reuse horizon
retention and lineage requirements
verification/admission burden
switch/compile cost
```

This is a necessity result for developmental context, not evidence that GMI is the only theory able to include it. A sufficiently complete ordinary lifecycle/resource model can match the prediction.

## 5. Negative twin

If `u_P<=u_M`, or if the horizon has `U delta<=Delta_0`, the current compact realization does not lose its lifecycle advantage. High revision count alone is insufficient; the update/lineage differential is the causal variable.

## 6. Executed finite hostile calibration

`run_gmi_current_state_compression_collision_v1.py` enumerates finite cost grids with `N=4..12`, `d<N`, multiple query horizons, serving prices, update frequencies, rewrite costs and lineage prices.

Among 23,800 registered volatile cells whose corresponding stationary world uniquely favors the compact realization, 21,835 exhibit the predicted lifecycle flip to local explicit state; every flip satisfies the exact inequality above and no non-flip violates it.

Receipt: `GMI_CURRENT_STATE_COMPRESSION_COLLISION_RECEIPT_V1.json`.

## 7. Claim ceiling

This separates GMI's developmental-state requirement from **current-state** compression rules. It does not establish superiority over a parent model that already includes the identical future lifecycle variables and full cost accounting. B1 therefore remains open against the strongest lifecycle-aware parent.
