# Grand GMI Claim Ledger — Developmental Underdetermination V1

Status date: 2026-09-13. Additive to the Grand-GMI claim ledgers. Authority:
`DEVELOPMENTAL_UNDERDETERMINATION_THEOREM_V1.md`.

| ID | Claim | Status | Scope |
|---|---|---|---|
| DU1 | Two development laws can share the admitted realization set, profiles, family assignment and every proved necessity and still give different reachable frontiers and verdicts, so the reachable frontier is not a function of that data. | THEOREM / NO-GO | registered finite development graphs |
| DU1a | Consequently no theorem of the form "necessities imply the trained outcome" can exist; the development law is an independent registered input. | COROLLARY | derivations that do not register `D` |
| DU2 | Reachability depends on the schedule of admitted updates, not only on which updates are admitted, so registering a set of operations is not registering a development law. | THEOREM / HYPOTHESIS REQUIREMENT | non-commuting admitted updates |
| DU3a | Restricting to reachable realizations never lowers a derived lower bound, so reachability evidence is PL-4a safe and a robust exclusion survives it. | THEOREM | derived lower bounds |
| DU3b | Restricting to reachable realizations can invalidate a construction, so the verdict is not monotone under reachability and can invert while every family bound rises. | THEOREM / NO-GO | constructions and selections |
| DU4 | Where each admitted update strictly improves the profile and changes family, the budget-`B` verdict reverses at budget `B+1`, so no finite budget certifies an unbounded-development verdict. | THEOREM / NO-GO | bounded development budgets |

## Exact witness aggregate

- shared realization data `{s0: 10, a: 5, b: 3}` with global family bests `NEURAL = 5`, `NON_NEURAL = 3`; law `D1` yields family support `{NEURAL}` and law `D2` yields `{NON_NEURAL}` at budget `1`;
- admitted updates `double` and `add_three` under admission cap `6`: schedule `double->add_three` reaches `5` and is admitted, schedule `add_three->double` reaches `8` and is rejected;
- reachability asymmetry: global bests `A = 2`, `B = 5` with support `{A}`; reachable bests `A = 9`, `B = 5` with support `{B}`; both bounds rose and the verdict inverted;
- alternating chain of length `8`: frontiers `9, 8, 7, 6, 5, 4, 3, 2` with the verdict alternating at every budget and covering both families;
- no learning process is measured, analysed or predicted at any scale.

Terminal: `GRAND_GMI_DEVELOPMENTAL_UNDERDETERMINATION_GREEN_AT_FINITE_SCOPE`.
DU1 does not forbid a training theorem **given** a registered `D`; it forbids
deriving one without `D`. Registered-`D` theorems remain an open target.
