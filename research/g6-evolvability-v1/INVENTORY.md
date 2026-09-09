# Bound in-repo failure / probe incidents

No root-cause labels were invented. Incident keys F1–F6 are the mapping from
issue #149; human diagnoses stay with the external curator.

## F1–F6 (issue #149 development incidents)

| Incident | Bound source | In HEAD tree | Trace completeness | Independent? |
|---|---|---|---|---|
| F1 | `3430919:research/math-language-learning-v1/ASSAY-ACQUISITION-DIAGNOSIS.md` | yes | SUMMARY_ONLY (four numeric funnel rows, all `final_pool=0`) | yes as a document; original A traces absent |
| F2 | `4f40e9f:research/cognitive-ladder/results/SUBSPACE_E1_V1.json` | no | SUMMARY_ONLY | **no** — shares this receipt with F3 |
| F3 | same blob as F2 | no | SUMMARY_ONLY | **no** |
| F4 | `4f40e9f:research/cognitive-ladder/results/DEPEND_E3_V1.json` | no | PARTIAL_REVISION_STEPS (120 numeric steps) | numeric steps only; full intervention calls absent |
| F5 | `4f40e9f:research/cognitive-ladder/results/DIAGNOSIS_E2_V1.json` | no | SUMMARY_ONLY | per-probe choices absent |
| F6 | `4f40e9f:research/cognitive-ladder/results/ESCALATION_INDEPENDENT_E4_V1.json` | no | SUMMARY_ONLY | 2000 instance traces absent |

F1 `FACTS.json` sha256 `37c41f6e13a44a628617651550a47f56f04341e661a8d682f8f0b5d02d891f19` is
not in this worktree. F2–F6 working-tree paths are absent on
`research/issue-165-g6-evolvability`; objects remain reachable at the ladder
commit used by self-evolution intake.

Hashes: [SOURCE-BINDS.json](SOURCE-BINDS.json).

## Historical ledger S11–S28

`src/ocm/selfmodel/replay.py` holds 18 recorded rows. Governance replay (narrow
shipped class, ceiling witnesses) is not diagnostic accuracy. Unlabeled
`diagnose()` on these rows, with ablations empty, yields UNKNOWN on every
layer.

## M11 planted S0–S7

`research/ocm-m11/M11_SELF_EVAL_V1.json` supplies true layers through an
oracle ablation channel. Issue #149 forbids treating this as blind
localization evidence. Inventoried only as a negative control class.

## Self-evolution generations (read-only at `d793f3f`)

Not present in this branch tree. Cycle files record:

| Cycle | Generation | Terminal |
|---|---|---|
| 0 | 0 → 1 | `DEVELOPMENT_CHANGE_ADOPTED` |
| 1 | 1 → 2 | `DEVELOPMENT_CHANGE_ADOPTED` |
| 2 | 2 → 2 | `SELF_DIAGNOSIS_NOT_IDENTIFIABLE` |

Catalogue: 10 C1 `existing_alternative` candidates; 8 probes/cycle. No third
earned change.
