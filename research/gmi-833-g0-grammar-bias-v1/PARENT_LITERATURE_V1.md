# Parent literature and repository ownership — E2

The E2 contribution is a bounded exact integration/certificate, not novelty for the parent concepts below.

## Program synthesis / grammar bias

- Rajeev Alur et al., **Syntax-Guided Synthesis**, FMCAD 2013, DOI `10.1109/FMCAD.2013.6679385`. SyGuS explicitly supplies a grammar as the syntactic set of candidate implementations in addition to semantic correctness constraints.
- Peter A. Whigham, **Grammatically-based Genetic Programming**, 1995. The grammar defines the hypothesis-language structure and directs variation; the paper explicitly frames that structure as inductive bias.
- Robert I. McKay, Nguyen Xuan Hoai, Peter A. Whigham, Yin Shan, Michael O'Neill, **Grammar-based Genetic Programming: a survey**, *Genetic Programming and Evolvable Machines* 11, 365–396 (2010), DOI `10.1007/s10710-010-9109-y`.

## Description-system dependence

- Classical Kolmogorov/algorithmic-information invariance results: shortest descriptions under suitable universal description systems are invariant only up to a description-system-dependent additive constant. E2 uses this only as a boundary against claiming finite code-length equality or representation neutrality.

## Repository parents

- #868 / PR #873 owns `G0-reg-v1` operational semantics and the finite register grammar.
- #863 owns the generic robustness requirements for alternate encodings/search/scalarizations.
- #864 owns finite machine-state/presentation remint equivariance and explicitly does not imply search invariance.

## Residual owned here

Exact finite `L/N/Q/d/A/R` census on the frozen G0 slice; grammar-node isometric-remint theorem/certificate; same-semantics non-isometric selection reversal; deterministic receipt/custody and scoped #833 reconciliation.
