# E2R alternative-accounting audit freeze

Date frozen: 2026-09-17.
Authority: revival ticket `REV-L49-L53-SEARCHER-ACCOUNTING` (GMI #833 baseline register, `BASELINE_MANIFEST_V1.json`), issue #833, section-E lane (#715).

This document is the **pre-outcome authority** for the E2R accounting audit. It is committed before any E2R audit witness execution. It does not alter `FREEZE_E2.md` or `ACCOUNTING_FREEZE_E2.md`; both remain frozen in place. The audit adds alternative resource accountings and re-adjudicates the E2 over/under-cap verdicts under each, closing the `UNAUDITED_COST_DEPENDENT` / `UNTESTED_SCALARIZATION_DEPENDENT` flags.

## Audited claims

The E2 Section-6 verdicts that rest on resource accounting (all other E2 content — search dynamics, success probabilities, exactness, terminals — is accounting-independent and is asserted as such, not re-adjudicated):

```text
V-RAND   uniform random: exact success probability 5/16 at the cap
V-STRICT strict evolutionary: success probability 0, under the cap
V-DRIFT  neutral drift: finite exact probability < 1, under the cap
V-NAS    one-shot ablation: exact recovery but OVER the primary cap
V-DARTS  DARTS-like gradient: exact recovery WITHIN the cap
```

Package-level claims re-adjudicated at the end:

```text
C-NAS-OVER   "the ablation method is over the common 320-touch primary cap"
C-ORDERING   the E2 claim ceiling: same-world finite-budget observed recovery
             is search-mechanism dependent; no universal searcher dominance
```

## Reference accounting A0 (preregistered, frozen)

Primary resource: `truth_example_touches` at 32 touches per complete discrete semantic verification, discrete cache free on re-visit, relaxed evaluations charged 32 touches each, final exact verification charged to the method. Cap 320. Arithmetic ops charged in a separate coordinate. (From `ACCOUNTING_FREEZE_E2.md`.)

## Alternative accountings (declared before execution)

Every constant below is traced to a frozen source; no new numeric constant is introduced.

### A1 EVAL-COUNT (count-based)

Unit: one **complete candidate evaluation** — one full discrete semantic verification or one full relaxed 32-example loss evaluation — priced 1 unit regardless of example count. Cache rule: kept (a re-visited cached discrete mask costs 0 units; it is not re-evaluated). Final exact verification charged to the method (consistent with A0). Cap: **10 units**, from the frozen derivation of the 320-touch cap as "ten full discrete candidate evaluations" (`FREEZE_E2.md`).

### A2 EXEC-B (exec-based; #978 EXEC-B precedent)

Unit: one **single-example execution** of any evaluation routine — one iteration of the per-example loop of the registered implementation. A discrete verification is 32 execs; a relaxed loss-only evaluation is 32 execs; the exact loss+gradient routine is 32 execs (its registered implementation is a single per-example loop computing loss and gradient per example). **No cache discount**: every executed verification pays 32 execs, including re-visited discrete masks. Cap: **320 execs** — the frozen touch-cap number read as single-example executions.

### A3 OP-PRICE (resource-price scalarization, arithmetic-op-dominant)

Single scalar cost over the two frozen coordinates:

```text
cost = 26 * truth_example_touches + arithmetic_update_ops
```

Exchange rate grounding: 26 is the frozen arithmetic cost of the cheapest registered per-example routine, the loss-only forward (`ACCOUNTING_FREEZE_E2.md`, "26 arithmetic ops/example"); it converts one example-touch into op-equivalents at the package's own implemented cost. Cap: **8320 op-equivalents** = 320 × 26, the frozen identity already stated in `ACCOUNTING_FREEZE_E2.md` (`10 * 32 * 26 = 8320`). Cache rule: as A0.

### A3B OP-PRICE-NOCACHE (resource-price variant, cache-dominant weighting removed)

As A3, but the discrete cache grants no discount: every verification event (including re-visited discrete masks) is charged 32 touches. This is the lever's "cache-dominant weighting" removed — the accounting in which the shared verifier cache does not exist.

### A4 VERIFIER-EXEMPT (count-based, shared final verifier not charged)

As A1, except the **final exact discrete verification is charged to the frozen ecology, not to the method** — the "verifier is the referee" convention: every searcher submits to the same shared verifier, which is part of the world, not the searcher. Search-intrinsic verifications (random's verification slots, drift's per-proposal verifications, strict evolution's candidate verifications) remain charged. Cap: **10 units**.

## Frozen predictions (exact rationals; adjudication = cost vs cap)

Per-searcher costs under each accounting, derived from the frozen mechanics:

```text
                       A1 (cap 10)         A2 (cap 320)            A3 (cap 8320)              A3B (cap 8320)             A4 (cap 10)
random   @10 slots     10                  320                     26*320 = 8320              8320                       10
strict   10 attempts   6 (cache)           10*32 = 320             26*192 = 4992              26*320 = 8320              6
drift    5 proposals   15622/3125          32*613/125 = 19616/125  26*499904/3125             26*19616/125 = 510016/125  15622/3125
nas      ablation      10+1 = 11           10*32+32 = 352          26*352+8320 = 17472        17472                      10 (exempt)
darts    one step      1+1 = 2             32+32 = 64              26*64+2122 = 3786          3786                       1 (exempt)
```

Adjudication states: `over` (cost > cap), `at` (cost == cap), `within` (cost < cap). Expected adjudication per accounting:

```text
            A0      A1      A2      A3      A3B     A4
V-RAND      at      at      at      at      at      at
V-STRICT    within  within  at      within  at      within
V-DRIFT     within  within  within  within  within  within
V-NAS       over    over    over    over    over    at        <-- FLIP under A4
V-DARTS     within  within  within  within  within  within
```

Success values are accounting-independent and must reproduce exactly: random 5/16; strict 0 / `STRICT_ELITIST_PLATEAU`; drift 12/125 (by 5) and 72696/390625 (by 10); nas exact mask 21; darts exact mask 21, 2122 ops; singleton negative twin unchanged.

## Frozen claim-level adjudication rule

- A verdict **holds** under an accounting if its adjudication state matches A0's.
- A verdict **flips** under an accounting if the state changes (predicted: V-NAS `over -> at` under A4 only).
- `C-NAS-OVER` is **accounting-sensitive** if any declared accounting flips V-NAS; the flip witness (accounting name + both states) is registered. Predicted: sensitive, flip witness A4.
- `C-NAS-OVER` is revived at full strength as `C-NAS-AT-OR-OVER` ("the ablation method consumes the entire evaluation budget or more under every declared accounting; it is never strictly within budget; it is strictly dominated in cost by the DARTS representative under every declared accounting") if the predicted table reproduces exactly.
- `C-ORDERING` is **accounting-robust** if, under every declared accounting, the five searchers' recovery outcomes remain pairwise distinct in the (cost state, success) projection. Predicted: robust.

## Witness requirements

1. The audit witness imports the frozen E2 witness and reuses its routines; it must not duplicate search mechanics.
2. Costs are recomputed from mechanics (instrumented counting), not multiplied from published result numbers, wherever the accounting changes what is charged: strict-evolution verification events under no-cache rules, drift verification events inside the 3125-path enumeration, relaxed-evaluation counts.
3. Exact rational arithmetic throughout (`fractions.Fraction`); no floats; no Monte Carlo.
4. Receipts record, per accounting and searcher: cost (exact rational), cap, adjudication state, A0 state, hold/flip. The receipt pins sha256 of `FREEZE_E2.md`, `ACCOUNTING_FREEZE_E2.md`, and the frozen witness source at audit time.
5. Exit non-zero if any frozen prediction above fails to reproduce exactly.

## Claim ceiling for this audit

```text
E2R_ALTERNATIVE_ACCOUNTING_AUDIT
FIVE_DECLARED_ACCOUNTINGS_A1_A2_A3_A3B_A4
C-NAS-OVER_ACCOUNTING_SENSITIVE_WITH_REGISTERED_FLIP (predicted)
C-NAS_AT_OR_OVER_REVIVED (predicted)
C-ORDERING_ACCOUNTING_ROBUST (predicted)
NO_CHANGE_TO_FROZEN_E2_CONTENT
```
