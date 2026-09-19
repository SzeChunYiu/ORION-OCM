# Parent ownership — `gmi-833-ag4-formalism-translations-v1`

Assimilation first. Each of the six families the AG4 section names is a mature formalism with a
mature owner, and the relationships between several of them are classical theorems. This package
invents none of them; it adjudicates all fifteen pairs exhaustively over one registered finite
universe and publishes the exact residual where a translation is not total.

## External mathematics absorbed

| what | owner | reference |
|---|---|---|
| a state space with finitary operations; free algebras over a signature | Birkhoff | Birkhoff, G. (1935), Math. Proc. Camb. Phil. Soc. 31(4):433-454, doi:10.1017/S0305004100013463 |
| labelled transition systems and structural operational semantics | Plotkin | Plotkin, G. D. (2004), *A structural approach to operational semantics*, JLAP 60-61:17-139, doi:10.1016/j.jlap.2004.05.001 |
| coalgebra as the general theory of state-based systems, parameterized by a functor; the identification of labelled transition systems with coalgebras for the powerset functor | Rutten; Aczel and Mendler | Rutten, J. J. M. M. (2000), *Universal coalgebra: a theory of systems*, TCS 249(1):3-80, doi:10.1016/S0304-3975(00)00056-6 |
| algebraic theories as categories, independent of a generating set | Lawvere | Lawvere, F. W. (1963), PNAS 50(5):869-872, doi:10.1073/pnas.50.5.869 |
| monads, Kleisli categories, and the powerset and distribution monads as the vehicles of nondeterminism and probability | Moggi | Moggi, E. (1991), *Notions of computation and monads*, Information and Computation 93(1):55-92, doi:10.1016/0890-5401(91)90052-4 |
| symmetric monoidal categories: serial versus parallel composition as independent structure | Mac Lane | Mac Lane, S. (1963), *Natural associativity and commutativity*, Rice Univ. Studies 49:28-46 — no DOI registered |
| Markov kernels and the Kleisli category of the distribution monad | Giry | Giry, M. (1982), *A categorical approach to probability theory*, LNM 915:68-85, doi:10.1007/BFb0092872 |
| strong bisimulation, used only to justify the observational reading of behaviour | Park; Milner | Park, D. (1981), LNCS 104:167-183, doi:10.1007/BFb0017309 |

## Merged `#833` parents pinned

| package | what it owns here | pinned receipt |
|---|---|---|
| `gmi-833-aj1-operational-process-base-v1` | the operational process base, the registered comparison of candidate elementary descriptions, `ABSOLUTE_PROCESS_ONTOLOGY_PROVEN` as a forbidden terminal, and the `MULTIPLE_FOUNDATIONALLY_EQUIVALENT_PROCESS_BASES` terminal this adjudication supports | `RESULT_V1.json` |
| `gmi-833-aj5-g0-lowering-v1` | one of the two family pairs that already had an exact translation on `main`: the `P-FUN` functional and `P-REL` relational presentations, an `A`-`E` instance, cited and not re-claimed; and the transfer boundary this package must not repair | `RESULT_V1.json` |
| `gmi-833-aj12-foundation-substrate-relativity-v1` | the other pair already on `main`: two formalization styles yielding the same operational quotient | `RESULT_V1.json` |

## What is NOT claimed novel

Not novel: any of the six formalisms; the isomorphism between labelled transition systems and
coalgebras for the powerset functor; the monadic account of nondeterminism and probability; the
independence of the tensor from serial composition in a monoidal category; the fact that a
monoid carries no preferred generating family. Not novel: the two family pairs already translated
on `main`, which are cited above.

## The residual contribution

1. All `30` directed translations adjudicated over one registered finite universe of `8,032`
   objects, each either verified total over the source's whole range or bounded by an exact
   domain (`AG4T-1`).
2. A closed obstruction vocabulary fixed before any run, with every partial verdict landing
   inside it and the three tokens that never fire reported rather than quietly dropped
   (`AG4T-2`).
3. Two residuals separated from obstructions and measured as fibres: the non-canonicity of any
   translation out of the category family (fibre sizes `1` to `13`), and the kernel-to-support
   fibre (`324` kernels over `102` supports, largest fibre `90`) (`AG4T-3`).
4. The anti-flattening control, run every time: cut to a common deterministic core the same
   universe makes all fifteen pairs mutually total, which is what a result designed to succeed
   would look like (`AG4T-4`).

## Compatibility with the parents' own forbidden sets

`gmi-833-aj1-operational-process-base-v1` registers `ABSOLUTE_PROCESS_ONTOLOGY_PROVEN` as a
forbidden terminal and states minimality only relative to named requirements. Nothing here
weakens that: obstructions in both directions for three pairs and in one direction for eight more
are evidence **for** multiple equivalent process bases and against a unique bottom.
`gmi-833-aj5-g0-lowering-v1` records that instruction description length, micro-step cost,
mutation distance and search geometry do not transfer across a semantics-preserving lowering;
`TRANSLATION_PRESERVES_COST` and `TRANSLATION_PRESERVES_SEARCH_GEOMETRY` are accordingly
forbidden promotions of this package, and every verdict here is about behaviour alone.
