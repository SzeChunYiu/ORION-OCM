# OCM design set V1 — the knowledge-space machine for ORION v2

Read this file first. It is the index of the complete design: what the machine is, the reading
order, and the legend every other file uses. The set answers one question end to end: *how does a
typed question become a properly warranted answer inside a knowledge-space object, with no LLM in
the store or the solver?* (#284 build contract, integration directive, end-to-end gate.)

## Status legend (every statement in this set carries one)

| tag | meaning |
|---|---|
| `[MACHINE: name]` | implemented and exercised on the running machine by the named checker (planted failure + no-alarm case) |
| `[PROVED: KS-Txx]` | theorem in `theory/KSO_SUBSTRATE_CONTRACT_V1.md` with proof and checker |
| `[SPEC]` | fully specified here, not yet built; the build lands at the milestone named beside it |
| `[OPEN_Mn: reason]` | cannot be stated before milestone n, with the reason |
| `[PARENT: name]` | owned by a published parent; we re-implement faithfully, delta stated where one exists |

A file is complete when its acceptance line (comment 5543880205 on #284) holds. A `[SPEC]` item is a
build obligation, not a claim. `NO NOVELTY OR BREAKTHROUGH CLAIM` anywhere in this set.

## What the machine is (one paragraph)

A **knowledge space** `𝒦 = (A, H, τ, L, Σ)`: atoms `A` (decomposed knowledge structures), typed
hyperedges `H` with type map `τ`, an ATMS warrant label `L` on every atom and edge, and a fixed
genome `Σ = {S1..S7}` no operation may write. A question is atomized into a seed vector over `A`,
navigated by a label-gated restart walk with frozen denominators, and the connected reacting
subgraph is **extracted, not generated**; composition of the extracted procedure carries a warrant
that is the `⊗` of its parts, so revoking any part revokes the whole exactly. Knowledge enters only
through warranted channels; feedback cannot warrant; an exact checker can. When navigation fails,
the machine says whether the failure is a **gap** (acquire) or a **witnessed obstruction** (Jump),
never a fluent guess. The LLM, if present, is a codec at the boundary and may never write a label.

## Reading order

| file | question it answers | acceptance (short) |
|---|---|---|
| [01_STRUCTURES.md](01_STRUCTURES.md) | which data structures, and why these over the alternatives | one comparison table per structure, every rejected row has a reason |
| [02_MATHS.md](02_MATHS.md) | the objects and every theorem | statement · proof · checker · parent · ledger row; zero `ABSENT` |
| [03_DYNAMICS.md](03_DYNAMICS.md) | what changes, at which time scale, under which law | five scales, each with state / law / invariant / fixed point / checker |
| [04_ALGORITHMS.md](04_ALGORITHMS.md) | the procedures, their cost and their correctness | pseudocode · typed I/O · complexity · theorem · checker |
| [05_MECHANICS.md](05_MECHANICS.md) | what happens, step by step, when a question enters | three reproducible traces: FOUND · GAP · OBSTRUCTION |
| [06_ARCHITECTURE.md](06_ARCHITECTURE.md) | components, interfaces, forbidden edges | every forbidden edge has a planted-violation checker |
| [07_ABSORPTION.md](07_ABSORPTION.md) | how ORION v1 and v2 live inside this machine | zero `UNMAPPED` at or below the current milestone |
| [08_PARENTS.md](08_PARENTS.md) | who owns each piece in the literature | every row `PARENT_OWNED` / `PARENT_SUFFICIENT` / `DELTA_STATED` |

## Milestones this set is built against

| milestone | deliverable | state (2026-09-04) |
|---|---|---|
| M0 substrate contract | `KSO_SUBSTRATE_CONTRACT_V1.md`, `kso_math_v1.py` (KS-T01..T09) | on main (#296 → `68d8e59`) |
| M1 KSO v0 on ME-X1 | `kso_m1_mex1_population_v1.py`, receipt, freeze checks | built; independent replay found 2 vacuous checkers; fixed on #295 (re-replay pending) |
| M2 solve loop vs oracle | `kso_m2_solve_v1.py`; comparator arms; translator invariance (provable half) | ran on #295 (design frozen, seed committed): exact vs oracle 50/50, two-atomizer invariance 50/50, 0 overruns — **pre-registered as exact-by-construction**; extraction reached the request atom on 38/50 only (12/50 answered by the store read in compose) → M2.1 revival lead; comparator join pending |
| M2b algebra domain | instruction-channel population + SymPy exact-checker channel | `[SPEC]` |
| M3 gap loop | missing atom ⇒ acquisition, never a guess | `[SPEC]` |
| M4 Jump loop | witnessed obstruction ⇒ governed rewrite; J0–J8; #558 worlds | `[SPEC]` |
| M5 codec boundary + `ocm chat` | two codecs, translator-invariance gate, CLI | `[SPEC]` |
| M6 frontier-maths pilot | proof assistant as warranting channel | `[OPEN_M6]` |

End-to-end gate (comment 5543899171): `ocm chat` answers the two registered probe classes
(P1 problem — "solve quadratic equations"; P2 dialogue — "hello how are you") on held-out paraphrases
under two codecs, budget-matched against an LLM alone and retrieval-QA. Today: neither.

## Custody

Owner: OCM lane (#284). This set is hash-bound in `results/KSO_M0_FREEZE_V1.json` once landed;
edits rebind. Every `[MACHINE]` tag names a checker that exists in `reference/`; an independent
lane replays them before any section is called complete.
