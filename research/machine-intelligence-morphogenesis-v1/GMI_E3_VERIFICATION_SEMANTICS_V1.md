# GMI E3 verification semantics v1

Status: **frozen common epistemic interface for the first real-domain pair**.

Refs #369 #46 #208 #233 #377.

GMI-v1 uses one external verifier/evidence interface across domains, but it does **not** claim that all verification regimes prove the same thing.

The rule is:

> same theory field, domain-specific evidence semantics, explicit claim ceiling.

---

# 1. Common verifier object

For task contract `tau`, candidate result `y`, and external constitution `C`, define a verifier/evidence process

\[
V(y,\tau;C)\to r_V
\]

where the receipt `r_V` contains at least:

```text
verifier identity/version
task/specification identity
candidate digest
admissibility terminal
evidence class
assumptions/allowed axioms/tools
known verifier limitations
resource receipts
```

The verifier is outside the learner's unilateral authority.

The machine may propose, search, train and predict. It may not redefine the criterion by which its protected success is accepted.

---

# 2. Evidence classes

These labels are **not a universal total order of truth**. They identify different external contracts.

## `FORMAL_KERNEL_VERIFIED`

Meaning:

- a formal statement/specification has been fixed;
- the candidate derivation is accepted by a pinned formal kernel/checker;
- only registered axioms/imports are permitted.

Primary E3 example: Lean 4 proof accepted by the pinned Lean kernel.

Does **not** automatically establish:

```text
faithful translation of an informal theorem
novelty of the mathematical result
absence of inconsistent external assumptions outside the checked environment
```

## `EXECUTION_TEST_VERIFIED`

Meaning:

- candidate artifact executes/builds in the frozen environment;
- it satisfies the registered executable test/oracle suite.

Primary E3 example: software patch/build accepted by public + protected regression tests.

Claim ceiling depends on test adequacy. A finite test suite generally establishes:

```text
passes this registered suite
```

not:

```text
implements the full intended specification for all inputs
```

unless the verifier is known complete for the declared fragment.

## `FORMAL_SPEC_VERIFIED`

Reserved for code/tasks where an executable artifact is checked against a formal specification with a sound proof/decision procedure.

This can be stronger than ordinary testing but inherits the specification-correspondence problem.

## `EMPIRICALLY_SUPPORTED`

Meaning:

- conclusion follows from a frozen empirical/statistical protocol;
- evidence, uncertainty and assumptions are reported.

This will matter later for science but is not the primary math/code E3 regime.

## `EXTERNAL_REVIEW_SUPPORTED`

Independent human/expert review or rubric evidence. This may be necessary for semantic correspondence but is not silently promoted to formal proof.

## `PARTIAL_CERTIFICATE`

A machine-checkable or externally inspectable partial result exists even though the full task contract was not discharged.

Examples:

```text
Lean proves a nontrivial registered lemma but not the target theorem
code patch fixes one registered failing behavior but full regression contract remains unsatisfied
counterexample/refutation witness for a subclaim
```

---

# 3. Mathematics verification is conjunctive

For a natural-language theorem task, a valid `KERNEL_VERIFIED` user-facing result requires two distinct obligations:

```text
A. STATEMENT_CORRESPONDENCE
   the formal Lean proposition faithfully expresses the registered intended theorem

B. PROOF_VALIDITY
   Lean kernel accepts the proof of that formal proposition under allowed imports/axioms
```

Therefore:

\[
MathSuccess = Correspondence \land KernelAccept.
\]

The two receipts must be stored separately.

A foundation model may propose the formalization, but it cannot self-certify correspondence unless the protocol explicitly defines that lower evidence class.

Required hard failures/terminals include:

```text
STATEMENT_MISMATCH
FORBIDDEN_AXIOM_OR_SORRY
PROOF_DOES_NOT_COMPILE
PROTECTED_PROOF_LEAKAGE
KERNEL_ENVIRONMENT_MISMATCH
CANNOT_CHECK_CORRESPONDENCE
```

A failed proof search does **not** imply the theorem is false.

---

# 4. Coding verification is test-strength relative

For software task `tau`, define:

```text
build/import gate
public tests visible to all arms
protected tests/evaluator hidden from solving arms
optional static/formal checks
regression/invariant checks
```

