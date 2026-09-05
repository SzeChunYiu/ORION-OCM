# KSO M2 — the solve loop on ME-X1, frozen design V1

Status: **DESIGN FREEZE, pre-run. NO NOVELTY OR BREAKTHROUGH CLAIM.** Prototype #284 §3/§6 (M2);
umbrella #194; master #197. Contract `KSO_SUBSTRATE_CONTRACT_V1.md` (Part I/II); architecture
`KSO_ARCHITECTURE_V1.md` (C2 solver); population `../reference/kso_m1_mex1_population_v1.py`
(M1 receipt `../results/KSO_M1_POPULATION_RECEIPT_V1.json`). Comparator arm and budget harness:
guards lane (`kso_m2_comparator_v1.py`, one receipt schema, agreed interface below).
Frozen digests and the seed commitment: `../results/KSO_M2_SOLVE_DESIGN_V1.json`.

## 0. Pre-registered expectation (written before any run)

The ME-X1 transition decision is a function of registered world facts (support families, result
bindings, criterion equivalence, spec fidelity, transport relations, evaluator coverage, authority
policy) under a registered precedence rule. A knowledge space that holds those facts as warranted
atoms and the rule as a procedure atom reproduces the decision by navigation + label check +
composition. **Expected result: exact agreement with `mex1_oracle` on 50/50 development
instances, and `PARENT_SUFFICIENT` against the strongest faithful federation (B5), which is the
oracle by construction on this generator (a ceiling control).** A disagreement is a defect of the
population or of the second implementation of the request semantics and is attributed to exactly
one stage. Nothing in M2 can establish an advantage; M2 establishes that the *mechanics work on a
real domain with exact warrant bookkeeping*, that extraction is translator-invariant, and what the
oracle-independent parents (RWR/PPR, CBR/KG) achieve under a matched budget.

## 1. Instances and information matching

- Instance set: `mex1_generator.generate_split("dev", "ME-X1-DEV-20260902", {f: 5 for f in FAMILIES})`
  — the 50 M1 worlds, ids `dev-<FAMILY>-NNN`. Protected split: **NOT RUN** (custody seed).
- World at request time: `w1 = mex1_oracle.final_world(inst.world_v0, inst.events)`.
- Graph every arm sees: `populate(w1, request=inst.request, request_id=inst.instance_id)` **plus
  the request-level atoms of §2** (added by the M2 module, one function, before any arm runs).
- Seed set `S = {req:<id>, claim:<target>} ∪ {res:<result_id> if populated}`, uniform,
  warrant-gated without renormalisation. Same graph, same seed vector, same budget to every arm.
- Budget (matched, from the guards lane): `steps = 2·|atoms|`, `edge_visits = 2·|hyperedges|`,
  `restarts = 1`, wall proxy = ops count; overrun ⇒ `CANNOT_CHECK` (exit 2). The KSO reports its
  actual `steps`/`edge_visits` per instance (its exact fixed point on a DAG uses ≤ |atoms| steps).

## 2. Request-level atoms — a second implementation of the registered request semantics

