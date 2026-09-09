# Heritable Search Transformation v1 — capsule map

Issue #233. Formal-theory child above #145/#149/#151/#165/#217/#221; evidence under #144.
**NOT a cognitive architecture.** Claim discipline: prove at actual scope, mark the
impossible, only the irreducibly empirical residual reaches LUNARC.

## Read order

1. `FREEZE_HST_V1.json` — freeze-before-theorem-artifacts, proof classes, forbidden terminals
2. `HST_DEFINITIONS_V1.md` — Σ_t, U, B, Ev, binding terminology (frozen)
3. `HST_THEOREM_REGISTRY_V1.json` — 18 rows, frozen statements, statuses filled by lanes
4. `LITERATURE_LEDGER.md` — parents and what each owns
5. lane artifacts: `proofs/` (P1/P5), `exact/` (P2 certificates + runners), `bounds/` (P3), `hostiles/` (counterexamples)
6. `HST_EMPIRICAL_BRIDGE_V1.json` — row → #145/#151/#217/#221 measurement map (centre, after lanes)

## Execution order (issue §14)

D0/D1 (this commit) → D2 core proofs lane A → D3 finite microscopes lane B →
D4+D5 limits lane C → D6 transfer bound lane D → D7 bridge (centre) →
D8 independent hostile review (fresh-context agent).

## Hard rules for lanes

- Statements in the registry are frozen; fill only the designated fields via declared amendments.
- Python is a witness/certificate generator, not a proof of P1 claims; no row becomes PROVED because a test passed.
- Exact runners/tests execute on **billy-laptop** (`ssh billy-laptop`), never on the Mac.
- Every attractive claim ships with its nearest-false-generalization counterexample (`hostiles/`).
- `CANNOT_PROVE_<reason>` / `CANNOT_CHECK_<reason>` / `PARENT_SUFFICIENT` are honest terminals.
