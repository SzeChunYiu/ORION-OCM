# Lifecycle decision-region advice gate — formal no-ML parent

**Status:** literature-backed reduction / exact finite model / no ML authorization.

This note narrows the remaining R0B uncertainty after the cold target-feature audit and the unknown-horizon switch study.  The relevant prediction target is not target identity and need not be the full future horizon.  It is the decision region induced by the exact parents.

## 1. Two-static-arm decision region

For one prospectively registered raw resource coordinate `r` and effective lifetime `H`, let

```text
I_r(H) = expected lifetime cost of always using exact inverse search
S_r(H) = expected lifetime cost of a cold persistent semantic session
O_r(H) = min(I_r(H), S_r(H))
```

under the frozen iid 142-target demand model.

Define the decision-region bit

```text
Z_r(H) = 0  if I_r(H) <= S_r(H)
         1  otherwise.
```

This is the decision-relevant object in the sense of Decision Region Determination / Equivalence Class Determination: recovering hidden horizon identity is unnecessary if all horizons in a region license the same optimal static arm.

### Theorem 1 — one perfect decision bit is sufficient for the two-static-arm benchmark

If an oracle supplies `Z_r(H)` before the episode, the policy

```text
Z=0 -> inverse
Z=1 -> persistent semantic
```

has cost exactly `O_r(H)` for every horizon.

**Proof.** `Z_r(H)` is defined as the identity of an arm attaining the minimum of the two registered arm costs.  Selecting that arm therefore costs `min(I_r(H),S_r(H))`. QED.

This is an advice-complexity statement about the benchmark, not a claim that the bit is cheaply observable.

### Theorem 2 — zero perfect advice bits cannot exactly recover the benchmark when the optimal regions conflict

Suppose there exist horizons `H_0,H_1` for which the unique optimal static arms differ.  Any horizon-blind randomized choice over the two static arms that has expected ratio exactly one at `H_0` must put probability one on the unique optimum at `H_0`; exact ratio one at `H_1` requires probability one on the other arm.  No single distribution can satisfy both. QED.

Thus at least one bit of future decision information is necessary for exact recovery of this two-arm clairvoyant benchmark whenever both strict regions are nonempty.

## 2. Frozen R0B regions

The source-derived expected curves have a single monotone crossover on each primary coordinate:

```text
transitions:                 semantic wins from H=4
arithmetic additions:        semantic wins from H=6
arithmetic multiplications:  semantic wins from H=9
```

Therefore the perfect advice problem is only a short-vs-long region bit on each scalar coordinate.  Before a price vector is registered there is no single scalar decision bit for the whole raw resource vector: inverse is Pareto-better through H=3, semantic is Pareto-better from H=9, and H=4..8 is price-sensitive.

## 3. Untrusted / imperfect region advice

The mature learning-augmented and untrusted-advice literature says not to follow a prediction blindly.  Preserve a worst-case guarantee and trade consistency against robustness.

Let advice `A in {0,1}` satisfy the prospective per-horizon guarantee

```text
P(A = Z_r(H) | H) >= 1 - epsilon.
```

The policy does not receive `H` or future targets.  Conditional on observed advice bit `a`, it chooses a distribution `p_a` over legal one-way switch thresholds `tau` from `online_switch.py`.

Let

```text
R_r(H,tau)
```

be threshold cost divided by `O_r(H)`.

For a fixed horizon, an adversary may choose an error probability `q in [0,epsilon]`.  Because expected ratio is affine in `q`, the worst value is attained at an endpoint.  Consequently the exact finite robust-advice problem is the LP

```text
minimize rho

over p_0, p_1 in simplex, rho

subject to, for every H with z = Z_r(H):

  sum_tau p_z(tau) R_r(H,tau) <= rho

  (1-epsilon) sum_tau p_z(tau) R_r(H,tau)
  + epsilon sum_tau p_(1-z)(tau) R_r(H,tau) <= rho.
```

### Theorem 3 — the LP is optimal for the declared advice channel and policy family

Every admissible policy in the family is completely specified by the two threshold distributions `p_0,p_1`.  For fixed `H`, the adversary's error choice enters linearly, so checking `q=0` and `q=epsilon` is sufficient.  The objective is the maximum of those finitely many linear forms.  Epigraph linearization gives exactly the LP above.  Therefore its optimum equals the minimax expected competitive ratio within the declared family. QED.

No predictor is trained by this theorem.

## 4. Consistency / robustness gate

`robust_lifecycle_advice.py` solves the LP on the source-derived matrix and reports:

- endpoint control `epsilon=0`: exact ratio 1;
- endpoint control `epsilon=1`: equality with the no-advice randomized time-only minimax value;
- monotonicity of optimal robust ratio as the error allowance grows;
- maximum `epsilon` compatible with target robust ratios 1.01, 1.02, 1.05, 1.10 and 1.20;
- the actual threshold support used after each advice value.

Independent pre-CI calculation indicates that to guarantee ratio <=1.05 on each coordinate separately, the per-horizon advice error bound must be roughly below 3.03% (transitions), 2.80% (additions), and 2.45% (multiplications).  These are **not** accuracy requirements for an ordinary classifier distribution; they are requirements under the stronger declared per-horizon adversarial error model.

## 5. Economic gate before prediction

Even a statistically valid advice channel is not automatically worth acquiring.  Let

```text
C_no_advice(H)
C_advice(H)
C_acquire(H)
```

be raw resource vectors for the certified no-advice policy, advice-conditioned policy, and feature/prediction acquisition plus maintenance.  Advice is economically admissible only under a prospectively registered objective if

```text
Value(C_no_advice - C_advice) > Value(C_acquire)
```

with lifecycle costs included: feature collection, predictor inference, calibration monitoring, updates, storage, checkpoint/replay and invalidation.

If the robust advice policy cannot repay this complete cost, terminate `COGNITION_NOT_ECONOMIC` even if the predictor is accurate.

## 6. Literature parents and scope

This reduction uses mature parents rather than claiming novelty:

- Decision Region Determination / Equivalence Class Determination: identify a decision-sufficient region, not necessarily a hidden hypothesis.
- Online algorithms with advice: quantify how much future information is structurally necessary.
- Learning-augmented ski rental / rent-or-buy: consistency versus robustness under imperfect predictions.
- Online computation with untrusted advice: do not let advice remove the adversarial guarantee.
- Calibrated/distributional advice: if a real lifecycle signal exists, uncertainty should enter the policy explicitly rather than as an unqualified point prediction.

The registered R0B curves are not claimed to be the classical linear ski-rental cost model.  We reuse the learning-augmented **methodology** on the exact finite threshold ratio matrix.

## 7. Research terminal

This lane authorizes a learned horizon/reuse predictor only after all of the following survive prospective testing:

```text
1. a legal lifecycle observation channel predicts the decision-region bit;
2. its calibration/error contract is measured without protected leakage;
3. a robust advice-conditioned exact parent materially improves the no-advice parent;
4. the improvement survives raw-resource and lifecycle accounting;
5. a simpler exact/statistical estimator does not already capture the signal.
```

Until then:

```text
LEARNED_ROUTER_NOT_AUTHORIZED_R0B_LIFECYCLE_ADVICE_GATE
```
