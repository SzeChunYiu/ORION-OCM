# Formal scope V11

Read [CORE.md](CORE.md), [THEORY_V11.md](THEORY_V11.md), and the frozen
targets in [FREEZE_V11.md](FREEZE_V11.md). These modules construct the
typed history laws and the bridge to arbitrary lawful categories.
Established free-category and quotient mathematics remains parent-owned.

## Files and dependencies

[TypedPathsV11.lean](TypedPathsV11.lean) imports only Lean's `Std`.
[QuotientPathsV11.lean](QuotientPathsV11.lean) imports the first module.
All declarations are in namespace `TypedPathsV11`.
The development supports arbitrary types in explicitly declared universes.
Finite enumeration, nonempty object sets and decidable arrow equality are
not premises of these general theorems.

## Constructed source paths

For vertices `V` and a typed generator family `G : V → V → Type`,
`Path G a b` is an inductive family with a typed empty path and a constructor
prepending an edge to a compatible tail. Distinct generator values, parallel
edges and repeated occurrences are retained by the syntax. There is no
quotient at this stage.

`Path.append` takes a path from `a` to `b` and one from `b` to `c`
and returns a path from `a` to `c`. Endpoint preservation is enforced by
these dependent types; no untyped operation is asserted safe afterward.
An incompatible join cannot be supplied to this function without changing
the types or providing a genuine endpoint equality.

The constructed source laws are:

- `Path.nil_append`: the empty path is a left unit;
- `Path.append_nil`: it is a right unit, proved by path induction;
- `Path.append_assoc`: concatenation is associative, proved by path induction.

`Path.category` packages these proved laws. It does not receive associativity
or unit laws as premises. Empty paths are indexed by their own object.

## Universal interpretation

`Category` separately describes a target category with its typed composition,
identity operations and lawful equations. These target laws are assumptions.
The construction does not establish that an arbitrary physical or computational
process description satisfies them.

Fix a target category, an object map and a typed generator map.
`eval` recursively interprets a finite path.
`eval_nil`, `eval_single`, and `eval_append` prove preservation of empty
paths, the specified generators and composition.
`interpreter` packages the constructed law-preserving map.

`eval_unique` and `interpreter_unique` prove pointwise uniqueness:
any other map with the same object map, generator interpretation,
identity law and composition law agrees on every path.
This is the universal extension statement for the specified typed graph.
Uniqueness is over the whole arbitrary path family, not a tested finite list.

The interpretation need not be faithful. Its target can identify distinct
paths, including histories whose effects coincide or satisfy nontrivial
equations. A target's identity arrow, supplied as a generator, becomes a
length-one source path; it is not syntactically the empty source path.

## Arbitrary typed congruence quotient

`Congruence` requires an equivalence relation on each typed path set and
stability under concatenation in both arguments.
`Congruence.comp` is defined by quotient lifting.
Its well-definedness uses exactly that stability requirement.

`Congruence.comp_assoc`, `Congruence.left_id`, and
`Congruence.right_id` descend the constructed path laws by quotient induction.
`Congruence.category` packages the resulting category.
`Congruence.comp_mk` records composition of represented paths.
An arbitrary equivalence without concatenation stability is not accepted
as a `Congruence`; no theorem promotes all equivalences to valid quotients.

`kernel` proves that equality under every constructed path interpretation
is a typed congruence, using `eval_append` and equality substitution.

## Every lawful category is recovered from its presentation

For any `Category C`, take its underlying typed arrow family as generators,
interpret objects identically, and interpret each generator as that very arrow.
`ownKernel` is this evaluation kernel.
`presented C` is its path quotient.

`eval_onto` proves that every target arrow is the value of its singleton path.
`class_eq_iff_eval_eq` proves exactness: two path classes agree if and only
if their evaluations agree. There are no extra identifications.

`lower` evaluates a quotient class; `quote` sends a target arrow to the
class of its singleton path. The proofs are:

- `lower_quote` and `quote_lower`: the two maps are inverse on every Hom;
- `lower_id` and `quote_id`: both preserve identities;
- `lower_comp` and `quote_comp`: both preserve composition;
- `lower_injective` and `lower_surjective`: explicit Hom bijectivity.

`presentationIso` packages both maps, inverses and preservation laws into
`CategoryIso (presented C) C`, fixing objects.
Thus the result covers arbitrary lawful categories, not only free categories.
It does not identify the unquotiented paths with target arrows.

## Claims outside these modules

THEORY_V11 section 3 also proves descent and uniqueness of an evaluator
through any congruence it respects. That auxiliary general factorization
is paper-only here; the kernel development implements its evaluation-kernel
specialization used in the presentation isomorphism.

These proofs do not verify the Python implementations, exhaustive corpus,
monoid classification, mutation controls or their correspondence to Lean.
Those checks have separately reported evidence.
No extracted implementation or general decision algorithm for quotient
equality is provided.

V5's admission closure/resource-state constructions and V9's process/context
nonrecoverability remain separately bound proofs. They are not re-proved here.
Scientific closure of the three named original atoms requires the independent
adjudication; successful compilation alone grants no status authority.

No universal smallest primitive signature, unique ontology, all-family
intelligence derivation, empirical discovery or whole-round closure follows.
The quotient bridge is relative to a lawful declared category and does not
infer physical admission, a sufficient state description or an objective.

## Fresh reproducible build

From the repository root on laptop billy:

```sh
gmi_v11_lean_dir=$(mktemp -d /tmp/gmi-v11-lean.XXXXXX)
LEAN_PATH="$gmi_v11_lean_dir" /home/billy/.elan/bin/lean +leanprover/lean4:v4.19.0 \
  -DwarningAsError=true -o "$gmi_v11_lean_dir/TypedPathsV11.olean" \
  research/gmi-1068-typed-foundation-v11/TypedPathsV11.lean
LEAN_PATH="$gmi_v11_lean_dir" /home/billy/.elan/bin/lean +leanprover/lean4:v4.19.0 \
  -DwarningAsError=true -o "$gmi_v11_lean_dir/QuotientPathsV11.olean" \
  research/gmi-1068-typed-foundation-v11/QuotientPathsV11.lean
```

A fresh directory prevents a stale first-module binary from supplying the
second module's dependency. Neither module declares an additional axiom,
uses an unsafe definition, or contains a proof placeholder.
Trust includes Lean's kernel, dependent type theory, its quotient principles,
and the imported standard library.
