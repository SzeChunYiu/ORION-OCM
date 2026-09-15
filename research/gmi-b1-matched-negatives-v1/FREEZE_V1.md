# Freeze V1 — prospective matched-negative controls for known-family protocol

Issue: #786. Parents: #602 P0, #431, #433.

**Pre-outcome authority.** This commit freezes eight successor control objects, their matching contracts, expected positive/fail directions, remint rules, falsifiers, and claim ceiling. At this commit there is no successor prediction receipt, no successor scorer/oracle, no protected result, and no workflow for this capsule.

## Pinned base and historical donors

Base `main`:

```text
54eea90557619b3864cb0cd5c0804942ee7dd67a
```

Historical protocol audit:

```text
research/machine-intelligence-morphogenesis-v1/GMI_PROTOCOL_CONFORMANCE_AUDIT_V1.md
blob b9342f41dcdcef22fd26e540603a4248d00e18d5
```

The audit's historical matched-negative count remains 11/19. This successor never edits that fact.

Pinned donor receipts:

```text
B3  STAGE_LINEAR_FAMILY_V1.json         94f36f3f294836963b9c933e0a42a9df8db97ec7
B4c STAGE_CREDIT_ASSIGNMENT_V1.json     19ac9ca341e86a3d0c32a645b1c9ef7277ac6f2e
B4u STAGE_UPDATE_LAW_V1.json            1970103336cd25a1c74a86128dc9b4e1fc57fae6
B6  STAGE_GATED_RECURRENCE_V1.json      a125dcfcbdaa6204c392664d4adc26946d5bde9d
B9  STAGE_STATE_SPACE_V1.json           811581d1b2ebcacada89b66539e66884f4dc98d0
B11 STAGE_EXEMPLAR_PARAMETRIC_V1.json   6bbfcb6aa33d5d068546df3a07b58f1a91b5816a
B13 STAGE_BELIEF_STATE_V1.json          0555b9348565aa0e832a05744e2d37309129c410
B16 STAGE_SEARCH_FRONTIER_V1.json       4efacaca13300cfffcdb78d6b15c0dcb53b63a90
```

Pinned donor implementations where the successor preserves an exact accounting convention:

```text
linear_family_witness.py       2d2656deed99d4aa603e8d7ec622a4fa706fb147
credit_assignment_witness.py   c00b06712aa65f9447bfdbfbacf1e8004f14626e
update_law_witness.py          5b6b168079704dd8682a876567b4d427f87d1629
gated_recurrence_witness.py    f3fb7dc133689b41ceecab19536577782d820d3d
state_space_witness.py         5217ee011569cf07f937da8ef556d4dbf4478265
exemplar_parametric_witness.py 4bfbd65703d425b53395d2f900f267e29f3201af
```

Donor outputs are **design donors only**. The successor scorer may not parse donor result values as measured outcomes.

## Common two-phase protocol

Evidence order is mandatory:

```text
FREEZE_V1 commit
  -> prediction-only implementation + PREDICTIONS_V1.json commit
  -> successor scorer/remint implementation
  -> RESULT_V1.json commit
  -> CI/replay hardening
```

The prediction receipt contains expected positive/fail verdicts but no measured successor outcomes. The scorer must be absent at the prediction-authority commit and may not import/call the prediction implementation.

Predictor-visible rows use only generic mathematical object kinds and semantic parameters. Family names, architecture names, donor paths, measured values, and phenotype labels are forbidden inside case rows.

## Common remint rule

Concrete surface labels do not exist until after the prediction receipt is committed. The scorer derives two surfaces from the prediction-authority commit using domain-separated SHA-256 labels:

```text
surface_label(domain, case_id, semantic_index, remint)
  = prefix + SHA256(
      "T602-B1N-V1|" + domain + "|" + prediction_commit + "|" +
      case_id + "|" + semantic_index + "|" + remint
    )[:12]
```

Surface permutations/names may change; semantic parameters below may not. Both remints must produce identical verdicts and exact measured invariants.

---

## C1 — finite coefficient identification

Generic object kind: `finite_coefficient_identification_control`.

Frozen semantics:

```text
d = 4
coefficient grid = {-3,-2,-1,0,1,2,3}
true w = (2,-1,3,0)
response y = <w,x>
observation count n = 4 in both arms
```

Positive arm: four independent standard-basis observations, rank 4.

Fail arm: three distinct standard-basis observations plus a duplicate of the first, rank 3.

Matching fields: `d`, coefficient grid, true vector, response channel, observation count, observation values/prices. The only declared varying coordinate is observation rank/independence.

Frozen expectations:

```text
positive consistent candidate vectors = 1
positive identified = true
fail consistent candidate vectors = 7
fail identified = false
```

