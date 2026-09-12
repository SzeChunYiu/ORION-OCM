# Stage F — blind recovery at tiny scope: report V1

Receipt `microscopes/results/STAGE_F_BLIND_RECOVERY_V1.json` (sha256 `01328599f70f5fd7…`).

Search: 12000 random candidates + 160 hill-climb steps from the top 12, per ecology, seed 1; the search saw only (score, charged cost).

## E_bind
best score 1.0, winners at θ=1.0: 12 (random-baseline fraction at θ: 0.0026666666666666666); classes: ['NUMERIC_SPARSE', 'NUMERIC_SPARSE', 'NUMERIC_SPARSE', 'NUMERIC_SPARSE', 'NUMERIC_SPARSE', 'STORE_LOCAL (M1/M5 class)', 'STORE_PLUS_NUMERIC (hybrid)', 'STORE_LOCAL (M1/M5 class)', 'STORE_PLUS_NUMERIC (hybrid)', 'STORE_PLUS_NUMERIC (hybrid)', 'STORE_LOCAL (M1/M5 class)', 'STORE_LOCAL (M1/M5 class)']

- score 1.0 · NUMERIC_SPARSE · writes/event 1 · store False · fx cells written 1 · cost {'desc': 42, 'exec': 24, 'upd': 8, 'ver': 0, 'rev': 0}
  f = `["OR", "x1", ["NOT", "x0"]]`
  g = `[["c3", "x1"]]`
- score 1.0 · NUMERIC_SPARSE · writes/event 1 · store False · fx cells written 1 · cost {'desc': 42, 'exec': 36, 'upd': 8, 'ver': 0, 'rev': 0}
  f = `["ADD", ["NOT", ["SUB", "x0", "x1"]], "L"]`
  g = `[["c0", "y"]]`
- score 1.0 · NUMERIC_SPARSE · writes/event 0 · store False · fx cells written 1 · cost {'desc': 42, 'exec': 48, 'upd': 8, 'ver': 0, 'rev': 0}
  f = `["ADD", "x1", ["SEL", "k0", ["GT", "c2", "x2"], ["NOT", "x0"]]]`
  g = `[["c3", "c3"]]`
- score 1.0 · NUMERIC_SPARSE · writes/event 1 · store False · fx cells written 1 · cost {'desc': 42, 'exec': 84, 'upd': 8, 'ver': 0, 'rev': 0}
  f = `["SUB", ["XOR", ["XOR", "kq", "c0"], ["SUB", "k0", "L"]], ["ADD", ["GT", "c3", "x0"], ["SUB", "x0", "x1"]]]`
  g = `[["c1", "out"]]`
- score 1.0 · NUMERIC_SPARSE · writes/event 2 · store False · fx cells written 2 · cost {'desc': 42, 'exec': 84, 'upd': 24, 'ver': 0, 'rev': 0}
  f = `["SUB", ["OR", ["SEL", "x3", "c3", "x1"], "x1"], ["SUB", ["MUL", "kq", "kh"], ["XOR", "x0", "k1"]]]`
  g = `[["c0", "y"], ["c0", "x3"], ["c1", "e"]]`
- score 1.0 · STORE_LOCAL (M1/M5 class) · writes/event 2 · store True · fx cells written 0 · cost {'desc': 122, 'exec': 20, 'upd': 30, 'ver': 0, 'rev': 0}
  f = `"L"`
  g = `[["INSERT", "y"]]`

## E_smooth
best score 0.8542, winners at θ=0.85: 1 (random-baseline fraction at θ: 0.0); classes: ['NUMERIC_SPARSE']

- score 0.8542 · NUMERIC_SPARSE · writes/event 2 · store False · fx cells written 2 · cost {'desc': 42, 'exec': 320, 'upd': 48, 'ver': 0, 'rev': 0}
  f = `["SEL", ["NEG", ["ADD", "L", "x1"]], ["AND", ["THRESH", "k0"], ["GT", "c3", "c3"]], ["SEL", "x3", ["ADD", "kq", "x1"], ["MUL", "x1", "c2"]]]`
  g = `[["c0", "x0"], ["c2", "k1"], ["c2", "e"]]`

## Verdicts
{
 "F1_bind_winners_store_local": {
  "fraction_store_local": 0.3333333333333333,
  "fraction_numeric_dense": 0.0,
  "holds": false
 },
 "F2_smooth_winners_numeric_dense": {
  "fraction_numeric_dense": 0.0,
  "fraction_store_local": 0.0,
  "holds": false
 },
 "F3_handover": "NOT_OBSERVABLE__NO_STORE_LOCAL_CANDIDATE_REACHED_THETA_IN_E_SMOOTH"
}

E2 exploratory at tiny scope, single search family, one basis column (B0), one seed; post-hoc label-free classification; not a confirmatory blind-recovery result (#377 §13 requires matched generic search parents, multiple encodings and seeds).

