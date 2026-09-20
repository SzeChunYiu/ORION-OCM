# Recursive scope audit: issue #1068

This audit inspected historical base `580b5ab8f4b92ee69c77d5c375d6fe656223459d`
and R4-S1 head `7736dca517f9d72ec17580168db99ef987bc5abc`. During the audit,
remote main advanced to `f86b327c16aa8aa8ebd6906fede36a362c7bd6ef`, merging R4-S1.
The snapshot records that merge without treating it as independent scientific
closure. R13 evidence adjudication #1092 was already merged at the original base;
R14 #1093 was open. Issue #833 remains historical evidence, not the control plane.

## What the new gate establishes

The gate validates the canonical R0–R17 DAG, the 205 stable original atomic IDs
plus the 17 additive R17 IDs, actual artifact content hashes, explicit evidence
locators, recursively bound parent evidence, and scope/status consistency. It
rejects an EARNED round with any unresolved atom or unearned parent. A changed
parent receipt invalidates unreconciled dependent receipts, including transitive
descendants. The output displays the derived stale closure without rewriting
historical evidence.

All 222 requirements remain unresolved in this successor audit ledger. For R0–R3,
UNKNOWN means independent atom-by-atom successor adjudication was not performed;
it does not retract every historical result. Historical initial atom statuses
remain NOT_STARTED in a separate field and are not confused with current audit
status. A verified local repair can be recorded without earning its entire round.
R5 has such a repair; no complete round is newly certified by this gate.

A hash proves content identity. A proof/witness locator proves that a named
object exists. Neither proves the scientific claim attributed to that object.
Adjudication and checker code are reviewer-trusted inputs. Simultaneously forging
a checker, its tests, all records and their hashes is outside this integrity
threat model; no claim is made to solve that trust problem. The tests explicitly
include a synthetic locator-valid closure fixture to expose this boundary.
The gate always emits `overall_closure: OPEN` and
`scientific_truth_certified: false`.

## R4-S1 audit

The Lean definitions distinguish ILLEGAL, evaluator UNDEFINED and VALUE. Equality
of all registered responses is an equivalence relation. Continuation congruence
is proved only when the test family has the stated precomposition compatibility.
The representation-separation lemma assumes a correct decoder and correctly
concludes that distinguishable histories need distinct representations.
Lean 4.19.0 accepted the unmodified successor file with
`-DwarningAsError=true` in the independent audit directory.

The normal and optimized Python routes and the separately executed finite oracle
agree: six histories, four tests, five full-response classes, four classes after
collapsing illegal/undefined, 203 representation partitions, exactly two sufficient
partitions, and one coarsest five-block sufficient partition. This is a finite
fixture result. It is not universal finite-state minimality.

Full R4-S1 acceptance still has concrete verification debt:

- Predictive sufficiency in both countermodels is returned as a literal Boolean,
  rather than calculated from joint or conditional probability tables. The
  mathematical examples are valid; the executable does not independently test
  that part of its claim.
- The claimed 12 hostile checks include positive census assertions and repeated
  conditions. That number does not mean 12 independent adversarial mutations.
- UNDEFINED is a semantic partial-evaluator case, not an algorithm for deciding
  nontermination. Executable unbounded evaluation needs a separate unknown or
  timeout state unless termination has been proved.
- Equivalence preserves only registered observations. Resource preservation and
  action-conditioned control sufficiency require those observations/conditions.

A successful theorem proof does not remove these executable-witness boundaries.
The narrow Lean theorems are retained; whole-round closure remains OPEN.

## Governance V2 audit and repaired failure modes

Isolated review of governance head `5be912733b8c5e24299827b26d4758a8d14f0942`
reproduced these accepted mutations despite its baseline tests passing:

1. Every round could be marked EARNED with `evidence: ["forged"]` while every R17
   atomic row remained NOT_STARTED.
2. Deleting every dependency edge permitted an otherwise forbidden R5 promotion.
3. A missing or unreadable supplied base silently disabled the historical gate.
4. The actual `gmi-1068-grand-unified-v2-r0` path did not identify R0 as changed.
5. Status-only promotions had no proof/receipt binding, and changed parent
   artifacts had no content-hash invalidation semantics.

The additive V3 gate rejects these mutation classes under its declared trust
boundary. Its 25 tests also cover missing files, wrong hashes, missing/forged
locators, deleted atoms, closed atoms without evidence, unresolved-parent closure,
changed-parent descendant review, unsafe paths, global promotion, missing custody
mode, and local repair without full closure. Tests pass with Python `-I -B` and
`-I -O -B`; the gate does not depend on removable `assert` statements.

## R5 local repair review

The successor Lean proofs use actual minimizing witnesses, nonnegative natural
costs, a zero-cost identity, composition and subadditivity. They do not assume the
identity/triangle conclusion. Minimal-element transport uses an order-reflecting
surjection and correctly proves the preorder result. The real-infimum extension
and infinite Pareto existence/nonattainment statements are paper proofs and are
explicitly outside this Lean bundle.

The finite check compares Floyd–Warshall against enumeration of simple paths for
all 4096 directed three-node nonnegative graphs, checks actual node relabeling,
and rejects a changed-cost control. The scalarization control computes actual
dot products for a dominated pair under a zero-weight coordinate. The infinite
`1/n` claim rests on the analytic descent argument, not the first 100 samples.
No physical resource model or complete R4 dependency is certified by this repair.

## Remaining round boundaries

| Rounds | Current successor audit status | Remaining boundary |
|---|---|---|
| R0–R3 | UNKNOWN | Historical results retained; full successor atomic audit unperformed. R1 erasure witnesses are presentation-relative; R2 non-uniqueness does not prove a primitive-symbol count. |
| R4 | OPEN | Conditional semantics valid; computed probability witnesses and adequacy review remain. |
| R5 | STALE with local repair | Corrected resource subtheorems do not earn the entire dependency chain. |
| R6–R10 | STALE | Operational genesis, family recovery, architecture leakage, and update/information reductions require successor evidence. |
| R11–R12 | STALE | Task-aware controlled-state semantics and exact theorem/premise/witness crosswalks remain. |
| R13 | STALE, historical adjudication merged | New empirical performance and corrected parent chain have not been earned. |
| R14 | OPEN | Prior and irreducibility audit remains. |
| R15–R16 | NOT_STARTED | Integrated simplification and publication claims need earned dependencies. |
| R17 | OPEN | Final atomic/ownership/empirical/hostile audit remains. |

## Reproduction and baseline custody

For the independently verified first introduction only:

```sh
python3 -I -B research/gmi-1068-recursive-audit-v3/gate.py --initial-introduction
python3 -I -B research/gmi-1068-recursive-audit-v3/test_gate.py
python3 -I -O -B research/gmi-1068-recursive-audit-v3/test_gate.py
```

Subsequent changes must use `--baseline BASE_SNAPSHOT.json --changed-files FILE`.
Both inputs are required together; missing input fails closed. CI must retrieve
that baseline from the trusted target base, derive changed paths from git, and
verify that `--initial-introduction` is used only when the target base has no prior
snapshot. The CLI does not independently authenticate a caller-supplied git ref.
Changing repair artifacts requires refreshing their file hashes and all affected
parent bindings; it never justifies marking unresolved atoms CLOSED.
