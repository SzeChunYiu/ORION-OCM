# Named results — `gmi-833-mtg-groupoid-hom-v1` (issue #833, programme comment 5687604615)

Claim ceiling: `GMI_833_MTG_REGISTERED_RELABELING_ACTION_ON_DERIVATION_RECORDS_AND_TYPED_HOM_COMPOSITION_AT_REGISTERED_FINITE_SCOPE`.

Every result is an exact statement about the registered finite fixture of `FREEZE_V1.md` (five
three-state presentations `M1..M5`, two actions, three intervention labels, two history tokens) and is
checked exhaustively by two materially independent routes (`groupoid_hom_v1.py`, `independent_oracle_v1.py`).
The analytic arguments are given where they are general; the exhaustive runs are certificates of the
implementation, not the proofs. Every number below is reproducible from `RESULT_V1.json`.
Parents are named by the aliases of `PARENT_PINS_V1.json`.

---

## GRP-1 — the registered relabeling group acts on derivation records, and the action groupoid is a groupoid

**Scope.** Derivation records `D = (M, obs, hist)` with `M` a three-state presentation, `obs` its
observation table on all words of length ≤ 3, `hist` a token sequence; the group
`G = Sym(X) × Sym(T)` (12 elements) acting by transport of every state-indexed component and renaming of tokens.

**Statement.** The identity acts trivially (**5/5** records); `(g·h)·D = g·(h·D)` for every ordered pair
(**720/720**); `g⁻¹·(g·D) = D` (**60/60**). The action groupoid `G ⋉ Orbit(D)` — objects the orbit elements,
morphisms `(g, D): D → g·D`, composition `(g′, g·D)∘(g, D) = (g′g, D)` — has associative composition
(**1728/1728** triples), identities and inverses. The orbit of `M1`'s record has exactly **12** elements
(no nontrivial automorphism).

**Quantifiers.** For all records of the fixture, all `g, h ∈ G`, all triples in `G³`.

**Assumptions.** Relabelings are bijections of a fixed state set and of a fixed token alphabet; the
observation table is recomputed after transport, never copied.

**Dependencies.** Parent `P03` (GAUGE-1A) owns the groupoid of state relabelings on mechanism
presentations; this result extends the object being acted on to a derivation record (presentation +
recomputed observations + history) and checks the action axioms rather than only invariance.

**Falsifiers.** Any pair with `(gh)·D ≠ g·(h·D)`; an identity that changes a record; an inverse that
does not return it; a non-associative composition of groupoid morphisms.

**Strongest parents.** Group actions and action groupoids are textbook algebra (any text on group
actions; e.g. Mac Lane, *Categories for the Working Mathematician*, Springer 1998, for the action
groupoid as a category). Nothing here is new mathematics. `P03` owns the mechanism-presentation instance.

**Forbidden extrapolations.** `UNIVERSAL_GRAMMAR_NEUTRALITY_PROVED`; no claim about relabelings that are
not bijections of the registered state set or that change description length (parent `P15`'s
`RELABEL-2` counterexample stands).

---

## GRP-2 — every registered conclusion commutes with the action

**Scope.** The four registered conclusions of the freeze: canonical fingerprint (route A: minimum over all
state numberings; route B: breadth-first numbering from the initial state), recomputed observation
table, membership of the record's quotient class in the Pareto-minimal set of the population's raw
resource vectors, and membership of its class in the forward ball of radius `4` around `M1`'s class under
the registered transform graph and price vector `(1,1,1)`.

**Statement.** For every record and every `g ∈ G`, all four conclusions computed on the relabeled
population equal those computed on the original (**60/60** checks, both routes). `M1` and its relabeled
copy `M4` share one class; the population has exactly **4** distinct classes, **1** Pareto-minimal class
and **3** ball members. Every hostile that couples a neutral rename to a label, transition,
intervention-response, resource or history mutation is refused (`OBSERVATION_CHANGED` or
`SEMANTIC_OR_RESOURCE_MUTATION`), and a non-bijective map is refused (`NOT_BIJECTIVE`): **6/6**
hostiles applicable and detected. Null: **0/200** seeded random maps `X→X` (non-bijective, or bijective
with a forced label flip) are accepted as valid group elements.

**Quantifiers.** For all records, all `g ∈ G`, all four conclusions.

**Assumptions.** Conclusions are functions of the quotient class and of quantities the action leaves
untouched (resources, graph burdens); the transform graph is indexed by classes, not by names.

**Dependencies.** GRP-1 (the action is an action); `P03` for fingerprint invariance of a single
presentation; `P04`/`P01` for the ball and burden objects the conclusion reuses.

