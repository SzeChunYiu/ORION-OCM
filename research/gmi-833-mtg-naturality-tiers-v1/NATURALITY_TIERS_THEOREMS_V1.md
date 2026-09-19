# Named results — `gmi-833-mtg-naturality-tiers-v1` (issue #833, programme comment 5687604615)

Claim ceiling: `GMI_833_MTG_APPROXIMATE_AND_STOCHASTIC_NATURALITY_TIERS_AT_REGISTERED_FINITE_SCOPE`.

All results are exact statements about the registered fixtures of `FREEZE_V1.md`: three three-state
deterministic developmental systems `M, N, P` over experiences `{a, b}` (`N` isomorphic to `M`), one
two-state quotient `Q`, one path-dependence pair `(H, V)`, and three exact stochastic systems `SM, SN, SP`
plus an overclaim pair `(OM, ON)`. Two metrics are registered on target states: the discrete metric and a
path metric with half steps (`d ∈ {1/2, 1}`). Everything is checked by two materially independent routes
(`naturality_tiers_v1.py`: direct definitions with dictionary push-forward; `independent_oracle_v1.py`:
integer-indexed trajectory enumeration and vector–matrix kernel products), which agree on **86** shared
quantities. Every number below is reproducible from `RESULT_V1.json`. Parents are named by the aliases of
`PARENT_PINS_V1.json`.

---

## NAT-1 — the naturality defect is exact and composes subadditively

**Scope.** `eps(T) = max_{x,e} d_Y(T(Phi(x,e)), Psi(T(x),e))` for every total map `T` between fixture
systems: **9** hom-sets of **27** maps each (**243** maps), **19,683** composable pairs.

**Statement.** Under the discrete metric `eps(U∘T) ≤ eps(T) + eps(U)` on **19,683/19,683** composable
pairs (strict in **17,917**). Under the registered path metric the plain inequality fails on **17** pairs
(recorded, informational) while the Lipschitz-weighted bound `eps(U∘T) ≤ Lip(U)·eps(T) + eps(U)` holds on
**19,683/19,683**. The **13** maps with `eps = 0` recover the parent's exact square and trajectory
preservation on every word through length 5 (**2,457** trajectory checks; **10,395** composite trajectory
checks over the **55** composable exact pairs).

*Proof.* `d(U(T(Phi(x,e))), Xi(U(T(x)),e)) ≤ d(U(T(Phi(x,e))), U(Psi(T(x),e))) + d(U(Psi(T(x),e)), Xi(U(T(x)),e))`;
the first term is at most `Lip(U)·eps(T)` and the second at most `eps(U)`. Every map is 1-Lipschitz for the
discrete metric. Trajectory preservation at `eps = 0` is the parent's induction on word length.

**Quantifiers.** For all maps in the nine hom-sets and all composable pairs.

**Assumptions.** Finite deterministic systems sharing the experience alphabet; a registered metric on
target states satisfying the metric axioms (validated at construction).

**Dependencies.** Parent `P02` (TRANS-2A: exact naturality, identity, composition, trajectory preservation)
is the `eps = 0` case; NAT-1 extends it to a quantitative defect.

**Falsifiers.** Any composable pair violating the discrete-metric bound; any `eps = 0` map failing
trajectory preservation; a Lipschitz-weighted bound violation under the registered metric.

**Strongest parents.** Approximate homomorphisms and quantitative bisimulation distances (Desharnais,
Gupta, Jagadeesan & Panangaden, *Theoretical Computer Science* 318 (2004), doi:10.1016/j.tcs.2003.09.013;
van Breugel & Worrell, *Theoretical Computer Science* 331 (2005), doi:10.1016/j.tcs.2004.09.035). `P02`
owns the exact case. Nothing here is a new metric-space theorem.

**Forbidden extrapolations.** `CONTINUOUS_STATE_NATURALITY_PROVED`; no claim for non-Lipschitz metrics or
infinite state spaces.

---

## NAT-2 — three tiers, defined and separated by exact witnesses

**Scope.** Tiers on total maps: `STATIC` (protected labels preserved), `LEARNING_COMPATIBLE(a)` (labels
preserved and `eps ≤ a`, registered `a = 1/2` under the path metric), `EXACT` (`eps = 0`), `FULL` (`eps = 0`,
bijective, inverse exactly natural). Complete census over all **243** three-state maps and all **8**
two-state maps, under both metrics.

**Statement.** Under the registered metric the three-state census is STATIC **36**, LC **24**, EXACT **9**,
FULL **5**; the inclusions `FULL ⊂ EXACT ⊂ LC(a) ⊂ STATIC` hold on **243/243** maps and every inclusion is
strict: `|EXACT∖FULL| = 4`, `|LC∖EXACT| = 15`, `|STATIC∖LC| = 12`, each with a recorded witness map
(FULL: the isomorphism `M→N`; EXACT∖FULL: the collapse `m2→n1`; LC∖EXACT: `M→P`, `m1,m2→p1`, `eps = 1/2`;
STATIC∖LC: `M→P`, `m1,m2→p2`, `eps = 1`). Under the discrete metric `LC(1) = STATIC` (recorded as a check),
which is why a graded metric is needed to separate the middle tier. The two-state census has FULL **0**
(no bijection exists), EXACT **1**.

