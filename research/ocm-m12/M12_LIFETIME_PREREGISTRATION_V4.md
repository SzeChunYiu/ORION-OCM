# M12 pre-registration V4 — paired lifetimes with a primary family (theory batch 7 G7/G8)

Frozen before any V4 outcome is read. V3 (`M12_LIFETIME_PREREGISTRATION_V3.md`, result
`M12_PAIRED_LIFETIMES_EVAL_V1.json`) is kept as the frozen record; batch 7 G8 showed its rule was
under-specified (no primary family, unbounded family count, two-sided unanimous test with power
0.43) — ledger S37. V4 re-registers the analysis and runs on **fresh** streams.

## Frozen items

| Item | Value |
|---|---|
| Streams | 8 fresh streams, seed `OCM-M12-V4`, same generator as V3 plus the world-true out-of-scope half (10 questions true in the world but unlicensed by the given facts; expected answer UNKNOWN, G7); manifest `research/ocm-m12/M12_V4_STREAM_MANIFEST_V1.json`, SHA-256 `72d7d78203895035cb851cdf2abc1194d29558642f08926467dc1889d413c9a2`; leak check 8/8 |
| Unit of inference | the lifetime (paired OCM vs whole-system parent on one stream) |
| Primary family | A conversations — one-sided exact sign test (H1: OCM > parent) over the 8 lifetime differences at α = 0.05: rejects iff ≥ 7 of 8 non-tied differences are positive (size 9/256 ≈ 0.035; power 0.81 at p = 0.9) |
| Secondary families (6) | A post-deployment lessons, A honest unknown (incl. the world-true half), D causal identification, E cross-domain transfer, F revision integrity, G self-repair — same one-sided test at α/6 (rejects iff 8/8) |
| All other families | descriptive |
| Collapsed-one-coin flag | a family whose eight differences are identical is flagged (shared variation may reduce it to one coin); reported, and its rejection is stated with the flag |
| Decision | OCM_LIFETIME_RESIDUAL_SUPPORTED iff the primary family rejects and kill gates are 0; PARENT_SUFFICIENT iff the primary is a tie and no secondary rejects; INCONCLUSIVE otherwise; CANNOT_CHECK on any gate hit |
| Kill gates | V3 gates (protected exposure, external IO, dead-skill run after revocation, missing outcomes, stream leak) + ledger-chain identity (F5) |
| Reference arm | the open-weight model on the same eight streams, graded four-class (licensed / unlicensed-true / unlicensed-false / wrong, G7); REFERENCE, never in the decision |
| Replication | second host, deterministic block byte-equal |
| Stopping rule | one run; any code change after outcome access relabels the run DEV_CALIBRATION and requires V5 |
