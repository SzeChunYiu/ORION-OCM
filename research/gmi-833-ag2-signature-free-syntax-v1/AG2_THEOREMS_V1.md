# AG2 named results

All results are stated at the **registered finite scope**: the many-sorted signature
`Sigma_G0 = (Sorts, Ops, arity)` with `Sorts = {Reg, Label, Instr, Prog}`, one register generator
`r0`, two label generators `l0`,`l1`, depth bound 3, step budget 8, and the four registered input
words `(), (0), (1), (2)`. Every quantity below is an exact integer or `fractions.Fraction`.

---

## AG2-1 — `G0 = FreeSyntax(Sigma_G0)` at the registered bound

**Statement.** The set of well-sorted ground terms over `Sigma_G0` at depth bound 3 has exactly
`|Reg| = 1`, `|Label| = 2`, `|Instr| = 11`, `|Prog| = 121` members, is closed under every
well-sorted application of every operation of `Sigma_G0` (0 missing terms), and is the least such
set: the depth-indexed recursive generator (route A) and the closure-to-fixed-point enumerator
(route B) produce identical term sets, the fixed point being reached in 2 rounds.

**Quantifiers.** For all operations `o` of `Sigma_G0` and all well-sorted argument tuples drawn
from the generated set whose result depth is at most 3, `o(t1,...,tn)` is generated.

**Assumptions.** Ground terms only (no variables); one register generator; two label generators;
depth bound 3. The signature is non-recursive, so depth 3 is already the fixed point.

**Falsifiers.** A well-sorted application whose result is absent from the generated set; a
disagreement between the two routes; a term count other than `(1, 2, 11, 121)`.

**Strongest parents.** Universal algebra: many-sorted signatures, term algebras, free algebras
(Birkhoff 1935, doi:10.1017/S0305004100013463; Burris & Sankappanavar, *A Course in Universal
Algebra*). Nothing in AG2-1 is new mathematics.

**Forbidden extrapolations.** `SIGNATURE_IS_THE_BOTTOM`, `UNIQUE_SIGNATURE_FOR_G0`,
`FREE_ALGEBRA_INVENTED_HERE`.

---

## AG2-2 — operation symbols do not determine interpretations

**Statement.** Two interpretations `I_STANDARD` and `I_VARIANT` of the **same** signature
`Sigma_G0` over the **same** generated term set assign materially different behaviour to
**43 of the 121** `Prog` terms. Witness: `prog(decjz(r0,l0,l1),emit(r0,l0))`.

**Quantifiers.** There exist two interpretations of `Sigma_G0` and at least one term on which they
differ; the exact count at this scope is 43.

**Assumptions.** `I_VARIANT` changes `inc` from `+1` to `+2` and swaps the `decjz` branch targets;
both remain total interpretations of the same symbols.

**Falsifiers.** A divergent count of 0 under any pair of distinct interpretations.

**Strongest parents.** Model theory / universal algebra: the distinction between a signature and
its `Sigma`-algebras is standard.

**Forbidden extrapolations.** `SYMBOLS_DETERMINE_SEMANTICS`; no claim that these two
interpretations exhaust the `Sigma_G0`-algebras.

---

## AG2-3 — formation rules are not transition rules

**Statement.** Formation (well-sortedness) is total and decidable on the 121 `Prog` terms, while
the small-step transition relation is partial: **11 of 121** well-formed terms yield an initial
configuration with no successor (those binding `halt` at the start label). Moreover the formation
shape does not determine behaviour: **120 unordered pairs** of terms share an identical
operation-symbol multiset yet differ in observed behaviour. Witness pair:
`prog(decjz(r0,l0,l1),emit(r0,l1))` vs `prog(decjz(r0,l1,l0),emit(r0,l1))`.

**Quantifiers.** For all 121 terms formation succeeds; there exist 11 with no successor and 120
same-shape behaviour-distinct pairs.

**Assumptions.** Registered step budget and input words; "successor" means a transition from the
initial configuration.

**Falsifiers.** Zero terms without a successor; zero same-shape behaviour-distinct pairs.

**Strongest parents.** Structural operational semantics (Plotkin, *A Structural Approach to
Operational Semantics*, doi:10.1016/j.jlap.2004.05.001); term rewriting (Baader & Nipkow, *Term
Rewriting and All That*).

**Forbidden extrapolations.** `FORMATION_IMPLIES_TRANSITION`, `SHAPE_DETERMINES_BEHAVIOUR`.

