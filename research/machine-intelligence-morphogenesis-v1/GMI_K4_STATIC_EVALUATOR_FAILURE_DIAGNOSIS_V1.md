# GMI K4 static-evaluator failure diagnosis v1

Status: **PRESERVED RED / CAUSAL DIAGNOSIS / OLD PROTOCOL RETIRED FOR KNOWN-FORM CLOSURE**

Date: 2026-09-12.

Evidence being diagnosed:

- corrected DG-10 resource probe panel: 39/39 variable traces, 22/22 state-law signatures and 21/21 serve-law signatures separated;
- full 264-cell development sweep;
- 159 `THEORY_RED` cells with a cheaper developed non-target realization;
- 69 `THEORY_RED_NULL_DOMINATES` cells;
- 36 inconclusive cells with no admissible target witness;
- 0/264 target-vector matches.

Nothing in this document converts any of those outcomes to GREEN.

## 1. What the old experiment actually falsified

It falsified the proposition:

> Given the old abstract obligation rubric, the old ten-axis vector and the registered lifecycle scalarization, minimizing the registered burden recovers the frozen historical-family property vector.

At development scope, that proposition is false.

```text
OLD_K4_STATIC_PROPERTY_FRONTIER = RED
```

The failure is broad across families, grammars and resource cells, so it is not responsibly explained as a single unlucky seed.

## 2. Three distinct failure classes

### F1 — target-information provenance absent from the property vector

The old evaluator can grant semantic adequacy to a fixed realization based on capability motifs without specifying how protected target-specific information entered the realization.

This creates two conflations:

```text
fixed GENERAL algorithm receiving the full instance in Q
!=
fixed TARGET-SPECIFIC answer/program that somehow already knows W
```

The first may be legitimate; the second must either fail on fresh worlds or pay target-information acquisition burden.

The missing coordinate is `target_information_source`, formalized in `GMI_TARGET_INFORMATION_ACQUISITION_THEOREM_V1.md`.

### F2 — static capability rubric is weaker than task execution

The old `semantic_score` evaluates operational motifs. It does not fit/develop a realization on a fresh post-freeze target and then test it on held-out behavior.

Therefore two candidates can both receive high semantic adequacy even when one would fail to acquire the actual target from legal observations.

The successor must execute concrete tasks.

### F3 — old ten-axis vector is not frontier-complete under the old meter

Even after excluding the null-dominated cells, 159 cells find a cheaper admissible non-target frontier.

Thus the old property vector is not a sufficient statistic for resource-frontier identity at that scope.

This remains a real negative result even after F1/F2 are repaired. The successor adds the smallest presently identified missing causal coordinate and must be willing to discover further missing coordinates prospectively.

## 3. Why null dominance is scientifically useful

The 69 null-dominated cells are not an inconvenience to remove. They prove that the corresponding registered obligation did not force development strongly enough under the old semantics.

A correct successor does **not** ban fixed realizations. Instead it:

1. draws the protected world after pre-world machine freeze;
2. denies a fixed answer access to world-specific information it was not legally given;
3. allows fixed general algorithms when query input supplies the problem instance;
4. charges any post-draw hard-coding as development/external intervention.

That preserves the null as a meaningful parent.

## 4. Why the protected old K4 run should not proceed as a closure attempt

The full development sweep has already shown that the registered static prediction is not viable. Spending protected compute to seek a GREEN under the same semantics would have little information value and risks creating pressure to tune against a known failure.

A protected replication of the old RED can be run for audit if desired, but it cannot establish known-form derivation completeness.

The high-value protected experiment is the **fresh developmental-acquisition successor**, frozen before its world draws.

## 5. Required theory change is minimal

Do not append architecture names or hand-coded exceptions.

Add:

```text
target_information_source
```

and replace static semantic adequacy with actual post-freeze development/query/authority execution.

If that successor still recovers a cheaper non-target frontier, preserve the RED and open the next smallest missing causal atom.

## 6. Consequences for old terminals

```text
K4_PROPERTY_PREDICTION_GREEN_AT_OLD_REGISTERED_SCOPE = FALSE
OLD_K4_STATIC_SEMANTIC_EVALUATOR_VALID_FOR_KNOWN_FORM_CLOSURE = FALSE
```

The following remain unchanged:

```text
KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE = FALSE
NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE = FALSE
```

## 7. Successor target

The successor question is:

> With the generic mechanism frozen before the protected world, and with target-specific information restricted to declared development/query/authority channels, which mechanism minimizes lifecycle burden while meeting held-out quality and retention requirements?

That is a legitimate zero-prior morphology question. The old static capability-rubric question is retired for this purpose.
