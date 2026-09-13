# Family-phase soundness correction — recursive audit FPS-1

Date: 2026-09-13. Predecessor reviewed: `7f8488edd77992ba0313fa9457294ed7bbc623cf`.

## Scope

This corrects `FAMILY_FRONTIER_PHASE_THEOREM_V1.md` (FP-2, FP-3, FP-5, FP-6),
its claim ledger and its checker. The defects are in the selection logic
itself, so they are independent of any measured resource law. Nothing here
establishes an empirical family verdict.

## Defect 1 — the stated crossover condition excludes nothing

Predecessor FP-3 concluded that a change from a robust `A` region to a robust
`B` region "cannot occur without passing through a parameter set where the
certified intervals touch or overlap", written as

`U_A(s) >= L_B(s)` and/or `U_B(s) >= L_A(s)`.

That disjunction is already implied at the destination. Robust `B` means
`U_B < L_A`, and well-formed certified intervals satisfy `L_B <= U_B` and
`L_A <= U_A`, so

`L_B <= U_B < L_A <= U_A`,

hence `U_A >= L_B` holds at every robust-`B` parameter. The stated touch set
therefore contains the whole robust-`B` region and identifies no boundary. The
checker enumerates all 225 ordered pairs of well-formed integer intervals on
`0..4` and confirms the condition at each of the 35 robust-`B` configurations.
This is a vacuity defect, not a false statement.

## Defect 2 — the intended claim needs a connected domain

The intended content is stronger: between two robust regions there is a
parameter at which **neither** family is robust. That claim requires
hypotheses the predecessor omitted.

Corrected statement (FP-3a). Let the parameter domain contain a path from `s1`
to `s2` on which `L_B - U_A` is continuous and all registered intervals are
well formed. If `A` is robust at `s1` and `B` is robust at `s2`, then there is
`s*` on that path with `U_A(s*) = L_B(s*)`, and neither `A` nor `B` is robust
at `s*`.

Proof. `f = L_B - U_A` satisfies `f(s1) > 0` by robustness of `A`. At `s2`,
`L_B <= U_B < L_A <= U_A` gives `f(s2) < 0`. The intermediate value theorem
supplies `s*` with `f(s*) = 0`. Then `U_A(s*) = L_B(s*)` is not the strict
inequality robust `A` requires. For `B`, `U_B(s*) >= L_B(s*) = U_A(s*) >=
L_A(s*)`, so `U_B(s*) < L_A(s*)` fails. QED.

The exact witness uses `A = [1+6s, 2+6s]`, `B = [5-4s, 6-4s]` on `[0,1]`. The
gap `3 - 10 s` is affine, so its root `s* = 3/10` is exact and rational; at
that parameter the pair is `A = [14/5, 19/5]`, `B = [19/5, 24/5]` and the
two-family verdict is `UNDECIDED_FROM_CURRENT_EVIDENCE`.

**On a discrete register the conclusion is false.** For the registered scale
set `{1,2}` with `A = [1,2]`, `B = [5,6]` at `s = 1` and `A = [7,8]`,
`B = [3,4]` at `s = 2`, the verdict is robust `A` then robust `B` and no
registered parameter abstains. A phase diagram over a discrete scale register
therefore may not claim an intervening boundary, and no interpolation between
adjacent registered parameters is licensed.

**The conclusion is pairwise, not global.** At `s* = 3/10` above, adding a
third family with interval `[1/2, 1]` makes that family robust, because
`1 < 14/5` and `1 < 19/5`. So a pairwise touch parameter need not be an
undecided parameter of the full phase diagram.

## Defect 3 — malformed intervals were compared instead of rejected

`robust_scalar_winner` compared bounds without validating them and asserted
that at most one winner exists. Two families registered as `[5,0]` each
satisfy the unvalidated test, so the predecessor checker would fail an
assertion rather than reject the input. A single malformed family also escapes
the Defect-1 chain: with `A = [1,2]` and `B = [5,0]`, `B` passes the
robustness test while `U_A = 2 < 5 = L_B`.

Both the corrected checker and the correction checker validate
`lower <= upper` on exact rational or integer bounds and raise a typed
`PhaseInputError`. Over all 625 integer configurations on `0..4` for two
families, 100 produce more than one unvalidated winner and every one of them
contains a malformed interval; no well-formed configuration does. This follows
the same abstention convention as `CERTIFICATE_INPUT_CORRECTION_20260913.md`.

