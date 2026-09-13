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
`NN_NONNN_PACKET_DECIDED_AT_MICROSCOPE_SCOPE__E3_REPORTED_NOT_BOUND` (all three tasks yield a DC-2 verdict other than UNDECIDED, with the reachability field reported rather than bound — see the E3 qualification).

## Scope, stated once

This decides the family question **for this packet's candidate universe on this instrument** (16 inputs,
8-bit fixed point, hand-built candidates plus neutral-search reachability evidence). It is not a claim
about modern neural systems, real hardware, or any ecology outside the registered families; per DC-3 no
named architecture is derived. Its value is that the readiness audit's `UNDECIDED` becomes a decided
verdict at a real, protected, task-bound scope with every load-bearing field discharged.

---

# RV-377-210 — ADJUDICATION (receipt `STAGE_NN_NONNN_PACKET_RV_377_210_old.json`, billy-old)

13 candidates × 3 tasks × 6 V2 interventions, charged lifecycle meter, rules 36 + 40, Pareto over
`(1 − min capability, desc, exec, upd, ver)`; family labels read after measurement; shuffled-label control
unchanged on every task.

| task | best constant | admissible (rule 36 V2 + rule 40) | Pareto set | DC-2 verdict | prediction |
|---|---|---|---|---|---|
| `E_cr4` | 0.8125 | `program_search`, `compiled_search` (min 0.9167, +2.5 fx) | both | **`DERIVED_NON_NEURAL`** | verdict HELD; survivor-set clause RED: the memory rows are **not** admissible under V2 (`hamming_knn` min 0.8021 under `extra_unseen_feedback_v2`) — the DG-13 closure removed exactly the bar they relied on (RV-377-150: 3/36 store cells lost admissibility) |
| `E_sym5` | 0.7917 | `program_search`, `compiled_search` (0.9375, +3.5 fx) | both | **`DERIVED_NON_NEURAL`** | HELD (best neural row (3,2) min 0.8333 < θ) |
| `E_wit1` | 0.7083 | `program_search`, `compiled_search` (1.0, +7.0 fx) **and `gradient_net_h3_lr1` (NEURAL, min 0.8542, +3.5 fx)** | all three | **`FAMILY_COEXISTENCE`** | **RED** — `INFEASIBLE` was predicted; instead the exact-search rows are admissible and one expansion neural row is intervention-robust under V2 |
| E11 | — | one of four expansion rows admissible (on `E_wit1`) | — | — | **RED** as written |

Terminal: **`NN_NONNN_PACKET_DECIDED_AT_MICROSCOPE_SCOPE__E3_REPORTED_NOT_BOUND`** — every task yields a
DC-2 verdict at this packet's scope.

**R3 is not discharged, and the readiness audit stays open on it.**
`NN_NONNN_EMPIRICAL_EVIDENCE_READINESS_AUDIT_V1.md` §6 requires "real candidate-specific reachability
distributions/certificates under a common development budget", and states that evidence from different
scopes may not be stitched together after the fact. This packet's E3 supplies **class-level** reachability
from the class-rate lane's searches (a different scope, different candidates), reported as a sidebar
beside the verdict, not bound into the packet. Per the certificate's own C9 (receipts, ledger and prose
must agree) the audit's R3 therefore remains `SYNTHETIC_ONLY` and the repository-wide family terminal
stays `UNDECIDED_FROM_CURRENT_EVIDENCE`; what this packet decides is the family question **for its own
candidate universe on this instrument**, with R0, R1, R2, R4–R8, R10 discharged and R3 reported.
RV-377-211 (a packet whose candidates are the searched elites themselves, so reachability is bound rather
than reported) is the named successor.

## Reading

1. **Non-neural is derived where the obligation is exactly identifiable and the resource meter is
   charged.** On `E_cr4` and `E_sym5` only the exact-search rows survive hard feasibility; the Pareto step
   never has to decide between families. This is the measured counterpart of E2E-2 (exact controller →
   non-neural) and matches the MS-2 reading of the frontier receipts (`GMI_MEASURED_PROFILE_FAMILY_SELECTION_V1.md`,
   PROGRAM_SEARCH derived in 55 scopes).
2. **A neural candidate is intervention-robust on the witness-bearing ecology.** `gradient_net(h=3, lr=1)`
   clears every V2 bar on `E_wit1` (min 0.8542, 3.5 fx over the constant) — the first hand-built coefficient
   row in the corpus admissible under a leak-free full family. It sits on the Pareto set with the two exact
   rows because its update work (6 835) is 500× smaller than theirs (≈ 3.4 M) while its capability is lower:
   the resource vector, not the semantics, keeps both families on the frontier. That is E2E-4's coexistence
   outcome, measured.
3. **Two predictions were wrong and are filed RED, not retuned.** The freeze predicted memory rows
   admissible on `E_cr4` (they are not under V2) and `E_wit1` infeasible (it is not). Root cause, one stage
   each: (i) the memory prediction reused the V1-family closed form after this session had itself closed
   the leak that form depended on; (ii) the `E_wit1` prediction transferred RV-377-113's *searched-elite*
   rule-36 failures to the *hand-built* expansion rows, which the freeze had explicitly added to represent
   the neural family at its best. Neither error touches the verdict machinery; both are recorded in the
   ledger and the demotion rule (R9) applies: no re-prediction on this packet.
4. **What is not claimed.** No named architecture (DC-3); nothing about modern hardware or SGD-trained
   networks (E3's reachability sidebar: neutral search recovers the coefficient class 0/12 on `E_sym5`,
   so the admissible neural row on `E_wit1` is reachable by construction, not by the registered search);
   the candidate universe is this packet's (E11 shows the verdict is universe-relative: adding the
   expansion rows changed `E_wit1` from `DERIVED_NON_NEURAL` to `FAMILY_COEXISTENCE`).

## Receipt / record terminal (C9)

The runner wrote `"terminal": "NN_NONNN_PACKET_DECIDED_AT_MICROSCOPE_SCOPE"` into
`STAGE_NN_NONNN_PACKET_RV_377_210_old.json` before this qualification was written. The receipt is run
evidence and is not edited; **this record's terminal —
`NN_NONNN_PACKET_DECIDED_AT_MICROSCOPE_SCOPE__E3_REPORTED_NOT_BOUND` — is the authoritative one**, and the
difference is exactly the E3 qualification above.
