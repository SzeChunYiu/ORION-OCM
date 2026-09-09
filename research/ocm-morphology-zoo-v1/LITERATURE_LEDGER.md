# Literature / source ledger — OCM Morphology Zoo (issue #221 sec 2)

Declared parents, bound by citation before implementation decisions. No papers were
fetched during MZ-D0 (per lane brief: bind the citations as declared parents). Each
entry records what the zoo actually uses from the parent.

## Quality-diversity core

| id | parent | citation | used for |
|----|--------|----------|----------|
| L01 | MAP-Elites / illumination | Mouret & Clune 2015, arXiv:1504.04909 | P05 grid archive: niche = descriptor cell, elite per cell |
| L02 | QD modular framework | Cully & Demiris 2017, arXiv:1708.09251 | archive/selector separation, QD as search-space illumination |
| L03 | QD survey | Qin et al. 2026, Swarm Evol. Comput. 100:102240 | algorithm landscape, taxonomy of QD variants |
| L04 | Novelty Search | Lehman & Stanley 2011, Evol. Comput. 19(2) | P03 behavior-only novelty, stepping stones |
| L05 | NSLC / QD overview | Pugh, Soros & Stanley 2016 | P04 local competition in novelty space |
| L06 | CVT-MAP-Elites | arXiv:1610.05729 | P06 fixed-size archives in 5-10D descriptor spaces |
| L07 | CMA-ME | arXiv:1912.02400 | P08 continuous parameter refinement within a morphology family |
| L08 | CMA-MAE | arXiv:2205.10752 | P09 archive-threshold exploration control |
| L09 | MOME | arXiv:2202.03057 | P07 Pareto front per niche; primary scientific archive |
| L10 | SAIL | DOI 10.1162/evco_a_00231 | P10 objective surrogate (gated: only if eval cost justifies) |
| L11 | BOP-Elites | arXiv:2307.09326 | P10 objective+descriptor surrogate with uncertainty |
| L12 | AURORA | arXiv:1905.11874, arXiv:2106.05648 | learned-descriptor lane; non-neural projection first refusal |
| L13 | POET / Enhanced POET | arXiv:1901.01753, arXiv:2003.08536 | P16 environment x solution coevolution, minimal criterion |
| L14 | CGP review | DOI 10.1007/s10710-019-09360-6 | E1 typed Cartesian GP graph encoding, neutral drift measurement |
| L15 | Lexicase selection | DOI 10.1109/TEVC.2014.2362729 | P11 case-as-axis selection |
| L16 | Population-Based Training | arXiv:1711.09846 | P14 inner-loop dynamic hyperparameters |
| L17 | QDax | JMLR 25(108) 2024 | accelerator reference only; NOT used (OCM semantics do not vectorize faithfully; #221 sec 9 forbids rewriting semantics to fit JAX) |
| L18 | pyribs | docs.pyribs.org | reference for MAP-Elites/CVT/CMA-ME contracts; LUNARC availability decides adopt-vs-stdlib (see FREEZE notes) |
| L19 | DEAP | (framework) | NSGA/GP baselines; same availability rule as L18 |

## Open-endedness caution

Per #221 sec 2: persistent novelty alone is insufficient. Hallmarks measured are
useful novelty (innovation that later occupies frontier niches), complexity growth
that is active (charged, exercised) not dead code, and evolvability (useful
descendants per evaluation). Complexity defined solely by generation count is
forbidden (P16 checklist).

## In-repo parents (strongest architecture parents)

| id | parent | evidence |
|----|--------|----------|
| R01 | production KSO/FKS core | src/ocm/kso/ on main at ab53109: typed relational store, authority lattice + scope algebra, gated-closure extraction (incl. pcst_exact_bounded, rarest-required-input operator index), warrant/revocation cones, obligations, nogoods, procedures; runtime executive in src/ocm/runtime/ |
| R02 | #216 MSC (merged #218) | minimum-sufficient non-neural cognition verdict, adaptive probe worlds — reused as E0 micro-worlds where applicable |
| R03 | #214 FNA (merged #215/#219) | functional donor atlas; typed-channel reach proposition (work vs reach) |
| R04 | #217 canonical lineage | adoption boundary (zoo -> #217 -> main, never direct) |

## Software binding decision (recorded MZ-D0, before any search code)

Stdlib-only faithful implementations of MAP-Elites / CVT-MAP-Elites / NSLC /
NSGA-II / MOME / lexicase in search/, because: (a) the repo itself is
stdlib-only (pyproject dependencies = []), (b) LUNARC module availability for
pyribs/DEAP is unconfirmed and Apptainer build adds a failure surface for zero
scientific content, (c) #221 sec 9 explicitly permits faithful stdlib
implementations with citation. Each search module cites its parent above. If a
later tranche adopts pyribs/DEAP, that is a numbered freeze amendment with a
cross-check run reproducing a stdlib result.
