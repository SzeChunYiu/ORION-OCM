# 06 — Architecture: components, interfaces, forbidden edges

Every component: contract (in / out / invariants), governing theorems, guarding checker, absorbed
parent. Then the dependency graph — what may call what — and the forbidden edges, each with a
planted-violation checker.

## Components

| component | in | out | invariants | theorems | checker | parent |
|---|---|---|---|---|---|---|
| **Store** `𝒦` (`KnowledgeSpace`) | transactions (τ2), revocations (τ3), rewrites (τ5) | read views for the solver | KS-T00 well-formed; `Σ`; frozen `d` | T00, T08, S1–S7 | `validate`, freeze predicates | ATMS node/justification store |
| **Solver** (A2–A6, A11, A12) | `𝒦` (read-only), `s_Q`, `R`, `B` | `ρ*, E_R, X_Q, π, Ω, B_spent` | never writes `𝒦`; `Ω` computed by A12 only | T02–T06b, T10a, T11, T19, T20 | M1 retraction/hub checkers; four-valued outcome checker | RWR/PPR + JTMS gate (the KSO law is their composition, 08) |
| **Channels** (A8 adapters) | external source + certificate kind | transaction `t` | label by kind; FEEDBACK ⇒ `0` | T13, T15, T08 | acquisition transaction checker | LfD, Angluin/KWIK, experimental design, RLHF (negative) |
| **Exact-checker channel** | candidate answer + instance | certificate `c` or refusal | a refusal is not feedback: it carries no label and closes no gap | T15 | SymPy/Lean adapter tests `[SPEC → M2b/M6]` | proof assistants; ME-X3 Lean cross-check |
| **Codec boundary** (M5) | text ↔ `(s_Q, req, η_Q)`; `(X_Q, π, warrant, Ω)` ↔ text | — | **no write access** to `L, H, T, Σ, Ω`; E30-R14 boundary contract; anchored-edit interface for any structured output | T10, T10a, S7 | translator-invariance gate; planted codec write rejected `[SPEC → M5]` | E30-R14 template, `anchored_edit_interface.py` |
| **Immune system** | every write, every run | accept / reject / `CANNOT_CHECK` | a check with no alarming outcome available is broken (ledger rule) | all | the checkers themselves + self-tests with planted failures | `FAILURE_LEDGER.md` (27 classes) + `OCM_FAILURE_LEDGER.md` |
| **Growth operators** (A9, A10, τ4) | admissible `~`, `φ` | `𝒦'` | S4, S5; labels never merged | T07, T12, T16 | stem-cell invariant; planted non-measurable merge `[SPEC → M3]` | DreamCoder (library), Gödel machine (self-modification) |
| **Jump operator** (A13, τ5) | obstruction witness | rewrite proposal atom | only after T19; never `Σ` | T14, T19 | planted Jump without witness rejected `[SPEC → M4]` | v1 J0–J8, ME-X2, #558 worlds |
| **Comparator harness** (A14) | same `(𝒦, s_Q, B)` per arm | paired table, `PARENT_*` verdict | equal budget or `CANNOT_CHECK` | T17 | random arm at null; oracle arm at 1.0; overrun ⇒ 2 `[SPEC → M2]` | B5 federation discipline (ORION v2) |
| **Run protocol** | design + gates | receipts | sha256 freeze pre-run; seed commitment pre-run, reveal post-run; no post-outcome edit; `PROTECTED_RUN_AUTHORIZATION` archived | — | `KSO_M0_FREEZE_V1.json` binding scan; self-digest assertion (the #295 stale-binding fix) | ORION v2 freeze discipline |
| **`ocm chat`** (M5) | stdin text | answer, `X_Q` ids+labels, warrant, `Ω`, `B_spent` | output fields are the solver's, verbatim; no field synthesised by the codec | S7 | end-to-end gate probes P1/P2 | — |

## Dependency graph (who may call whom)

```
ocm chat ──▶ codec ──▶ solver ──▶ store (read)
                │          │
                │          └─▶ exact-checker channel (certificate) ──▶ channels ──▶ store (write, via τ2)
                └─▶ render ◀── solver outputs (read-only)
immune system ──▶ intercepts every store write, every solver outcome, every run
growth ops ──▶ channels (τ2) + revise (τ3) ──▶ store        jump ──▶ (witness from solver) ──▶ store shape (τ5)
comparator ──▶ solver (KSO arm) + parent arms on the same store view
```

## Forbidden edges (each has, or gets, a planted-violation checker)

| edge | why forbidden | checker | tag |
|---|---|---|---|
| codec → `L` (writes a label) | fluency is not warrant (S7) | planted codec label write rejected | `[SPEC → M5]` |
| codec → `Ω` (sets the outcome) | outcome is computed by A12 | planted codec-written `Ω` ignored, mismatch flagged | `[SPEC → M5]` |
| FEEDBACK → live label | KS-T15 | feedback atom cannot enable any edge | `[MACHINE]` |
| any → `Σ` | genome has no writer | seven planted violations; digest unchanged after every operator | `[MACHINE]` |
| τ2/τ3/τ4 → existing `L` | labels are append-only per atom; revocation changes `R`, not `L` | planted label edit rejected | `[MACHINE (acquisition)]` |
| τ2 → existing `d(a)` | frozen denominators (KS-T04) | recompute-on-acquire mutant differs from frozen | `[SPEC → M2b]` |
| Jump without witness | KS-T14 | planted Jump rejected | `[SPEC → M4]` |
| solver → store write | solver is pure | write during navigation raises | `[SPEC → M2]` |
| comparator arm with unequal `B` | KS-T17 | overrun ⇒ `CANNOT_CHECK` | `[SPEC → M2]` |
| run without freeze / seed commitment | run protocol | receipt writer refuses without the freeze digest | `[MACHINE: freeze binding scan]` |
| a checker with no failing outcome | ledger rule (vacuity) | every checker ships with its planted failure; the independent replay adds its own | `[MACHINE — replay found 2 vacuous in M1, being fixed]` |

## Interfaces (types)

- `Transaction = (atoms: tuple[Atom], edges: tuple[Hyperedge], cert: Certificate(kind, source_id, label))`
- `Query = (s_Q: dict[atom_id, Fraction], req: atom_id | kind, eta: dict[type, Fraction])`
- `SolveResult = (rho, enabled, X_Q, pi, warrant: Label, omega: Outcome, budget: NavigationBudget, witness | hook | None)`
- `Receipt = (freeze_digest, seed, command, python, inputs, result, self_digest)`
Everything crosses a boundary as these; nothing crosses as free text except at the codec.
