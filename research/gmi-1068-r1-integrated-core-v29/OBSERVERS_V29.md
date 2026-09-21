# Anchored observer and actual interface transport

## O1 — semantic observer
A typed category gives a bundled arrow (source,target,morphism).
Arrow leaves return their bundle; Empty(A) returns id_A.
Seq evaluates both subtrees and composes exactly when both succeed and the
left target equals the right source. Otherwise its response is None.
Malformed syntax is outside this semantics and must be rejected by the Python
whole-tree structural validator before any semantic failure short-circuit.

Empty anchors cannot be erased: Empty(A);Empty(B) fails for A≠B.
Guarded flattening retains each Empty(A) as an identity arrow before using the
actual Option word evaluator. Associativity handles arbitrary bracketings;
unit laws justify the successful insertions at matching endpoints.

## O2 — functor transport
For F:C→D, map Empty by F.obj and Arrow by its actual bundled arrow map.
If a source tree succeeds, induction and functor identity/composition laws
show its mapped tree succeeds with the mapped output.
For exact equality of Option responses, additionally assume object injection.
In the Seq case this reflects equality of intermediate endpoints; a failed join
cannot revive. Induction then proves equality for every raw tree.

Conversely suppose all raw responses commute. If F(A)=F(B) but A≠B,
Seq(Empty(A),Empty(B)) fails in C but maps to a successful identity in D.
Thus universal response commutation implies object injection.

Faithfulness alone is not object injection. It implies output reflection only
within a fixed source Hom. With object injection, equality of target bundles
first identifies both source endpoints, then faithfulness identifies the arrows.
A nonfaithful one-object functor can preserve all failures while merging outputs.

## O3 — actual named and ambient interfaces
The frozen NamedAdapter uses a proper injective arrow-label map ell and a
bijection from external object names to category objects.
Its Presented carrier is the ascending image of ell, with multiplication
reindexed through the actual inverse on that image.
Its named identity map is ell composed with identities and the object decoder.
This construction checks membership even for singleton Arrow queries.

A present-leaf raw tree decodes to a typed-category raw tree.
Structural induction proves named_response equals the encoded bundled response,
and named_word agrees through the immutable guarded-flattening theorem.
An absent ambient Arrow has no typed inverse; it is not mapped to a default.
Nonunit Empty is relevant to the raw canonical-unit interface; external named
Empty uses the separately validated identity map.

The fixture ell=(0,1,3,4,5,6), object decoder=(2,0,1), identity map=(6,0,4)
retains unused ambient label2. Both endpoints must be encoded, not just arrows.
The V25 permutation-only map_tree cannot implement this proper injection.

## O4 — restriction and resources
A wide restriction includes every identity and is closed under composition.
Its inclusion is identity on objects and injective on each Hom.
Consequently all its own raw trees transport, including failed joins.
Across a shared ambient label set the statement requires every Arrow leaf
to belong to the restricted carrier. Removed full-category arrows may succeed
only in the full model; that is an availability distinction outside inclusion.

Resource projection forgets balances, so it can identify intermediate objects
and revive a raw join. It still preserves successful typed histories.
For additive Nat costs with identity cost0, an actual base path lifts from r
iff its cost is at most r; the lift projects to that SAME path with residual
r minus cost. This is not raw failure reflection or recovery of balances.
