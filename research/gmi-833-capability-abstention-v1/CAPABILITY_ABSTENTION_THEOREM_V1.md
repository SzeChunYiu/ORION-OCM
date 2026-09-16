# Capability identification and mandatory abstention — v1

**Issue:** #913, child of #833 Section K  
**Freeze:** `FREEZE_V1.md` at commit `b1615a6f55ffe1ad5925ab3d75674fc55dcc2886`  
**Claim ceiling:** `GMI_833_CAPABILITY_IDENTIFICATION_ABSTENTION_AT_REGISTERED_FINITE_SCOPE`

## 1. Typed contract

Fix a finite nonempty registered candidate realization/model domain `X`, a
surviving set `C subseteq X`, and an architecture-name-free external capability
query `q:X->Q` in the sense of #848. `C` is either a bare feasible set or an
explicit confidence set carrying failure budget `alpha`; those uncertainty
types are not interchangeable.

Define the exact identified capability set

`I_q(C)=q[C]={q(x):x in C}`.

This tranche does not construct `C`, fit a predictor, or calibrate it. It states
the decision rule after the candidate set and query semantics are registered.

## 2. ABSTAIN-1 — point prediction iff singleton image

For nonempty `C`, emit a point prediction `y` if and only if

`I_q(C)={y}`.

If `|I_q(C)|>1`, emit

`CANNOT_IDENTIFY(I_q(C))`

with the complete set and no point value.

### Proof

If `I_q(C)={y}`, every surviving candidate has query value `y`, so the point is
invariant over all registered possibilities. Conversely, if the image contains
distinct values `y` and `z`, candidates realizing both remain possible; neither
point is invariant. Thus a uniformly sound exact point is licensed exactly in
the singleton case. `□`

### Forced-point counterexample theorem

For every chosen member `y` of a non-singleton exact image, some surviving
candidate `x` satisfies `q(x) != y`; that candidate is an explicit
counterexample to uniform soundness. The binary hostile uses two survivors with
capability values `{0,1}`. Choosing either value is refuted by the other model.

Abstention is query-relative, not model-identity-relative. The same two
unresolved models under the coarser constant query `q(x)=7` have image `{7}`
and therefore license point value 7. Full model identification is unnecessary
for every capability functional.

## 3. Terminals that must remain distinct

- `C=emptyset` -> `INCONSISTENT_REGISTERED_ASSUMPTIONS`. There is no surviving
  world over which to identify a capability.
- Missing query -> `CANNOT_CHECK_QUERY_NOT_REGISTERED`.
- Query not total on `X` -> `CANNOT_CHECK_QUERY_NOT_TOTAL_ON_DOMAIN`.
- Nonempty multi-valued image -> `CANNOT_IDENTIFY` and mandatory abstention.

The empty-set terminal takes precedence because inconsistency is already known
without evaluating a query. Missing semantics are not evidence of multiple
capability values, and multiple values are not a checker failure.

## 4. Confidence is preserved, not promoted

If `C` is a confidence set with

`P(theta in C) >= 1-alpha`,

then by event inclusion

`P(q(theta) in q[C]) >= 1-alpha`.

If `q[C]={y}`, this specializes to

`P(q(theta)=y) >= 1-alpha`.

The exact failure budget remains attached; confidence is not rewritten as
certainty. A bare feasible set carries no probability premise, so supplying an
`alpha` with `FEASIBLE_SET` is rejected rather than treated as calibration.

## 5. Exact replay

On a three-candidate domain, the executor checks:

- all 64 survivor-set/binary-query pairs as feasible sets;
- the same pairs at three exact failure budgets, 192 confidence cases;
- all 36 choices of a forced point from non-singleton images, each with an
  explicit counterexample candidate; and
- all 8 survivor sets with missing query semantics.

Hostiles cover floats/Booleans, out-of-domain survivors, duplicate/empty
domains, non-total queries, feasible sets carrying fabricated alpha, malformed
confidence budgets, incomplete identified sets, parent mutation, and forbidden
scope promotion.

## 6. Parent subtraction and boundary

This is the capability-specific binding of #851's parent-owned finite
identified-set/reject rule to #848's external capability functional. The
repository contribution is only the exact fail-closed adapter, exhaustive
certificate, and Section K claim boundary.

Allowed terminal:

`GMI_833_CAPABILITY_IDENTIFICATION_ABSTENTION_AT_REGISTERED_FINITE_SCOPE`

Not established: a completed capability predictor, calibration from a feasible
set, real-system validation, universal capability identification, or complete
GMI.