**Quantifiers.** For all maps of both fixtures, both metrics.

**Assumptions.** The registered level `a` is strictly between `0` and the metric's maximum.

**Dependencies.** NAT-1 (the defect); `P02` for the static-vs-exact distinction, which this result refines
to four levels.

**Falsifiers.** An inclusion failure; an empty difference set where a witness is claimed; a witness whose
recomputed `eps` contradicts its tier.

**Strongest parents.** Compiler correctness as static behaviour preservation versus bisimulation as
dynamic equivalence (Milner, *Communication and Concurrency*, Prentice Hall 1989); `P02`. The tier lattice
is a bookkeeping device over parent notions, not new mathematics.

**Forbidden extrapolations.** `OPTIMIZER_EQUIVALENCE_PROVED`, `REAL_LEARNING_DYNAMICS_VALIDATED`; the
tiers classify state maps between finite update laws, not training procedures.

---

## NAT-3 — path dependence is tracked, not erased by final-output equivalence

**Scope.** The pair `(H, V)` with `T = (h0→v0, h1→v2, h2→v1)`, all **15** words through length 3 from
every start state (**45** tracker rows).

**Statement.** Final outputs agree on **45/45** rows (a final-output-only check reports **0** mismatches)
while the per-prefix tracker reports **34** state mismatches in **14** rows (`eps(T) = 1`). The hysteresis
witness in `H`: from `h0`, the experience orders `ab` and `ba` reach the distinct states `h1` and `h2` that
carry the same label `1`.

**Quantifiers.** For all registered words and start states of the pair.

**Assumptions.** Tracking compares intermediate states after transport, not only outputs.

**Dependencies.** NAT-1 (the defect the tracker refines); `P09`/`P23` own hysteresis in the choice
setting, which this result does not re-claim.

**Falsifiers.** A final-output-only check that reports the mismatches; a tracker that reports zero on this
pair; a hysteresis witness whose two words reach the same state.

**Strongest parents.** History dependence in transition systems is elementary; `P23` HYST-1 owns the
developmental-trajectory hysteresis law at its scope. This result only exhibits the erasure hazard for
naturality checks.

**Forbidden extrapolations.** `UNIVERSAL_HYSTERESIS`; nothing about real learning trajectories.

---

## NAT-4 — stochastic kernels: exact defect interval, subadditivity, and the deterministic-overclaim hostile

**Scope.** Exact row-stochastic kernels on `SM, SN, SP` (denominators 2 and 4); `tv(T) = max_{x,e}
TV(T_* K_M(x,e), K_N(T(x),e))`; all **243** maps and **19,683** composable pairs.

**Statement.** `tv(U∘T) ≤ tv(T) + tv(U)` on **19,683/19,683** pairs (strict in **18,882**); observed `tv`
values are `{0, 1/2, 3/4, 1}`; lifting the deterministic fixture to point-mass kernels reproduces `tv = eps`
under the discrete metric on **243/243** maps (**0** failures); the reported object is the exact interval
`[0, tv(T)]` (the isomorphism `SM→SN` gives `[0, 0]`). Deterministic-overclaim hostile: for `(OM, ON)` the
mode-projected deterministic systems commute exactly (`eps = 0`) while the true kernels have `tv = 1/4`,
interval `[0, 1/4]`; a checker that projects to the mode passes and the exact checker refuses. Null:
**0/200** seeded random exact kernels (denominator 4, resample-until-different from the truth) have `tv = 0`;
minimum drawn `tv = 1/2`.

*Proof of subadditivity.* Push-forward is 1-Lipschitz in total variation, so
`TV(U_*T_*K_M, K_P∘U) ≤ TV(U_*T_*K_M, U_*K_N∘T) + TV(U_*K_N∘T, K_P∘U) ≤ tv(T) + tv(U)`.

**Quantifiers.** For all maps and composable pairs of the stochastic fixture; 200 null draws.

**Assumptions.** Exact rational kernels; floats and non-normalized rows are rejected at construction.

**Dependencies.** `P24` (STOCH-1..6: exact kernel object, composition, relabeling covariance, `UNC-BND`
boundary); NAT-1 for the deterministic specialization.

**Falsifiers.** A pair violating `tv` subadditivity; a lifted deterministic map with `tv ≠ eps`; the
overclaim pair passing the exact checker; any null draw with `tv = 0`.

**Strongest parents.** Total-variation contraction under Markov kernels and push-forwards (Levin & Peres,
*Markov Chains and Mixing Times*, AMS 2017, ch. 4); probabilistic bisimulation metrics as above. `P24`
owns the kernel object.

**Forbidden extrapolations.** `BAYESIAN_OR_LATENT_UNCERTAINTY_CLAIMED` (the interval is a predictive
defect bound, not a confidence set; `P24`'s `UNC-BND` is inherited); no claim about learned stochastic
policies.
