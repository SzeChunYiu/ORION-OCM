# KSO M2 solve loop on ME-X1 — outcome record V1

Design (frozen pre-run, unchanged): `../theory/KSO_M2_SOLVE_DESIGN_V1.md`, sha256 `78931b75…`,
seed commitment `KSO_M2_SOLVE_DESIGN_V1.json` (50 dev instance ids, `b3bcb5e3…`).
Receipt: `KSO_M2_SOLVE_RECEIPT_V1.json` (one command, exit 0; byte-reproducible in-process).
Comparator arms and paired table: guards lane, `KSO_M2_COMPARATOR_RECEIPT_V1.json`, joined on
`instance_id` and the shared `graph_sha256`. **NO NOVELTY OR BREAKTHROUGH CLAIM.**

## Headline (the mechanic's own number first)

```text
NAVIGATION_EXACT   38/50   the walk surfaced every live request atom COMPOSE used (FOUND_BY_NAVIGATION)
STORE_EXACT        50/50   the store's exactness: on the other 12 COMPOSE read ≥ 1 live request atom the
                           walk did not surface (FOUND_BY_STORE_READ) — attributed to EXTRACT (finding 1)
mechanic terminal  M2_NAVIGATION_EXACT_38_OF_50__EXTRACT_ATTRIBUTED
```

The 50/50 is not a navigation result; it is the labels and the registered rule doing what they
do. The 38/50 is what the mechanic did on its own. M2.1 (the revival) targets the 12 — lever =
the surprise baseline (uniform background is wrong at small seed cardinality; compare against
the background walk at matched seed cardinality, or degree-normalised reactivity), re-tested on
the same 50 against the strongest parent, all costs charged, no tuning to the outcome.

Per-row fields for the comparator join: `store_read` (COMPOSE used ≥ 1 live request atom outside
`G_Q`), `navigation_only_answer` (= `answer` when `store_read` is false, else `null`, scored as
`KSO_NAVIGATION_ONLY` by the guards lane), `dead_request_atoms_read_through_fire`. One precision
the split needs: a **dead** request atom is never in `G_Q` by construction (KS-T04b: its
activation is exactly 0), so the decisive dead atom of a non-UPDATE answer is always read through
the compose hyperedge's tail gate — that is the FIRE stage (label-gated enabling, a mechanic), not
a read beyond the subgraph. `store_read` therefore counts only *live* request atoms the walk
failed to surface, which is exactly the EXTRACT finding.

## Comparator join (guards lane, `KSO_M2_COMPARATOR_RECEIPT_V1.json`, #298, scored on the 066aaf9 receipt; joined on `instance_id` + `graph_sha256`, 50/50 rows)

```text
B5_STRONGEST_FAITHFUL_PARENT_FEDERATION  50/50   ceiling control (oracle by construction)
KSO_M2_SOLVE (full)                      50/50   paired vs B5: 0/0 discordant, p = 1   -> PARENT_SUFFICIENT
KSO_NAVIGATION_ONLY                      38/50   12 OBSTRUCTION (store_read rows scored not-exact)
RWR_PPR_SPREADING_ACTIVATION             32/50   NAV vs RWR 15/9 discordant, p = 0.31
CBR_KG_RETRIEVAL                         34/50   NAV vs CBR 13/9 discordant, p = 0.52
C_RANDOM_ACTION (null)                    5/50   null band 0–9 over 200 re-seeds
ORACLE_POSITIVE_CONTROL                  50/50
NAV vs B5                                        0/12 discordant, p = 4.9e-4
```

Reading, as the guards lane stated it: the full arm reproduces the ceiling (`PARENT_SUFFICIENT`;
`GENERAL_NOVELTY NOT_ESTABLISHED`); the navigation-only mechanic is indistinguishable from the two
oracle-independent retrieval parents at n = 50 and loses to the ceiling on exactly the 12
store-read instances. Per-arm permissions (label-gated firing over graph structure allowed for
every graph arm; `store_read` = a live atom neither the walk nor firing surfaced) are in
`KSO_M2_COMPARATOR_OUTCOME_V1.md`.

