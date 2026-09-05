# M10 — scientific/data/formal reasoning agent: study report

Date 2026-09-05. Terminal: **MIXED, claim by claim** — the lifecycle capabilities below are
established on OCM-authored oracle worlds with registered parents built here; every external
benchmark and any frontier target is `CANNOT_CHECK`. No `M10_SCIENTIFIC_AGENT_SUPPORTED` claim is
made (no pre-registered residual under matched conditions on an external task). No novelty claim.

## 1. Objects (issue #12 §1–§3, §10, §12–§14)

`ScientificTask` (question, estimand, prior evidence, measurement model, experiments with cost
and risk, budget, known confounders, hidden checker-only oracle, required reporting);
`Observation` with provenance, conditions, error model, replicate identity, pipeline version,
scope, confounders and warrant — corroboration counts **distinct sources** (replicates never
corroborate); `Hypothesis` layers (symbolic / statistical / causal / simulation / program / formal)
with predictions, scope, assumptions, support and counter-evidence; `Conclusion` with the
identification assumptions a causal claim needs; the proof-kernel boundary with the kernel warrant
and the formalisation-correspondence warrant kept apart; the science ledger (derived conclusions
on the M2 runtime); the science role map for M9 transfer; the communication gate.

## 2. Results (`research/ocm-m10/M10_SCIENCE_EVAL_V1.json`)

| capability | result | denominator |
|---|---|---|
| causal identification | identified estimators (back-door, interventional) within 0.25 of the oracle effect | 10/10 over five SCM worlds |
| naive regression on confounded worlds | biased by ≥ 0.3 (1.28 vs 0.5; 0.52 vs 0.0) | 2/2 |
| collider adjustment | flagged non-identified; induces −0.49 where the oracle is 0 | 1 world |
| causal claims without registered assumptions | 0 allowed | gate |
| experiment selection (OCM value policy) | isolates the true effect in 1 experiment, cost 0.4, risk 0.1 | 4/4 truths |
| entropy (cost/risk-blind) | 4/4, same on this suite | 4/4 |
| random | 2/4, 5.5 experiments, risk 0.78 | 4 |
| greedy confirmation (hostile) | 0/4 — never isolates, 10 experiments | 4 |
| pre-registered analysis (exact permutation) | false positives 0 on null datasets; 6/6 effect datasets significant; 1 analysis per dataset | 6 null / 6 effect |
| p-hacking hostile | 12 analyses tried per null dataset (0 false positives on these small nulls; the search count is the finding) | 6 null |
| proof kernel (propositional, exact) | 8/8 correct verdicts; unparsable → CANNOT_CHECK; Lean 4 → CANNOT_CHECK; a mistranslation passes the kernel with a **dead** correspondence warrant | 8 + 3 |
| FAIL-means-false hostile | fires on 3/3 FAILs regardless of kernel completeness | 3 |
| retraction | retracting one observation kills exactly the conclusion resting on it (1/3), unrelated 2/2 intact, replacement live with lineage, old stays dead, replay reproduces | 3 conclusions |
| cross-field transfer (M9 → science) | full mapping TRANSFER with ⊗ warrant; missing report binding ADAPTER_REQUIRED; work verifier as validation REFUSE_TRANSFER | 3 cells |
| communication gate | 3 committed, 1 downgraded ("causes" → "suggests" on association), 2 refused (no marker; elegant "proves" over CANNOT_CHECK) | 6 sentences |

## 3. Hostiles (planted, detected)

Replicates as corroboration; correlation as causation; confirmation-bias experiment chooser;
p-hacking search; FAIL read as falsity; mistranslated formal statement accepted for the informal
claim; lookalike work verifier as statistical validation; fluent overclaim; CANNOT_CHECK hidden by
wording.

## 4. CANNOT_CHECK

SciCode / SciCode-Verified (no pinned audited release; no network), ResearchGym, LifeSciBench full
(`CANNOT_CHECK_LIFESCIBENCH_FULL`), miniF2F / Lean 4 (no toolchain), any frontier target
(`CANNOT_CHECK_FRONTIER_TARGET`); frontier scientific agents and Bayesian experimental-design
packages as comparators (not built here — the entropy policy is the only design parent run).

## 5. Backlog

Bayesian experimental-design parent with priors over effect sizes; Lean 4 kernel adapter with a
formalisation-correspondence review protocol; audited SciCode subset as a scientific-coding
lifecycle (units/invariants/limits checks) once a release is pinned; larger causal worlds with
transport across environments; a pre-registered matched study before any SUPPORTED claim; theory
batch 4 D3 (graded operator warrant) for probabilistic hypotheses.
