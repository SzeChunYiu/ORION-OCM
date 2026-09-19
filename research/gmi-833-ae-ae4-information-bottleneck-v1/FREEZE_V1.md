# GMI #833 Section AE4 — Information Bottleneck / relevant-information boundary: prospective freeze v1

Source `main`: `5e57d4292266bccf435136e1f7d72caa32e920a0`.

Committed **before** any executor, oracle, test, receipt, theorem note or
reconciliation file of this package exists in the tree.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE4 — Information Bottleneck / relevant-information boundary`

1. `- [ ] Formalize the task-relevant representation problem using established Information Bottleneck / rate-distortion terminology where applicable.`
2. `- [ ] Determine when a GMI minimal behavioral/predictive state is equivalent to, refines, or is incomparable with an IB-optimal representation.`
3. `- [ ] Prove smallest counterexamples preventing unqualified identification.`
4. `- [ ] Distinguish \`retain information about Y\` from \`retain information required for action/control under utility U\`.`
5. `- [ ] Derive conditions under which forgetting task-irrelevant information is optimal under resource constraints.`
6. `- [ ] Derive conditions under which apparently irrelevant information must be retained because of future task uncertainty, transfer, revision, causal intervention, or verifier needs.`
7. `- [ ] Quantify representation-capacity vs predictive/control distortion frontiers.`
8. `- [ ] Add held-out crossover predictions as memory/compute/precision prices change.`

**No neighboring row is earned here.** No AE1, AE2, AE3, AE5, AE7, AE8, AE10,
AE13 or other AE row, no row of any other issue comment, and no row of the #833
issue body, is earned by this tranche.

## A second correction to the section map, declared before implementation

`AE_SECTION_MAP_V1.md` states that the AE4 package "needs AE3's coding-language
registry". Read against the eight row texts above, that dependency is **not
load-bearing**: every AE4 row is an Information-Bottleneck / rate-distortion
obligation, and none of the eight consumes a prefix-code language, a program
length, or a description-length registry. This package therefore takes **no**
dependency on `gmi-833-ae-ae3-compression-learning-v1`, which in any case is not
on `main` at `source_main` and could only have been pinned to an open branch.

This is recorded in the same spirit as the morphology-sweep lane's correction:
the map's "receipts/registries already exist" claims are not to be trusted
without opening them.

## Frozen scope

- **Support.** `X` uniform on `{0,1}^3` — `8` atoms, each of exact mass `1/8`.
- **Worlds.** A registered finite family of joint laws `p(X, Y)`; `Y` finite.
  Both deterministic targets `Y = f(X)` and registered noisy channels
  `p(Y | X)` with **exactly rational** entries are admitted.
- **Encoders.** `T` ranges over the **deterministic** encoders: all set
  partitions of the 8-atom support. There are `Bell(8) = 4140` of them and the
  executor must enumerate all of them, not a sample.
- **Utilities.** A registered finite family of exactly rational utilities
  `U(y, a)` over a finite action set `A`, used for every control quantity.

## Frozen exact arithmetic — no logarithm is ever evaluated

Every entropy and mutual information in this package is carried as an exact
**rational combination of prime logarithms**: a value is a finite map
`q -> c_q` with `q` prime and `c_q` an exact `Fraction`, denoting
`sum_q c_q * log2(q)`. For a rational mass `p = a/b`, `-p*log2(p)` contributes
`+p*e` to `c_q` for each `q^e` in `b` and `-p*e` for each `q^e` in `a`.

Order is decided **exactly**, never numerically: the sign of
`sum_q c_q log2(q)` is the sign of `prod_q q^{D c_q} - 1`, where `D` is the
lowest common denominator of the `c_q`, an exact comparison between two
integers. Equality holds **iff** that product is exactly `1`.

No float appears in any claim. A value is reported as a plain rational only
when its prime support is `{2}`; otherwise it is reported in the exact
prime-log form. Any code path that would evaluate `math.log` is a package
defect and must be absent; the test asserts its absence by AST scan.

## Frozen definitions

- **GMI minimal predictive state** `T_GMI(W)`: the coarsest partition of the
  support that is sufficient for `Y`, i.e. the partition whose blocks are the
  level sets of the map `x -> p(Y | X = x)`. (For deterministic `Y = f(X)` this
  is the level-set partition of `f`.)
- **IB objective** at an exactly rational tradeoff `beta`:
  `L_beta(T) = I(T;X) - beta * I(T;Y)`, minimised over the registered encoder
  family. `IB*(W, beta)` is the **set** of minimisers, compared by exact sign,
  so ties are sets and are never silently broken.
- **Control value** `V(T, U)`: the best expected utility achievable by a policy
  measurable with respect to `T`, an exact rational.
- **Priced selection** at a price vector `pi`: `argmax_T [ V-or-predictive gain
  of T  -  pi . cost(T) ]` with `cost(T)` a registered exactly rational
  capacity vector (block count, memory bits, decision-precision cells).

## Registered scope restriction and the promotion it forbids

The IB optimum here is taken over **deterministic** encoders. This is the
*deterministic information bottleneck* setting (Strouse & Schwab 2017), not the
stochastic-encoder IB of Tishby, Pereira & Bialek 1999. The package must say so
in the receipt as a checked field, and
`IB_OPTIMUM_OVER_STOCHASTIC_ENCODERS_PROVED` is a registered forbidden
promotion. Closing row 2 or row 3 by silently reading the deterministic result
as the stochastic one is a package defect.

## Required evidence and falsifiers

