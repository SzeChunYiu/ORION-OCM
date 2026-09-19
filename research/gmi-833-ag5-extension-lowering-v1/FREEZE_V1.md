# FREEZE — `gmi-833-ag5-extension-lowering-v1`

Committed **before** any executor, oracle, test, receipt or workflow file of this package.
Nothing below may be edited after the first implementation commit; a later correction must
arrive as a new file that cites this one.

## Custody

| field | value |
|---|---|
| `source_main` | `5e57d4292266bccf435136e1f7d72caa32e920a0` |
| issue | `SzeChunYiu/ORION-OCM#833` |
| sections | AG2 (one row), AG5 (three rows) |
| comment | `5693520829` |
| claim ceiling | `AG5_G0_EXTENSION_OPERATORS_LOWERED_AND_STATUS_ADJUDICATED_AT_REGISTERED_FINITE_SCOPE` |

## The exact rows this tranche may reconcile

Byte-exact from comment `5693520829` at `source_main`. No other row of any section is in scope.

Anchor `### AG2 — Signature before grammar`:

```
- [ ] Audit every `G0` instruction (`READ/EMIT/INC/DECJZ/HALT`, stochastic/local/channel/self-change extensions, etc.) for whether it is a generator, derived operation, macro, semantic convenience, or resource-priced implementation primitive.
```

Anchor ``### AG5 — `G0` must be derivable from lower relations/processes``:

```
- [ ] Derive stochastic update from kernels/distributions rather than a named probabilistic architecture.
- [ ] Derive communication/tool calls as typed interaction composition.
- [ ] Derive governed self-change as state/process transformation plus an externally registered admission relation.
```

**No neighboring row is earned here.** In particular this tranche does not touch AG5's five
already-checked rows, AG6 rows 34-36 and 38, AG7 row 41, AG8 row 48, or any AH row.

## What is frozen

### 1. The status vocabulary

Exactly five statuses, fixed here before any adjudication, taken verbatim from the AG2 row:

- `GENERATOR` — not reconstructible from the registered lower roles at this scope.
- `DERIVED_OPERATION` — a composition of lower roles that reproduces the parent operator exactly.
- `MACRO` — a `DERIVED_OPERATION` whose lowering is a fixed closed term with no free lower input
  beyond its declared arguments, i.e. a named abbreviation.
- `SEMANTIC_CONVENIENCE` — carries no registered state effect: deleting it leaves every registered
  well-formed transition identical. AJ5's token `PRESENTATION_ONLY` is the same status; the
  crosswalk is recorded in the receipt and may not be rewritten later.
- `RESOURCE_PRICED_IMPLEMENTATION_PRIMITIVE` — a `DERIVED_OPERATION` whose lowering cost is not
  constant in the registered scope but a declared function of registered structure.

A sixth qualifier `EXTERNALLY_REGISTERED` may be attached to a status when the operator's outcome
is not a function of the machine-internal state tuple declared below. It is a qualifier, never a
status.

### 2. The lower role basis

The lowering may use only the AJ5 roles (`NEXT_INPUT`, `LOAD`, `STORE`, `SUCC`, `IS_ZERO`,
`PRED_POS`, `SELECT`, `APPEND_OUTPUT`, `TERMINAL`, sequential composition) over a natural-number
register store, plus these, each of which is itself expanded into AJ5 roles and charged:

`NAT_ADD`, `NAT_MUL`, `NAT_SUB_SAT`, `NAT_EQ`, `NAT_MOD`, `NAT_GCD`, `PAIR`/`FST`/`SND`,
bounded `FOLD`, bounded `INDEX`.

No rational, matrix, queue, graph, distribution or receipt object may be introduced as a role.
Rational weights must be built as normalized pairs of naturals; adjacency must be read from the
register store; queues must be built from `NEXT_INPUT`/`APPEND_OUTPUT` streams.

### 3. The parent operators in scope, and nothing else

Sixteen registered operators across five merged packages, named here so the ledger cannot grow
to fit the result:

