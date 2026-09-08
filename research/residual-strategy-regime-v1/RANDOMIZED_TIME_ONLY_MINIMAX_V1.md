# Randomized time-only minimax — exact no-feature parent for R0B

**Status:** research theorem/reduction + frozen numerical certificate; no ML authorization.

This note closes the next parent in the R0B unknown-lifetime ladder.  It is not a
new online-algorithms theorem.  The parent result is the finite zero-sum minimax
theorem / linear-programming strong duality.  The OCM-specific work is the exact
reduction from the source-derived lifetime curves, the protected scope, raw
resource treatment, and a solver-independent certificate.

## 1. Why this parent exists

At cold known-horizon entry, legal target features already leave less than 0.08%
feature-conditional regret on every primary phase coordinate before feature or
policy cost.  Unknown effective lifetime is a much larger uncertainty: inverse
wins short stable lifetimes while persistent semantic search wins longer ones.

Before acquiring a target feature, horizon forecast, or learned prediction, test
the strongest controller that sees only:

```text
elapsed completed query count
private randomness
```

It does not see the future horizon, future targets, target coefficients, a
learned score, or a post-outcome cost.

The policy draws one threshold `tau` at session start, uses exact stateless
inverse for the first `tau` queries, then switches once to the incumbent
persistent semantic arm from cold and never switches back.

## 2. Exact deterministic cost family

For resource coordinate `r`, let the source-derived iid expected lifetime curves
be

```text
I_r(H) = expected cost of H stateless inverse queries
S_r(H) = expected cost of H queries in one cold persistent semantic session
I_r(0) = S_r(0) = 0.
```

The one-way threshold policy has exact expected cost

```text
C_{r,tau}(H) =
  I_r(H)                    if H <= tau
  I_r(tau) + S_r(H - tau)  if H > tau.
```

The benchmark used in this tranche is the clairvoyant best of the same two
static exact arms:

```text
B_r(H) = min(I_r(H), S_r(H)).
```

Exhaustive enumeration confirms that, on the frozen 142-target population and
`H in 1..142`, allowing a known-horizon intermediate one-way threshold does not
beat `B_r(H)` on any primary coordinate.  Thus this benchmark is also the exact
known-horizon optimum inside the current one-way threshold family at this scope.

Define the finite ratio matrix

```text
A_r[H,tau] = C_{r,tau}(H) / B_r(H).
```

Every entry is generated from source-derived exact accounting; no learned model
or measured future outcome enters the controller.

## 3. Deterministic minimax baseline

Exhaustive threshold search gives:

| resource coordinate | best tau | worst ratio | hostile H |
|---|---:|---:|---:|
| transitions | 2 | 1.635612817971589 | 3 |
| arithmetic additions | 4 | 1.503896158734181 | 9 |
| arithmetic multiplications | 6 | 1.513430075410343 | 12 |

No single deterministic threshold is coordinate-independent.  If one threshold
must serve all three primary coordinates without a price vector, the best joint
choice is `tau=3` with worst coordinate-by-horizon ratio approximately
`1.869814604347208`.

This is already enough to reject the claim that an unknown lifetime can be
handled by one cheap universal deterministic break-even point.

## 4. Randomized policy as a finite zero-sum game

Let `p_tau` be a probability distribution over thresholds.  Against an
**oblivious horizon adversary**, which chooses/fixes `H` without observing the
policy's private threshold draw, the expected ratio at horizon `H` is

```text
R_r(H,p) = sum_tau A_r[H,tau] p_tau.
```

The minimax randomized time-only parent is

```text
V_r = min_p max_H R_r(H,p).
```

This is a finite matrix game.

### Primal LP

```text
minimize    z
subject to  A_r p <= z 1
            sum_tau p_tau = 1
            p_tau >= 0.
```

### Dual LP

Let `q_H` be a probability distribution over hostile horizons:

```text
maximize    v
subject to  q^T A_r >= v 1^T
            sum_H q_H = 1
            q_H >= 0.
```

### Lemma 4.1 — weak-duality certificate

For every feasible `p,q,z,v`,

```text
v <= q^T A_r p <= z.
```

**Proof.**  From dual feasibility, every component of `q^T A_r` is at least
`v`; multiplying by `p>=0` and using `sum p=1` gives `q^T A_r p >= v`.
From primal feasibility, every component of `A_r p` is at most `z`;
multiplying by `q>=0` and using `sum q=1` gives `q^T A_r p <= z`. QED.

For finite zero-sum games, von Neumann minimax / LP strong duality gives equality
at the optimum.  We therefore do not need to trust a solver's status string: a
frozen primal distribution and dual distribution whose **recomputed** upper and
lower bounds meet within tolerance are an independently checkable numerical
certificate.

## 5. Adversary boundary is load-bearing

Randomization is useful here only against an oblivious horizon adversary.  If an
adversary observes the realized private `tau` before choosing `H`, it can choose
the worst horizon for that deterministic threshold, and mixing gives no such
minimax benefit.

This is the standard randomized-online-algorithms/Yao scope.  The repository
therefore freezes:

```text
adversary = oblivious horizon; cannot observe private threshold draw
```

and explicitly makes no adaptive-adversary claim.

## 6. Coordinate-specific certified solutions

The offline certificate generator used HiGHS through SciPy once.  CI does not
import NumPy, SciPy or the solver.  `randomized_switch_verify.py` rebuilds the
matrix from `regime.json`, reconstructs the frozen distributions from
`RANDOMIZED_SWITCH_CERTIFICATE_V1.json`, and recomputes the primal upper and dual
lower bounds using only the Python standard library.

The certified minimax values are:

