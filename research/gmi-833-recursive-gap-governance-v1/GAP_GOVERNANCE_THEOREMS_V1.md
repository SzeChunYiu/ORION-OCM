# #833 recursive gap governance v1

Parent: #833. Child: #839. Dependency: merged #838/#837 foundation.

## 1. Result record

Every theorem, proof, or experiment-result record uses the same mandatory scientific ledger: ordered quantifiers and declared domain; assumptions and dependency ids; proof/evidence mode, evidence level and maturity level; falsifiers/counterexamples; strongest parent/subsumption candidates; prior disclosure; explicit forbidden extrapolations; unresolved `OPEN_GAP` ids; scientific closure state; distinct `representable` / `reachable` and `optimal` / `selected` fields; causal-claim/identification metadata; and counterexample-generation methods.

A flagship record must register at least two distinct counterexample methods before it can be admitted by this schema. `HOSTILE_CLOSED` also requires two methods. This is a **requirement**, not evidence that two independent hostile reviews have already happened.

## 2. Experiment ledger

Every experiment ledger separately declares hypothesis/search space, cost/resource model, evaluation rule, sampling-bias audit, leakage audit, negative controls and whether outcomes were seen before the freeze. `outcomes_seen_before_freeze` must be exactly false for prospective evidence.

## 3. Gap graph

Let `G=(V,E)` be the registered directed graph of gap records, with parent-to-descendant edges. Each gap records severity, status, premise, inference, unresolved assumption, possible counterexample, owner role, evidence required, introduced assumptions and counterexample methods.

The validator reports, rather than hides, missing descendant nodes, missing roots, orphans not declared as roots, and directed cycles. Cycles invalidate this closure-DAG contract until the dependency is refactored or an explicit joint-obligation node is registered; no cycle is silently collapsed.

### G-1 — critical-descendant closure blocker

For a result `R` with registered open-gap roots `O(R)`, let `Desc(O(R))` be their transitive descendants. If any `g` in `O(R) ∪ Desc(O(R))` has severity `CRITICAL` and status `OPEN`, promotion of `R` to a closed scientific state is rejected. This follows from the registered semantics of `CRITICAL`: the unresolved gap can reverse the claim, invalidate a core premise/quantifier, or reveal circularity/leakage. The executable hostile contains a root gap with an open critical child and verifies refusal with `CRITICAL_DESCENDANT_OPEN`.

## 4. Logic-category guards

The validator forces machine-readable distinctions whose conflation commonly invalidates reasoning: ordered quantifiers are mandatory; necessity/sufficiency/IFF are distinct; a claimed converse requires a registered necessity/IFF relation; finite-exhaustive evidence cannot use unrestricted-universal wording; `representable` and `reachable` are separate; `optimal` and `selected` are separate; and a causal claim requires a registered intervention/randomized/identified-quasi-experiment/deductive route.

Corpus-wide search for every historical quantifier, converse, stationarity, identifiability or encoding error is **not** claimed by this package; that remains a corpus-audit descendant.

## 5. Standard recursive research loop

The registered iteration order is:

`formalize -> parent_search -> derive -> counterexample_search -> repair_or_downgrade -> architecture_prior_audit -> independent_implementation -> frozen_prediction -> replication -> real_scale_test -> new_gap_extraction`.

Every iteration emits explicit `new_gap_ids` and `new_assumptions`, even when the lists are empty after a bounded search. Silent assumption edits are invalid.

If a result fails, the record must retain failure evidence and state a theory update. If a strongest parent subsumes the result, the iteration must record parent-mathematics absorption and movement of the novelty claim upward. If multiple theories remain observationally compatible, the iteration must either register an identifiable discriminating experiment or name the exact scope at which they remain observationally indistinguishable.

An iteration may stop only with an explicit evidence ceiling and stop reason. This makes “we stopped because the checklist was long” non-admissible.

## 6. Closure states

Scientific state names are exactly `OPEN`, `LOCALLY_CLOSED`, `HOSTILE_CLOSED`, `REPLICATED_CLOSED`, `REAL_SCALE_CLOSED`. Bare `CLOSED` is rejected. These labels are evidence states, not deletion/history-erasure states.

## 7. Parent / novelty boundary

The graph/assurance pattern is parent-owned by proof-obligation graphs, assurance cases, requirements traceability, theorem dependency graphs and ordinary scientific falsification/replication practice. The #833 residual is the explicit machine-readable contract tying those ideas to GMI claim levels, prior disclosure, hostile methods and recursive gap extraction.

## 8. Claim ceiling

`GMI_833_RECURSIVE_GAP_GOVERNANCE_V1_AT_DECLARED_SCOPE`

Not claimed: all gaps exhausted, corpus audit complete, independent hostile review complete, SMT/model-checking completion, proof-assistant formalization, replicated closure, real-scale closure, or complete GMI.
