# Parallel developmental evolution (issue #217)

Supercomputer candidate search for multi-generation OCM self-development.
The canonical lineage stays SERIAL (one adoption per generation cycle through
the real M11 path); everything parallel happens in the search layer.

## What this is

* A **morphology grammar** (`execution/pdev_grammar.py`): declarative machine
  configurations over 9 dimensions (basic-unit FORM x knowledge-space
  STRUCTURE), classified C3/C4/C5, with the checker/evaluator/authority (C)
  hard-excluded from the grammar.
* A **frozen meter** (`execution/pdev_runner.py`): executes any legal
  morphology through the vendored byte-identical donor runtime and returns the
  charged resource vector.  No scorer-field reads, no unmetered paths.
* **16 matched search arms** (`execution/pdev_search.py`) on an identical
  budget/information surface, including a MAP-Elites **quality-diversity
  archive** (3240 descriptor cells, persisting across generations) and scalar
  optimizers as controls.
* **11 fail-closed hostiles** (`execution/pdev_hostiles.py`): checker
  weakening, protected-data access (dynamic audit), memorization, unmetered
  scans, hidden preprocessing, preservation regression, overcompression,
  cost-moving (independent recomputation), the registered adverse example,
  novelty-gaming, niche-colonizing.
* A **parent-disjoint task pool** (`execution/pdev_tasks.py`): fresh task
  identities with checkable disjointness from everything the #149 parent
  consumed.
* The **canonical serial cell** (`execution/pdev_machine.py`): the vendored
  #149 EvolutionCell over the real `ocm` package; adoption requires the full
  M11 path AND a frozen external decision
  (`HUMAN_GATE_BYPASSED__MODEL_PROXY` — a fresh-context model given only the
  frozen adoption packet; fail-closed).
* **Serial controls** (PDEV-11): PARENT (never adopts), CONTINUED (from g2),
  RESET (from the donor initial morphology) — same meter, same suites, same
  frozen scalar rule.

## Run layout (LUNARC)

```
run/                                  # /projects/hep/fs9/users/scyiu/pdev217-20260909/run
  task_ledger.json  search_history.jsonl
  DIVERSITY_ARCHIVE_V1.json
  CANDIDATE_LEDGER.jsonl  GENERATION_LEDGER.jsonl
  generations/state.json               # run state (paths["state"])
  generations/g{G}/suites.json incumbent.json parent_batch_g{G}.json
  generations/g{G}/waves/w{W}/{batch,verify_batch,aggregate}.json eval/ verify/
  generations/g{G}/{ADOPTION_PACKET,decision,cycle_receipt}.json
  parents/{PARENT,CONTINUED,RESET}/  lineage/CONTINUED/
  manifests/{BATCH.json,submissions.jsonl}
```

Bootstrap: `python3 centre_init.py --run-root RUN`.  One wave:
`slurm/run_wave.sh RUN GEN WAVE SALT QUOTA` (chained sbatch: generate ->
evaluate array -> aggregate collect -> verify array -> aggregate finalize;
parent array rides along once per generation).  One generation cycle (after a
winner exists and the decision file is frozen):
`python3 centre_cycle.py --run-root RUN --generation G [--freeze]`.

## Freeze discipline

Everything outcome-bearing is frozen before measurement: grammar, pool,
suites, arms + seeds (master salt `pdev217-20260909-uniform-ignorance`),
hostiles, selection rules (PDEV-8), budgets, denominators (manifests/BATCH.json
BEFORE submission).  See `PROTOCOL.json`.  Terminals only from the issue's
section 21 (`EXPECTED_TERMINALS.json`); `PARENT_SUFFICIENT_*` is a SUCCESS.

## Deliverables map

