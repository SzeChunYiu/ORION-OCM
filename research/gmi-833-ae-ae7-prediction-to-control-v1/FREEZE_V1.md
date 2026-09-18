# GMI #833 Section AE7 — from prediction to control: prospective freeze v1

Source `main`: `5e57d4292266bccf435136e1f7d72caa32e920a0`.

Committed **before** any executor, oracle, test, receipt, theorem note or
reconciliation file of this package exists in the tree.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE7 — From prediction to control`

1. `- [ ] Prove that prediction alone is insufficient for general intelligence by constructing same-predictive/different-control-relevance examples.`
2. `- [ ] Formalize control-relevant sufficient state / action equivalence under a utility or behavioral specification.`
3. `- [ ] Relate to POMDP belief states, sufficient information states, rate-distortion control and bounded rationality; subtract parent mathematics.`
4. `- [ ] Derive value-of-information conditions for when sensing/remembering/computing additional information is worth its resource cost.`
5. `- [ ] Derive when an agent should compress observations more aggressively because actions are insensitive to distinctions.`
6. `- [ ] Derive when control requires preserving distinctions that pure prediction would discard.`
7. `- [ ] Prospectively predict policy/representation transitions under changing information-processing prices.`

**No neighboring row is earned here.** No AE1, AE4, AE8, AE10, AE13 or other AE
row, no row of any other issue comment, and no row of the #833 issue body, is
earned by this tranche. In particular row 1 of AE7 is about *utility*
insufficiency; the *causal* insufficiency of observational prediction is AE13's
row 1 and is **not** claimed here.

## Frozen scope

- **Support.** A finite latent state set `S`; the registered census uses
  `S = {0,1}^3`, `8` states, `X` uniform, each atom of exact mass `1/8`.
- **Sensors.** A sensor is a partition `T` of `S`; the full registered sensor
  family is all `Bell(8) = 4140` partitions, enumerated exhaustively.
- **Targets.** A registered finite family of prediction targets `Y = g(S)`,
  used to define predictive sufficiency independently of any utility.
- **Control problems.** A finite action set `A` and an exactly rational utility
  `U(s, a)`. `V(T) = sum_blocks max_a sum_{s in block} p(s) U(s, a)`, the best
  expected utility achievable by a policy measurable with respect to `T` — an
  exact rational. `V_blind = V({S})`, `V_full = V(discrete partition)`.
- **Prices.** A registered exactly rational price ladder on sensing cost. The
  priced objective is `J_pi(T) = V(T) - pi * cost(T)` with `cost(T)` a
  registered exactly rational sensing cost, non-decreasing in refinement.

All arithmetic is `fractions.Fraction` or `int`. No float appears in any claim;
the test asserts by AST scan that no float literal and no `math.log` reaches a
reported quantity.

## Frozen definitions

- `T` is **predictively sufficient** for `Y` iff `p(Y | T(s)) = p(Y | s)` for
  every `s`, i.e. `T` refines the level-set partition of `s -> p(Y | s)`.
- `T` is **control-sufficient** for `(U, A)` iff `V(T) = V_full`.
- **Action equivalence.** `s ~_U s'` iff the two states admit the same optimal
  action set at every registered belief weight on `{s, s'}`; the frozen v1
  instantiation is the coarsest partition `T` with `V(T) = V_full`, computed by
  exhaustive search over the 4140 partitions, so "coarsest" is a proved
  property rather than an assertion. If the coarsest control-sufficient
  partition is **not unique**, the whole set of minimal ones is reported; a
  silent tie-break is a package defect.
- **Value of information** of `T` over `T'`: `VoI(T, T') = V(T) - V(T')`, an
  exact rational, defined only when `T` refines `T'`.

## Required evidence and falsifiers

- `PC-1` (row 1): a construction in which two registered configurations have
  **identical predictive content** — the same predictive-sufficiency status for
  every registered target `Y`, with the induced predictive distributions equal
  cell by cell as exact rationals — and **different** achievable control value
  under a registered utility. The census count of such pairs is reported, not
  only the witness. The claim is scoped to the registered utility family and
  must not be stated as a claim about general intelligence as such;
  `PREDICTION_INSUFFICIENT_FOR_INTELLIGENCE_IN_GENERAL` is a forbidden
  promotion — what is proved is insufficiency *at the registered scope*.
- `PC-2` (row 2): the formal definitions above, with the coarsest
  control-sufficient partition computed exhaustively for every registered
  control problem, its uniqueness or non-uniqueness reported, and a proved
  statement of how it relates to the coarsest predictively sufficient
  partition (refines / is refined by / incomparable), each relation counted
  over the census including the ones with count `0`.
- `PC-3` (row 3): a machine-readable parent crosswalk with citations covering
  POMDP belief states and sufficient information states, rate-distortion
  control, and bounded rationality, each entry stating what is
  **parent-owned** and what — if anything — is residual here. A
  `PARENT_SUFFICIENT` terminal on any entry is a **success**, recorded as such.
