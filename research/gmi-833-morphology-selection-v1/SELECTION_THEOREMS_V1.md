# Finite niche-partition and resource-repricing laws — v1

Status: **LOCAL FORMAL CLOSURE — NOT PROSPECTIVE, REPLICATED, OR REAL-SYSTEM EVIDENCE**

Parent: #892 / #833 Section J. The merged #893/#894 package owns the finite
selection correspondence, uniqueness/Pareto conditions, and affine phase
schema. #895 owns history/switching/hysteresis. This tranche targets only the
two remaining formal rows: niche partitioning and resource repricing.

## 1. Protected scope

Morphologies are finite protected computational-mechanism equivalence classes,
not architecture-family names. Utilities, masses, qualities, raw resource
vectors, and prices are exact integers/rationals. Prices and resources are
nonnegative. Every niche uses one common nonempty morphology carrier.

## 2. NICHE-1 — positive-mass local allocation

Let `Z` be a finite niche set, `mu(z)>=0` its registered mass with
`sum_z mu(z)>0`, and `u_z(m)` an exact local utility on common morphology
carrier `M`. Define the complete local winner set

`W(z)=argmax_{m in M} u_z(m)`

and local-allocation support

`Supp_local = union_{z:mu(z)>0} W(z)`.

This definition preserves local ties. It never invents a tie-breaker and a
zero-mass niche contributes no morphology.

### Theorem NICHE-1a — sufficient coexistence

If two positive-mass niches have disjoint unique winners `m1` and `m2`, then
`m1,m2 in Supp_local`, so at least those two morphologies coexist under the
registered local allocation semantics.

**Proof.** Positive mass includes both niches in the union. Singleton local
argmax sets contribute `m1` and `m2`, and disjointness makes them distinct. `□`

### Theorem NICHE-1b — ties remain set-valued

If a positive-mass niche has `W(z)={m1,m2}`, both morphologies occur in
`Supp_local`.

**Proof.** The support uses the complete argmax set, not an arbitrary selected
representative. `□`

### Boundary: global aggregation is another problem

A global weighted average has winners

`argmax_m [sum_z mu(z)u_z(m)/sum_z mu(z)]`.

That set need not equal `Supp_local`. In the executable witness, left utility
is `(A=4,B=0)`, right utility is `(A=0,B=4)`, and masses are `(1,2)`.
Local allocation supports `{A,B}`, while global averaging uniquely selects
`B`. Replacing the former with the latter is an added aggregation assumption,
not a theorem.

### Exact census

For two niches, two morphologies, utilities in `{0,1,2}`, and mass supports
`(1,0),(0,1),(1,1)`, all 243 worlds exactly reproduce the positive-mass union
definition. Eighteen worlds have disjoint unique positive-mass winners and all
eighteen retain both morphologies.

## 3. REPRICE-1 — vector-resource phase geometry

For quality `v_m`, nonnegative raw resource vector `r_m`, and registered
nonnegative price vector `p`, define the explicit scalarized score

`q_m(p)=v_m-p dot r_m`.

Raw vectors remain primary; the scalarization is conditional on `p`.

### Theorem REPRICE-1a — pair boundary

For morphologies `i,j`, a tie occurs exactly on the hyperplane

`v_i-v_j = p dot (r_i-r_j)`.

**Proof.** Subtract the two scores:

`q_i(p)-q_j(p)=(v_i-v_j)-p dot (r_i-r_j)`.

The difference is zero exactly on the displayed hyperplane. `□`

On every connected cell of the complement of all pair hyperplanes, each
pairwise difference is continuous affine and nonzero, so its sign is constant.
Therefore the complete selected set is constant within each cell. A selected
set can change only at a boundary; crossing a boundary need not change the
global winner if another morphology remains superior.

For one resource coordinate and unequal resource use, the exact candidate
boundary is `(v_i-v_j)/(r_i-r_j)`. Equal resource use gives either
`NO_CROSSING` or `TIED_EVERYWHERE`.

### Theorem REPRICE-1b — dominance no-flip

If `v_i>=v_j` and `r_i<=r_j` coordinatewise, then `q_i(p)>=q_j(p)` for every
`p>=0`.

**Proof.**

`q_i-q_j=(v_i-v_j)+p dot (r_j-r_i)>=0`.

Thus a morphology that is weakly better in quality and weakly cheaper in every
registered resource cannot lose under nonnegative linear repricing. `□`

### Exact witnesses and census

With qualities `(A=5,B=4)` and one-coordinate resources `(A=3,B=1)`, the
boundary is `p=1/2`: `A` wins at zero price, both tie at the boundary, and `B`
wins at price one. A two-coordinate witness registers hyperplane normal
`(2,-1)` and quality gap `1`.

The executable census checks all 1,024 tuples with qualities, resources, and
integer price in `{0,1,2,3}`. It verifies the exact score-difference identity,
400 dominance-premise cases, and 26 strict adjacent-price sign changes; every
strict sign change has its exact boundary inside that price interval.

## 4. Parent and claim boundary

Exact Git objects pin #837, #847, #850, #876, and #893/#894. No selection,
phase, history, switching, search-law, or finite-budget result is re-claimed.
Only the two #892 rows may be reconciled.

The three empirical Section-J rows remain open: 20 prospective held-out
transitions, independent-search replication, and five real-system validations.

Claim ceiling:

`GMI_833_FINITE_NICHE_AND_RESOURCE_REPRICING_LAWS_AT_REGISTERED_SCOPE`.

The result is falsified if a zero-mass niche adds support, a local tie is
collapsed, global aggregation is silently substituted for local allocation,
a pair changes order away from its hyperplane, a dominance no-flip case
reverses, an inexact numeric value is accepted, or a pinned parent drifts.
