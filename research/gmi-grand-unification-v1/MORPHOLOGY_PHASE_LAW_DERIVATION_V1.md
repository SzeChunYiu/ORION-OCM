# Grand GMI Morphology Phase Law — Derivation Layer V1

Date: 2026-09-13; scoped selection repair recorded in receipt V2.
Status: **DERIVED LOWER BOUNDS; SELECTION INSUFFICIENT IN GENERAL**

Authority: `RECURSIVE_GAP_AUDIT_20260913.md`,
`FAMILY_PHASE_SOUNDNESS_CORRECTION_V1.md` and
[MSC-1--3](CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md).

## 1. What is derived

The family-phase theorem compares bounds `L_F,U_F` whose validity must be
supplied. This module derives a family lower bound from proved necessities
and sound accounting. Its unconditional output is a lower bound; independently
proved feasibility, attainment, coverage or tightness can make it decisive.
It supplies no empirical resource measurement or unrestricted family winner.

Register allocation domain `X`, proved necessities `N`, structural family
predicates `sigma_F`, resource accounting map `A`, and scalar functional `J`.
`A` is nondecreasing in allocation coordinates; `J` is nondecreasing in every
resource coordinate. Coordinates with no proved necessity have only their
registered nonnegativity restriction. Families are structural predicates,
not historical architecture names (MS-5).

The load-bearing coverage and accounting contract is:

- Every feasible machine covered by the family claim maps to `x(m) in X`.
- Its allocation satisfies every registered necessity, and family membership
  implies `sigma_F(x(m))`.
- Its actual resources satisfy `rho(m) >= A(x(m))` coordinatewise.

Thus accounting must not exceed actual expenditure. Omitted allocations or
unregistered families are not silently covered by the theorem.

## 2. PL-1--2 — relaxed program and sound transport

<<<<<<< HEAD
Define

`L_F = inf {J(A(x)): x in X, x satisfies N, sigma_F(x)}`.

Other feasibility constraints are dropped, so this is a relaxation.
`inf(empty)=+infinity`; an empty relaxed set excludes actual family members
only under the coverage contract above. This is not an existence certificate.

For exact finite computation, `X` must be effectively enumerable and finite,
necessity/predicate tests decidable, and `A,J` computably evaluable in a number
representation with decidable order for the required comparisons. Integers
and rationals suffice. Finiteness and arbitrary computable-real values alone
do not supply an exact comparison algorithm. The checker uses `None` with
zero feasible allocations as its representation of the empty relaxed set.

**PL-2.** Every physically legal, adequate, reachable machine of family `F`
covered by the contract has `J(rho(m)) >= L_F`.

Proof. Its allocation belongs to the relaxed set, giving
`J(A(x(m))) >= L_F`. Accounting soundness and monotonicity of `J` give
`J(rho(m)) >= J(A(x(m)))`. Combining them proves the bound. QED.

The quantifier includes unbuilt machines within the covered structural class;
it does not prove that those classes exhaust the physical candidate universe.
MSC-1--2 retains the separate universe-coverage, attainment and complete-fiber
obligations for a global morphology conclusion.

**Accounting counterexample.** The hostile machine spends
`(memory,compute)=(2,4)`, while accounting charges `(6,6)`. With
`J=memory+2*compute`, actual cost `10` violates the claimed floor `18`.
The accounting map **overcharges**. Sound undercharging preserves transport.
Overcharging removes the guarantee and can cause failure; it does not force
the scalar inequality to reverse in every possible instance.

## 3. PL-3 — looseness and an attained tightness certificate

A relaxed program can combine coordinates that no single feasible realization
can jointly attain. Its lower bound can therefore be strictly loose.

Two distinct sources of interval abstention are:

- Loose evidence: an additional valid necessity can resolve the comparison.
- A genuine tie between independently attained family optima: sound strict
  bounds cannot select a unique scalar winner.

These are illustrative, not exhaustive. Missing feasibility, attainment or
candidate coverage are additional boundaries. Mere overlap of attainable
cost sets does not imply a tie between their optimal values.

The registered non-neural upper witness costs `16`. Against neural lower
bound `15` the comparison abstains; adding valid necessity `w1+t1>=8` raises
that bound to `18`, so the same witness excludes the neural class. The
physical instance remains fixed while the evidence becomes more informative.

**PL-3b.** If each compared family's bound is attained by a registered
construction (`L_F=U_F`), the interval verdict equals the true-optimum verdict
at that compared-family scope.

Proof. Every interval is its family's attained scalar minimum. The strict
comparison of these singleton intervals is exactly comparison of those
minima. QED. Tight-bound abstention therefore means an optimum tie; loose
bounds alone do not distinguish such a tie from an evidence gap.

