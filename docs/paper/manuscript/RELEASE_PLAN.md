# Release plan for the OCM manuscript package

Purpose: close the readiness report's release blockers (archived release with a persistent identifier; release-integrity binding) in the way the programme's rules allow, and name the one action that stays with the operator.

## 1. Package contents (built by `tools/paper/build_release.py`; rebuilt on every manuscript commit, verified by `.github/workflows/paper-release.yml`)

| Item | Source |
|---|---|
| `main.md`, `claims_map.md`, `claims_verification.txt`, `figures.md`, `positioning.md`, `positioning_refs.md` | `docs/paper/manuscript/` at the release commit |
| `reviews/*` (venue contract, three blind reviews, editor synthesis, revision log, readiness report) | same |
| receipt chain | `docs/provenance/M1…M12_RECEIPT_V1.json`, `M12_REPLICATION_RECEIPT_V1.json`, `M12_PAIRED_RECEIPT_V1.json`, `M12_PAIRED_RECEIPT_V4.json`, `M12_PAIRED_REPLICATION_RECEIPT_V4.json`, `M12_REFERENCE_RECEIPT_V1.json`, and the current-runtime successor receipts under `docs/provenance/runtime_revision_20260905_v4/` |
| evaluation results | `research/ocm-m*/…json` including `research/ocm-m12/M12_PAIRED_LIFETIMES_EVAL_V4R.json`, `docs/M12_V4R_REEVALUATION_NOTE.md`, `research/ocm-n1/N1_UD_INDUCTION_V1.json` (whatever the text cites) |
| evidence successor files | `docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md` and `_V2.md`, `docs/theorems/*.json` including `OCM_SELF_OBLIGATION_REGISTRY_V2.json` (the V1 files are byte-frozen by the custody regime; both generations are packaged) |
| theory | ORION-V2 `research/machine-epistemics-theory/` batch documents and checkers at the ORION-V2 commit named in the manuscript |

## 2. Release-integrity binding

1. `SHA256SUMS` over every packaged file, plus the ORION-OCM and ORION-V2 commit ids.
2. `RELEASE_MANIFEST.json`: for every number-bearing sentence of `main.md`, the `claims_map.md` row and the receipt field it reads (the claim-verification script re-run at release time must print 0 MISMATCH / 0 MISSING).
3. The manifest's own SHA-256 recorded in the receipt chain as `docs/provenance/PAPER_RELEASE_RECEIPT_V1.json` (bound files = the package list; deterministic result = the claims-verification counts). Built 2026-09-06: 87 package files, 257 claims rows OK, terminal `PACKAGE_BOUND__IDENTIFIER_PENDING`; the package is rebuilt whenever the manuscript or a bound file changes, so the receipt on the branch head is always the binding of that head.
4. CI verifies the release receipt like every other receipt.

## 3. Persistent identifier (human gate)

Minting a DOI (Zenodo or the institutional archive) requires the operator's account. Until it exists, the manuscript's data-availability statement names the GitHub release tag and commit ids and carries the label `HUMAN_GATE_BYPASSED__MODEL_PROXY` for the identifier line, per the programme's rule on human-only gates; the operator's upload replaces the label with the DOI.

## 4. Order

Positioning text merged → pipeline round 2 (re-review with V4-R and the matched transfer cells) → text frozen → package built and bound → release tag → DOI by the operator → submission.
