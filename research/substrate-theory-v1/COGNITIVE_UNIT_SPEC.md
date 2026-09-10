# Formal Cognitive-Unit Spec v1 — verdicts on u and the corrected unit u₂

Evidence base: KSO audit of origin/main @ 2d95bcc (annex KSO_AUDIT.md, code refs therein); live results #356 #357 #359 #360; three parent-subtraction annexes. Distinguish: **epistemic truth** (does the unit hold a verified fact), **applicability** (when can it fire), **deployment** (is it live), **utility** (what is serving it worth), **economic value** (does it pay after full cost).

## Field-by-field verdict

| Field | Verdict | Evidence | Decision |
|---|---|---|---|
| Z representation/context | **necessary, wrongly defined at the selection joint** | representation *choice* is a hardcoded stub (solve.py:600 always `typed_hypergraph_v1`) | keep; make representation selection priced and learnable |
| I applicability | **necessary; split in two** | structural typing resolved at solve time (solve.py:382-384); no learned predicate exists | I_hard stays a typed contract on the unit; I_learned (utility) moves OUT of the unit into the control layer — see placement |
| φ transformation/policy | necessary, operative | registered units; production compilation (ARCH 1.2) is the consolidation import | keep |
| β termination/fallback | necessary, operative | divergence-triggered β is the strongest import (RL 2.3) | keep |
| Ψ predictive effect | **redundant as implemented** | declared on every OperatorSpec, serialized into manifests, read by nothing | wire it or remove it; recommendation: WIRE — three imports need it (Ψ-δ reflection ARCH 4.6, dream-phase gating SYNTH 2.3, cracking switch law SYNTH 6.2) |
| V conditional future value | **absent entirely** | `decide()` commits `passed[0]` in fixed catalogue order (solve.py:498-502) — no value, score, or cost ranks anything | the single most load-bearing gap; add as control layer, never flips liveness |
| W warrant/provenance | necessary, operative | warrant lattice, FEEDBACK⇒zero-warrant channel | keep |
| C capital+marginal cost | necessary; accounting operative, prediction dead | ledger bites (budgets); predictive cost model metadata-only; charging semantics corrected #353/#359 | keep; wire predictive C |
| L lifecycle/plasticity | necessary, incomplete | revocation/reinstatement exists; no retirement/consolidation loop (Soar excision ARCH 1.3, capital recycling RL 6.3) | keep; complete with priced retirement |
| P causal support/history | necessary, partial | support edges live; causal-effect history eval-lane-only | keep; move effect history into receipts |

## Missing fields (all three behavior-affecting in code, absent from u)

1. **A — authority lattice**: commit coordinate, meet-composition, `internal_authority` stripping (types.py:112-173). Permission ≠ provenance; W does not cover it. Behavior-affecting at the commitment gate and boundary.
2. **S — scope with epoch interval**: `covers()` semantics, UNBOUNDED_EPOCH refusal (solve.py:534-541). Neither I nor L captures deployment scope over time.
3. **κ — acquisition certificate channel**: 8 channels incl. FEEDBACK⇒zero-warrant (admission.py:28-36); drives the genome predicate and warrant laws.

## The corrected unit

```
u₂ = <Z, I_hard, φ, β, Ψ, W, C, L, P, A, S, κ>     (on the unit, warrant-bearing)
control layer = <I_learned, V>                       (outside the warrant lattice:
                                                     may order/prune candidates,
                                                     NEVER flips liveness/admission)
```

**Placement rule (from the code's own MEG-02/CoverageCertificate + `Candidate.score` "outside the lattice, ranking only" pattern):** hard applicability = decidable typed contract on the unit; learned utility/value = separate developmental-control layer; deployment-liveness = revocation/reinstatement + S.epoch, with automatic wiring from ActionReceipts/SelfModel FailureRecords into revocation (the missing wire, not the missing field).

## Failure taxonomy requirement (directive)

A failed candidate must distinguish: semantic invalidity / inapplicability / bad routing / insufficient representation / verifier rejection / resource exhaustion / economic harm. Today: a 9-layer taxonomy exists but the richest (ResidualKind, 11 kinds, runtime/residuals.py) is **dead code in the runtime**; inapplicable operators vanish silently in compose_stage (no receipt, unauditable); **no economic-harm class exists anywhere**. Requirement: every failure emits a receipt with class ∈ the 7 classes; see EFFICIENCY_ROADMAP F-1.

## Counterexample scoping rule

A counterexample constrains an entire hypothesis class only when the failure is *structural* (reproducible under the class's invariant set: e.g. shared-substring mining failure SYNTH 2.2 constrains all support-rank miners) and constrains only one scoped attempt when the failure is *operational* (routing, budget, seeding). The admit/deny decision between these two is itself typed into P and replayable.