A protected success receipt binds the exact environment and test identities.

Required distinctions:

```text
COMPILES_ONLY
PUBLIC_TESTS_PASS
PROTECTED_TESTS_PASS
REGRESSION_SUITE_PASS
FORMAL_SPEC_PASS
```

Do not collapse them into one Boolean before the claim ceiling is assigned.

If a benchmark test is flawed or underspecified, use:

```text
ASSAY_DEFECT
CANNOT_CHECK_TEST_VALIDITY
```

rather than silently scoring the model.

Public benchmark audits in 2026 reinforce this requirement: SWE-bench Verified has documented contamination/flawed-test problems, and later audits also report substantial SWE-Bench Pro task defects. Confirmatory GMI coding evidence should therefore prefer protected/private audited tasks.

---

# 5. Verifier-strength metadata

Every verifier contract should declare:

```text
soundness_status        known / conditional / empirical / unknown
completeness_status     known / conditional / empirical / unknown
specification_scope
correspondence_status
contamination_risk
hidden_test_oracle_policy
version/hash/pin
```

This metadata determines the strongest semantic claim the episode may emit.

It is **not** used to invent a universal scalar weighting between formal proof and empirical evidence.

---

# 6. Verification cost is part of intelligence burden

A system that obtains the same verified capability only by making vastly more checker/test calls occupies a different resource point.

Charge at least:

```text
kernel/checker calls
compile/build work
test execution
proof-state environment calls
protected evaluator calls
statement/spec correspondence review
whole-library/index maintenance needed for checking
```

Verification cannot be treated as free merely because it is external.

---

# 7. Verifier access must be matched

Matched arms receive the same protected feedback bandwidth.

Examples of invalid comparisons:

```text
OCM sees individual hidden-test failures while parent gets only final score
parent can query Lean errors indefinitely while OCM is checker-budgeted
one arm receives a theorem's reference proof or gold patch indirectly through the evaluator
```

If one treatment deliberately purchases extra information, charge it and classify it as an intervention/tool difference rather than hidden intelligence.

---

# 8. Semantic failure versus search failure

The theory must distinguish:

```text
SEARCH_FAILURE
  valid target/spec, no admissible candidate found within budget

SEMANTIC_MISMATCH
  candidate solved a different formal/program specification

VERIFIER_REJECTION
  candidate reached verifier and failed

VERIFIER_INSUFFICIENCY
  registered verifier cannot justify the desired claim

ASSAY_DEFECT
  evaluator/task is invalid for the intended claim
```

This distinction is required for meaningful developmental learning. A system should not learn a search heuristic from a failure that was actually a broken test or mistranslated theorem.

---

# 9. Math/code commonality

The two E3 domains use the same abstract sequence:

```text
human/task input
-> TaskContract
-> semantic target/specification
-> cognition/search/tool actions
-> candidate artifact
-> external verifier receipt
-> resource/capability episode
-> governed learning/update
```

Their verifier semantics differ:

```text
math:  formal statement correspondence + Lean kernel proof
code:  executable specification/test contract + execution/checking
```

GMI-v1 succeeds at the semantic-transfer level only if no new definition of state, morphology, burden, K1/K2 or generality is required to accommodate this difference.

---

# 10. Required E3 terminals

Mathematics:

```text
FORMAL_KERNEL_VERIFIED
PARTIAL_WITH_FORMAL_CERTIFICATE
STATEMENT_MISMATCH
REFUTED_WITH_WITNESS
UNKNOWN
CANNOT_CHECK_<reason>
```

Coding:

```text
EXECUTION_TEST_VERIFIED
FORMAL_SPEC_VERIFIED
PARTIAL_WITH_EXECUTABLE_CERTIFICATE
REGRESSION_FAILURE
ASSAY_DEFECT
UNKNOWN
CANNOT_CHECK_<reason>
```

Cross-domain theory:

```text
GMI_VERIFICATION_INTERFACE_TRANSFER_SUPPORTED
GMI_VERIFICATION_INTERFACE_REQUIRES_REVISION
VERIFIER_INSUFFICIENT_FOR_CLAIM
```

No positive domain terminal upgrades GMI K1/K2 without the matched developmental controls required by `GMI_E3_REAL_COGNITION_EPISODE_V1`.
