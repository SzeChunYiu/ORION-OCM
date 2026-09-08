# G2.1 cognitive object schema

Research capsule for ORION-OCM issue #165 **G2.1**. It defines and emits a
stable object language so later causal-reuse experiments have somewhere to
land. It does **not** establish causal reuse, amortized generation, or a G2
scientific terminal.

Claim authority: **SCHEMA_TRANSPORT_ONLY**.

## What landed

```text
research/g2-cognitive-objects-v1/
  schemas/*.json
  g2_cognitive_objects/     emit + validate (stdlib dataclasses, no pydantic)
  examples/frozen_episode.json
  tests/
  CORE.md
```

Required types (JSON Schema + dataclasses):

| Type | Schema |
|---|---|
| `CognitiveEpisodeV1` | `schemas/cognitive_episode_v1.json` |
| `MethodRecordV1` | `schemas/method_record_v1.json` |
| `MethodSchemaV1` | `schemas/method_schema_v1.json` |
| `ReuseEventV1` | `schemas/reuse_event_v1.json` |
| `FailureAttemptV1` | `schemas/failure_attempt_v1.json` |
| `ScopeTransferV1` | `schemas/scope_transfer_v1.json` |
| `RepresentationChangeV1` | `schemas/representation_change_v1.json` |
| common resource vector | `schemas/resource_vector.json` |
| acquisition lineage | `schemas/acquisition_lineage.json` |
| usefulness evidence | `schemas/usefulness_evidence.json` |
| correctness evidence | `schemas/correctness_evidence.json` |
| current authorization state | `schemas/current_authorization_state.json` |

## Four axes (kept distinct)

```text
correctness         independent checker / proof certificate
usefulness          later-task causal benefit
acquisition history origin, episodes, donors, prior information, cost
current authority   admitted / live / eligible *now*
```

Invariants:

- correctness cannot encode usefulness (`independent_of_usefulness: true`)
- usefulness cannot encode correctness (`independent_of_correctness: true`)
- LIVE serving requires LIVE proof **and** LIVE applicability **and** `admitted=true`
- a LIVE-correct method may be DEAD for serving (withdrawn applicability)
- a reuse event that claims actual invocation must carry an execution witness
- `G24Lifecycle.complete` cannot be true unless every G2.4 gate is MEASURED and
  satisfied; this capsule never sets it true

This split ADAPTs the unary issuer, which already returns `correctness`,
`selection`, and `eligible` as separate liveness readings
(`research/math-language-learning-v1/unary_method_store.py` `MethodStore.read`),
and the native importer, which stores `proof` and `applicability` as distinct
evidence IDs (`research/native-method-serving-v1/native_store.py`).

Unary `utility` / native `applicability` are **selection or import policy**, not
G2 usefulness. Mapping marks usefulness `CANNOT_CHECK` with that reason.

## Resource vector

**ADOPT** `research/machine-epistemics-lifetime-v1/ME_LIFETIME_RECEIPT_SCHEMA_V1.json`
`$defs.resource` and `$defs.information`, including the non-collapsed coordinates
and the reuse-event definition (execution/causal witness required). A test locks
field names to that schema. Liveness ADAPTs `src/ocm/kso/warrant.py`. Scope and
authority ranks ADAPT `src/ocm/kso/types.py`.

## Mapping from existing receipts

`g2_cognitive_objects/mapping.py` projects source dicts onto G2.1 types.
Disposition is ADOPT / ADAPT / REJECT / OPEN. Gaps are `UNKNOWN` or
`CANNOT_CHECK`, never filled with a favorable story.

