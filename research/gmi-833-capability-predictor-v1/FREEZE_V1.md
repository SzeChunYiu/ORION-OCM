# GMI #833 Section K capability-predictor freeze v1

**Pre-implementation freeze.** At this commit the package contains only this file,
`TAXONOMY_V1.md` and `SCOPE_V1.md`. No executor, oracle, test, receipt, manifest,
workflow or reconciliation artifact exists yet. The taxonomy in `TAXONOMY_V1.md`
and the universe generator / input grid in `SCOPE_V1.md` are frozen *before* any
census is run; the git commit order is the evidence.

- parent issue: **#833**, Section K ("Capability theory upgrade")
- package: `research/gmi-833-capability-predictor-v1`
- source main: `c70dd24eeade46a3afe8322c1a0e0c16a648311e`

## 1. Claim ceiling

```text
GMI_833_EXACT_CAPABILITY_PREDICTOR_FAILURE_TAXONOMY_AND_TOTAL_UNCERTAINTY_AT_REGISTERED_FINITE_SCOPE
```

This string is byte-identical in `FREEZE_V1.md`, `MANIFEST_V1.json`, `RESULT_V1.json`,
`CORE.md` and `ISSUE_833_RECONCILIATION_KPRED_V1.json`.

## 2. Exact rows this tranche may reconcile

Anchor line: `# K. Capability theory upgrade`

Exactly these three unchecked rows, verbatim:

```text
- [ ] Derive failure modes prospectively.
- [ ] Build `C_hat = F(M,E,R,H,D,U)` capability predictor.
- [ ] Attach uncertainty/calibration to every capability prediction.
```

**No neighboring row is earned here.**

In particular this tranche does **not** touch, and its receipt may not be read as
evidence for, the Section K test tranche:

```text
- [ ] Test predictor on held-out synthetic machine species.
- [ ] Test predictor on held-out known architectures.
- [ ] Test predictor on real trained systems.
- [ ] Predict qualitative failure before evaluation.
- [ ] Predict quantitative resource/capability curves before evaluation.
- [ ] Measure calibration error.
- [ ] Measure out-of-distribution failure.
```

**Deliberately left open, stated in advance.** "Derive failure modes prospectively"
means the failure-mode taxonomy is *derived from registered structure and frozen
before the census*. It is **not** "predict qualitative failure before evaluation":
no held-out system, no pre-registered per-system prediction, and no evaluation
campaign occurs here. Likewise "attach uncertainty/calibration to every capability
prediction" is closed as *total typed attachment plus exact finite coverage and
dependence-safe budget composition*; it is **not** "measure calibration error",
which requires an empirical audit population and is left to the second tranche.
The predictor below is deliberately built so that those seven rows are executable
next round: the frozen scope object, the emit contract and the receipt schema are
all parameterised by the registered universe, so a held-out universe can be
substituted without changing `F`.

## 3. Frozen strongest-parent subsumption

Parent-owned mathematics that this tranche imports and does **not** claim as novel:

| parent | owns |
|---|---|
| #837 `gmi-833-foundation-v1` | behavioral specification `B`, realization contract `M=(X,x0,Q,U,Chi,rho)`, developmental law `Delta` and `Reach_Delta(M0,B)`, the 14-coordinate lifecycle resource contract (from #805), `forall_fin[U]` notation, evidence/maturity ladder |
| #848 `gmi-833-morphcap-v1` | external capability contract `c=(T,mu,u,V,b,tau)`, `C_c(M)=E_{t~mu}[u(trace)]`, CAP-2 ceilings / impossibility regions / admissible-class and resource monotonicity, CAP-3 observational-aliasing information ceiling |
| #851 `gmi-833-global-uncertainty-v1` | U-1 five typed uncertainty constructors, U-2A exact relational image composition, U-2B dependence-safe `1-alpha-sum(beta)` bound and the refusal of the independence product, U-3A/U-3B missing/empty relation semantics, U-4A exact query identification, U-4B confidence image preservation, U-5 marginal non-identifiability |
| #913 `gmi-833-capability-abstention-v1` | ABSTAIN-1: a point is emitted iff the exact query image over survivors is a singleton; forced-point counterexample theorem; the four machine-distinct terminals |
| #906 `gmi-833-capability-bounds-interactions-v1` | BOUND-1 floors/ceilings, INT-1 mixed-difference interaction, BUDGET-1 mandatory shared-charge interference iff |
| #874 `gmi-833-global-vs-reachable-morphology-v1` | separation of the globally optimal candidate from the developmentally reachable one |
| #877 `gmi-833-finite-search-budget-morphology-v1` | finite deterministic complete search trace, cost-feasible prefix, budget-indexed visibility |
| #854 `gmi-833-axiom-core-v1` | registered finite axiom core |

