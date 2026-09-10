# Comparator ladder freeze — FE-DEV-AMORT-1 (developmental arm)

Design authority: `COMPARATOR_LADDER_FREEZE_V1.json` (this file is the distilled reading order; the
JSON is the freeze). Binds #151 / DC-10. Opened 2026-09-10, frozen before any protected run,
explicitly non-final. This closes the flagship entry gate **"Strongest comparator configurations
frozen"** (was PENDING) and nothing else — FE-DEV-AMORT-1 authorization stays withheld while G2,
G3 and the two-domain gate remain open.

## What was frozen

Every rung of the #165 section 9 ladder is now a concrete registered machine configuration with
shared budgets, seed policy, capability-gate parameters and cost-vector recording. No rung is a
placeholder; every "strongest" claim is anchored to a sealed receipt, not prose.

Shared invariants (all rungs):

- **Budgets** — serving 200,000 slots/serve; dev 200,000 slots; the one-time dev enumeration charge
  (D1: 14,427,131 slots, sealed) is a single fixed ledger entry paid once per run by every arm that
  uses dev history (M1C charging rule, cited verbatim). 200k is the registered M1B completed-serve
  budget — the only rung where RESET and the strong parent both finish 8/8 checker-verified serves.
- **Seeds** — 20260910 frozen (matches the M1B estate) for null/bootstrap machinery; sampling seeds
  pick instances *within* frozen semantic partitions, never the boundary; no redraw after results.
- **Capability gate** — `Performance_OCM >= Performance_parent − δ`, δ = 0.20 (the registered
  pre-experiment margin default, M1→M1B→M1C unchanged), measured as CHECKER_C-verified competence
  at the frozen budget, frozen before any protected outcome.
- **Cost vector** — the HDI-14 families verbatim plus E3-P3 physical meters (wall, RSS, I/O,
  storage; energy where available); store bytes are charged, never converted to slots.
- **Parity** — matched information, resources and checker access for every parent rung; parity
  receipt per run; oracle arms stay calibration riders, never headline comparators.

## The ladder in one line each

| Rung | Frozen configuration |
|---|---|
| B0 conventional domain system | Registered primitive search, zero learned state (D1: the M1B RESET configuration byte-identically; dialogue: stateless `MatchedParent`). RESET_OCM coincides with B0-D1 at serving time — declared identity, both readings recorded. |
| B1 strong Transformer | **In-estate instantiation**: the FNA-3 tournament winner per world (CTW / PCFG-EM / BPE+PPM / n-gram, `fna3.py` AS-IS). A true trained Transformer is NOT_RUNNABLE_IN_ESTATE (no chargeable training denominator) and is routed to E5; until then `LLM_CAPABILITY_DOMINATES` reads in-estate scope only. |
| B2 + RAG | B1 + the registered retrieval unit `semantic_memory.py` AS-IS (its own retrieval behaviour — no new depth parameter) over the SAME knowledge the OCM machine holds. |
| B3 + persistent memory | B2 + the matched parent's own persistence model (`matched_parent.py` save/load) across exactly the OCM arm's stage-boundary checkpoints. |
| B4 + tools/checkers | B1 + the external CHECKER_C subprocess channel — the parent verifies through the same independent checker units, with spawns charged in the ledger. |
| B5 + memory + tools | B3 + B4 combined; the strongest non-adaptive parent product. |
| B6 + adaptation/skill memory | B5 + parent-side skill accumulation under the FNA-4 utility-gated admission rule (recurrence-gated admission stays excluded: measured harmful), own persistence, storage charged. |
| B7 strongest domain-specialized parent | D1: the M1B STRONG_ADAPTIVE_PARENT machinery byte-identically (decision-list applicability on dev data only, serving the mined fragments through registered `M.solve`). Dialogue: `semantic_parent.py` AS-IS. Sequence worlds: FNA-3 winner (B7 = B1 there — declared identity). |
| B8 strongest faithful parent product | `matched_parent.py` (M7 §4) + the M12 semantic layer on language: same knowledge, lessons, record and budget, built from known components, *without* warrant intervals / reopening / version spaces / commitment gate — the subtraction control. |
| OCM | The registered core AS-IS: F = kso/store epistemic field, O = `learning/methods.py` learner + operators, Π = `runtime/ocm_runtime.py`, C = constitution + CHECKER_C; M1 8-step lifecycle with OS-restart evidence; `DevelopmentTransitionV1` per transition. `src/ocm` never edited — drift = RECEIPT_BINDING_DEFECT. |

## Binding to the developmental arms

- **CONTINUED_OCM** — OCM rung, no reset across stages, pays the one-time dev ledger entry once.
- **RESET_OCM** — OCM rung reset at each stage boundary; no dev phase, no dev charge; the "reset
  OCM" integrated ablation of #165 §9.
- **STRONG_ADAPTIVE_PARENT** — the B7 machinery with the *same* allowed history, persistence and
  legal adaptation rights (M1/M1B ORDINARY_ADAPTIVE_PARENT parity clause), riding every rung —
  comparators evolve too; no frozen-parent strawman (#165 G7).
- The remaining #165 §9 integrated ablations (no learned methods, no composition, no failure
  memory, no dependency/revocation graph, global scan, no representation change, no consolidation)
  ride the OCM rung as declared knockouts.

## Honest limitations (registered, not hidden)

1. B1's canonical form does not exist in this estate; the frozen instantiation is the registered
   tournament winner, and the Transformer comparison is an E5 deliverable.
2. B7 = B1 on sequence worlds (there the tournament winner IS the strongest specialized parent).
3. D2 (implication-systems, P1-E3 authored families) inherits every constant here; its
   dev-enumeration cost is a measured output sealed in its own pre-registration — writing a number
   now would fabricate a measurement.

## Forbidden (short list)

Post-hoc tuning of any frozen number; adding/substituting arms mid-study; editing `src/ocm` or any
registered comparator module (imported AS-IS); running a weakened ladder subset and calling it the
comparator set; presenting an oracle rider as headline; claiming the Transformer gap closed without
a delivered E5 implementation; any scored FE-DEV-AMORT-1 run while authorization reads
FROZEN_DESIGN_NOT_AUTHORIZED.
