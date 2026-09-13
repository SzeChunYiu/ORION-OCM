# Measured-profile family selection — MS-2 applied to the charged frontier receipts

Date: 2026-09-12 (lead session). Receipt: `microscopes/results/STAGE_MS2_MEASURED_SELECTION_old.json`
(script `gmi_microscope/ms2_measured_selection.py`, run on billy-old over the committed corpus; pure
aggregation, no search, no fitting, no new evaluation).

## 1. Why this exists

`research/gmi-grand-unification-v1/END_TO_END_DERIVATIONS_V1.md` closes the derivation pipeline
`(E,Ω,Θ) → S* → (κ,τ) → realizations → (ρ, Reach) → Pareto → family` with **synthetic** resource
profiles and names the empirical next step: replace them with independently measured profiles. The
Morphology Selection Theorem (MS-2) gives the quantifier: a family/property is *derived* at a scope iff
every frontier morphology at that scope has it.

The corpus already contains the measured object. Every Stage D'/E' frontier receipt
(`STAGE_DE_SMOOTH_V*.json`, 51 receipts, RV-377-009 … RV-377-062) records, for a registered ecology,
for each of six declared resource models (price columns `B0`…`B3`, `U`, `P3`) and each (reuse horizon
`H`, revision count `r`) cell, the frontier winner rows under the **charged lifecycle meter** (description,
execution, update, revision, verification work actually metered on the VM). Rows are hand-built
parents of known families: `S4` gradient net (coefficient), `S2/S2a` exact linear search (program),
`S5` exemplar table (memory), `S5h` generalizing memory (kNN), `S3` particles (stochastic search).

## 2. What MS-2 returns on the measured data

| quantity | value |
|---|---|
| receipts (ecologies × studies) | 51 |
| scopes = receipt × price column | 309 |
| scopes where ONE family occupies every (H, r) cell — a **derived family** | 82 (27 %) |
| … of which PROGRAM_SEARCH / MEMORY_GENERALIZING / MEMORY_EXACT / STOCHASTIC_SEARCH / other | 55 / 12 / 6 / 3 / 6 |
| scopes with a family **boundary** inside the (H, r) grid — a measured phase transition | 191 (62 %) |
| receipts with a **cross-column inversion** — identical semantics and capabilities, different frontier family under a different resource model | 26 of 51 |

Two worked scopes:

* `STAGE_DE_SMOOTH_V1` (`E_smooth1`): column `B2` derives PROGRAM_SEARCH on 56/56 cells; columns `B0`,
  `B1`, `B3`, `P3`, `U` are mixed, with the boundary at revision count `r: 0 → 1` at every `H` — the exact
  program wins with no revisions, the coefficient learner wins once revision is priced in (11 boundary
  transitions per column, 246 cross-column inversions). This is RV-025's `r*` crossover, now read as an
  MS-2 selection verdict.
* `STAGE_DE_SMOOTH_V22_SYM5_S4` (`E_sym5`): columns `B3`, `P3`, `U` derive STOCHASTIC_SEARCH on 56/56 cells;
  column `B0` flips from STOCHASTIC_SEARCH to MEMORY_GENERALIZING at `(H=1, r: 4 → 8)`; between `B0` and
  `B2` the winner differs at `(H=1, r=1)` and `(1, 2)` while the capability table is column-identical
  (`C2 = True` in the receipt) — E2E-4's "substrate inversion", measured rather than declared.

## 3. Reading

1. **Family identity is a resource consequence, measured.** In 26 of 51 ecologies the same protected
   semantics select different families under different declared resource models. That is the empirical
   content of Substrate Lifting + Physical Resource Bridge + Family Selection on this instrument.
2. **A derived family exists only where the resource model leaves no boundary.** 82 scopes derive one
   family under MS-2; in 191 scopes the honest statement is a phase law in `(H, r)`, and in the remaining
   36 the frontier holds several families with no ordering along the registered axes.
3. **No neural prior.** The coefficient (neural-like) family is derived in 0 scopes as the sole occupant
   of a whole grid and wins only past a revision-count boundary under priced revision; the program family
   is derived most often because the registered ecologies are exactly identifiable (RV-024/RV-041b).
   This matches E2E-2's conditional non-neural selection and is a resource statement, not a claim about
   modern hardware.

## 4. Scope

Same universe as the boundary theorem: 16-input, 8-bit fixed point, hand-built parent rows, six declared
price columns, ecologies of the smooth/table families. The winners are rows, not searched genotypes; the
K4 result (named-family recovery by cost-minimising search fails) is untouched. The receipt is a
re-reading of committed evidence through the selection quantifier and adds no new measurement; it
closes the "synthetic profile" caveat of END_TO_END_DERIVATIONS_V1 §7 at this registered scope only.
Terminal: `MS2_FAMILY_SELECTION_EVALUATED_ON_MEASURED_CHARGED_PROFILES_AT_REGISTERED_SCOPE`.
