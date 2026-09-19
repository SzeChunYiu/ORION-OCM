# Parent ownership — `gmi-833-emergence-conditions-v1`

Assimilation first. The idea that a resource constraint can decide which strategy a bounded
agent adopts is old and well owned. This package invents none of it.

## External mathematics and literature absorbed

| what | owner | reference |
|---|---|---|
| bounded rationality: the resource account, not the goal, shapes the procedure | Simon | Simon, H. A. (1955), *A behavioral model of rational choice*, QJE 69(1):99-118, doi:10.2307/1884852 |
| the value of computation and metalevel control of computation | Russell and Wefald; Horvitz | Russell, S. and Wefald, E. (1991), *Principles of metareasoning*, Artificial Intelligence 49(1-3):361-395, doi:10.1016/0004-3702(91)90015-C |
| the value of information: when an observation is worth its price | Howard; Lindley | Howard, R. A. (1966), *Information value theory*, IEEE Trans. Systems Science and Cybernetics 2(1):22-26, doi:10.1109/TSSC.1966.300074; Lindley, D. V. (1956), Ann. Math. Statist. 27(4):986-1005, doi:10.1214/aoms/1177728069 |
| sequential design of experiments: choosing the next observation from what has been seen | Chernoff (1959), Ann. Math. Statist. 30(3):755-770, doi:10.1214/aoms/1177706205 | |
| register and counter machines, and instruction-set decomposition | Minsky, M. (1967), *Computation: Finite and Infinite Machines* — no DOI registered | |
| exhaustive program enumeration over a bounded instruction alphabet; Levin-style bounded search | Levin, L. (1973), *Universal sequential search problems* — no DOI registered | |
| minimum-description-length and cost-sensitive choice among conforming models | Rissanen, J. (1978), *Modeling by shortest data description*, Automatica 14(5):465-471, doi:10.1016/0005-1098(78)90005-5 | |
| emergence as a property of the composition rather than of the parts | classical; no single owner claimed here | |

## Merged `#833` parents pinned

| package | what it owns here | pinned receipt |
|---|---|---|
| `gmi-833-aj5-g0-lowering-v1` | the generic lower role basis this substrate's operation names follow, and the finding that named opcodes are presentation, not primitives | `RESULT_V1.json` |
| `gmi-833-aj8-intelligence-boundary-v1` | the registered negative controls, including the fixed lookup table and the universal interpreter without a task selector, which this package must not contradict | `RESULT_V1.json` |
| `gmi-833-g0-register-core-v1` | the register-machine reference semantics from which `B0`'s operation set is drawn | `RESULT_V1.json` |
| `gmi-833-aj6-aj8-development-value-intelligence-v1` | `UNIVERSAL_COMPUTATION_IS_INTELLIGENCE` as a registered forbidden promotion, carried into this package's own list | `RESULT_V1.json` |

## What is NOT claimed novel

Not novel: metareasoning as a subject, the value of computation, the value of information,
sequential experiment design, bounded rationality, register machines, exhaustive program
enumeration, or the observation that a resource price can change which program is preferred.
Not novel: that emergence should be demonstrated rather than named — that is the AH3 row's own
requirement.

## The residual contribution

1. `EC-1`: the emergence condition written so that it is decidable — an exhaustive enumeration
   plus an exact integer margin, with a four-verdict vocabulary fixed before any run.
2. `EC-2`: the structural reading of a forced verdict as blind-cover impossibility, with the
   blind-cover count published for every family.
3. `EM-4`: the central negative — `EMERGES_BY_PRICE` occurs `0` times in thirteen families,
   under two accountings and the whole price sweep. The mechanism this package was built to test
   is empty at this scope, and the reason is given rather than hidden.
4. `EM-5`: the two boundaries with no coverage anywhere in the merged corpus decided exactly:
   forced in every one of `132` and `1,648` conforming programs, with `0` blind covers, over
   `813,615` enumerated programs of a substrate that names neither.
5. `EM-6`: the disclosure that five of the thirteen frozen requirements entail their own
   predicate, and what happens when the clause is removed.
6. `EM-7`: four exhaustively proved non-expressibility results with their named obstructions and
   their revivals on one-operation extensions.
7. The extensionality detector, which turns "not a primitive macro" from a promise into a
   checkable property, validated in both directions.

## Compatibility with the parents' own forbidden sets

`gmi-833-aj6-aj8-development-value-intelligence-v1` forbids
`UNIVERSAL_COMPUTATION_IS_INTELLIGENCE`; this package asserts nothing of the kind and carries
the token into its own forbidden list. `gmi-833-aj8-intelligence-boundary-v1` records that
`UNIVERSAL_DEFINITION` is `NOT_FROZEN`; nothing here freezes one, and `INTELLIGENCE_DEFINED` is
a registered forbidden promotion of this package. `gmi-833-aj5-g0-lowering-v1` forbids
`G0_IS_THE_OPERATIONAL_BOTTOM`; `B0` is presented as one registered neutral substrate and never
as a bottom.