| package | operators |
|---|---|
| `gmi-833-g0-register-core-v1` via `gmi-833-aj5-g0-lowering-v1` | `READ`, `EMIT`, `INC`, `DECJZ`, `HALT` |
| `gmi-833-g0-stochastic-update-v1` | `UPDATE`, `COMPOSE`, `IDENTITY_KERNEL`, `DETERMINISTIC_KERNEL`, `TRANSPORT` |
| `gmi-833-g0-local-graph-ops-v1` | `POINTWISE`, `GLOBAL_BROADCAST`, `NEIGHBOR_UPDATE` |
| `gmi-833-g0-interaction-channels-v1` | `SEND`, `RECV`, `APPLY_RECEIVED`, `CALL`, `APPLY_EXTERNAL` |
| `gmi-833-g0-governed-self-change-v1` | `PROPOSE`, `VERIFY`, `ADOPT` |

(Twenty-one rows in the ledger: five core plus sixteen extension operators.)

### 4. The universes, fixed before any run

- stochastic: the parent's own families — 6 registered distributions, `6^3 = 216` kernels.
  One-step update on all `6 x 216 = 1296` pairs; composition on all `216 x 216 = 46656` pairs;
  transport on all `216 x 6` permutation cases and all `6 x 6` distribution cases; all `27`
  deterministic maps; the identity.
- local/graph: all `8` simple undirected graphs on three sites, all `27` states, all `3`
  operators, all `6` site relabelings.
- channels: all `27` local states, all `6` directed channels, both messages, all `3` agents,
  both tools, all `3` tool arguments, and all `2`-message queue sequences.
- governed self-change: all `27` candidates, each through propose/verify/adopt, plus the replay,
  stale-version and two-generation controls.

### 5. The gates, fixed before any run

`status: GREEN` requires **all** of:

1. zero lowering mismatches against the parent semantics on every universe above;
2. zero resource-accounting mismatches against the parent's own declared resource vectors;
3. route A and route B agreeing on every published quantity, route B importing nothing from
   route A or from the parent modules;
4. every declared hostile detected, each paired with a control proving the perturbation moves the
   quantity it claims to move;
5. the null reproducing the parent semantics in `0` of its live draws;
6. the no-alarm case asserted: on unperturbed input the checker raises no finding.

Any failure publishes `status: RED` with the failing gate named. A red result is a result.

### 6. Falsifiers, fixed before any run

- If any extension operator's lowering mismatches the parent on one registered case, the status
  ledger entry for that operator is void.
- If `ADOPT`'s outcome turns out to be a function of the internal triple
  `(active behavior, active version, pending candidate)` alone, the `EXTERNALLY_REGISTERED`
  qualifier on `ADOPT` is false and AG5's third row is not earned.
- If deleting the external-data tag changes one registered well-formed transition, the
  `SEMANTIC_CONVENIENCE` reading of that tag is false.
- If `NEIGHBOR_UPDATE`'s result is a function of the site-value tuple alone, its
  `RESOURCE_PRICED_IMPLEMENTATION_PRIMITIVE` status is wrong and it is a plain `MACRO`.
- If a randomized lowering reproduces a parent operator's full behaviour map, the lowering is not
  identifying and the corresponding claim is withdrawn.

## Forbidden promotions

`G0_EXTENSIONS_ARE_THE_OPERATIONAL_BOTTOM`, `UNIQUE_LOWEST_EXTENSION_BASIS`,
`ALL_G0_EXTENSIONS_ENUMERATED`, `STOCHASTIC_ARCHITECTURE_DERIVED`, `BAYESIAN_INFERENCE_DERIVED`,
`GNN_DERIVED`, `TOOL_USE_INTELLIGENCE_DERIVED`, `EMERGENT_COMMUNICATION`,
`RECURSIVE_SELF_IMPROVEMENT_PROVED`, `AUTONOMOUS_SELF_AUTHORITY`, `VERIFIER_INFALLIBLE`,
`COMPLETE_GMI`.

## What is not claimed novel

Term algebras over a signature, the field-of-fractions construction, row-stochastic matrix
algebra and its composition law, register-machine instruction decomposition, structural
operational semantics, FIFO channel semantics, and verifier-gated update with replay protection
are all parent mathematics. They are pinned in `PARENT_LEDGER.md`. The residual contribution of
this tranche is only the adjudication itself: an exact, exhaustive, two-route lowering of the
four registered extension families into the AJ5 role basis, and the resulting status ledger with
its two structural residuals.
