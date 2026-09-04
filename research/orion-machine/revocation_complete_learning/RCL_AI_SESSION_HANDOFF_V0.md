# RCL AI-session handoff V0

**Date:** 2026-09-03  
**Branch:** `research/ocm-revocation-complete-learning-20260903`  
**Base:** `7ae422075a782cbee743fe0eaac176c81dbab08b`  
**Issues:** #194 / #197  
**Protected outcomes accessed:** NO

## Completed in this tranche

- formal minimal-warrant profiles, revocation signatures, CWC, and Revocation-Shattering Dimension;
- hand proofs RCL-0, RCL-1, RCL-1b, RCL-1c, RCL-1d, RCL-2, RCL-2a, RCL-2b, RCL-3, RCL-4, RCL-5, and RCL-6;
- exact finite oracle and 16 unit tests;
- 65,536 candidate-family scan, 168 antichains, and 168 distinct signatures at `n=4`;
- 2,688/2,688 agreement between independent liveness formulations;
- 1,253 proper positive-only subtranscripts, each with a distinguishing revocation;
- fixed-current-proof shattering checks through `n=5`, where 512 profiles share one proof and realize all 9 future bits;
- every integer storage/query split on the exact finite frontier;
- two-skill direct-sum check with 1,024 joint profiles and 10 independent revision bits;
- rank/unrank checks for 44 one-warrant `(n,d)` cases through `n=8`;
- live planted over-retraction, no-alarm, and mutation controls;
- material contractions for computational traces, hidden-hypergraph learning, exact/ticketed/system-aware unlearning, provenance, dynamic computation, authority revocation, and provenance-to-forget-set systems.

## Strongest honest theorem

Let `C_n = binom(n, floor(n/2))`. There is a family of warrant profiles in which every skill has the same current semantics and the same valid current proof, but the family shatters `C_n-1` future revocation decisions. Consequently:

```text
zero-query retained information >= C_n - 1 bits
coordinate-query full-audit frontier: S + Q >= C_n - 1
m independent skills: S + Q >= m(C_n - 1)
```

Matching constructions attain equality in the registered coordinate-query model.

These are elementary all-size hand proofs with finite sanity checks. They do not establish external novelty.

## Current scientific residual

`RCL-B`: jointly learn reusable operator semantics and counterfactual warrant structure from independently checked experience, then support evidence/checker/scope/rule/authority changes while optimizing:

```text
semantic bits
warrant bits
later proof/data queries
repair time
state recourse
collateral skill loss
false/stale authority
abstention
```

The theorem must survive the strongest faithful product of trace learning, monotone-DNF/hypergraph learning, unlearning, provenance/TMS/self-adjusting computation, proof-carrying execution, authority revocation, and a recurrent-Transformer implementation.

## Next smallest tasks

1. Read complete proofs, not abstracts, for the decisive parents listed in the source ledger.
2. Prove a relation or strict separation between RSD and eluder/star/teaching/query dimensions; otherwise demote RSD to notation.
3. Freeze a natural compositional operator family with reminted held-out compositions and explicit checker/scope/authority identities.
4. Give endpoint, raw-trace, positive-proof, and CWC interfaces exactly equal total information or charge the difference.
5. Prove or refute a joint upper/lower frontier. Safety may not be obtained by retracting everything.
6. Compile the learner into a recurrent/looped Transformer with identical interfaces and contract architecture wording if parity holds.
7. Mechanize the elementary pack and obtain an independent proof reconstruction from the frozen review packet.

## Kill conditions

- the final theorem is exact monotone-DNF learning plus standard provenance maintenance;
- revocation reduces at equal cost to an explicitly supplied example forget set;
- the checker or certificate carries the target program or future answers for free;
- safety is achieved by retracting everything;
- transfer vanishes under reminted identities;
- a recurrent Transformer matches all resources;
- a primary source owns the same joint theorem.

## Commands

```bash
python3 research/orion-machine/revocation_complete_learning/revocation_complete_oracle.py --self-test --pretty
python3 -m pytest -q tests/unit/test_revocation_complete_learning.py
python3 -m py_compile research/orion-machine/revocation_complete_learning/revocation_complete_oracle.py tests/unit/test_revocation_complete_learning.py
```

## Files not to touch

Do not edit protected/frozen results in existing ORION, ORION-V2, or ORION-Q lanes. This branch adds only `research/orion-machine/**` and `tests/unit/test_revocation_complete_learning.py` unless a new claim comment expands scope.
