# Fifteen-gap closure ledger V1

Date: 2026-09-13  
Authority: linked proofs and evidence, not the status words in this table.

This ledger translates the requested GMI gaps into atomic claims. A row may be closed at one scope while stronger scopes remain open.

| # | Gap | Baseline on current main | This capsule target |
|---|---|---|---|
| 1 | Core axioms | Grand-GMI V1 has an 8-field causal-process declaration. | `MINIMAL_AXIOM_FREEZE_V1.md` factors it into five architecture-neutral primitives; downstream proofs must use only declared restrictions. |
| 2 | Adaptive inference | ARC-1–4 proves predictable adaptive row visits/counts and finite stopping for a fixed finite row register with fixed conditional laws. | Prove one global e-process/supermartingale theorem covering repeated revisits, arbitrary cross-row dependence compatible with conditional validity, predictable dynamic row birth, and unbounded monitoring. |
| 3 | Composition | Several scoped semantic/query/delegation composition results exist. | Prove a statistical/system validity composition theorem with a precise interface contract; explicitly show local validity alone is insufficient. |
| 4 | Learning theory | Developmental reachability exists, but a single compact definition of learned/improved/converged/failure is absent. | Define epistemic state, risk/regret, improvement, consistency and failure modes relative to `(I,E,O,R,D)`. |
| 5 | Representation / realization | Grand-GMI already treats architectures as candidate realizations and has representation/selection work. | Give a constructive finite-computation realization theorem with neural and non-neural corollaries while refusing the false implication representable=>selected. |
| 6 | Optimization | Existing repo work studies optimization/resource claims, but no minimal derivation bridge is normative. | Prove conditional reverse-mode credit assignment for differentiable DAG realizations; derive gradient descent only after adding local first-order descent geometry, and list valid alternatives. |
| 7 | Memory / state | Exact semantic state, working-state and reuse/invalidation results exist. | Unify transient state, persistent epistemic state, provenance, revision, conflict and resource-bounded forgetting. |
| 8 | Causality | The master theory is causal-process scoped and several intervention results exist. | State an observational non-identifiability boundary and an SCM/intervention extension with explicit identifiability premises. |
| 9 | Agency / planning | Controlled acquisition and decision cores provide scoped policies. | Separate truth/evidence from preference; define policy value under action-dependent kernels and derive finite Bellman recursion as a specialization. |
| 10 | Resource boundedness | Rich resource/frontier accounting exists. | Define metareasoning/value-of-computation choice over experiments/computations with all costs charged. |
| 11 | Architecture emergence | Morphology/frontier/selection theorems exist. | Define emergence as selection from a complete admitted feasible family under obligation/resource/development constraints; state when prediction is impossible due underdetermination. |
| 12 | Novel predictions | Existing finite predictions/experiments are domain-scoped. | Register at least one discriminating candidate prediction before executing its decisive experiment; do not claim literature novelty merely from a new name. |
| 13 | Existing-theory map | Parent theories are cited locally across capsules. | Provide one explicit specialization/difference table for Bayes, information theory, PAC/VC, MDL/PAC-Bayes, RL, causal inference, active learning and neural computation. |
| 14 | Falsifiability | Many current theorems include counterexamples and hostile controls. | Attach falsifiers to the synthesis-level claims: statistical, learning, representation, optimization, architecture and empirical prediction. |
| 15 | Experimental validation | Multiple exact finite and hosted empirical capsules exist. | Provide a prospective cross-family benchmark protocol measuring sample, robustness, adaptation, compute, lifetime cost and generalization with matched parents. |

## Dependency graph

`1 -> {2,4,5,7,8,9,10}`  
`2 -> 3`  
`{3,4,5} -> 6`  
`{4,5,6,7,8,9,10} -> 11`  
`11 -> 12`  
`{4,8,9,10} -> 13`  
`{2..13} -> 14`  
`{11,12,14} -> 15`

This graph is a proof/program dependency, not a statement that later scientific questions can ever be exhausted.

## Scope discipline

The intended endpoint is **not** “GMI proves every intelligent architecture.” The strongest defensible target is:

1. a small architecture-neutral language;
2. valid global inference under declared sequential contracts;
3. closure rules for composing certified components;
4. constructive realization of broad computational families;
5. explicit conditions that select among realizations;
6. falsifiable predictions and prospective experiments.

A representation theorem without a selection theorem leaves architecture emergence open. A selection theorem without complete feasible-family coverage is conditional on its candidate class. An experiment without a preregistered discriminator supplies evidence, not a unique-theory derivation.
