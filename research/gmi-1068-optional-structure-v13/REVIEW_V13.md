# V13 independent implementation review

Verdict: no unresolved scientific or API defect found in the reviewed scope.
Reviewer authored THEORY_V13.md and the adjudication/parent documents, but did
not author optional_v13.py, independent_oracle_v13.py or their tests. This is
independent review of those implementations, not a second independent paper author.
Formal proof review is recorded separately in FORMAL_REVIEW_V13.md.

## Actual source and corpus review

Read the production API and both complete test modules, including the full
calibration loop without rerunning its 19683-operation enumeration.
The production reset table is compared against composition of actual finite
functions in the independent oracle. The three functions are distinct and
closed; actual inverses and noncommutativity are checked before obstruction use.
The oracle's actual functions differ in representation and evaluation from the
production label table. The comparison therefore checks the table's semantics.

The primary enumeration visits every 3×3 table over three labels. Its independent
associativity/common-unit checks select exactly the normalized operations.
For each normalized candidate it checks every interchange quartet, compares
the returned concrete first failure, and exercises all six label permutations.
The obstruction certificate validator recomputes each claimed failure and checks
exact candidate-set equality against separately generated normalized operations.
A one-candidate failure, duplicate record, missing candidate, constant verdict or
non-failing quartet cannot constitute the complete obstruction certificate.
The failed equations refute necessary conditions, which is sufficient for the
nonexistence conclusion when combined with the separately proved unit reduction.

## Necessary weak data versus sufficient monoidal structure

weak_tensor_necessary validates a lawful sequential monoid, exact shared carrier,
valid unitors with genuine two-sided inverses, tensor identity preservation,
both unitor naturality equations and interchange. Its name and docstring correctly
restrict a True result to necessary conditions; it does not assert existence of
an associator, pentagon or triangle witnesses. In particular, all four choices
of C2 unitors pass the necessary checker; this does not say all choices extend
to coherent monoidal structures. The successful full C2 control uses identities.

For the reset category, identity is its only invertible arrow. The proof thereby
reduces any weak unitors to identities, forcing a common unit by naturality.
The normalized finite search has a justified domain; it is not an arbitrary
selection of possible tensors. The constant tensor supplies a useful control:
identity preservation and interchange can hold while unitor naturality fails.
The one-sided retraction example has unequal source/target objects and correctly
does not pretend to be a one-sided inverse in a finite one-object monoid.

## Typed model and API validation

Discrete and product arrows have explicit object labels and valid loop parity.
compose rejects incompatible endpoints; tensor uses actual reset multiplication
on objects and XOR on loops. Identity, composition associativity, tensor units,
tensor associativity and bifunctorial interchange are all exercised. The exact
cross-object hom-set required for a reset-pair braiding is empty in both models.
The product model has actual nonidentity loops, so discreteness is not essential
to the obstruction. These claims concern the registered tensor only.

Table entries, identities and arrow indices reject bool/float aliases before
mathematical use. Empty, nonsquare, out-of-carrier and malformed inputs fail.
Accepted list/tuple representations normalize to the same lawful operations.
The general finite-function composition helper allows different finite domains;
its output need not stay in the reset carrier. reset_composite separately checks
that membership, so the broader helper does not enlarge the registered model.

## Bounded execution evidence

All execution below occurred on billy-laptop using Python3.12, in normal and -O
modes with identical deterministic outputs. No full calibration was repeated.
Selected six existing tests: actual reset category, C2 positive control, typed
monoidal models, obstruction corruptions, weak unitors/one-sided inverse and
malformed inputs. All six passed in both modes.

Observed selected-test counters included 9 actual compositions, 27 actual reset
associativity equations, 18 hom-sets, 15 typed compositions, 30 incompatible
composition rejections, 45 typed tensors, 243 tensor associativity equations,
153 typed interchange equations and two empty braiding hom-sets. Hostiles rejected
12 corrupted obstruction certificates and 65 malformed inputs; all 734 registered
weak-unitor necessity checks passed their expected verdicts.

Additional temporary review probes checked all 64 pairs of C2 arrow-tensor and
unitor choices, with exactly four accepted necessary-data cases. Twenty seeded
non-normalized reset tensors (seed106813), each with all nine unitor pairs,
gave 180 further comparisons against a direct equation evaluator; all rejected
as predicted. Normal and -O results agreed. These are bounded diagnostic probes,
not additional coverage claimed in the driver's registered exhaustive receipt.

## Claim and integration boundary

No API converts a necessary-data acceptance into a full monoidal claim.
No result establishes architecture recovery, physical completeness, empirical
novelty, stochastic/higher-cell elimination or absolute primitive minimality.
R1-010 uses the original freeze's category-law scope and must freshly replay
V11 source-bound typed registrations; this review does not replace that gate.
The final driver, snapshot custody and exact-head CI remain integration gates.