The checker includes a separate complete finite control with costs `{14,17}`
and `{14,20}`. Both attained minima are `14`. It is not the allocation-grid
instance whose refined neural lower bound is `18`.

## 4. PL-4 — necessity and family refinement

**PL-4a.** Adding a valid necessity cannot lower `L_F`: it shrinks the relaxed
set, and an infimum over a subset cannot decrease. Consequently an exclusion
`U_A<L_B` persists when the same feasible upper witness and problem are held
fixed and further valid necessities are registered. QED.

**PL-4b.** Weakening a family predicate cannot raise `L_F`: it enlarges the
relaxed set. An established exclusion can therefore be lost, but need not be.
QED. Neither statement licenses changing the accounting or evidence event.

Dropping the shared-kernel restriction from the neural predicate lowers its
refined bound from `18` to `12`; the cost-`16` non-neural witness no longer
excludes that enlarged class. This is sensitivity to the candidate universe,
not an assertion that every enlargement invalidates every verdict.

## 5. PL-5 — lower bounds are insufficient in general

**PL-5.** The relaxed program does not determine the selected family for
every compatible physical instance. Its value depends only on `N`, predicates,
`X,A,J`; different feasible physical worlds can share all of those data.

Proof. Keep refined bounds `L_NEURAL=18`, `L_NON_NEURAL=14`. In one complete
finite synthetic world, actual neural/non-neural minima are `18,16`; in
another they are `18,20`. Use the same neural allocation of accounted cost
`18` and non-neural allocation of accounted cost `14` in both; add nonnegative
non-neural overhead `2` or `6`. Both worlds satisfy the program and accounting
premises, but their uniquely optimal families differ. Any function of the
shared relaxed instance alone gives the same answer for both worlds, so it
cannot correctly identify both winners. QED.

This is general insufficiency, not impossibility on every input. In a separate
instance take `X={0,1}`, necessity `x>=1`, predicates `A:x=1`, `B:x=0`.
The rival relaxation is empty, so no feasible `B` machine exists. If `A,B`
cover the actual universe and a nonempty selected set is independently proved,
every selected machine is in `A`. This family conclusion needs no numeric
upper bound. A complete finite world with one feasible `A` machine supplies
an explicit positive example with attained selection.

The same relaxed sets with no actual feasible machines select nothing.
Nonempty feasibility alone also does not establish attainment: in a separate
instance, `A={a_n:n>=1}` with costs `1/n`, accounting floor zero and empty
rival class has no minimum. MSC-1 requires nonempty selection; MSC-2 supplies
a sufficient finite constructive coverage certificate for it. Exclusion,
existence, attained selection and a common implementable witness are distinct.
Tightness certificates can also connect lower bounds to selection.

## 6. Exact finite evidence and historical custody

The allocation grid is `0..7` for `(w1,w2,t1,t2)`, giving `4096` allocations.
Necessities are `w1>=2,w2>=1,t1>=3`; accounting is `memory=w1+w2`,
`compute=t1+t2`, and `J=memory+2*compute`. The neural predicate requires
`t1=t2,w1>=w2`; the non-neural predicate requires `t2=0,w2>=3`.

| Evidence | Neural bound / feasible allocations | Non-neural bound / feasible allocations |
|---|---|---|
| Initial necessities | `15 / 135` | `11 / 150` |
| Add `w1+t1>=8` | `18 / 119` | `14 / 120` |

Four sound registered machines respect these bounds. The overcharging witness
fails at actual cost `10`; enlarging the neural class gives bound `12`.
The corrected checker also retains opposite-optimum worlds, empty-rival
selection with proved existence, empty-world abstention and refusal of an
uncovered cheaper family. These are synthetic logical controls, not measured
substrates or exhaustive physical architecture comparisons.

Current payload: `GRAND_GMI_MORPHOLOGY_PHASE_LAW_RECEIPT_V2.json`.
The V1 receipt remains byte-identical, including obsolete undercharging labels.
Terminal: `GRAND_GMI_MORPHOLOGY_PHASE_LAW_SCOPE_REPAIRED_V2_GREEN`.

## 7. Parent mathematics and remaining scope

The parents are relaxation as a lower-bound technique, monotone composition,
infimum monotonicity, and the existence/attainment distinctions in MSC-1--3.
No novelty is claimed for those results. The contribution is their precise
application to the conditional generator `(necessities,predicate,A,J) -> L_F`,
with corrected scope and retained negative and constructive positive controls.
The module does not itself supply a feasible upper witness, tightness,
physical resource maps or coverage of all legal families. Those remain
separate evidence obligations; a selected family is not implied in general.
=======
\[
\mathcal I=(\mathcal N,\ \Sigma_{\mathcal F},\ A,\ J,\ X),
\]

