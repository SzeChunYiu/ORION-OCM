# gmi-833-orchestrator-verifications-v1

Independent re-executions of load-bearing #833 claims by the orchestrating lane,
on **laptop-billy** rather than the host that produced them, recorded with scope.

A verification has a shelf life. Stated here in the past tense with its branch
head, so a later lane can see exactly what was checked and when, instead of
re-deriving it or - worse - assuming it.

| id | claim | package | outcome |
| --- | --- | --- | --- |
| V1 | repaired law `lambda* = eta*p*R0` exact on all worlds; retired law fails on skew | `gmi-833-z-z6-discrimination-v1` | CONFIRMED |
| V2 | IC-1: thresholds are marginal masses, never levels; 135/135; unique perfect law | `gmi-833-z-z1-master-principle-v1` | CONFIRMED |

Both are **re-executions** - same code, different host. That licenses
reproducibility and nothing more: not independent replication, not M5.

Closes no checkbox. See `VERIFICATIONS_V1.json` for every observed field.

## V3, V4 — proxy verdicts recorded as negatives (2026-09-19)

Two fresh-session model proxies (`HUMAN_GATE_BYPASSED__MODEL_PROXY`) returned
`NOT_SATISFIED`: AC05 (8/48 crosswalk rows without an in-place verified
citation) and AG8-R48 (the AJ13 checker writes GREEN as a literal; conjunct 6
untested; `MUTUAL_INTERPRETATION` unearned; process frame untagged). Both are
recorded verbatim in `VERIFICATIONS_V1.json`; neither row is closed. Their
objections are the frozen targets of lanes `research/833-revive-ac05` and
`research/833-revive-ag8`.
