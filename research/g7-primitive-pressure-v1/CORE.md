# G7 primitive pressure at registered miniature scope

Issue [#165](https://github.com/SzeChunYiu/ORION-OCM/issues/165) final-checklist
Development box: **“primitive pressure tracked.”** Coordinator
[PR #206](https://github.com/SzeChunYiu/ORION-OCM/pull/206).

G7 D1–D6 already exist and emit `PHASED_COGNITIVE_DEVELOPMENT`. This capsule
**cites** those receipts. It does **not** overwrite them, does **not** rerun
the lineage, and does **not** manufacture generations by relabeling historical
M11 `g0 → g1 → g2 → g2`.

**This capsule’s terminal:** see [`RESULT.json`](RESULT.json). Allowed:

```text
PRIMITIVE_PRESSURE_DECLINES_AT_SCOPE
PRIMITIVE_PRESSURE_PERSISTS
PARENT_SUFFICIENT
```

Not programme-wide developmental close. Not #73.

## Predecessors (cited, not overwritten)

| capsule | terminal | role |
|---|---|---|
| [`research/g7-lineage-v1`](../g7-lineage-v1/CORE.md) | `PHASED_COGNITIVE_DEVELOPMENT` | T0–T1 |
| [`research/g7-lineage-d2-v2`](../g7-lineage-d2-v2/CORE.md) | `PHASED_COGNITIVE_DEVELOPMENT` | through T2 |
| [`research/g7-lineage-d3-v3`](../g7-lineage-d3-v3/CORE.md) | `PHASED_COGNITIVE_DEVELOPMENT` | through T3 |
| [`research/g7-lineage-d4-v4`](../g7-lineage-d4-v4/CORE.md) | `PHASED_COGNITIVE_DEVELOPMENT` | through T4 |
| [`research/g7-lineage-d5-v5`](../g7-lineage-d5-v5/CORE.md) | `PHASED_COGNITIVE_DEVELOPMENT` | through T5 |
| [`research/g7-lineage-d6-v6`](../g7-lineage-d6-v6/CORE.md) | `PHASED_COGNITIVE_DEVELOPMENT` | through T6; primary table |

Primary numbers come from the D6 `transitions[]` table (seven earned
`DevelopmentTransitionV1` records, one lineage id). Prior RESULT files are
hashed and required to remain `PHASED_COGNITIVE_DEVELOPMENT` on the same
lineage. SHA-256 pins live in `experiment.py`.

## Question

Does the fraction of competence that requires **new hand-authored primitives**
decline across those earned transitions, **versus reset**, at this registered
miniature microscope?

Theory (`P_t` new primitive pressure): later related cognition should need
fewer newly authored operators, or the pressure should become phased. Reset
must re-import the whole donor stack at every stage.

## Registered metric (frozen before the terminal)

Hand-authored primitive identities:

- T0 (`EMPTY → OCM_0`): `imported_donor_identities` (seed taught primitives;
  `primitive_operators_added` is empty because they are seed, but they are
  new at EMPTY).
- Later: `primitive_operators_added`, excluding `donor:already-earned:*`
  (already-earned methods, not new primitives).

Let `n_new(t)` be that count and `n_cum(t)` the cumulative unique count
through `t`. Competence `Q(t)` is the number of verified
`actual_execution_witnesses`.

**Primary** (stack fraction, in `[0,1]`):

```text
P_stack_continued(t) = n_new(t) / n_cum(t)
P_stack_reset(t)     = 1
```

Reset starts empty, so every primitive in the cumulative stack is newly
(re-)authored at that episode.

**Secondary** (competence intensity):

```text
P_comp_continued(t) = n_new(t) / Q(t)
P_comp_reset(t)     = n_cum(t) / Q(t)
```

## Decision rule (pre-registered)

`PARENT_SUFFICIENT` if `P_stack_continued(t) = P_stack_reset(t)` for every `t`
(no continued-versus-reset contrast).

`PRIMITIVE_PRESSURE_DECLINES_AT_SCOPE` if all of:

1. seven earned transitions on lineage `orion-ocm-g7-lineage-v1:microscope-d0-d1`;
2. `P_stack_continued(T6) < P_stack_continued(T0)`;
3. mean first difference of `P_stack_continued` is negative;
4. Kendall τ of `(stage index, P_stack_continued)` is negative;
5. `P_stack_continued(t) < P_stack_reset(t)` for every `t ≥ T1`.

Otherwise `PRIMITIVE_PRESSURE_PERSISTS`.

A T2/T6 family-injection bump is allowed. The rule is **net** decline versus
reset, not monotonicity. That is the theory’s “↓ or becomes phased” reading
at this scope, not a programme-wide evolvability law.

Ordinary-parent mechanism ties (`parent_ties_continued_mechanism`) are
recorded. They do **not** by themselves emit `PARENT_SUFFICIENT` here: the
question is continued versus reset, not OCM versus the ordinary library.

## What this does not claim

- Not `PHASED_COGNITIVE_DEVELOPMENT` as **this** capsule’s terminal (already
  earned by D1–D6).
- Not `DEVELOPMENTAL_CROSS_FAMILY_TRANSFER_SUPPORTED`.
- Not Metamath / FLT / #73 / M11 relabel / constitution mutation.
- Not production `src/` change.
- Not programme-wide `DEVELOPMENTAL_EVOLVABILITY_SUPPORTED`.

## Reproduction

```sh
python3 -B -m unittest discover -s research/g7-primitive-pressure-v1 -p 'test_*.py' -v
python3 -B research/g7-primitive-pressure-v1/experiment.py \
  --out research/g7-primitive-pressure-v1/RESULT.json
```
