# Lifetime belief collision — mean plus decision-region probability is insufficient

**Status:** exact source-derived theorem witness / synthetic priors only / no ML.

`DISTRIBUTIONAL_LIFECYCLE_STATE_V1.md` proves that the scalar probability of the
static semantic-winning decision region is not generally a sufficient Bayes
state.  A natural attempted repair is to add expected horizon:

```text
phi(P) = ( E_P[H], P[semantic-static-winning region] ).
```

The frozen R0B curves refute this representation too.

## Theorem

If two admitted priors `P,Q` satisfy

```text
E_P[H] = E_Q[H]
P_P[Z=1] = P_Q[Z=1]
```

but their Bayes-optimal one-way switch threshold sets are disjoint, then no
controller whose only belief input is `phi(P)` can be Bayes-optimal for both.

**Proof.**  The representation is identical, so a deterministic controller emits
the same threshold under `P,Q`, contradicting disjoint optimal sets.  A randomized
controller can attain fixed-prior Bayes optimum only with support on deterministic
Bayes-optimal thresholds; disjoint optimal sets therefore also rule out a common
optimal mixture. QED.

## Source-derived witnesses

`moment_collision_verify.py` searches rather than trusts this prose.  It restricts
to simple equal-weight two-point theorem priors with one support point in each
static decision region, groups them by equal support sum (hence equal mean), and
requires disjoint optimal threshold sets.

The first witnesses found from the current curves are expected to be:

```text
transitions:
  P = 0.5 delta_1 + 0.5 delta_5
  Q = 0.5 delta_2 + 0.5 delta_4
  same mean = 3, same semantic-region probability = 0.5
  P optimum tau=1; Q optimum tau>=4

arithmetic additions:
  P = 0.5 delta_1 + 0.5 delta_7
  Q = 0.5 delta_2 + 0.5 delta_6
  same mean = 4, same semantic-region probability = 0.5
  P optimum tau=1; Q optimum tau>=6

arithmetic multiplications:
  P = 0.5 delta_1 + 0.5 delta_10
  Q = 0.5 delta_2 + 0.5 delta_9
  same mean = 5.5, same semantic-region probability = 0.5
  P optimum tau=1; Q optimum tau>=9
```

The executable output is authoritative; these priors are counterexamples, not
claims about operational lifetime frequency.

## Consequence

A mean-horizon regressor plus a calibrated probability of "long enough for
semantic to win" can still throw away decision-relevant distribution shape.
Increasing model capacity on those two outputs cannot repair the collision.

For the finite threshold family, a sufficient parent representation is the
expected loss vector

```text
ell_P(tau) = E_P[C(H,tau)]  for every legal tau,
```

or any exact quotient that preserves its argmin and the future update law.  The
full posterior over `H` is sufficient but is not claimed minimal.

This sharply defines the eventual feature/search problem: seek the **coarsest
lawful representation that preserves the relevant expected policy losses**, not
a conventional point forecast because it is easy to train.

Current terminal remains

```text
DEMAND_SIGNAL_SOURCE_NOT_ESTABLISHED_R0B_PHASE2C0
```

because no operational prior/signal source has yet been admitted.
