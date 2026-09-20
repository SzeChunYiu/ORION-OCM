# V13 independent formal proof review

Verdict: no unresolved mathematical or formal-scope defect found.
Reviewer authored the paper/adjudication, but not the three Lean modules or
proof_contract_v13.py. Independence here concerns code and proof implementation;
this is not an independent second author of the paper argument.

## Inputs and fresh build

Read InterchangeV13.lean, DiscreteMonoidalV13.lean, LoopMonoidalV13.lean and all
37 explicit expected statement types in proof_contract_v13.py.
On billy-laptop, copied the sources into a new temporary directory, set LEAN_PATH
to that directory, and compiled all three with Lean4.19.0. Then independently
generated and compiled the entire typed audit module and six specialization
probes. All passed. Temporary artifacts were removed by the temporary-directory
context manager. The full finite Python calibration was not rerun here.

Reviewed source SHA256:

- InterchangeV13.lean: `4ad026c039349050b737b492771d68d543f33dd2d26ea3a0a9e769d4f91707f1`
- DiscreteMonoidalV13.lean: `2418c39f35cdaeea552d3f5da1cadfd16833b67613625d110cdacebf549993e2`
- LoopMonoidalV13.lean: `96f35949b7563ef19d5ab812ac4cddfbabfc21b872f05c686e825f9f19dd4852`

The generated typed audit printed axiom dependencies for every entry. No sorryAx
was present. The general interchange consequences and M2 coherence/obstruction
proofs use no axioms; function faithfulness uses propext and Quot.sound. Reset
invertibility, derived unitors/units and no_any_tensor use propext. No additional
mathematical axiom or assumed
nonexistence conclusion was found.

## M1: actual processes and general interchange

BitProc has three distinct constructors, but the proof does not stop at labels:
act interprets them as actual Bool functions, sequence_actual proves composition
soundness, and act_faithful proves the interpretation injective. The registered
sequence is execute-first-then-second; reset1 after reset0 wins, not the reverse.
Associativity and both identities are proved by case analysis and reduction.
Invertibility is a conjunction of both inverse equations, equivalent to identity;
it is not confused with a retraction or an assumed unitor law.

operations_coincide and operations_commute quantify over an arbitrary type and
two arbitrary binary operations. Their premises are only the four unit equations
and interchange. Their proof substitutes units; neither commutativity nor equality
of operations is hidden in a hypothesis. No associativity assumption is needed.

WeakTensorData contains unitors, explicit inverses, the two inverse equations for
each, both naturality equations, and interchange. It does not assume the unitors
are identities or assume the resulting tensor unit equations. Those conclusions
are derived by weak_unitors_forced and tensor_units_derived before no_any_tensor.
With execution-order composition, the left equation is
(tensor identity f);leftUnitor = leftUnitor;f; the right equation is analogous.
These are the correct naturality squares for I⊗(-)⇒Id and (-)⊗I⇒Id.

An actual monoidal structure on the unchanged one-object category necessarily
supplies this data. Extraction from a bundled monoidal-category library is a
paper-level argument; WeakTensorData is only necessary data. Its inconsistency
suffices, so omission of associators from that necessary-data structure is valid.
No inference from its satisfiability to a full monoidal structure is made.

## M2: genuine typed models and full concrete coherence

DiscreteHom is endpoint equality. Identity/composition and tensor are typed;
all parallel arrows agree by proof irrelevance. Structural arrows exist by the
actual sequence associativity/unit laws. Thus the discrete coherence argument
is legitimate thin-category uniqueness, not an assumption that arbitrary diagrams
commute. no_discrete_braiding contradicts the reset pair's unequal tensor objects.

LoopHom is endpoint equality together with a Bool bit. This is not a thin model:
toggle has bit true and is proved distinct from the identity bit false, with
self-composition equal to identity. ext removes equality-proof representation
noise only after the bits agree; it does not identify the two genuine loop arrows.
Typed comp uses XOR, and tensor combines reset-product endpoints with XOR bits.

The module constructs associator and unitors as zero-bit arrows with actual
endpoint equalities. structural_inverse proves both inverse equations.
The three naturality theorems quantify over arbitrary typed arrows, including
the nonidentity toggles. tensor_interchange is the full bifunctor equation.
The pentagon has common source ((ab)c)d and common target a(b(cd)); its two-arrow
and three-arrow routes use precisely the expected associators/tensor identities.
The triangle compares the associator followed by id⊗leftUnitor with rightUnitor⊗id.
Both equations reduce to zero-bit equality after well-typed endpoints are checked.
They are genuine coherence equations, rather than arbitrary equal expressions.

no_braiding_component excludes even an arrow from reset0⊗reset1 to its reversed
object. The stronger no_braiding statement excludes a component assignment for
all object pairs, without needing naturality or hexagon assumptions. It therefore
excludes any braiding for this tensor, including symmetric ones. Alternative
tensors on the same underlying category are outside this conclusion.
Packaging these concrete data as a standard bundled monoidal structure remains
paper-level; the component laws themselves are proved, not merely asserted.

## Additional nonvacuity probes and retained scope

The six independent compiled probes established: the actual ordered reset product;
a reset/id disagreement at true; existence of a nonidentity self-inverse loop at
reset0; emptiness of the reset1→reset0 hom-set; the general interchange theorem
instantiated with actual Bool XOR and proved unit laws; and associator naturality
instantiated with three nonidentity toggles. Thus the positive examples have actual
inhabitants and nonidentity arrows, while the negative conclusions use exact types.

R1-010 requires a separate fresh replay of the V11 general path/category contract.
This review does not claim that finite M1/M2 examples establish all-category laws.
Nor does it certify physical admission, all primitive minimality, arbitrary
congruence evaluator descent in Lean, architecture recovery or complete GMI.
The original frozen interpretation of that atom remains universal category-law
consequences, and target-category laws remain explicit interpretation premises.
