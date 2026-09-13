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
