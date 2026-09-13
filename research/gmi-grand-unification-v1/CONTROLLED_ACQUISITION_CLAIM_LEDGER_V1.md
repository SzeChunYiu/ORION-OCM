# Controlled acquisition claim ledger V1

Date: 2026-09-13. Additive; no earlier acquisition evidence is overwritten.

| ID | Claim | Status | Scope |
|---|---|---|---|
| CA-1 | Compatible `(world,current-state)` pair sets are sufficient information states for future robust acquisition when future legality/dynamics/cost/success depend only on the current pair and chosen operation. | THEOREM | finite deterministic Markov controlled acquisition |
| CA-2 | The robust Bellman recursion over pair information states equals optimization over arbitrary finite history-dependent policies. | THEOREM + EXACT | finite horizon, scalar nonnegative test cost |
| CA-3 | Candidate-world support alone is insufficient when experiments change state or future legality. | COUNTEREXAMPLE + EXACT | destructive probe witness |
| CA-4 | A state-changing operation can make the obligation compatible without reducing world uncertainty. | CONSTRUCTIVE EXACT | set-valued terminal actions |
| CA-5 | Every path-dependent resource that affects future feasibility/value must be included in the controlled state unless already represented physically. | NECESSITY COUNTEREXAMPLE | finite budget witness |
| CA-6 | Support-set recursion is not promoted to expected-risk stochastic acquisition; belief/statistical state is required under the appropriate stochastic parent theory. | BOUNDARY | stochastic extension open in prior-free multi-ecology form |

Exact evidence:

- `390625/390625` two-world/two-state/two-test kernels: pair-state DP equals explicit history-tree optimum at horizon two;
- result distribution: `210000` value-1, `60944` value-2, `119681` infeasible;
- destructive state witness: same world support, fresh value `1`, burned value `INF`;
- control-to-compatibility witness: world support unchanged, terminal compatibility created in one step;
- remaining-budget witness: same pair set, budget 1 feasible, budget 0 infeasible.

Terminal:

`CONTROLLED_STATEFUL_ACQUISITION_CLOSED_AT_FINITE_DETERMINISTIC_ROBUST_SCOPE = TRUE`.

Novelty status under `NOVELTY_PARENT_SUBTRACTION_V1.md`: parent-assisted synthesis. POMDP belief/information-state planning and decision-region/equivalence-class acquisition are explicit parents; no priority claim is made for dynamic programming itself.
