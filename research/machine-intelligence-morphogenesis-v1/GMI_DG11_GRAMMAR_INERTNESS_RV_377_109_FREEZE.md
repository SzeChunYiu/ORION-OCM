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
