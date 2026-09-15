# K4 substitution per-cell audit under repaired pricing

Date: 2026-09-15. Lane: `machine-intelligence-morphogenesis-v1`.
Package: `gmi_k4_substitution_percell_audit_v1/`.
Auditor: `gmi_k4_substitution_percell_audit_v1.py`.
Stage receipt: `microscopes/results/STAGE_K4_SUBSTITUTION_PERCELL_AUDIT_V1.json`
(and package-local `STAGE_K4_SUBSTITUTION_PERCELL_AUDIT_V1.json`).
Depends on: `GMI_K4_SUBSTITUTION_REPAIR_V1.md`, `gmi_k4_substitution_repair_v1.py`,
`STAGE_K4_SUBSTITUTION_REPAIR_V1.json`, `GMI_K4_V5_DEV_SWEEP_RV_377_107.json`,
`GMI_K4_LOFO_FREEZE_V1.json`.

Closes checklist items **22**, **23**, **35** clause **(a)** on the MIM repair
lane: which of the 159 frozen `THEORY_RED` cells **admit a substitution under
the repaired pricing**.

## Parent subtraction

| parent | first refusal |
|---|---|
| `GMI_K4_COST_STRUCTURE_ROOT_CAUSE_V1` | diagnoses no channel trade in frozen V4 |
| `GMI_K4_SUBSTITUTION_REPAIR_V1` + `STAGE_K4_SUBSTITUTION_REPAIR_V1.json` | establishes R1/R2/R3 create a material storage↔serve trade and recover retention by label-free search |
| `GMI_NEUTRAL_SEARCH_ADEQUACY_THEOREM_V1` NS-1 consequence 2 | substitution-defined targets with no expressible witness are `INCONCLUSIVE_GRAMMAR`, not `THEORY_RED` |
| sibling package `research/gmi-k4-substitution-cell-audit-v2/` | classifies which cells *target* a substitution (property-vector only) |

This package adds only the **repaired-pricing admission** partition. It invents
no morphology, no pricing correction, and no campaign.

## Method

1. Load the 159 `THEORY_RED` cells from `GMI_K4_V5_DEV_SWEEP_RV_377_107.json`.
2. Classify each cell's LOFO property vector for substitution kinds
   (retention/caching, external authority, amortisation, parameter sharing,
   sparsity specialisation, latent compression).
3. Read `STAGE_K4_SUBSTITUTION_REPAIR_V1.json` and require
   `q1["R1+R2 repaired"].material_trade == true` with frozen control false.
4. A cell **admits substitution under repaired pricing** iff at least one of its
   kinds is in the repair-expressed set **and** the stage material trade holds:

| kind | expressed by repair? | mechanism |
|---|---|---|
| `retention_caching` | yes | R2 store→serve, gated on retrieval |
| `external_authority` | yes | R2 corpus consult |
| `amortisation` | yes | R1 store / reuse; R3 search / reuse |
| `parameter_sharing` | yes | R1 amortises shared state across a context axis |
| `sparsity_specialisation` | **no** | window vs dense is morphology, not R1/R2/R3 |
| `latent_compression` | **no** | latent vs full dim is not the storage↔serve overlay |

Classification is family-constant across grammar × width.

## Admissible vs reachable

| label | claim |
|---|---|
| **admissible** | For cells with `admits_substitution_under_repaired_pricing=true`, the frozen `THEORY_RED` is an *admissible* mis-label under NS-1: the repaired instrument can express the targeted substitution. |
| **reachable** | **Not claimed.** No cell is asserted green. Clause **(c)** (`gmi_k4_repaired_campaign_v1`) owns reachability under repaired pricing. |

Frozen V4/V7 bytes and frozen cell verdicts are untouched.

## Falsifiers

- `STAGE_K4_SUBSTITUTION_REPAIR_V1.json` loses `material_trade` under R1+R2, or
  the frozen control gains it.
- Auditor returns a cell count other than 159, or either partition fails
  `yes + no == 159`.
- A cell with `retrieval != none` is classified `targets_substitution=false`.
- A cell whose only kinds are in `{sparsity_specialisation, latent_compression}`
  is classified `admits_substitution_under_repaired_pricing=true`.
- Receipt claims `frozen_verdicts_rewritten: true` or `frozen_model_mutated: true`.

## Scope

- Sweep: RV-377-107 development grid (22×3×4), `THEORY_RED` slice only.
- Property vectors: LOFO freeze `GMI_K4_LOFO_FREEZE_V1.json`.
- Repair evidence: existing stage receipt; this audit does not re-run the probe.
- Does not duplicate or edit `gmi-k4-substitution-cell-audit-v2/`.
