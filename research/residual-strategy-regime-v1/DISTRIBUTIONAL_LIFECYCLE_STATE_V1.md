# Distributional lifecycle state — why a decision-bit probability is not enough

**Status:** exact finite decision-theory refinement / source-derived counterexample protocol / no ML authorization.

`PAID_HORIZON_INFORMATION_PROTOCOL_V1.md` correctly represents a prospective lifetime belief as a distribution over effective horizon `H`.  This note proves why that richer object cannot in general be replaced by one calibrated probability that the episode belongs to the eventual semantic-winning region.

The distinction is important:

```text
ex-post action sufficiency:
  once H is realized, which static exact arm is cheaper?

ex-ante economic sufficiency:
  before H is known, which investment/switch policy minimizes expected cost?
```

A one-bit decision region can solve the first problem perfectly and still be an insufficient statistic for the second.

## 1. Exact objects

Fix one prospectively registered scalar resource coordinate `r` and horizons `H=1,...,M`.

Let

```text
I_r(H) = expected cost of always using exact inverse search
S_r(H) = expected cost of one cold persistent semantic session
Z_r(H) = 1[S_r(H) < I_r(H)]
```

with ties assigned prospectively to the inverse region only to make `Z_r` single-valued.  Let `C_r(H,tau)` be the exact one-way threshold cost already used by `online_switch.py` and `horizon_information.py`:

```text
C_r(H,tau) = I_r(H)                         if H <= tau
             I_r(tau) + S_r(H-tau)          if H > tau.
```

For a lifetime prior `P`, the Bayes risk of threshold `tau` is

```text
L_r(P,tau) = E_{H~P}[C_r(H,tau)].
```

The exact optimal threshold set is

```text
T*_r(P) = argmin_tau L_r(P,tau).
```

## 2. Decision-region probability insufficiency theorem

Define the coarse representation

```text
phi_r(P) = P[Z_r(H)=1].
```

### Theorem 1

If there exist two admitted lifetime distributions `P,Q` such that

```text
phi_r(P) = phi_r(Q)
```

but

```text
T*_r(P) intersection T*_r(Q) = empty,
```

then no controller whose only belief input is `phi_r(P)` can be Bayes-optimal for both distributions.

### Proof

A controller of the form `pi(phi_r(P))` receives identical input under `P` and `Q`, hence emits the same threshold (or the same distribution over thresholds) in both cases.

For a deterministic controller, any common output threshold would need to belong to both optimal sets, contradicting their empty intersection.

For a randomized controller, expected Bayes cost under a fixed prior is a convex combination of deterministic threshold risks.  Such a mixture attains the minimum Bayes risk only if all thresholds in its positive support are Bayes-optimal for that prior.  Therefore a mixture optimal under both `P` and `Q` would require positive support inside `T*_r(P) intersection T*_r(Q)`, again impossible. QED.

This is an observation/representation insufficiency result, not a model-capacity result.  A larger classifier or MLP on the same scalar probability cannot repair it.

## 3. Why the bit loses economic information

`Z_r(H)` preserves only the sign of the static-arm difference

```text
Delta_r(H) = S_r(H) - I_r(H).
```

It discards:

```text
|Delta_r(H)|,
when a future switch can occur,
the residual semantic lifetime after a switch,
and how threshold cost varies inside each decision region.
```

Two priors can therefore put exactly the same probability mass on the two static decision regions while putting that mass at very different horizons.  Their probability of "semantic eventually wins" is identical, but the cost of waiting, switching early, or never switching is not.

### Corollary 1 — calibrated binary probability is not generally a sufficient economic state

Even if a predictor is perfectly calibrated for the event `Z_r(H)=1`, its scalar output `p` is not in general sufficient for Bayes-optimal threshold control.  Sufficiency requires an additional structural condition such as all candidate-policy cost differences being functions of `Z` alone, or access to enough conditional cost moments to recover every relevant expected policy loss.

The R0B source-derived curves do not satisfy that collapse, as the executable witness below checks.

