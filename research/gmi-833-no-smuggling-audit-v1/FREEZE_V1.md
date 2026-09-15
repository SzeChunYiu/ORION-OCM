# GMI #833 no-smuggling audit — freeze v1

**Child issue:** #855  
**Parent:** #833 Section D  
**Frozen from main:** `af467254206fa76ec3eab31078a420f1ad4d7cea`  
**Claim ceiling:** `GMI_NO_SMUGGLING_AUDIT_TOOLING_VALIDATED_AT_REGISTERED_FINITE_FIXTURE_SCOPE`

This file is the pre-implementation scientific custody record. Executor code, fixtures, tests, expected receipt, reconciliation spec, and workflow must postdate this freeze.

## Exact target rows

This tranche may reconcile only these six #833 rows:

1. `Build an automated architecture-name/macros leakage detector.`
2. `Build a semantic leakage audit: detect architecture-specific operators disguised under neutral names.`
3. `Build a cost-prior audit.`
4. `Build a search-prior audit.`
5. `Build an evaluation-prior audit.`
6. `Build an ecology-selection-bias audit.`

It may not reconcile the later execution requirements for matched grammar twins, alternate encodings, alternate search algorithms, or alternate scalarizations across the corpus.

## Scientific meaning

The object under test is a machine-readable `PriorAuditRecord`. A clean result means only that all six registered finite-scope audit predicates were evaluable and returned clean on the supplied record. It is not a proof of ontological neutrality, architecture-prior freedom, or real-world representativeness.

## Frozen audit vocabulary

Terminal families:

- `LEXICAL_LEAKAGE`
- `SEMANTIC_MACRO_LEAKAGE`
- `COST_PRIOR_SENSITIVE`
- `SEARCH_PRIOR_SENSITIVE`
- `EVALUATION_PRIOR_SENSITIVE`
- `ECOLOGY_SELECTION_BIAS`
- `CLEAN_AT_REGISTERED_AUDIT_SCOPE`
- `CANNOT_AUDIT_<MISSING_DISCLOSURE>`

A missing required disclosure fails closed and cannot produce CLEAN.

## A1 — lexical leakage

Search-visible identifiers are normalized across case, punctuation, snake/kebab/camel boundaries and checked against a versioned denylist of named architectures, aliases, target-family IDs, and forbidden macros.

Frozen hostiles include at least:

- `transformer`
- `self_attention`
- `Conv2D`
- `lstm_gate`
- `rag_retriever`
- mixed-case and punctuation variants.

Lexical cleanliness is a screen only and cannot discharge A2.

## A2 — semantic macro leakage

Each search-visible primitive exposes a finite semantic signature with at least:

- arity and type signature;
- state-access mode;
- locality/globality;
- addressability;
- content-dependent routing;
- parameter sharing;
- recurrence;
- stochasticity;
- verifier access;
- resource/asymptotic class.

A target fingerprint is a conjunction of required semantic features. A primitive that satisfies a registered target fingerprint atomically is flagged even if its identifier is neutral.

Frozen hostiles:

- rename query/key/content-routing weighted aggregation to `mix`: still flags;
- rename translation-shared local neighborhood aggregation to `local_apply`: still flags;
- decomposed arithmetic/index/read/write primitives that individually do not satisfy a target fingerprint remain admissible.

Scope is the registered finite fingerprint library only.

## A3 — cost-prior audit

The raw lifecycle resource vector remains primary. The audit rejects or flags:

- negative scored coordinates;
- undeclared scored coordinates;
- target-dependent bonus/penalty terms;
- zero-cost privileged operators when they structurally determine the advertised winner;
- a universal-winner claim when admissible positive scalarizations reverse the order of incomparable candidates.

Frozen hostile: two Pareto-incomparable candidates reverse ranking under two positive weight vectors.

## A4 — search-prior audit

The audit records enumeration/order, pruning, tie rules, budget/stopping, randomness/seeds, and search strategy identity.

On a shared finite candidate/objective space, if two admissible search strategies under the same objective and budget return different phenotypes solely because of search ordering/trajectory, terminal is `SEARCH_PRIOR_SENSITIVE` unless an exhaustive/minimality certificate removes the dependence.

Frozen hostile: budget-one search over tied candidates returns different winners under forward vs reverse enumeration.

## A5 — evaluation-prior audit

Evaluation predicates may use protected task/resource outcomes but not architecture/family identifiers where blindness is required.

The audit flags:

- target-ID bonus in the evaluator;
- thresholds not frozen before outcomes;
- post-hoc target-family classification feeding back into the scientific score;
- registered metric alternatives that reverse the ranking while a universal ranking is claimed.

Frozen hostile: an evaluator adds one point solely for a target-family ID.

## A6 — ecology-selection-bias audit

Required disclosures:

- finite sampling frame or explicit `UNKNOWN_FRAME`;
- inclusion/exclusion rules;
- sampled ecology IDs;
- strata/target-favoring labels where known;
- matched-negative/control registration.

If the finite frame is known, report sample-vs-frame target-favoring prevalence exactly. A positive-only sample from a balanced frame is flagged. If the frame is unknown, the audit must preserve `CANNOT_AUDIT_FRAME_REPRESENTATIVENESS` rather than fabricate representativeness.

## Cross-audit CLEAN rule

`CLEAN_AT_REGISTERED_AUDIT_SCOPE` is permitted iff:

1. all required disclosure blocks are present;
2. A1 has no lexical leakage;
3. A2 has no registered semantic fingerprint match;
4. A3 has no registered cost-prior sensitivity or malformed costs;
5. A4 has no registered search-prior sensitivity;
6. A5 has no registered evaluation-prior sensitivity;
7. A6 has no registered ecology selection bias and the declared frame status is auditable for the claim being made.

Otherwise the global result is a structured union of sub-audit terminals, never a coerced CLEAN.

## Exact evidence commitments

The post-freeze package must include:

- a pure-Python finite auditor with no network/runtime architecture dependencies;
- schema/record validation;
- exact rational arithmetic for cost/ecology quantities;
- positive and negative fixtures for all six audits;
- at least two search strategies on the same finite objective/budget;
- at least two positive scalarizations on the same Pareto-incomparable candidates;
- semantic-renaming hostile defeating lexical-only screening;
- missing-disclosure fail-closed tests;
- deterministic normal and `python -O` tests;
- byte-stable machine-readable result receipt;
- PR check-only / main-push apply-only reconciliation for the six exact rows.

## Parent ownership / non-novel mathematics

This tranche treats the following as parent concepts rather than novel mathematics:

- inductive bias / representation bias;
- Pareto order and scalarization dependence;
- algorithm/search bias under finite budgets;
- measurement/evaluation construct validity;
- sampling/selection bias and frame mismatch.

Its residual contribution is the typed GMI no-smuggling audit contract plus executable fail-closed integration at the registered finite fixture scope.

## Forbidden promotions

This tranche alone cannot support:

- `ENTIRE_GMI_CORPUS_PRIOR_FREE`
- `ALL_ARCHITECTURE_LEAKAGE_DETECTED`
- `SEMANTIC_NEUTRALITY_PROVED`
- `ALL_COST_MODELS_UNBIASED`
- `ALL_SEARCH_ALGORITHMS_EQUIVALENT`
- `ECOLOGY_REPRESENTATIVE_REAL_WORLD`
- `P3_RECOVERY_COMPLETE`
- `COMPLETE_GMI`
