# ORION Cognitive Machine (OCM)

**Canonical repository for the ORION Cognitive Machine / Knowledge Space Object programme.**

OCM is a research programme toward a minimal self-extending cognitive machine that learns executable ways of accomplishing tasks from instruction, demonstration, interaction, experimentation, and feedback; composes and revises what it learns; and may eventually reorganize its own representations, operators, learning procedures, and cognitive topology under an external constitutional shell.

## Current programme priority

**The revised runtime requires renewed scientific evaluation.** Roadmap v1 recorded historical M0–M12 terminals. The 2026-09-05 review found invalid predecessor bindings in historical M11 adoption cells and M12 phase G, as well as runtime revocation, durability and statistical-guarantee defects. Those defects now have implementation fixes and regression tests. Replays of the authored scenarios are engineering evidence; they do not renew the old protected-evaluation claims.

Current receipt verification and the historical records are separated in [the runtime revision receipts](docs/provenance/runtime_revision_20260905_v3/). The immediate priority is corrected adoption-cell evaluation, stronger matched parents, longer lifetimes and independent assessment; see [the programme terminals](docs/OCM_PROGRAMME_TERMINALS_V1.md) and [runtime revalidation](docs/RUNTIME_LIFECYCLE_REVALIDATION_V2.md).

The active target is a runnable machine that can sustain real multi-turn English conversation over a bounded knowledge world while:

- understanding utterances into internal meaning/task state;
- thinking/retrieving/learning through KSO state rather than hidden answer generation;
- maintaining dialogue context and uncertainty;
- planning responses before surface realization;
- learning new vocabulary/constructions after deployment;
- preserving provenance, warrant, scope, and exact revocation;
- refusing or clarifying when it cannot support an answer;
- exposing a diagnostic trace from understanding to cognition to committed speech;
- using no hidden frontier LLM as the central reasoning or writing mechanism in the mechanism arm.

## Run the bounded chat runtime

Install with `python -m pip install .`, then run `ocm chat --state ./ocm-state`.
The installed wheel includes its checked vocabulary and knowledge manifest; it does not need the
repository test suite. `python -m ocm.chat` is also available. Repository custody audits (`status`
and the M0 `demo`) remain checkout-only commands and explain missing custody outside a checkout.

The [continuation report](docs/IMPLEMENTATION_CONTINUATION_2026-09-05.md) records actual-speech
checks, recoverable data-only rollback, complete assurance measurements, numerical optimizations
and current validation. Earlier results remain historical evidence.

Current integration: chat now proposes spelling corrections, asks about ambiguous
spellings, remembers user-reported facts, and learns/reuses checked arithmetic
methods across restarts. See [the current capability report](docs/CHAT_LEARNING_INTEGRATION_V4.md).
The [V4 successor evidence](docs/provenance/runtime_revision_20260905_v4/) preserves
both local and upstream histories. Historical programme terminals are not
current scientific admission. ChatGPT equivalence and frontier mathematics
remain unestablished.

```text
ocm chat --state ./ocm-state
> is parsi in france
> remember: mira is a botanist
> learn method next-square: inc square
> run next-square on 3
> list skills
> find method: 1,2,1
```

Run `ocm methods` for the checked method-learning demonstration: learn reusable
program fragments, generate methods for different polynomial specifications,
verify exact solutions, persist the generator, and reopen it when support is
revoked. The [method-learning and recovery report](docs/METHOD_LEARNING_AND_RECOVERY_V3.md)
states the finite convergence conditions, measured search improvements and the
remaining requirements for real scientific evaluation.

## Scientific discipline

OCM does **not** assume that Language KSO, Method KSO, Wisdom KSO, field/subject/domain hierarchies, symbolic grammar, hypergraphs, or any other current decomposition is the final architecture of cognition. These are candidate organizations to test and replace when evidence warrants it.

The stable commitment is the epistemic contract: evidence identity, provenance, uncertainty, authority, scope, resource accounting, revocation/reopening, matched comparison, and fail-closed `CANNOT_CHECK` behavior.

