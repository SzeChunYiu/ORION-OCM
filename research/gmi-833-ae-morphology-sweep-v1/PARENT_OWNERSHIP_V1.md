# Parent ownership — gmi-833-ae-morphology-sweep-v1

Assimilation first: the strongest parents are absorbed and named, then the
residual is stated. Nothing below is claimed as novel.

## Repository parents (pinned by blob sha at `source_main`)

| parent | what it owns | pin |
|---|---|---|
| `gmi-833-morphology-selection-schema-v1` | the choice correspondence itself: raw nonnegative resource vectors, strictly-positive price scalarization, Pareto frontier, full argmin set with no fabricated tie-break, `NO_VIABLE_MORPHOLOGY` fail-closed, and the affine phase schema (`SEL-1`, `SEL-2`) | `2adeddd2…` |
| `gmi-833-morphology-selection-v1` | positive-mass niche coexistence and the nonnegative-repricing no-flip law | `6511cba4…` |
| `gmi-833-global-vs-reachable-morphology-v1` | optimal versus developmentally reachable model class | `37a0dda5…` |
| `gmi-833-finite-candidate-space-v1` | the finite candidate space, semantic quotient and neutral descriptor | `4086d6be…` |
| `gmi-833-finite-morphology-metrics-v1` | exact semantic / resource / developmental model-class metrics | `b5bafc0a…` |
| `gmi-833-ae-ae10-usable-information-v1` | `U(W,T,R)`, the achievability-gap definition of usable information, and its monotonicity and ceiling | `69aafebe…` |
| `gmi-833-ae-ae1-structure-separation-v1` | task-relative exploitable structure and the accessibility separations | `ceb77f5b…` |

## Literature parents

- **Predictive V-information.** Xu, Zhao, Song, Stewart, Ermon, *A theory of
  usable information under computational constraints*, ICLR 2020,
  arXiv:2002.10689. `U` at a fixed budget is an instance with `V = H_R` and 0-1
  loss. This tranche adds nothing to that theory; it only feeds it into a
  model selection rule.
- **Bounded rationality / resource-rational analysis.** Simon 1955,
  doi:10.2307/1884852; Lieder & Griffiths 2020,
  doi:10.1017/S0140525X1900061X. The price vector and the budget lattice are
  theirs.
- **Computational mechanics.** Crutchfield & Young 1989,
  doi:10.1103/PhysRevLett.63.105; Shalizi & Crutchfield 2001,
  doi:10.1023/A:1010388907793. Causal states, statistical complexity and the
  minimality of the epsilon-machine are theirs; the causal-state partition used
  in `SWEEP-6` is computed by their definition, not a new one.
- **Fourier / Walsh analysis of boolean functions.** O'Donnell,
  *Analysis of Boolean Functions*, CUP 2014, doi:10.1017/CBO9781139814782. The
  closed form `max_{affine} Pr[h(X)=Y] = 1/2 + max_a |W(a)|/2` and the fact that
  parity has no correlation with any junta of arity `< n` are theirs.
- **Juntas and learning under locality.** Blum & Langley 1997,
  doi:10.1016/S0004-3702(97)00063-5; Mossel, O'Donnell & Servedio 2004,
  doi:10.1016/j.jcss.2004.04.002.
- **Causal calculus and Markov equivalence.** Pearl, *Causality*, 2nd ed., CUP
  2009, doi:10.1017/CBO9780511803161; Verma & Pearl 1990 (equivalence classes
  of DAGs); Spirtes, Glymour & Scheines, *Causation, Prediction, and Search*,
  2nd ed., MIT Press 2000, doi:10.7551/mitpress/1754.001.0001. The fact that
  `A -> C` and `C -> A` are Markov-equivalent and that `do(.)` separates them is
  entirely theirs.
- **Manifold hypothesis and intrinsic dimension.** Fefferman, Mitter & Narayanan
  2016, doi:10.1090/jams/852; Bengio, Courville & Vincent 2013,
  doi:10.1109/TPAMI.2013.50. The hierarchy language AE6 asks for is theirs; the
  locality predicate used here is the coordinate-junta special case and is
  labelled as such.

## What is NOT claimed novel

The model selection correspondence, the usable-information definition, the
causal-state definition, the Walsh identity, Markov equivalence, the
do-calculus, and the observation that observational data underdetermines
intervention. Every one of these is a parent result and is used as given.

## The residual contribution of this tranche

Exactly one thing, and it is small:

> the **viability bridge** `active(W, tau) = { m : acc(m, W) >= tau }`,
> which maps an exact achievability quantity computed on a world onto the active
> candidate set that the parent choice correspondence consumes.

No parent package on `main` contains any information-theoretic or achievability
quantity — verified by inspection of all five parent model-class receipts — so no parent
can, on its own, answer "which quantity predicts the selected model class". The
section map's claim that these four rows need "no new mathematics" is therefore
wrong, and the correction was recorded in `FREEZE_V1.md` before any result
existed.

Everything downstream (`SWEEP-1` … `SWEEP-6`) is the functional-dependence
census that the bridge makes possible, plus the exact `tau`-phase maps.