where:

- `N` is the set of **proved necessities** on an allocation vector `x`. Each
  necessity is a lower bound already established by the semantic-cut,
  transformation-complexity, symmetry, physical or developmental layers. A
  coordinate with no proved lower bound admits non-negativity only.
- `Sigma_F = {sigma_F}` are **structural family predicates** on morphology
  descriptors, in the sense of `MORPHOLOGY_SELECTION_THEOREM_V1.md` §2. A
  family is the extension of its predicate, never a historical name (MS-5).
- `A` is the declared **resource accounting map** from allocations to
  registered resource coordinates, nondecreasing in every argument.
- `J` is the declared scalar selection functional, nondecreasing in every
  resource coordinate.
- `X` is the registered allocation domain.

The **accounting-soundness contract** is a hypothesis of this layer:

> For every admitted machine `m` with allocation `x(m)`,
> `rho(m) >= A(x(m))` coordinatewise.

The accounting map must undercharge. It is a budget floor, not an estimate.

## 3. PL-1 — the relaxed accounting program

Define, for each family predicate,

\[
\boxed{
L_F=\inf\{J(A(x)):x\in X,\ x\models\mathcal N,\ \sigma_F(x)\}.
}
\]

Only the proved necessities and the structural predicate constrain `x`. Every
other feasibility condition — joint realizability, legality, reachability,
deployment adequacy — is **dropped**. The program is therefore a relaxation,
and its value is computable whenever `X` is finite and `J`, `A` are decidable.

## 4. PL-2 — derived family lower bound

> **PL-2.** Let `m` be any admitted machine that is physically legal, adequate,
> reachable and satisfies `sigma_F`. Under the accounting-soundness contract,
> `J(rho(m)) >= L_F`.

### Proof

`m` is admitted, so its allocation `x(m)` satisfies every proved necessity,
because a necessity holds of every admitted machine. It satisfies `sigma_F` by
assumption. Hence `x(m)` lies in the feasible set of the program, so
`J(A(x(m))) >= L_F`. Accounting soundness gives `rho(m) >= A(x(m))`
coordinatewise, and `J` is nondecreasing, so `J(rho(m)) >= J(A(x(m)))`.
Chaining the two inequalities gives the claim. QED.

Two consequences matter.

**It covers machines nobody has built.** The proof quantifies over the
structural predicate, not over a registered list of candidates. Any future,
undiscovered or exotic realization satisfying `sigma_F` is already bounded by
`L_F`. This is the only sense in which the present package makes a prospective
claim about unknown forms, and it is confined to the registered structure
class — see `CANDIDATE_UNIVERSE_COVERAGE_CORRECTION_V1.md` for the residue.

**Accounting soundness is load bearing.** If the map may overcharge in any
coordinate, the last inequality reverses and the bound fails. The checker
includes a machine whose accounting undercharges by construction; its scalar
cost is `10` against a derived bound of `18`.

## 5. PL-3 — relaxation looseness, and two causes of abstention

`L_F` can be strictly below every attainable cost, because the relaxation may
combine coordinates that no single feasible realization can combine. This is
the family-level form of the attainment defect that the master already
records: componentwise lower envelopes need not be attained.

Therefore an `UNDECIDED_FROM_CURRENT_EVIDENCE` verdict has **two distinct
causes**, which FP-2 did not separate:

1. **epistemic** — the derived bounds are loose, and a valid necessity not yet
   registered would resolve the comparison;
2. **physical** — the attainable sets genuinely overlap, and no additional
   necessity can separate them.

The exact witness exhibits cause 1. The registered non-neural construction
costs `16`. Against the relaxed neural bound `15` the comparison abstains;
against the refined neural bound `18`, obtained by registering one further
valid joint necessity, the same construction robustly excludes the neural
class. The physics never changed, only the evidence.

> **PL-3b — tightness certificate.** If every compared family's derived bound
> is attained by a registered construction, so that `L_F = U_F`, then the
> verdict computed from the intervals equals the verdict computed from the true
> family optima.

### Proof

Each interval is the singleton `{L_F}`, which is by hypothesis the family's
attained optimum. The strict-separation test on singletons is exactly the
comparison of optima. QED.

So abstention under tight bounds is physical, and abstention under untight
bounds is uninformative about physics. A phase diagram must therefore publish
its tightness status per region; otherwise its boundary regions cannot be
interpreted.

## 6. PL-4 — evidence refines monotonically; candidates do not

> **PL-4a.** Adding a valid necessity to the program cannot lower `L_F`.
> Hence a robust exclusion established from valid necessities is never lost by
> registering further valid necessities.

### Proof