Frozen parent `RESULT_V1.json` blob shas (git blob ids at `source_main`):

- foundation: `c0c574c4ec6e237d5fdafa694eac131399625a70`
- morphcap: `bdc5c3cd42e312d8c7af52f7ba84220631a25f8a`
- global_uncertainty: `9ab16cf59087214e093ace3b18c6d08fc79ab871`
- capability_abstention: `d0616a04cde834f2329e376b395366981a1c7893`
- capability_bounds: `7ff80bab4a0b9e967e02cc6943bbe8828e3acea0`
- global_vs_reachable: `37a0dda56649c02de1dd733b20a1266d481a3d30`
- finite_search_budget: `4ea315e651475cc8afcc39860a0d2ac621e9f571`
- axiom_core: `3366a3bc7236d286f8d123bf53e4e3b2d22ad7b9`

**Historical non-authority.** `research/gmi-capability-predictor-v1/`,
`research/gmi-capability-predictor-dev-v1/` and `research/gmi-capability-calibration-v2/`
are pre-#833 work under the #602/#764/#766 ledger. They are mined for design ideas
(the architecture-name-free descriptor, the signed-margin monotone envelope, the
determinate-frame-before-sample rule) and are cited as `historical_non_authority`.
Their results are **not** evidence for any claim in this tranche, and none of their
receipts is pinned as a parent authority.

The brief's `research/gmi-833-theory-baseline-v1/BASELINE_V1.md` does not exist at
`source_main`; the governing baseline used instead is
`research/gmi-833-foundation-v1/FOUNDATION_THEOREMS_V1.md` sections 1, 2, 9, 10, 11
(claim ceiling, evidence/maturity ladder, `forall_fin` notation, forbidden
promotions).

## 4. Frozen formal scope

1. `F` is an **exact, total, deterministic** function on the registered typed input
   grid. It is not fitted, sampled, regressed or learned. All arithmetic is
   `fractions.Fraction` / `int`. No float appears in any claim.
2. The six inputs are exactly the registered objects `M, E, R, H, D, U`. No new
   primitive object is introduced.
