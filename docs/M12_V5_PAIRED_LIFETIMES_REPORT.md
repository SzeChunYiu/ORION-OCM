# M12 V5 — paired lifetimes on the corrected runtime (protected, pre-registered)

Pre-registration: `research/ocm-m12/M12_LIFETIME_PREREGISTRATION_V5.md` (SHA-256 `6f29ab7ee4d1009ec2db54d32f593d2e38522b182fe29a2f8447fade9728cbd7`), frozen at commit bb459b9 before any outcome was read. Streams: `M12_V5_STREAM_MANIFEST_V1.json` (SHA-256 `db8c2d0c2e76f685606d041d779278ea2a6955049e9ef18b3fbc12b52b045729`, seed OCM-M12-V5, 8 fresh lifetimes, leak check 8/8). Result: `M12_PAIRED_LIFETIMES_EVAL_V5.json` (billy-old); replica `billy-laptop` byte-identical in the deterministic block (`docs/provenance/M12_PAIRED_REPLICATION_RECEIPT_V5.json`, MATCH). Study status recorded by the evaluation code: `PROTECTED_PREREGISTERED_V5__FRESH_STREAMS_CURRENT_RUNTIME`.

## Decision

**OCM_LIFETIME_RESIDUAL_SUPPORTED** under the pre-registered V5 rule; kill gates 0 hits (identity chain continuous in 8/8 lifetimes; adoption predecessors bound in 8/8 self-repair episodes: [True, True, True, True, True, True, True, True]; protected exposure 0; external IO 0; no dead skill run after revocation; frozen manifest regenerated identically).

Scope of the claim: one bounded world under lexical substitution, eight paired lifetimes, the whole-system parent matched in information and acceptance discipline. No frontier language-model parent was matched; no claim outside the bounded world; no novelty claim.

## Pre-registered families

| Family | Role | OCM mean | Parent mean | Positive / non-tied | one-sided p | Verdict |
|---|---|---|---|---|---|---|
| A_conversations | primary | 0.9954 | 0.6088 | 8/8 | 0.00391 | OCM_RESIDUAL |
| A_post_deployment | secondary | 0.8929 | 0.7143 | 8/8 | 0.00391 | OCM_RESIDUAL |
| A_honest_unknown | secondary | 0.9667 | 0.5667 | 8/8 | 0.00391 | OCM_RESIDUAL; collapsed one coin |
| D_causal | secondary | 1.0 | 0.6 | 8/8 | 0.00391 | OCM_RESIDUAL; collapsed one coin |
| E_transfer | categorical | 1.0 | 0.1667 | 8/8 | — | CATEGORICAL (pre-registered descriptive); collapsed one coin |
| F_integrity | categorical | 1.0 | 0.0 | 8/8 | — | CATEGORICAL (pre-registered descriptive); collapsed one coin |
| G_self_repair | categorical | 1.0 | 0.0 | 8/8 | — | CATEGORICAL (pre-registered descriptive); collapsed one coin |

The primary family rejects with the machine ahead in all eight lifetimes; its differences take three values ([0.3704, 0.3889, 0.4074]), so it is not collapsed. Of the three inferential secondaries, post-deployment lessons rejects with two difference values (not collapsed); honest unknown and causal identification reject at 8/8 but their eight differences are identical, so both carry the collapsed-one-coin flag as pre-registered: they are reported with the flag and add no independent weight. Secondary rejections recorded: ['A_post_deployment', 'A_honest_unknown', 'D_causal'].

## Categorical families (pre-registered descriptive; never tested)

| Family | Wins | Ties | Losses | Identical in all lifetimes |
|---|---|---|---|---|
| E_transfer | 8 | 0 | 0 | yes |
| F_integrity | 8 | 0 | 0 | yes |
| G_self_repair | 8 | 0 | 0 | yes |

**Prospectively matched transfer cells (issue #38).** Both arms now answer the same six cell questions on identical inputs; the parent uses its own mechanism (name-similarity transfer with no role or semantics check). Lifetime 0 cells (identical pattern in all eight):

| Cell | Expected | OCM | Parent |
|---|---|---|---|
| partial_adapter_required | ADAPTER_REQUIRED | ADAPTER_REQUIRED | SIMILARITY_TRANSFER_FAILED |
| representation_correspondence | TRANSFER | TRANSFER | SIMILARITY_TRANSFER_FAILED |
| deceptive_analogy | REFUSE_TRANSFER | REFUSE_TRANSFER | ACCEPTED |
| science_full_mapping | TRANSFER | TRANSFER | TRANSFER |
| science_missing_binding | ADAPTER_REQUIRED | ADAPTER_REQUIRED | TRANSFER |
| science_lookalike_verifier | REFUSE_TRANSFER | REFUSE_TRANSFER | TRANSFER |

The parent accepts the two deceptive cells the machine refuses and cannot produce the adapter-required and full-mapping transfers; the comparison is now determined (6 vs 6 cells) and is reported as categorical because its per-lifetime difference is a function of the design, not of the stream.

## Descriptive families

A_factual, A_negative_transfer, B_enterprise, C_software, D_selection, D_analysis, D_proof, D_communication, unknown_no_action — not pre-registered; no inference is drawn. Work families B and C and the selection, analysis and proof families tie.

## Reference arm (F8: unbound pretraining; beside the decision, never inside it)

Qwen2.5 7B instruct (Ollama digest prefix 845dbda0, temperature 0) on the same eight streams: factual in scope 230/240; honest unknown 18/240; negative transfer 38/56; always-attempts per stream [29, 27, 30, 23, 26, 30, 27, 30]. Four-class grading over the questions whose licensed answer is yes or unknown: licensed 243, unlicensed-true 180, unlicensed-false 47, wrong 2. The unlicensed-true count is the signature of a channel outside the given knowledge, as in V4. Result file `research/ocm-m12/M12_V5_REFERENCE_ARM_V1.json`; runner `ocm.evaluation.m12_reference_arm`.

## Post-run code change, declared

After the run, `phase_G` was changed so that the `predecessors_bound` field is emitted only on the V5 path (`report_predecessors=True`), because the lane's frozen engineering replay of the lifetime evaluation (`M12_REFERENCE_REPLAY_V4.json`, compared in CI) includes the self-repair block and must stay byte-identical. The V5 computation path is unchanged; to show it, the frozen V5 run was replayed with the changed code to a new path (`M12_PAIRED_LIFETIMES_EVAL_V5_REPLAY_POSTREFACTOR.json`) and its deterministic block is identical to the frozen result. The receipt binds both files and the changed sources; the frozen result file itself was never rewritten.

## What V5 establishes and what it does not

- Establishes, at its stated scope: the primary-family lifetime residual survives on the corrected runtime under a pre-registration frozen before outcome access, with the corrected adoption gate and predecessor binding as kill gates, and the transfer comparison determined by matched cells.
- Does not establish: any residual over a learned language model; anything about natural language beyond the bounded world; independent evidence from the two collapsed secondaries or from the categorical families.
- Next study named: per-lifetime variation of the planted design (faults, revision events, transfer maps) so that the categorical families can become inferential.