- `PC-4` (row 4): an exactly stated value-of-information condition — acquire
  the finer sensor iff `VoI > price` — with the exact break-even price computed
  for every registered refinement pair, and machine-checked witnesses strictly
  on **each** side of the threshold, plus the exact behaviour **at** the
  threshold (the tie) reported rather than skipped.
- `PC-5` (row 5): an exactly stated condition under which merging two states
  costs no control value (their optimal action sets agree in the relevant
  sense), with the census count of merges that are free and the count that are
  not, and a witness of each.
- `PC-6` (row 6): a distinction that is **predictively redundant** for every
  registered target `Y` yet **control-relevant** — merging it strictly lowers
  `V`. Census count reported. This is the exact converse of `PC-5` and both
  directions must be attested or the absent one reported with count `0`.
- `PC-7` (**prospective — frozen here, before any executor exists**). On the
  registered sensing-price ladder:
  - `R1` the selected sensor is **monotone coarsening** in the price: for
    `pi <= pi'` the selected sensor at `pi'` is refined by the selected sensor
    at `pi` — no re-refinement anywhere, in any registered problem.
  - `R2` at least one registered control problem exhibits **three or more**
    distinct selected sensors across the ladder.
  - `R3` every transition price lies in the finite exact set
    `{ (V(T) - V(T')) / (cost(T) - cost(T')) }` over registered sensor pairs
    with `cost(T) != cost(T')`; no transition price falls outside it.
  - `R4` at a price strictly above `V_full - V_blind` divided by the minimal
    positive cost increment, the blind sensor is selected in **every**
    registered problem.
  - `R5` the price-ordered sensor sequence is **not** in general the
    predictive-sufficiency order: some registered problem selects, at some
    price, a sensor that is control-sufficient and **not** predictively
    sufficient for a registered `Y`, or the receipt records that no such
    problem exists.
  Each of `R1`-`R5` is recorded `HELD` or `FAILED` with its exact numbers. A
  `FAILED` prediction is reported, attributed to a single stage, and carries a
  recorded revival attempt.
- Two materially independent routes for every computational claim. Route B is
  written separately, imports nothing from route A, and computes `V(T)` by
  explicit enumeration of every deterministic policy measurable with respect to
  `T` rather than by the per-block maximisation route A uses.
- Hostiles must be shown to **move their target quantity** before they are
  shown to be **detected**.
- A null the true result beats, with the no-alarm case asserted on known-clean
  input.
- `RESULT_V1.json` byte-identical under `python3 -I -B` and `python3 -I -O -B`.

## Claim ceiling

`GMI_833_AE7_PREDICTION_TO_CONTROL_BOUNDARY_EXACTLY_SEPARATED_AND_PRICED_AT_REGISTERED_FINITE_SCOPE`

## Forbidden promotions

`PREDICTION_INSUFFICIENT_FOR_INTELLIGENCE_IN_GENERAL`,
`CONTROL_SUFFICIENCY_IMPLIES_PREDICTIVE_SUFFICIENCY`,
`PREDICTIVE_SUFFICIENCY_IMPLIES_CONTROL_SUFFICIENCY`,
`POMDP_BELIEF_SUFFICIENCY_REPROVED`,
`INFINITE_HORIZON_CONTROL_PROVED`,
`CONTINUOUS_STATE_EXTENSION_PROVED`,
`ENERGY_OR_TIME_PRICE_MEASURED`,
`ARCHITECTURE_SELECTION_LAW`,
`GMI_MORPHOLOGY_PREDICTION`,
`COMPLETE_GMI`.

Parent-owned and not claimed novel: belief-state sufficiency for POMDPs
(Åström 1965, doi:10.1016/0022-247X(65)90154-X; Smallwood & Sondik 1973,
doi:10.1287/opre.21.5.1071), sufficient information states (Striebel 1965),
the information theory of decisions and actions and rate-distortion control
(Tishby & Polani 2011, doi:10.1007/978-1-4419-1452-1_19; Rubin, Shamir & Tishby
2012, doi:10.1007/978-3-642-24647-0_3), thermodynamic/free-energy bounded
rationality (Ortega & Braun 2013, doi:10.1098/rspa.2012.0683), rational
inattention (Sims 2003, doi:10.1016/S0304-3932(03)00029-1), bounded rationality
(Simon 1955, doi:10.2307/1884852), value of information (Howard 1966,
doi:10.1109/TSSC.1966.300074) and bisimulation/state aggregation for MDPs
(Givan, Dean & Greig 2003, doi:10.1016/S0004-3702(02)00376-4). The residual is
the exhaustive exact-rational census over all 4140 sensors that separates
predictive from control sufficiency **in both directions with counts**, and the
priced sensor ladder with its five prospectively frozen predictions.
