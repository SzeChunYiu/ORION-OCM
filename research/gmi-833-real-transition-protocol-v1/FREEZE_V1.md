# GMI #833 real-system morphology transition evidence protocol v1 — freeze

Parent: #833 Section J. Child: #903.  
Base main: `a0d2b4e6535f5d47dba3c56e94faa7aa8a2d8678`.

## Purpose

Make the final Section-J real-system evidence gate machine-checkable without promoting synthetic/toy evidence.

Protocol completion is not scientific completion. The Section-J row `Validate at least 5 transitions on real systems` remains open until five distinct qualifying receipts exist.

## Qualifying receipt fields

Each receipt must bind:

- `system_id`: stable distinct system identity;
- `system_version`: version/commit/model identifier;
- `implementation_ref`: replayable repository/container/model reference;
- `prediction_ref`: preregistered prediction artifact identifier;
- `prediction_frozen_before_outcome=true`;
- `evidence_kind=REAL_SYSTEM` exactly;
- `task_or_workload_id`;
- `before_context` and `after_context` describing the registered ecology/resource intervention;
- `predicted_before_property`, `predicted_after_property`;
- `observed_before_property`, `observed_after_property`;
- `classification_blind_to_target_family=true`;
- measured nonempty raw lifecycle resource vectors for before/after;
- `run_id_before`, `run_id_after`;
- `artifact_hash_before`, `artifact_hash_after`;
- `protected_outcome_leakage=false`;
- `classification_identified=true` or else the receipt must abstain and cannot qualify.

A qualifying transition additionally requires predicted and observed before/after properties to match exactly and before != after.

## Global closure rule

Return `REAL_SYSTEM_TRANSITION_VALIDATED_AT_REGISTERED_SCOPE` only if at least five qualifying receipts have five distinct `system_id` values.

Otherwise return `INSUFFICIENT_REAL_SYSTEM_EVIDENCE` with typed rejection reasons. Synthetic/toy/simulator-only evidence, duplicate systems, post-hoc prediction, missing resource measurements, non-replayable runs, leakage, or unidentified morphology can never count toward five.

## Hostiles

The executor must reject:

- synthetic receipt with otherwise perfect fields;
- duplicate system identity;
- post-outcome prediction;
- missing raw resources;
- target-family-visible classification;
- leakage=true;
- unidentified classification;
- matching before/after property (no transition);
- predicted/observed transition mismatch.

A positive schema fixture of five distinct receipts may be used only to prove validator logic and must be machine-labeled `PROTOCOL_FIXTURE`, never scientific evidence.

## Claim ceiling

If validator/tests/CI are GREEN, only:

`GMI_REAL_SYSTEM_TRANSITION_VALIDATION_PROTOCOL_MACHINE_CHECKABLE`

No real-system transition count is promoted by this protocol tranche itself.
