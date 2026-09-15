# #809 freeze — Section R exact-microscope closure audit V1

Parent: #602 Section R. Child: #809.

This file freezes the audit universe and gates before any manifest, audit result, scorer, or dedicated CI exists on this branch.

## Registered audit universe

The audit contains exactly 14 class IDs, matching the 14 already-checked microscope classes in #602 Section R:

```text
R_ARCH       architecture derivation
R_LEARN      learning-law
R_MEMORY     memory differentiation
R_CONCEPT    concept formation
R_PLAN       planning
R_CAUSAL     causal
R_SOCIAL     social/theory-of-mind
R_TEACH      teaching
R_CULTURE    culture
R_SPECIES    multi-species ecology
R_DOMAIN     domain collision
R_CAP        capability ceiling
R_DEV        development/evolvability
R_REACH      reachability/search-bias
```

The two master rows under audit are universal only over these 14 registered class IDs. No other repository experiment is implicitly certified.

## Enumerability gate

A class may receive `ENUMERABLE_CERTIFIED` only when a pinned canonical artifact provides all of:

1. a finite registered universe/domain, with explicit bounds;
2. an exact oracle, exhaustive enumerator, exact dynamic enumeration, or formal theorem plus finite exhaustive certificate that covers every object in that registered universe;
3. a machine-checkable certificate/receipt or executable replay artifact;
4. a declared evidence class (`P2` or `P1+P2` for this audit);
5. a scoped claim ceiling.

Sampling, selected examples, empirical averages, or an unverified `RESULT` filename are insufficient.

The audit must verify source paths exist at the audited commit and that required certificate metadata is nonempty. If a canonical artifact is executable under repository CI, normal Python and `python -O` must not disagree on the registered receipt; a pre-existing CI/custody receipt may satisfy this when pinned.

## Minimal-negative-twin gate

A class may receive `MINIMAL_NEGATIVE_TWIN_CERTIFIED` only when the pinned authority provides a negative twin satisfying all of:

1. same frozen comparison universe as the positive case;
2. all non-intervention coordinates held fixed, or a proof that the declared joint intervention is one atomic registered perturbation;
3. reversal/removal of the positive property or exact demonstration of the targeted failure;
4. an explicit finite perturbation/minimality order;
5. proof or exhaustive certificate that no strictly smaller perturbation in that order suffices;
6. provenance identifying whether the twin was preregistered confirmatory evidence or a post-hoc corrective hostile. Corrective hostiles may validate the mathematical boundary, but cannot be relabeled as preregistered confirmation.

A merely convenient negative example does not pass the global minimality row.

## Machine-readable manifest schema

Every manifest row must contain:

```text
class_id
class_name
canonical_artifact
claim_scope
finite_universe
certificate_artifact
certificate_kind
proof_class
claim_ceiling
enumerability_status
enumerability_reason
negative_twin_artifact
negative_twin_intervention
minimality_order
minimality_certificate
negative_twin_provenance
negative_twin_status
negative_twin_reason
```

Statuses are only:

```text
PASS
GAP
```

The audit receipt derives counts from the manifest. Hard-coded `14/14` claims are forbidden.

## Fail-closed hostiles

The validator must reject or downgrade appropriately when:

- any registered class ID is omitted;
- any unknown or duplicate class ID appears;
- a referenced path does not exist;
- finite-universe text is empty;
- sampled/example evidence is labeled exhaustive;
- certificate kind is missing or outside the registered exact kinds;
- negative twin changes multiple uncontrolled coordinates without an atomicity proof;
- minimality order is empty;
- minimality certificate is missing;
- a GAP row is mutated to PASS without supplying all required evidence;
- expected pass counts are injected rather than recomputed.

## Decision rule

The #602 row

```text
Every microscope fully enumerable with certificate.
```

may be reconciled only if the audit result derives enumerability PASS for all 14 class IDs.

The #602 row

```text
Every positive microscope paired with a minimal negative twin.
```

may be reconciled only if the audit result derives minimal-negative-twin PASS for all 14 class IDs.

One row may close without the other. Any gap remains explicit.

## Claim ceiling

Allowed:

```text
REGISTERED_SECTION_R_MICROSCOPE_AUDIT_AT_FINITE_SCOPE
```

Forbidden from this lane alone:

```text
ALL_REPOSITORY_EXPERIMENTS_ENUMERATED
ALL_POSSIBLE_MICROSCOPES_COMPLETE
REAL_WORLD_VALIDATION
COMPLETE_GMI
```