**Falsifiers.** A conclusion that differs across an orbit; a hostile accepted as a valid relabeling; any
null draw accepted; disagreement between the permutation-minimum and breadth-first canonical forms on
which presentations are equivalent.

**Strongest parents.** Graph-isomorphism invariants and canonical labeling (McKay & Piperno,
*J. Symbolic Computation* 60 (2014), doi:10.1016/j.jsc.2013.09.003); Myhill–Nerode canonical forms for
deterministic transition systems. `P03` owns fingerprint invariance; `P16`/`P17` own invariance of
reachability fractions and cluster membership under operation-token relabelings at their scopes.

**Forbidden extrapolations.** `REACHABILITY_INVARIANCE_PROVED`, `SEARCH_PRIOR_INVARIANCE_PROVED` (see GRP-3).

---

## GRP-3 — search-order statistics are not invariant (boundary, earned by counterexample)

**Scope.** The first-hit statistic: the first record, in the lexicographic order of serialized
presentations, whose observation table equals `M1`'s.

**Statement.** Before the state swap `s1 ↔ s2` the first hit is **`M2`**; after applying the swap to the
whole population it is **`M4`**. The statistic is therefore not a function of the quotient class:
representation invariance (GRP-2) and search-order invariance are separated by an exact witness.

**Quantifiers.** Existential: one registered swap suffices.

**Assumptions.** The enumeration order is a registered lexicographic order on serialized presentations.

**Dependencies.** GRP-2 (the same population whose conclusions are invariant).

**Falsifiers.** The first hit being equal before and after the swap under this order.

**Strongest parents.** `P03` §7 (budget-one forward/reverse control), `P07` FSB-6 (order dependence of
finite-budget choice), `P15` RELABEL-2. This result only re-exhibits the boundary inside the record
population of GRP-2; it claims nothing new about search.

**Forbidden extrapolations.** No claim that every search statistic is order-dependent, nor that any is invariant.

---

## HOM-1 — typed composition laws, identities, associativity, and soundness of every declared field

**Scope.** Typed transforms `T = (s, t, τ, ε, unc, ρ, A, E, I, tier)` between fixture presentations
`M1, M2, M3, M5`; `Hom(M,N)` = all total label-preserving state maps (**48** maps over **16** ordered pairs;
tier census EXACT **4**, APPROX **4**, STATIC **40**). The defect `ε(τ) = max_{x,a} d_N(τ(δ_M(x,a)), δ_N(τ(x),a))`
uses the label-graded metric `d_N ∈ {0, ½, 1}` (`½` = different states, same label; `1` = different labels);
`tier_of(ε)` is EXACT at `0`, APPROX at `≤ ½`, STATIC otherwise.

**Statement.** Composition `U∘T` adds `ε`, adds the uncertainty interval endpointwise, adds `ρ`
coordinatewise, unions assumptions (conflict → refuse), unions evidence kinds, intersects intervention
contracts, and takes the minimum tier. Identities are two-sided (**96/96**); composition is associative on
every composable triple of the chain `M1→M2→M3→M5` (**32/32**). Over all **576** composable pairs, every
declared field of the composite is sound against recomputation from the composite map: recomputed
`ε ≤` declared `ε` (**576/576**, hence `ε` is subadditive), recomputed tier `≥` minimum tier (**576/576**),
recomputed contract `⊇` intersected contract (**576/576**). Equality with recomputation is **not** claimed:
the recomputed tier is strictly better in **20/576** pairs (the recorded witness composes the involution
`s1↔s2` on `M1` with itself: two STATIC maps whose composite is the identity), and the recomputed contract
is strictly larger in **64/576**. The summed-`ε` bound `tier_of(ε_T+ε_U)` is also sound (**576/576**) and is
coarser than the minimum rule in **4** pairs.

