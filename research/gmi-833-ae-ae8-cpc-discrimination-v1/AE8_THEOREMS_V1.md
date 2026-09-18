# AE8 named results

Every result is stated at the registered finite scope of `FREEZE_V1.md`, using
only the grid, integer description lengths, tie-break, classifier criteria and
null size of `PROSPECTIVE_REGISTER_V1.json`. All quantities are exact `Fraction`
or `int`; information-theoretic values are carried as exact rational
combinations `sum_p c_p log2(p)` and compared by the integer identity

    sign( sum_p c_p log2 p ) = sign( prod_p p^(c_p L) - 1 ),  L > 0 clearing
                               the denominators of the c_p,

so no float and no numeric bound is ever needed. Route A is
`ae8_cpc_discrimination_v1.py`, route B is `independent_cpc_oracle_v1.py`, and
the two agree on every reported value.

The registered universe is the three-bit cube with the uniform measure. A
**model** is a code map, a per-cell prediction and a per-cell action; its
**term vector** `v(m) = (cost, predictive loss, control regret)` is DERIVED from
that object — the cost from a Kraft-compliant prefix-free encoding of the
partition and the decision tables, the predictive loss by counting errors
against the target, the control regret from the exact value difference. Nothing
is carried as a flag. The registered model space has `4110` members and each of
the `12` registered worlds carries `4` of them, chosen by a deterministic rule.

---

## AE8-1 — the objective family, reported over the whole frozen grid

*Scope.* The `45` weight triples of eighths summing to one.
*Quantifiers.* Every claim below is reported at every one of them.

`J_lambda(m) = l_C cost(m) + l_P predloss(m) + l_K ctrlloss(m)`, with argmin ties
broken by the frozen ascending name order. No weight is chosen after a result is
seen: the receipt carries the agreement count at every grid index, and any claim
that holds only on a sub-region names that region. The best agreement with the
registered preference is `4` of `12`, attained at grid indices `1` through `5`
among others.

**Assumptions.** The grid, the tie-break and the description-length integers are
frozen in the register, whose self-digest the executor rechecks.
**Dependencies.** The derived term vectors.
**Falsifiers.** A reported claim that holds at one weight and is stated without
its region; an argmin that disagrees with an explicit re-sort.
**Strongest parents.** Scalarised multi-objective optimisation; nothing novel.

---

## AE8-2 — CPC is a decomposition at the registered scope, not a theorem

*Scope.* The `12` registered worlds and the frozen classifier criteria.
*Quantifiers.* The criteria are evaluated in the register's own order.

The ladder is `THEOREM` false, `VARIATIONAL_PRINCIPLE` false, `DECOMPOSITION`
**true**, `HEURISTIC` false, `SLOGAN` true, so the verdict is the first that
holds: `DECOMPOSITION`.

The two halves are worth stating separately, because they point in opposite
directions and both are reported. On the unrestricted roster the best weight
agrees on `4` of `12` worlds while the randomized control reaches as high as `7`
and `74` of its `200` draws reach `4` or more: the CPC family does **not** beat
chance there. Once the registered preference is restricted to the stated
condition — its structural-attribute key deleted, so that every key it uses is a
function of the term vector — a single weight (grid index `8`) reproduces it on
**all `12`** worlds.

That is exactly what `DECOMPOSITION` means in the frozen criteria: agreement
holds on every world only after restricting to a stated registered condition.
CPC decomposes the part of the preference the term vector determines, and is at
chance on the part it does not.

**Assumptions.** The classifier criteria and null size are frozen; the
randomized control is a uniformly random model per world, drawn from a
generator read at its high bits.
**Dependencies.** AE8-1, AE8-4, the null.
**Falsifiers.** A weight reaching `12` of `12` on the unrestricted roster; a
restricted agreement below `12`; a control distribution with no variance, which
would mean the sampler, not the result, was being reported.
**Forbidden extrapolation.** `DECOMPOSITION` is a verdict about this roster
under this preference. It is not a claim that CPC is or is not a theorem in
general, and `CPC_IS_A_THEOREM` is a registered forbidden promotion.
**Strongest parents.** Minimum description length (Rissanen 1978,
doi:10.1016/0005-1098(78)90005-5; Grunwald 2007,
doi:10.7551/mitpress/4643.001.0001); rate-distortion (Shannon 1959; Berger
1971); resource-rational analysis (Lieder and Griffiths 2020,
doi:10.1017/S0140525X1900061X).

---

## AE8-3 — which registered laws are corollaries of a minimal objective

*Scope.* The six registered laws and the `7` non-empty subsets of the term basis
crossed with the frozen grid. *Quantifiers.* Exhaustive over that space.

