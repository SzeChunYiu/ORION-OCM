# Concept realizations, and granularity as a bang-bang law — I2 (#602)

Date: 2026-09-14. Status: **DERIVATION + EXACT WITNESS, WITH A NAIVE READING CORRECTED**. Closes the two
remaining boxes of I2. The other four were closed by `GMI_CONCEPT_FORMATION_TRIGGER_V1.md`.

## 1. Prototype, exemplar and rule are realizations, not rival theories

A concept is a retained equivalence class. Storing one admits three realizations, and they are exactly
this corpus's carrier classes:

| realization | carrier | cost |
|---|---|---|
| **exemplar** — keep every member | `TABLE` / `KVSTORE` | ∝ class size |
| **prototype** — keep a representative and a metric | `DENSE` | constant |
| **rule** — keep a membership predicate | `PROGRAM` | ∝ description length |

Swept over class size × description length:

| class size \ description length | 1 | 3 | 12 |
|---:|---|---|---|
| 1 | exemplar | exemplar | exemplar |
| 2 | **rule** | exemplar | exemplar |
| 5 | **rule** | **prototype** | **prototype** |
| 20 | **rule** | **prototype** | **prototype** |

**All three win somewhere; none dominates.** Exemplar for tiny classes, rule where the predicate is
short, prototype where the class is large and no short rule exists. They are alternative realizations of
one object, selected by the same charged accounting that selects everything else here — which is the claim
I2 asks for, and it explains why the corpus's carrier classes are what they are rather than an arbitrary
list.

## 2. Granularity — the naive reading, and why it is wrong

The expected result was "tighter resources → coarser concepts". A first sweep appeared to confirm it,
optimal granularity falling 8 → 6 → 4 → 2 → 1 as the budget tightened.

**That sweep was degenerate.** Merge-error cost (3.0) exceeded storage cost (1.0) throughout, so the
optimum was always *the finest the budget allowed*. The budget was binding; nothing was being traded.

Sweeping the ratio instead, with a budget generous enough never to bind:

| merge error / storage | cost by `k` | optimal `k` |
|---:|---|---:|
| 0.25 | 2.8, 3.5, 4.2, 5.0, 5.8, 6.5, 7.2, 8.0 | **1** |
| 0.5 | 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0 | **1** |
| 1.0 | 8.0 at every `k` | indifferent |
| 2.0 | 15, 14, 13, 12, 11, 10, 9, 8 | **8** |
| 3.0 | 22, 20, 18, 16, 14, 12, 10, 8 | **8** |

Total cost is **linear in `k`** with slope `(storage − error)`, so:

> **Granularity is bang-bang at `error = storage`.** Below the threshold a *single* concept is optimal;
> above it, *maximal* granularity is optimal, capped by the budget. **Under linear costs there is no
> interior optimum.**

## 3. What that corrects

Resources do **not** set granularity directly. The **ratio** of merge-error cost to storage cost does, and
the budget only enters in the fine regime, where it caps how fine you may go. The first sweep looked like
a smooth resource law only because it sat entirely on one side of the threshold.

A genuinely graded granularity would require **nonlinear** error or storage — for instance error growing
faster than linearly in merges, or storage with economies of scale. That is a concrete prediction about
what any smoothly-graded concept system must contain, and it is testable.

## 4. Scope

**Derived:** the three realizations as cost-selected alternatives, and the bang-bang granularity law with
its threshold.

**Assumptions:** additive per-class storage, error linear in the number of merges, and a fixed number of
underlying distinctions. All three are exactly what the bang-bang result depends on, and §3 says what
relaxing them would buy.

**Falsifier:** an interior optimum under linear costs, or a class size and description length where none of
the three realizations is cheapest.

## 5. I2 status — all six boxes

| box | where |
|---|---|
| concept as an architecture-independent object | trigger document — a retained equivalence class |
| category boundary from obligation-equivalence, not labels | trigger document — verified exactly |
| when examples collapse into one concept | trigger document — same response-equivalence class |
| when distinctions must remain separate | trigger document — different class |
| **prototype / exemplar / rule as alternative realizations** | **here** |
| **granularity from ecology/resource pressure** | **here** — and it is a ratio law, not a resource law |
