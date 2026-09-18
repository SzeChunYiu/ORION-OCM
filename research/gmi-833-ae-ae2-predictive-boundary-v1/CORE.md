# gmi-833-ae-ae2-predictive-boundary-v1

Section AE2 asks for the information-theoretic learnability boundary to be
proved, quantified, separated from *usable* information, and populated with
adversarial control sources. This package does all four in exact rational
arithmetic with two independent computational routes.

| result | headline numbers |
|---|---|
| `PIB-1` no-predictive-information boundary | improvement exactly `0` under three registered losses, at history lengths 1 and 2 (observation alphabets 2 and 4; 4 and 16 deterministic rules enumerated) |
| `PIB-2` bounded-information performance bound | `gain <= D/2` verified on **670,396** exhaustive grid cases, **0** violations, **15,328** equality cases; tight witness `gain = 1/2`, `D = 1` |
| `PIB-3` exact mutual-information enclosure | rational brackets from two independent series, all probe widths below `1e-9`, both inside the crude `[1-1/t, t-1]` bracket |
| `PIB-4` Shannon vs accessible information | `I(X;Y) = 1` bit exactly, yet best accuracy is exactly `1/2` at decoder depths 0, 1 and 2, and `1` only at depth 3 |
| `PIB-5` fixture roster | four sources, each defining property machine-checked |

**The performance bound.** With `D = sum |P(x,y) - P_X(x)P_Y(y)|`, the Bayes
gain satisfies `gain <= D/2`. Chaining the parent-owned
Csiszar-Kullback-Pinsker inequality `I(X;Y) >= D^2/2` gives `2*gain^2 <= I(X;Y)`
in nats. Only the rational forms are ever asserted numerically. Route B verifies
each **step** of the proof separately across all 670,396 cases — including the
cancellation identity `sum_x Delta(x,y) = 0` — not merely the conclusion.

**Shannon is not usable.** On `Y = x_0 xor x_1 xor x_2` the learner sees all of
`x` and the target carries a full bit of mutual information, yet no decision
tree of depth below 3 does better than guessing. The dictator `Y = x_0` carries
*exactly the same* one bit and is decoded perfectly at depth 1. The separation
is **unconditional**: it rests on the machine-checked fact that for all `7`
proper coordinate subsets, `(x_S, y)` is exactly uniform (`0` violations), not
on any cryptographic assumption.

**The four control sources.**

- `LOWENT_IID` — Bernoulli(1/10): nonuniform marginal, L1 dependence and
  predictive gain **exactly** `0`.
- `HIGHENT_CYCLIC` — `X_t = X_{t-1}+1 mod 4`: marginal entropy `2` bits exactly
  (maximal), predictive gain `3/4`.
- `DRIFT_INVERT` — `Y = X` then `Y = 1-X`: each phase carries `1` bit, the
  pooled joint is exactly independent, and the phase-1 rule scores exactly `0`
  in phase 2 against a base rate of `1/2` — dependence becomes harmful, not
  merely useless.
- `CHAOS_DOUBLING` — doubling map on `8`-bit states with `4` bits observed, all
  `256` states enumerated: certainty for exactly `4` steps, then exactly `1/2`.

**Null.** Detector: one exact bit of mutual information with no depth-2 tree
beating the base rate. Fires on the planted 3-parity, does not fire on the
dictator or the two-bit xor, and fires on `0` of `200` random deterministic
worlds.

Claim ceiling:
`GMI_833_AE2_PREDICTIVE_INFORMATION_LEARNABILITY_BOUNDARY_PROVED_AND_EXACTLY_WITNESSED_AT_REGISTERED_FINITE_SCOPE`.
Everything is finite-alphabet and finite-horizon; no infinite-horizon,
continuous-state or complexity-class claim is made.

## Reproduce

```bash
python3 -I -B research/gmi-833-ae-ae2-predictive-boundary-v1/test_ae2_predictive_boundary_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae2-predictive-boundary-v1/test_ae2_predictive_boundary_v1.py -v
python3 -I -B research/gmi-833-ae-ae2-predictive-boundary-v1/ae2_predictive_boundary_v1.py
```