A further necessity shrinks the feasible set, and an infimum over a subset is
at least the infimum over the set. The exclusion test `U_A < L_B` is
monotone in `L_B`. QED.

> **PL-4b.** Weakening a structural predicate cannot raise `L_F`, so a robust
> verdict **can** be lost by enlarging the structure class.

### Proof

A weaker predicate enlarges the feasible set and an infimum over a superset is
at most the infimum over the set. QED.

Together these give the exact asymmetry that DC-4 states informally: more
evidence is always safe, more candidates never are. The witness makes it
arithmetic. Dropping the shared-kernel restriction from the neural predicate —
admitting a heterogeneous-kernel neural form that no one had registered — drops
the derived bound from `18` to `12`, and the non-neural verdict is withdrawn.

## 7. PL-5 — the derivation is one sided

> **PL-5.** No relaxation program of this form can select a family. Two
> substrate worlds sharing every proved necessity share every derived lower
> bound, and can still have different verdicts.

### Proof

The program's value depends only on `N`, `sigma_F`, `A`, `J` and `X`. A verdict
additionally requires an upper bound, which only a construction supplies. The
witness exhibits two worlds with identical derived bounds `L_NEURAL = 18`,
`L_NON_NEURAL = 14`: where a non-neural construction of cost `16` exists the
verdict is `NON_NEURAL`; where instead only a neural construction of cost `18`
exists the verdict abstains, since `18 < 14` is false. QED.

Hence necessities exclude; constructions select. A phase diagram built from
necessities alone has robust-exclusion regions and abstention regions, and no
selection regions at all.

## 8. Exact finite witness

The registered witness instance has two cuts with widths `w1, w2`, two
transformation sites with costs `t1, t2`, allocation domain `0..7` in each
coordinate (`4096` allocations enumerated exhaustively), proved necessities
`w1 >= 2`, `w2 >= 1`, `t1 >= 3`, no proved lower bound on `t2`, accounting
`memory = w1 + w2`, `compute = t1 + t2`, and `J = memory + 2 * compute`.

Structural predicates: the neural class charges one shared kernel at both
sites (`t1 = t2`) with a widest-first carrier (`w1 >= w2`); the non-neural
class places a lookup at site 2 (`t2 = 0`) and carries the full key across cut
2 (`w2 >= 3`).

| Evidence state | `L_NEURAL` | `L_NON_NEURAL` |
|---|---:|---:|
| proved necessities only | 15 | 11 |
| plus the joint necessity `w1 + t1 >= 8` | 18 | 14 |

The enlarged heterogeneous-kernel neural class gives `12` in the refined
state. Four registered machines with sound accounting each respect their
family's derived bound; the undercharging machine breaks it at `10`.

These numbers verify the derivation logic. They are not measurements of any
real substrate.

## 9. What this adds, and what it does not

The master chain's final arrow is now a theorem rather than a schema, in one
direction:

\[
(\mathcal N\ \text{from}\ \kappa,\tau,G,\rho)\ +\ \sigma_F\ +\ A\ +\ J
\;\Longrightarrow\;
L_F
\;\Longrightarrow\;
\text{robust family exclusion}.
\]

It does **not** supply `U_F`, does not measure any substrate, does not produce
a selection from necessities, does not make the relaxation tight, and does not
establish that the registered structure classes cover the physically legal
set. The last of those is the subject of the candidate-universe coverage
correction. Real resource maps and large-scale learning evidence remain the
empirical obligations already listed in the recursive audit.

`CONTINUOUS_LIFT_BOUNDARY_THEOREM_V1.md` determines which of these results
survive an infinite instance. PL-2's lower bound transfers with no compactness,
measurability or effectivity hypothesis, because its proof uses only
feasible-set membership and monotonicity, so a robust exclusion is not a
finite-scope artifact. PL-3b's tightness certificate does not transfer: where
the infimum is unattained, an abstention cannot be classified as epistemic or
physical at all. Computing the bound additionally needs an effective
description, since every finite observation window strictly overestimates it.

Terminal: `GRAND_GMI_MORPHOLOGY_PHASE_LAW_DERIVATION_GREEN_AT_FINITE_SCOPE`.

## 10. Parent mathematics and contribution boundary

The parent results are elementary: monotonicity of an infimum under set
inclusion, relaxation as a lower-bound technique in mathematical programming,
and monotone composition of nondecreasing maps. No novelty is claimed for
them. The contribution is the identification of the missing generator arrow in
the registered phase law, its one-sided repair under an explicit
accounting-soundness contract, the separation of epistemic from physical
abstention with a tightness certificate, and the exact evidence/candidate
asymmetry, each with an exhaustive finite witness.
>>>>>>> origin/main
