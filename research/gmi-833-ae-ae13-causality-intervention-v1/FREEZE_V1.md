# GMI #833 Section AE13 — causality and intervention: prospective freeze v1

Source `main`: `5e57d4292266bccf435136e1f7d72caa32e920a0`.

Committed **before** any executor, oracle, test, receipt, theorem note or
reconciliation file of this package exists in the tree.

## Rows this tranche may reconcile (verbatim, from issue comment 5692689542)

Anchor heading (verbatim, three hashes):

> `### AE13 — Causality and intervention`

1. `- [ ] Prove that observational compression/prediction does not generally identify causal structure.`
2. `- [ ] Construct observationally equivalent worlds with different intervention consequences.`
3. `- [ ] Define when interventions are required for the behavioral specification.`
4. `- [ ] Derive the value of intervention under resource cost.`
5. `- [ ] Distinguish predictive state from causal/control state.`
6. `- [ ] Relate to causal-state, causal-representation-learning and causal-inference parents precisely.`

## Row explicitly NOT closed here

`- [x] Test whether causal structure changes selected morphology relative to observational prediction alone.`

That row is Tier 2 in `AE_ROW_TIER_ASSIGNMENT_V1.json` and is **already closed**
by `gmi-833-ae-morphology-sweep-v1` `SWEEP-5` in a sibling lane. This tranche
neither re-closes it nor depends on it.

**No neighboring row is earned here.** No AE1, AE4, AE5, AE7, AE8 or other AE
row, no row of any other issue comment, and no row of the #833 issue body, is
earned by this tranche.

## Frozen scope

- **Variables.** Three binary variables `A, B, C` over `{0,1}`; the joint
  support has `8` atoms. Every probability in the package is an exact
  `Fraction`.
- **Structural causal models.** A registered census of SCMs over the `25`
  labelled DAGs on three vertices, each parameterised by conditional
  probability tables drawn from a **frozen finite rational grid**
  `G = {0, 1/4, 1/2, 3/4, 1}` — declared here, so the census is reproducible
  and exhaustive over `G` rather than sampled.
- **Interventions.** `do(V = v)` for a single variable, defined by the standard
  truncated-factorisation: delete the incoming edges of `V`, set its value, and
  keep every other conditional unchanged. Only single-variable atomic
  interventions are in scope; `MULTI_VARIABLE_INTERVENTION_PROVED` is a
  forbidden promotion.
- **Behavioral specification.** A registered finite set of queries, each an
  exactly rational functional of an interventional distribution, together with
  an exactly rational tolerance.

All arithmetic is `fractions.Fraction` or `int`. No float appears in any claim;
the test asserts by AST scan that no float literal reaches a reported quantity.

## Frozen definitions

- Two SCMs are **observationally equivalent** iff their observational joints
  agree on **all 8 atoms** as exact rationals — cell by cell, not by a summary
  statistic.
- The **predictive state** of a world for target `Y`: the partition of the
  observed-variable support by the map `x -> p(Y | x)`.
- The **causal/control state** for a registered intervention target: the
  partition of the support by the map `x -> p(Y | do(...) , x)`, i.e. the
  coarsest partition sufficient for the interventional answer.
- Interventions are **required** for a specification `Spec` iff the
  observational equivalence class of the world contains two members whose
  `Spec` answers differ by more than the registered tolerance. They are **not**
  required iff every member of the class answers within tolerance.
- **Value of intervention** at budget `b` and price `pi`:
  `VoInt = bestSpecScore(with b interventions) - bestSpecScore(observational
  only)`, an exact rational; acquire iff `VoInt > pi`.

## Required evidence and falsifiers

- `CI-1` (row 1): the non-identification claim, proved at the registered scope
  rather than asserted — for **every** Markov equivalence class on three
  vertices containing more than one DAG, an exhibited pair of parameterisations
  with **identical** observational joints (all 8 atoms equal) and **different**
  interventional distributions, plus the census count of such pairs over the
  frozen grid. Classes for which no such pair exists over `G` are reported with
  count `0`, never omitted. The claim must be stated with its quantifier: *not
  generally identified*, not *never identified* — a world whose class is a
  singleton **is** identified, and the count of those is reported too.
- `CI-2` (row 2): the full observational equivalence class of a named witness
  enumerated exhaustively over `G`, with the interventional disagreement given
  as an exact rational interval (minimum and maximum answer across the class).
