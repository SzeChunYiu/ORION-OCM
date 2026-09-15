# New-Domain Claim Gate Theorem v1

**Capsule**: `research/gmi-new-domain-claim-gate-v1`  
**Issues**: #602 (J4, K), related #592  
**Date**: 2026-09-15

## T1 — Gate completeness over the checklist

There exist exactly 25 machine-checkable predicates corresponding one-to-one with the unchecked #602 J4 (11) and K (14) boxes. Each predicate is a total function from a candidate domain dossier to `{pass, fail}` with an explicit reason string.

## T2 — Residual survival is necessary

A dossier receives `gate_pass = true` only if:

1. every structural predicate J4.1–J4.11 and K.1–K.13 passes, and
2. `parent_review.residual_survives` is true, and
3. every D1–D8 reduction attempt has status `FAILS` (no `ABSORBS`, no `OPEN`), and
4. strongest-parent tournament verdict is `RESIDUAL_SURVIVES_REGISTERED_PARENT_SET`.

## T3 — Novelty refusal law

Novelty wording is permitted only when T2 holds and the dossier asserts novelty under claim ceiling

```text
FINITE_DOSSIER_GATE_NOT_ONTOLOGICAL_NOVELTY
```

Otherwise the disposition is `NOVELTY_WORDING_REFUSED`. Asserting novelty on a failing dossier cannot upgrade the disposition.

## T4 — Positive / negative twin invariant

The capsule ships:

- a **positive** residual twin that passes the gate and may assert novelty under the ceiling;
- a **negative** absorbed twin that fails structural predicates and receives novelty refusal.

The executable report invariant requires both behaviours simultaneously.

## T5 — Registry alignment

Domain identifiers and display names are aligned with `gmi-domain-registry-v1` / `gmi-completeness-attack-v1` (`D1`…`D8` and the eight structural names). E3 burden evidence cannot establish separation or equivalence.

## Claim ceiling

Finite exact dossier gate. Does not mint an ontological new domain of machine intelligence.
