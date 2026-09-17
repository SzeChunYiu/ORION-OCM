# REV-L47-CUSTODY-GAPS — custody-gap tranche (CLOSED_GREEN)

Ticket REV-L47-CUSTODY-GAPS (GMI #833): 18 CUSTODY_NON_DEMONSTRABLE corpus
packages from the corpus-passes v2 L47 screen, worked to 18/18 principled
terminals.

- `TRIAGE_V1.json` — 6 MECHANICAL / 12 SUBSTANTIVE, every decision cited
  (`triage_timeline_v1.json`, `triage_crosspkg_v1.json`; collectors
  `collect_triage_v1.py`/`v2.py`).
- `mechanical_specs_v1.json` + `custody_repair_v1.py` +
  `CUSTODY_REPAIR_RECEIPTS_V1.json` — tree-level custody repair for the
  mechanical class (L1 order / L2 separation / L3 window immobility /
  L4 blob pins + per-package extra legs; negative controls verified).
- `REV_FREEZE_V1.md` — W4 prospective freeze, committed before any re-run.
- `run_batch_v1.py` — remote batch runner (mechanical self-tests,
  substantive re-runs, section-d replica stages A/B with in-repo custody
  chain verification).
- `REPLICA_SAMPLE_V1.json`, `REPLICA_TRAIN_V1.json`,
  `REPLICA_FIT_FREEZE_V1.json` — section-d replica custody artifacts
  (stage-2 freeze committed before any n=17/31 execution).
- `reruns/billy-old/`, `reruns/billy-laptop/` — per-package receipts
  (primary py3.14; multihost agreement py3.8, version-bound disagreements
  root-caused as zip-strict artifacts).
- `VERDICTS_V1.json` — final per-package verdicts + routed new finding
  (AJ9A-AUDIT-WALKER-LIST-EVASION, aj-lane owned).

Registers: corpus-passes `VERDICT_REGISTER_L47_REV_ADDENDUM_V1.json`
(append-only); baseline `SUPPLEMENT_1_REV_L47_CUSTODY_GAPS.md`. Nothing on
the frozen V1 registers was edited; no frozen corpus content was touched.