---

## AG2-4 — syntactic equivalence is strictly finer than semantic equivalence

**Statement.** On ground terms syntactic equality is term identity, giving **121** syntactic
classes. The observational quotient by (terminal status, output, final register) over the four
registered input words gives **33** semantic classes. The syntactic partition refines the semantic
partition with **0** refinement failures, and the refinement is **strict**: the collapse ratio is
exactly `88/121 = 8/11`. Witness pair, syntactically distinct and semantically equal:
`prog(halt,decjz(r0,l0,l0))` and `prog(halt,decjz(r0,l0,l1))`.

**Quantifiers.** For all 121 terms, the term's syntactic class lies in exactly one semantic class;
there exist two distinct terms in one semantic class.

**Assumptions.** The registered observation family (four input words, budget 8). A larger
observation family can only refine the semantic quotient, never coarsen it.

**Falsifiers.** A semantic class count equal to 121; any refinement failure.

**Strongest parents.** Myhill–Nerode and observational/contextual equivalence; already pinned at
registered scope by `gmi-833-parent-equivalence-v1` and `gmi-833-aj2-operational-equivalence-v1`.

**Forbidden extrapolations.** `SYNTACTIC_QUOTIENT_EQUALS_SEMANTIC_QUOTIENT`; the 33 classes are
relative to this observation family and are not a claim about G0 semantics in general.

---

## AG2-5 — the registered `G0` grammar is reconstructed from `Sigma_G0`, not assumed primitive

**Statement.** The 11 `Instr` terms of `FreeSyntax(Sigma_G0)` map bijectively onto the five
registered `G0` instruction classes `{READ, INC, EMIT, DECJZ, HALT}` of
`gmi-833-g0-register-core-v1` with their registered operand shapes, and the 121 `Prog` terms
correspond one-to-one with the **121** bounded programs enumerated by `gmi-833-aj5-g0-lowering-v1`.
Executing all 121 terms on the four registered input words under `I_STANDARD` (484 executions)
reproduces AJ5's published terminal histogram **exactly**: `HALTED 63`, `INPUT_UNDERFLOW 107`,
`STEP_BUDGET_EXHAUSTED 314`. The interpreter here was written independently of the AJ5 checker and
of `g0_register_core_v1.py`.

**Boundary earned by counterexample (do not omit).** The terminal histogram **saturates at step
budget 6**: budgets 6 through 13 all give `63/107/314`. Matching AJ5's histogram therefore
identifies the step budget only up to `>= 6`, and a budget-7 hostile is structurally invisible to
this gate. Independently, **8 of 195** randomized opcode-role permutations reproduce the histogram
(200 draws, 5 identity permutations excluded because the identity is the true semantics, not a null),
so the histogram alone does **not** identify the semantics. The identification claim therefore
rests on the full behaviour map (terminal status, output and final register for each of the 121
programs on each of the 4 words), which **0 of those 195** randomized semantics reproduce and on
which the two independent routes agree exactly. The independent syntactic null (randomized
arities over the same operator names) is **0 of 200** draws.

**Quantifiers.** For all 121 terms and all 4 words, the two routes agree on the full behaviour
record; the aggregate histogram equals AJ5's.

**Assumptions.** AJ5's receipt is pinned by path and git blob sha at `source_main`; the registered
`G0` operational conventions (read-past-end is `INPUT_UNDERFLOW`; `DECJZ` decrements on the
nonzero branch; `HALT` consumes one step).

**Falsifiers.** Any disagreement with AJ5's `bounded_programs`, `primitive_status` keys or
`terminal_histogram`; any route disagreement.

**Strongest parents.** Minsky register machines (*Computation: Finite and Infinite Machines*, 1967)
own the instruction set; `gmi-833-g0-register-core-v1` owns the registered `G0` semantics;
`gmi-833-aj5-g0-lowering-v1` owns the lowering of `G0` onto the AJ1 operational role basis and the
`5t` overhead bound. AG2's residual contribution is only the explicit **signature** below the
grammar and the four separations above.

**Forbidden extrapolations.** `G0_IS_THE_OPERATIONAL_BOTTOM`, `UNIQUE_LOWEST_INSTRUCTION_BASIS`,
`BASIS_INDEPENDENT_OPERATION_THEORY_CLAIMED`, `COMPLETE_GMI`.
