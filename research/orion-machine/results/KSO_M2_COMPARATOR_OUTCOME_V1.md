# KSO M2 comparator outcome V1

Receipt: `KSO_M2_COMPARATOR_RECEIPT_V1.json` (body sha256 `975ee9a9c283fceba48938b4c29d950d21396aa7064aa38f647418786852dab0`, `wall_ns` zeroed); design `KSO_M2_COMPARATOR_DESIGN_V1.json` (`bd25d4b45816`, module matches freeze: True); KSO column from `KSO_M2_SOLVE_RECEIPT_V1.json` at lane-ocm-3 head `066aaf9`, joined on `instance_id` + `graph_sha256` (equal on 50/50 rows). 50 development instances (`ME-X1-DEV-20260902`, per_family 5; ids_sha256 `b3bcb5e34484…`). NO NOVELTY OR BREAKTHROUGH CLAIM.

## Terminal

**`PARENT_SUFFICIENT = YES`** — the full KSO arm reproduces the strongest faithful parent exactly (0/0 discordant vs B5). That is the expected honest result and a success. **The mechanic's honest number is the navigation-only row:** 38/50, indistinguishable from the two oracle-independent retrieval parents at n = 50 (vs RWR p = 0.31, vs CBR p = 0.52). `GENERAL_NOVELTY: NOT_ESTABLISHED`.

## Table

| arm | role | exact | obstruction | cannot_check |
|---|---|---|---|---|
| `B5_STRONGEST_FAITHFUL_PARENT_FEDERATION` | ceiling control | 50/50 | 0 | 0 |
| `KSO_M2_SOLVE` | the machine under test (full arm; COMPOSE may read the store) | 50/50 | 0 | 0 |
| `KSO_NAVIGATION_ONLY` | the machine under test, navigation only (may NOT read the store): the mechanic's honest number | 38/50 | 12 | 0 |
| `RWR_PPR_SPREADING_ACTIVATION` | oracle-independent comparator | 32/50 | 0 | 0 |
| `CBR_KG_RETRIEVAL` | oracle-independent comparator | 34/50 | 0 | 0 |
| `C_RANDOM_ACTION` | null control | 5/50 | 0 | 0 |
| `ORACLE_POSITIVE_CONTROL` | positive control | 50/50 | 0 | 0 |

Random-control null band over 200 re-seeded arms: [0, 9] (mean 4.91). `KSO_M2_SOLVE`: 12 store-read rows (`exact_by = FOUND_BY_STORE_READ`), 38 by navigation. `KSO_NAVIGATION_ONLY` = `navigation_only_answer` (null ⇒ OBSTRUCTION, never exact).

| x | y | x only | y only | exact p (two-sided) | red |
|---|---|---|---|---|---|
| `KSO_M2_SOLVE` | `B5_STRONGEST_FAITHFUL_PARENT_FEDERATION` | 0 | 0 | 1 | no |
| `KSO_NAVIGATION_ONLY` | `B5_STRONGEST_FAITHFUL_PARENT_FEDERATION` | 0 | 12 | 0.000488 | RED |
| `KSO_NAVIGATION_ONLY` | `RWR_PPR_SPREADING_ACTIVATION` | 15 | 9 | 0.307 | no |
| `KSO_NAVIGATION_ONLY` | `CBR_KG_RETRIEVAL` | 13 | 9 | 0.523 | no |
| `RWR_PPR_SPREADING_ACTIVATION` | `B5_STRONGEST_FAITHFUL_PARENT_FEDERATION` | 0 | 18 | 7.63e-06 | RED |
| `CBR_KG_RETRIEVAL` | `B5_STRONGEST_FAITHFUL_PARENT_FEDERATION` | 0 | 16 | 3.05e-05 | RED |
| `C_RANDOM_ACTION` | `B5_STRONGEST_FAITHFUL_PARENT_FEDERATION` | 0 | 45 | 5.68e-14 | RED |
| `ORACLE_POSITIVE_CONTROL` | `B5_STRONGEST_FAITHFUL_PARENT_FEDERATION` | 0 | 0 | 1 | no |

The store-reading arm is never paired against a navigation-only parent: information is matched within each pair.

## Which arms may read the store

Rule (lane-ocm-3, KS-T04b): label-gated **firing** over graph structure — a dead request atom read through a compose hyperedge's tail gate — is a mechanic available to every arm that sees the graph; a dead atom is never in G_Q by construction (activation exactly 0). What `store_read` flags is reading a **live** atom that neither the walk nor firing surfaced.

| arm | may read the store | how |
|---|---|---|
| `B5_STRONGEST_FAITHFUL_PARENT_FEDERATION` | yes | its parent modules read the whole world (ceiling control) |
| `KSO_M2_SOLVE` | yes, flagged per row | COMPOSE consulted a live request atom the walk did not surface on 12/50 (`store_read: true`) |
| `KSO_NAVIGATION_ONLY` | **no** | answer = what EXTRACT returned from the navigated subgraph |
| `RWR_PPR_SPREADING_ACTIVATION` | **no** | reachable activation only |
| `CBR_KG_RETRIEVAL` | **no** | 2-hop retrieved neighbourhood only |
| `C_RANDOM_ACTION` / `ORACLE_POSITIVE_CONTROL` | n/a | controls |

## Budget (row A14)

Caps 2·|atoms| steps, 2·|hyperedges| edge visits, 1 restart, shared with the KSO. Max usage: RWR steps 0.52 of cap, edge visits 0.50; CBR steps 0.19; 0 overruns. `--cap-scale 0` plants 100 overruns → exit 2. B5, random and oracle are recorded, not capped.

## Checkers (all green in the receipt)

K1 random at the null (oracle-peeking plant outside the band) · K2 positive control exactly 1.0 (perturbed plant breaks it) · K3 no overrun · K4 paired red on 12 planted flips (p = 0.00049), quiet on a copy (p = 1) · K5 one graph / seed set / status map per instance · K6 byte-reproducible (timing zeroed) · K7 joined exact flags recomputed (0 disagreements).

## Not run / not claimed

Protected split (custody seed; same as M1). Nothing beyond the development split. Supersedes the receipt scored at `3abbb22` (KSO column without the navigation-only split), per the design's supersession note (4).
