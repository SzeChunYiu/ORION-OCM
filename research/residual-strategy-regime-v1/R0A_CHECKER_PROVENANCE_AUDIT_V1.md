# R0A checker provenance audit V1

**Status:** source-custodied negative / constructive identity collision / no production change / no ML.

R0A originally looked like a small exact optimization: stop checking after the
first passing candidate.  The current suffix-elision audit already showed why
that is not valid under the unrestricted host-callback contract: a later checker
may mutate runtime state, revoke support, or otherwise invalidate an earlier
PASS.  The corrected frozen opportunity is at most **20 actual CHECK-stage tail
callbacks**, not the old 40 mixed verification units, and none is currently
authorized for omission.

This audit sharpens the remaining question.  Even if a pure-checker calculus is
available, can the frozen 20 callbacks be retrospectively classified as pure?
The answer is **no** with the evidence that was recorded.

## 1. Frozen evidence channel does not bind checker code

Source custody:

```text
frozen R0 branch   claude/machine-epistemics-cognitive-ladder-69lo4d
frozen R0 commit   47d706ab42d8528060356c7d4a267e1454ce9e7a
instrument blob    2af3f979932bbe0156970f619bbfe28e217008fe
receipt blob       2de217fda11b00708ad143ebe64b5a1ff6fef90d
```

The immutable instrument's per-candidate record contains exactly the semantic
selection/work fields it needed:

```text
operator_id
input_atoms
verdict
composition_work
verification_calls
```

It does **not** record a checker implementation digest, checker-language version,
effect certificate, proof object, or content-bound checker identity.  The derived
receipt therefore proves which operator/verdict/work was observed, but not which
checker code/effect semantics produced the verdict.

This is not a criticism of the original R0 instrument.  Its registered question
was routing/work, for which those fields were sufficient.  It becomes a binding
limitation only when a later study asks the new counterfactual question "was the
omitted tail checker effect-free?"

## 2. Current persistence has the same aliasing problem

The current runtime's `_operator_manifest` explicitly states that it is a
**declared contract, not a code-identity proof**.  It persists

```text
checker_required = true/false
implementation_identity = HOST_SUPPLIED_UNVERIFIED
```

but not the checker implementation.  `OperatorSpec.fingerprint` likewise binds
operator id/version/kind/inputs/output, not checker code.

`r0a_checker_provenance_audit.py` makes the consequence constructive.  It creates
two operators with the same registered metadata:

```text
pure checker       -> PASS, no host effect
effectful checker  -> PASS, mutates host-visible state
```

and verifies all of the following simultaneously:

```text
same operator fingerprint
same serialized operator metadata
same persistent runtime manifest
same checker verdict (PASS)
different effect semantics
```

Thus the current persistent observation map has an exact collision:

```text
phi(operator, checker_pure) == phi(operator, checker_effectful)
```

while the lifecycle consequences differ.  No retrospective classifier, larger
model, confidence score, or empirical PASS rate can recover a distinction that
the recorded identity channel did not bind.

## 3. Why the pure-checker calculus is only a prospective parent

`pure_checker_contract.py` is useful because its admission certificate contains
exactly the kind of content-bound object the current production manifest lacks:

```text
certificate schema
checker language version
AST SHA-256
claimed effects = []
```

The validator recomputes the certificate from the bounded checker AST.  Two
checker programs in the same language receive different AST identities, while
the language excludes host callbacks/runtime capabilities by construction.

This does **not** retroactively certify any of the frozen R0 tail callbacks.  The
frozen channel did not record such a certificate, so there is no sound mapping
from an old PASS verdict/operator id to a pure-checker AST.

## 4. Required prospective migration contract

Before any production early exit can be evaluated, the operator/replay identity
must bind at least:

```text
checker_certificate_schema
checker_language_version
checker_ast_sha256
checker_claimed_effects
```

and admission must verify that binding before execution.  Replay/rebind must fail
closed if the checker binding changes.  An arbitrary host callback must not be
allowed to impersonate the certificate merely by sharing operator id/version or
returning the same verdict.

Only after that prospective migration is frozen should R0A re-run the population
and ask:

```text
how many tail callbacks are certified pure?
what CHECK work is actually removable under the new trace contract?
what certificate validation/storage/replay cost is added?
what fraction remains on unrestricted host checkers and therefore non-elidable?
```

## 5. Scientific terminal

The current terminal is:

```text
CHECKER_PROVENANCE_INSUFFICIENT_R0A
```

This is an **observation/provenance terminal**, not evidence that pure checkers
are impossible and not a reason to learn a router.  The constructive parent is a
prospective, content-bound pure-checker migration followed by a new census.

The claim boundary remains:

```text
production early exit:          NOT AUTHORIZED
frozen 20 callbacks are pure:   NOT ESTABLISHED
checker effects from PASS:      NOT IDENTIFIABLE
pure-checker migration:         PROSPECTIVE ONLY
ML / learned routing:           NOT AUTHORIZED
```

No novelty is claimed for proof-carrying/content-addressed executable identity or
restricted pure languages.  The contribution here is the repository-specific
negative: the historical observation channel and current manifest are too coarse
to support the desired lifecycle-elision claim.
