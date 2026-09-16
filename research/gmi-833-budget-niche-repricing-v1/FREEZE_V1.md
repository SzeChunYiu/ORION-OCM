# GMI #833 finite budget, niche and repricing laws v1 — freeze

Parent: #833 Section J. Child: #899.  
Base main: `23e20b02166843437fc4010f96bcabf704455dab`.

## Frozen scope and theorem targets

### BUDGET-1 — finite search/discovery budget

Each finite candidate has exact objective value `J(m)` and a registered first-availability/discovery budget `tau(m)`. At budget `B`, observed selection is the full argmin among `tau(m)<=B`.

Prove/check:
- available candidate sets expand monotonically with budget;
- best observed objective value cannot worsen as budget increases;
- if the global optimum is unique, once that morphology becomes available it is the unique selected morphology at every later budget;
- a hostile must show an early finite-budget winner can differ from the eventual/global winner.

### NICHE-1 — finite operating-regime partition and coexistence

For a finite weighted regime set `E` with exact probability weights and per-regime candidate costs, retain the full argmin set in every regime.

For morphology `m` define:
- lower niche mass = total weight of regimes where `m` is the unique winner;
- upper niche mass = total weight of regimes where `m` belongs to the winner set.

Prove/check `0 <= lower <= upper <= 1`. Define robust coexistence when at least two morphologies have positive lower mass; possible coexistence when at least two have positive upper mass. Ties must widen bounds, not be arbitrarily allocated.

### REPRICE-1 — morphology transitions under resource repricing

For raw resource vector `r(m)` and affine positive price path `w(theta)=w0+theta v`, score is affine:

`S_m(theta)=w(theta) dot r(m)`.

Derive all pairwise crossing points in a registered interval and prove the exact winner set is constant in every open crossing-free cell. A crossing of non-winning candidates need not be a morphology transition and must be retained as a non-envelope boundary rather than promoted.

## Required finite certificates

- exhaustive three-candidate objective/discovery-order census;
- exact finite-budget hostile;
- exact three-regime niche partition witness and tie-share bounds;
- exhaustive binary 3x3 regime-cost census;
- exact three-form resource-repricing witness with positive prices throughout the interval and direct interior checks.

## Forbidden promotions

No prospective transition validation, independent real-system replication, stochastic ecology dynamics, real-scale validation, all-known-form closure, or complete GMI.

Expected claim ceiling if GREEN:

`GMI_FINITE_BUDGET_NICHE_AND_REPRICING_SELECTION_LAWS_AT_REGISTERED_SCOPE`
