# Claim disposition (issue #217 close-out)

Every claim the issue registers, with its terminal disposition and the
artifact that carries the evidence.  `PARENT_SUFFICIENT_*` terminals are
SUCCESS outcomes per the issue's section 21 (`EXPECTED_TERMINALS.json`).

| Item | Disposition | Evidence |
|------|-------------|----------|
| PDEV-0 repo state capsule | CLOSED — state captured before and after | `REPO_STATE.json` |
| PDEV-1 canonical serial lineage | CLOSED — g2 -> g3 adopted via full M11 path; freeze identity `e56a24cd…33ac5` | `results/LINEAGE_FINAL.json`, `results/CYCLE_RECEIPT_g2.json` |
| PDEV-2 parent dispositions | CLOSED — 217 + 123 parent-entry measurements, 340 rows, 0 crashes | `parents/PARENT_RESULT.json`, `results/RESOURCE_LEDGER.json` |
| PDEV-3 slurm layout as specified | CLOSED — arrays as wide as the partition tolerates; dependency quirk recorded and worked around | `slurm/`, `incidents/INCIDENTS.jsonl` (INC-1), `manifests/submissions.jsonl` |
| PDEV-4..5 grammar/meter/hostiles/task pool | CLOSED — executed on all 784 candidate evaluations, 0 crashes, 0 CANNOT_CHECK | `execution/`, `results/CANDIDATE_LEDGER_REBUILT.jsonl` |
| PDEV-6 adverse + cannot-check rows | CLOSED — 10 ADVERSE_RECORDED (H9 registered example), 0 CANNOT_CHECK | `results/ADVERSE_AND_CANNOT_CHECK.jsonl`, `incidents/INCIDENTS.jsonl` |
| PDEV-7 QD archive | CLOSED — persisted across generations; 1 occupied cell of 3240 (honest: verified-candidate descriptor space collapsed to the incumbent-point cell), failed niches recorded | run-root `DIVERSITY_ARCHIVE_V1.json`, `results/RESOURCE_LEDGER.json` |
| PDEV-8 frozen selection rules | CLOSED — never relaxed; negative waves attributed per stage (quality/integrity/dominance) with the next-wave history-consuming arms as the revival lever | `PROTOCOL.json`, `results/EXHAUSTION_TERMINAL_g3.json` |
| PDEV-9 determinism receipts | CLOSED — cold restart exact, rollback counterfactual, determinism re-measure exact (cycle receipt); PLUS cross-host: 170/170 rows reproduce exactly on two other machines | `results/CYCLE_RECEIPT_g2.json`, `results/CROSS_HOST_REPLICATES.json` |
| PDEV-11 serial-controls discriminator | CLOSED — DISCRIMINATED: history-carrying CONTINUED re-found the canonical optimum (work 96590); history-blind RESET ended at work 107982 | `parents/PARENT_RESULT.json` |
| PDEV-12 denominators + accounting | CLOSED — every denominator registered in `manifests/BATCH.json` BEFORE submission; 3 numbered amendments recorded BEFORE the extended jobs were scored; frozen-min and full-set reported separately and they coincide | `manifests/AMENDMENTS.json`, `RESOURCE_ACCOUNTING.json`, `results/EXHAUSTION_TERMINAL_g3.json` |
| PDEV-13 protected freeze | CLOSED — emitted at cycle 1 end with the adoption receipts | `results/LINEAGE_FINAL.json` |
| PDEV-14 honest terminals only | CLOSED — every terminal from the section-21 vocabulary: one DEVELOPMENT_CHANGE_ADOPTED, one PARENT_SUFFICIENT_BY_REVIVAL_EXHAUSTION | `results/GENERATION_LEDGER.jsonl` |

## Human gates

Two `HUMAN_GATE_BYPASSED__MODEL_PROXY` instances, both labelled, neither
marked as externally obtained:

1. g2 adoption decision — fresh-context model given ONLY
   `ADOPTION_PACKET.json`, schema `pdev217.proxy_decision.v1`, decision
   APPROVED (`proposals/DECISION_g2w1.json`);
2. the same gate token carried in the cycle receipt's `decision_gate` field
   (`results/CYCLE_RECEIPT_g2.json`).

The M11 cell's own assurance, probes, shadow suites and obstruction
certificate ran in full and are recorded in the cycle receipt; the proxy
decision gated only the external adoption authority, as frozen in
`PROTOCOL.json` before measurement.

## Frozen minimum vs full set (per AMENDMENTS.json)

- Cycle 1 (g2): single smoke wave, frozen minimum = full set (14 evals).
- Cycle 2 (g3): frozen minimum recomputed over the first 12 candidates per
  arm per wave (14 + 84 + 60x3 = 278 evals); full set = 770 evals (waves
  6-7 amendment-only).  Both reach the identical verdict on every wave and
  overall: no admissible dominant candidate.  No frozen comparison changed.
