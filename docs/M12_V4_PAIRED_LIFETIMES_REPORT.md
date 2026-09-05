# M12 V4 — paired lifetimes with a pre-registered primary family

Pre-registration: `research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V4.md` (frozen on the V4 stream-manifest
hash before the run). Evidence: `research/ocm-m12/M12_PAIRED_LIFETIMES_EVAL_V4.json`,
`docs/provenance/M12_PAIRED_REPLICATION_RECEIPT_V4.json`, bound by `docs/provenance/M12_PAIRED_RECEIPT_V4.json`.
Theory: batch 7 G7 (licence vs truth), G8 (sizes, powers, family bound, collapsed one coin); ledger S37–S38.

## 1. Why V4 after V3

Batch 7 G8 showed the V3 rule was under-specified: no primary family, an unbounded family count
(FWER ≤ α only for ≤ 6 families) and a two-sided unanimous test with power 0.43. V3 stays the frozen
record of its own rule (10 families 8/8); V4 re-registers the analysis and runs on **fresh** streams
(seed `OCM-M12-V4`) with the world-true out-of-scope half (G7).

## 2. Result

| Family | role | OCM mean | parent mean | OCM > parent | one-sided p | verdict |
|---|---|---|---|---|---|---|
| A conversations | **primary** (α = 0.05) | 0.982 | 0.607 | 8/8 | 0.0039 | **OCM_RESIDUAL** (not collapsed: differences vary across streams) |
| A post-deployment lessons | secondary (α/6) | 0.881 | 0.714 | 8/8 | 0.0039 | OCM_RESIDUAL ⚑ collapsed |
| A honest unknown (20 world-false + 10 world-true) | secondary | 0.967 | 0.567 | 8/8 | 0.0039 | OCM_RESIDUAL ⚑ collapsed |
| D causal identification | secondary | 1.000 | 0.600 | 8/8 | 0.0039 | OCM_RESIDUAL ⚑ collapsed |
| E cross-domain transfer | secondary | 1.000 | 0.000 | 8/8 | 0.0039 | OCM_RESIDUAL ⚑ collapsed |
| F revision integrity | secondary | 1.000 | 0.000 | 8/8 | 0.0039 | OCM_RESIDUAL ⚑ collapsed |
| G self-repair | secondary | 1.000 | 0.000 | 8/8 | 0.0039 | OCM_RESIDUAL ⚑ collapsed |
| A factual, A negative transfer, D communication | descriptive | 1.0 / 1.0 / 1.0 | 0.9 / 0.714 / 0.5 | 8/8 | — | descriptive (not pre-registered) |
| B/C work, D selection, D analysis, D proof, unknown-domain refusal | descriptive | equal | equal | ties | — | descriptive ties |

Kill gates 0 (chain identity continuous in all 8 lifetimes). **Decision (pre-registered rule):
`OCM_LIFETIME_RESIDUAL_SUPPORTED`** — the primary family rejects at p = 0.0039 (8/8, the rule needs
≥ 7/8), in scope relative to the matched whole-system parent buildable here; the frontier-class
parent remains CANNOT_CHECK_MATCHED_PARENT.

⚑ Collapsed one coin: every secondary family has *identical* differences in all eight lifetimes —
these families are deterministic functions of the planted design (which fault, which revision event,
which transfer cells), so the stream substitution does not vary them and the eight differences carry
the evidence of one coin (G8). They are reported as rejections with the flag; the inferential weight
of V4 rests on the primary family, whose differences vary across streams (parent 0.574–0.611).

Honest-unknown detail (G7): OCM 29/30 in every lifetime; the one miss is "is a whale a mammal",
which the world-true half labelled unlicensed although the manifest holds it as a verified fact —
a label defect of the stream generator (ledger S38), penalising both arms equally; V4 stands as
frozen and the generator gains a licence check for the next version.

## 3. Replication

REPLICATION_PLACEHOLDER

## 4. Reference arm on the same streams, four-class grading (G7)

REFERENCE_PLACEHOLDER

## 5. What V4 does and does not show

* A pre-registered, replicated lifetime-level residual on the primary family under a rule with
  known size (9/256) and power (0.81 at p = 0.9); six pre-registered secondary rejections whose
  evidential weight is limited by the collapse flag; PARENT_SUFFICIENT descriptively wherever no
  revision, identification, role typing or repair is needed.
* Not shown: a residual against a frontier-class parent, natural-language generality beyond the
  bounded world, human usefulness. The reference arm is labelled REFERENCE and never enters a decision.