Falsifier: the fail arm identifies uniquely or the positive arm remains ambiguous.

## C2 — credit accumulation

Generic object kind: `parameter_output_credit_control`.

Use the donor graph/accounting convention exactly:

```text
y_k = sum_j V[k,j] * relu(sum_i W[j,i] * x_i)
W parameterized; V fixed
n_in = 4
n_hid = 1
P = 4 parameters
x = all ones
```

Only `n_out` varies:

```text
positive/reverse arm: n_out=1
boundary arm:         n_out=6
fail/forward arm:     n_out=8
```

Forward accumulation executes one full forward pass per parameter. Reverse accumulation executes one forward pass plus one backward traversal per output, with the same multiply-accumulate counter as the pinned donor.

Frozen expectations:

```text
n_out=1: forward=20 reverse=10 winner=reverse
n_out=6: forward=40 reverse=40 winner=tie
n_out=8: forward=48 reverse=52 winner=forward
```

Matching fields: graph equation, input width, hidden width, parameterized block, parameter count, input values, operation accounting. Only output count varies.

Falsifier: reverse remains cheaper at `n_out=8`, forward wins at `n_out=1`, or the boundary is not an exact tie.

## C3 — slope-informative update law

Generic object kind: `finite_update_landscape_control`.

Frozen common semantics:

```text
parameter dimension d=3
coordinate values {0,1,2,3}
target=(3,3,3)
start=(0,0,0)
update horizon=16 evaluations
per-evaluation prices: random=1, local=1, gradient=3
```

Only the landscape signal varies:

```text
positive smooth(theta) = -sum_i |theta_i-target_i|
fail needle(theta) = 0 at target, -1 everywhere else
```

Use the donor update procedures: uniform search without replacement; local +/-1 hill climbing; gradient rule that reads all coordinate slopes and moves every improving coordinate at once.

Frozen expectations:

```text
smooth: gradient reaches in 3 evaluations; charged cost 9; random expectation 65/2; gradient cheaper than random
needle: gradient cannot move/reach; local cannot move/reach; random expectation remains 65/2
```

Matching fields: dimension, domain, target, start, horizon, prices and update procedures. Only slope informativeness/landscape response varies.

Falsifier: gradient reaches the needle from the frozen start or fails to reach the smooth target within the frozen horizon.

## C4 — variable-duration retention

Generic object kind: `conditional_retention_control`.

Alphabet semantics: marker `M`, payload bit, filler `0`, query `Q`. Stream is `M,payload,0^gap,Q`; demanded answer at Q is payload.

Common semantics:

```text
maximum gap = 4
payloads = {0,1}
register lengths searched = 1..8
same shift-register and one-cell conditional-write semantics
same gate price (2) when costs are reported
```

Only duration variability differs:

```text
positive-for-register / fail-for-gating-necessity: gap set {4}
positive-for-gating-necessity: gap set {0,2,4}
```

Frozen expectations:

```text
fixed gap {4}: working register lengths = [5]; gated cell works; conditional write is not required for solvability
variable {0,2,4}: no register length 1..8 works; gated cell works; conditional write is required within the registered candidate class
```

Falsifier: any frozen register solves all variable-gap streams or no register solves the fixed-gap streams.

## C5 — affine compressed-state update

Generic object kind: `finite_transition_affinity_control`.

Both arms have exactly four carrier states, binary alphabet of two symbols, and two-bit state encodings. Only the transition structure varies.

Positive transition object:

```text
symbol a: q -> q
symbol b: q -> (q+1) mod 4
```

Fail transition object:

```text
on a: 0->1, 1->1, 2->1, 3->1
on b: 0->3, 1->2, 2->3, 3->3
```

The scorer must exhaust every injective assignment of the four semantic states to two GF(2) bits and every per-symbol affine map `A x + c`.

Frozen expectations:

```text
positive: some coding makes every symbol update affine
fail: no coding makes both symbol updates affine
```

Matching fields: number of carrier states, alphabet size, encoding width, search space over codes/matrices/biases. Only transition structure varies.

Falsifier: both objects receive the same affine-realizability verdict.

## C6 — local exemplar sufficiency

Generic object kind: `metric_local_lookup_control`.

Common semantics:

```text
universe = {0,1}^4
metric = Hamming distance
k = 1 nearest held case
subset cap = 8
same deterministic distance/surface tie-break
```

Only the obligation's smoothness in that metric varies:

```text
positive obligation: 1[sum(x)>=2]
fail obligation: sum(x) mod 2
```

The scorer must exhaust subsets in increasing size and test every query.

Frozen expectations:

```text
threshold obligation: smallest sufficient held subset size = 4
parity obligation: no sufficient subset of size <=8
```

