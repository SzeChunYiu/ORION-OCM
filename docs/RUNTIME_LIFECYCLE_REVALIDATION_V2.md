# Runtime lifecycle engineering revalidation V2

This successor records engineering corrections against the accepted M2/M4/M11/M12 lifecycle contracts. Historical results, receipts and scientific terminals are unchanged. A passing local replay does not supply a new protected evaluation, independent review or external adoption decision.

## Implemented mechanics

| Boundary | Previously missing behavior | Corrected behavior |
|---|---|---|
| Event append and snapshot | A stale runtime read the newest disk head and appended an event based on old state, making restart fail | CAS uses the ledger head actually replayed or successfully appended by this instance; stale writes leave state and disk unchanged |
| External action | The persistent intent was written after the effector returned | Boundary events persist synchronously; intent is durable before the authority or effector callback |
| Interrupted action | A process interruption could leave no durable intent; reuse could run the same intent again | Pending intents survive; recorded intent IDs cannot silently execute again; receipt-write failure leaves the unresolved intent |
| Authority callback | Revoking evidence during authority evaluation could leave the subsequent effector using stale liveness | The runtime checks its post-intent event/state/ledger checkpoint after the host decision and refuses a changed authorization state |
| Evidence revocation | Rejecting derived-evidence revocation occurred after durable append and partial mutation | The whole request is validated before append; callers revoke the assumptions instead |
| Interval persistence | Derived evidence serialized only its lower family, collapsing UNKNOWN to DEAD | Both warrant bounds persist; old exact-family event payloads remain readable; upper-bound references are validated |
| Dialogue promotion | A derived bridge was cited by raw record ID, so revoking its assumptions missed the promoted claim | Promotion uses the registry's citation warrant, including the bridge assumptions and the speaker commitment |
| Operator registration | Registry mutation preceded its event; restart could not reconstruct the recorded revision | Events persist declared manifests before host installation; replay restores metadata; implementations remain explicitly host supplied |
| Statistical output | A population coverage certificate promoted a selected answer to LIVE | The output remains UNKNOWN without an exact target certificate; a distinct scoped `OPERATOR_GUARANTEE` carries the coverage statement and its revocable support |
| Self-change adoption | Decision fingerprint, protected targets and exact target predecessor were not all checked at adoption | Adoption checks all three before constructing the challenger and before recording completed adoption |
| Challenger failure | Failed construction could already have a completed-adoption evidence stamp | Construction completes before that stamp; writes to the runtime during the declared-pure callback are detected |
| Rollback | Snapshots aliased caller state; failed revocation discarded the only rollback artifact; old rollback could bypass live successors | Snapshot copies are independent, restoration copies are staged first, artifacts survive failed writes, and whole-table rollback follows reverse adoption order |
| Restarted self-change | A lost host rollback object caused an untyped missing-key failure | Durable adoption metadata remains queryable; unavailable process-local restoration returns `CANNOT_CHECK_ROLLBACK_ARTIFACT_UNAVAILABLE` |
| Re-adoption | The same proposal could deduplicate onto its revoked adoption stamp | A recorded proposal fingerprint cannot be reused as a new adoption |

The operator manifest includes the declared warrant, resource model, expected effects and checker-presence requirement. It explicitly labels implementation identity `HOST_SUPPLIED_UNVERIFIED`. It is not a hash proof of backend/checker code or closure state. A new process never deserializes executable code from the ledger.

## Validation

`PYTHONPATH=src python -m pytest -q tests/m2 tests/m4 tests/m11 tests/m12` completed with **174 passed** using Python 3.12 and pytest 8.3.5.

The new suites contain **34 tests**: **32 reproduced failing behavior before their corresponding corrections**, plus two legacy-format/receipt-failure controls. They cover fresh restart, stale writers, interrupted callbacks, receipt storage failure, invalid whole-request revocation, UNKNOWN intervals, derived dialogue bridges, explicit operator binding, wrong predecessors, protected targets, caller-owned mutable state, retryable rollback, typed statistical guarantees and unrelated state preservation.

The fresh controlled M11 replay is `research/ocm-m11/M11_SELF_EVAL_LIFECYCLE_V2.json`. Its descriptive summary matches the historical run: seven repairs and exact rollbacks, seven preserved capabilities, and one no-fault control that raises no proposal. The two parent summaries are unchanged. This is an engineering replay over the same authored controlled scenarios. The historical self-application rows embedded in the evaluator remain recorded metadata, not new executions.

## Historical predecessor cells reopened

The previous benchmark supplied a component table keyed by `machine` while proposing replacement of a named layer. The corrected gate rejects that predecessor mismatch. New executions now supply the exact target key and declared incumbent identity. The old result files remain byte-identical.

| Historical evaluation | Cell | Missing target in the old component table |
|---|---|---|
| M11 V1 | S1 router fault | `layer.D1` |
| M11 V1 | S2 operator fault | `layer.D2` |
| M11 V1 | S3 representation ceiling | `layer.D3` |
| M11 V1 | S4 learning policy | `layer.D6` |
| M11 V1 | S5 false structural alarm | `layer.D2` |
| M11 V1 | S6 harmful jump | `layer.D2` |
| M11 V1 | S7 environment drift | `layer.D2` |
| M12 V2, OCM phase G | O1 operator fault | `layer.D2` |
| M12 V2, OCM phase G | O2 learning policy | `layer.D6` |
| M12 V2, OCM phase G | O3 environment drift | `layer.D2` |

These historical cells did not prove the now-enforced predecessor check. Equality of the new descriptive outcomes does not retroactively validate the old input binding or upgrade a scientific terminal.

The previous M2 `test_coverage_certificate_licenses_only_inside_its_scope` also explicitly asserted that a population coverage certificate made an individual output LIVE. That assertion was corrected to inspect the separate operator guarantee. This follows the distinction stated in ORION-V2 `foundation_typed_lifecycle_v1/THEORY.md`, T04, and `certificate_lifecycle_v1/THEORY.md`: applicability of an operator guarantee is not exact truth of a selected output or action permission. It does not establish full Foundation absorption parity or verify real calibration premises.

## Limits and receipt custody

- Durable intent plus refusal of recorded-ID reuse is not an exactly-once guarantee for arbitrary external effects. A crash or receipt-write failure after an effect leaves an unresolved intent requiring external reconciliation. The runtime does not fabricate a receipt.
- Checkpoint validation covers the tested interleavings; a general concurrent commit protocol spanning independent hosts and external systems remains outside this implementation.
- Cold-restart restoration of executable host artifacts still needs an explicit, identity-bound artifact storage and loading contract. Current metadata truthfully records its absence.
- Pure challenger callbacks are checked for mutation of this runtime; that check does not sandbox arbitrary Python callbacks or prove absence of external side effects.
- Old operator events that already encoded a post-mutation expectation remain invalid and fail closed. This change does not rewrite or silently migrate them.
- The M2 runtime, M4 workspace, M11 governance/benchmark and M12 lifetime sources changed. Their historical digest-bound receipts must remain addressable. A successor engineering receipt must bind these source revisions, new tests and replay output separately from prior scientific results.
