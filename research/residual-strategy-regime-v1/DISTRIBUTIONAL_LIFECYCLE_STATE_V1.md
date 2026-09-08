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

For the current source-derived curves the witness has the following tied sets:

```text
coordinate                    T*(P_r)                  T*(Q_r)
transitions                    {4,...,142}              {1}
arithmetic additions           {6,...,142}              {1}
arithmetic multiplications     {9,...,142}              {1}
```

Every threshold at or after `H_c` is behaviorally identical on `P_r` because that witness has no mass beyond `H_c`; the theorem does not pretend `tau=H_c` is a unique optimum.  What matters is that the complete optimal sets are disjoint.  The verifier, not this prose table, is authoritative for the branch head.

## 5. A sufficient finite economic representation

For a finite action family `A`, a belief representation `psi(P)` is decision-sufficient for one-shot Bayes control if equality of representations preserves enough expected losses to preserve the optimizer.

Fix a reference action `a_0`.  Define the loss-difference moments

```text
m_a(P) = E_P[C(H,a) - C(H,a_0)],  a != a_0.
```

### Proposition 2 — loss-difference vector suffices for one-shot Bayes action selection

The vector `m(P)` determines the Bayes-optimal action set.

### Proof

For every action `a`,

```text
E_P[C(H,a)]
 = E_P[C(H,a_0)] + m_a(P),
```

with `m_{a_0}=0`.  The first term is common to all actions, so minimizing expected total loss is exactly minimizing `m_a(P)`. QED.

This is sufficient but not generally minimal.  Any further quotient is legal only if it preserves the argmin and, for a persistent controller, the future update/value law.

## 6. Exact R0B threshold-loss rank theorem

The frozen donor admits a stronger structural result for the full one-way threshold family.

Use `tau=M` (never switch within the registered horizon) as the reference policy and define the `M x M` loss-difference matrix

```text
D[h,tau] = C(h,tau) - C(h,M),

h   in {1,...,M}
tau in {0,...,M-1}.
```

### Lemma 3 — `D` is lower triangular

For `h <= tau`, threshold `tau` has not switched before the episode ends, so

```text
C(h,tau) = I(h) = C(h,M).
```

Hence `D[h,tau]=0` whenever `h<=tau`, which is exactly the zero region above the diagonal when row `h=tau+1` is paired with column `tau`. QED.

### Lemma 4 — the diagonal is the one-query cold semantic premium

At diagonal entry `h=tau+1`,

```text
D[tau+1,tau]
 = I(tau) + S(1) - I(tau+1).
```

Under the frozen IID target population, expected inverse lifetime cost is additive across queries:

```text
I(tau+1) - I(tau) = I(1).
```

Therefore every diagonal entry is

```text
S(1) - I(1).
```

On all three primary coordinates the cold one-query semantic parent is strictly more expensive than inverse, so this quantity is nonzero. QED.

### Theorem 5 — exact loss-difference matrix is invertible

For each primary coordinate,

```text
det(D) = (S(1) - I(1))^M != 0.
```

### Proof

By Lemma 3, `D` is triangular.  By Lemma 4, every diagonal entry is the same nonzero scalar.  The determinant of a triangular matrix is the product of its diagonal entries. QED.

### Corollary 5.1 — preserving every threshold loss difference preserves the full horizon prior

Write a prior as row vector `p` over `H=1,...,M`.  Its complete expected loss-difference vector is

```text
m(p) = p D.
```

Since `D` is invertible,

```text
p = m(p) D^{-1}.
```

Thus, on the frozen threshold family, the complete exact expected loss-difference vector is informationally equivalent to the full horizon prior.

### Scope of this result

This does **not** prove that every action-only decision quotient must encode all `M-1` prior degrees of freedom.  A one-shot representation is allowed to discard distinctions that never change the Bayes-optimal threshold.  The theorem proves a narrower but useful statement:

```text
there is no nontrivial exact linear/moment compression that preserves the
complete threshold-loss vector for all lifetime priors.
```

It also matters for future cognition: if the controller must evaluate arbitrary later signals, survival conditioning, or changes in the admissible action set, preserving only the current argmin may be insufficient.  Full posterior information remains the safe conventional parent until a smaller dynamically sufficient quotient is proved.

`distributional_lifecycle_verify.py` checks the triangular/nonzero-diagonal premises from the source-derived curves rather than relying on numerical matrix rank.

## 7. Survival/hazard state is free information already present

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

## 8. Blackwell/value-of-information consequence

The correct ordering of candidate lifecycle signals is decision-relative.  A signal that predicts `Z` accurately can be economically weaker than a signal that predicts coarse residual-lifetime magnitude, because the latter may better separate threshold losses.

Use the existing exact signal calculus:

```text
R_K(pi,0) = sum_z min_tau sum_H pi_H K(z|H) C_tau(H)
```

and compare candidate channels by Bayes risk / Blackwell dominance where available.  Mutual information with `H` or classification accuracy for `Z` is secondary; neither is the protected objective.

## 9. Research gate

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
