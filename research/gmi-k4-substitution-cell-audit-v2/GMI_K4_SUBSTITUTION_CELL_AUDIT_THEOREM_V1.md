# K4 substitution per-cell audit (items 22 / 23 / 35 clause a)

Date: 2026-09-15. Package: `research/gmi-k4-substitution-cell-audit-v2/`.
Auditor: `cell_audit_v1.py`. Input: `AUDIT_INPUT_V1.json` (159 frozen
`THEORY_RED` cells from `GMI_K4_LOFO_FREEZE_V1.json` / RV-377-107).
Receipt: `RECEIPT_V1.json`.

Closes the standing remainder of checklist items **22**, **23** and **35**
clause **(a)** after root cause (#622) and instrument repair (#626):

> per-cell audit of which of the 159 target a substitution

Clause **(c)** (registered campaign under repaired pricing) is a separate
protocol package and is not performed here.

## Method

No campaign is re-run. Each cell is classified from its family's LOFO
**property vector** under a decidable predicate. The predicate encodes the
substitution kinds named by `GMI_K4_COST_STRUCTURE_ROOT_CAUSE_V1.md`:

| kind | marker on property vector |
|---|---|
| `retention_caching` | `retrieval != none` |
| `external_authority` | `external_authority == true` |
| `amortisation` | `state_scales_with != serve_scales_with` and serve names a context axis (`length` / `positions` / `rounds` / `window` / `n_edges`) beyond the state axis |
| `parameter_sharing` | `sharing == shared` with the same amortisation/context pattern |
| `sparsity_specialisation` | `serve_scales_with` contains `window` |
| `latent_compression` | `state_scales_with` contains `latent` |

A cell **targets a substitution** iff at least one marker fires. Otherwise it
is classified `targets_substitution=no` with an explicit non-substitution
reason (variance reduction, verifier compose, equal state/serve scales, etc.).

Classification is **family-constant**: every grammar × width cell of a family
inherits the family's property-vector judgment. That is deliberate — the
question is which *targets* are substitution-defined, not which runs recovered.

## Claim ceiling (admissible vs reachable)

| label | claim |
|---|---|
| **admissible** | Which of the 159 frozen `THEORY_RED` cells have a substitution-defined target property. For those cells, NS-1 consequence 2 makes `INCONCLUSIVE_GRAMMAR` the *admissible* reading of the frozen instrument failure (no channel trade exists to express the mechanism). |
| **reachable** | **Not claimed.** This audit does not assert that any cell is green under frozen or repaired pricing, does not re-run search, and does not flip any registered verdict. Reachability under repaired pricing is clause **(c)**. |

Frozen V4/V7 model bytes and frozen cell verdicts are **untouched**. Sha256 pins
in the auditor fail closed on drift.

## What this does not do

- Does not rewrite `THEORY_RED` → `INCONCLUSIVE_GRAMMAR` in any freeze /
  aggregate / beacon.
- Does not mutate `gmi_k4_resource_native_v4.py` or adopt repaired pricing as
  the registered K4 protocol.
- Does not duplicate clause **(c)** (`gmi_k4_repaired_campaign_v1`).

## Falsifiers

- Any of the six frozen/repair pin sha256s drifts while this package claims
  "untouched".
- Auditor returns a cell count other than 159, or `yes + no != 159`.
- A family with `retrieval != none` is classified `targets_substitution=no`.
- A family with identical `state_scales_with == serve_scales_with`,
  `retrieval == none`, and no latent/window/external marker is classified
  `targets_substitution=yes`.
- Receipt claims `frozen_verdicts_rewritten: true` or `frozen_model_mutated: true`.
