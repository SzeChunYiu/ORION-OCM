# §16 boxes this lane can check

| Box | Status |
|---|---|
| Do not label benchmark truth from generator intent where the intended cause is the target | **CHECK_POLICY** — fail-closed in `policy.py`; ME-X1 cause labels use recovery only. Other suites audited, scoring code not rewritten. |
| Recover ground truth independently where tractable | **CHECK** — ME-X1 50/50 recovered; 32 planted≠recovered. |
| Use independently authored world/task families for E3+ | **BUILT_PENDING_E3_USE** — pipeline built per `P1_PIPELINE_FREEZE_V1.json`: 3 IPC STRIPS domains transcribed in `ipc_domains/` (blocksworld/gripper/logistics, external authorship), independent validator `p1_validator.py` (no src/ocm imports), family table `P1_FAMILY_TABLE_V1.json` (3 families, 13 members, hostile selftest green). Grants no E3 execution rights (E3_PROTOCOL_FREEZE_V1 promotion_rule). |
| Preserve generator-intent audit | **CHECK** — planted family/variant retained as audit-only. |
| Separate task generator from diagnosis policy | **PARTIAL** — ME-X1 arms already omit the oracle; planter still filters on oracle invariants and shares the taxonomy. |
| Externally validate key taxonomies | **OPEN** |
| Retain artifact-explained positive results as negative findings | **CHECK_POLICY** — 17 POSITIVE family matches classified as rejection-sampled artifacts. |
