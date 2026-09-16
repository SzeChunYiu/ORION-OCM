# GMI #833 history, switching and hysteresis v1 — freeze

Parent issue: #833 Section J. Child: #895.  
Base main: `44ec64478075bef14ad17bd009822225c972e983` (selection/phase schema #894 merged).

## Frozen scope

Finite architecture-name-free morphology set `M`. A current ecology supplies exact scalar base costs `c(m)`. The previous selected morphology `h` affects current choice only through an exact nonnegative switching/migration burden `K(h,m)`.

The current history-conditioned selection set is

`Sel(h)=argmin_m [ c(m) + K(h,m) ]`.

No architecture names enter the object.

## Frozen theorem targets

### HIST-1 — exact history-dependence criterion

History changes observed morphology at the registered current ecology iff there exist previous morphologies `h1,h2` with `Sel(h1) != Sel(h2)`. Preserve tie sets exactly.

Provide an exact hostile where identical instantaneous base costs select different morphologies solely because switching costs retain the previous form.

### HIST-2 — two-form symmetric hysteresis band

For forms `A,B`, self-switch cost `0`, cross-switch cost `kappa>=0`, and instantaneous difference

`delta = c(B)-c(A)`,

prove:

- if `delta < -kappa`, both histories select `B`;
- if `-kappa < delta < kappa`, history matters: previous `A` selects `A`, previous `B` selects `B`;
- if `delta > kappa`, both histories select `A`;
- at `delta = +/- kappa`, preserve the exact boundary tie rather than forcing a winner.

If `delta(theta)=alpha+beta theta` with `beta != 0`, the hysteresis switching thresholds are exactly the solutions of `delta(theta)=+/- kappa`.

### ERASE-1 — origin-additive switching erases history

If

`K(h,m)=u(h)+v(m)`,

then `u(h)` is a common additive term across all current candidates and cancels from the argmin. Therefore `Sel(h)` is identical for every previous history. Zero switching is the special case `u=v=0`.

### ERASE-2 — uniform winner margin

For proposed current morphology `m*`, if for every previous state `h` and rival `n`:

`c(n)-c(m*) > K(h,m*)-K(h,n)`,

then `m*` is the unique current winner for every history. This is a sufficient history-erasure condition even when `K` is not origin-additive.

### RESET-1 — explicit migration/reset

If a registered migration/reset map sends every previous morphology to the same canonical preselection state `h0`, subsequent selection is history-independent by construction and equals `Sel(h0)`. Charge/reset cost remains external to this identity unless explicitly included in the selection objective.

## Required hostiles and certificates

- symmetric persistence hostile with equal base costs and positive switching cost;
- exact boundary ties at `delta=+/-kappa`;
- history-independent origin-additive switching census;
- uniform-margin implication census;
- reset semantics check;
- malformed negative switching costs fail closed.

## Forbidden promotions

This tranche does not claim stochastic switching dynamics, endogenous learned switching costs, general non-Markov history compression, real-world migration calibration, universal hysteresis, all morphology dynamics, or complete GMI.

Expected claim ceiling if GREEN:

`GMI_FINITE_HISTORY_SWITCHING_AND_HYSTERESIS_SELECTION_AT_REGISTERED_SCOPE`