- `CI-3` (row 3): the exact requirement condition above, with machine-checked
  witnesses on **both** sides — a specification for which interventions are
  provably required, and one for which the observational class answers within
  tolerance so they are provably **not** required. The tolerance at which the
  verdict flips is computed exactly.
- `CI-4` (row 4): the exact break-even price for intervention for every
  registered specification, with witnesses strictly on each side and the
  behaviour **at** the break-even price reported rather than skipped. The
  value of intervention must be shown to be `0` for at least one registered
  specification — intervention is not universally worth its cost, and claiming
  otherwise is a defect.
- `CI-5` (row 5): worlds where the predictive state and the causal/control
  state **differ**, with the census counts of `EQUAL`,
  `PREDICTIVE_STRICTLY_REFINES`, `CAUSAL_STRICTLY_REFINES` and `INCOMPARABLE`;
  each relation with count `0` reported as such.
- `CI-6` (row 6): a machine-readable parent crosswalk with citations covering
  do-calculus and identifiability, Markov equivalence, causal discovery, causal
  representation learning and computational-mechanics causal states, each entry
  stating what is **parent-owned**. `PARENT_SUFFICIENT` terminals are
  **successes** and are recorded as such. The crosswalk must explicitly
  separate the computational-mechanics sense of `causal state` (a predictive
  equivalence class, **not** interventional) from the Pearlian sense, because
  conflating them is the specific error this row exists to prevent.
- Two materially independent routes for every computational claim. Route B is
  written separately, imports nothing from route A, and computes interventional
  distributions by explicit sampling-free enumeration over the exogenous noise
  representation rather than by route A's truncated factorisation.
- Hostiles must be shown to **move their target quantity** before they are
  shown to be **detected**. At least one hostile must be the specific error the
  section warns about: reading an interventional answer off the observational
  joint.
- A null the true result beats, with the no-alarm case asserted on known-clean
  input.
- `RESULT_V1.json` byte-identical under `python3 -I -B` and `python3 -I -O -B`.

## Claim ceiling

`GMI_833_AE13_OBSERVATIONAL_TO_CAUSAL_NON_IDENTIFICATION_EXACTLY_CENSUSED_AND_PRICED_AT_REGISTERED_FINITE_SCOPE`

## Forbidden promotions

`OBSERVATIONAL_DATA_NEVER_IDENTIFIES_CAUSAL_STRUCTURE`,
`CAUSAL_DISCOVERY_IMPOSSIBILITY_PROVED`,
`MULTI_VARIABLE_INTERVENTION_PROVED`,
`LATENT_CONFOUNDER_GENERAL_CASE_PROVED`,
`CONTINUOUS_VARIABLE_EXTENSION_PROVED`,
`INTERVENTION_ALWAYS_WORTH_ITS_COST`,
`COMPUTATIONAL_MECHANICS_CAUSAL_STATE_IS_PEARLIAN_CAUSAL_STATE`,
`GMI_MORPHOLOGY_PREDICTION`,
`ARCHITECTURE_SELECTION_LAW`,
`COMPLETE_GMI`.

Parent-owned and not claimed novel: do-calculus, truncated factorisation and
identifiability (Pearl 1995, doi:10.1093/biomet/82.4.669; Pearl 2009,
doi:10.1017/CBO9780511803161), Markov equivalence of DAGs (Verma & Pearl 1990;
Andersson, Madigan & Perlman 1997, doi:10.1214/aos/1031833662), causal
discovery (Spirtes, Glymour & Scheines 2000,
doi:10.7551/mitpress/1754.001.0001), elements of causal inference (Peters,
Janzing & Schölkopf 2017), causal representation learning (Schölkopf et al.
2021, doi:10.1109/JPROC.2021.3058954), experimental design for causal discovery
(Eberhardt, Glymour & Scheines 2005; Hauser & Bühlmann 2014,
doi:10.1111/rssb.12071) and computational-mechanics causal states (Shalizi &
Crutchfield 2001, doi:10.1023/A:1010388907793). The residual is the exhaustive
exact-rational census over the frozen grid that turns *not generally
identified* into counted statements with both quantifiers attested, and the
priced value-of-intervention threshold with a registered specification whose
value of intervention is exactly zero.
