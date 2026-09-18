# AG2 parent ownership and residual contribution

## What is NOT claimed novel

Everything in the mathematics of AG2 is parent-owned. Specifically:

| Object used here | Parent that owns it | Citation |
|---|---|---|
| Many-sorted signature `(Sorts, Ops, arity)` | Universal algebra | Birkhoff, *On the structure of abstract algebras*, Math. Proc. Camb. Phil. Soc. 31(4), 1935. doi:10.1017/S0305004100013463 |
| Term algebra / free algebra over a signature; least-fixed-point generation | Universal algebra | Burris & Sankappanavar, *A Course in Universal Algebra*, Springer GTM 78, 1981 |
| Equational logic, varieties, HSP | Universal algebra | Birkhoff 1935 (as above) |
| Presentation-independent algebraic theories; definable operations not privileged by a generating set | Lawvere theories | Lawvere, *Functorial Semantics of Algebraic Theories*, PNAS 50(5), 1963. doi:10.1073/pnas.50.5.869 |
| Formation vs reduction rules; small-step configuration semantics | Structural operational semantics | Plotkin, *A Structural Approach to Operational Semantics*, J. Log. Algebr. Program. 60–61, 2004. doi:10.1016/j.jlap.2004.05.001 |
| Term rewriting, confluence/termination vocabulary | Term rewriting | Baader & Nipkow, *Term Rewriting and All That*, CUP, 1998 |
| Observational / contextual equivalence strictly coarser than syntactic identity | Automata and process theory | Nerode, *Linear automaton transformations*, Proc. AMS 9(4), 1958. doi:10.1090/S0002-9939-1958-0135681-9 |
| The register instruction set `READ/INC/EMIT/DECJZ/HALT` | Register machines | Minsky, *Computation: Finite and Infinite Machines*, Prentice-Hall, 1967 |

Within this repository, the following merged packages own their results and AG2 imports rather
than re-derives them:

- `gmi-833-g0-register-core-v1` — the registered `G0` execution semantics and instruction classes.
- `gmi-833-aj5-g0-lowering-v1` — the lowering of `G0` onto the AJ1 operational role basis, the
  `primitive_status` ledger for the five core opcodes, the `121` bounded programs, the `484`
  executions and the `lower_ops <= 5 * G0_steps` overhead bound.
- `gmi-833-aj1-operational-process-base-v1` — the typed operational process frame that the role
  basis sits in.
- `gmi-833-aj2-operational-equivalence-v1`, `gmi-833-parent-equivalence-v1` — operational and
  parent equivalence boundaries.

## Explicitly not claimed

AG2 claims **no** basis-independent operation theory. Lawvere theories already own
presentation-independent algebraic structure; row AG3 "Parent-subtract Lawvere theories/universal
algebra before claiming a new basis-independent operation theory" is discharged here by the
subtraction itself: the residual below is deliberately narrow and contains no such theory.

AG2 also claims no uniqueness for `Sigma_G0`. Many signatures present the same finite behaviour;
`gmi-833-g0-grammar-bias-v1` already exhibits same-semantics non-isometric grammar twins.

## Residual contribution of this tranche

1. An **explicit signature written below the registered `G0` grammar**, with `G0` exhibited as the
   free term algebra it generates — replacing the previous treatment of `G0` syntax as primitive.
2. Four **exact finite separations** with named witnesses: symbols vs interpretations (43/121);
   formation vs transition (11/121 with no successor; 120 same-shape behaviour-distinct pairs);
   syntactic vs semantic equivalence (121 vs 33 classes, collapse `8/11`); and the term-set to
   registered-program bijection.
3. An **independent reproduction of AJ5's published terminal histogram** (`63/107/314` over 484
   executions) from a separately written interpreter, together with the **boundary** on what that
   cross-check proves: the histogram saturates at step budget 6 and is reproduced by 8/200
   randomized opcode-role permutations, so it does not identify the semantics on its own.