For each law the search reports the minimum-cardinality objective whose argmin
reproduces the law's choice on every world the law covers. `AE6_LOCALITY` and
`AE15_MODEL_NECESSITY` are `COROLLARY`. `AE2_NO_PREDICTIVE_INFORMATION` and
`AE12_AMBIGUITY_INDEPENDENCE` are `NOT_A_COROLLARY`.
`AE1_BUDGET_MONOTONE` and `AE10_USABLE_SEPARATION` are
`NOT_APPLICABLE_ON_ROSTER`: their triggers never fire here, and that is reported
rather than glossed.

**Assumptions.** The term basis is `(cost, predictive loss, control regret)`.
**Dependencies.** AE8-1. **Falsifiers.** An objective in the searched space
reproducing a law marked `NOT_A_COROLLARY`; a law marked `COROLLARY` whose
witness fails on one of its covered worlds.
**Strongest parents.** No parent is claimed for the search itself; the laws it
tests are the registered results of the neighbouring AE tranches.

---

## AE8-4 — the irreducibility theorem: what CPC structurally cannot see

*Scope.* Every objective in the registered term basis and every weight in the
frozen grid. *Quantifiers.* Universally quantified over both.

`J_lambda(m)` depends on `m` **only through** `v(m)`. Hence any two models with
`v(m1) = v(m2)` receive exactly equal objective value at every weight, and the
choice between them is settled by the frozen name order rather than by anything
outside the term vector. A phenomenon whose registered preference distinguishes
such a pair is therefore not reducible to CPC without an additional term.

The evidence is a search, not a stipulation: over the `4110`-model space the
executor finds, for each named term, the first pair in the frozen enumeration
order whose **derived** term vectors are equal element-wise, whose objects
differ, and which differ on that attribute alone.

| term | world | derived term vector | status |
|---|---|---|---|
| communication | `W03` | `(29, 0, 1/4)` | irreducible at the registered scope |
| development | `W02` | `(16, 1/2, 1/2)` | irreducible at the registered scope |
| history | `W04` | `(16, 1/2, 1/2)` | irreducible at the registered scope |
| uncertainty | `W05` | `(16, 1/4, 1/2)` | irreducible at the registered scope |
| verification | — | — | **not proved irreducible** |

Four of the five named terms are proved irreducible at the registered scope.
`verification` is reported as **not proved irreducible**: no pair differing in
verifiability alone, with all four other attributes equal and exactly equal
derived term vectors, exists in the registered model space. That is a statement
about what was found, never a claim that verification is reducible.

Each colliding pair also carries a mirror observation: because the two models
receive exactly equal objective value, exchanging their names exchanges the CPC
choice, so the impossibility does not depend on which tie-break was frozen.

**Assumptions.** The objective is a function of the term vector; the attributes
are computed from the model object; the model space is the registered one.
**Dependencies.** The derived cost, predictive loss and control regret.
**Falsifiers.** A colliding pair whose term vectors are not in fact equal; a pair
differing in more than its own attribute; an objective in the registered basis
that separates a colliding pair; a collision for `verification` in the
registered model space, which would move that row from not-proved to proved.
**Forbidden extrapolation.** Irreducibility is claimed at the registered scope
and for the registered basis only. Nothing here says the phenomenon is
irreducible to some larger objective, and the receipt names the extra term each
collision calls for.
**Strongest parents.** The arity argument is elementary. Its content is in the
computed collisions, not in the observation that a function of `v` cannot
separate arguments with equal `v`.

---

## AE8-5 — the agreement matrix against eight alternative master principles

*Scope.* `MDL`, cardinality-constrained rate-distortion, bounded rationality,
predictive information, active inference, control as inference,
algorithm selection and resource-rational computation, each an exact choice
rule.
*Quantifiers.* Every ordered pair, every world.

Agreement with the registered preference, out of `12`: predictive information
`5`, CPC `4`, active inference `3`, algorithm selection `3`, control as
inference `3`, resource-rational `3`, MDL `2`, bounded rationality `1`,
rate-distortion `1`. The full pairwise matrix is in the receipt as exact integer
counts.

Four of the alternatives — algorithm selection, bounded rationality, control as
inference and rate-distortion — coincide with some member of the CPC family at
some weight of the frozen grid, and the receipt names them. That is a structural
observation about the family, not a ranking.

**Assumptions.** The rate-distortion rule is the cardinality-`1` constrained
optimum and the receipt asserts that constraint is feasible in every world;
control as inference is the regret minimiser, which is the choice any monotone
optimality likelihood yields.
**Dependencies.** The exact logarithmic comparisons for predictive information
and active inference. **Falsifiers.** A world where the cardinality-`1`
constraint is infeasible and the rule was silently relaxed; a disagreement
between the two routes on any count.
**Strongest parents.** Each principle is its authors'; see
`PARENT_OWNERSHIP_V1.md`.