The oracle reads request-level statuses from the world (`mex1_oracle.request_atoms`). The M2
module **re-implements that reading from the `World` fields** (`kso_m2_request_atoms`), never calling
the oracle's function; agreement between the two readings is itself checked per instance
(stage CHECK). Each request-level status becomes one atom of type `constraint`, id as the oracle
names it (`identity:<r>`, `criterion:<c>`, `spec:<r>`, `checker:<r>`, `src:<e>` / `ident:<e>` /
`cal:<e>` (shared with M1's base atoms when present), `comparability:<r>`, `support:<r>`,
`transport:<r>`, `evaluator:<r>`, `piece:<c>`, `overlap:<o>`, `witness:<c>`, `authority`), with
label `{{i}}` over a fresh evidence index unless it is an M1 base atom; status VALID ⇒ live,
INVALID ⇒ `i ∈ R`, UNKNOWN ⇒ `i ∈ U` (censored). `piece:<c>` atoms are derived: their label is the
claim's label (`⊗`), not a fresh index. Every request atom is connected: DEPENDENCE edge
`req:<id> → atom`; the `piece` atoms additionally by SUPPORT from `claim:<c>`.

The **precedence rule** is a registered protocol constant (`MODULE_RANK`, and the action each atom
kind carries on failure — `ME_X1_TRANSITION_COUPLING_PROTOCOL_V1.md`), admitted as one procedure
atom `proc:transition_rule` (INSTRUCTION channel, label ONE) with a COMPOSITION hyperedge from
the request atoms (in precedence order, as `head_weights` carry the rank) to a decision atom
`decision:<id>`. The rule's *content* is data the world registers; the *walk* is the KSO's
compose + check.

## 3. The loop, stage by stage, with the stage check that attributes a disagreement

| stage | operator | stage check (first failing stage is the attribution) |
|---|---|---|
| ATOMIZE | `atomize_A(inst)` → parts → seed vector `s_Q` | `S` equals the declared seed set; `atomize_B` (§5) gives the same vector |
| NAVIGATE | `navigate(𝒦, s_Q, claim:<target>, B)` → outcome | outcome `FOUND` for the target claim; `GAP`/`OBSTRUCTION` are answers, scored not-exact, never dropped |
| FIRE | enabled hyperedges under label gating with `θ = 0` on activation and `ℓ_R` on labels | the enabled set equals `{h : all tails live}` computed from labels alone (KS-T02) |
| EXTRACT | reacting subgraph `G_Q` (KS-T11a) | every request atom of the instance is in `G_Q` (each is one hop from `req:<id>`) |
| COMPOSE | walk the request atoms in precedence order: `action` = the on-failure action of the first atom that is **not live under `R`**; `UPDATE` if all live; **censoring rule**: if a censored atom (`i ∈ U`) precedes the first non-live atom and its on-failure action differs from the terminal action, `DEFER_CANNOT_CHECK` (the label is not certified complete, §3 of the contract) — this is the singleton rule of `mex1_oracle.walk` restated on labels; `PROPAGATE_DEFEAT`: `reopened` = accepted claims whose `claim:<c>` is non-live; any censored accepted claim ⇒ `DEFER_CANNOT_CHECK` | the composed `(action, reopened)` equals the oracle's `Expected.decision()` **given** the statuses; a mismatch here with statuses agreeing is a COMPOSE defect |
| CHECK | for every request atom and claim: `ℓ_R(label)` vs the oracle's status / support (P2 extended to request atoms) | 0 mismatches; a mismatch is a CHECK defect (population or second reading) |
| RENDER | `Decision(action, reopened).as_dict()` | dict shape; sorted `reopened` |

Attribution rule: for a non-exact instance the attribution is the **first** stage in table order
whose stage check fails; if none fails and the answer is still wrong, `ATTRIBUTION_FAILED` is a
result (and a ledger entry), never softened.

## 4. Gates

| gate | statement | pass |
|---|---|---|
| G0 self-test | `mex1_generator.known_answer_fixtures()` (hand-authored) solved exactly by the loop | all fixtures exact; any miss blocks the run |
| G1 exact agreement | per instance `answer == Expected.decision()` | reported as `n_exact/50`; **expected 50/50**; every miss attributed to one stage |
| G2 translator invariance | two independent atomizers (§5) ⇒ identical seed vector and **byte-identical** canonical `G_Q` | 50/50; a single difference is a KS-T10a violation → reopen M0 |
| G3 budget | every arm under the same caps; KSO actual usage reported | no overrun; else `CANNOT_CHECK` |
| G4 comparator table | paired exact McNemar (`mex1_run.paired_summary`) KSO vs each arm | B5 = ceiling control; oracle-independent comparators = RWR/PPR, CBR/KG; null `C_RANDOM_ACTION`; positive control `ORACLE_POSITIVE_CONTROL` 1.0 |
| G5 no-alarm / must-differ | a planted label flip (one request atom's status inverted) changes the answer on ≥ 1 instance; the null arm is not exact on ≥ 1 instance | both fire |

Terminals: `M2_EXACT_ON_DEV` (G1 50/50 ∧ G2 50/50) · `M2_DEFECT_ATTRIBUTED__<STAGE>` (G1 < 50 with
every miss attributed) · `M2_ATTRIBUTION_FAILED` · `CANNOT_CHECK`. Comparator verdict (with the
guards lane): `PARENT_SUFFICIENT` (KSO ties the ceiling; no significant edge over the
oracle-independent arms is claimed — and cannot be, the ceiling is the oracle) · `KSO_LOSES_TO_CEILING`
· `CANNOT_CHECK`.

## 5. Two atomizers (translator-invariance gate)

- `atomize_A`: from the `TransitionRequest` object — parts `[(kind, "goal", (req,)), (target, "claim", (claim:<t>,)), (result, "proof|observation", (res:<r>,))?]`.
- `atomize_B`: from the world's registered result binding and the instance id — reads
  `w1.results[r].bound_claim_id` when a result exists, else the request's target, and emits the
  parts in the opposite order with different texts. Both must yield the same seed vector; the
  canonical extraction (`sorted atom ids`, `sorted hyperedge ids`, JSON, sorted keys) must be
  byte-identical. Texts differ, order differs, code paths differ (`VACUOUS_CONTRAST` guard: the two
  functions are asserted not to share a code path by a source-hash check).

## 6. Seed commitment and freeze

Committed before the run in `../results/KSO_M2_SOLVE_DESIGN_V1.json`: sha256 of this file; the
50 instance ids (from the public dev seed) and their sha256; the M1 receipt body sha256 the graph
is built on; the M0 freeze digest; the budget caps; the gate table. The run is one command,
`python research/orion-machine/reference/kso_m2_solve_v1.py --out research/orion-machine/results/KSO_M2_SOLVE_RECEIPT_V1.json`,
exit 0/1/2; it refuses to run if the design digest in the JSON does not match this file
(`DESIGN_DRIFT` ⇒ exit 2). No post-outcome change to this file; a revision is V2 with a
supersession receipt.

## 7. Ledger audit (pre-run)

All 28 + 7 classes read against this design. Named risks: `VACUOUS_CONTRAST` (two atomizers —
guarded by the source-hash check; KSO vs B5 — B5 is declared a ceiling, not a comparator);
`STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE` (G1's 50/50 is expected by construction — declared as
such in §0; the informative rows are G2, the attribution of any miss, and G4's oracle-independent
arms); `HANDICAPPED_COMPARATOR` (budgets matched; parents run faithfully by the guards lane);
`CHECK_THAT_RUNS_AND_CANNOT_FIRE` (G5 must-differ plants); `AUTHORITY_LAUNDERING` (development
split only; no protected claim).
