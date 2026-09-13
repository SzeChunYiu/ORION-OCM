# RV-377-210 — FREEZE: a task-bound NN / non-NN family packet on the validated microscope

`research/gmi-grand-unification-v1/NN_NONNN_EMPIRICAL_EVIDENCE_READINESS_AUDIT_V1.md` returns
`UNDECIDED_FROM_CURRENT_EVIDENCE` because no immutable packet binds one protected task, a neural and a
non-neural candidate under one accounting boundary, real development, real resources and protected
deployment (R0, R2, R3, R4, R5, R9). This record freezes that packet on the instruments this programme
has already validated, following `NN_NONNN_EMPIRICAL_INSTANTIATION_PROTOCOL_V1.md` E0–E13 in order.
Everything below is written before the protected measurement; the runner is
`gmi_microscope/nn_nonnn_packet.py`.

## E0 — problem registration

Three registered ecologies, each rule-40 discriminating (RV-377-108/101) with non-degenerate obligations
(RV-377-112) and the leak-free intervention family V2 (RV-377-150):

| task | coefficients / family | why it is in the packet |
|---|---|---|
| `E_cr4` | (−½, −½, −½, ⅜) smooth | memory-predicted-present, witness-free (RV-377-140 §8) |
| `E_sym5` | (5/16)×4 smooth | the corpus's most-searched discriminating ecology; 12-seed class record |
| `E_wit1` | (−½, −½, −½, −¼) smooth | witness-bearing (constructed to host a coefficient witness, RV-377-102) |

Obligation: the registered 16-input smooth target; development = the registered protocol (16 feedback
events, two passes over the 8 `TRAIN` inputs, revocation at event 9); protected deployment = the 8
`UNSEEN` inputs, `cap = 1 − err/1.5`, θ = 0.85; interventions = `INTERVENTION_FAMILY_V2`; null =
best constant on `UNSEEN` (rule 40, ≥ 1 fx margin). Semantic metric: the exact served trace (RV-377-116).

## E1 — family predicates (operational, decided on the artifact)

`NEURAL`: the served answer's dominant carrier on the raw genotype is `DENSE` (`b1.carrier_of`) and the
genotype contains a `GRAD` update kind — i.e. numeric coefficient state trained by a gradient-style
error-driven update. `NON_NEURAL`: served carrier ∈ {`TABLE`, `KVSTORE`, `PROGRAM`, `NONE`} and no `GRAD`
kind. `HYBRID`: served path reads `DENSE` **and** a store/program carrier. Decided by
`nn_nonnn_packet.family_of` before any capability is read.

## E2 — candidate universe (immutable; canonical genotype hashes recorded in the receipt)

Registered zoo rows: `gradient_net_h2`, `gradient_net_h4` (NEURAL); `exemplar_table`, `hamming_knn_k3`,
`soft_retrieval`, `program_search`, `compiled_search`, `particles_p4`, `constant_emitter` (NON_NEURAL).
**E11 expansion of the neural family** (so the family is represented by its best-known instances, not
only the zoo defaults): `gradient_net(h, lr)` for (3,1), (3,2), (6,2), (8,2) — the hand-built coefficient
witnesses of RV-377-082/102/140. 13 candidates × 3 tasks.

## E3 — development / reachability

Every candidate is developed by the same registered protocol (16 events) with the same budget; that is
the common development law. Reachability under a neutral developmental *search* is supplied by the
committed class-rate record (RV-377-140/141): on `E_sym5` memory class recovered 9/12 seeds, program 1/12,
coefficient 0/12 at 20 000 charged evaluations; on `E_wit1` 1/3 (raw) → 0/3 (atrophied); `E_cr4`'s three
seeds are scored in `STAGE_CLASSRATE_FRESH_V43_CLASSRATE_billy.json` when it lands. Reachability is
reported per family alongside the verdict; it is not used to exclude hand-built candidates (E3 rule: a
candidate not reached by the registered search is flagged, and the verdict is reported both with and
without the reachability gate).

