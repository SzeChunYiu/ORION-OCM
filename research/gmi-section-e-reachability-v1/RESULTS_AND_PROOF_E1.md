# Section E reachability and charged search-burden result E1

Authority: issue #710. Pre-outcome freeze commit: `0329ea74f6d2475ed47e3e8e65c29f4105ea77fd`.

## Result

Every frozen E1 prediction passed exactly in normal and optimized local execution.

The protected target is the five-bit affine rule

```text
y(x)=x0 XOR x2 XOR x4,
```

represented by support mask `21`. The candidate grammar contains every one of the 32 homogeneous affine support masks.

### 1. Representability is not reachability

The target is literally a member of the global candidate grammar, so representability is immediate.

Under the restricted development law that flips exactly two support bits, Hamming-weight parity is invariant. Starting from mask zero, the reachable component is precisely the 16 even-parity masks. The target has Hamming weight 3, so it cannot be reached.

The exact exhaustive component search observed:

```text
unique semantic verifications = 16
pair-flip proposals            = 160
burden                         = 16*32 + 160 = 672
terminal                       = SEARCH_NEGATIVE_TARGET_REPRESENTABLE_BUT_OPERATOR_UNREACHABLE
```

This is a global support/reachability impossibility for the declared developmental law, not a local-search failure.

### 2. Adding an operator restores reachability

Adding one-bit support flips makes the candidate graph the five-dimensional hypercube, hence connected. A constructive path is

```text
0 -> 1 -> 5 -> 21.
```

With the frozen raw bit-neighbor order, BFS finds the target on the 21st semantic verification after 100 proposal attempts:

```text
burden = 21*32 + 100 = 772.
```

The larger burden than the failed pair-flip search is not paradoxical: restoration of reachability is not an efficiency theorem.

### 3. Local plateau barrier is distinct from global impossibility

For any wrong affine support mask `m != m*`, the difference `f_m XOR f_m*` is a nonzero linear form on `{0,1}^5`. Every nonzero linear form is balanced, so exactly 16 of the 32 inputs differ. Therefore the exact error surface is

```text
error(m*) = 0
error(m)  = 16 for every m != m*.
```

The one-bit graph is connected, but a strict-improvement local search at mask zero sees five neighbors with the same error 16 and cannot take its first step.

Observed:

```text
unique semantic verifications = 6
proposals                     = 5
burden                        = 6*32 + 5 = 197
terminal                      = REACHABLE_BUT_LOCAL_STRICT_IMPROVEMENT_BLOCKED_BY_PLATEAU
```

This is the registered separation between a local basin/plateau barrier and global developmental impossibility.

### 4. Encoding controls finite search burden

The frozen complete prefix code has lengths

```text
1,2,...,30,31,31.
```

Its Kraft sum is exact:

```text
sum_{l=1}^{30} 2^-l + 2*2^-31
= (1 - 2^-30) + 2^-30
= 1.
```

Two encodings preserve all candidate semantics while changing only which semantic mask receives which rank/code.

`ENC_SHORT` gives the target rank 0 and length 1:

```text
verifications = 1
decode/proposals = 1
burden = 33.
```

`ENC_LONG` gives the target rank 31 and length 31:

```text
verifications = 32
decode/proposals = 32
burden = 1056.
```

The target prior mass differs by exactly

```text
2^(-1) / 2^(-31) = 2^30.
```

This is parent-owned Levin/OOPS-style bias/description-length dependence. E1 does not rename it as GMI novelty.

### 5. Search can determine observed finite-budget recovery

At the prospectively frozen budget of 20 semantic verifications on the same target/ecology:

```text
Levin ENC_SHORT    -> recovered
one-bit BFS        -> not yet recovered (target is verification 21)
Levin ENC_LONG     -> not recovered
strict local       -> not recovered
```

At complete budget, one-bit BFS and both Levin encodings all recover the same target semantics.

Thus E1 distinguishes:

```text
final semantic target under complete search
```

from

```text
finite-budget observed recovery under a registered search/encoding.
```

The former is invariant here; the latter is not.

### 6. Disjoint input remint

The bit-coordinate remint `(2,4,1,0,3)` maps the target support to `{0,1,3}`, mask `11`.

The semantic invariants reproduce:

```text
target support size                    = 3
all non-target affine errors           = 16
pair-flip reachable component          = 16 even masks
pair-flip target reachable             = false
strict local terminal                  = plateau-blocked
one-bit graph                          = connected
```

But raw-order BFS burden changes exactly as frozen:

```text
source target: verification 21, proposals 100, burden 772
remint target: verification 18, proposals 85,  burden 661
```

This is not a remint failure. It is the intended evidence that semantic reachability class can be invariant while finite search burden changes with encoding/order.

## Formal sufficiency statements

For a finite candidate graph, ordinary graph reachability is necessary and sufficient for a complete graph-search method such as BFS to eventually visit the target, provided each reachable vertex is eventually expanded and the verifier terminates.

For the one-bit hypercube specifically, a path exists between every pair of masks because differing coordinates can be flipped one at a time.

For the pair-flip graph from zero, parity invariance supplies a necessary obstruction; enumeration confirms the even component has all 16 even masks, so in this registered graph parity is also a complete component classifier.

These are graph-theoretic parent results, not GMI theorems.

## Parent subtraction

Parents receive first refusal:

- Levin-style universal / prefix-prior search owns description-length/probability-biased scheduling.
- Schmidhuber OOPS/PowerPlay owns bias-optimal/incremental program-space search and reuse concepts.
- BFS and connected-component theory own graph reachability.
- Local-search / fitness-landscape theory owns plateau trapping.
- Genotype-phenotype and NAS encoding literature owns the fact that encoding/search-space choice can alter finite discovery performance.

The scoped GMI residual is procedural governance only:

1. predict the target morphology before search;
2. register development/search operators and encoding before outcomes;
3. audit target support/reachability;
4. charge every failed verification and proposal;
5. distinguish global impossibility, local barrier, and finite-budget failure;
6. require alternate search/encoding checks where ecology-determined recovery is claimed.

## Section E box disposition

At this finite exact scope, E1 supports:

- [x] Define developmental reachability formally.
- [x] Define morphology-search burden.
- [x] Separate representability from reachability.
- [x] Separate local basin barriers from global impossibility.
- [x] Derive sufficient conditions for reaching a morphology.
- [x] Derive search/encoding dependence bounds.
- [x] Construct worlds where the predicted best morphology is unreachable by a chosen developmental law.
- [x] Construct worlds where added developmental operators restore reachability.
- [x] Charge all failed-candidate/search cost.
- [x] Cross-search replication of recovered target semantics under complete budget.
- [x] Search-negative terminal when theory is right but the development law is demonstrably inadequate.

Not earned here:

- broad random/GP/CGP/evolutionary/NAS/gradient/meta-search comparison;
- four-family neutral recovery;
- four-family cross-grammar replication;
- real-scale reachability/search-cost transfer;
- a universal search or morphogenesis theory.

## Claim ceiling

```text
FINITE_EXACT_PROSPECTIVE_SECTION_E_REACHABILITY_AND_SEARCH_BURDEN_V1
PARENT_OWNED_LEVIN_OOPS_GRAPH_LOCAL_SEARCH_AND_ENCODING_BIAS
NO_NOVEL_SEARCH_ALGORITHM_OR_REAL_SCALE_MORPHOGENESIS_CLAIM
```