## Migration

This repository is being initialized from the OCM research stack developed in `SzeChunYiu/ORION-V2`. A provenance ledger records the exact source PR/commit chain and scientific boundaries. Existing controlled results are migrated as prior evidence, not promoted into broader claims.

## Milestone state

The table below preserves the **historical roadmap v1 terminals**. It does not certify the revised engine. Current M11 is `M11_ENGINEERING_REVALIDATION__HISTORICAL_ADOPTION_CELLS_REOPENED`; current M12 is `M12_ENGINEERING_REVALIDATION__PROTECTED_REEVALUATION_REQUIRED`. Every old receipt remains unchanged, with explicit successor receipts for the revised code.

| milestone | issue | terminal | receipt | report |
|---|---|---|---|---|
| M0 canonical repository | #2 | `M0_CANONICAL_REPO_GREEN` | `docs/provenance/M0_RECEIPT_V1.json` | — |
| M1 KSO core | #3 | `M1_KSO_CORE_GREEN` | `docs/provenance/M1_RECEIPT_V1.json` | — |
| M2 unified KSO runtime | #4 | `M2_UNIFIED_RUNTIME_GREEN` | `docs/provenance/M2_RECEIPT_V1.json` | — |
| M3 language understanding + meaning | #5 | `M3_LANGUAGE_UNDERSTANDING_GREEN` | `docs/provenance/M3_RECEIPT_V1.json` | — |
| M4 dialogue workspace | #6 | `M4_DIALOGUE_COGNITIVE_LOOP_GREEN` | `docs/provenance/M4_RECEIPT_V1.json` | — |
| M5 continual language acquisition | #7 | `M5_CONTINUAL_LANGUAGE_LEARNING_GREEN` | `docs/provenance/M5_RECEIPT_V1.json` | — |
| M6 Conversational Alpha | #8 | `LANGUAGE_KSO_ALPHA` | `docs/provenance/M6_RECEIPT_V1.json` | `docs/LANGUAGE_KSO_ALPHA_REPORT.md` |
| M7 protected matched comparison | #9 | `MIXED (claim-by-claim; see terminal_table)` | `docs/provenance/M7_RECEIPT_V1.json` | `docs/M7_PROTECTED_COMPARISON_REPORT.md` |
| M8 learned KSO organisation | #10 | `M8_PARENT_SUFFICIENT_AT_THIS_SCALE` | `docs/provenance/M8_RECEIPT_V1.json` | `docs/M8_ORGANISATION_REPORT.md` |
| M9 method space + work transfer | #11 | `M9_CANNOT_CHECK_FOR_SUPPORTED_AT_THIS_N` | `docs/provenance/M9_RECEIPT_V1.json` | `docs/M9_TRANSFER_REPORT.md` |
| M10 scientific/formal reasoning | #12 | `M10_MIXED_CLAIM_BY_CLAIM` | `docs/provenance/M10_RECEIPT_V1.json` | `docs/M10_SCIENCE_REPORT.md` |
| M11 governed self-reorganisation | #13 | `M11_MIXED_CLAIM_BY_CLAIM` | `docs/provenance/M11_RECEIPT_V1.json` | `docs/M11_SELF_REORGANISATION_REPORT.md` |
| M12 full heterogeneous lifetime | #14 | `FULL_OCM_RESIDUAL_SUPPORTED` | `docs/provenance/M12_RECEIPT_V1.json` | `docs/M12_LIFETIME_REPORT.md` |

Active core: `src/ocm/kso/` (specs under `docs/spec/`). The build is itself run as an OCM problem —
see `docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md`.

## Programme management

- **Issue #1** is the master programme plan and milestone dependency graph.
- Each milestone has its own executable issue with tasks, datasets, comparators, metrics, hostile tests, artifacts, and exit gates.
- Active work must converge into the current milestone; disconnected research lanes are not accepted.
- Negative and `PARENT_SUFFICIENT` results are first-class outcomes.
