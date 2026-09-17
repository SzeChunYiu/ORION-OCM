# GMI #833-F finite candidate space, semantic quotient, and neutral descriptor

This package closes four proof-first Section-F tasks at an explicitly bounded
scope. It defines `M(G0-fin-v1,B)`, enumerates it exactly for registered small
budgets, collapses programs by a declared finite behavioral interface, and
computes morphology descriptors only from external behavior, exact resources,
and declared developmental distance.

The registered two-coordinate structural resource vector is additive:

```text
REGISTER_CELL = (0,1)
CODE_CELL     = (1,0)
rho(P)        = sum atoms = (number of instructions, number of registers).
```

For `n` labels and `r` registers, the typed instruction-instance alphabet has

```text
q(n,r) = 1 + 3rn + rn^2
```

members: one `HALT`, three single-successor classes (`READ`, `INC`, `EMIT`),
and one two-successor class (`DECJZ`). Consequently,

```text
|M(G0-fin-v1,(N,R))|
    = sum_{r=1..R} sum_{n=1..N} q(n,r)^n.
```

The implementation independently agrees with a direct Cartesian oracle on four
registered budgets. At `(N,R)=(2,1)`, all 126 candidates are emitted exactly
once and collapse to 18 semantic classes on protected inputs `(),(0,),(1,)`
with step cap 6, reproducing the merged #875 finite semantic count while adding
the exact quotient and neutral descriptors needed here.

Evidence:

- analytic finiteness, completeness, soundness, and exactly-once proofs;
- independent code-path Cartesian enumeration oracle;
- exhaustive equality-relation and quotient checks on the 126-candidate slice;
- all `5! = 120` registered operation-token remints across all 126 candidates;
- all 450 two-register candidates under the nontrivial register permutation;
- a semantics-changing pseudo-remint hostile that is detected;
- normal and optimized-mode deterministic tests and byte-stable receipt.

Claim ceiling:

`GMI_833_FINITE_CANDIDATE_SPACE_QUOTIENT_DESCRIPTOR_ENUMERATION_AT_REGISTERED_SCOPE`

This is not an unbounded equivalence decision procedure, an unbiased or unique
grammar, a universal morphology taxonomy, scalable large-budget sampling,
million-scale generation, clustering, or known-family recovery.

## Reproduce

```bash
python3 -I -B research/gmi-833-finite-candidate-space-v1/test_finite_candidate_space_v1.py -v
python3 -I -O -B research/gmi-833-finite-candidate-space-v1/test_finite_candidate_space_v1.py -v
python3 -I -B research/gmi-833-finite-candidate-space-v1/finite_candidate_space_v1.py
```