## Defect 4 — an upper bound was summed into a lower bound

Predecessor §10 registered a neural smooth-region **upper** bound `4`, a
neural exact-region **lower** bound `8`, a non-neural smooth-region **lower**
bound `9`, a non-neural exact-region **upper** bound `3` and a bridge upper
bound `1`. It then asserted that "any pure neural realization costs at least
`4 + 8 = 12`" and any pure non-neural realization at least `9 + 3 = 12`, and
concluded that the hybrid upper bound `8` robustly selects the hybrid family.

A lower bound on a sum of regional costs is the sum of regional **lower**
bounds. The neural smooth-region lower bound was never registered. With
non-negativity alone the sound pure-neural bound is `0 + 8 = 8`, which does
not strictly exceed the hybrid upper bound `8`. The evidence world with
neural smooth cost `0` and neural exact cost `8` satisfies every registered
bound and ties the hybrid, so the predecessor verdict is not robust. The
correct verdict from the predecessor's own registered inputs is
`UNDECIDED_FROM_CURRENT_EVIDENCE`.

The non-neural side survives: its smooth-region **lower** bound was registered,
so the sound bound `9 + 0 = 9` still strictly exceeds `8`. Only one of the two
exclusions was defective.

Repair. Register the missing regional lower bounds. With
`L_N(R_s) = 4` and `L_X(R_x) = 3` the sound pure-family bounds are `12` and
`12`, and the hybrid verdict is recovered. The amended sector checker
registers both, asserts `lower <= upper` for each region, and additionally
asserts that the unregistered-bound computation does **not** license the
exclusion.

## Defect 5 — a regional sum bounds decomposed candidates only

FP-5's additive regional law was declared in order to **compose** a hybrid
upper bound. FP-6 and §10 then used the same law as a **necessity** for pure
competitors. That direction needs an extra hypothesis: every admissible
realization of the pure family must factor through the registered regional
decomposition with additively charged costs.

A monolithic realization is not bound by the regional sum. With the repaired
registration the regional pure-neural bound is `12` against a hybrid upper
bound of `8`; a monolithic pure-neural realization of total cost `6` is
compatible with a substrate model in which the registered cut is never
instantiated, and it defeats the hybrid selection. The corrected FP-5/FP-6
therefore require a **decomposition-closed candidate class**, or regional
bounds proved as lower bounds on the whole obligation for that family.
Without that hypothesis the verdict abstains.

This is the same direction defect that `SUFFICIENCY_DIRECTIONS_AUDIT_V1.md`
repaired elsewhere: a declared sufficient construction law is not
automatically a necessity for competitors.

## What is retained

FP-1 vector robust exclusion, FP-2's strict-separation criterion, FP-4's
no-go result and the §9 scalar interval phase witness are unchanged; the §9
witness already registers well-formed intervals and its overlap parameters are
genuine non-identification at the registered scale set. The amended text adds
the well-formedness, connectedness, pairwise-scope, lower-bound-summation and
decomposition-closure hypotheses, and records that an overlap region of a
discrete register carries no interpolation licence.

## Bounded validation and preserved evidence

`grand_gmi_family_phase_soundness_checks_v1.py` executes the five findings
above with exact rational arithmetic, including the enumerations
`225`/`35`/`625`/`100` and the exact crossover root `3/10`. Its complete
output is frozen as `GRAND_GMI_FAMILY_PHASE_SOUNDNESS_RECEIPT_V1.json`.
`grand_gmi_family_phase_checks_v1.py` is amended in place; its replay receipt
is regenerated and its historical top-level receipt is preserved with an
updated supersession record.

Current terminal: `GRAND_GMI_FAMILY_PHASE_SOUNDNESS_CORRECTION_GREEN_AT_FINITE_SCOPE`.
This is a mathematical soundness repair of the selection logic at declared
finite scope. It does not supply `L_F(s)` or `U_F(s)` for any real substrate
and does not establish any family verdict.

## Parent mathematics and contribution boundary

The parent results used are the intermediate value theorem for a continuous
real function on a connected domain, Pareto domination, and elementary
interval arithmetic over an uncertainty set as used in robust comparison. No
novelty is claimed for any of them. The contribution is the identification of
the vacuity, well-formedness, pairwise-scope, bound-direction and
decomposition-closure defects in the registered family-phase statements, and
their scoped repair with exact finite witnesses.