## 4. Frozen R0B witness construction

For each primary coordinate, the expected static crossover is source-derived:

```text
transitions                 H_c = 4
arithmetic additions        H_c = 6
arithmetic multiplications  H_c = 9
```

Construct two synthetic theorem witnesses, not deployment priors:

```text
P_r = 0.5 delta_{H=1} + 0.5 delta_{H=H_c}
Q_r = 0.5 delta_{H=1} + 0.5 delta_{H=M}.
```

Both have

```text
P_r[Z=1] = Q_r[Z=1] = 0.5,
```

because `H=1` lies in the inverse region and `H_c` and `M=142` lie in the semantic region.

`distributional_lifecycle_verify.py` rebuilds `I_r,S_r` from the source-derived `regime.json`, enumerates every legal threshold `tau in 0..M`, and requires the two Bayes-optimal threshold sets to be disjoint.  No hard-coded expected cost is trusted.

The currently observed source-derived witness is:

```text
coordinate                    P_r optimum    Q_r optimum
transitions                        tau=4          tau=1
arithmetic additions               tau=6          tau=1
arithmetic multiplications         tau=9          tau=1
```

The verifier, not this prose table, is authoritative for the branch head.

## 5. Minimal sufficient economic state

For a finite action family `A`, a belief representation `psi(P)` is decision-sufficient for Bayes control only if equality of representations preserves the vector of expected action losses up to distinctions that cannot change the optimizer.  A sufficient but generally nonminimal representation is the full posterior over `H`:

```text
P(H | legal history).
```

A smaller exact state may exist.  For the threshold family it is enough to preserve the expected loss vector

```text
ell_P(tau) = E_P[C(H,tau)]   for every candidate tau,
```

up to a common additive constant and any further quotient that preserves the argmin and future update law.  This is the correct decision-theoretic target for compression; it is not automatically the mean horizon, the median, a static-arm class probability, entropy, confidence, or a learned embedding.

This is the Bayes analogue of the feature-collision result in `FORMAL_DECISION_CORE_V2.md`: two beliefs mapped to the same representation but requiring disjoint optimal actions prove the representation is too coarse.

## 6. Survival/hazard state is free information already present

At age `d`, merely observing that the session has survived reveals `H>d`.  Under a registered prior, the exact posterior is

```text
P(H=h | H>d).
```

Therefore a future lifecycle predictor must be compared against a controller that already conditions on age/survival.  A distributional or hazard forecast is useful only to the extent that it improves expected protected value beyond that legal baseline.

This makes the next scientific target more specific than "predict horizon":

```text
find a lawful lifecycle observation whose induced posterior changes the
cost-relevant distribution over remaining reuse opportunity enough to alter the
optimal paid cognition/state-investment decision.
```

## 7. Blackwell/value-of-information consequence

The correct ordering of candidate lifecycle signals is decision-relative.  A signal that predicts `Z` accurately can be economically weaker than a signal that predicts coarse residual-lifetime magnitude, because the latter may better separate threshold losses.

Use the existing exact signal calculus:

```text
R_K(pi,0) = sum_z min_tau sum_H pi_H K(z|H) C_tau(H)
```

and compare candidate channels by Bayes risk / Blackwell dominance where available.  Mutual information with `H` or classification accuracy for `Z` is secondary; neither is the protected objective.

## 8. Research gate

Do not open a learned lifecycle router merely because the binary decision region is predictable.  A future signal lane must establish, in order:

```text
1. a lawful operational source for effective-lifetime information;
2. a prospectively admitted lifetime prior / survival process;
3. calibration or a distributional uncertainty contract;
4. exact Bayes/robust value against age-only and no-signal parents;
5. complete acquisition, inference, update, storage, drift and lifecycle costs;
6. only then, residual model-selection complexity.
```

Until such a source exists, the stronger current interpretation remains:

```text
DEMAND_SIGNAL_SOURCE_NOT_ESTABLISHED_R0B_PHASE2C0
```

and no learned router is authorized.
