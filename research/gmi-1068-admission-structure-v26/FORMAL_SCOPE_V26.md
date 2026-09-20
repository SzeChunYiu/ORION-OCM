# Formal scope V26

This file describes the actual kernel inventory for the frozen Z1–Z4 result.
It does not certify the Python corpus, close an atom, or establish a complete intelligence theory.
The exact registration contract is `proof_contract_v26.py`: 34 source files and 227 entries.
Twenty-one immutable sources are rebuilt alongside thirteen new modules.
No theorem conclusion is supplied as a premise in place of the required construction.

## Reproduction and audit

From this package on billy-laptop, run:

```sh
GMI_LEAN_BIN=/home/billy/.elan/bin/lean /home/billy/.local/bin/python3.12 -c 'import check_lean_v26; print(check_lean_v26.evaluate())'
```

The checker invokes Lean `+leanprover/lean4:v4.19.0 -DwarningAsError=true`.
It copies the dependency closure into a fresh temporary directory, sets `LEAN_PATH` there,
and compiles each source and then a separately generated typed audit.
Every registered definition/theorem must inhabit its explicit reviewed type.
Constructor and operation equations bind the actual structures, not only their names or return types.
The audit also prints the axioms of every registration; unproved proof placeholders are rejected.
Classical choice, propositional extensionality and quotient soundness may occur through inherited proofs.
This is a Std-only development; no mathlib dependency or Real implementation is introduced.
Unavailable toolchains/files are CANNOT_CHECK; source or typed audit rejection is a distinct failure.
The checker API retains `ROOT`, `SOURCES`, `evaluate` and `InvalidProof.stage`.
Source-valid mutants compile before their independently typed registrations reject at AUDIT.
Neither source hashes nor the static contract alone substitute for kernel replay.

## Z1: restriction is an actual category and observer transport

`CategoryAdaptersV26` constructs V11 Category ↔ V5 ProcCategory adapters.
Object/Hom/identity/composition equations and both record roundtrips are registered.
`RestrictedV26.category` uses the actual V5 restrictedCategory through these adapters.
Its Hom is the predicate subtype; identity and composition retain the original operations.
The closed predicate contains every original identity and every composite of admitted arrows.
The original V5 closure characterization is replayed with its exact type.

The inclusion has unchanged objects and erases only subtype proofs.
Its bundled map is injective. Actual V19 partial multiplication commutes, including None.
Actual V25 raw-tree responses commute for every bracketed tree, mapping both Arrow and Empty.
Failure reflection and equality reflection of successful bundled outputs are proved separately.
An ambient arrow has a restricted lift exactly when it satisfies the predicate.
The unit characterization prevents a retained nonidentity idempotent becoming a new identity.

`ProcessMapsV26.ProcessMap.path` recursively maps actual V11 paths.
Nil, cons, append, evaluation and actual V25 pathTree interpretation are registered.
The restriction result therefore covers genuine histories, not only their evaluated composites.
It does not infer which physical arrows should be admitted or make arbitrary predicates closed.
An ambient-query implementation must still guard nonadmitted inputs.

## Z2: the exact raw-query boundary for functors

`ProcessMapsV26.ProcessMap` stores an actual object map and dependent Hom map,
with identity and composition preservation. Source and target Category laws are explicit.
Its bundled map retains mapped endpoints; its raw-tree map translates both leaf constructors.
`RawTransportV26.sharp_equivalence` proves:

- all bundled partial products commute iff the object map is injective;
- all raw-tree Option responses commute iff the object map is injective.

The theorem includes empty object/arrow types and needs no Hom injectivity or surjectivity.
Sufficiency derives endpoint reflection and then inducts over actual trees.
The proof inventory also binds `collapsed_empty_witness`: distinct source objects with equal images
give literal Seq(Empty A, Empty B), source None and target success at the mapped identity.
Thus the anchored query required by the freeze is an actual constructor-level witness.
The generic recursive `eval_map` theorem assumes atomic operation/encoder commutation;
the category theorem derives those hypotheses rather than assuming the desired tree equality.

Every functor preserves successful raw trees and actual typed paths without object injectivity.
Homwise faithfulness plus object injectivity gives bundled-output injection and reflection.
Object injection alone need not recover arrow distinctions.
`FunctorControlsV26` supplies the actual two-object indiscrete category collapsing to terminal,
fullness/faithfulness, an explicit section, inverse components and naturality equations.
A global categorical Equivalence record is not built; its standard packaging is paper-level.
The actual one-object Boolean group collapsing to terminal preserves raw transport but loses outputs.
The comparison concerns this literal raw syntax, not an equivalence-invariant category observation.

