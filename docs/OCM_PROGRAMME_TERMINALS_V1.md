# OCM programme terminals — roadmap v1 (M0–M12)

Every milestone of issue #1 closed with a receipt-bound terminal. This index is generated from the
`terminal` field of each `docs/provenance/M*_RECEIPT_V1.json`; the receipts bind the code, data,
registries and reports that produced the terminal, and the chain `python tools/m*_receipt.py --verify`
(m2…m12) is checked in CI.

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

## Reading the terminals

* **PARENT_SUFFICIENT / EQUIVALENT** rows are successes of the method: the strongest matched parent
  explains the result at the stated scale (M2.1 discordant-scale equivalence; M8 at 10^5 atoms).
* **MIXED_CLAIM_BY_CLAIM** rows carry a table in their report with one terminal per claim
  (SUPPORTED at the stated n, DESCRIPTIVE, PARENT_SUFFICIENT, CANNOT_CHECK, NOT ATTEMPTED).
* **M12 `FULL_OCM_RESIDUAL_SUPPORTED`** is in scope: relative to the matched whole-system parent
  buildable in this environment, with one inferential family (conversations, n = 54) and every other
  residual descriptive; against a frontier foundation-model whole-system parent it is
  `CANNOT_CHECK_MATCHED_PARENT`. External benchmarks, blinded human rating and the frontier reference
  arm are CANNOT_CHECK throughout the programme (no network, containers or foundation model).
* No novelty, consciousness, human-equivalence or universal-intelligence claim is made anywhere.

## Self-application

The build was run as an OCM problem: `docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md`
(rows S1–S34) records each defect the machine's own discipline caught in its builders, with the
attribution, the fix and the lesson; the ORION-V2 ↔ OCM intake/export protocol
(`src/ocm/selfmodel/intake.py`) records theory-reported defects and runtime-exported open items.

## Theory loop

Machine-epistemics theory batches 1–5 (ORION-V2 `research/machine-epistemics-theory/`, PRs #333,
#341, #343, #344) gave the obligations KS-T1…T109; batch 6 takes the M12 feedback packet
(`research/ocm-m12/ORION_V2_FEEDBACK_PACKET_V1.md`, P1–P6).

## What is next (revival backlog, in priority order)

1. Longer lifetimes so that work/science/transfer/self-repair families reach n ≥ 40 from one instance.
2. A second protected language suite so that phase A differs across orderings.
3. A stronger repair parent (learned failure classifier over traces) with the same candidate channel.
4. Real-language coverage (UD structural alignment; BLiMP/BabyLM pinning) — CANNOT_CHECK today.
5. A foundation-model reference arm with a bound information budget (batch-6 F8) when one is available.
6. Blinded human rating of the conversation suites.


## Post-roadmap additions (2026-09-05)

| item | terminal | receipt | report |
|---|---|---|---|
| M11.1 / M11.2 theory intake (batches 5–6: eleven runtime obligations) | applied with hostiles; benchmark results unchanged | `docs/provenance/M11_RECEIPT_V1.json` | `docs/M11_SELF_REORGANISATION_REPORT.md` §6–§7 |
| M12 V3 eight paired lifetimes on protected streams | `OCM_LIFETIME_RESIDUAL_SUPPORTED` (10 families 8/8 at p = 0.0078, 6 ties; replication MATCH) | `docs/provenance/M12_PAIRED_RECEIPT_V1.json` | `docs/M12_V3_PAIRED_LIFETIMES_REPORT.md` |
| M12 V4 paired lifetimes with a pre-registered primary family (batch-7 G7/G8 intake) | `OCM_LIFETIME_RESIDUAL_SUPPORTED` (primary 8/8, one-sided p = 0.0039; six secondaries reject but collapsed-one-coin; replication MATCH) | `docs/provenance/M12_PAIRED_RECEIPT_V4.json` | `docs/M12_V4_PAIRED_LIFETIMES_REPORT.md` |
| Reference arm (local open-weight LLM, F8) | REFERENCE (descriptive; never in a decision) | `docs/provenance/M12_REFERENCE_RECEIPT_V1.json` | `docs/M12_LIFETIME_REPORT.md` §10.1, V3 report §4 |
| Paper plan | claims → receipts map; gates | — | `docs/paper/OCM_PAPER_PLAN_V1.md` |

## Branch inventory (2026-09-05)

| branch | state | disposition |
|---|---|---|
| `m0-self-contained-ocm` | 9 commits, 2026-09-04: M0 staging (frozen-dependency import, `.m0/` bundle chunks, two bootstrap workflows); 16/23 files already byte-identical on main | SUPERSEDED by the merged M0 (`m0-canonical.yml`); not merged; kept as history |
| `research/m2b-v3-migration-20260904` | 1 WIP commit ("NOT gated"): V2-only file copies + design notes + M2b V3 algebra results | design notes, results and domain fixtures (20 md/json files) archived on main under `research/orion-machine/` by this PR; the V2 file copies duplicate `src/orion_v2` and the ungated tests are not merged |
| `perf/verified-knowledge-kernel` | 1 commit, 2026-09-05 07:50: a workflow for a knowledge-kernel benchmark lane (`tools/knowledge_kernel_benchmark.py`, `tests/optimization/` — not yet present) | ACTIVE external lane; merged when it opens its PR and its own checks are green |
| `m1/…` … `m12/lifetime`, `m11.1/…`, `docs/…`, `codex/m0-canonical-runtime` | 0 ahead of main | merged |
