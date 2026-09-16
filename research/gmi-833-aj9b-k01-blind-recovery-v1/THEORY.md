# AJ9b — first frozen blind known-family recovery

## Scientific question

Can the frozen AJ operational/process programme recover a registered known machine-intelligence family **without giving generation, search, or evaluation the family name, fingerprint, architecture macro, or family-specific score**?

This tranche tests only frozen benchmark family `K01`; AJ9 as a whole remains open until all registered families are adjudicated.

## Freeze and separation

The generic search configuration was frozen at commit `42fb250c9b139e8fed51c8882cbfc3d9879f6420`; the freeze marker commit is `5324b806afc06ff392b81e810aa86bc74921df4b`. At that commit, neither search implementation nor outcome nor post-hoc adjudicator existed.

The blind generator receives only:

- four two-bit observations and required outputs;
- generic constants `-1,0,1`;
- addition, negation, and a positive-value test;
- exact behavior evaluation;
- raw resources `(operation_nodes, positive_tests, depth, constant_uses)`;
- search budget `operation_nodes <= 7`.

It does not read the frozen family registry.

## Two materially different searches / presentations

1. `SIZE_LAYERED_SYNTAX_ENUMERATION` builds canonical tree expressions by exact operation count.
2. `SEMANTIC_COST_CLOSURE` independently constructs minimum-cost semantic values in postfix stack encoding.

Both first reach the protected output vector `(0,1,1,0)` at operation cost 7. Both have raw resource vector:

`(operation_nodes=7, positive_tests=2, depth=5, constant_uses=1)`.

No exact semantic candidate exists below operation cost 7 in the complete frozen closure. The number of newly reachable semantic vectors by cost is:

`[5, 11, 26, 39, 67, 88, 105, 118]`.

One recovered tree is, in generic process notation,

`POS(x0+x1) + NEG(POS(x0+x1-1))`.

This description is explanatory only; the blind search itself contains no family label.

## Post-hoc adjudication

Only after `BLIND_OUTCOME_V1.json` is committed does `posthoc_adjudicate_v1.py` read the frozen AJ9a benchmark Git blob `6b9ac3095c90d74e2717671a70ad7cc18955310c`.

For each of the two independently generated encodings it verifies:

- exact protected I/O;
- directed acyclic multi-stage composition;
- at least two distinct numeric mixing sites feeding the same generic non-affine test construction;
- both incoming signals causally contribute to at least two such sites;
- an internal non-affine response witness;
- reuse of the generic mixing/test pattern across multiple internal sites.

The recovered internal response witnesses are the Boolean OR-like and AND-like responses `(0,1,1,1)` and `(0,0,0,1)`, combined downstream to realize the protected mapping.

Under the frozen K01 post-hoc structural-mechanism fingerprint, both searches terminate `RECOVERED`.

## What this proves

At the registered finite scope, a family-hidden generic process search can independently produce an organization that satisfies the frozen post-hoc K01 structural fingerprint. This is stronger than compiling a known recipe because the target fingerprint is unavailable to generation/search/evaluation and the outcome is frozen before adjudication.

## What this does not prove

- It does not derive all neural networks or all feed-forward architectures.
- It does not derive training, gradient descent, reverse-mode differentiation, or backpropagation.
- It does not earn `PREDICTED_SELECTED`; no pre-search morphology-selection prediction was registered.
- It does not prove that this generic primitive basis is unbiased; AJ0/AJ5 and earlier grammar-bias results explicitly forbid that reading.
- It does not close AJ9 until K02–K11 also undergo the registered holdout protocol.
- It does not establish real-scale usefulness.

## Claim ceiling

`AJ9B_K01_BLIND_STRUCTURAL_RECOVERY_AT_FROZEN_FINITE_SCOPE`
