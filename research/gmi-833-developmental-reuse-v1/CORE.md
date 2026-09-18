# CORE — gmi-833-developmental-reuse-v1 (#833 Section L)

**Three Section-L rows closed; two deliberately left OPEN.**

## What this package proves (exact, machine-checked, two routes)

- **REP-1** — a representation change reduces discovery burden **iff its length
  compression outruns its alphabet inflation**, decided rank-free by
  `Φ(n',ℓ1) ≤ Φ(n,ℓ0−1)` (reduction) / `Φ(n',ℓ1−1) ≥ Φ(n,ℓ0)` (increase),
  **without running the search**. 702-cell census `359/167/176`, 0 disjointness
  and 0 monotonicity violations. **REP-1b** (found by the second route) refines
  it five-way to `359/3/172/1/167` with 0 conflicts: the frozen rule is sound
  but incomplete at 4 boundary cells.
- **REP-2** — `ΔNet = −Saving(T⁺) + Tax(T⁰) + K_total`, reproducing #897's
  published `HLD-1` integers **exactly** (`50,052 → 1,307`, `K=6`, net
  `−48,739`; control `538 → 1,710`, `+1,178`; combined Saving `48,745`, Tax
  `1,172`, `ΔNet −47,567`), and rejecting the solution-capital library that
  REP-1 accepts per target (`−36,890` alone vs `+18,139` on the distribution).
- **REP-3** (EARNED-BY-COUNTEREXAMPLE) — at `w = cccccabcccc` the macro **is**
  used and `ℓ` drops `11 → 10`, yet burden rises `265,152 → 1,048,831`
  **rank-free** (`Φ(4,9)+1 = 349,525 > 265,719 = Φ(3,11)`). Shortening the
  description is **not sufficient**. The registered near-miss at `|w| = 10` must
  be — and is — refused as `RANK_DECIDED`.
- **NOV-1** — **proven impossibility**: conservative growth adds **zero**
  expressive power at every `t` (`{Expand(p) : p over A_t} = Σ⁺`, checked on all
  1,092 words of length ≤ 6; 3 cyclic hostiles rejected fail-closed).
- **NOV-2** — under the only surviving reading (budget-reachability), growth
  **does** add and **simultaneously removes**: `ADDED/REMOVED` = `3/4`, `23/45`,
  `1/698`, `0/343`, `0/0` at `B = 10, 100, 1000, 5000, 20000`. A trade, not a gain.
- **SD-1/2/3** — 8 dynamics × 3 ecologies × 200 targets in one charged frame.
  **No dynamic best in every ecology, none worst in every ecology.** The
  ordering is *derived*: enumeration is exactly optimal in expectation under
  opacity (`(|X|+1)/2 = 3281`, attained); coordinate descent hits in exactly
  `1 + ℓ(n−1) = 17` under separable grading (separation floor **28× / 193× /
  1,405×** at `ℓ = 6 / 8 / 10`, verified exhaustively over every start point at
  `ℓ ∈ {6, 8}`); under deception the same dynamic
  collapses to a restart accident of window exactly `3/6561` (every measured hit
  explained; route B's exhaustive sweep finds precisely the predicted set).
  `OPAQUE` query sequences are provably **target-independent** for all 8
  dynamics, and the three objective-blind ones (`MUT`, `NAS`, `RAND`) have
  byte-identical rows in all three ecologies. `NAS` runs inside the same charged
  frame (12/200 hits everywhere) and its sign was predicted by REP-2 before it
  ran, 4/4. `META`'s
  coverage-dilution identity: its `ENUM` arm gets exactly `|X|/3 = 2,187`.

## Rows left OPEN, and why

- `Predict evolvability on genuinely future task families.` — futurity is a
  custody property this tranche cannot manufacture; anything it could author or
  pin from repository blobs is out-of-sample but **past**.
- `Validate developmental predictions on continual-learning systems.` — no real
  system with a sha256-bound data source in hand; synthetic trajectories would
  be a category error.

## Read in order

`FREEZE_V1.md` (scope + adjudication, commit `01c6a820`, before all code) →
`PARENT_OWNERSHIP_V1.md` → `DEVELOPMENTAL_REUSE_THEOREMS_V1.md` (L0, REP-1..3,
NOV-1..2, SD-1..3) → `RESULT_V1.json` / `ORACLE_RESULT_V1.json` →
`RECEIPTS_RUN_LOG.md` → `MANIFEST_V1.json`.

## Reproduce (stock CPython ≥ 3.8, stdlib only; CI reruns both modes)

```bash
python3 -I -B  research/gmi-833-developmental-reuse-v1/developmental_reuse_v1.py   # == RESULT_V1.json
python3 -I -B  research/gmi-833-developmental-reuse-v1/independent_oracle_v1.py    # == ORACLE_RESULT_V1.json
python3 -I -B  research/gmi-833-developmental-reuse-v1/test_developmental_reuse_v1.py -v
python3 -I -O -B research/gmi-833-developmental-reuse-v1/test_developmental_reuse_v1.py -v
```

## Honest disposition of a failed registered criterion

`FREEZE_V1.md` §5 froze "`OPAQUE`: guided dynamics must NOT beat the RAND
control". Measured: GRAD 133, LS 133, MUT 136 vs RAND 129 of 200 — **not met as
specified**, reported verbatim in the receipt. Attribution: the criterion
measured a hit count, but under `OPAQUE` no dynamic can use guidance at all
(SD-2d), so the hit count is a pure coverage lottery. Replaced by the exact,
mechanical, strictly stronger target-independence test.

**Claim ceiling:**
`GMI_833_FINITE_EXACT_REPRESENTATION_CHANGE_CRITERION_GRAMMAR_GROWTH_NOVELTY_CHARACTERIZATION_AND_ECOLOGY_CONDITIONAL_SEARCH_DYNAMIC_COMPARISON_AT_REGISTERED_SCOPE`.
Forbidden promotions are pinned in `MANIFEST_V1.json` and enforced by CI.