| Source | Target | Disposition | Gap |
|---|---|---|---|
| `research/machine-epistemics-lifetime-v1/ME_LIFETIME_RECEIPT_SCHEMA_V1.json` resource vector | `ResourceVector` | ADOPT | — |
| `research/math-language-learning-v1/unary_method_store.py` `ocm.unary-method.data.v1` | `MethodRecordV1` | ADAPT | utility policy ≠ usefulness |
| `research/native-method-serving-v1/native_store.py` imported plans | `MethodRecordV1` | ADAPT | authored import, not episode-induced abstraction |
| `research/math-language-learning-v1/unary_method_journal.py` `ocm.unary-method.use.v1` | `ReuseEventV1` / `FailureAttemptV1` | ADAPT | no restart, no ablation, no fresh-task disjointness |
| `research/native-method-serving-v1/native_journal.py` `ocm.native-method.use.v1` | `ReuseEventV1` / `FailureAttemptV1` | ADAPT | same; selected method IDs are invocation, not G2.4 |
| `research/native-method-serving-v1/native_packet.py` `selected_proof_method_ids` | invocation witness | ADAPT | identifies macros used in a derivation |
| `research/ordinary-cut-source-evidence-v1/consumer-v3/teaching_packet.py` | `CognitiveEpisodeV1` | REJECT | training-trace / prefix authority, not a method object |
| `research/native-typed-lifecycle-v1/CORE.md` | learned `MethodRecordV1` | REJECT | no useful acquisition; empty serving-eligible method IDs |
| `research/math-language-learning-v1/release-review-records/REVIEW.json` | G2.4 | REJECT | restart / fresh causal use explicitly not established |
| `research/ocm-prototype/results/stitch-public-induction-20260906/CORE.md` | `RepresentationChangeV1` | ADAPT | `PRIMITIVE_ALIAS`; useful operator NOT_ESTABLISHED |
| `research/ocm-prototype/results/clia-reuse-study-result-20260906/CORE.md` | `ReuseEventV1` / G2.4 | ADAPT | closest lifecycle; **not** G2.4 complete |
| typed correspondence + reminted target vocabulary | `ScopeTransferV1` | OPEN | no existing receipt |

## G2.4 is unchecked

G2.4 requires: admitted before the fresh task; process restart; fresh task
disjoint from acquisition; actual invocation; execution trace identifies the
object; material cost/capability change; removal ablation; answer-cache
excluded; retrieval-only excluded or `PARENT_SUFFICIENT`.

Closest existing control:

- `research/ocm-prototype/results/clia-reuse-study-result-20260906/CORE.md`
- protocol: `research/ocm-prototype/results/clia-reuse-study-qualification-20260906/protocol/protocol.json`
- readout: `research/ocm-prototype/results/clia-reuse-study-result-20260906/READOUT.json`

That study **does** record six fresh OS processes, F1 admission before apply,
post-acquisition invocation with zero later synthesis, and authority withdrawal
that refused reuse then recovered on restore.

It does **not** close G2.4:

- terminal is `EXECUTABLE_REUSE_DEVELOPMENT_SUPPORTED` with
  `PARENT_SUFFICIENT_FUNCTION_ONLY`
- cost terminal remains `CANNOT_CHECK_COST`
- CORE.md: no OCM residual over the matched native library; not protected
  acceptance
- objects are synthesized/imported programs, not episode-induced methods
- this is not `CAUSAL_METHOD_REUSE_SUPPORTED`

Do not check the G2.4 boxes from this capsule.

## G2.1 boxes that can be checked

Issue #165 G2.1 checkboxes for the twelve named types can be checked: each type
has a schema, a dataclass, emission/validation, a frozen round-trip, and an
explicit mapping or UNKNOWN gap.

G2.2–G2.5 and G2.4 remain unchecked.

## Frozen example

`examples/frozen_episode.json` is a transport fixture (`claim_authority:
SCHEMA_TRANSPORT_ONLY`). Round-trip is required; it is not a scientific
receipt.

## Run

From the repository root, Python 3.11+, pytest 8.3.5:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
python -B -m pytest -q research/g2-cognitive-objects-v1
```

This lane stays outside installed `src/ocm`. Absorbing it into the runtime
would need a new receipt.