## E4 — resource vector and accounting boundary

The charged VM lifecycle vector of `ecology.run_genotype` (`lifecycle` / ledger `R`: description, execution,
update, revision, verification work, memory cells/stores) under the `standard` protocol, exact and
deterministic (zero-width intervals), one accounting boundary for every candidate. Pareto mode (E8 §11.1):
minimize `(1 − min-over-V2 capability, desc, exec, upd, ver)`; no scalarization.

## E5 — deployment evidence

Capability on `UNSEEN` under each of the six V2 interventions; admissibility = min over the six ≥ θ **and**
margin over the best constant ≥ 1 fx (rules 36 + 40). Hard feasibility (E7) before preference (E8).

## E9/E10 — frozen predictions (from the theory's closed forms and committed receipts, no new run)

| task | prediction | source |
|---|---|---|
| `E_cr4` | every NEURAL candidate inadmissible under V2 (best hand-built coefficient row min-over-six 0.849 < θ, RV-377-140 §8); memory rows admissible (closed form A_mem 0.9062 ≥ θ+1 fx); survivors all NON_NEURAL → **`DERIVED_NON_NEURAL`**; MS-2 property of the survivor set: store or exact-search carrier | RV-140 closed forms |
| `E_sym5` | no NEURAL candidate admissible under the family (RV-377-089b: no coefficient witness on `E_sym5` over 80 rows to h = 32; V2 only removes the leaky bar); memory and program rows admissible (RV-377-113 table) → **`DERIVED_NON_NEURAL`** | RV-089b, RV-113 |
| `E_wit1` | the coefficient witness holds under `standard` only (RV-377-103 C2 fails `shuffled_events`/`half_events`), so NEURAL inadmissible; memory/program rows: RV-377-113 found all three recovered carriers fail rule 36 on `E_wit1`, so the hand-built rows are predicted inadmissible too → **`INFEASIBLE_AT_REGISTERED_SCOPE`** (M* = ∅); if any non-neural row survives, `DERIVED_NON_NEURAL` | RV-103, RV-113 |
| E11 | none of the four expansion rows is admissible under V2 on any task | witness scans |

Falsifiers: a NEURAL candidate admissible under V2 on any task → that task's verdict is `FAMILY_COEXISTENCE`
or decided by the Pareto step, recorded as the outcome (the prediction was wrong, the packet stands);
`E_wit1` with a surviving memory row → `DERIVED_NON_NEURAL` (prediction of infeasibility wrong).
Demotion rule (R9): a wrong family prediction is filed as RED for the clause and is not re-predicted on
the same packet.

## E12 — family-neutral controls

`constant_emitter` (must be inadmissible everywhere: rule 40); the best constant per task; a family-blind
re-run in which candidate labels are shuffled must leave every admissibility number unchanged (labels are
read after measurement).

## E13 — packet

Receipt `microscopes/results/STAGE_NN_NONNN_PACKET_RV_377_210_{HOST}.json`: candidate registry with
hashes and families, per-task capability under each intervention, resource vectors, admissible set,
Pareto set, family support, DC-2 verdict, reachability sidebar, and the shuffled-label control.
Terminal names: `NN_NONNN_PACKET_VERDICT_<task>=<DC-2 verdict>` and the aggregate
`NN_NONNN_PACKET_DECIDED_AT_MICROSCOPE_SCOPE` (all three tasks yield a DC-2 verdict other than UNDECIDED).

## Scope, stated once

This decides the family question **for this packet's candidate universe on this instrument** (16 inputs,
8-bit fixed point, hand-built candidates plus neutral-search reachability evidence). It is not a claim
about modern neural systems, real hardware, or any ecology outside the registered families; per DC-3 no
named architecture is derived. Its value is that the readiness audit's `UNDECIDED` becomes a decided
verdict at a real, protected, task-bound scope with every load-bearing field discharged.
