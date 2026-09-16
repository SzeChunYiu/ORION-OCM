# AJ9f — blind recovery of K05 compositional rule/search structure

The task supplies a finite compositional environment state `N(N(E,A),N(B,E))`, goal `N(A,B)`, and two legal local environment transformations `N(E,x)->x` and `N(x,E)->x`. Those are task laws, not a supplied solver architecture.

Two family-hidden procedures operate on different encodings: FIFO frontier search over nested tuples and iterative depth-limited search over prefix token sequences. Both reach the goal in two steps. The initial state has two legal successors, and the procedures deliberately choose opposite first branches.

Only after the blind outcome is frozen, K05 adjudication verifies explicit compositional discrete state, rule-governed local transformations, a multi-step semantics-preserving path, multiple legal successors, control over alternative derivation paths, and exact goal reachability. Both paths preserve the ordered non-`E` leaf semantics `(A,B)` at every step. Terminal: `RECOVERED`.

This is a finite symbolic/rewrite/search mechanism recovery conditional on a compositional discrete task world. It does not derive general theorem proving, unrestricted term-rewriting completion, natural-language symbolic reasoning, or universal symbolic superiority. No pre-search selection prediction was frozen.

Claim ceiling: `AJ9F_K05_BLIND_COMPOSITIONAL_RULE_SEARCH_RECOVERY_AT_FROZEN_FINITE_SCOPE`.