---

## AE8-6 — the preregistered discriminating world

*Scope.* The disagreement AE12 registered before any implementation blob of this
package existed. *Quantifiers.* The three principles named there.

AE12's register commit precedes every implementation blob here, and its world
`W_DISC1` predicted a disagreement: expected free energy chooses `a1`,
cardinality-`1` rate-distortion control chooses `a0`, and no weight of this same
`45`-point grid reproduces both. That half of the prediction was confirmed in
AE12's receipt; the clause predicting that CPC would reach all three actions was
refuted there and reported as refuted.

The register of **this** package names `the frozen predicted disagreement sets`
but does not enumerate them per world. That gap is disclosed in the receipt, and
the per-world disagreements of this package are therefore reported as
measurements rather than as confirmed predictions. Calling a measurement a
confirmed prediction is the failure mode pre-registration exists to prevent.

**Assumptions.** AE12's register is committed earlier in the same branch.
**Dependencies.** AE12's receipt. **Falsifiers.** An AE12 register commit that
does not precede this package's implementation; a disagreement reported as
preregistered without a register entry.
**Strongest parents.** Pre-registration practice; no technical parent.

---

## AE8-7 — observational equivalence where no registered experiment discriminates

*Scope.* Principle pairs agreeing on every one of the `12` registered worlds.

Exactly one pair does: bounded rationality and cardinality-`1` rate-distortion
control. It is emitted as `OBSERVATIONALLY_EQUIVALENT_AT_REGISTERED_SCOPE`.
Equivalence on a finite registered roster is **not** identity: it says only that
no registered world discriminates them, and it licenses no promotion of either
member over the other. `OBSERVATIONAL_EQUIVALENCE_IMPLIES_IDENTITY` is a
registered forbidden promotion.

**Assumptions.** The roster is finite and registered.
**Dependencies.** AE8-5. **Falsifiers.** A registered world on which the pair
differs; a promotion of either member anywhere in the package.
**Strongest parents.** Underdetermination of theory by finite evidence; no
technical parent claimed.

---

## AE8-8 — the master-law claim is withheld

*Scope.* The registered roster, the frozen integer description lengths and the
stated Pareto decision rule. *Quantifiers.* Both legs of the row's condition.

The row permits calling CPC the master law only if it beats the bag-of-laws
baseline **and** survives parent discrimination. Both legs are run.

*Leg one.* The baseline is the frozen priority union of the laws that are
**valid on the roster** — a law that is wrong on the worlds it covers is
reported as `REFUTED_ON_ROSTER` and excluded, and `AE12_AMBIGUITY_INDEPENDENCE`
is so reported, correct on `3` of the `4` worlds it covers. The valid laws cover
`10` of `12` worlds and agree on all `10`, at `54` description bits. CPC's best
is `4` of `12` at `12` bits. Neither Pareto-dominates the other, so CPC does not
beat the baseline. The frozen integers cannot be tuned to change this: the
agreement counts already separate, and the corresponding hostile demonstrates
the verdict is invariant to them.

*Leg two.* The number of registered worlds on which CPC's choice differs from
**every** registered parent principle is `0`. CPC says nothing here that no
parent says.

Both legs fail, so the receipt emits the registered terminal
`CPC_MASTER_LAW_CLAIM_WITHHELD` and the manifest carries
`CPC_IS_THE_GMI_MASTER_LAW` as a forbidden promotion. Withholding is the closure
this row asks for. It is **not** evidence against the parent principles, and
`CPC_MASTER_LAW_CLAIM_WITHHELD_IS_A_NEGATIVE_RESULT_ABOUT_PARENTS` is itself a
registered forbidden promotion.

The baseline is falsifiable rather than perfect by construction: it covers `10`
of `12` worlds, so `2` are uncovered, and the receipt asserts the coverage is
strictly below the world count. A baseline covering every world by construction
could be neither beaten nor missed, and would make this row unfalsifiable.

**Assumptions.** The Pareto decision rule is stated in the receipt; the register
does not pin one, and that gap is disclosed.
**Dependencies.** AE8-2, AE8-3, AE8-4, AE8-5.
**Falsifiers.** A baseline covering all `12` worlds; a CPC weight Pareto
dominating the baseline; a world where CPC differs from every parent; a law
counted in the baseline while refuted on its own coverage.
**Forbidden extrapolation.** The withholding is a statement at the registered
scope about a registered roster. It does not say CPC is false, nor that some
other principle is the master law.
**Strongest parents.** Each comparator's authors; see `PARENT_OWNERSHIP_V1.md`.
