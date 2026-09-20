# Independent formal review V26

The reviewer authored the paper proofs and independently read all thirteen new
Lean modules, the exact registration inventory, replay checker and final formal scope.
The reviewer did not edit the formal sources or generate their proofs. This is
independent proof/code review, not a second independent paper authorship.

## Observed fresh replay

Executed check_lean_v26.evaluate on billy-laptop with the pinned Lean4.19.0 runtime.
The checker built21 immutable dependencies and13 new sources in a fresh isolated
directory, then checked227 explicit registered types and their printed axiom sets.
Actual result: PASS,34 source files,227 exact registrations.
Audit SHA256: 2bcbc48a6722833687bf269238afedf960a0c4b9b7ed066dbe5c38db494a5c90
Independent record: /tmp/gmi-v26-independent-kernel.json.
Proof contract SHA256: 1ec676169c9cb039c58939c36e836472d2f65734c3f2ca668ae5eec335a205b9
Replay checker SHA256: 40071f80eb2822e244cf40516fd51095f70a2225861a746d0969c782d8447e9a
Final FORMAL_SCOPE SHA256: 6bc450a08d832e57fb1e2ef2417acbbb3a4f86e8a7c9ff56f0d2df372235407f
This pass is an independently observed kernel replay, not inferred from file hashes.

## Z1: actual inherited structures

CategoryAdapters retains the actual V11/V5 object, Hom, identity and composition
fields, with both record roundtrips. RestrictedV26.category is the actual V5
restrictedCategory through these adapters; ConstructorBindings binds that equation.
The closure criterion has its original inherited-operation meaning. No desired
observer equation is smuggled into a category or admission-field premise.
Inclusion fixes objects and erases subtype proofs. Its partial-product equation
splits real endpoint equality, and its tree theorem applies generic induction only
after deriving the atomic equation. Actual V11 nil/cons/append/evaluation and
V25 pathTree equations are registered. Bundled injectivity and response reflection
use subtype extensionality. Nonadmitted lifts and absence of spurious units have
explicit theorem types. Nothing infers physical adequacy or arbitrary P closure.

## Z2: sharp iff and separate recovery

ProcessMap.mk is explicitly registered with only an object map, dependent Hom map,
identity and legal-composition laws. Object injection is a conclusion in the
sharp equivalence, not a constructor requirement; hom faithfulness is separate.
The raw ProductsCommute/TreesCommute definitions are bound to actual Option outputs.
Sufficiency derives endpoint reflection; necessity rules out a collapsed pair of
identities. The separate collapsed_empty_witness registers the freeze's literal
Seq(Empty A,Empty B), including source None and target mapped-identity success.
Success preservation works without injection. Bundled-output injection uses both
object injection and hom faithfulness; failure/output reflection are not conflated.
The C2 collapse is an actual nonfaithful positive. The indiscrete collapse has
actual full/faithful maps, a section, inverse components and naturality, while
raw reflection fails. A standard global Equivalence record is not constructed;
identification of those concrete components with it remains paper-level.

## Z3: exact path, not evaluated-composite substitution

Resource category and projection bindings use actual V5 Nat resource data.
The cost laws are explicit primitives, with separate nil/cons pathCost equations.
ResourcePaths.balance derives the initial=sum+residual equation from actual edge
constraints. lift constructs each subtype edge and coherent intermediate balance
by path induction. lift_iff and the mutation leaf quantify a genuine resource Path
whose projection equals the entire original Path. residual and exact_lift retain
the exact endpoint balance. Empty paths and zero-cost edges are covered.
ResourceControls uses the actual Nat process and explicit cost-one arrows; failed
raw join, successful forgetting, no balance1 lift and actual balance2 lift are
registered. This is neither a shortest-path proof nor a physical resource model.
The bounded Python chain is separately checked implementation evidence.

## Z4: optional structures have actual data

LocallyDiscrete uses PLift of equality of parallel actual arrows. Local Hom/id/
composition, horizontal equations and underlying category are explicitly bound.
Its inverse components, naturality, interchange, pentagon and triangle are correctly
typed; equality of parallel proof data follows from proof irrelevance, not an
assumed global coherence theorem. The actual V25 observer remains unchanged.
Standard external bicategory packaging remains paper-level; arbitrary higher-cell
information is not reconstructed by the equality2-hom example.

OptionalCategories/Bindings wrap actual V13 reset/loop and V14 function/matrix/
relation/rational operations, including Hom/id/comp and map applications. Generic
matrix results retain full Weight assumptions; they do not introduce a Real/Rat
instance. Actual rational normalization/composition and support probability loss
are freshly replayed. Graph/Dirac faithfulness and support transport are distinct.
Reset no_any_tensor is a necessary-law obstruction; standard weak-monoidal extraction
remains paper. The loop no-braiding theorem concerns its registered tensor only.

## Audit and verdict boundaries

The checker stages all sources and compiles them before the generated audit.
Every registration has a static explicit type; constructors and operational
equations prevent name-only placeholder acceptance. Source placeholders are
rejected and each registration's axiom report is inspected. Classical/proof-
extensionality dependencies inherited from the stated constructions are permitted.
Missing toolchain/source inputs are CANNOT_CHECK; invalid proofs have a distinct stage.
Root's four source-valid corruption cases and complete integrated Python suite
are recorded by their actual canonical receipt, not asserted from this review.
The reviewer observed no formal defect within this exact scope. Kernel validity
does not certify arbitrary physical admission, malformed-input handling, finite
coverage counts, standard external packaging or complete GMI. Sole original006
eligibility and the six source-row distinctions remain subject to all frozen gates.
