# Formalization V1 — matched-negative successor controls

Issue: #786. Parents: #602 P0, #431, #433.

## Purpose and evidence order

`GMI_PROTOCOL_CONFORMANCE_AUDIT_V1.md` recorded measured matched negatives for 11/19 known-family witnesses. The old receipts also contained several scientifically useful contrasts, but those contrasts were not registered as prospective matched fail arms. This successor does not rewrite the historical audit. It freezes eight successor controls, commits their expected positive/fail directions, and only then creates independent scorers and surface remints.

Protected custody:

```text
freeze      a57664ec99b143f5c56fdd2f058d1a3aa5e16bb7
prediction  95e817f46a3224b6299013fdae47aaa0835c8f31
scorer      5c10b2d7466e43ee0f187b6429191885f14cb55d
result      379dd3a0da46405e154e774e354f05c5a1fccaf9
```

The prediction commit contains no scorer/result. The scorer does not import `predict_v1.py` and does not parse historical donor receipts as measured outcomes.

## Control logic

### N1 — information rank, not observation count

For exact coefficient vector `w in {-3,...,3}^4`, four standard-basis observations reveal all four coordinates and leave exactly one candidate. Replacing one basis vector by a duplicate leaves one coordinate unobserved; its seven grid values remain possible. Thus the matched `n=4` pair yields candidate counts `1` versus `7` solely from rank 4 versus rank 3.

### N2 — credit accumulation mode

On the fixed graph with `n_in=4`, `n_hid=1`, `P=4`, one forward pass costs `4+n_out` multiply-accumulates. Forward-mode repeats that pass once per parameter, so

```text
C_f = 4(4+n_out).
```

Reverse mode pays one forward pass plus, per output, one fixed-readout traversal and four parameter traversals:

```text
C_r = (4+n_out) + 5 n_out = 4 + 6 n_out.
```

Therefore `n_out=1` gives 20/10 (reverse), `n_out=6` gives 40/40 (tie), and `n_out=8` gives 48/52 (forward). Only output count changes.

### N3 — update law requires local signal

On the smooth coordinate-distance landscape, every gradient evaluation moves all three coordinates one step toward `(3,3,3)`, so three evaluations reach the target and charged cost is `3*3=9`. Uniform search over `4^3=64` points has exact without-replacement expectation `(64+1)/2=65/2`.

On the matched needle landscape every non-optimal point has equal value. From the same start, neither local nor gradient update has an improving move, while random search retains expectation `65/2`. Dimension, target, horizon and prices are fixed; only slope informativeness changes.

### N4 — variable duration forces conditional retention

A length-`L` unconditional shift register answers exactly the stream with gap `L-1`. Hence fixed gap 4 is solved by `L=5`. No single `L` can simultaneously equal `1`, `3`, and `5`, so no registered register solves gaps `{0,2,4}`. A one-cell conditional write stores the payload after the marker and holds it until the query, so it solves both ecologies. Both have the same maximum gap 4.

### N5 — transition structure controls affine realizability

Both arms use four states and two-bit codes. For the positive four-cycle, the natural binary code is an explicit witness: symbol `a` uses identity matrix/bias zero; symbol `b` is realized over GF(2) by

```text
A = [[1,0],[1,1]], c=(1,0).
```

For the fail arm, symbol `b` has fibers of sizes 3 and 1. Any affine map on a finite vector space has equal-sized nonempty fibers (cosets of its kernel), so no bijective state coding can make that update affine. This gives an algebraic negative independent of the scorer's exhaustive code/matrix search.

### N6 — local lookup depends on metric smoothness

On the 4-bit Hamming cube with `k=1`, exhaustive subset search finds a four-case sufficient set for the threshold obligation and no sufficient set of size at most eight for parity. The result is invariant under all feature-coordinate permutations because Hamming distance and both obligations are coordinate-symmetric. The scorer checks two post-prediction permutations; the independent tests exhaust all 24.

### N7 — dependence, not sparsity, breaks factorization

The positive 3x3 joint is uniform (`1/9` each). The fail joint has diagonal `1/6` and off-diagonal `1/12`. Both have all nine cells nonzero and exactly uniform `1/3` row and column marginals. The fail joint cannot factorize because, for example, `p(0,0)=1/6 != (1/3)(1/3)=1/9`. Thus dimensions, support cardinality, marginals and storage prices are matched; only dependence differs.

### N8 — heuristic information, not price or search world

A complete ternary tree of depth 4 has

```text
1+3+9+27+81 = 121
```

nodes. The goal is the last semantic leaf `(2,2,2,2)`. With a constant heuristic and insertion-order ties, best-first degenerates to breadth-first and expands all 121 nodes. The informative heuristic assigns finite decreasing priority only to prefixes of the goal and therefore expands root plus four goal-prefix nodes: 5 total. Both arms pay heuristic price 1 per expanded node, so charged work is 242 versus 10.

## Remints and matching

Concrete labels/permutations are derived only from the prediction-authority commit. Two independent domain separators are used. Every case has a machine-readable `matched_fields` list equal to every common semantic coordinate and exactly one declared `varying_coordinate`. An arm that overrides any matched field is rejected before scoring.

## Protected result

All eight controls matched their frozen expected values on both post-prediction remints. Prediction-tamper, positive/fail expected-label swap, second-coordinate mutation, and family-label injection hostiles all fired.

The successor therefore supplies eight exact matched controls in addition to the historical 11/19 audit count:

```text
11 historical measured controls + 8 prospective successor controls = 19/19
```

Earned terminal:

```text
B1_MATCHED_NEGATIVE_CONTROLS_MEASURED_19_OF_19_AT_REGISTERED_EXACT_SCOPE
```

This is a successor-coverage statement, not a rewrite of the historical audit.

## Claim boundary

This closes only the matched-negative-control column at the registered exact scope. It does not make the entire B1 common protocol green. In particular, all-family pre-outcome prediction, cross-grammar recovery and real-regime replication remain open; the historical audit's 0/19 real-regime count is unchanged.

Forbidden from this result alone:

```text
B1_COMMON_PROTOCOL_CLOSED
KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE
ALL_KNOWN_FAMILIES_PROSPECTIVELY_VALIDATED
REAL_REGIME_REPLICATION_COMPLETE
COMPLETE_GMI
```
