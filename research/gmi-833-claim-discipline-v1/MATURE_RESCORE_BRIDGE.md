# Maturity re-score bridge — the seven G6 analytic proofs WITH registered falsifiers

**Rule applied (FREEZE_V2.md §4, judgment table, verbatim):** `ANALYTIC_PROOF` (deductive argument) with explicit premises AND falsifiers → **EV1 / M1**; `ANALYTIC_PROOF` without registered premises/falsifiers → EV0 / M0 (recorded gap G6).

**Input change made by this tranche:** falsifiers (and parents/forbidden where absent) are now registered per object in `REGISTRATIONS_V1.json` — `authored_g6_v1.py` holds the authored records, each falsifier an observable derived from the claim's own statement/proof. The rescore-v2 package is NOT modified; this table is the recomputation under its own frozen rubric.

| # | result_id | object | premises (before → after) | falsifiers (before → after) | M (before → after) | EV (before → after) |
|---|---|---|---|---|---|---|
| 1 | GMI833_V2_LEGACY_003_AS-1 | AS-1 (analog D1/D6 reduction) | explicit in-doc → unchanged, now REGISTERED (EXTRACTED, 3 premises) | none in package → REGISTERED (3 observables) | **M0 → M1** | **EV0 → EV1** |
| 2 | GMI833_V2_LEGACY_014_EC-2 | EC-2 (finite external-state reduction) | explicit in-doc → REGISTERED (3 premises) | none in package → REGISTERED (2 observables incl. frozen-ecology predictions) | **M0 → M1** | **EV0 → EV1** |
| 3 | GMI833_V2_LEGACY_089_DE-3 | DE-3 (residual-rate CI) | explicit in-doc → REGISTERED (2 premises) | none in package → REGISTERED (2 observables) | **M0 → M1** | **EV0 → EV1** |
| 4 | GMI833_V2_LEGACY_091_DP2-6 | DP2-6 (finite-horizon switch criterion) | explicit in-doc → REGISTERED (1 premise block) | none in package → REGISTERED (2 observables) | **M0 → M1** | **EV0 → EV1** |
| 5 | GMI833_V2_LEGACY_124_NC-3 | NC-3 (shot/sample readout scaling) | explicit in-doc → REGISTERED (1 premise block) | none in package → REGISTERED (2 observables) | **M0 → M1** | **EV0 → EV1** |
| 6 | GMI833_V2_LEGACY_166_SG-1 | SG-1 (stability bounds expected gap) | explicit in-doc → REGISTERED (2 premises) | none in package → REGISTERED (1 observable) | **M0 → M1** | **EV0 → EV1** |
| 7 | GMI833_V2_LEGACY_170_TI-2 | TI-2 (conditional acquisition burden) | explicit in-doc → REGISTERED (3 premises) | none in package → REGISTERED (2 observables) | **M0 → M1** | **EV0 → EV1** |

**Delta:** 7 × (M0→M1, EV0→EV1). Corpus-level effect at frozen v2 scope: M0 48→41, M1 30→37; EV0 46→39, EV1 30→37. DOWN_GENERATING count for these 7 flips from 48-row membership to MAINTAINS-at-M1 under the bridged judgment; every other v2 score is untouched.

**What does NOT move, and why (typed):**

- `GMI833_V2_LEGACY_073_MORPHOLOGY_PHASE_RV_THEO` (ANALYTIC_PROOF at M0) is **G7**, not G6: its blocker is `DEGENERATE_HELDOUT_NO_DISCRIMINATIVE_POWER` (100%-by-construction held-out on a deterministic world) — a substance gap in the evidence design, not a registration gap. Falsifier registration does not unblock it.
- `V0.2` stays UNSCORED_WITH_REASON (SUPPORT_NOT_LOCATED — document preamble, no claim statement to register against).
- The 62 census proof-mode disagreements and the M0–M6 terminology collision inside `machine-intelligence-morphogenesis-v1` (FREEZE_V2 G4: `M0..M5` tokens are morphology-signature row names, never maturity levels) are **reported, not fixed** — they are owned by the dependency-graph/terminology successor lanes (PR #949 merged the graph side; the terminology collision belongs to the terminology lane's successor tranche).

**Verification:** each of the seven proofs was read in full at its locator by the tranche author (statements, premises, proof bodies quoted in `authored_g6_v1.py` sources); the premises cited are exactly those the printed proofs invoke; no falsifier was registered that is not an observable of its own claim.
