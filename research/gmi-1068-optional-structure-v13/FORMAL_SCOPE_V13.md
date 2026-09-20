# Formal scope — V13 optional structure

Read [CORE.md](CORE.md), then [THEORY_V13.md](THEORY_V13.md).
This file identifies the exact Lean boundary for frozen round M.
The categorical mechanisms belong to the primary parents recorded in
[PARENTS_V13.json](PARENTS_V13.json); this is a concrete formal repair,
not a claim to have discovered the interchange argument.

## Files and proof interface

All modules use Lean 4.19.0 with Std; no Mathlib dependency is needed.

1. `InterchangeV13.lean`: general interchange result, actual reset functions,
   and the necessary weak-unitor obstruction.
2. `DiscreteMonoidalV13.lean`: the discrete object-monoid construction.
3. `LoopMonoidalV13.lean`: its product with the one-object C2 category.

The latter two import only the first. No V11 proof is imported here.
`proof_contract_v13.py` provides `SOURCE_NAMES`, 37 explicit typed
`ENTRIES`, and `audit_source()`. The generated audit re-elaborates each
registered statement using its named declaration; mere name existence
or successful compilation of empty modules cannot satisfy this contract.

## M1: common units and the actual one-object countermodel

`operations_coincide` and `operations_commute` quantify over an arbitrary
type and two binary operations. Their hypotheses are a shared two-sided
unit and the displayed interchange equation. The proofs derive equality
of the operations and commutativity. Associativity is not needed or
assumed for these implications.

`BitProc` has constructors identity, reset0 and reset1. `act` interprets
them as functions on Bool. `sequence` executes its first argument and
then its second. `sequence_actual` proves function-composition fidelity;
`act_faithful` proves distinct constructors are distinct actual functions.
The closed operation has proved associativity and both identity laws.
`invertible_iff_identity` proves that exactly identity has a two-sided
inverse. `resets_noncommute` exhibits the unequal reset orders.

`WeakTensorData tensor` contains candidate left and right unitors,
their two-sided inverse witnesses, their naturality equations, and
interchange. It does **not** assume the unitors are identities, a strict
tensor unit, or the desired contradiction.

`weak_unitors_forced` derives that both unitors are identity by using
the actual invertibles theorem. `tensor_units_derived` then derives
the shared unit from the actual naturality equations.
`no_weak_tensor` and `no_any_tensor` exclude this necessary data for
every binary operation on the three morphisms. This is an arbitrary
operation theorem, independent of the finite Python enumeration.

The connection from the standard definition of a monoidal structure
on this unchanged one-object category to `WeakTensorData` is a
**paper proof** in THEORY. A bundled full monoidal-category interface
and a Lean extraction function from it are not implemented.
That extraction uses invertibility and naturality of weak unitors and
bifunctorial interchange; no strictness assumption is introduced.
Associator and coherence conditions are unnecessary for this contradiction.
The conclusion concerns this unchanged category, not embeddings into
a larger category or alterations of its composition.

## M2: discrete and nonidentity-arrow monoidal examples

`DiscreteHom a b` is the proposition `a=b`. The model defines typed
identities, composition, tensor, associators and unitors. It proves
category associativity and unit laws, tensor interchange, and equality
of any two parallel arrows. The latter entails any well-typed coherence
diagram commutes. Separately instantiating every discrete coherence
diagram as a named declaration is not done.
`no_discrete_braiding` rules out even an arrow family of the required
braiding type using the reset pair.

`LoopHom a b` consists of a proof `a=b` and a Bool.
Its composition and tensor use XOR on the Bool component; tensor on
objects uses `sequence`. The proofs check the following actual typed
operations, rather than receiving categorical laws as hypotheses:

- `comp_assoc`, `left_id`, `right_id`;
- `tensor_ident`, `tensor_interchange`;
- `structural_inverse`, covering the chosen associators and unitors;
- `associator_natural`, `leftUnitor_natural`,
  `rightUnitor_natural`;
- `pentagon` and `triangle`, with both composite arrows stated explicitly.

These declarations are in namespace `OptionalV13.LoopHom`.
Object associativity and unit equalities come from the actual reset
monoid. Structural arrows have Bool false and the requisite endpoint
proof. Their inverse arrows use the symmetric endpoint proof.
Calling this construction a monoidal category packages these checked
laws according to the standard definition; that bundled packaging
itself is not implemented.

`toggle_nonidentity` and `toggle_involution` give actual nonidentity,
invertible loops at every object. `no_cross_hom` derives absence of
arrows between unequal objects from the endpoint field.
`no_braiding_component` applies this to the unequal tensor orders of
reset0 and reset1. `no_braiding` excludes a family of components.
No naturality or hexagon test is needed when a required component
cannot exist. This excludes braiding for the displayed tensor only;
it does not exclude a different tensor on the same underlying category.
The XOR interchange theorem also gives the commuting positive control
used in the loop construction.

## Reproduction and kernel dependencies

On laptop billy, from the worktree root, use a fresh directory and compile
in `SOURCE_NAMES` order. Set `LEAN_PATH` to that directory and run:

```sh
/home/billy/.elan/bin/lean +leanprover/lean4:v4.19.0 \
  -DwarningAsError=true -o "$proofdir/InterchangeV13.olean" \
  research/gmi-1068-optional-structure-v13/InterchangeV13.lean
```

Repeat for the two remaining modules with their respective names.
Generate `AuditV13.lean` from `proof_contract_v13.audit_source()`
and compile it with the same `LEAN_PATH` and warning flag.
The root-owned checker performs this fresh replay and inspects
`#print axioms` for every registered statement.

The observed registration dependencies are standard `propext` and
`Quot.sound` for function faithfulness, and `propext` for the
invertibility-derived obstruction. The other registrations have no
listed dependencies. There are no added axioms or unfinished proofs.

## Authority boundary

These proofs address the optional tensor and braiding countermodels.
R1-010 relies on a separate fresh V11 replay of the general typed-path
and congruence-quotient proofs; this package does not replace that replay.
The Python finite corpus and its independent oracle are separate evidence,
not a kernel-checked correspondence with the Lean implementations.
This round proves neither primitive-count minimality nor a canonical
architecture, learning method, probability prior, or universal AI derivation.
Atom decisions and remaining requirements belong to ADJUDICATION and
the current control-plane snapshot, not to compilation alone.
