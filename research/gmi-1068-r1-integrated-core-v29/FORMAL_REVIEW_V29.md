# Independent formal review — V29

## Reviewed artifact and actual replay
Independently read all14 new Lean modules, the63-source inherited inventory,
static331-entry contract, generated-audit mechanism and FORMAL_SCOPE.
This reviewer also authored the paper notes; independence here concerns the
actual code/proof review and fresh replay, not a second paper authorship.

Ran check_lean_v29.evaluate from this worktree with the explicitly selected
Lean4.19.0 binary. The checker staged every source in a new temporary directory,
compiled all77 sources with warningAsError and then compiled the331 typed
registrations. Observed result: PASS,56.311 seconds.
No repository olean cache or theorem-name-only check supplied the result.

Independent receipt: /tmp/gmi-v29-independent-kernel.json
Receipt SHA256:
42e62c17bd1dd24ae2a0570751ee5dd8a00c64442df93de1824cdc8862a2a549
Generated audit SHA256:
091d623d1e4c1d2d57cf526971ac2ca1e032ae89d10407fccf75bf891060114c
proof_contract_v29.py SHA256:
1080e75588e059893dbdd1c09a2f6ec6f0b0ce39795df55806e1b9525a377763
check_lean_v29.py SHA256:
0704bde4a9bc5ae2326656204f515fd8c2bdf4d162ca9ba1237eb383b3f28cef
FORMAL_SCOPE_V29.md SHA256:
34fa8b9f1e87e52e53a5e45b5b939858831b89a27a74079a27edb1a6da1813b4

## Semantic audit
EvalKernel uses the actual typed V11 evaluation kernel.
lower injectivity is derived from quotient equality; generation is not assumed
for faithfulness. quote selects actual generating paths only under Generates.
Both inverse equations, identity/composition laws and the actual ownKernel
specialization are proved, with explicit ProcessMap object/Hom bindings.
Classical choice supplies representatives, not an effective word-search algorithm.

PresentationBridge maps bundled arrows and arbitrary trees in both directions.
Its inverse trees have quotient arrows, so no raw c/ab distinction is recovered.
NamedTransport rewrites the actual V25 named observer and applies the actual
V26 raw theorem: full Option transport iff object injection; success alone
needs no such premise; output reflection also needs Hom faithfulness.

ImageAlgebra constructs the actual image subtype and transports a real algebra
through put/get. Associativity, true local units and coherence are derived.
The Presented constructor's carrier, multiplication and underlying algebra
are explicitly bound. Proper injections are supported, with no preimage for
an absent label. AmbientNamed derives the actual unit landing and observer
equation; complete naming additionally assumes decoder injection and surjection.

AmbientFunctor retains the local label equation and object injection.
RestrictedAmbient derives its restricted label map, carrier and common identity
encoder from the actual wide restriction. guarded_transport has a genuine
present-leaf condition; removed_arrow proves the complementary failure/success
contrast. It does not assume the desired observer equation as a premise.
The final four RestrictedBindings entries bind those exact constructors.

FixedEncoders fixes the common model/code/signature interfaces, derives
Option-map injection and applies the actual V9 recovery_transport theorem.
Its query map may repeat; the conclusion is the q-indexed target pullback.
No target coverage, variable encoder or erased None is silently introduced.
EncoderControls supplies actual Bool/xor response functions, source collision,
target decoder, retained-encoder repair and omitted-query failure.
PresentationControls proves actual missing-generation and Fin6→Fin7 codebooks;
these are nonvacuous witnesses, not opaque expected verdicts.

## Registration and proof-level boundaries
The192 inherited entries reproduce the frozen selection, including the first
explicit registration of the source-derived V9 recovery_transport type.
The139 new entries include actual operation/constructor equations and three
independent final leaves. The static contract fixes expected types before
replay; the runtime does not discover or weaken those expectations.
Each registered value receives an axiom inspection; sorryAx is rejected.
Standard classical choice, quotient soundness and propositional extensionality
remain logical dependencies, not additional physical/category conclusions.

Malformed external syntax is a Python validation concern; Lean Tree is an
inductive datatype. The finite DAG enumeration, adapter implementation and
all population counts remain independent finite calibration. They are not
certified Python extraction or a general finite-enumeration theorem.
Inherited optional and seven-parent paper/finite boundaries remain intact.
A shape/hash guard does not independently prove their prose.

Root separately reported four source-valid weakening controls passed in178.530s:
all-empty and the three final leaves compiled as sources, then failed at AUDIT.
This is distinct from the independent unchanged-source replay above. The
canonical RESULT must retain those actual controls and their coverage.
Missing compiler/input is CANNOT_CHECK; invalid proofs retain SOURCE/AUDIT
failure classification. These outcomes must not be conflated.

## Conclusion within scope
No assumption/definition mismatch was found in the reviewed final proof scope.
The paper theorem ledger now names actual registered declarations and retains
the abstract-kernel versus executable-refinement distinction.
The original eight-result/ten-atom crosswalk and six/six/seven ledgers remain
source-specific. Only a separately validated successor may re-earn current R1;
none of these proofs changes original atom records, R2/R3 or V16 authority.
