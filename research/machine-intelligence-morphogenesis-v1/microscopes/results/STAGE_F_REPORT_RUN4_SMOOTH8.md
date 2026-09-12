# Stage F — blind recovery at tiny scope: report V1

Receipt `microscopes/results/STAGE_F_BLIND_RECOVERY_V1.json` (sha256 `cc168c294bf4af5c…`).

Search: 12000 random candidates + 160 hill-climb steps from the top 12, per ecology, seed 3; the search saw only (score, charged cost).

## E_smooth8
best score 0.7676, winners at θ=0.85: 0 (random-baseline fraction at θ: 0.0); classes: []


## Verdicts
{
 "F1_bind_winners_store_local": {
  "fraction_store_local": null,
  "fraction_numeric_dense": null,
  "holds": false
 },
 "F2_smooth_winners_numeric_dense": {
  "fraction_numeric_dense": null,
  "fraction_store_local": null,
  "holds": false
 },
 "F3_handover": "NOT_OBSERVABLE__NO_STORE_LOCAL_CANDIDATE_REACHED_THETA_IN_E_SMOOTH"
}

E2 exploratory at tiny scope, single search family, one basis column (B0), one seed; post-hoc label-free classification; not a confirmatory blind-recovery result (#377 §13 requires matched generic search parents, multiple encodings and seeds).

