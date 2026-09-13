# GMI recursive theory closure V1

Status: **ACTIVE CONDITIONAL THEORY CAPSULE; NO UNIVERSAL-COMPLETION CLAIM**  
Date: 2026-09-13

This capsule turns the current GMI gap list into a dependency-ordered theory programme without replacing the corrected results in `research/gmi-grand-unification-v1/`.

The governing rule is conservative: a result here may strengthen or factor an existing theorem, but it may not silently weaken its hypotheses, turn finite evidence into a universal theorem, or promote representability into architectural selection.

## Dependency order

1. [Minimal axiom freeze](MINIMAL_AXIOM_FREEZE_V1.md): factor the existing Grand-GMI declaration into five architecture-neutral primitives and six scope rules.
2. Global adaptive inference: repeated row visits, cross-row dependence, dynamic row creation, countably long operation and one global validity statement.
3. Composition: state the exact interface contract under which locally valid evidence processes remain globally valid.
4. Learning: define epistemic state, loss/risk, improvement, consistency/regret and explicit failure conditions.
5. Realization: separate **representation** (a structure can realize the process) from **selection** (the theory prefers that structure).
6. Optimization: derive reverse-mode credit assignment only under differentiable compositional realizations, and separate that from the choice of gradient descent.
7. Memory: transient state, retained knowledge, provenance, revision, conflict and lossy forgetting with a declared distortion/resource contract.
8. Causality: add intervention semantics and identifiability assumptions; observational evidence alone is not promoted to a causal claim.
9. Agency: add preferences/loss over consequences and action-dependent dynamics; epistemic validity is distinct from decision optimality.
10. Resource-bounded intelligence: make computation/experiment selection a metalevel decision with charged compute, memory, samples and time.
11. Architecture emergence: define a feasible architecture space and a selection functional before claiming an architecture is predicted.
12. Predictions: require a registered prediction that discriminates GMI from matched parents before seeing the decisive result.
13. Theory map: state specializations and differences relative to Bayesian inference, information theory, PAC/VC, MDL/PAC-Bayes, reinforcement learning, causal inference, active learning and neural computation.
14. Falsifiability: attach explicit countermodels or empirical rejection regions to each non-tautological claim family.
15. Experimental validation: prospective protocols must include matched baselines, development and lifetime cost, uncertainty and held-out tasks/substrates.

## Scientific closure states

Each item is recorded in exactly one of the following states:

- `THEOREM`: proved from declared premises.
- `CONSTRUCTION`: an admitted realization/witness exists.
- `CONDITIONAL`: the implication is proved but one or more premises are externally supplied.
- `EMPIRICAL`: a finite or statistical claim with its confidence/evidence contract.
- `OPEN`: no sufficient proof or decisive experiment yet.
- `REFUTED`: the stated implication has a counterexample; a repaired weaker statement may coexist.

`REPRESENTABLE` and `SELECTED` are not closure states. They answer different questions and must not be conflated.

## Compatibility with current Grand GMI

The existing master declaration

`G = (P, B, E, Omega, Theta, rho, D, epsilon)`

remains authoritative for the detailed causal-process schema. The minimal core in this capsule is a factorization:

- causal interface `I := (P, B, Theta)`;
- environment class `E` unchanged;
- obligation `O := (Omega, epsilon)`;
- resource ledger `R := rho`;
- development law `D` unchanged.

No theorem may infer that a neural, symbolic, Bayesian, tree, retrieval, quantum or other implementation is privileged merely because it is representable.

## Immediate target

The first target after this freeze is the global adaptive-validity/composition bridge. The existing ARC result already handles predictable adaptive row visits and finite stopping under a fixed finite conditional-law contract. The successor must make explicit what changes when rows are revisited indefinitely, rows are dependent, the registry grows dynamically, and operation has no fixed terminal horizon.

## Literature boundary

The sequential-validity layer deliberately builds on established confidence-sequence/e-process/test-martingale theory rather than claiming novelty for optional-stopping validity. Relevant parents include Howard et al. (2021), Ramdas et al. (2023), Grünwald, de Heide and Koolen (2024), and Vovk/Wang work on sequential e-values. New GMI content, if any, must therefore lie in the declared system-level interfaces, cross-layer consequences, resource accounting or a preregistered learner/architecture prediction—not in relabelling those parent results.
