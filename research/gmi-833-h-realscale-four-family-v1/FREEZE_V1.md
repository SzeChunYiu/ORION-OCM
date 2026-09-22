# FREEZE V1 — real-scale second tranche of the four known-family rows (GMI #833 Section H)

Frozen BEFORE any implementation, outcome, search, or adjudication file in this
package exists. This manifest freezes the machine space, the battery classes,
the cost model, the selection rule, the null discipline, the tolerance rules,
the predicted recovery pattern derivation, and the claim ceilings. It extends
two merged parents, pinned by git blob in `MANIFEST_V1.json`:

- `research/gmi-833-h-neutral-four-family-v1/` (PR #960): the shared finite
  process grammar (carrier {0,1,2}; ARG/CONST atoms; ADD_MOD/MUL_MOD/
  ZERO_TEST compositions; INDEXED_PARAMETER_READ storage; DELAY_CELL
  temporal), the ten-gate family ledger whose ONLY open gate per family is
  `real_scale_test`, and the four posthoc structural classes
  PERSISTENT_THREE_CLASS_FUTURE_RESPONSE_QUOTIENT, AFFINE_SHARED_RESPONSE /
  BINARY_DECISION_ON_AFFINE_SCORE, NON_AFFINE_LINK_OF_ONE_DIMENSIONAL_SCORE,
  CROSS_COORDINATE_LIFTED_INTERACTION.
- `research/gmi-833-blind-recovery-v2-v1/`: the channel-closure standard
  (coverage-complete neutral battery, tier-declared basis, prior-disclosure
  manifest, bijective adjudicator, A2 semantic screen, freeze custody).
- `research/gmi-833-g0-grammar-growth-v1/-v2/`: execution-cost (EXEC-B)
  charging and the 200-seed null/rank discipline.

## Scientific question

Can the four family morphologies be recovered by a family-hidden search at
REAL SCALE — real-valued interfaces, statistical samples, held-out
generalization, exact numerical conditioning, and real kernel realizations —
under one declared neutral grammar with no per-family channel? And where are
the recovery boundaries as functions of noise scale, conditioning, and task
class, measured rather than asserted?

## F1 — Machine space (frozen; the real-scale extension of the parent grammar)

The grammar tiers, extended to the real interface by the same tier rules the
parents declared (v2 CH2; parent GRAMMAR):

- Atoms: the p real input coordinates x_1..x_p, and constants {-1, 0, +1}
  (the minimal sign-symmetric set; unchanged from both parents).
- Binary tier: {ADD, MUL} — the two field laws of the real numbers, the
  exact analogue of the parent carrier's {ADD_MOD, MUL_MOD}. No macro, no
  comparison-of-two-signals compound.
- Unary tier U_ORD(R): {NEG} ∪ {GE_c : c ∈ CUTS}, CUTS = the complete set of
  one-sided cut points at every order statistic of every one-dimensional
  projection realized on the training rows (the v2 "every cut point" rule
  transported to the real interface: completeness within order statistics of
  the observed sample; no cut is privileged).
- Storage tier: INDEXED_PARAMETER_READ over the encoded carrier lattice
  (per-coordinate order-statistic quantization onto {0,1,2}, the unique
  order-complete 3-level encoding — derived from the parent carrier size 3,
  not chosen).
- Temporal tier: DELAY_CELL chains of length 0..D_MAX carrying real values
  (one cell per symbol of lag), D_MAX = 11 (derivation D-8).

Machine space = the depth/structure-labeled closures (strata) of these tiers:

| stratum id | closure | description cost | serve cost per row |
|---|---|---|---|
| S_CONST | constants | 1 | 0 |
| S_ADD | ADD-closure of atoms + constant | 1+p | 2p |
| S_ORD | U_ORD applied to S_ADD | 2+p | 2p+1 |
| S_MONO | complete monotone unary tier on the ENCODED 3-level score grid (exact isotonic fit per level; D-5/D-1) applied to S_ADD | 1+p+3 | 2p+3 |
| S_LIFT | ADD-closure of atoms, constant, and all pairwise MUL products | 1+p+p(p-1)/2 | 2(p+p(p-1)/2) |
| S_TABLE | INDEXED_PARAMETER_READ on the encoded lattice | 3^p | 1 |
| T_c (c=0..D_MAX) | any static stratum over the delay-augmented interface (x_t, x_{t-1}, .. x_{t-c}) | stratum cost + c (one description slot per cell) | stratum serve + c |

Family names attach ONLY posthoc (posthoc_adjudicate + ledgers); the
search-visible surface uses stratum vocabulary only (enforced by the lexical
+ A2 screens, test_realscale_v1.py).

## F2 — Batteries (frozen classes; registry committed before outcomes)

All generation is exact dyadic-rational (integer-scaled) arithmetic — no
binary floating point anywhere in the search path (the float64 control of
D-12 is host-side only). The PRNG is the declared SHA-256 counter stream
(D-10); every task id pins its seeds, so the battery regenerates
byte-identically on any host.

B_STATIC (response batteries; complete in the declared parameter lattices):
- T_CONST: constant-response members (the null-stratum positives).
- T_AFFINE: ALL 2^p - 1 non-empty coordinate supports; coefficients drawn
  from the dyadic magnitude lattice (D-4); the LINEAR family member class.
- T_DECISION: binary labels = GE_cut on an affine score, cut from CUTS;
  the LINEAR classifier member class.  The battery's own cut rule: the
  upper-tercile order statistic of the true score (the D-1 tercile rule,
  the same rule that defines the encoded lattice).
- T_LINK: monotone step links g* (complete monotone tier on the score grid,
  D-5) composed with affine scores; non-affine-link members are the GLM
  member class; affine-link members are the GLM boundary.
- T_NONMONO: U-shaped (non-monotone one-dimensional) links; GLM boundary
  by counterexample.
- T_LIFT: ALL 2^(p(p-1)/2) pair-support patterns over the interaction terms
  (empty support = additive boundary); non-empty supports are the
  basis/kernel member class.
- Null arm: within-train response permutation (shuffle) of every member
  class, 200 seeds each (D-9).
- Sweeps: noise-lattice sweep at identity conditioning; conditioning-lattice
  sweep at the noise-lattice floor; support census at the mid-lattice noise.

B_STREAM (temporal batteries; complete in the lag parameter):
- T_DELAY_L for L = 0..D_MAX: response y_t = x_{t-L} on a real dyadic input
  stream of length n (D-8), Rademacher noise at lattice scales; L=0 is the
  family boundary (no cell admissible), L>=1 the member class.
- Binary de Bruijn arm: the v2 B_DELAY class on the binary substream, for
  the exact residual-quotient bound check (minimal cells = L; the counting
  bound executed, not logged).

## F3 — Canonical stratum solvers (frozen)

Each stratum's exact empirical-risk minimizer, in closed or canonical form;
the SEARCH is over strata/delay augmentation (where morphology is decided),
never a per-family algorithm import:
- S_CONST/S_ADD/S_LIFT: least squares = the orthogonal projection onto the
  stratum's ADD-closure span — the closure's own exact ERM; computed in
  integer-scaled exact arithmetic via fraction-free (Bareiss) elimination.
- S_ORD: affine score by exact least squares on 0/1-encoded targets, then
  the cut minimizing training risk over the COMPLETE CUTS tier.
- S_MONO: alternating canonical minimization — exact isotonic regression
  (pool-adjacent-violators, the unique L2 isotonic fit) on the score grid
  alternating with exact weighted least squares; iteration bound D-11.
- S_TABLE: per-cell exact mean (real arm) / majority (binary arm).
- Delays: the interface augmentation x_{t-c}; no separate solver.
- DUAL realization check (the real-kernel gate): S_LIFT refit in the dual —
  exact kernel projection with k(x,z) = (x·z + 1)^2, c = 1 the additive
  identity of the lifted constant coordinate; exact-arithmetic runs assert
  EXACT prediction equality with the primal; the float64 control reports
  the deviation boundary (D-12).

## F4 — Cost model (frozen; EXEC-B charged)

Uniform integer prices as in the parents: description_price per fitted
parameter slot, serve_price per row-operation, reuse multiplier as the
parents' R_REUSE; state cells charged one description slot each. No
scalarization: selection is lexicographic (F5) — this also keeps the cost
audit free of SCALARIZATION_WINNER_REVERSAL by construction. Crossover
regimes: the parents' R_STORAGE/R_REUSE transported, plus the derived
price-ratio lattice (D-7).

## F5 — Selection rule (frozen; the plateau structure rule)

AMENDMENT A (pre-outcome, before any implementation of selection or any
outcome; v2-erratum precedent): the fiber is defined with a DERIVED noise
indifference band, not raw exact-risk equality.  With dyadic Rademacher
noise +-sigma and n_test held-out rows, the standard error of a risk
estimate is sqrt(2 sigma^4 / n_test); at the registered n = 2^12 (n_test =
2^11) this is EXACTLY sigma^2 * 2^-5, and the two-sided 2-se band is
EXACTLY band = sigma^2 * 2^-4 (dyadic; derived, not tuned).  Binary arms:
band = 2 * sqrt(eps(1-eps)/n_test), an exact rational at every dyadic eps.
Noise-free cells (sigma/eps = 0): band = 0, exact ties only.  The FIBER =
every machine with held-out risk <= minimal risk + band; cost tie-break,
canonical champion order, and uniform drift then apply WITHIN the fiber.
Justification: at the registered scale, superset strata compete with true
strata within O(sigma^2 d / n) — the same order as the estimation noise —
and raw minimum selection flips on noise fluctuations (a search-order and
draw artifact, not structure); the 2-se band + parsimony cost is the
derived, threshold-free resolution.  F7's prediction rule is UNIFIED with
this band: recovery predicted iff the noise-free gap Delta_min(cell)
exceeds band (the single derived constant of the tranche).

Risk = exact rational empirical risk on the frozen held-out half (real arm:
mean squared dyadic residual; binary arm: mean 0-1 error — the carrier's own
equality). A machine's held-out SEMANTICS is its prediction tuple; the risk
map fibers partition the machine space. Selection:

1. fiber: minimal-risk band (AMENDMENT A);
2. within the fiber: minimal (description, serve) cost;
3. champion = the cost-minimal element of the fiber — deterministic and
   enumeration-order-independent BY CONSTRUCTION (the fiber and the cost are
   order-free functions of the machine space);
4. neutral drift = the seeded uniform measure on the cost-minimal fiber set
   (maximum entropy = the unique choice-invariant distribution on the
   fiber); the drift mass distribution over strata is a reported outcome.

Justification from the frozen formalism (not convenience): the machine space
is a quotient by exact held-out semantics; a lexicographic (errors, cost)
rule that resolves cost WITHIN an error plateau freezes the first-encountered
structure whenever cost-increasing partial matches compete with cheap
champions — the recorded sibling trap — and makes the reachable minimal
construction enumeration-order-dependent, which the A2 search audit flags as
ORDER_OR_TRAJECTORY_DEPENDENT_WINNER. Band-fiber cost minimization with
uniform drift keeps structure accumulation ON the plateau (drift measures
the whole cost-minimal fiber) while the champion stays deterministic. Exact
dyadic arithmetic makes the band exact, so the fiber is well-defined without
tuned knobs.

## F5b — Canonical completion rules (frozen; needed for exactness)

- Monotone-map canonical extension to unseen abscissae: the fitted isotonic
  map is the right-continuous step function with breaks at the exact
  midpoints between adjacent distinct training abscissae; below the minimum
  it takes the first fitted value, above the maximum the last. Midpoints of
  dyadics are dyadic, so the extension stays exact.
- Binary-arm rounding: a real-valued fit on a binary arm predicts label 1
  iff its fitted value >= 1/2 (the carrier midpoint), label 0 otherwise.
- Canonical tie orders: cut-scan ties among equally good cuts resolve to the
  median cut position; champion ties among equal-(risk, description, serve)
  machines resolve by the F1 stratum table order, then ascending delay-cell
  count; drift remains uniform over the full tied set.
- S_TABLE on delay-augmented interfaces is admissible only while its
  description cost 3^(c+1) does not exceed the storage budget 3^p = 81
  (c <= 3); beyond that the storage tier's own lattice is exhausted.
- PROC2 affine solver: EXACT conjugate gradients on the normal equations
  from the initialization 0 (the additive identity) — in exact rational
  arithmetic CG terminates at the unique minimizer in at most d steps
  (finite termination; d < the 2^7 bound everywhere), a Krylov path
  materially different from PROC1's direct elimination; the band-pruned
  best-first tier-growth search is PROC2's second independence axis.
  Strata whose exact ERM is unique and order-free (S_CONST mean, S_TABLE
  cell means, S_ORD cut scan, S_MONO 3-level link) share the canonical fit
  in both procedures; the procedures differ in search mechanics and in the
  affine solver.

## F6 — Nulls, tolerances, error bars (frozen)

- 200 seeds per null arm (the programme standard; grammar-growth v2 null
  discipline). Seed derivation D-10 makes cherry-picking impossible.
- GREEN per family requires: every permutation-null seed fails the family's
  recovery clause (0/200), every frozen boundary member fails it, and the
  member-class recovery counts match the frozen prediction table (F7).
  Exact one-sided binomial tail p-values reported; the GREEN gate is the
  0/200 count itself, not a tuned threshold.
- Error bars: exact 2.5/50/97.5 percentiles of the 200-seed held-out risk
  distributions per (family, lattice point); reported as exact rationals.
- Every tolerance that appears is derived in D-1..D-12 or does not appear.

## F7 — Frozen predictions (committed before any noisy run)

For each family and each (noise, conditioning, task class) cell, the
predicted recovery pattern is derived from the EXACT noise-free risk gaps
and the SINGLE derived constant of the tranche — the AMENDMENT A band:
recovery predicted iff the noise-free gap Delta_min(cell) between the true
stratum's fit risk and the best strictly-lower stratum's fit risk exceeds
band (sigma^2 * 2^-4 real arm; 2*sqrt(eps(1-eps)/n_test) binary arm), the
same quantity the selection itself uses.  One derived rule, one derived
constant, applied to both prediction and selection — no second threshold
exists. The prediction table is generated by `freeze_predictions_v1.py`
from the noise-free battery only, committed at the battery commit, and the
noisy outcome runs must match it cell-by-cell; every mismatch is reported
as a boundary finding, never silently dropped.

## Derivations (every constant in this package; nothing else may appear)

- D-1 carrier/encoding: encoded lattice {0,1,2} per coordinate; the
  order-statistic tercile quantizer is the unique order-complete 3-level map
  (completeness inherited from the parent carrier size 3).
- D-2 p = 4: the smallest dimension whose exact rational orthogonal group is
  nontrivial beyond signed permutations (the 4x4 Hadamard/2), required so
  that an EXACT conditioning construction exists (D-6); also the smallest p
  with p(p-1)/2 >= p+2 (the lift stratum strictly richer than atoms).
- D-3 n = 2^12 = 4096: the dyadic noise lattice terminates at its
  per-sample resolution floor 1/n; n is the smallest power of two at which
  the lattice depth 12 (= log2 n) reaches the double-precision octave
  structure used by the float control (D-12). The stream battery shares the
  same budget (stream length = n).
- D-4 coefficient lattice: {0} ∪ {±2^j : j ∈ [-4, +4]}, K_c = floor(12/3) =
  4 — signal coefficients span at most one third of the noise-lattice
  depth centered at the constants-tier unit 1, leaving two thirds of scale
  separation between signal and noise.
- D-5 monotone link tier: all monotone step maps on the score grid at the
  CUTS lattice points (complete monotone-unary closure on the observed
  grid); smooth links are closure limits, NOT members (declared boundary).
- D-6 conditioning lattice: kappa ∈ {2^(4k) : k = 0..13}, spanning [1,
  2^52]; 52 = IEEE754 double mantissa bits (the float control's own
  resolution); construction: X = R·H_4·S·P with R diagonal Rademacher rows,
  H_4 the exact Hadamard, S = diag(2^e_j) with e_j linearly spread so
  s_max/s_min = kappa EXACTLY, P a seeded signed permutation — every entry
  dyadic, every singular value exact.
- D-7 price-ratio lattice for crossover regimes: {2^j} over the observed
  cost range of the fitted machines, bounded by 2x the max observed cost
  ratio (the v2 cap precedent).
- D-8 D_MAX = 11: the lag class is complete up to the stream budget
  (L ≤ n-1 needs L cells; the de Bruijn binary arm of order L_MAX+1 = 12
  has length exactly 2^12 = n).
- D-9 null arms: within-train response permutation, 200 seeds, at the
  mid-lattice noise point and identity conditioning; plus every boundary
  member class at 200 seeds.
- D-10 seeds: seed(x) = int(SHA-256("GMI833H-RSF1|" + id)[:16], 16); run
  index k appends "|k". PRNG = SHA-256 counter stream: byte j of draw i =
  SHA-256("GMI833H-RSF1|PRNG|" + seed_hex + "|" + i)[j]. No other entropy
  source. bits → dyadics: m bits over 2^m.
- D-11 alternating-solver bound: 2^7 rounds or exact objective decrease <
  2^-52 · initial (52 again the double-mantissa reference); the outcome
  REPORTS whether the round bound ever bound.
- D-12 float64 control (host-side, numpy): same tasks, same seeds; reports
  max |float prediction - exact prediction| per kappa and the exact kappa
  at which the float control first disagrees with the exact search's
  selection. No float participates in any GREEN check.
- D-13 held-out split 1/2: the unique variance-balancing split (equal
  exact binomial variance in both halves).
- D-14 CI scope: the stride-sampled subcensus with at most 16 tasks per
  family (stride = ceil(tasks/16)); CI re-runs these to byte equality and
  validates every committed receipt; the full battery is receipt-bound.

## Claim ceilings (frozen)

`GMI_833_H_REALSECALE_FOUR_FAMILY_MORPHOLOGIES_RECOVERED_NEUTRALLY_WITH_MEASURED_BOUNDARIES_AT_REGISTERED_EXACTDYADIC_SCOPE`

Forbidden promotions (CI-enforced): `FINITE_STATE_AUTOMATA_FAMILY_ROW_CLOSED_BEYOND_REGISTERED_SCOPE`,
`LINEAR_REGRESSION_CLASSIFIER_FAMILY_ROW_CLOSED_BEYOND_REGISTERED_SCOPE`,
`GLM_FAMILY_ROW_CLOSED_BEYOND_REGISTERED_SCOPE`,
`BASIS_KERNEL_FAMILY_ROW_CLOSED_BEYOND_REGISTERED_SCOPE`,
`ALL_KNOWN_FAMILIES_RECOVERED`, `REAL_SCALE_VALIDATION_COMPLETE`,
`UNIVERSAL_GRAMMAR_NEUTRALITY`, `SEARCH_NEUTRALITY`, `COMPLETE_GMI`,
`SMOOTH_LINK_TIER_MEMBERSHIP`, `FLOAT64_REQUIRED_FOR_RECOVERY`.

## Custody

FREEZE_COMMIT (this file + PRIOR_DISCLOSURE_V1.md + the workflow only — no
implementation, no outcomes) precedes the BATTERY_COMMIT (generator +
registry + frozen predictions; still no outcomes), which precedes every
outcome/adjudication/receipt file. The test suite asserts both custody
boundaries by `git cat-file` and the manifest's blob pins.

## AMENDMENT B — H02 corrected-null-arm slice addendum (committed 2026-09-22, before the corrected-null rerun)

Scope: H02 "Linear regression / linear classifiers." (L:852d4bd7dafb). The
four-family real-scale battery's perm-null arm is amended from a within-train
response permutation to a JOINT FULL-ROW response permutation. The amendment
applies to every perm_null cell of every member class (the whole battery's
null arm); the registered claim — AFFINE_SCORE member recovery at real scale —
is unchanged. Only the null construction changes.

### Amended D-9 (null arms)

Frozen D-9: within-train response permutation — permute the training-half
response only; the held-out half keeps the true response. At the registered
identity conditioning (kappa_exp = 0) the design X = R·H_4·S·P has only 4
distinct Hadamard row classes (each repeated 1024 times), so the design Gram
has rank <= 4. A within-train null row therefore still carries the true
response in the held-out half, and a stratum fit aligned with the few row
classes reaches the family signature strata on held-out risk. Measured on the
bounded r02r04 rerun (2026-09-21/22, OUTCOME_FULL_V1.json
sha256 76d68678f2ce2d448001a1dd56ebe035badcf288f614f7c241811de7de740bb5):
148/400 linear and 62/200 kernel perm_null rows recovered on the family
signature strata, and the fingerprint-anchor pass (FINGERPRINT_ANCHOR_V1.json)
dropped 0 of them — no fit-based criterion rejects these nulls as constructed.
One-stage attribution: the null construction fails, not the claim.

Amended D-9 (this addendum): permute the response jointly across the whole
row set — one permutation of all n rows applied to the train and held-out
halves together — so the null design is decorrelated from BOTH halves and a
null champion is a genuine noise fit (the family signature strata have no
signal to fit on the held-out risk). Implemented in battery_realscale_v1.py
under the module flag AMENDED_NULL (0 = frozen within-train permutation,
1 = joint full-row permutation; the amended slice runs with AMENDED_NULL = 1).

### Battery cell registry note

The amended slice re-uses the committed BATTERY_REGISTRY_V1.json unchanged
(same task ids, seeds, member and boundary cells); only the null-arm
materialization differs. The rerun is bounded (bounded_r02r04_v1.py: the
1360 static affine/decision/pair_lift tasks, imap_unordered progress log,
2-hour hard cap). FROZEN_PREDICTIONS_V1.json is regenerated under the amended
materialization for the four used gens (affine, decision, pair_lift,
constant), so null rows are re-predicted under the joint full-row null; the
mono_step and stream rows carry the committed table (out of scope here). This
is the fresh-custody prediction table of the amended package.

### Predicted outcome (derived before the rerun, F7 style)

With the joint full-row null every perm_null champion is a noise fit; the
cost-minimal champion on a decorrelated response is S_CONST, so C1
(0/200 null recoveries) is predicted to hold for both families. The member
census, boundary twins, frozen-prediction match, and PROC2 agreement cells are
untouched by the null change and keep their measured values.