| resource coordinate | deterministic best | randomized minimax | ratio reduction |
|---|---:|---:|---:|
| transitions | 1.635612818 | **1.368216034** | ~16.35% |
| arithmetic additions | 1.503896159 | **1.325270314** | ~11.88% |
| arithmetic multiplications | 1.513430075 | **1.333712604** | ~11.87% |

The supports are sparse.  For example, the transition-optimal policy mixes only
`tau in {0,1,2,3}`.  The corresponding dual lower-bound witness puts mass only on
`H in {1,2,3,11}`.  The full decimal certificate, not rounded prose values, is in
`RANDOMIZED_SWITCH_CERTIFICATE_V1.json`.

These numbers prove that private randomization materially improves the exact
no-feature online parent, but they do **not** make the horizon uncertainty small.
All three values remain far above the frozen 1.05 research terminal.

## 7. One price-independent policy over raw resource coordinates

Choosing a separate threshold distribution after selecting a resource price
would repeat the X3 error.  We therefore form one larger game whose rows are

```text
(resource_coordinate, H)
```

for all three primary coordinates and all `H in 1..142`, while the columns are
still the same threshold choices.  The minimizer must choose one distribution
`p` before learning any scalar resource price.

The frozen joint certificate gives

```text
alpha_joint = 1.559190999265383
```

with primal support

```text
tau 0 : 0.16072131821845118
tau 1 : 0.15539378228142220
tau 2 : 0.17050607817483330
tau 3 : 0.19307600237038125
tau 4 : 0.22110320718257370
tau 5 : 0.09919961177234374
```

and a matching dual lower bound `1.5591909992653779` before verifier rounding.
The worst rows are drawn from transition and multiplication regimes; additions
are strictly below the joint worst value.

### Theorem 7.1 — coordinatewise competitive bounds imply a price-independent bound

Let the chosen policy have raw expected cost vector `C(H)`, and let the two
static exact arms have vectors `A(H),B(H)`.  Suppose for every registered resource
coordinate `i`

```text
C_i(H) <= alpha * min(A_i(H), B_i(H)).
```

Then for every nonnegative price vector `w>=0`,

```text
w.C(H) <= alpha * min(w.A(H), w.B(H)).
```

### Proof

Componentwise bounds and `w_i>=0` give

```text
w.C
<= alpha * sum_i w_i min(A_i,B_i).
```

For each coordinate, `min(A_i,B_i) <= A_i` and also `<= B_i`, hence

```text
sum_i w_i min(A_i,B_i) <= min(w.A,w.B).
```

Combining the inequalities proves the result. QED.

Thus the joint randomized threshold is a genuinely **price-independent exact
parent** for every nonnegative linear scalarization of the registered raw
coordinates.  It is not a retrospective exchange-rate result.

It improves the best single deterministic joint threshold from about `1.869815`
to `1.559191`, but still leaves a large online gap.

## 8. Scientific interpretation

This result changes what the residual means.

```text
cold target-feature residual before cost: < 0.08%
unknown-lifetime joint minimax residual:   ~55.9% competitive overhead
```

These are different experiments and should not be subtracted numerically, but
the scale separation is decisive for research ordering.  The dominant missing
information is about **survival/reuse of the cognitive state**, not about which
polynomial target has arrived.

A larger target classifier does not reveal how long the session will remain
valid.  If the legal observation channel contains no useful lifetime signal,
this is an observation/demand-channel limit.  If such a signal exists, its value
must be measured and its acquisition/maintenance cost charged before any
predictor is authorized.

Current terminal:

```text
RANDOMIZED_TIME_ONLY_SWITCH_LEAVES_ONLINE_RESIDUAL_R0B_PHASE2B2
```

This is **not** `RESIDUAL_ALGORITHM_SELECTION_OPPORTUNITY` yet.  It says only that
elapsed time + private randomness are insufficient to approach the clairvoyant
static lifetime benchmark within 5%.

## 9. Next parent: paid horizon information

The next question is decision-theoretic:

```text
What legal observation Z about session survival/invalidation changes the optimal
investment decision, and is

    value_of_information(Z)
    > acquisition + inference + calibration + maintenance + lifecycle cost?
```

The immediate mature parents are Bayesian stopping under a horizon prior,
Blackwell value of information, and online algorithms with costly predictions.
A prediction is not free preprocessing.

Required order:

1. freeze a legitimate held-out source for a lifetime prior or forecast signal;
2. compute the exact no-signal Bayes/time-only parent;
3. compute the perfect-horizon information upper bound;
4. compute exact value for each legal candidate signal;
5. charge signal acquisition and policy cost;
6. test misspecification/drift and fail-closed behavior;
7. only if paid residual survives, compare robust learning-augmented parents;
8. only after those parents fail may an OCM-specific learned lifetime model be studied.

## 10. Literature parent map

We rely on mature results rather than claiming novelty for them:

- von Neumann finite minimax theorem / LP strong duality for matrix games;
- Yao-style randomized online analysis, with the oblivious-adversary scope made
  explicit;
- classical randomized ski rental and its multislope/multi-option extensions;
- Purohit, Svitkina & Kumar (NeurIPS 2018), learning-augmented online algorithms;
- Gollapudi & Panigrahi (ICML 2019), rent-or-buy with expert advice;
- Drygala, Nagarajan & Svensson (AISTATS 2023), **costly predictions**;
- Shin et al. (ICML 2023; later TOALG), randomized learning-augmented multi-option
  ski rental;
- Sun et al. (ICML 2024), uncertainty-quantified predictions;
- Kang, Park & Fan (AAAI 2026), discrete Bayesian ski rental;
- recent 2026 distributional-advice work is relevant as a later robustness parent,
  not evidence that OCM currently possesses a lawful distributional forecast.

The reusable contribution here is the admission discipline: reduction first,
exact simple parent second, paid information third, learned model last.
