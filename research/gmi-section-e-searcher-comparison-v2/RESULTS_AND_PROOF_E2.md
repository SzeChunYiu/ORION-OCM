# Section E same-world parent searcher comparison E2

Authority: issue #715. Pre-outcome freeze `773bebb5b7851c72a0a80e4ff22381406d9cac99`; arithmetic/cache supplement `d437442367b7314a8ef453c0c1d4630e86b579c4`.

## Result

All frozen E2 predictions passed exactly in normal and optimized local execution.

The protected discrete phenotype space is unchanged across searchers: all 32 five-bit homogeneous affine support masks, with target mask 21 for `x0 XOR x2 XOR x4`. The exact discrete loss remains flat away from the target: every wrong mask makes 16 errors on the 32-input cube.

## 1. Uniform random search

In a uniformly random permutation of 32 candidates, the target rank is uniform on 1..32. Therefore

```text
P(hit within 10) = 10/32 = 5/16
E[rank] = (1+32)/2 = 33/2
E[truth touches to discovery] = 32*(33/2) = 528.
```

The witness enumerates the exact rank support rather than sampling a random seed.

## 2. Strict evolutionary representative

The `(1+1)` strict representative starts at mask 0, mutates one bit, and accepts only a strict decrease in exact semantic error. The start and all five one-bit neighbors have error 16; hence no proposal is accepted. Because the target has Hamming distance 3, it can never be proposed from the fixed parent by one mutation.

At ten frozen mutation attempts the semantic cache contains the start plus five distinct neighbors:

```text
unique verified masks = 6
truth touches = 192
success = false
terminal = STRICT_ELITIST_PLATEAU.
```

This is ordinary elitist local-search/evolutionary plateau behavior.

## 3. Neutral CGP/GP-like drift

If equal-fitness point mutations are accepted, every non-target mutation is neutral and the process is a simple random walk on the five-cube with the target absorbing.

The witness enumerates all `5^5=3125` five-proposal mutation-choice strings and obtains exactly

```text
P(hit by 5) = 12/125.
```

With early stopping, exact expectations are

```text
E[unique verified masks] = 15622/3125
E[truth touches]         = 499904/3125
E[proposal attempts]     = 613/125.
```

An independent exact transition dynamic program gives

```text
P(hit by 10) = 72696/390625.
```

No Monte Carlo result is used.

## 4. One-shot edge-ablation NAS-like representative

The registered relaxed parity supernet is

```text
p_z(x) = (1 - product_i (1 - 2 z_i x_i))/2.
```

At symmetric gates `z_i=1/2`, independently ablating each gate to 0 or 1 gives exact endpoint losses:

```text
target bits {0,2,4}:  z_i=0 -> 17/64, z_i=1 -> 15/64
other bits  {1,3}:    z_i=0 -> 15/64, z_i=1 -> 17/64.
```

The hard mask is therefore exactly 21 and passes the final exact verifier.

The preregistered accounting is not free:

```text
truth touches          = 10*32 + 32 = 352
arithmetic update ops  = 10*32*26 = 8320
```

so the method is over the common 320-touch primary cap despite exact recovery.

## 5. DARTS-like differentiable representative

For exact MSE at the symmetric point,

```text
L(1/2,...,1/2) = 31/128
grad L          = (-1,+1,-1,+1,-1)/32.
```

The witness derives this with exact rational arithmetic from all 32 examples. It does not insert the vector as a constant.

With learning rate 8,

```text
z'=(3/4,1/4,3/4,1/4,3/4),
```

which thresholds to hard mask 21 and passes exact verification.

Frozen arithmetic accounting reproduces:

```text
loss+gradient pass = 2112 arithmetic ops
five gate updates  =   10 arithmetic ops
arithmetic total   = 2122
truth touches      = 32 relaxed + 32 exact = 64.
```

Thus it succeeds inside the primary truth-touch cap, but carries an explicit arithmetic coordinate.

## 6. Same ecology, different finite-budget recovery

At the shared 320 truth-touch cap:

```text
uniform random       success probability 5/16
strict evolutionary  success probability 0
neutral drift        finite exact probability < 1
one-shot ablation    exact but over budget at 352 touches
DARTS-like gradient  exact success within cap at 64 touches + 2122 arithmetic ops.
```

The ecology, target, exact verifier and final discrete phenotype space are identical. The observed finite-budget recovery therefore depends materially on the registered search mechanism and representation.

This is not a universal ordering: the continuous relaxation has been chosen to match affine parity structure.

## 7. Representation-misspecification negative twin

For singleton target `y=1 iff x=10101`, no hard affine mask is exact. The DARTS-like step yields all gates 1/4, rounds to mask 0, and the exact verifier records one singleton error.

Required terminal reproduces:

```text
REPRESENTATION_MISSPECIFIED_NO_EXACT_AFFINE_TARGET.
```

This prevents the successful parity result from being interpreted as universal gradient-search superiority.

## 8. Remint

The coordinate permutation `(2,4,1,0,3)` maps the parity target to mask 11, support `{0,1,3}`. The exact wrong-mask plateau is unchanged. Consequently:

- strict evolution remains plateau-blocked;
- neutral drift retains the exact `12/125` and `72696/390625` hit probabilities because Hamming distance remains 3;
- one-shot ablation selects the reminted support;
- DARTS gradient signs permute with the support and threshold to mask 11.

## Parent subtraction

Mechanism ownership stays with parent literatures: uniform random search; evolutionary/neutral mutation search; GP/CGP neutral networks; one-shot/NAS encoding search; DARTS differentiable architecture search; genotype-phenotype and encoding-bias theory.

The only GMI residual asserted here is the governed same-world comparison: freeze the ecology, target, grammar, verifier, resource coordinates and search protocols before scoring, then attribute observed finite-budget differences to the registered search mechanism rather than to a changed task.

## Section E disposition

At this registered finite scope E2 supports a bounded comparison of random, evolutionary, GP/CGP-like, NAS-like and gradient search representatives, and strengthens the claim that search algorithm/encoding can determine observed morphology recovery under a fixed finite budget.

It does **not** close four-family neutral recovery, four-family cross-grammar replication, full meta-search, real-scale NAS/evolution, or universal searcher dominance.

## Claim ceiling

```text
FINITE_EXACT_SAME_WORLD_PARENT_SEARCHER_COMPARISON_E2
PARENT_OWNED_RANDOM_EVOLUTION_CGP_NAS_DARTS_SEARCH
NO_UNIVERSAL_SEARCHER_DOMINANCE_OR_REAL_SCALE_NAS_CLAIM
```
