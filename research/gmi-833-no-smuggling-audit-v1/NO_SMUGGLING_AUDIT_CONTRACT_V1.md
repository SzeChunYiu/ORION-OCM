# No-smuggling audit contract — v1

**Issue:** #855, child of #833 Section D  
**Freeze:** `research/gmi-833-no-smuggling-audit-v1/FREEZE_V1.md`  
**Claim ceiling:** `GMI_NO_SMUGGLING_AUDIT_TOOLING_VALIDATED_AT_REGISTERED_FINITE_FIXTURE_SCOPE`

This tranche turns six kinds of derivation bias into explicit, machine-auditable disclosures and fail-closed terminals. It does not claim that a finite fingerprint library detects every semantic prior or that passing the auditor proves architecture-prior freedom.

## Expert review lanes

The tranche was reviewed as four distinct problems:

1. **Formal-methods lane:** typed disclosure contracts, total/fail-closed terminals, deterministic receipts, and exact reconciliation scope.
2. **Learning/search-bias lane:** lexical/semantic inductive bias and search-procedure dependence.
3. **Optimization/resource lane:** raw Pareto vectors, scalarization sensitivity, and privileged zero-cost operations.
4. **Hostile-review lane:** neutral renaming, missing disclosures, target-ID scoring, search-order flips, and ecology frame mismatch.

## Parent theory ownership

The mathematics and methodological ideas below are parent concepts, not GMI inventions:

- inductive bias: T. M. Mitchell, *The Need for Biases in Learning Generalizations* (1980);
- search/optimization dependence on problem class: D. H. Wolpert and W. G. Macready, *No Free Lunch Theorems for Optimization*, IEEE TEC 1(1), 1997, DOI 10.1109/4235.585893;
- multiobjective/Pareto scalarization: weighted-sum methods select according to registered weights and can reverse incomparable alternatives; GMI keeps raw vectors primary;
- construct/evaluation validity: S. Messick, *Validity of psychological assessment*, American Psychologist 50(9), 1995, DOI 10.1037/0003-066X.50.9.741;
- sample-selection bias: J. J. Heckman, *Sample Selection Bias as a Specification Error*, Econometrica 47(1), 1979.

The residual contribution of #855 is the typed GMI integration contract, hostile finite fixtures, deterministic receipt, and issue-governance gate.

---

## A1 — lexical leakage screen

Let `N(s)` normalize an identifier by splitting camel case, punctuation, snake/kebab separators, lower-casing tokens, and concatenating them. For registered denylist compact forms `D`, identifier `s` leaks lexically iff some `d in D` occurs in `N(s)`.

This is deliberately one-sided: a hit is evidence of a visible forbidden name/macro; no hit is **not** proof of semantic neutrality.

Exact hostiles include `transformer`, `self_attention`, `SelfAttention`, `Conv2D`, `lstm_gate`, `rag_retriever`, and `RAG-Retriever`.

---

## A2 — semantic macro audit

A search-visible primitive is assigned a finite semantic signature

`Sigma(p)=(arity,types,state_access,locality,addressability,content_routing,sharing,recurrence,stochasticity,verifier_access,resource_class)`.

A registered target fingerprint is a partial predicate on these coordinates. If one atomic primitive satisfies a target fingerprint, the auditor emits `SEMANTIC_MACRO_LEAKAGE` regardless of the primitive's spelling.

### Renaming hostile

A primitive named `mix` is lexically clean but has `global` locality, content-dependent routing, addressability and `O(n^2)` resource class. It therefore matches the registered content-routing weighted-aggregation fingerprint and is rejected semantically.

Likewise `local_apply` is lexically clean but matches a translation-shared local-kernel fingerprint through neighborhood locality plus parameter sharing.

### Negative control

Decomposed arithmetic/index/read/write primitives remain clean when no individual primitive atomically satisfies a target-family fingerprint. This prevents the semantic screen from equating generic computational expressivity with architecture smuggling.

Scope boundary: only the finite registered fingerprint library is checked; undiscovered semantic priors remain possible.

---

## A3 — cost-prior audit

Raw resource vectors remain primary. Let candidate `m` have nonnegative vector `r(m)` and a positive scalarization `w`. The scalar score is `w · r(m)`.

### Pareto preservation boundary

If `r(a) <= r(b)` coordinatewise with a strict inequality somewhere, every strictly positive `w` ranks `a` strictly below `b`. For incomparable vectors, positive scalarizations can reverse the winner.

Exact hostile:

- `compute_light=(1,4)`;
- `memory_light=(4,1)`;
- `w_compute=(4,1)` selects `compute_light`;
- `w_memory=(1,4)` selects `memory_light`.

Thus a universal winner claim is invalid when only price-conditional selection is supported.

The auditor also rejects negative/malformed resource coordinates, target-specific score adjustments, nonpositive scalar weights, and target-privileged operations assigned zero cost.

---

## A4 — search-prior audit

A finite search disclosure registers the candidate objective values, search strategies/order, budget, tie rule, pruning, stopping, randomness/seeds, and any exhaustive certificate.

Search-prior sensitivity is operationally witnessed when two registered strategies on the **same objective and budget** return different winners and no exhaustive/minimality certificate removes order/trajectory dependence.

Exact hostile: two tied candidates `a,b`, budget one, forward order returns `a`, reverse order returns `b`; terminal `SEARCH_PRIOR_SENSITIVE`.

Negative control: exhaustive search of a finite space with a unique optimum returns the same winner under forward/reverse enumeration.

---

## A5 — evaluation-prior audit

A protected evaluation score must depend on declared task/resource outcomes, not on the target architecture/family identifier when blindness is required.

The auditor emits `EVALUATION_PRIOR_SENSITIVE` for:

- architecture IDs entering the score;
- target-ID bonus/penalty;
- thresholds set after outcome observation;
- post-hoc classifier feedback into the scientific score;
- metric winner reversal while a universal ranking is claimed.

Exact hostile: adding one score point solely because a candidate carries the target-family identifier fails, independent of its task performance.

---

## A6 — ecology-selection-bias audit

For a known finite ecology frame `F` and sampled subset `S`, the auditor computes exact target-favoring prevalence

`p_F = |{e in F: favor(e)}|/|F|`, `p_S = |{e in S: favor(e)}|/|S|`.

A one-sided sample from a mixed frame, missing matched negative when representativeness is claimed, or `p_S != p_F` under a representativeness claim emits `ECOLOGY_SELECTION_BIAS`.

Exact hostile: frame prevalence `1/2`, sample prevalence `1`, terminal `ECOLOGY_SELECTION_BIAS`.

If the frame is unknown, the auditor emits `CANNOT_AUDIT_FRAME_REPRESENTATIVENESS` for claims requiring representativeness rather than fabricating a population reference.

---

## Cross-audit theorem — CLEAN is conjunctive and scoped

For the registered record, `CLEAN_AT_REGISTERED_AUDIT_SCOPE` is emitted iff all six sub-audits are evaluable and each emits CLEAN. A missing disclosure returns a `CANNOT_AUDIT_*` terminal and the global object returns `AUDIT_NOT_CLEAN`.

Therefore absence of evidence is never converted into evidence of absence by the auditor.

## Exact hostile certificate

The deterministic receipt requires all of the following:

- seven lexical variants flag;
- semantic renaming of both registered family fingerprints flags while lexical screening remains clean;
- generic decomposed primitives remain clean;
- Pareto-incomparable candidates reverse under two positive scalarizations;
- a privileged zero-cost operator flags;
- search-order hostile flags;
- target-ID evaluation and metric-reversal hostiles flag;
- positive-only ecology sample from a balanced frame flags;
- unknown sampling frame abstains;
- each of six missing disclosures fails closed;
- clean fixture passes all six audits;
- no floating-point quantity appears in the exact receipt.

The same result must reproduce under normal Python and `python -O` byte-for-byte.

## Falsifiers

This tranche is falsified at its claimed scope by any of:

- a registered lexical variant escaping the denylist normalizer;
- a registered semantic fingerprint match being declared clean after neutral renaming;
- winner reversal not being surfaced under the registered scalarizations/search/evaluation metrics;
- missing disclosure producing CLEAN;
- known-frame one-sided ecology selection producing a general clean result;
- normal and optimized executions disagreeing;
- receipt regeneration changing bytes without an explicit new version.

## Forbidden extrapolations

Passing the auditor does not license `ENTIRE_GMI_CORPUS_PRIOR_FREE`, `ALL_ARCHITECTURE_LEAKAGE_DETECTED`, `SEMANTIC_NEUTRALITY_PROVED`, `ALL_COST_MODELS_UNBIASED`, `ALL_SEARCH_ALGORITHMS_EQUIVALENT`, `ECOLOGY_REPRESENTATIVE_REAL_WORLD`, `P3_RECOVERY_COMPLETE`, or `COMPLETE_GMI`.