`REPO_STATE.json` (PDEV-0) - `PROTOCOL.json` - `LINEAGE_V1.json` /
`LINEAGE_FINAL.json` (PDEV-1/PDEV-9) - `EXPECTED_TERMINALS.json` -
`RESOURCE_ACCOUNTING.json` + `manifests/` (PDEV-12, incl. `AMENDMENTS.json`) -
`execution/` (PDEV-2..8) - `slurm/` (PDEV-3) - `parents/PARENT_RESULT.json`
(PDEV-2/PDEV-11) - `incidents/INCIDENTS.jsonl` (PDEV-6) -
`results/ADVERSE_AND_CANNOT_CHECK.jsonl` (PDEV-6) - `proposals/` (governance
proposals incl. external-gate provenance) - `results/` (campaign summaries) -
`CLAIM_DISPOSITION.md` + `SHA256SUMS` at close.

## Outcome (closed 2026-09-09)

Programme executed end-to-end on LUNARC (hep partition, account hep2023-1-3)
with cross-host replicates on two laptops (AMENDMENT-3).  Two generation
cycles, the bound:

* **Cycle 1 (g2), wave 1** (smoke quota=1, 14 evals, array 3585267; parent
  array 217 entries, 3585268; verify 3585499): winner `g2.w1.repair.4`
  (arm `repair`, class C3, origin program_repair) with vector
  `failures=0 persistent_bytes=31610 work=96590` vs incumbent
  `0 / 31610 / 97202` — a strict work improvement at equal failures and
  bytes.  Full M11 path inside the vendored cell: probes, shadow suites,
  assurance, honest ObstructionCertificate for the D3 escalation (every
  measured lower-layer alternative recorded, none both dominant and
  admissible), LIVE certified warrants, ceiling evidence admitted as runtime
  evidence.  Frozen `HUMAN_GATE_BYPASSED__MODEL_PROXY` decision approved;
  cycle terminal **DEVELOPMENT_CHANGE_ADOPTED**, generation 3 installed,
  protected freeze identity
  `e56a24cddecc56a127ec22097eb70d765a23cdfd4822021f213c8a8ff7333ac5`
  (`results/CYCLE_RECEIPT_g2.json`, `results/LINEAGE_FINAL.json`).
* **Cycle 2 (g3), waves 1-7** (770 evals; frozen waves 1-5 plus amendment
  waves 6-7 per `manifests/AMENDMENTS.json`): no admissible dominant
  candidate in ANY wave — waves 1/2/4 reached final admissibility (2/6/1
  rows) and failed at `dominance`; waves 3/5/6/7 offered nothing past the
  collect frontier.  Frozen-minimum (first 12/arm) and full-set verdicts
  coincide on every wave: no winner.  Cycle terminal
  **PARENT_SUFFICIENT_BY_REVIVAL_EXHAUSTION** (SUCCESS):
  `results/EXHAUSTION_TERMINAL_g3.json`.
* **PDEV-11 discriminator: DISCRIMINATED.**  CONTINUED (history-carrying
  serial control) adopted exactly one change and independently re-found the
  canonical optimum (digest `e05e3ae63bb01037`, work 96590); RESET
  (history-blind) adopted twice and ended at a different morphology (work
  107982, bytes 71249).  Carried history earned a strictly better final
  parent-space morphology under the same frozen scalar
  (`parents/PARENT_RESULT.json`).
* **Cross-host determinism (AMENDMENT-3)**: 170/170 frozen eval rows
  re-measured on `billy` (laptop) and `billy-laptop-old` (tailscale)
  reproduce the LUNARC vectors exactly — status, n, success, work,
  persistent_bytes (`results/CROSS_HOST_REPLICATES.json`).  Replicate rows
  never enter selection.
* **Scale**: 1168 slurm task records, 784 candidate evaluations (0 crashes),
  340 parent-entry measurements, 10 verify tasks; 3900 CPU-seconds
  (~1.08 CPU-hours) total (`results/RESOURCE_LEDGER.json`).  The append-only
  candidate ledger suffered concurrent-append interleaving (INC-3); it was
  rebuilt canonically from the single-writer per-candidate files
  (`results/CANDIDATE_LEDGER_REBUILT.jsonl`, 784/784 rows).
* **Hostiles**: H9's registered adverse example measured on every verified
  candidate (10 `ADVERSE_RECORDED` rows, zero `CANNOT_CHECK`)
  (`results/ADVERSE_AND_CANNOT_CHECK.jsonl`).