Matching fields: universe, metric, k, cap, storage/lookup semantics. Only response geometry varies.

Falsifier: parity has a sufficient subset at or below the cap or threshold has none.

## C7 — probabilistic factorization

Generic object kind: `finite_joint_factorization_control`.

Both arms are 3x3 rational joints, have all 9 cells nonzero, identical uniform row and column marginals, full storage cost 9 and factored-marginal storage cost 6. Only dependence structure varies.

Positive independent joint:

```text
every cell = 1/9
```

Fail dependent full-support joint:

```text
diagonal cells = 1/6
off-diagonal cells = 1/12
```

Both have row/column marginals `1/3` exactly. The scorer must compute marginals and test `p(i,j)=p(i)p(j)` with exact rational arithmetic.

Frozen expectations:

```text
positive factorizes = true; factorized storage legal = true
fail factorizes = false; factorized storage legal = false
```

This successor deliberately improves on the sparse diagonal donor by keeping support cardinality and marginals matched, so sparsity cannot explain the verdict.

Falsifier: the dependent full-support joint factorizes or the independent joint does not.

## C8 — heuristic informativeness

Generic object kind: `finite_search_heuristic_control`.

Common search world is a complete 3-ary rooted tree of depth 4:

```text
node count = 1+3+9+27+81 = 121
goal semantic path = (2,2,2,2)
child generation order = 0,1,2
best-first queue ties by insertion order
heuristic evaluation price = 1 per expanded node
```

Only heuristic informativeness varies.

Positive heuristic: for a node that is a prefix of the goal, return remaining depth; otherwise return 100. This prioritizes the unique goal-prefix path.

Fail heuristic: constant zero everywhere.

Frozen expectations:

```text
positive expansions to goal = 5
positive charged work = 10
fail expansions to goal = 121
fail charged work = 242
positive reduces verified expansions relative to fail = true
```

Matching fields: graph, goal, best-first algorithm, child order, tie-break, heuristic price. Only heuristic values/informativeness vary.

Falsifier: constant heuristic expands fewer than the full 121-node tree under the registered ordering or informed heuristic does not reach in 5 expansions.

---

## Matching checker

Every successor case must carry a machine-readable list of `matched_fields` and exactly one `varying_coordinate`. A hostile that mutates one additional matched field must be rejected before scoring.

## Prediction receipt contract

`PREDICTIONS_V1.json` must contain the generic semantic parameters and exact frozen expectations above, plus:

```text
outcomes_seen=false
scorer_exists=false
surface_remints_materialized=false
```

No donor measured outcomes may appear as successor measured fields.

## Independent scoring contract

The later scorer is a new file absent from the prediction commit. It must reconstruct outcomes from the frozen semantics:

- C1 literal candidate-vector enumeration;
- C2 explicit graph execution counters;
- C3 exact update-law execution with rational costs;
- C4 exhaustive streams/register lengths;
- C5 exhaustive GF(2) code/matrix/bias search;
- C6 exhaustive held-subset search;
- C7 exact rational marginal/factorization check;
- C8 explicit best-first traversal.

An independent test oracle must use alternate reasoning paths where practical (rank/free-coordinate, closed-form operation counts, algebraic transition properties, direct factorization identities, tree counting).

## Required hostiles

1. prediction expected verdict/value tamper -> mismatch;
2. positive/fail label swap -> mismatch;
3. second matched field mutation -> matching-contract rejection;
4. family/architecture label injection -> rejection;
5. scorer imports/calls prediction implementation -> rejection;
6. donor result used as successor measured outcome -> source/static rejection;
7. remint changes a semantic verdict -> failure;
8. post-outcome edit to freeze/prediction authority -> Git custody failure.

## Acceptance and claim ceiling

All eight controls must match on both post-prediction surface remints and all hostiles must fire.

If GREEN, the strongest allowed terminal is:

```text
B1_MATCHED_NEGATIVE_CONTROLS_MEASURED_19_OF_19_AT_REGISTERED_EXACT_SCOPE
```

This means: historical audit had 11/19 measured matched negatives; this successor supplies eight prospectively registered exact matched controls covering the remaining audited witnesses. The historical audit remains historical and is not rewritten.

This still does **not** establish all-family prospective prediction, all-family neutral recovery, cross-grammar replication, or any real-regime replication. In particular, the audit's 0/19 real-regime result remains a separate blocker.

Forbidden from this child alone:

```text
B1_COMMON_PROTOCOL_CLOSED
KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE
ALL_KNOWN_FAMILIES_PROSPECTIVELY_VALIDATED
REAL_REGIME_REPLICATION_COMPLETE
COMPLETE_GMI
```
