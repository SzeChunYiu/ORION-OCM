# GMI #833 Section Z / Z5 — critical phenomena and scaling

Closes the six rows of `### Z5` in issue comment `5684819296`.

## What it establishes

Over the registered `65552`-candidate binary mechanism universe and the `60`
frozen worlds, with exact rational arithmetic:

- **two control parameters** `CP-1`: the objective is homogeneous of degree `1`
  in `(eta, lambda)`, so the verdict depends only on `(p, mu)` with
  `mu = lambda/eta`; `0` homogeneity violations, `15` distinct `(p, mu)` keys,
  `0` determinism violations;
- **an analytic threshold** `CP-2`: *every* stateless candidate has
  `e_delay = N/2` exactly, so the best stateless cost is `eta*p/2`, the best
  one-state-bit cost is `lambda`, and `lambda* = eta*p/2` follows by counting;
  the analytic threshold equals the exact crossing at all `60` worlds;
- **first order, with an exact latent-quantity relation** `CP-3`: `J*` is
  continuous and piecewise linear, the derivative jump is exactly `1 = Delta m`,
  the tie at `lambda*` is exact in `Q`, and the critical window has width `0`;
- **zero finite-size drift** `CP-4`: `lambda*(L) = eta*p/2` for every `L >= 2`,
  verified exhaustively at `L in {2,3,4,5}` (`N = 4, 16, 48, 128`);
- **a refuted extrapolation** `CP-5`: with symbol alphabet `A` and state cost in
  registers, `lambda*(A) = eta*p*(1 - 1/A)`. The registered law's literal
  extrapolation — `lambda*` independent of `A` — is **false** for `A >= 3`, shown
  by exhaustive enumeration of `16`, `729` and `65536` stateless tables giving
  `1/2, 2/3, 3/4`;
- **the failure is published** `CP-6`: `FAILED_SCALING_PREDICTION_REGISTER_V1.json`
  carries one refutation beside four confirmations and a parent negative control,
  each pinned by path, blob sha and a verbatim anchor occurring exactly once.

## What it does not establish

No universal exponents, no continuous transition, no thermodynamic limit, no
physical or real-substrate scaling. Alphabet size is this package's **registered
scoped reading** of a substrate change, not a device or a medium. The scaling law
is stated in the registers accounting convention; the bits convention is
excluded because it makes the threshold irrational at `A = 3`.

**After this package `lambda* = eta*p/2` may only be stated at `A = 2`.** The
forbidden promotion `LAMBDA_STAR_IS_ETA_P_OVER_TWO_IN_GENERAL` applies downstream.

Claim ceiling:

```
GMI_833_Z5_EXACT_FIRST_ORDER_MORPHOLOGY_TRANSITION_ZERO_FINITE_SIZE_DRIFT_AND_THE_REFUTED_ALPHABET_INDEPENDENT_THRESHOLD_AT_REGISTERED_FINITE_SCOPE
```

## Reproduce

```bash
python3 -I -B  research/gmi-833-z-z5-critical-phenomena-v1/independent_scaling_oracle_v1.py
python3 -I -B  research/gmi-833-z-z5-critical-phenomena-v1/z5_critical_phenomena_v1.py
python3 -I -B  research/gmi-833-z-z5-critical-phenomena-v1/test_z5_critical_phenomena_v1.py -v
python3 -I -O -B research/gmi-833-z-z5-critical-phenomena-v1/test_z5_critical_phenomena_v1.py -v
```

Stdlib only. Route A takes about 18 s and route B about 7 s on one core.

## The instrument failed first

The first null compared each drawn scaling law against the author's own closed
form and never touched the enumerated data — it would have scored `200/200` with
the enumeration deleted. It was replaced by a verdict-level adjudicator grounded
in the `A`-ary enumeration and an exhibited zero-error one-register witness, with
a probe-offset guard. Full ladder: `200/200` caught. An `A = 2`-only adjudicator:
`186/200`, with the `14` blind laws verified to be exactly those that agree at
`A = 2`. See `FREEZE_V1_AMENDMENT_1.md`, committed before the receipt.
