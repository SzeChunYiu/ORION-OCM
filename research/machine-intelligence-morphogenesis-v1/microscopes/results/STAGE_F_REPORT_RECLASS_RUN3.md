# Stage F — blind recovery at tiny scope: report V1

Receipt `microscopes/results/STAGE_F_BLIND_RECOVERY_V1.json` (sha256 `de81135b67c85169…`).

Search: 6000 random candidates + 80 hill-climb steps from the top 12, per ecology, seed 2; the search saw only (score, charged cost).

## E_bind16
best score 1.0, winners at θ=1.0: 9 (random-baseline fraction at θ: 0.0015); classes: ['LOCAL_MEMORY (store or cell-memory; M1/M5 class)', 'LOCAL_MEMORY (store or cell-memory; M1/M5 class)', 'LOCAL_MEMORY (store or cell-memory; M1/M5 class)', 'LOCAL_MEMORY (store or cell-memory; M1/M5 class)', 'LOCAL_MEMORY (store or cell-memory; M1/M5 class)', 'STORE_PLUS_NUMERIC (hybrid)', 'LOCAL_MEMORY (store or cell-memory; M1/M5 class)', 'LOCAL_MEMORY (store or cell-memory; M1/M5 class)', 'STORE_PLUS_NUMERIC (hybrid)']

- score 1.0 · LOCAL_MEMORY (store or cell-memory; M1/M5 class) · writes/event 2 · store True · fx cells written 0 · cost {'desc': 362, 'exec': 272, 'upd': 408, 'ver': 0, 'rev': 0}
  f = `"L"`
  g = `[["INSERT", "y"]]`
- score 1.0 · LOCAL_MEMORY (store or cell-memory; M1/M5 class) · writes/event 2 · store True · fx cells written 0 · cost {'desc': 362, 'exec': 320, 'upd': 440, 'ver': 0, 'rev': 0}
  f = `["NEG", "L"]`
  g = `[["INSERT", ["NEG", "y"]]]`
- score 1.0 · LOCAL_MEMORY (store or cell-memory; M1/M5 class) · writes/event 2 · store True · fx cells written 0 · cost {'desc': 362, 'exec': 320, 'upd': 408, 'ver': 0, 'rev': 0}
  f = `["THRESH", "L"]`
  g = `[["INSERT", "y"]]`
- score 1.0 · LOCAL_MEMORY (store or cell-memory; M1/M5 class) · writes/event 2 · store True · fx cells written 0 · cost {'desc': 362, 'exec': 272, 'upd': 504, 'ver': 0, 'rev': 0}
  f = `"L"`
  g = `[["INSERT", ["SUB", ["ADD", "k1", "y"], ["OR", "c3", "k1"]]]]`
- score 1.0 · LOCAL_MEMORY (store or cell-memory; M1/M5 class) · writes/event 2 · store True · fx cells written 0 · cost {'desc': 362, 'exec': 272, 'upd': 472, 'ver': 0, 'rev': 0}
  f = `"L"`
  g = `[["INSERT", ["ADD", ["THRESH", "y"], "k0"]]]`
- score 1.0 · STORE_PLUS_NUMERIC (hybrid) · writes/event 3 · store True · fx cells written 1 · cost {'desc': 362, 'exec': 464, 'upd': 536, 'ver': 0, 'rev': 0}
  f = `["ADD", ["SEL", ["ADD", "kh", "c2"], ["XOR", "c3", "L"], "x2"], "k0"]`
  g = `[["INSERT", ["NOT", ["SUB", "y", "e"]]], ["c3", "out"], ["c3", "kq"]]`

## Verdicts
{
 "F1_bind_winners_store_local": {
  "fraction_store_local": 0.7777777777777778,
  "fraction_numeric_dense": 0.0,
  "holds": true
 },
 "F2_smooth_winners_numeric_dense": {
  "fraction_numeric_dense": null,
  "fraction_store_local": null,
  "holds": false
 },
 "F3_handover": "NOT_OBSERVABLE__NO_STORE_LOCAL_CANDIDATE_REACHED_THETA_IN_E_SMOOTH"
}

E2 exploratory at tiny scope, single search family, one basis column (B0), one seed; post-hoc label-free classification; not a confirmatory blind-recovery result (#377 §13 requires matched generic search parents, multiple encodings and seeds).

