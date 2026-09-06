# Authority-indexed navigation: a small ORION-Q donor transfer

**Status: research prototype, not the production OCM controller.** Owners: OCM #72; field semantics #93; compression #70; architecture #69. Synthesis: PR #92. This is an additive executable experiment, not another top-level research lane.

## Parent ownership and the quantum connection

The adopted rule comes from [ORION #908](https://github.com/SzeChunYiu/ORION/issues/908), specifically [the original router at pinned commit 962e9d264fe24780291ca8223b8da130ebd6cea9](https://github.com/SzeChunYiu/ORION/blob/962e9d264fe24780291ca8223b8da130ebd6cea9/research/extensions/orion-q/max_r4ea_authority_indexed_router.py): **filter routes by earned authority for the requested question, then choose a cheaper eligible representation**. Its ten receipt-grounded quantum/compiler cases are historical source evidence, not newly reproduced results here.

That research found that a bulk statistic, a defect-spectrum statistic, and a detailed representation answer different questions. In particular, the 45-class and 54-class partitions were incomparable. A physically smaller representation is not automatically sufficient for a different question. The present selector transfers that *classical control principle*, not domain constants, quantum hardware, or quantum advantage.

This is standard indexed selection plus a host-checking boundary. A native indexed parent receives full ownership of that mechanism. No OCM-specific scientific residual is claimed. [ORION-V2 #205](https://github.com/SzeChunYiu/ORION-V2/issues/205) remains at `NO_ELIGIBLE_OPERATOR`; this prototype is not a reason to reopen it.

## What is implemented

`RouteIndex` builds exact query-key buckets once. Each descriptor has an identity, advertised query keys, a host-resolved contract reference, two resource estimates, and an ANSWER or REFINE kind. Supplied collections are copied into immutable tuples/frozensets; maps are read-only. There are no learned parameters and no third-party dependencies.

For each query:

1. Retrieve the exact query-key bucket; a key is a retrieval signature, **not a sufficiency certificate**.
2. Stop with `CANDIDATE_LIMIT` if the bucket exceeds the explicit candidate budget. Do not silently select from a truncated prefix and call it the best route.
3. Discard routes outside the declared **estimated** resource envelope. The actual runtime meter is still required.
4. Ask the host to resolve the route's contract against the query, context, authority kind and snapshot. Only an actual `Eligibility.APPROVED` enum participates in ranking. Missing/uncertain evidence stays UNKNOWN. A callback exception or malformed return refuses selection.
5. Select by an explicitly requested lexicographic cost policy, `work_first` or `bytes_first`, with deterministic ID ties. This is not a universal richness order, semantic ordering, Pareto-optimal architecture, or global minimum.
6. Preserve REFINE as a request for further work, never as an answered query.
7. Before execution, `preflight` checks that the query/snapshot and catalogue descriptor are unchanged and calls the host again. `READY_FOR_HOST_COMMIT_CHECK` is **not** permission to commit or perform an external action.

If an approved route exists while a cheaper route is UNKNOWN, the approved route may be selected. Minimality is only over the approved offered routes in the estimated envelope. An empty result means no approved route **in this catalogue**, never impossibility of answering the question.

## Host boundary: deliberately not reinvented

The callback is not implemented as a second OCM constitution. Its production adapter must reuse existing KSO warrant/liveness, scope, authority and checker contracts. Test callbacks are finite fixtures, not certificates of real scientific truth.

The host must bind the snapshot to the relevant field, evidence, representation, contract and checker identities; resolve the contract from an authoritative registry rather than trusting a caller's string; preserve alternative support; and pin/revalidate state atomically at execution/commit. This standalone Python module is not a security boundary against hostile code running in its process.

Preflight cannot prevent a revocation arriving *after* preflight without host transaction discipline. Global snapshot rejection is conservative: it does not prove minimal/local invalidation. Scope/formal-versus-empirical behavior is exercised through explicit fixtures; its real implementation remains an integration obligation.

## Reproduce the development checks

From the repository root, using Python 3.11 or later:

```sh
python -m unittest discover -s research/qg_routing -p 'test_*.py' -v
python research/qg_routing/run_checks.py /tmp/qg-routing-new-result.json
```

Choose a new output filename for each run; the runner refuses to overwrite evidence. The runner records source hashes and raw unit/mutation logs. These are **local development evidence**, not an official source-bound engineering receipt or a protected scientific result. No precomputed result is consumed by the tests.

The suite has 20 tests. One performs 1,944 finite index/reference comparisons: 3^4 eligibility assignments, four query keys, three estimated envelopes and two cost policies. The reference performs an independent full scan and sort. This checks indexing/selection equivalence, not the truth of host certificates. A deliberate mutant that skips REJECTED eligibility is separately run; five tests reject that mutant in the authoring run.

Controls include unknown versus rejected, formal versus empirical authority, context changes, alternate-support withdrawal/restoration, stale snapshots, replaced contracts, checker failure, immutable descriptor inputs, incomparable summaries, explicit cost trade-offs, refinement and candidate-limit handling.

The growth diagnostic builds catalogues with 2, 102 and 10,002 descriptors. The registered query inspects two candidates in each. Index references built grow to 2, 102 and 10,002. This is expected database-style indexing behavior, **not** an OCM cognition, total-memory or whole-lifetime speedup result. It does not compare with an LLM.

## Resource boundaries

Let N be catalogue size, I the number of query-key incidences, and k the requested bucket size. Construction visits N routes and I incidences; deterministic sorting of each route's keys has its own cost. Retained index storage is O(N + I) references plus maps/key storage. Query selection visits k descriptors and invokes at most k host checks; expected dictionary lookup costs assume ordinary fixed-size keys. The host checks may themselves do global work and must be profiled separately. Catalogues with every route sharing one key still have k = N.

Index replacement currently rebuilds the index. No packed physical field, incremental index maintenance, compressed support store, selective evidence invalidation, or learned method induction is implemented here. Resource estimates are supplied data, not measured backend cost. Performance on the actual OCM path remains untested.

## Integration checklist: keep under #72 / #93, not a new programme

- [x] Inspect the existing #908 algorithm and current #92/#93 direction; preserve parent ownership.
- [x] Implement the small indexed selector and independent finite full-scan reference.
- [x] Run 20 development tests, 1,944 comparisons and a planted unsafe-eligibility mutant.
- [x] Count catalogue construction separately from candidate visits; demonstrate an unrelated-growth control.
- [ ] Bind the callback to actual OCM registry, warrant, scope and authority objects without hand-authored outcome labels.
- [ ] Demonstrate host-pinned snapshot and atomic commit/revocation behavior; keep REFINE separate from answers.
- [ ] Replay frozen #908 receipts through a separately reviewed adapter, with all source bindings and original scope intact.
- [ ] Test one formal-math and one non-math task using the same controller; independently grade semantic correspondence.
- [ ] Include same-summary/different-answer counterexamples and changes to supported intervention/revocation families.
- [ ] Measure full path: query formation, contract resolution, index build/maintenance, evidence reads, checker/backend work, retention and revision costs.
- [ ] Compare to native indexed authority routing, native always-rich and unsafe-cheapest controls; then the strongest same-tool LLM system under #73.
- [ ] Freeze new task/scale/resource identities before protected runs; do not retune this exposed development fixture into a headline result.
- [ ] Obtain independent review and repository integration qualification before any production adoption.

## Science and quantum boundaries

A formal result proves a statement under its definitions, assumptions and trusted checker. It does not certify that an empirical model describes nature, that a drug will work, or that a hardware abstraction captures every physical behavior. FORMAL and EMPIRICAL must remain distinct host authority coordinates.

A physical quantum operator is a separate optional backend. It needs a concrete common access model and an end-to-end accounting of classical preprocessing, state preparation, oracle construction, quantum execution/repetitions, readout, error handling and verification. A query-count advantage alone is not an OCM lifetime advantage. Classical sampling, compression and symmetry techniques inspired by quantum research may be adopted without making a quantum-computation claim.

The useful experiment is whether a governed machine can avoid unnecessarily rich state **while retaining the distinctions required by each query and later revision**. The selector is one testable piece, not evidence that the whole hypothesis already holds.
