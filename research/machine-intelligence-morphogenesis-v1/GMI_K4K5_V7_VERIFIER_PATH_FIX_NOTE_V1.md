# K4 V7 / K5 V7 verifier path fix — disclosure note (RV-377-118 Lane A)

Approved by the lane lead on 2026-09-12 with the conditions recorded here. Merged in PR #455
(merge commit `9b06a3b6`), executed on LUNARC.

## The defect

`hpc/gmi_beacon_verify.py` retrieved the execution freeze from its declared commit with
`git show <commit>:<path>` where `<path>` was relative to the **study directory**
(`research/machine-intelligence-morphogenesis-v1`, the `repo_root` every caller passes).
Git resolves a bare `<commit>:<path>` against the **repository toplevel**, so the lookup failed
with `Path 'research/.../GMI_K4_EXECUTION_FREEZE_V7.json' exists, but not 'GMI_K4_EXECUTION_FREEZE_V7.json'`
and every protected task, submitter and aggregate raised
`cannot retrieve execution freeze from declared commit` before any round was checked.
The existing tests passed because they used `repo_root == toplevel`.

## The fix

The path is now resolved against `git rev-parse --show-toplevel` (realpath on both sides).
Nothing else in the verifier changed: schema, `no_reroll`, blob-membership check, commit
timestamp, `round_for`, delay, chain hash, signature/randomness consistency and the returned
contract are byte-for-byte the same logic.

| Freeze | Superseded verifier pin | Executed verifier commit |
|---|---|---|
| `GMI_K4_EXECUTION_FREEZE_V7.json` | `1dcbd564791511466de858d55d6f2ddbee22a92d` | `bf59efd7` (fix), hardened + regression test in `fd7ea7cb` |
| `GMI_K5_BH_EXECUTION_FREEZE_V7.json` | `11b011f686071ec6129ce76040490dff6bfc86ac` | same |

The freeze JSONs are byte-identical to main base `7998ef56`
(`GMI_K4_EXECUTION_FREEZE_V7.json` blob `084ba26d`, `GMI_K5_BH_EXECUTION_FREEZE_V7.json` blob
`3a8003e1`, `GMI_K4_NULL_AWARE_SUCCESSOR_FREEZE_V5.json` blob `fb85013a`,
`GMI_K4_LOFO_FREEZE_V1.json` blob `caea83eb`). No round, seed, threshold, task-plan or
engine semantics changed.

Two further frozen execution scripts were broken as committed and fixed in the same PR with
the same discipline (no semantic change): `hpc/gmi_k4_probe.py` (`sh` helper shadowed by the
science-freeze hash) and the `plan()` of `hpc/gmi_k5_bh_task_v7.py` / `hpc/gmi_k5_bh_aggregate_v7.py`
(undefined `s`; the first K5 job 3604928 failed on all 256 tasks and its receipts are kept under
`microscopes/results/k5_bh_v7_invalid_job3604928_plan_bug/`, outside the aggregate glob).

## Development proof of verification and seed derivation (receipts discarded)

Run under `srun` on partition `aurora` from the merged main (`9b06a3b6`), host token `DEVPOSTHOC`,
receipts deleted afterwards so no task index is duplicated. These runs happened after the
protected arrays, not before, because the lead's condition arrived after PR #455 merged.

| Task | Dev budget | Verified round | Derived seed | Same seed and task_hash as protected receipt |
|---|---|---|---|---|
| K4 index 0 (`K4-A01`, `G1_TENSOR_GRAPH`, `w1`) | 1 000 | 32138309 | 1984095976 | yes (`28f30ef6…5c0a64`, job 3605505) |
| K5 index 0 (`B_COMPILE_SEARCH`, `query_reuse=1`, r0) | n/a | 32138625 | 4249052434 | yes (`4254f331…708aca`, job 3605249) |

## Execution record

* LUNARC clone: `/projects/hep/fs9/users/scyiu/ORION-OCM-gmi` (home is over quota; fs9 is
  visible from compute nodes). Scripts run with `PYTHONPATH=<study dir>`.
* Partition `aurora`, account `lu2026-2-51`: the `lu48` association MaxSubmit=300 counts array
  tasks individually and 138 other-lane jobs occupy it; aurora's association was empty, so both
  arrays ran whole at full concurrency (`0-263%264`, `0-255%256`).
* Job ids: K5 V7 = 3605249; K4 V7 = 3605505 (an earlier K4 submission 3605184 was cancelled
  before any receipt was written). Recorded in `hpc/GMI_K4_SUBMISSION_RECEIPT_V8.json` and
  `hpc/GMI_K5_BH_SUBMISSION_RECEIPT_V7.json`.
* `GMI_WORK_MANIFEST_V1.json` unit U-A001 is stale (V5 beacon, `--render` flag) and untouched;
  the V7 submitters `hpc/gmi_k4_submit.py` and `hpc/gmi_k5_bh_submit_v7.py` are the executed path.
