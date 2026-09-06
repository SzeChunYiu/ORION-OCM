# Current bootstrap binding repair
The current prospective language-bootstrap audit now accounts for PR109's fixed
reported-speech authority. The existing three bootstrap controls and the existing
speaker/world-truth session control pass (4/4); the original three source-drift
failures are retained.

## Scope
- Only the current manifest changes: reviewed main, one session source binding,
  and P11's explicit fixed constitutional prior.
- Said-records carry speaker-axis rank 1, conversation scope and source identity.
  They do not independently establish world truth (world_truth rank 0).
- Numeric/seed inventories, minimal target, required ablations,
  protected_outcomes_read=false and AUDIT_AND_DESIGN_ONLY authority are unchanged.
- Core, auditor, tests, numerical code and historical scientific receipts are
  unchanged. All 738 files in the existing exact-sparse trial packet still match
  its original inventory.
- These checks are engineering accounting; they do not evaluate learned
  language capability or revisit protected outcomes.

## Evidence
[RECEIPT](RECEIPT.json) records exact commits, commands, runtime and source hashes.
[Manifest diff](manifest-repair.diff) is the complete current-contract change.
[Original manifest](original-manifest.json) preserves the predecessor bytes;
[current snapshot](current-manifest.json) and [audit](current-audit.json) bind
the repaired contract. [Session source diff](session-source.diff) records the
reviewed upstream behavior change, which this repair does not modify.

[Original CI failure](ci-run-34033765586-failed.log),
[local red](red.log) / [XML](red.xml), and
[green](green.log) / [XML](green.xml) retain the raw checks.
[SHA256SUMS](SHA256SUMS) binds this packet.

Upstream: [PR109](https://github.com/SzeChunYiu/ORION-OCM/pull/109).
Trigger: [run34033765586](https://github.com/SzeChunYiu/ORION-OCM/actions/runs/34033765586).
