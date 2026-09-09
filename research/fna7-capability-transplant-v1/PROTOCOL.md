# FNA-7 / D8 — CapabilityTransplantProtocolV1 (#208 capability-source transplant)

**Issue #214 work package FNA-7, deliverable FNA-D8, over issue #208. Base commit
`ab5310942b01be11776c0eddc4403dc0e0dcb51c`. Research-only: production `src/` untouched, no
agent deployed, no #165 box touched. Concurrency: no live #208 artifacts exist
(`CONCURRENCY_CHECK.json`, verdict `NO_CONCURRENT_WORK_COLLISION`).**

## What this protocol is and is not

#208 asks, at frontier-agent scale, whether adding OCM state/control improves a coding agent.
FNA-7 (#214 §4) inverts the lens on the SAME capability-source surface: the frontier model
currently *supplies* certain capabilities inside that agent; a transplant removes **one
capability at a time** from the model-supplier and gives it to an explicit non-neural
mechanism, holding the model, harness, tools, budgets and memory permissions fixed, then
asks whether capability is preserved, model dependence falls, or an obstruction appears.
This capsule delivers the executable protocol (V1) plus one micro-pilot proving the protocol
runs end-to-end. It does not run frontier models, does not touch #208's H1/H2 protected
tasks, and claims nothing at #208's scale.

## Generic transplant mechanics (all seven capabilities)

Each transplant is a frozen quadruple `T = (K, A_inc, A_rep, H)` plus meters and a gate:

1. **Capability contract K** (from #214 §2 `FunctionalMechanismContractV1`): exact I/O
   contract, state transformation, information surface (what the supplier may legally see),
   declared failure modes, and the *decisive consumption step* — the downstream harness
   action that actually consumes the capability's output. A capability with no decisive
   consumer is not transplantable; the protocol records that as an obstruction.
2. **Incumbent arm A_inc — model-supplied, never degraded.** At #208 scale this is the SAME
   foundation model + harness of the control arm, supplying capability K in-context. Every
   model call, token, tool call and preprocessing byte the incumbent spends on K is charged.
   The incumbent keeps every power the replacement would have (kill-gate: "ordinary parent
   denied an OCM-nonessential power" — inverted here: replacement never denied an
   incumbent-nonessential power).
3. **Replacement arm A_rep — non-neural, strongest-parent first refusal.** Parent ladder per
   #214 §4 FNA-5 order: exact analytic/guarded rule → conventional estimation/selection
   parent → kNN/linear → tree/rule learner → bandit; bindings to capsule results where they
   exist (#215 typed indexes + FNA-1 channel ordering; #218 minimum-sufficient donors;
   #219 guard-first routing + acquisition-price economics; #222 working-state parents, open
   PR #222 cited by branch). First *sufficient* arm owns the terminal; later arms run only as
   gap measurement; a neural reference may diagnose a representation gap and is never
   adoptable.
4. **Held-constant harness H.** The agent loop outside K is byte-identical across arms:
   routing, tools, budgets, repair policies, maintenance triggers. If the harness itself must
   react to K's output (e.g. a maintenance refresh), the reaction rule is part of H and is
   identical across arms — arms differ *only* in what their K-supplier says.

**Meters (every transplant):** capability score on protected evaluation; capability-
preservation margin vs A_inc (frozen ε); model dependence (model calls, tokens, tool calls
spent on K — must be exactly 0 in A_rep for the capability, verified structurally);
acquisition/index/maintenance price of A_rep (label prices charged per #219 economics);
inference work; fitted-state bytes; authored-source bytes (a hand-authored rule may not hide
its prior — #214 §6); whole-chain cost per task (all of the above amortized); shuffle-equal-n
null and no-supplier floor.

**Causal gate (#214 §5, all 10 clauses, executed by the protocol's gate runner):**
dononer-function frozen before outcomes (FREEZE); no hidden information (structural
no-latent-leak test on the legal information surface); consumed at the decisive step
(harness consumption trace + substitution test); non-inferior within frozen margin or exact
loss reported; complete resource vector; removal/substitution destroys the claimed effect;
strongest-parent first refusal; no neural computation attributed to the non-neural arm
(structural import/invocation test); revision/revocation semantics correct (stale advice is
detected and paid for, not hidden); protected evaluation disjoint from development.

**Terminals:** from #214 §7 and #208 §7, scoped per transplant, e.g.
`PARENT_SUFFICIENT_FOR_<capability>`, `NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE`,
`NON_NEURAL_RESOURCE_ADVANTAGE_AT_REGISTERED_SCOPE`, `NO_FUNCTIONAL_PARITY_<capability>`,
`NEURAL_DONOR_DOMINATES_AT_SCOPE`, `ACQUISITION_COST_DOMINATES` (side-flag),
`REPRESENTATION_INSUFFICIENT`, `CANNOT_CHECK_<reason>`.

## The seven transplant specs (capability list frozen from #214 §4 FNA-7 / #208 §9)

Machine-readable form with full bindings: `CAPABILITY_TRANSPLANT_PROTOCOL_V1.json`.

| # | capability K | decisive consumer | incumbent supplies | strongest non-neural parents (first refusal) | status |
|---|---|---|---|---|---|
| 1 | repository semantic retrieval | artifact set fed to the edit step | model reads/greps files, picks artifacts | #215 FNA-1 typed indexes + exact scan (`kso/extraction_indexed.py`, channel ordering); inverted indexes; then ANN/kNN | PROTOCOL_ONLY |
| 2 | failure classification | post-failure repair-action selection + maintenance triggering | model reads the failed trace, assigns responsibility | guarded rule from declared laws (zero acquisition) → calibrated estimator (labels charged, #219 economics) → rule learner | **PILOTED here** |
| 3 | planning / obligation control | next-obligation choice + budget allocation | model holds plan in-context | #219 guard-first routing (analytic-guarded first refusal); #222 blackboard/Soar working-state parents (open PR #222) | PROTOCOL_ONLY |
| 4 | API/interface induction | call-shape proposal consumed by the next edit | model recalls/infers interfaces from pretraining | grammar/adaptor-grammar induction (#214 §3 in-context row), #215 `FunctionalMechanismContractV1` contract fitting | PROTOCOL_ONLY |
| 5 | repair-method reuse | method record selected and applied to a fresh failure | model improvises the repair from context | case-based reuse over scoped failure memory (g3 capsule convention), #219 cost-model selection, #214 FNA-4 library parents | PROTOCOL_ONLY |
| 6 | code transformation / synthesis | patch candidate applied to the workspace | model writes the patch | #214 FNA-4: anti-unification, rewrite/e-graph, CEGIS/verifier-guided synthesis, Soar chunking | PROTOCOL_ONLY |
| 7 | verification interpretation | accept/reject/continue decision after checker output | model reads test output, decides meaning | exact O(1) certificates + counterexample-to-clause mapping (#215 FNA-1 checker convention; repo mechanical-proof capsules) | PROTOCOL_ONLY |

Per-capability frozen fields (in the JSON): contract I/O/state, information surface, arm
definitions, held-constant harness, margins, dependence metrics, cost model, terminal
vocabulary, and the `capability_source_map_binding` (the six #208 §9 fields:
supplier/necessity/cost/failure-mode/replacement/evidence-status) that #208's future
`capability_source_map.json` must fill per capability before any H1-scale transplant runs.

## Pilot (executed here): capability 2 — failure classification, micro scale

**World (strongest existing exact world on main; reused read-only, not authored fresh):**
the FNA-5 routing world `research/fna5-routing-first-refusal-v1/fna5_world.py` (PR #219,
merged) — 2400 seeded queries, real `SolveOperatorIndex` applicability surface, five method
families with declared centres and seeded realized laws, per-query latent noise `u(q)`,
exact O(1) checker, frozen DEV/EVAL/DRIFT md5 splits, frozen drift mutation. Failures of
approximate families have *exact* responsibility ground truth computable from the latents —
no favorable benchmark was authored for this pilot; it is #219's world with a transplant
harness on top.

**Host loop H (held constant):** per query — extract features (charged) → route with the
#219 A2 cost-model router (AMENDMENT 1: fitted on DEV identification records, identification
and fit charged identically to every arm as harness cost; the analytic-guarded A1 was
superseded pre-outcome because its 0.0043 fallback stream is too sparse to exercise the
capability) → execute + verify
(charged) → on FAIL, invoke the capability under transplant: classify the failure's
responsibility into frozen classes → the frozen REPAIR TABLE consumes the classification:
`SELECTOR_METHOD_MISMATCH` → retry cheapest different-family approximation, then scan on
second failure; `NOISE_BOUNDARY_UNAVOIDABLE` → scan immediately (skip doomed retries);
`STALE_DECLARED_MODEL` → scan immediately + stale flag. Stale flags ≥ 8 in the drift window
trigger H's maintenance refresh: the frozen identification price is billed to that arm and
the router is re-fitted once on the maintenance-window records (identical rule for every arm;
arms differ only in when their classifications trigger it). Held-constant enforcement
(AMENDMENT 2): every arm runs its own freshly built seed-identical world (drift is applied
in-stream), verified by a single shared EVAL failure-stream digest across arms. With no
supplier, H's default is the
portfolio-recovery convention (scan immediately) — the floor, never a result.

**Responsibility ground truth (frozen order, from latents, labels/eval only):** (a)
`STALE_DECLARED_MODEL` iff drift regime AND declared point-prediction said PASS AND realized
outcome FAILS with binding-clause gap > 0.04; else (b) `SELECTOR_METHOD_MISMATCH` iff some
applicable different-family approximation would PASS at declared cost below scan; else (c)
`NOISE_BOUNDARY_UNAVOIDABLE`. Class (a)/(c) share the per-query repair (scan) and differ
exactly in maintenance timing — declared before outcomes, so the pilot measures whether
classification quality moves whole-chain cost through both the repair choice and the
refresh trigger.

**Legal information surface (clause 2):** the 12 world features plus trace facts of the
failed attempt (family, param, clause slacks under *declared* centres with neutral noise,
declared cost estimates, applicability counts, cheapest different-family declared cost,
catalogue-version flag). Never `u(q)`, never realized thetas, never other instances'
realized outcomes. A pinned test asserts the legal view carries no latent.

**Arms.** Replacement ladder: R1 `GUARDED_DECLARED` (Bayes-rule on declared centres, γ-guard
0.15 on noise bands, zero label acquisition; structurally cannot assert STALE — honest
limitation of the zero-acquisition parent, recorded); R2 `CALIBRATED_BAYES` (realized
constants re-estimated from DEV failure labels, moment intervals; acquisition charged at
the in-world identification price — executing all applicable per labeled failure); R3
`CART_TREE` (depth ≤ 3, gini, dev-trained, acquisition charged). Incumbent class:
`INCUMBENT_NEURAL_REF` — seeded pure-stdlib MLP (legal surface → 3), dev-trained with the
same charged acquisition. **At #208 scale the incumbent is the same frontier model/harness
control arm; the pilot's MLP is a declared stand-in for the incumbent *class* (neural,
same surface), so every pilot terminal is scoped to the pilot** (FNA-1/FNA-5 neural-
reference precedent: diagnostic, bounds nothing about frontier capacity). Controls:
`ORACLE_LATENT` (exact latents — ceiling, never a result), `NO_CLASSIFIER` (harness floor),
`SHUFFLE_NULL` (label permutation null).

**Frozen sufficiency (before outcomes):** arm sufficient iff on protected EVAL failures
accuracy ≥ incumbent − 0.03 AND mean whole-chain charged cost per failed query (repairs +
inference + amortized acquisition/maintenance) ≤ incumbent × 1.05 AND neural invocations
for the capability = 0 (structural). Terminal: R1 sufficient →
`PARENT_SUFFICIENT_FOR_FAILURE_CLASSIFICATION` (guarded declared rule); R2 → same token
(calibrated estimator); R3 → `NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE`; none sufficient
while `ORACLE_LATENT` meets the incumbent bar → `NO_FUNCTIONAL_PARITY_FAILURE_CLASSIFICATION`
with the measured obstruction (acquisition-priced gap flags `ACQUISITION_COST_DOMINATES`;
surface-information gap flags `REPRESENTATION_INSUFFICIENT`); incumbent-class advantage at
matched charged cost that no legal-surface arm including oracle reaches →
`NEURAL_DONOR_DOMINATES_AT_SCOPE`; machinery failure → `CANNOT_CHECK_<reason>`.

**Declared limitations (before outcomes):** one authored world (E1/L1 evidence class,
#219's authorship); single-instance responsibility classes tuned to that world's physics;
the incumbent is a seeded MLP stand-in, not a frontier model; three responsibility classes,
not #208's full taxonomy; wall/CPU descriptive; nothing here licenses deployment — the
output is a proven-executable protocol plus one pilot terminal at pilot scope.
