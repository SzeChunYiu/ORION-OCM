# V16 formal scope

Read after FREEZE_V16.md and TARGET_CONTRACT_V16.json.
This file describes proof scope, not original-atom closure or scientific authority.
Original GMI2-R2-003/007 remain unchanged and UNKNOWN.
Only the explicitly versioned replacement statements can receive new evidence.

## Kernel and reproducibility

Pinned compiler: Lean 4.19.0; every source uses warningAsError.
No new mathematical dependency is installed.
Run on billy-laptop from this package:

```sh
GMI_LEAN_BIN=/home/billy/.elan/bin/lean /home/billy/.local/bin/python3.12 \
  -c 'import check_lean_v16; print(check_lean_v16.evaluate())'
```

The driver supplies the reviewed sibling-module imports for isolated Python.
check_lean_v16.py returns PASS only after source compilation and typed audit.
Missing tooling or unreadable inputs raise CannotCheck.
Rejected sources or statements raise InvalidProof with SOURCE/AUDIT stage.
These distinctions do not turn missing evidence into successful verification.

SOURCE_PATHS names ten repository-relative files in dependency order:
five immutable sources from V11, V9, V5 and V12, then five new V16 modules.
Every run reads their bytes, stages them in a fresh temporary directory, and
compiles every dependency anew. LEAN_PATH points to that directory.
No repository .olean or previous run's compiled files provide this evidence.
The returned receipt binds source bytes and generated audit bytes.

proof_contract_v16.py supplies 46 explicit typed entries.
The audit builds definitions at those exact types and prints their assumptions.
It registers conclusions with quantifiers and premises, not merely names.
Classical choice, proposition extensionality and quotient soundness are standard
Lean foundations; no custom mathematical premise is declared as a new axiom.
Primitive scalar laws and explicit linearity hypotheses remain visible.

## P1: actual typed admission reconstruction

HistoryAdmissionV16.lean imports the immutable V11 inductive Path.
Its arbitrary object and typed-edge universes need not be finite or inhabited.
P is an arbitrary predicate on typed edges; no decidability is required.

Admitted recursively accepts an empty path and requires P at every cons edge.
Edges is the subtype of admitted edges.
Raw is the subtype of ambient paths satisfying Admitted.
Their definitions retain both endpoints in the type.

erase removes edge proofs from a subtype-edge path.
lift constructs a subtype-edge path from an ambient path and admission proof.
forget and restore bundle these maps with the required admission evidence.
The kernel proves both inverse equations:
forget(restore p)=p and restore(forget q)=q.
It also proves both maps preserve empty paths and concatenation.
No endpoint conversion, untyped string encoding or bridge law is assumed.

admitted_single proves singleton membership iff admission of its actual edge.
decode_admission makes the decoder explicit as that singleton membership.
domain_eq_iff_admission_eq proves both directions for complete generated domains.
admitted_iff_lift connects this domain to the actual subtype-edge paths.

The supplied semantic domain already contains membership information.
This is not an effective test for physical admission, empirical identification,
or certification that an arbitrary callback implements the generated domain.
An arbitrary callback can accept all singletons and reject a legal longer path.
The theorem does not silently extend to that callback.

Evaluated histories alone can omit admitted but undefined histories.
The full-source correction requires the full labelled source separately.
No arbitrary normalization, quotient or erasure of singleton labels is permitted.
These facts correct the specified historical reading, not every possible
definition of Hist(C) or every reading of the original broad atom title.

## P2: equal actual contexts, different composition

GroupLawsV16.lean defines four labels with numeric codes zero through three.
c4mul and v4mul are concrete operations.
c4_is_modulo and v4_is_xor connect their tables to addition modulo four and
Nat.xor respectively; these identifications are kernel calculations.
Associativity and both identity laws follow by exhaustive constructor cases.

Law packages actual composition with its proved laws and the fixed identity.
category constructs a V11 category on Unit with these four arrows.
Registered category_comp/category_id connect its operations to the actual law,
rather than merely checking that some Category Unit exists.

CompositionContextV16.lean defines product by recursively using each law's
own composition. The empty product is its fixed identity.
rawParity is the independent XOR fold of label parities.
The parity homomorphism equations for C4/V4 are proved from their actual tables.
fold_parity then proves the arbitrary-word result by list induction.
Finite word enumeration is not the source of the universal quantifier.

FullContext retains source membership, a dependent partial value function and
an actual reflexive/transitive Bool order false<=true.
context(m) includes every word and returns some(parity(product(m,w))).
full_context_eq proves equality of the complete C4/V4 records.
context_nonconstant separates the empty word from singleton one.
The definition therefore does not replace evaluation by a constant selector.

Actual products one*one are two in C4 and zero in V4.
The freshly replayed V9 collision theorem is applied to context and Law.comp,
yielding composition_not_recoverable on attained context observations.
The output is the actual composition function, not a process name.
Both models have the same admission; admission nonrecovery is not claimed.

evaluationKernel compares actual products of pairs of words.
kernel_witness identifies [one,one] and [two] in C4 but separates them in V4;
evaluation_kernels_different proves the relation-level inequality.
It does not claim that arbitrary encodings of the quotient sets are unequal.
Composition-aware quotient histories are not identified as a common source.
The proof does not establish physical equivalence or category nonisomorphism.

## P3: derived finite linear representation

LinearBasisV16.lean imports immutable ScalarV12/FiniteSumsV12.
Scalar supplies primitive ordered commutative ring laws, including 0<1.
It does not supply a representation, basis theorem or vector-order conclusion.

IsLinear requires actual additivity and homogeneity for every scalar.
F is defined on every vector Fin n -> alpha, not merely a finite sample.
linear_zero derives preservation of zero from homogeneity.
basis_expansion and linear_map_sum derive the finite basis argument.
weights(F,i)=F(basis(i)) is a definition, not a linearity certificate.
linear_basis_representation proves F(x)=dot(weights F,x).
representation_unique and unique_linear_representation establish uniqueness.
dot_linear proves the converse construction directly.

PositiveAggregationV16.lean proves monotonicity iff nonnegative coefficients
under those linearity hypotheses, and normalization iff their sum is one.
Zero weights are allowed; strict positivity is not the premise.
probability_representation_iff includes both directions, and
probability_representation_unique gives uniqueness of the resulting coefficients.
The proof works in every finite dimension.
zero_ne_one follows from the primitive strict inequality 0<1.
zero_dimension_not_normalized derives the empty-dimension impossibility.

int_projection_consistency uses the actual V12 Int instance and the projection
onto coordinate zero in dimension two. It is a normalized monotone linear
functional, so the generic premises are not merely an uninstantiated interface.
It is not a fractional probability mixture or a Real/Rat instance.
The general Real specialization remains a paper proof using the stated laws.
The kernel does not certify arbitrary Python callbacks or executable arithmetic
against these definitions. Finite Fraction experiments provide calibration only.

## P4 and exclusions

The audit freshly registers exactly the V5 Nat types of
aggregator_rank_reversal, min_not_additive and max_not_additive.
Their natural-number calculations are not kernel proofs about Real.
General real min/max monotonicity, symmetry, constant preservation and exclusion
of one fixed weighted sum are paper proofs in THEORY_V16.md and inherited V5.
The narrower fixed-weight interpretation is corrected; requiring a declared
aggregation rule survives. No canonical objective, prior or universal scalar
is derived. Infinite-dimensional representation is outside this result.

No theorem here closes the unchanged original targets, all of R2, or R0-R17.
Parent mathematics remains classical typed paths, group homomorphisms, fiber
factorization and finite linear algebra/order. No novelty claim is made.