3. **Candidacy vs contract.** `M`, `H`, `D` and the registered search-budget cut
   determine *which realizations are consistent with the inputs* (the survivor set
   `C`). `E` and `R` determine the *capability functional*
   `q_{E,R}(x) = cap_E(x)` when `x` is resource-admissible and the distinguished
   value `UNSATISFIED` otherwise. A resource-inadmissible realization is therefore
   **not removed from `C`**; per CAP-1 ("if no admissible execution exists,
   capability is not fabricated; the contract is unsatisfied") it stays a candidate
   carrying `UNSATISFIED`. `UNSATISFIED` is a distinct bottom, not the number `0`,
   and it fails every registered threshold.
4. The registered search cut `Seen(B)` is a **candidacy** restriction (which
   realizations the registered finite deterministic search could have produced
   within budget `B`). This tranche registers **no selection or optimality rule**
   and makes no claim that the selected system optimises the contract score.
   Search-objective/contract-proxy misalignment is out of scope and is filed as
   `GAP-KPRED-SEARCH-OBJECTIVE-MISALIGNMENT`.
5. Emission vocabulary is exactly #851/#913's: `IDENTIFIED`, `CANNOT_IDENTIFY`,
   `INCONSISTENT_REGISTERED_ASSUMPTIONS`, `CANNOT_CHECK`. No fifth terminal.
6. Every emission carries a U-1 typed uncertainty object. A `FEASIBLE_SET` carries
   no coverage statement; only a `CONFIDENCE_SET` may carry a composed budget, and
   that budget is the U-2B dependence-safe `max(0, 1 - alpha - sum beta_i)`.
   The independence product is refused.
7. The registered universe and input grid are those in `SCOPE_V1.md` and are frozen
   at this commit. Per-mode non-emptiness is a **discovered** fact of the census,
   not a design target; if a mode is empty on the frozen grid the receipt reports
   it empty and any witness supplied afterwards is labelled a constructed witness
   outside the frozen census.

## 5. Frozen theorem acceptance items

Named results that must be stated, proved and exactly replayed:

- **KP-1A** `F` is total, deterministic and exception-free on the registered grid.
- **KP-1B** (soundness, unconditional) if `F` emits `IDENTIFIED(y)` then every
  realization consistent with the registered inputs has capability exactly `y`.
- **KP-1C** (completeness, exact iff) `F` emits a point iff `q_{E,R}` is constant on
  the nonempty survivor set; when it is not constant, abstention is *forced* and the
  census exhibits two survivors with different capability.
- **KP-1D** (boundary, EARNED-BY-COUNTEREXAMPLE) the bridge from KP-1B to a
  real system requires the registration to be truthful; a mis-registered constraint
  that excludes the true realization admits a sound-looking wrong point. Exhibited
  counterexample, not an assumption swept under the rug.
- **KP-2A** the six registered ladder ceilings are nonincreasing (CAP-2A instance).
- **KP-2B** the ten-class failure-mode taxonomy is a partition of the registered
  input grid: pairwise disjoint and jointly exhaustive, zero overlaps, zero gaps.
- **KP-2C** (unique binding cut) if the assigned mode is ladder index `i`, then
  `A_{i-1}` contains a `>= tau` witness and `A_i` does not; `P_i` is the unique cut
  that, conditional on all preceding registered cuts, destroys attainability.
- **KP-2D** (boundary, EARNED-BY-COUNTEREXAMPLE) first-crossing attribution is
  order-dependent; all `5! = 120` cut orders are censused, the exact order-sensitive
  count is reported, and a two-cut counterexample is exhibited.
- **KP-3A** (total attachment) no code path emits a bare value: every `return` in the
  reachable predictor call graph is a call to the single `emit` constructor
  (verified by `ast`, not by inspection), every emission validates its uncertainty
  object, and the grid census raises zero exceptions.
- **KP-3B** (budget composition) the emitted coverage budget equals the U-2B
  dependence-safe bound for the registered relation chain on every confidence case;
  the independence product is strictly larger and is refused.
- **KP-3C** (exact finite coverage) over all registered (input, consistent-world)
  pairs the emitted object contains the true capability value in exactly 100% of
  pairs; this is an exact finite coverage statement, **not** an empirical
  calibration-error measurement.

## 6. Frozen falsifiers

The tranche is RED if any of the following occurs:

- a point is emitted for a multi-valued image, or a singleton image is forced to abstain;
- a resource-inadmissible realization is silently removed from the survivor set,
  or `UNSATISFIED` is coerced to `0`;
- any emission lacks a well-formed typed uncertainty object, or any `return` in the
  reachable predictor call graph bypasses `emit`;
- a `FEASIBLE_SET` emission carries a coverage/calibration number;
- a composed budget uses the independence product, or differs from `1-alpha-sum(beta)`;
- the taxonomy admits an input in two modes or in none;
- the order census is not run, or its order-sensitive count is not reported;
- the two routes disagree on any grid point, or route B imports route A;
- the null predictor is not strictly beaten on exact soundness counts;
- any hostile is not DETECTED;
- a float enters any claim;
- any second-tranche row is reconciled, or the receipt is read as held-out,
  real-system, calibration-error or OOD evidence;
- a parent result blob drifts from its pinned sha.

## 7. Forbidden promotions

```text
HELD_OUT_PREDICTOR_VALIDATION
KNOWN_ARCHITECTURE_VALIDATION
REAL_SYSTEM_CAPABILITY_VALIDATION
EMPIRICAL_CALIBRATION_ERROR_MEASURED
OOD_FAILURE_MEASURED
QUALITATIVE_FAILURE_PREDICTED_BEFORE_EVALUATION
QUANTITATIVE_RESOURCE_CURVE_PREDICTION
UNIVERSAL_CAPABILITY_PREDICTION
CAPABILITY_PREDICTOR_EMPIRICALLY_VALIDATED
CALIBRATION_FROM_FEASIBILITY_ALONE
UNIVERSAL_UNCERTAINTY_CALIBRATION
COMPLETE_GMI
ONTOLOGICAL_COMPLETENESS
```
