# Section E same-world parent searcher comparison freeze E2

Date frozen: 2026-09-15.
Owner: #602 Section E. Child tracker: #715.

This file is the **pre-outcome authority** for E2 and is committed before any scored E2 witness/result/test artifact.

## Claim boundary

E2 compares bounded representatives of parent-owned search families on one identical frozen ecology, semantic target, exact verifier, and discrete phenotype grammar. It does not claim that these representatives exhaust GP/CGP, evolutionary, NAS, differentiable or meta-search.

Parents own the search mechanisms: uniform random search, `(1+1)` evolutionary mutation/selection, CGP/GP-style point mutation and neutral drift, one-shot architecture ablation, DARTS-style continuous relaxation/gradient search, and genotype-phenotype / architecture-encoding bias.

Claim ceiling:

```text
FINITE_EXACT_SAME_WORLD_PARENT_SEARCHER_COMPARISON_E2
PARENT_OWNED_RANDOM_EVOLUTION_CGP_NAS_DARTS_SEARCH
NO_UNIVERSAL_SEARCHER_DOMINANCE_OR_REAL_SCALE_NAS_CLAIM
```

## Frozen semantic world

Five-bit affine target:

```text
y(x)=x0 XOR x2 XOR x4.
```

Discrete phenotype grammar is all 32 homogeneous affine support masks. Target mask is 21. Exact discrete semantic error is frozen as 0 for target and 16 for every other mask.

Every searcher reports the vector

```text
truth_example_touches
proposal_or_mutation_attempts
unique_discrete_candidates_verified
arithmetic_update_ops
success_probability_or_exact_success
terminal
```

without post-hoc scalarization. One complete discrete semantic verification touches all 32 truth examples.

Primary comparison cap: 320 truth-example touches, equal to ten full discrete candidate evaluations. Proposal/arithmetic coordinates remain charged separately.

## S1 uniform random search

Enumerate the exact target-rank distribution for a uniformly random permutation rather than sampling.

Predictions:

```text
success within 10 verification slots = 10/32 = 5/16
expected target rank                 = 33/2
expected touches to discovery        = 32*(33/2)=528
```

## S2 strict `(1+1)` evolutionary representative

Start mask 0. Propose a uniformly chosen one-bit mutation. Accept only strict error decrease.

Because all five one-bit neighbors have exact error 16, equal to start error, the state never moves. Target is Hamming distance 3, so it is never proposed from the fixed parent.

Prediction:

```text
success probability = 0
terminal = STRICT_ELITIST_PLATEAU
```

## S3 neutral CGP/GP-like drift

Start at mask 0. Propose a uniformly chosen one-bit mutation and accept any non-worsening move. Target is absorbing. Since every non-target mask has equal discrete error, this is the simple random walk on the five-cube until target hit.

Exact dynamic-program predictions:

```text
P(hit by 5 proposals)  = 12/125
P(hit by 10 proposals) = 72696/390625
```

No Monte Carlo may substitute for the exact transition calculation.

## S4 one-shot edge-ablation NAS-like representative

Continuous gate vector `z in [0,1]^5` and relaxed parity prediction:

```text
p_z(x) = (1 - product_i(1 - 2 z_i x_i))/2.
```

Initialize all `z_i=1/2`. For each coordinate, evaluate full 32-example squared loss at `z_i=0` and `z_i=1` holding the other gates at 1/2; choose the lower-loss endpoint independently. Then round to a hard mask and perform one final exact 32-example discrete verification.

Frozen endpoint losses:

```text
i in target support {0,2,4}: L(z_i=0)=17/64, L(z_i=1)=15/64 -> choose 1
i outside support    {1,3}:   L(z_i=0)=15/64, L(z_i=1)=17/64 -> choose 0
```

Predictions:

```text
hard mask = 21
truth_example_touches = 10*32 + 32 = 352
```

Therefore this method is exact-successful but **over the 320-touch primary cap**.

## S5 DARTS-like differentiable representative

Use exact mean-squared loss over the same relaxed predictor.

At `z=(1/2,...,1/2)` freeze:

```text
L = 31/128
grad L = (-1,+1,-1,+1,-1)/32.
```

One gradient step with learning rate 8 gives

```text
z'=(3/4,1/4,3/4,1/4,3/4).
```

Threshold at 1/2 -> hard mask 21, then perform final exact discrete verification.

Accounting:

```text
truth_example_touches = 32 relaxed forward/backward examples + 32 final verifier examples = 64
```

Arithmetic update operations must be counted explicitly by implementation. The gradient must be computed from exact rational arithmetic, not inserted as a constant.

## S6 common-budget conclusion

At 320 truth-example touches:

```text
uniform random       exact success probability 5/16
strict evolutionary  success probability 0
neutral CGP drift    exact finite-horizon probabilities, not certainty
one-shot ablation    over budget (352 touches)
DARTS-like gradient  exact success within budget (64 touches + arithmetic ops)
```

Same ecology, target, verifier and final discrete phenotype grammar; finite-budget observed recovery is search-mechanism dependent.

No universal dominance follows because the differentiable relaxation is strongly matched to affine parity.

## S7 representation-misspecification negative twin

Singleton target:

```text
y=1 iff x=10101.
```

Final hard candidate grammar remains the same 32 affine masks, none of which represents this singleton exactly.

Prediction:

- exact relaxed loss and gradient may be computed;
- after the registered one gradient step and threshold, no hard affine mask passes the exact verifier;
- terminal = `REPRESENTATION_MISSPECIFIED_NO_EXACT_AFFINE_TARGET`.

## S8 disjoint bit remint

Coordinate permutation `(2,4,1,0,3)` maps target to support `{0,1,3}`, mask 11.

Predictions:

- random rank distribution unchanged;
- strict evolutionary remains plateau-blocked;
- neutral-drift hit probabilities remain 12/125 by five and 72696/390625 by ten because target Hamming distance remains 3;
- one-shot ablation chooses bits `{0,1,3}`;
- exact DARTS gradient signs permute with support and threshold to mask 11.

## What E2 may support if all gates pass

At this registered finite scope only:

- bounded same-world comparison of random, evolutionary, CGP/GP-like, NAS-like and gradient search representatives;
- stronger evidence that search mechanism/representation can determine finite-budget observed recovery under fixed ecology;
- parent-owned search-mechanism separation and negative representation-misspecification terminal.

Not earned: four-family neutral recovery, four-family cross-grammar replication, full meta-search comparison, real-scale NAS/evolution, or universal searcher ordering.
