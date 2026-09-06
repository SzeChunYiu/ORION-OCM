# M12 pre-registration V5 — paired lifetimes on the current runtime (issue #38 M12 gates)

Frozen before any V5 outcome is read. V4 (`M12_LIFETIME_PREREGISTRATION_V4.md`, result `M12_PAIRED_LIFETIMES_EVAL_V4.json`, receipt `M12_PAIRED_RECEIPT_V4`) is the frozen record of the runtime before the lifecycle revalidation (#39/#40); its re-run on the corrected runtime (V4-R, `M12_PAIRED_LIFETIMES_EVAL_V4R.json`) is an engineering regression on exposed streams and carries no scientific terminal. V5 is the first protected study whose streams were never exposed to the corrected runtime, so its decision stands as pre-registered.

## Why V5 (what changed since V4, each with its ledger or theory source)

| Finding | Source | V5 answer |
|---|---|---|
| The adoption gate checked a component table keyed by the machine instead of the exact predecessor of the named layer; historical self-repair cells reopened | `docs/RUNTIME_LIFECYCLE_REVALIDATION_V2.md` (#39), ledger S-rows in `OCM_SELF_APPLICATION_LEDGER_V2.md` | corrected runtime; kill gate on `adoption_predecessors_bound` |
| Cross-domain transfer compared six machine cells with four parent cells (undetermined as a comparison) | ledger S38 discussion; V4 report §5.9; #38 M12 | prospectively matched cells: `phase_E(matched_cells=True)` asks the parent the same six cell questions on identical inputs through its own mechanism |
| Six secondary families collapsed to one coin (differences identical in every lifetime because each is a deterministic function of the planted design) | V4 result, `collapsed_one_coin_families` | families whose difference is categorical by design (transfer, revision integrity, self-repair) are pre-registered as CATEGORICAL and never tested; only families with genuine per-lifetime variation are inferential |
| Truth grading rewards an unbound channel; licence grading is exact | theory batch 7 G7 | world-true out-of-scope half kept (10 questions per stream) |

## Frozen items

| Item | Value |
|---|---|
| Runtime | ORION-OCM main at the commit recorded in the V5 receipt (after #75); no code change between this freeze and the run except the receipt tool |
| Streams | 8 fresh streams, seed `OCM-M12-V5`, generator `src/ocm/lifetime/streams.py` (same as V4: lexical substitution of the bounded world, per-stream ordering of the three domains, per-stream work task and science dataset identities, world-true out-of-scope half); manifest `research/ocm-m12/M12_V5_STREAM_MANIFEST_V1.json`, SHA-256 `db8c2d0c2e76f685606d041d779278ea2a6955049e9ef18b3fbc12b52b045729`; leak check must be 8/8 |
| Arms | persistent OCM (one ledger root per lifetime, phases A–G in the stream's ordering) vs the whole-system parent matched in information and acceptance discipline (ledger S27); template floor reported as descriptive only |
| Unit of inference | the lifetime (paired OCM vs parent on one stream); eight lifetimes; nothing pooled across lifetimes except the sign test |
| Primary family | A conversations — one-sided exact sign test (H1: OCM > parent) over the 8 lifetime differences at α = 0.05: rejects iff ≥ 7 of 8 non-tied differences are positive (size 9/256 ≈ 0.035; power 0.81 at p = 0.9) |
| Inferential secondary families (3) | A post-deployment lessons; A honest unknown (incl. the world-true half); D causal identification — same one-sided test at α/3 (rejects iff 8/8) |
| Categorical families (3) | E cross-domain transfer (matched cells), F revision integrity, G self-repair — reported per lifetime as win / tie / loss with the collapsed-one-coin flag; pre-registered as descriptive; no test, no rejection language |
| All other families | descriptive |
| Collapsed-one-coin flag | any family whose eight differences are identical is flagged; a flagged inferential family's rejection is reported with the flag |
| Decision | OCM_LIFETIME_RESIDUAL_SUPPORTED iff the primary family rejects and kill gates are 0; PARENT_SUFFICIENT iff the primary family ties and no secondary rejects; INCONCLUSIVE otherwise; CANNOT_CHECK on any gate hit |
| Kill gates | protected exposure > 0; external IO > 0; a dead skill run after revocation (F); missing phase outcomes; stream leak; identity chain broken at any phase boundary (F5); adoption predecessors unbound in any lifetime; frozen manifest mismatch |
| Reference arm | open-weight model (Qwen2.5 7B instruct, Ollama, temperature 0) on the same eight streams, graded four-class (licensed / unlicensed-true / unlicensed-false / wrong); label REFERENCE (F8); reported beside the decision and never inside it |
| Replication | the deterministic block re-run on a second host must be byte-identical (MATCH) for the receipt terminal to stand; otherwise CANNOT_CHECK (replication mismatch) |
| Outcome access | the V5 result path is written once by `python -m ocm.evaluation.m12_paired_eval --v5`; the tool refuses to run without this file and the frozen manifest; any later run needs a new output path and is an engineering replay |
| What V5 does not claim | no residual over a frontier language-model agent (none matched); no claim outside the bounded world; no human rating; no novelty |

## Stopping rule

One run of eight lifetimes; no extension, no re-sampling. If the result is CANNOT_CHECK the gate hit is reported and the study is not re-run on the same streams.
