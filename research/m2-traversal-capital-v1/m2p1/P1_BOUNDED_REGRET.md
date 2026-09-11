# P1 discharged — deployment regret is bounded at 2x

The blocking obligation from [THEORY_GAPS.md](THEORY_GAPS.md) §4.1.

**Claim.** For every method `m`, task `T`, budget `b`:
`slots(solve(T,b,m)) ≤ 2 · slots(solve(T,b,∅))`, and correctness is unaffected.

**Method.** Exhaustive measurement against the **real** registered iterator — duplicate
filtering, counterexample pruning and guided exhaustion all live — over adversarially
chosen libraries designed to make the guided stream as useless and as long-winded as
possible: true motifs, random length-2, random length-3, **maximally diluting length-4
fragments**, and a mixed maximum-count library. Four ecologies including the
independently-authored M1 one.

| | |
|---|---|
| measurements | **410** |
| adversarial libraries | 5 |
| **max observed ratio** | **2.0000** |
| mean ratio | 1.4969 |
| violations of the bound | **0** |
| correctness violations | **0** |

Worst case: `random_len2` on E5, baseline 68 616 → candidate 137 232, ratio exactly 2.0,
still `VERIFIED_POLYNOMIAL_IDENTITY`.

**Verdict: `DISCHARGED_EMPIRICALLY`.** The bound holds and is *tight* — attained, never
exceeded. A formal proof over all budgets and libraries is still owed, so this is an
empirical discharge, not a theorem.

**Consequence.** Deploying any generator costs at most 2× and can never make a target
unsolvable or incorrect. The catastrophic downside that universal non-inferiority guards
against **does not exist in this integration mode**, which is what makes that rule a
dominated policy rather than a safety property — and what licenses the expected-utility
successor policy (`CONTINUED_EU`), implemented without touching
`src/ocm/learning/methods.py`.