## Terminal (as defined in the frozen design: G1 ∧ G2)

```text
M2_EXACT_ON_DEV
  G0 known-answer fixtures      14/14 exact
  G1 exact agreement vs oracle  50/50   (attributions: none; by navigation 38, by store read 12)
  G2 translator invariance      50/50   byte-identical canonical extraction from two atomizers whose sources differ
  G3 budget                     0 overruns; KSO used ≤ 0.5 of the steps cap and ≤ 0.3 of the edge-visit cap
  G5 planted label flip         5/10 flips changed the answer (must-differ fired); 5 flips on atoms that were not decisive did not — recorded
  comparator verdict            deferred to the joined table (B5 is the ceiling; RWR/PPR and CBR/KG are the oracle-independent comparators)
```

Pre-registered expectation (design §0) met: exact agreement is by construction — the request
statuses are registered world facts and the walk is the registered rule — so G1 carries no
scientific weight beyond "the mechanics reproduce the rule with exact warrant bookkeeping";
`PARENT_SUFFICIENT` against the B5 ceiling is the expected joined verdict.

## What the loop does, per instance (measured, 50 instances)

- graph = M1 `populate(w1, request=…)` + request-level atoms from the second reading of the
  request semantics (311 added over 50 instances; every reading agrees with
  `mex1_oracle.request_atoms` at the CHECK stage — 50/50 and 10/10 in the unit test);
- ATOMIZE: two atomizers, 3-atom seed set (goal, target claim, result when populated);
- NAVIGATE: exact restart fixed point on the DAG; `FOUND` on 45, `GAP_NOT_FOUND:WARRANT` on 5
  (the target claim is non-live at request time — the four-valued rule; the decision is still
  composed from labels);
- FIRE: label-gated enabling equals the label-only prediction on every instance;
- EXTRACT: reacting subgraph `G_Q` (see the finding below);
- COMPOSE: precedence walk restated on labels, censoring rule = the oracle's singleton rule;
- CHECK: request atoms and claim labels vs the oracle's statuses and support, 0 mismatches;
- RENDER: `Decision.as_dict()`.

## Findings the design did not predict (informational; no attribution, the answers are exact)

1. **`EXTRACT_SURPRISE_MISSES_ONE_HOP_REQUEST_ATOMS` — 12/50 instances.** A 3-seed question gives
   a one-hop child of the goal atom (fan-out ≈ 13) activation `a_Q = a(req)(1−α)/k ≈ 0.0057`, below
   the uniform background `π ≈ 0.0061` on a 57-atom graph, so its reaction surprise is 0 and it
   falls outside `G_Q` although it is live and one hop from the seed. COMPOSE reads the compose
   hyperedge's tails from the store, not from `G_Q`, which is why the answer stays exact. This is
   a structural weakness of the surprise measure under fan-out on small graphs — a lead for M2.1
   (seed-count-conditioned background, or fan-out-aware surprise), **not** tuned here (the design
   is frozen; a revised extraction is V2 with a supersession receipt and its own gate).
2. **`TARGET_CLAIM_DEAD_AT_REQUEST_TIME` — 5/50.** Reported as `GAP_NOT_FOUND:WARRANT` by the
   four-valued rule; correct by definition, recorded so the outcome distribution is visible.

## Ledger audit (post-run)

`VACUOUS_CONTRAST`: the two atomizers are asserted to differ in source (hash); B5 is labelled a
ceiling. `STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE`: G1's 50/50 declared as by-construction in
the frozen design. `CHECK_THAT_RUNS_AND_CANNOT_FIRE`: G5 fired on 5/10 planted flips; the EXTRACT
stage check fired on 12 instances (informational) — it can fire. `HANDICAPPED_COMPARATOR`: budgets
matched; KSO usage reported. `AUTHORITY_LAUNDERING`: development split only; protected `NOT_RUN`.

## Next

M2.1 extraction revival (surprise under fan-out) with a V2 design; M2b elementary-algebra domain
through the instruction channel with SymPy as the EXACT_CHECKER channel (operator directive on
#284); comparator join once `KSO_M2_COMPARATOR_RECEIPT_V1.json` lands.
