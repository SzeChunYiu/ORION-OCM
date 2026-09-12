# RV-377-109 — FREEZE: is the grammar axis verdict-inert, or merely under-resourced?

Frozen BEFORE the run. Outcomes appended only.

## The gap

`DG-11`, opened by `RV-377-107`: all three K4 grammars — typed tensor dataflow
(`G1`), register machine (`G2`), FSM message passing (`G3`) — agreed on the verdict
for **88 of 88** family × cell combos, while changing every numeric quantity on
every combo where it is defined (search winner cost 0/76 identical, null cost 0/24,
null-vs-witness margin 0/24). They do arithmetic work and no adjudicative work.

If that holds, the 3× grammar replication supplies no independent evidence, the
effective K4 sample is 88 rather than 264, and the freeze's
`grammar_independence_note` overstates what the axis buys.

The obvious alternative explanation is **budget**: at 20 000 evaluations the search
may be too starved for grammar differences to express themselves in a verdict. This
run tests that directly.

## Design

Identical grid — 22 families × 3 grammars × 4 cells = 264 cells — at **budget
200 000, a 10× increase**, same development seed `0x4B345035`. Measured cost:
16.47 s/cell at 200 000 against 1.63 s at 20 000 (linear), ≈ 18 min at 4-way
parallelism.

Still development scope. Still **not protected evidence**: the frozen `green_rule`
requires ≥ 10⁶ scored candidates and this is 0.2 × 10⁶.

## Frozen predictions

| id | prediction | falsifier |
|----|-----------|-----------|
| S1 | **The grammars still agree on 88/88 combos.** Grammar is verdict-inert, not budget-starved. | any combo where two grammars disagree |
| S2 | **GREEN stays 0 of 264.** | any green cell |
| S3 | `THEORY_RED_NULL_DOMINATES` **falls below 69** — 10× more search should find developed witnesses cheaper than the inert nulls on some cells. | ≥ 69 null-dominated cells |
| S4 | `INCONCLUSIVE_GRAMMAR` **falls below 36** — some of `K4-A13`/`A18`/`A20` should acquire an admissible witness. | still 36 |

S1 is the DG-11 test proper. S2 is the prediction against GMI: if it holds, 10×
budget buys the K4 engine nothing at all.

S3 and S4 are the predictions that let budget-starvation *rescue* the 20 000-cell
result. If S3 and S4 both fail — if the counts do not move — then the `RV-377-107`
verdicts were not an artefact of an under-resourced search, and the K4 failure is
structural. That is the outcome most damaging to GMI and it is the one being tested
for, not around.

---

# RV-377-109 — ADJUDICATION (appended; nothing frozen above was edited)

264 cells at budget 200 000, all `OK`, zero errors. Wall 6 797 s against the
development sweep's 443 s.

## Every verdict is identical. Not one cell moved.

| verdict | 20 000 | 200 000 | Δ |
|---|---|---|---|
| `THEORY_RED` | 159 | 159 | **+0** |
| `THEORY_RED_NULL_DOMINATES` | 69 | 69 | **+0** |
| `INCONCLUSIVE_GRAMMAR` | 36 | 36 | **+0** |
| cells whose verdict changed | — | — | **0 of 264** |

| id | prediction | outcome |
|----|-----------|---------|
| S1 | grammars still agree 88/88 | **CONFIRMED** |
| S2 | GREEN stays 0 of 264 | **CONFIRMED** — 0 |
| S3 | null dominance falls below 69 | **FALSIFIED** — exactly 69 |
| S4 | `INCONCLUSIVE_GRAMMAR` falls below 36 | **FALSIFIED** — exactly 36 |

The freeze named the consequence in advance: *"If S3 and S4 both fail — if the counts do
not move — then the `RV-377-107` verdicts were not an artefact of an under-resourced
search, and the K4 failure is structural. That is the outcome most damaging to GMI and it
is the one being tested for, not around."*

**Both failed. Neither count moved by a single cell.**

## The budget was honoured — checked before concluding anything

Identical verdicts could mean the budget parameter was never plumbed through, which would
void the conclusion. It was not:

| quantity | cells differing between 20 000 and 200 000 |
|---|---|
| wall time | ratio **15.34×** against a 10× budget ratio |
| **search winner cost** | **194 of 264** |
| `null_cost` | 0 of 264 |
| `null_vs_target_witness_margin` | **0 of 264** |
| verdict, reason | 0 of 264 |

The search genuinely did ten times the work and genuinely found better candidates —
e.g. `K4-A01 | G1 | w1`, winner cost **45.92 → 37.42**.

## The mechanism, which is worse than "nothing changed"

`null_cost` is unchanged because nulls are hard-coded and budget-independent — expected.
But `margin` is `witness_cost − null_cost`, and **margin is unchanged on all 264 cells**,
so the **frozen-target witness cost did not improve on a single cell** either.

Put together:

> **Ten times the search budget made the non-target frontier materially cheaper on 194 of
> 264 cells, and moved the frozen-target witness on none of them.**

The gap between what cost-minimising search converges on and what GMI predicts it should
converge on does not close with budget. It **widens**. Extra compute is evidence against
K4, not for it — which is the opposite of the direction a budget-starvation defence needs.

This also settles the scope caveat carried by `RV-377-107`. That record listed "0 of 264
target vectors recovered" as **not** budget-robust, because more search might recover
some. At 10× it recovers none, and the witness cost does not move at all. The caveat is
discharged in the direction that hurts.

## DG-11: the grammar axis is verdict-inert, and it is not a budget artefact

88 of 88 family × cell combos agree across all three grammars at 200 000, exactly as at
20 000, while the grammars continue to produce different numbers. The budget explanation
for DG-11 is eliminated.

DG-11 stands as opened: until a cell is exhibited whose verdict differs between two
grammars, grammar is a presentation variable and not an independent probe, and the
effective K4 sample is **88**, not 264.

## Standing scope

Still development scope: 200 000 against the frozen `green_rule`'s ≥ 10⁶, and explicitly
not protected evidence. `RV-377-107`'s Q4 — that the protected beacon run reproduces
these verdicts — remains frozen and pending, and is now better supported: the verdicts
were invariant under the one order-of-magnitude change already tested.

`K4_PROPERTY_PREDICTION_GREEN_AT_REGISTERED_SCOPE` is **FALSE at development scope, and
the failure is structural rather than budgetary.**