- `IB-1`: the formalisation, with a machine-readable crosswalk mapping every
  introduced symbol onto its established parent name (IB, rate-distortion,
  deterministic IB, minimal sufficient statistic), each entry carrying a
  citation. Introducing a term with no crosswalk entry is a defect.
- `IB-2`: for **every** registered world and **every** `beta` on the frozen
  rational ladder, the relation between `T_GMI` and `IB*(W, beta)` is
  classified as exactly one of `EQUAL`, `GMI_STRICTLY_REFINES`,
  `IB_STRICTLY_REFINES`, `INCOMPARABLE`. Each relation that occurs is reported
  with its exact count and a named witness; each that does **not** occur is
  reported as absent with its own count of `0`, never omitted.
- `IB-3`: a **smallest** counterexample to unqualified identification of
  `T_GMI` with an IB optimum, minimality proved by **exhaustive** search over
  every strictly smaller instance (fewer support atoms, then fewer target
  values), so that minimality is a proved property and not a description.
- `IB-4`: a registered world, utility and pair of encoders in which the
  encoder that maximises `I(T;Y)` within a capacity class is **strictly**
  suboptimal for `V(T, U)`, and a second pair in which the ordering reverses.
  Both gaps exact.
- `IB-5`: an exactly stated condition under which discarding a distinction
  costs nothing under a capacity constraint, plus machine-checked witnesses on
  **both** sides of the boundary — one world where the condition holds and
  forgetting is optimal, one where it fails and forgetting strictly loses.
- `IB-6`: five named retention mechanisms — future-task uncertainty, transfer,
  revision, causal intervention, verifier need — each either carrying a witness
  in which a distinction that is provably irrelevant to the present `Y` is
  **necessary**, or declared `NOT_WITNESSED` in the receipt. Silence about a
  mechanism is a defect.
- `IB-7`: the exact capacity-versus-distortion frontier: for each capacity
  bound, the exact minimal achievable predictive distortion and the exact
  minimal achievable control distortion, with the Pareto set reported and its
  size counted. Predictive and control frontiers must be reported separately
  and shown to differ on at least one registered world, or shown to coincide
  everywhere with that reported as the finding.
- `IB-8` (**prospective — these predictions are frozen here, before any
  executor exists**). On the registered price ladder:
  - `Q1` the block count of the priced-selected encoder is **monotone
    non-increasing** as the memory price rises: no re-refinement anywhere on
    the ladder, in any registered world.
  - `Q2` at least one registered world exhibits **three or more** distinct
    selected encoders across the ladder — a genuine multi-stage transition, not
    a single on/off switch.
  - `Q3` every price at which the selection changes lies in the finite exact
    set of pairwise gain differences of the registered encoder family; no
    transition price falls outside it.
  - `Q4` at a memory price strictly above the maximal achievable gain, the
    one-block encoder is selected in **every** registered world.
  - `Q5` IB-optimality and price-optimality are **not** the same ordering:
    some registered encoder is in `IB*(W, beta)` for some ladder `beta` yet is
    selected at **no** price point, or the receipt records that no such encoder
    exists.
  Each of `Q1`-`Q5` is recorded `HELD` or `FAILED` with its numbers. A `FAILED`
  prediction is **not** deleted: it is reported, attributed to a single stage,
  and a revival attempt is recorded in the receipt.
- Two materially independent routes for every computational claim. Route B is
  written separately, imports nothing from route A, and the test asserts the
  independence by AST scan of route B's imports.
- Hostiles must be shown to **move their target quantity** before they are
  shown to be **detected**.
- A null the true result beats, with the no-alarm case asserted on known-clean
  input.
- `RESULT_V1.json` byte-identical under `python3 -I -B` and `python3 -I -O -B`.

## Claim ceiling

`GMI_833_AE4_IB_RELEVANT_INFORMATION_BOUNDARY_EXACTLY_CLASSIFIED_OVER_DETERMINISTIC_ENCODERS_AT_REGISTERED_FINITE_SCOPE`

## Forbidden promotions

`IB_OPTIMUM_OVER_STOCHASTIC_ENCODERS_PROVED`,
`GMI_PREDICTIVE_STATE_IS_THE_IB_OPTIMUM`,
`IB_OPTIMAL_IMPLIES_CONTROL_OPTIMAL`,
`INFINITE_SUPPORT_EXTENSION_PROVED`,
`CONTINUOUS_VARIABLE_EXTENSION_PROVED`,
`RATE_DISTORTION_THEOREM_REPROVED`,
`FORGETTING_IS_ALWAYS_OPTIMAL`,
`ENERGY_OR_TIME_PRICE_MEASURED`,
`ARCHITECTURE_SELECTION_LAW`,
`COMPLETE_GMI`.

Parent-owned and not claimed novel: the information bottleneck (Tishby, Pereira
& Bialek 1999), rate-distortion theory (Shannon 1959; Berger 1971; Cover &
Thomas 2006), the deterministic information bottleneck (Strouse & Schwab 2017,
doi:10.1162/NECO_a_00961), minimal sufficient statistics (Lehmann & Scheffé
1950, doi:10.1214/aoms/1177729695), the information-theoretic treatment of
decisions and actions (Tishby & Polani 2011,
doi:10.1007/978-1-4419-1452-1_19), rational inattention (Sims 2003,
doi:10.1016/S0304-3932(03)00029-1) and bounded rationality (Simon 1955,
doi:10.2307/1884852). The residual is the exact prime-log arithmetic that makes
the whole 4140-encoder comparison decidable without evaluating a logarithm, the
exhaustively proved smallest counterexample, and the priced-selection ladder
with its five prospectively frozen predictions.
