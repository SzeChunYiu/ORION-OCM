# Section-M hierarchy / planning / causal re-audit — implementation v1

Package: `research/gmi-833-cognitive-reaudit-v2-implementation-v1`.
Issue #833 Section M ("Cognitive-function derivation upgrade").
Freeze: `research/gmi-833-cognitive-reaudit-v2/FREEZE_V1.md`
(PR #927, commit `cb6d6a590535e8660559b143cbe32308a880c482`).
Allowed terminal:
`GMI_833_HIERARCHY_PLANNING_CAUSAL_REAUDIT_AT_REGISTERED_EXACT_SCOPE`.
Evidence level EV2, maturity M2. Verdict GREEN.

This is the implementation tranche of the #926/#927 freeze. It closes exactly
three rows:

- `Re-audit hierarchical skills/chunking.`
- `Re-audit planning and stopping.`
- `Re-audit causal cognition/intervention/counterfactuals.`

It does not touch metacognition, social cognition, communication, imitation,
teaching, culture, empirical validation, or any comment/addendum row.

## The three closures

| row | result | what is registered |
|---|---|---|
| hierarchy | re-frame + register of `gmi-hierarchical-chunking-repair-v1` | hierarchy is a charged reuse policy, not an anatomical or universal-depth primitive: exact fixed-dictionary parsing (shortest path) and exact finite acyclic acquisition (min-plus DP over retained sets) with complete acquisition/validation/storage/lookup/transport/execution charges; greedy-longest-match failure and a hierarchy-loses workload are registered hostiles |
| planning | **the genuinely new result** | PS-1: on a finite acyclic computation graph with all costs charged, stopping is optimal exactly when the best registered terminal action value is at least every cost-charged continuation value computed with future optimal computation included (Bellman comparison, exact rational, independently confirmed by full-policy enumeration of all 48 policies per instance, 144 across hostile/clean/tie). PS-2: a merely myopic one-step EVC rule is not generally sufficient — registered hostile (X = f1 XOR f2, cost 1/8) stops under myopic EVC yet a two-step information plan has strictly positive net value +1/4; k=1 clean variant does not alarm; ties remain sets; missing goal/model and cyclic graphs refused |
| causal | re-frame + register of `gmi-causal-rung-repair-v1` | causal answers are fiber-relative: evidence identifies a target exactly iff it is constant on the compatible-model fiber; terminating identified / partially-identified / incompatible finite-class procedure with attaining endpoint witnesses (Tian–Pearl sharp PN bounds, constructive attainment); observation-equivalent models with different intervention/counterfactual targets, incompatible-evidence and undefined-conditioning refusals, and an identified constant-on-fiber control |

All three rows are re-parented to the upgraded #833 foundation
(`c0c574c4ec6e237d5fdafa694eac131399625a70`) and axiom core
(`3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9`): the result blobs are pinned
and the Python objects are actually imported and exercised (foundation
forbidden-promotion registry, prior taxonomy, Pareto certificate; axiom-core
finite model, hostile hypercube, dependency graph, claim governance). The
three legacy packages are pinned by their frozen blobs and replayed
byte-exactly (isolated `-I -B` replay reproduces their committed receipts).

## Verdict rule

The registered result is RED if it erases first-use or descendant charges,
treats a named option/macro/planner/causal algorithm as a primitive, derives
goals from value-free dynamics, silently breaks optimal ties, equates one-step
EVC with general optimal stopping, reports a point outside a singleton causal
target fiber, accepts parent drift, or uses floating-point decisions.

## Reproduce

```bash
python3 -I -B  research/gmi-833-cognitive-reaudit-v2-implementation-v1/executor_v1.py
python3 -I -O -B research/gmi-833-cognitive-reaudit-v2-implementation-v1/executor_v1.py
python3 -I -B  research/gmi-833-cognitive-reaudit-v2-implementation-v1/test_reaudit_v1.py -v
python3 -I -O -B research/gmi-833-cognitive-reaudit-v2-implementation-v1/test_reaudit_v1.py -v
python3 -I -B  research/gmi-833-cognitive-reaudit-v2-implementation-v1/replay_v1.py
```

Both executor modes must write a byte-identical `RESULT_V1.json`; the CI
workflow `cmp`s the generated output against the committed file. Stdlib only;
exact `Fraction` arithmetic throughout; a test enforces that no float literal
exists in any package source file. Parent blobs are pinned in
`MANIFEST_V1.json` and re-checked at run time — parent drift is a red result.
The package's `FREEZE_V1.md` is a byte-identical copy of the canonical freeze
(sha256 `5f457a7f2fa6af1fce554e29e90df4ee3afd58c1cd6656418fcdfbde76bd3e2c`,
git blob `b436513f28b06269c060a34c0ac635e44a23ce63`); the CI freeze-custody
step proves every implementation artifact postdates the freeze commit in git
order.

## Demarcations

- `gmi-833-cognitive-reaudit-social-v1` owns metacognition, social cognition,
  communication, imitation/teaching, cultural accumulation — this package
  explicitly lists those rows as not owned.
- Memory, attention, concept formation are owned by PR #919 / #917.
- The within-lifetime library formation and reuse-transfer rows are owned by
  #897; this tranche is Section-M re-audit only.
