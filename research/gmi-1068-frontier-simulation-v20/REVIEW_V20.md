# V20 independent scientific and executable review

Reviewer authored the paper derivations but did not implement production or the
independent oracle. This is an independent implementation review, not a second
independent paper authorship. Formal proof review is recorded separately.

## Actual implementation inspected

Read core_v20, frontier_v20, maps_v20, simulation_v20 and bridge_v20.
Finite Max is an actual filter over the supplied attained values and all declared
preorder comparisons. It retains every equivalent maximal value. The representative
scan then chooses the first encountered member of each maximal equivalence class;
its output is presentation-relative. attained filters the actual selected V15
histories by admission and evaluator definedness before forming the value image.

Map guardedness explicitly checks that an ordered upper input remains defined
whenever its lower input was defined, and compares their actual outputs.
postcompose accepts arbitrary well-typed partial maps; it changes E by successful
Option output and leaves P intact, including illegal ambient evaluations.
Construction itself does not incorrectly require monotonicity. That hypothesis
is checked separately when using the pruning theorem.

The finite Machine admits empty state and action sets. refine deletes pairs
synchronously from the preceding relation and reports both deleted pairs and
the final stability check. is_simulation accepts general candidate relations,
not only preorders, which is appropriate for the greatest-relation definition.
run and endpoints validate all action symbols before executing, even with no
starting endpoints or with a prefix that later fails. Set inputs reject duplicate
indices and Boolean/integer aliases before indexing or deduplication.

## Endpoint-value bridge premise diagnosed and incorporated

During derivation, state simulation alone was found insufficient for transporting
an arbitrary partial endpoint Context: a dominating state can have undefined or
worse evaluation. The correction is the existing T2 guard on the actual active
map x↦some(ν(x)) on P∩E, otherwise None. This is an exposed application
premise, not a weakening of the frozen state-simulation theorem.

Production valued_endpoints now requires that guard against machine.base and
the Context order; from_v8 takes an explicit base order and the actual existing
budget_lift. The bridge reads the lift's real destinations and retains residual
budget. It does not synthesize an order on unknown values or claim full EDGE
trace equality. The premise was independently exercised with both valid and
invalid endpoint contexts below.

## Independently executed bounded probes

All probes ran on billy-laptop using Python 3.12 normally and with -O.
They used explicit failure checks; serialized counts were identical.
A fixed seed 106820 chose bounded examples beyond the primary size-three corpus.

| Actual supplementary check | Count |
| --- | ---: |
| Four/five-state deterministic machines | 12 |
| Independently enumerated candidate simulation relations | 2,210 |
| Valid candidates in that enumeration | 24 |
| Word/pruning comparisons through length six | 1,524 |
| Actual partial contexts | 60 |
| Actual postcomposition outcome-tag checks | 174 |
| Cofinal-subset/cardinality comparisons | 90 |
| V8 lifted destination checks | 40 |
| Valid guarded endpoint-value comparisons | 20 |
| Undefined/nonmonotone endpoint-guard rejections | 8 |
| Invalid suffix rejections after a failed prefix | 7 |
| Endpoint-equivalent but full-trace-different control | 1 |

For the simulation probes, expected G was the union of independently enumerated
relations satisfying the simulation clause, not another descending-refinement
implementation. Restricting that enumeration to relations containing the diagonal
is sound: any simulation can be unioned with the diagonal, and the greatest
simulation contains it. Every production greatest relation matched that union.
The resource probe used original edge costs 0,1,2 and maximum budgets 0–3.
A separate two-state example had identical endpoint behavior and different EDGE
outputs, confirming the declared distinction from V8 full-trace equivalence.
These supplementary counts are not added to the primary receipt's exhaustive
counts. This review did not rerun the full primary corpus.

## Independent oracle and scope audit

Read oracle_v20, test_frontiers_v20, test_maps_v20, test_simulation_v20,
test_bridge_v20 and test_controls_v20.
The frontier oracle enumerates cofinal covers and derives its maximal set as the
union of minimum covers; it does not call production's maximal filter.
Map tests compare the guarded predicate with actual downward-image equality
for every registered cofinal subset, making the characterization more than two
copies of the same guard predicate. Context tests use actual P/E assignments
and selectors, not only constructor names or fixed illustrative examples.

The simulation oracle uses breadth-first search on ordered state pairs to find
actual distinguishing words. Tests check that each word witnesses left success
and right failure or a base-order violation, and compare deletion depth with
refinement steps. They verify actual pruned endpoint equations, and independently
enumerate candidate relations on the smallest carriers. Finite algorithm and
representative cardinality results remain distinct from whatever general Lean
statements are registered. Counters increment inside real loops; canonical
receipt and exact-coverage validation belong to the integrated driver.

Read check_frontier_v20 and custody_v20. The driver requires the paper detail
files, binds the exact original R3-004 title and carries only its scoped closure.
Custody verifies the preregistration-only tree and ancestry, every frozen input,
and the contents of inherited V19/V16 receipts. Qualified records remain the two
immutable V16 readings. Missing inputs are distinct from checked-invalid evidence.
The actual successor CORE and RECONCILIATION were also read: they retain R3
stale, close only 004 and report 21/201 original records, with the two qualified
readings separately leaving 199 active unresolved. Current counts must be
derived by the successor snapshot, not copied from a historical receipt. No extra original closure or new amendment is justified here.

No defect was found in the reviewed production or the bounded probes after the
endpoint-value guard was incorporated. This conclusion does not replace the
final typed-kernel replay, source-valid mutation guards or integrated receipt.
