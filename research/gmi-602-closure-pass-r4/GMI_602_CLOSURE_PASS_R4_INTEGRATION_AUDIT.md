# GMI #602 closure-pass R4 — integration audit

Date audited: 2026-09-14.
Live ledger: #602.
Contributed ZIP SHA-256: `c9dcbd003a301331c56b616c61576896547b64e744f6e2c904f8f96f1273404f`.

This artifact records an adversarial audit of the user-contributed `gmi-602-closure-pass.zip`. It intentionally does **not** import the bundle's historical checkbox/accounting snapshot as current #602 truth. The repository and #602 continued moving after the bundle was assembled, including later Section D prospective evidence.

## 1. What the bundle contains

The contribution includes:

- a 451-open-item gap ledger across 49 sections;
- a strongest-parent atlas;
- 38 formal results / derivation notes;
- exact certificate files and generators;
- domain and falsification registries;
- closure-accounting and open-item snapshots;
- executable microscope/certificate generators;
- explicit retractions rather than silent claim repair.

Its own claim ceiling remains conservative: the contribution does not claim complete-theory closure and flags two high-risk parent-subtraction lanes as still unresolved.

## 2. Reproducibility audit

The bundle's generators were executed against the contributed files. With the author's original absolute working path emulated, the generated ledger/certificate/registry/accounting outputs reproduced the committed outputs exactly.

A packaging defect was then identified: four scripts used the author-local path `/home/claude/gmi602`, despite `APPLY.md` describing execution from a checked-out directory. The validation copy replaced those absolute roots with `Path(__file__).resolve().parent` in:

- `build_ledger.py`;
- `render_ledger.py`;
- `microscopes.py`;
- `m3_superadditive.py`.

After that portability-only repair, every generated artifact again reproduced byte-for-byte. No theorem statement, certificate value, ledger row, or accounting result changed.

## 3. Scientifically useful material retained from the contribution

### Section D normal-fan / sensitivity material

The bundle formalizes the parent-owned fact that finite linear-price morphology selection is the lower/normal fan of the resource hull, with pairwise equality hyperplanes refining the actual winning fan. It also records a perturbation bound for phase-wall normals under resource-count error.

These are useful governance tools, but they are convex/polyhedral sensitivity results rather than novel GMI mathematics.

### Finite-size extrapolation material

The bundle records a parent-owned finite-size expansion: when registered resource counts are affine in scale, a pairwise price wall has a rational `pi*(s)=pi*_infinity+c/s+O(1/s^2)` form away from singular denominators.

This supplied theory input for fresh prospective Section D scale tests; the retrospective formula itself was not treated as sufficient evidence for the #602 extrapolation box.

### Domain/falsification registries

The domain and falsification registries are useful as research-planning inventories. They remain snapshots, not automatic closure authorities. Any live box disposition still requires the corresponding frozen witness / parent subtraction / negative controls.

## 4. Snapshot conflicts with newer live evidence

The bundle predates later Section D work and therefore understates or misstates some live status. In particular, subsequent merged prospective tranches established:

- #674: conditional free-lunch symmetry control, obligation-structure collision, exact tiny-world morphology phases;
- #676: probabilistic, clean neural-like, search/planning phase winners and stochastic-search replication;
- #680: developmental history as a phase axis with executed conversion costs and zero-switch-cost falsifier;
- #685: statistical phase-boundary confidence interval and frozen out-of-scale `n=17,31` extrapolation.

Accordingly, `CLOSURE_ACCOUNTING_R3.json`, `open_items.txt`, and the bundle ledger are provenance snapshots only. They must not overwrite the current #602 body or later reconciliation comments.

## 5. High-risk parent subtractions still explicitly open in the contribution

The bundle correctly refuses to raise its global claim ceiling until at least these reductions are carried through:

1. Levin/OOPS/PowerPlay-style universal / bias-optimal search parents versus the Section E morphogenesis residual.
2. Active-inference / related control-as-inference parents versus the bundle's `G602-C-01` residual.

This audit preserves those as open research obligations rather than interpreting the bundle as a positive complete-theory result.

## 6. Downstream use

The contributed Section D sensitivity and finite-size material was used only as **theory input** for a new preregistered lane (#689 / PR #690). The live first closure of #602's D19/D20 boxes came from independently frozen PR #685; PR #690, if merged, is an exact/combinatorial replication only.

## 7. Claim boundary

This integration audit establishes:

```text
CONTRIBUTED_R4_BUNDLE_REPRODUCED_AFTER_PORTABILITY_REPAIR
SNAPSHOT_LEDGER_NOT_LIVE_AUTHORITY
USEFUL_PARENT_OWNED_DERIVATIONS_AND_RESEARCH_REGISTRIES
HIGH_RISK_PARENT_SUBTRACTIONS_REMAIN_OPEN
NO_COMPLETE_GMI_CLAIM_FROM_BUNDLE
```

The full contributed ZIP is identified by the SHA-256 above; this repository artifact records the audited scientific disposition without vendoring a stale 478-KB patch wrapper or allowing historical checkbox state to override current GitHub evidence.
