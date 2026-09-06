# Reviewer 3, round 2 (reproducibility, artifacts, release)

Written against draft V3.3, the claims map (256 rows) and the repository state at ORION-OCM main after PR #75, blind to the other round-2 reports.

## Assessment

**Claim verification.** `tools/paper/verify_claims.py` reports 256 rows OK, exit 0, on the paper branch rebased onto main; the ten new rows read the V4-R evaluation file, the N1 receipt and the V2 obligation registry. The claims map now reads two ORION-OCM regimes' successor files (the V2 ledger and registry) because the archived V1 files are byte-frozen by the custody regime; the manuscript does not need to explain this, but the release package must include both V1 and V2 files.

**R3-r2-1 (major, closable):** the N1 receipt of record was produced under concurrent load and superseded an earlier run's counts on the tracking issue. For reproducibility the receipt of record should come from a run with no other job on the host, or the receipt should record the load condition (it records wall time only). Recommend a load-free re-run as the receipt of record, or a per-sentence result file so that the reached prefix can be compared across hosts.

**R3-r2-2 (minor):** the data-availability statement still says "an archived release with a persistent identifier is pending" and should name the label under which the identifier line is proxied (`HUMAN_GATE_BYPASSED__MODEL_PROXY`, per `RELEASE_PLAN.md`) so the reader knows what "pending" means at submission time.

**R3-r2-3 (minor):** the release plan's package list should add `docs/self-application/OCM_SELF_APPLICATION_LEDGER_V2.md`, `docs/theorems/OCM_SELF_OBLIGATION_REGISTRY_V2.json`, `research/ocm-m12/M12_PAIRED_LIFETIMES_EVAL_V4R.json`, `docs/M12_V4R_REEVALUATION_NOTE.md` and `research/ocm-n1/N1_UD_INDUCTION_V1.json`, all now read by the claims map.

Round-1 R3-6 (archive pending) remains open and is a release action, not a manuscript edit.

## Recommendation
Minor revision. The artifact chain is intact; the two open items are a receipt-of-record hygiene point and release-package completeness.
