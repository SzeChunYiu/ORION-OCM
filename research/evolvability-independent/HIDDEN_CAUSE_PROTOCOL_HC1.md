# E150-D hidden-cause diagnosis — protected HC1

Status: **FROZEN BEFORE HC1 PROTECTED OUTCOME ACCESS**

This is a separate confirmatory lane from factorization V2. It does not alter V2 worlds, code or decision rules.

## THEORY QUESTION

Can OCM diagnose the minimum sufficient failure layer when the cause label is hidden, and refuse to guess when the allowed interventions do not identify the cause?

## PREDICTION

For intervention-identifiable failures, the lowest restoring intervention is the minimum sufficient repair. For observational/interventional aliases with no restoring discriminator, diagnosis must be `CANNOT_CHECK`, never a frequency- or symptom-based guess.

## STRONGEST PARENT

A TMS/nogood symbolic parent given the exact same candidate layers and intervention outcomes. It selects the lowest restoring layer and otherwise returns unknown. No cause label is supplied to either arm.

## RED COUNTEREXAMPLE

The parent matches OCM diagnosis and refusal behavior at equal or lower intervention/state cost, or OCM guesses an aliased cause.

## MECHANISM

Use the existing M11 `FailureRecord` + `AblationEvidence` + `diagnose` path. The hidden true cause exists only in evaluator state. Learner-visible failure records contain symptoms, candidates and intervention outcomes, never the cause label.

## CAUSAL ABLATION

Remove restoring intervention evidence: the result must become `CANNOT_CHECK`. Repeated symptom frequency is not allowed to substitute for intervention evidence.

## Protected cases

Seeds: `9201..9240`.

Layer order: `D0, D1, D2, D5, D6, D3`.

A SHA256 stream `E150-HC1|<seed>` selects a hidden cause layer. For 32 identifiable cases, every layer is intervened on and the hidden cause plus every strictly broader layer restores the task; the minimum restoring layer is therefore identifiable. For 8 alias cases (`seed % 5 == 0`), allowed interventions are non-restoring and do not identify the hidden cause; the only admissible terminal is `CANNOT_CHECK`.

The failure record includes no task-family ID, cause label, generator seed, frequency shortcut or routing key. Frequency is fixed at 1.

## RESULT fields

Per case: `seed, identifiable, hidden_cause[evaluator-only], ocm_terminal, parent_terminal, interventions, false_jump`.

Aggregate: exact minimum accuracy on identifiable cases; alias refusal rate; OCM-parent disagreement count; interventions; false jumps.

## RESOURCE VECTOR

`[identifiable_accuracy, alias_cannot_check_rate, interventions, diagnosis_state_bytes, false_jumps]`. No scalar collapse.

## FALSIFIER

Any wrong minimum on an identifiable protected case, any guessed layer on an alias case, or any OCM-parent disagreement favorable to OCM caused by withholding parent information.

## CLAIM CEILING

At most `INTERVENTION_IDENTIFIABLE_DIAGNOSIS`. If the parent matches, terminal is `PARENT_SUFFICIENT`; this cannot support an OCM-specific evolvability residual.
