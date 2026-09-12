# Stage F — blind recovery at tiny scope: report V1

Receipt `microscopes/results/STAGE_F_BLIND_RECOVERY_V1.json` (sha256 `76dcc50232c3269c…`).

Search: 3000 random candidates + 40 hill-climb steps from the top 12, per ecology, seed 0; the search saw only (score, charged cost).

## E_bind
best score 1.0, winners at θ=1.0: 6 (random-baseline fraction at θ: 0.002); classes: ['NUMERIC_SPARSE', 'NUMERIC_SPARSE', 'NUMERIC_SPARSE', 'NUMERIC_DENSE (M4 class)', 'STORE_PLUS_NUMERIC (hybrid)', 'STORE_PLUS_NUMERIC (hybrid)']

- score 1.0 · NUMERIC_SPARSE · writes/event 1 · store False · fx cells written 1 · cost {'desc': 42, 'exec': 48, 'upd': 16, 'ver': 0, 'rev': 0}
  f = `["NOT", ["SEL", "c0", ["NOT", "L"], ["SEL", "x1", "k0", "x0"]]]`
  g = `[["c1", "c1"], ["c1", "kh"]]`
- score 1.0 · NUMERIC_SPARSE · writes/event 1 · store False · fx cells written 1 · cost {'desc': 42, 'exec': 60, 'upd': 16, 'ver': 0, 'rev': 0}
  f = `["OR", ["SEL", "x0", ["SUB", "x3", "x3"], "k1"], ["THRESH", ["AND", "x1", "x0"]]]`
  g = `[["c1", "L"], ["c1", "kh"]]`
- score 1.0 · NUMERIC_SPARSE · writes/event 0 · store False · fx cells written 2 · cost {'desc': 42, 'exec': 84, 'upd': 16, 'ver': 0, 'rev': 0}
  f = `["OR", ["ADD", ["OR", "x1", "c3"], ["SEL", "c0", "c1", "c1"]], ["SEL", ["OR", "x0", "x1"], "x3", ["THRESH", "k1"]]]`
  g = `[["c1", "c1"], ["c0", "L"]]`
- score 1.0 · NUMERIC_DENSE (M4 class) · writes/event 3 · store False · fx cells written 3 · cost {'desc': 42, 'exec': 72, 'upd': 72, 'ver': 0, 'rev': 0}
  f = `["ADD", ["SEL", "x0", ["NOT", "c2"], ["SEL", "c3", "kq", "c1"]], ["SEL", ["SEL", "c3", "x1", "x2"], "x3", "x1"]]`
  g = `[["c1", "y"], ["c3", ["NEG", ["THRESH", "out"]]], ["c2", ["ADD", "c3", ["MUL", "e", "kq"]]], ["c2", "c1"]]`
- score 1.0 · STORE_PLUS_NUMERIC (hybrid) · writes/event 3 · store True · fx cells written 1 · cost {'desc': 122, 'exec': 152, 'upd': 38, 'ver': 0, 'rev': 0}
  f = `["SEL", ["SEL", "x1", ["ADD", "c3", "k1"], ["OR", "x0", "k1"]], ["SEL", ["THRESH", "x3"], ["MUL", "c3", "x3"], "L"], ["XOR", ["XOR", "x3", "c1"], ["ADD", "c2", "x3"]]]`
  g = `[["c1", "y"], ["INSERT", "y"]]`
- score 1.0 · STORE_PLUS_NUMERIC (hybrid) · writes/event 3 · store True · fx cells written 2 · cost {'desc': 122, 'exec': 128, 'upd': 62, 'ver': 0, 'rev': 0}
  f = `["SEL", ["NOT", ["GT", "x0", "k0"]], ["OR", ["NOT", "x2"], ["XOR", "x3", "x3"]], ["SEL", ["XOR", "x0", "x1"], "kq", ["XOR", "c1", "L"]]]`
  g = `[["INSERT", ["THRESH", ["NOT", "x2"]]], ["c3", "kq"], ["c2", "kq"]]`

## E_smooth
best score 0.8333, winners at θ=0.85: 0 (random-baseline fraction at θ: 0.0); classes: []


## Verdicts
{
 "F1_bind_winners_store_local": {
  "fraction_store_local": 0.0,
  "fraction_numeric_dense": 0.16666666666666666,
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

