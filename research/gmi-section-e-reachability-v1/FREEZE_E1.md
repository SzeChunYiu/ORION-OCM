# Section E reachability / search-burden freeze E1

Date frozen: 2026-09-15.
Owner: #602 Section E. Child tracker: #710.

This file is the **pre-outcome authority** for E1 and is committed before the scored witness, receipt, tests, or result/proof file.

## Claim boundary

This experiment does not invent a search algorithm. Search mechanisms and encoding effects are parent-owned by Levin-style universal search, OOPS/PowerPlay, graph search, local-search/fitness-landscape theory, genotype-phenotype encoding theory, and NAS search-space/encoding theory.

The candidate GMI residual is only: a morphology target predicted before search, exact developmental reachability, complete charged search burden, and prospectively predicted success/failure across registered development laws and search encodings.

Claim ceiling:

```text
FINITE_EXACT_PROSPECTIVE_SECTION_E_REACHABILITY_AND_SEARCH_BURDEN_V1
PARENT_OWNED_LEVIN_OOPS_GRAPH_LOCAL_SEARCH_AND_ENCODING_BIAS
NO_NOVEL_SEARCH_ALGORITHM_OR_REAL_SCALE_MORPHOGENESIS_CLAIM
```

## Frozen world and candidate grammar

Inputs are all 32 five-bit strings. Protected obligation:

```text
y(x)=x0 XOR x2 XOR x4.
```

Candidate masks are the 32 homogeneous affine support masks

```text
f_m(x)=XOR_{i:m_i=1} x_i.
```

Target mask is support `{0,2,4}`, integer `21`.

Exact semantic verification checks all 32 inputs. Frozen prediction:

- target error = 0;
- every non-target support mask error = 16.

The latter follows because the XOR of target and any distinct affine mask is a nonzero linear form, balanced over the Boolean cube.

## Frozen formal objects

For operator set `O` and start `s0`, `Reach_O(s0)` is the vertex set reachable in the candidate graph. Target morphology is reachable iff its phenotype preimage intersects this set.

Search burden is

```text
B = 32 * unique_semantic_verifications
  + 1  * proposal_attempts
```

Proposal attempts include duplicates later filtered by a visited set. No failed candidate is free. The inherited start description still pays semantic verification.

## E1-R1: representable but operator-unreachable

Start support = 0. `O_pair` flips exactly two support bits per step.

Predictions:

- Hamming-weight parity is invariant;
- reachable component from zero has 16 even-parity masks;
- target has odd weight 3 and is absent;
- exhaustive pair-flip BFS: 16 unique verifications, 160 proposal attempts;
- burden = `16*32+160=672`;
- terminal = `SEARCH_NEGATIVE_TARGET_REPRESENTABLE_BUT_OPERATOR_UNREACHABLE`.

## E1-R2: operator restoration

Add one-bit flips `O_single`. The five-cube is connected. Registered path:

```text
00000 -> 00001 -> 00101 -> 10101
```

using the witness's integer bit convention.

BFS with neighbor order bits `0,1,2,3,4` predicts:

- target is the 21st unique candidate verified;
- 100 proposal attempts before terminal;
- burden = `21*32+100=772`.

## E1-R3: local plateau distinct from global impossibility

Strict-improvement local search on the connected one-bit graph uses exact semantic error and accepts only a strict decrease.

Prediction:

- start error 16;
- all five one-bit neighbors error 16;
- no first move is accepted although the target is graph-reachable;
- 6 unique verifications, 5 proposals;
- burden = `6*32+5=197`;
- terminal = `REACHABLE_BUT_LOCAL_STRICT_IMPROVEMENT_BLOCKED_BY_PLATEAU`.

## E1-R4: prefix encoding / bounded Levin-style parent

Freeze a complete prefix code over 32 semantic masks. Ranks 0..29 have lengths 1..30; ranks 30 and 31 have length 31. Kraft sum is 1.

Two semantic-preserving rank encodings:

- `ENC_SHORT`: target rank 0, length 1;
- `ENC_LONG`: target rank 31, length 31.

The bounded Levin-style parent orders candidates by increasing `2^length`, then frozen rank. Each decoded-and-tested candidate pays 1 decode/proposal + 32 semantic checks.

Predictions:

- short: target first, burden 33;
- long: target last, burden `32*33=1056`;
- target prior-mass ratio short/long = `2^30`.

## E1-R5: finite-budget search dependence

At budget 20 semantic verifications:

- Levin short succeeds;
- one-bit BFS fails because target verification index is 21;
- Levin long fails;
- strict-improvement local search fails.

At complete budget, one-bit BFS and both Levin encodings recover identical target semantics. E1 therefore tests search-dependent observed recovery/non-recovery, not a claim that the final exhaustive target identity changes.

## E1-R6: disjoint input remint

Bit-coordinate remint is

```text
(2,4,1,0,3).
```

The target support becomes `{0,1,3}`, integer `11`.

Predictions:

- target weight remains 3;
- all non-target affine errors remain 16;
- pair-flip component remains size 16 and excludes target;
- one-bit graph remains connected;
- strict local search remains plateau-blocked;
- raw-order one-bit BFS now verifies target at index 18 with 85 proposal attempts.

This changed BFS index is an intended demonstration of encoding/order-sensitive finite burden, not a failure of semantic remint invariance.

## Box disposition if every prediction passes

At registered finite scope E1 may support:

- developmental reachability formalization;
- morphology-search burden formalization;
- representability vs reachability separation;
- local barrier vs global impossibility separation;
- sufficient reachability conditions;
- search/encoding dependence bounds;
- unreachable-best world under chosen development law;
- operator-restored reachability;
- complete failed-search cost charging;
- search-negative terminal;
- cross-search recovery of the same target semantics under complete budget.

E1 does **not** claim full random/GP/CGP/evolutionary/NAS/gradient/meta-search comparison, four-family neutral recovery, four-family cross-grammar replication, real-scale costs, or universal morphogenesis.
