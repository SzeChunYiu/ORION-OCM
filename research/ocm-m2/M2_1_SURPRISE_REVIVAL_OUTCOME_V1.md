# M2.1 surprise revival — outcome (dev split, pre-registered)

Receipt: `M2_1_SURPRISE_REVIVAL_RECEIPT_V1.json` (verdict `POSITIVE__EXTRACT_MISSES_REDUCED`, body sha256 `4d10e52e4d90…`). Study code: `src/ocm/evaluation/m21_surprise_revival.py` (pre-registration in the module docstring; guards evaluated before the verdict). Run off-Mac (billy-old, exact ℚ, 11 s).

| arm | FOUND_BY_NAVIGATION | EXTRACT misses | translator invariance | mean \|G_Q\| |
|---|---|---|---|---|
| UNIFORM (frozen contract §6) — baseline reproduced exactly | 38/50 | 12 | 50/50 | 9.2 |
| PROPAGATED (`ocm.kso.surprise`) | **47/50** | **3** | 50/50 | 11.2 |

Guards (all held): baseline reproduced (same 12 instances, same 38); no live request atom that UNIFORM surfaced is lost; translator invariance kept; two-direction hub theorem KS-T06b holds under both models. STORE_EXACT is unaffected by construction (the decision is composed from labels).

Attribution of the improvement: EXTRACT (background model). The receipt's own lever — a seed-count-conditioned background — is a no-op by linearity of the fixed point in the seed (`surprise.check_seed_count_lemma`, exact); the effective lever is removing the background's self-teleport term (restart mass is the prior, not reaction).

Remaining 3 misses, all family `X1-I_LOCAL_COMPAT_GLOBAL_OBSTRUCTION`, all `piece:cN` atoms (derived-claim constraints fed by a SUPPORT edge from their claim *and* a DEPENDENCE edge from the goal). Under the query they receive one structural source; under the background two. Next attributed lever (not tried here, per pre-registration): per-source propagated comparison (fan-out-aware normalisation of the background by inbound structural share). Filed in `docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md`.

Authority: a design-choice comparison of two registered surprise models under identical closure, budget and labels on the development split; the default model is **not** switched by this study — switching requires the M2 receipt to be re-run with the model as a declared parameter and the protected split still `NOT_RUN`. No novelty claim: the PROPAGATED model is the standard contribution-vector reading of personalised PageRank with the teleport term removed.