*Proof of the minimum rule.* Both maps preserve labels, so for every cell the three states
`U(T(δ_M(x,a)))`, `U(δ_N(T(x),a))`, `δ_P(U(T(x)),a)` carry the same label whenever the mismatches of `T`
(at `(x,a)`) and of `U` (at `(T(x),a)`) are within-label; a within-label mismatch composed with a
within-label mismatch is within-label, so `ε(U∘T) ≤ ½` whenever `ε(T), ε(U) ≤ ½`, and `ε(U∘T) = 0` when
both are `0` (the parent's exact naturality composition). *Proof of the summed bound.* A label-preserving
map is 1-Lipschitz for `d`, so the triangle inequality through `U(δ_N(T(x),a))` gives
`ε(U∘T) ≤ ε(T) + ε(U)`.

**Quantifiers.** For all maps in the 16 Hom sets, all composable pairs and all composable triples on the chain.

**Assumptions.** Declared atomic costs are functions of the map's semantic content only
(`ρ = (4ε, |X| − |image τ|, 1)`, `unc = [ε/2, ε]`); every atomic map declares `ε` and its recomputed tier.

**Dependencies.** `P01` TRANS-1A (identity/associativity and additive error/resource laws, assumption
consistency, evidence union with a neutral identity marker); `P02` TRANS-2A (exact naturality composes).
This result adds the interval, contract and tier fields and the soundness theorem.

**Falsifiers.** An identity that alters a field; a composable triple that depends on parenthesization;
any composite whose recomputed `ε`, tier or contract is worse than declared; a field composition law
that disagrees with the freeze.

**Strongest parents.** Categories of typed morphisms with cost annotations are parent mathematics
(Lawvere, *Rend. Sem. Mat. Fis. Milano* 43 (1973), doi:10.1007/BF02924844); soundness of declared
lower bounds is the usual contract-refinement reading (Hoare-style specifications). `P01` owns the
category; nothing here is new category theory.

**Forbidden extrapolations.** `DEVELOPMENTAL_EQUIVALENCE_PROVED`; no equality between declared and
recomputed fields; no claim beyond the registered fixture and the label-graded metric.

**Correction of the record.** The first run defined `ε` as the *fraction* of failing cells. That object
is not carried along a state map that collapses states: subadditivity failed in **2/576** pairs and the
minimum tier rule in **10/576** (recorded in `RESULT_V1.json` under `first_run_negative_and_revival`).
The single-stage attribution is the fraction measure; the lever is the max-form defect over the
label-graded metric. The test module re-derives one failing pair of the refuted object on every run.

---

## HOM-2 — composition fails closed, including on evidence loss

**Scope.** Construction and composition of typed transforms on the fixture.

**Statement.** Endpoint mismatch, assumption conflict, negative error, negative resource, malformed
uncertainty interval, missing ordinary evidence, float input, a declared tier above the recomputed tier
(`TIER_OVERCLAIM`), a declared `ε` below the recomputed defect (`EPS_UNDERCLAIM`), a declared contract not
preserved by the map (`CONTRACT_OVERCLAIM`), and a composite whose union of evidence kinds lacks a kind
required by the target class (`EVIDENCE_LOSS`) each refuse rather than return a transform:
**11/11** hostiles applicable and detected. The no-alarm case holds: when one component carries the
required kind, the composite is accepted.

**Quantifiers.** One registered instance per branch, each with an `applicable` flag proving the
perturbation moved the guarded quantity.

**Assumptions.** Required evidence kinds are registered per target class before composition.

**Dependencies.** `P01`'s fail-closed hostiles (endpoint, assumption, evidence, negative values) are the
parent set; `EVIDENCE_LOSS`, `TIER_OVERCLAIM`, `EPS_UNDERCLAIM`, `CONTRACT_OVERCLAIM` are added here.

**Falsifiers.** Any branch that returns a transform; any hostile whose `applicable` flag is false.

**Strongest parents.** Fail-closed validation is engineering practice, not a theorem; `P01` owns the pattern.

**Forbidden extrapolations.** No claim that the eleven branches exhaust the ways a transform can be malformed.

---

## HOM-3 — registered relabelings of source and target induce a bijection of Hom sets preserving every field

**Scope.** For each ordered pair `(M,N)` of fixture presentations and each pair of relabelings
`r: M→M′`, `s: N→N′` to fresh state names (**36** pairs per ordered pair, **576** in all), the conjugation
`τ ↦ s∘τ∘r⁻¹`.

**Statement.** Conjugation is a bijection `Hom(M,N) → Hom(M′,N′)` (**576/576** relabeling pairs; Hom sizes
equal) and every conjugate carries the same `ε`, interval, resources, contract and recomputed tier as its
preimage (**1728/1728** maps checked, both routes). Hence equivalent presentations of source and target
have isomorphic typed transform sets at the registered scope.

**Quantifiers.** For all 16 ordered pairs, all 36 relabeling pairs, all maps.

**Assumptions.** Relabelings are bijections of state sets; declared atomic costs depend only on the map's
semantic content (as in HOM-1).

**Dependencies.** GRP-1 (transport of presentations), HOM-1 (the fields being preserved).

**Falsifiers.** A conjugate outside `Hom(M′,N′)`; two maps with the same conjugate; any field changed by
conjugation.

**Strongest parents.** Transport of structure along isomorphisms is elementary; `P03` owns the
presentation-level invariance. Nothing new mathematically; the residual is the typed-Hom instance with
the field-preservation check.

**Forbidden extrapolations.** `HOM_SETS_ISOMORPHIC_BEYOND_REGISTERED_RELABELINGS`: no claim for maps that
are not bijective relabelings, nor for grammar changes that alter description length or search geometry.
