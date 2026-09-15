# Issue #602 formal verification and live-state reconciliation V1

Date: 2026-09-15. This note verifies only rows whose exact/formal antecedents are present and executable. It does not promote adjacent empirical or prospective rows. During this tranche, merged PR #694 and a repository-owned reconciliation workflow checked the detailed B14/B20/I5 rows. This tranche does not claim credit for those live checkbox mutations; it supplies the P2 selector comparison missing from B14's old annotation, independently revalidates the cited B20/I5 evidence, and closes the still-open P0 causal summary dependency.

## Newly proved in this tranche

- `[x] B14 Derive rule/rewrite operators from generic transformations.` The sound-cover theorem derives the complete selector-emitter instruction. The exact eight-input microscope compares positional, equality, and arbitrary-subset selector families and proves the matched XOR/MUX reversal by exhaustive minimum cover.

## Existing exact evidence independently cross-validated

- `[x] I5 Derive condition where observational prediction aliases causal states.` `CAUSAL_IDENTIFIABILITY_BOUNDARY_THEOREM_V1.md` gives the necessary-and-sufficient condition: a causal target is observationally identified exactly when it is constant on the nonempty compatible-model fiber `C(P)`. Aliasing is the negation: two compatible models share the complete observational law but require different causal answers. W1 is the exhibited pair and gives the worst-world exact-success bound `<= 1/2`.
- `[x] I5 Parent-subtract Pearl/SCM, active causal learning, Bayesian experimental design.` The causal boundary/rung artifacts attribute SCM and identification to Pearl/Tian-Pearl/Balke-Pearl. `EPISTEMIC_ACQUISITION_PARENT_SUBTRACTION_V1.md` explicitly assigns optimal decision trees, active causal intervention design, Bayesian experimental design, and generic active causal discovery to parent theory. The declared GMI residual is obligation-relative interface/charging and no new causal calculus is claimed.
- `[x] P0 Finish causal cognition.` This is a dependency summary, earned because every I5 row is now either already checked in #602 or reconciled immediately above. It is formal finite-scope closure only, not arbitrary-graph discovery, finite-sample causal inference, or physical intervention validation.

The existing `GMI_TOOL_ROUTING_DERIVATION_V1.md` and `STAGE_TOOL_ROUTING_V1.json` also earn two B20 rows that were not reconciled:

- `[x] B20 Derive when heterogeneous solvers dominate one monolith.` Formally, after hard-budget filtering and under a frozen price vector, a mixed assignment dominates exactly when its complete held-plus-obtained-plus-routing-plus-verification burden is below the monolith's. The exhaustive registered microscope realizes both sides: a mixture is uniquely selected in 40 of 70 worlds and the all-held machine in 30 of 70. Thus heterogeneity is conditional, not universally superior.
- `[x] B20 Derive routing cost and verification cost.` Routing is charged as retained competence-map nodes and payload probes; verification is independently charged as checking probes. In the registered tasks, the relational obligations cost one probe to check versus three to solve, while every functional obligation costs exactly as much to check as to solve. The result includes a collapse control where the competence map costs 31 nodes against one node for holding the trivial capability, so routing is not assumed free.

## Rows deliberately left open

- B20 failure-aware fallback: the existing artifact measures fallback availability and exposure but states that no recovery protocol is modelled.
- B20 verifier-gated proposal/admission: checking costs are derived, but proposal, rejection, retry, and adoption transitions are not yet a complete lifecycle.
- B20 neuro-symbolic/statistical-symbolic hybrid conditions: no matched carrier/operator comparison yet exists.
- B20 composition versus a distinct domain: the outside/inside additivity result does not satisfy the J4 domain claim gate.
- B15 DreamCoder/Stitch-like pressure: current artifacts formalize and measure library amortization, but the retained-chunk proposal operator remains supplied rather than neutrally derived from a lower grammar.
- Every held-out, real-scale, unbounded empirical, natural-cognition, and new-domain row remains open.

Live update authorized after merge and green CI:

1. replace B14's stale `PARTIAL` annotation with this P1+P2 evidence;
2. check the still-open P0 `Finish causal cognition` dependency summary;
3. do not rewrite the five detailed rows that the concurrent repository workflow already checked.

Claim ceiling: `ISSUE_602_B14_P2_AND_CAUSAL_SUMMARY_RECONCILED_AT_REGISTERED_SCOPE`.

Forbidden promotions:

```text
COMPLETE_THEORY_OF_MACHINE_INTELLIGENCE
ALL_MACHINE_INTELLIGENCE_DERIVED
UNIVERSAL_BEST_SELECTOR_LANGUAGE
UNIVERSAL_BEST_TOOL_ROUTER
CAUSAL_DISCOVERY_COMPLETE
NEW_SYMBOLIC_DOMAIN
```
