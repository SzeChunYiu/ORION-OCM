# Z8 parent-ownership disclosure

Assimilation-first: every mechanism behind the nine ingredients is owned by a
parent named below and is absorbed, not re-derived as new. The residual
contribution of this tranche is stated narrowly at the end.

## External parents (nothing here is claimed novel against them)

| parent | what it owns | citation |
|---|---|---|
| Lagrangian scalarisation and its affine invariance | the price-weighted argmin `E(k) + λρ(k)`; invariance of argmins under positive affine rescaling of the objective (`ZH-2`) | Everett, *Operations Research* 11(3):399–417, 1963, doi:10.1287/opre.11.3.399 |
| Lower convex envelope / supporting-line duality | thresholds as supporting slopes of the lower convex hull; the vertex criterion for a level to be selectable at some price | Rockafellar, *Convex Analysis*, Princeton 1970, doi:10.1515/9781400873173 |
| Bayes error and label noise | the affine map `e ↦ (1−2ε)e + ε` of an error rate under symmetric flip noise, and the fact that channel-selective noise is not affine on a mixture (`I2`) | Angluin & Laird, *Machine Learning* 2(4):343–370, 1988, doi:10.1007/BF00116829; Natarajan et al., NeurIPS 2013 |
| Covariate / distribution shift | model selection under one law, evaluation under another (`I4a`) | Shimodaira, *J. Statist. Plann. Inference* 90(2):227–244, 2000, doi:10.1016/S0378-3758(00)00115-4; Quiñonero-Candela et al. (eds.), *Dataset Shift in Machine Learning*, MIT Press 2009 |
| Hysteresis under switching costs | retaining an incumbent while its excess cost is below a threshold (`I6b`) | Dixit, *J. Political Economy* 97(3):620–638, 1989, doi:10.1086/261619 |
| Mealy / Moore machines and input-only transitions | the three transducer grammars of `I7` | Mealy, *Bell Syst. Tech. J.* 34(5):1045–1079, 1955, doi:10.1002/j.1538-7305.1955.tb03788.x; Moore, *Automata Studies*, Princeton 1956 |
| Local search and single-start descent | the search-attained (as opposed to exhaustive) optimum (`I8`) | Aarts & Lenstra (eds.), *Local Search in Combinatorial Optimization*, Wiley 1997; Hoos & Stützle, *Stochastic Local Search*, Elsevier 2005 |
| Preregistration | predictions frozen before outcomes (`I9`) | Nosek, Ebersole, DeHaven & Mellor, *PNAS* 115(11):2600–2606, 2018, doi:10.1073/pnas.1708274114 |

**Not claimed novel:** affine invariance of argmins, the convex-envelope
threshold picture, flip-noise algebra, covariate shift, hysteresis bands,
transducer grammars, local-search suboptimality, or preregistration as concepts.

## On-main parents (pinned by blob sha in `MANIFEST_V1.json`)

| package | what it owns | how this package uses it |
|---|---|---|
| `gmi-833-history-switching-hysteresis-v1` (`HIST-1`, `HIST-2`) | the exact two-form hysteresis band under switching costs | `I6b` re-instantiates the band on the three-mode ladder and counts moved `V_SEL` cells |
| `gmi-833-search-law-morphology-change-v1` (`SLM-1`..`SLM-6`) | when a search law changes the observed candidate | `I8` measures the verdict move of a single-start descent and a seeded hill-climb |
| `gmi-833-g0-grammar-bias-v1` (`RELABEL-2`) and `gmi-833-remint-equivariance-v1` | a same-semantics grammar change reverses a choice; relabelling invariance | `I7c` is the relabelling no-alarm control; `I7a/b` are the grammar changes that do move verdicts |
| `gmi-833-capability-predictor-v1` (`FM_ALIASING`) | observational aliasing forces abstention | `I3` is the causal-aliasing law (period-2) whose floors collapse the delay-2 channel |
| `gmi-833-capability-predictor-evaluation-v1` (`KE-7`) | structural out-of-universe shift | `I4` is the in-population distribution shift, the complement of `KE-7` |
| `gmi-833-ae-ae2-predictive-boundary-v1` (`DRIFT_INVERT`) | a nonstationary source | `I4b` is the in-window switch `q → q'` whose floor is `ZH-4` |
| `gmi-833-heldout-20-transitions-v1` | exact ties at the registered boundary | `I1` probes the ties at `±1/64` |
| `gmi-833-z-z6-discrimination-v1` (`DS-4`, `DS-5`, `DS-6`) | positive-affine invariance of every declared-cost parent; observational equivalence | `ZH-2` is the same invariance read on the profile axis |
| `gmi-833-z-z12-prediction-scoring-v1` | the `applicable`-flag and vacuity vocabulary | every hostile and bound here carries it |

## Sibling-branch parents (named results, not yet on `source_main`; not pinned by blob)

`gmi-833-z-z13-adjudication-v1` `ZA-1` (the nine base floors, re-enumerated here
rather than imported) and `ZA-5`; `gmi-833-z-z1-master-principle-v1` `IC-1`
(the registered law `λ* = ηp·R0`, thresholds as marginal error masses);
`gmi-833-z-z5-critical-phenomena-v1` `CP-3`, `CP-6`; `gmi-833-z-z7-impossibility-v1`
`IM-4`, `IM-7`. Where this package needs a number from them it recomputes it
from scratch and reports agreement; nothing is imported.

## The named residual of this tranche

**None of the parents states or measures whether its ingredient moves a
registered verdict on the three-mode ladder.** This package supplies exactly
that: a `9 × 4` verdict-move matrix (`ZH-1`) in which every cell is either a
counted move with its exact world/cell count, reproduced by two routes, or an
`UNABLE` backed by a theorem (`ZH-2`: affine maps; `I7c`: bijections;
price-independence of `V_NICHE`/`V_THR`), plus the structural reason five
unrelated ingredients move the niche verdict in the same twelve worlds
(`ZH-3`), the earned-by-counterexample boundary of the nonstationary floor
(`ZH-4`) and the published tie-cell misses (`ZH-5`).
