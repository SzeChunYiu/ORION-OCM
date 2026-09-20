# Independent formal implementation review — V16

Verdict: CLEAR for the frozen qualified replacement scopes P1–P4.
This reviewer authored the paper theory, but did not author the Lean modules,
proof registration or compiler driver. This is an independent implementation
and proof review, not a second independent authorship of the paper argument.
It does not close either unchanged original atom.

## Evidence actually checked

Read all five new Lean modules, the five reused mathematical dependencies,
proof_contract_v16.py, check_lean_v16.py and final FORMAL_SCOPE_V16.md.
Independently ran fresh isolated Lean 4.19.0 replay on billy-laptop:
ten sources and all 46 explicit statement registrations passed with
warningAsError and assumption inspection. Final audit SHA256:

`f99615f2635b53e6b85a2596842ccd2ed2fb013d42db340b01f967cd8fcbfab5`

The contract binds theorem types with hypotheses and quantifiers, not names.
Fresh source hashes are recorded by the scientific receipt. The corrected
GroupLawsV16 source hash is:

`620a77846083be4ab507eb6df9638f30f7441770a6fbbbaa75b89a2f1cceadce`

The newly strengthened category_comp wrapper initially omitted its Unit
endpoint annotations and failed SOURCE elaboration in independent replay.
The author added explicit endpoints in source and registration. The final
replay above verifies the repair; failed transient runs are not passes.

Six additional temporary Lean examples passed in a second fresh replay:
Int projection has coefficient one at coordinate zero and coefficient zero at
coordinate one; actual C4/V4 products differ; their concrete kernel witness
holds; singleton admission holds for the always-true predicate and fails for
the always-false predicate. These are nonvacuity diagnostics, not new scope.

Independently executed test_kernel_guard_v16.py: its three isolated source
mutants all compiled their sources and were rejected at AUDIT. The cases are
all ten sources replaced by import Std, composition_not_recoverable weakened
to True, and probability_representation_unique weakened to True. No historical
source was edited. This checks semantic type registration beyond manifest hashes.

## P1: generated typed histories

The primitive data are arbitrary objects, typed edges and an edge predicate.
Path is the actual V11 inductive type. Admitted recursively checks each edge;
it is not a final reconstruction theorem supplied as an assumption.
The subtype-edge and admitted-raw-path maps are constructed recursively.
Both inverses use actual path induction and proof irrelevance; empty paths,
concatenation and endpoints are preserved. The decoder is membership of the
actual singleton, and equality of generated domains is equivalent to equality
of edge predicates. Empty object/edge types are not excluded by hidden premises.

A full source and an evaluator-defined subset remain distinct. The theorem
assumes the full generated source is observed. Neither this kernel result nor
the executable singleton extractor certifies an arbitrary callback's longer
paths or decides physical admissibility. This is the exact qualified refutation.

## P2: composition collision

Actual four-label operations are connected to modulo-four addition and XOR.
Their associativity, units and parity homomorphisms are proved by constructor
cases. Law assumes category laws for a caller-supplied operation, while the
C4/V4 witnesses provide those proofs rather than assuming their conclusions.
category_comp/category_id explicitly bind the constructed category to that
operation and zero label, avoiding an unrelated lawful-category witness.

The evaluator uses each operation's actual recursive product. The all-word
parity theorem follows by list induction. FullContext equality retains the
common complete source, dependent partial evaluator and actual Bool preorder.
Empty word and singleton one prove nonconstancy. Composition differs at one,
one; the evaluation kernels differ on words [one,one] and [two]. The V9
collision theorem is freshly replayed and applied to actual observation maps.
The kernel's model space is the larger Law type, which contains both witnesses;
that establishes the paper's two-model impossibility as well.

Both models have the same admission. The result does not establish admission
nonrecovery, equality of composition-dependent quotient sources, physical
identity, or equivalence of all possible process representations.

## P3: finite linear functionals

ScalarV12 supplies primitive ordered-ring laws, not a basis representation or
an aggregation conclusion. IsLinear requires actual additivity and homogeneity
for every scalar and every full-domain vector. Finite basis expansion, mapping
of finite sums, representation and uniqueness are derived inside the kernel.
The converse weighted functional is proved linear from primitive algebra laws.

Monotonicity implies nonnegative basis values by comparing zero with each
basis vector; the converse follows from coordinatewise order of weighted sums.
Normalization is exactly the sum-one equation. Coefficient zero is admitted.
The combined representation equivalence includes linearity on its left side;
it does not infer arbitrary-function linearity from basis samples or monotonicity.
The n=0 contradiction follows from the single empty vector and zero not equal
one. Actual Int projection satisfies all premises in dimension two.

The generic theorem applies to any supplied lawful Scalar instance. There is
no new kernel Real or Rat instance, and Int consistency does not establish a
fractional mixture. General Real/Rat interpretations remain paper-level.
Exact Fraction tests independently calibrate executable finite arithmetic.

## P4, custody and authority

The three immutable V5 Nat theorem types are freshly registered: rank reversal,
min nonadditivity and max nonadditivity. General Real min/max monotonicity,
symmetry, constant preservation and fixed-weight exclusion remain paper proofs.
The word 'weighting' is not silently narrowed in the original record.

The driver rebuilds dependencies in a new temporary directory and isolates
LEAN_PATH; no repository compiled artifact is substituted for a source proof.
It rejects forbidden proof constructs and sorryAx, distinguishes SOURCE from
AUDIT failure, and distinguishes missing inputs/toolchain from invalid proof.
The receipt binds source bytes, generated audit bytes and registration count.
Standard Lean logical foundations remain; no new unproved mathematical axiom
was accepted. These facts establish the stated mathematical scope only.
Original R2-003/007 stay UNKNOWN, original counts stay 18 fulfilled/204
unresolved, and the full programme remains OPEN. Sidecar governance determines
whether the reviewed qualified replacements receive active authority.
