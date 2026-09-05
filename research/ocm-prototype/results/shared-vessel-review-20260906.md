# Shared-vessel pilot — independent source review

Read-only review on laptop billy, 2026-09-06. Checkout `/home/billy/orion-director-work/20260906/ocm-vessel`, branch `codex/ocm-shared-vessel-pilot-20260906`, baseline HEAD `366c203e2872938f282c26df1af8984fed9cbe7d`. Six new files under `research/ocm-prototype/`; source changed during first integration run. No tests, commits or issue writes by this reviewer.

## Supported by source inspection

- `vessel_pilot.query` supplies language, guided polynomial and primitive polynomial descriptors on every query, then calls existing `OCMRuntime.solve`, which invokes unchanged `SV.solve`.
- All capability roots are offered; expected held-out meanings/programs are not passed to the controller. Polynomial coefficients are legitimate target specifications.
- Learned payloads contain word/slot/fragment data. Fixed host callbacks interpret those records; no learned Python or checker selector is executed.
- The shared solver's committed result is independently rechecked before answer admission. Liveness and scope are rechecked at that boundary.
- Polynomial proof support depends on the trusted primitive semantics and query, not on the revocable heuristic that found the solution. Primitive fallback after generator withdrawal is correct.
- Direct language reference interpretation and complete polynomial catalogue construction are actually executed outside `SV.solve`; these establish tiny capability only.
- Dense navigation, repeated hashing, source binding, process reload and storage are disclosed. Per-stage counts are proxy measurements; the outer envelope records elapsed/CPU time.

This supports the narrow claim `COMMON_LOOP_SUPPORTED_AT_TINY_REGISTERED_SCOPE` once its actual checks pass. It does not show that the executive itself learned a general policy: whole parsing/search routines remain credited domain operators. No protected comparison, sparse execution or LLM parity is established.

## Findings sent to implementation owner

1. **Stale test assertion:** initial `test_shared_vessel.py:61` expected `independently_executed is False`, contradicting the actual direct parent implementation. Expect True and require `shared_solver_invoked is False`.
2. **Parent gate omits correctness:** initial `vessel_study.py:95` checks only 341 enumerated programs. Require successful exact polynomial check and expected language digest, as well as genuine independent execution. Add an aggregate `receipt.passed` regression assertion so new receipt controls are not silently omitted by the test suite.
3. **Missing scope negative control:** registration includes out-of-scope proposals, but initial pilot lacks the control. A host fault replacing all descriptor scopes with a foreign scope should yield no admission and a commitment refusal.
4. **Wrong injection scope label:** the initial `checker_injection` control inserts a forbidden field into query input, not learned state. Rename its assertion accordingly, or test actual malformed learned-state schema. Do not claim the existing input test proves persisted-payload rejection.
5. **Prior byte metric overstates its coverage:** initial `domain_prior_bytes` includes only `vessel_state.py` and `vessel_ops.py`, while templates/DSL/parser implementations are imported. Rename it to adapter-source bytes and disclose imported source separately, or count an explicit complete donor/implementation manifest. The host fixture digest list is a source binding, not complete transitive constitutional isolation.
6. **Stale-answer lifecycle oracle:** initial language withdrawal check tests only refusal of a new admission. Record old answer liveness after first and last grammar support withdrawal: first remains LIVE; last does not. Mathematical retained truth already has the corresponding old-answer check.

These are bounded fixes to the existing pilot; none requires a new framework or production-runtime rewrite.

## Scope limitations to retain

- Current language object aggregates all six lexical lesson supports; no within-language lexical-locality result is tested.
- The pilot teaches before the scored queries. Its setup invokes existing learners, but this packet alone has no before-teaching/after-teaching acquisition contrast.
- Scope is one trusted host. File hashes and MappingProxyType do not isolate arbitrary malicious Python operators.
- The polynomial grammar is finite and its current length-four parent completely enumerates 341 syntactic programs. Parent sufficiency at that scope is expected to remain an admissible result.

## Stable-source reread

All six findings are resolved in the source reread. Parent correctness and independent execution now participate in the aggregate gate; wrong scope is an executed host fault; the query injection assertion is correctly named; old language-answer liveness is checked after first/last withdrawal; prior coverage is labelled and incomplete dependency accounting is explicit. The new empty-custody guard prevents silently reusing an old study world.

Reviewed SHA-256 bindings:
- `vessel_ops.py`: `537a13bc7a0dcae81976affc7fa2c19dda980634040ec5d230f4efb07080db58`
- `vessel_study.py`: `cf18372e118b2004a627cd178973f70eb30b2f802bc8902ffe3f19187b78b773`
- `vessel_pilot.py`: `9b101ee80286beac45b498f27e801147234632e8de5bcb16922c1f6b53129459`
- `test_shared_vessel.py`: `09c93a35fed3ea142fcc5bd22328dac021063cfd53b4f2c3fd13d84b144c0745`
- `vessel_state.py`: `2b7e6e5809caa8de2813b3f08bb48fbd88f8140aacae678aace36f6a959cb444`
- `vessel_parents.py`: `cb06e286f7a07e2440cb9ea1fa52e21a253b0701eea5cae453a8f692321eff08`

Review outcome: no unresolved blocking source finding within the tiny trusted-host integration scope. Root owns final laptop execution and publication. This review did not independently run tests and does not assert their results.
