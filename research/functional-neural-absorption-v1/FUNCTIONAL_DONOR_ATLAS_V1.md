# FNA-0 functional donor atlas v1

**Evidence class E0 / L0.** Donor survey. No experiment, no terminal, no capability claim.
Sources were read at **abstract level** via topical search; full texts were not read, and
`SOURCE_LEDGER.json` marks every row accordingly.

## The Phase B finding: #214's own multi-head row assigns the wrong function

#214 §3 tabulates:

| feature | functional obligation | candidate OCM form |
|---|---|---|
| multi-head attention | *multiple concurrent relevance relations* | *semantic / causal / temporal / failure / provenance / goal heads* |

The literature does not support that reading of what heads are *for*.

- **Multi-Head Attention as Ensemble Nadaraya-Watson Estimation** (2605.20271) develops MHA as
  an **ensemble of kernel-regression estimators**, building on an algebraic identity with
  single-head softmax. The stated role of multiple heads is **variance reduction through
  decorrelation**, with an optimal head diversity.
- **Identifying and Evaluating Inactive Heads in Pretrained LLMs** (2504.03889) reports heads
  whose learned behaviour is inactive. If each head were a distinct semantic relation, inactive
  heads would be missing relations rather than redundant estimators.
- **Multi-Head Attention Is a Multi-Player Game** (2602.00861) likewise frames heads as competing
  and coordinating estimators, not as a typed relation vocabulary.

So the obligation multi-head discharges is **statistical**: it averages decorrelated noisy
estimators to reduce the variance of one aggregation. It is not a mechanism for representing
several kinds of relation.

**This matters directly, and it is the reason FNA-1's target changed.** OCM's retrieval is
*exact*. An exact gated closure has **no estimator variance to reduce**. If multi-head's
function is variance reduction, then in an exact system that function has **no obligation to
discharge at all** — it is not that OCM needs a substitute, it is that the requirement is absent.

The typed-channel mechanism #214 proposes is real and useful, but it belongs to a **different
parent**: heterogeneous information networks and typed/metapath retrieval (2605.30966 typed
claim networks; 2510.15552 multi-view KG retrieval). Attributing it to multi-head credits the
neural donor with a function the classical graph literature already owns.

## Parent ownership, by function

| neural function | obligation, as the literature states it | strongest non-neural parent | ownership |
|---|---|---|---|
| self-attention | query-conditioned content-addressed aggregation; formally test-time kernel regression / Nadaraya-Watson (2601.22766, 2501.12352) and associative-memory retrieval (2505.19488) | inverted index with selectivity anchor; kernel/kNN regression; associative memory | **PARENT_OWNS_IT** — and `runtime/operator_index.py` on main is already an instance |
| multi-head | ensemble variance reduction over decorrelated estimators (2605.20271) | ensemble/bagging of estimators | **NO_OBLIGATION_IN_AN_EXACT_SYSTEM** |
| "typed channels" (mis-attributed to multi-head) | representing several distinct relation kinds | heterogeneous information networks, metapath retrieval, typed claim networks | **PARENT_OWNS_IT** (graph IR, not Transformers) |
| neural ranking | relevance scoring | cross-encoders shown to implement a semantic variant of **BM25** (2502.04645) | **PARENT_OWNS_IT** |
| KV cache | reuse of prior context state | indexed episodic store; `ExtractionIndex` object-bound preparation on main | **PARENT_OWNS_IT** |
| VSA/HDC proposal | approximate similarity for candidate generation | kernel approximation via Nyström (2608.06860) | **ADAPT** — absent on main (R6) |
| kNN external memory | nonparametric recall beside a parametric core | kNN-LM (1911.00172) | **ADAPT** — absent on main (R3) |

## Changed-vocabulary second pass (hostile, as §FNA-0 requires)

Searched under the non-neural names so ordinary parents receive first refusal rather than being
reached only through Transformer vocabulary: *associative lookup*, *kernel regression*,
*nonparametric conditional aggregation*, *inverted index*, *term-at-a-time / WAND*, *typed
edges / metapath*, *graph diffusion*, *hyperdimensional computing*. Every one of the seven
functions above resolved to a named non-neural parent. **No function in this pass required a
new OCM-specific mechanism.**

## Saturation status — honest

**NOT saturated.** This is one topical pass at abstract level. Specifically not yet covered:
CTW/PPM and grammar induction (FNA-3), library learning and CEGIS (FNA-4), blackboard/production
architectures (FNA-6). Those belong to later work packages and are not claimed here. Saturation
is not asserted from citation count.

## What FNA-1 should therefore test

Not "can a non-neural mechanism do query-conditioned retrieval" — main already does, exactly.
The two questions this atlas leaves open and testable on current main are:

1. **Can typed multi-channel retrieval add reach that the existing undifferentiated exact
   closure misses?** (The parent is heterogeneous-graph metapath retrieval, not multi-head.)
2. **If it cannot add reach, can it reduce work — and under what condition does channel
   selection become capability-relevant rather than merely cheaper?**