## Z3: exact same-path Nat resource lift

`ResourceCategoryV26.category` uses actual V5 resourceCategory.
Objects are (object, residual Nat); Hom over f requires r = cost(f) + s.
The projection has actual object/Hom/identity/composition bindings.
Premises are cost(identity)=0 and cost(composition)=sum of costs, with Nat costs.
A single-arrow lift exists iff its cost is affordable; every lift has residual r−cost(f).

The recursively defined `pathCost` sums the edge costs of the actual V11 Path.
Its nil/cons equations and equality with cost of path evaluation are registered.
`ResourcePathsV26.lift_iff` quantifies an actual resource Path q whose projection is exactly p.
Its construction chooses coherent intermediate residuals by induction on p.
`balance`, `residual` and `exact_lift` establish the precise endpoint balance.
This includes empty paths and zero-cost edges; it is not merely a lift of eval(p).

`ResourceControlsV26` instantiates the V5 Nat process and cost n=n.
Two separately available cost-one arrows at residual 1 fail to join after the first reaches 0,
while their forgotten base arrows compose. Literal Path(1;1) cannot lift from residual 1.
Its actual lift from residual 2 passes through 2→1→0 and projects to that same Path.
Projection preserves successful histories but does not reflect incompatible resource joins.
The finite Python chain model is a bounded full subcategory, not every Nat resource object.
No finite compression theorem for the infinitely many balances is claimed.

## Z4: exact retained information in optional structures

`LocallyDiscreteV26.Two C f g` is PLift(f=g), retaining typed parallel boundaries.
The module constructs actual V11 local hom categories, vertical/horizontal composition,
identity compatibility, interchange, associators/unitors/inverses and typed coherence.
Naturality, pentagon and triangle are derived from equality proofs and actual Category laws.
The underlying category is C and its actual V25 observer is unchanged.
The two-dimensional data and these diagrams are kernel checked.
Their packaging into a standard external bicategory record is paper-level.
Arbitrary nonidentity two-cells or other enriched observations are not reconstructed.

`OptionalCategoriesV26` constructs actual V11 function, normalized-matrix and total-relation categories,
and actual Dirac, graph and support ProcessMaps using immutable V14 definitions.
The contract binds Hom/id/comp, map object/Hom applications, matrix entries and relation predicates.
Dirac and graph faithfulness, support composition and probability-loss evidence are freshly replayed.
The full V14 Weight interface remains assumed, including support-specific hypotheses.
Boolean semirings remain permitted: generic normalized Boolean matrices need not be functions.
Ordinary nonnegative rational/real interpretations are inherited paper specializations.
The actual seven-arrow Std.Internal.Rat model and its distinct same-support probabilities are replayed.
No general Lean rational/real semiring instance is silently inferred from that finite witness.

Actual V13 reset and loop categories are wrapped with their inherited operations.
The reset obstruction concerns the unchanged category; extraction from standard weak unitors is paper-level.
The loop obstruction concerns the registered tensor, not every tensor on that category.
Inherited exact Eckmann–Hilton, reset/unit, loop/coherence and no-braiding witnesses are registered.
These results make optionality relative to the sequential observer precise.
They do not erase stochastic probabilities, branch sets, a chosen tensor or arbitrary higher information.

## Boundaries, controls and status

`ConstructorBindingsV26` and `OptionalBindingsV26` pin the actual definitions used above.
`ProofTargetsV26` supplies three independent mutation leaves, in this order:
raw_transport_contract, restricted_history_contract, resource_lift_contract.
The last requires exact projection of actual paths, not merely an arrow over a composite.

The exhaustive Python tables, restrictions, tree observations and resource lift attempts are finite evidence.
Their independently checked correspondence with these Lean definitions is not a verified extraction theorem.
Malformed-input rejection, complete dependency custody and six-row ledger validation are Python checks.
Kernel validity alone does not certify those operational requirements or their measured counts.
The finite enumerations do not replace any of the arbitrary-carrier theorems above.

The classical parent mechanisms are credited in the theory and parent ledger.
This development claims an explicit integration and correction of scope, not new category theory.
Only the frozen relative R1-006 target is a candidate for closure after all independent checks.
R1-009, whole R1 and the rest of #1068 retain their separately governed status.
