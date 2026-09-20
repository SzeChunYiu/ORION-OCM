# Independent formal review — V14

Verdict: the reviewed formal statements establish the declared optional-process
scope. No mathematical defect was found. Final registration replay and the
additional probes below passed on billy-laptop under Lean 4.19.0.
The reviewer authored THEORY/ADJUDICATION but did not author these Lean sources
or their proof contract. This is independent review of the implementation and
proofs, not a second independent authorship of the paper argument.

## What was checked

Read all five Lean modules, the 37 exact typed registrations, FORMAL_SCOPE,
the kernel checker and its source-valid mutation tests. Copied the five sources
into a fresh temporary directory, compiled each with warningAsError and a fresh
LEAN_PATH, then compiled the generated audit in the same isolated directory.
All 37 advertised types elaborated against the actual theorem values.
The printed dependencies were limited to propext, Quot.sound and
Classical.choice; no sorryAx, new axiom or unfinished proof was accepted.
The input files were not modified by the independent replay.

The audit SHA256 is
`4b4ac4e2ea2d75dad29e6bca161686f2b03ddd5b13c185d3711d2dc95dedc95b`.
Reviewed source SHA256 bindings:

| Source | SHA256 |
| --- | --- |
| WeightSumsV14.lean | e5be5ec25ba3ed82b51589198ffcdaa3acd55655782cfee43aec26b19af47b2e |
| MatricesV14.lean | 83fc0ca4ffd70184cea2830dba311e7a575930153cf0d0d89a54b11bbfccf5c6 |
| RelationsV14.lean | 53f17b8594ded4cabea0d557d5c130a11f4ecfe3b6aa98214dc5c1ece6080291 |
| SupportV14.lean | 94a2edb9480a5fcfabcf5061da11e4200879eca96022885affd69ba896f79422 |
| RationalModelV14.lean | 63ff269c4a6e3962281a505e77faee44040937fbbbe7fc4407c32e3912f88d48 |

## Assumptions versus conclusions

Weight contains primitive scalar laws. It does not contain associativity of
matrix composition, normalization closure, finite-sum support, functor laws or
faithfulness as assumptions. Those conclusions are derived in the sources.
Finite sums are recursive over Fin n, including n=0. Their distributivity,
interchange and zero-sum characterization support actual matrix multiplication.
No finite calibration dimension or sampled table substitutes for the generic
matrix proof. Multiplication need not commute for sequential composition.

The complete Weight interface includes zero-sum freeness and no zero divisors.
Generic matrix-law signatures therefore formally assume these even though their
proofs do not use them. THEORY's weaker ordinary-semiring theorem is paper-only
at that sharper boundary. Support composition uses precisely these extra laws:
finite sum nonzero iff a summand is nonzero, and product nonzero iff both factors
are nonzero. Support totality follows from normalization and 1≠0.

TotalRel is an actual relation with pointwise totality, on arbitrary state
types. Its composition retains an existential intermediate state; the proofs
regroup witnesses and transport equality. No global selector, probability or
independence assumption is inserted. Graph and Dirac embeddings preserve
composition and are faithful; identity preservation is definitional.

Empty-source uniqueness is proved for both constructions. Existence is given
by embedding the empty function. A supplied source inhabitant excludes arrows
to an empty target. Thus the general laws are not restricted to nonempty objects.

## Nonvacuous specialization probes

Seven extra theorem declarations were compiled in a temporary audit module:

1. A concrete Boolean Weight with OR addition and AND multiplication admits a
   normalized 1→2 row (true,true) whose support contains both targets.
2. The concrete Nat kernel 0→3 obtained from Fin.elim0 is unique.
3. There is no Nat kernel 1→0.
4. The total relation Empty→Nat obtained from Empty.elim is unique.
5. There is no total relation Unit→Empty.
6. In the actual rational arrow model, reset-zero followed by flip is reset-one,
   whereas flip followed by reset-zero is reset-zero.
7. The actual third and twoThirds entries are mkRat 1 3 and mkRat 2 3 and differ.

These probes passed without sorryAx and are review diagnostics, not added
production receipt counters or additional original-atom closures. Temporary
probe elaboration was corrected before acceptance; failed probe attempts were
not counted as evidence. The Boolean probe guards the scope distinction:
normalized zero/one rows need not be functions for every generic Weight carrier.

## Actual rational witness

The seven-arrow model interprets every arrow as Std.Internal.Rat entries.
Nonnegativity, row sums, all composition entries and faithful interpretation
are checked by finite case proofs with kernel decide. The category laws and
function encoding are proved for the actual closed family, not assumed from
its arrow names. reduced_entries checks positive denominators and reduced
fractions; event_probabilities and half_nontrivial bind the advertised values.
The equal-support/unequal-event result refers to actual matrix entries.

There is no generic Weight instance for arbitrary rational or real weights.
The Nat instance proves consistency but is not a stochastic witness. General
nonnegative-rational/real specializations, and the exactly-one-support converse
to Dirac construction, remain paper proofs as explicitly stated in THEORY.
No bundled Markov-category theorem or certified Python extraction is claimed.

## Registration and authority boundaries

The guard uses isolated copies of the actual source files. Replacing all
sources by import-only modules, weakening support_comp to True, and weakening
support_probability_loss to True are required to compile as sources and fail
at the AUDIT stage. A source parse failure or changed hash alone cannot satisfy
that test. Independent execution of test_kernel_guard_v14 passed all three
source-valid rejection cases; each failed at AUDIT, as required.
Missing tools or inputs remain distinct from a disproved/invalid proof; the
standalone pipeline must preserve its documented CANNOT_CHECK exit status.

The evidence supports only GMI2-R1-008 under FREEZE_V14. Generic sequential
instances and a concrete stochastic subcategory do not prove primitive
minimality, physical randomness, a unique prior or recovery of all intelligence
architectures. Classical constructions retain their cited parent ownership.
