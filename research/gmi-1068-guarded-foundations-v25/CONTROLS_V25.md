# Loss witnesses and corrected deletion arguments

## 1. TYPE — legality information, not an independent endpoint field

On labels 0,1 compare discrete p=((0,None),(None,1)) and join q=((0,1),(1,1)).
Both are lawful partial algebras. Filling every None with 1 makes their untagged
output arrays identical; however Arrow(0);Arrow(1) fails under p and returns 1
under q. The failure tag/definedness cannot be discarded. Given the full lawful
tagged table, endpoints are derived, so deleting only a redundant TYPE field causes
no loss and is not a valid witness of field irreducibility.

## 2. PROCESS — availability under a common ambient interface

On L={0}, compare empty support with support {0} and identity product0·0=0.
Arrow(0) fails in the former and succeeds in the latter. On L={0,1}, supports {0}
and {1} have equal cardinalities but Arrow(0) separates them. Their padded tables
are different; local-unit row recovery rules out a same-table lawful counterexample.
These are availability losses, not a claim that the empty category is inconsistent.

## 3. COMPOSITION — actual product, not admission alone

Use actual one-object groups C4 and V4 with labels 0,1,2,3, identity0, every pair
admitted. C4 adds modulo 4; V4 uses xor. Arrow(1);Arrow(1) returns 2 versus 0.
Carrier, units, typing and admission agree, while composition and history meaning
differ. Both models retain associativity and unit laws. This is the V16 witness.

## 4. IDENTITY — internal neutral behavior

On two labels use total constant product x·y=0. It is associative and coherent.
Neither 0 nor 1 is a genuine unit:0·1=0 differs from 1, and1·1=0 differs from 1.
No legal raw Empty exists. Thus lawful internal empty-history interpretation does
not follow from associative composition alone. Removing only a stored identity
field from a lawful table does not cause this loss: true units remain derivable.
This law omission does not preserve the local-unit premise and does not claim to.

## 5. ASSOCIATIVITY — output and definedness

V19's total unital table on 0,1,2 is ((0,1,2),(1,2,0),(2,0,2)).
Unit 0 and coherence remain, but (1·1)·2=2 whereas 1·(1·2)=1.
The corresponding three-arrow trees therefore differ by bracketing alone.

The weak-only table ((0,None,2),(None,1,2),(2,None,2)) has actual local units and
coherence and agrees whenever both triple associations exist. Yet (0·1)·2=None
and0·(1·2)=2. Equality on jointly defined outputs is too weak: definedness agreement
is part of the registered observer. V19 provides the exact finite/kernel checks.

## 6. IDENTITY_LAWS — designated candidates do not supply laws

On two labels with right-projection product x·y=y, every designated e is left
neutral and multiplication is total, associative and coherent. Choose e=0,x=1:
x·e=0 differs from x. Right insertion is not harmless. Left projection x·y=x is
the dual witness: e·x=e differs from x. These e are designated candidates, not
true units satisfying the two-sided IsUnit predicate. A weakened Empty interface
which accepts them therefore changes histories; the lawful raw interface rejects them.

## 7. Coherence and anchors are separate requirements

Table ((0,1),(1,None)) is strongly associative and has local unit 0. The local
endpoints of 1 match, but 1·1 is absent. Coherence fails; endpoint matching alone
would incorrectly admit this join. This is separate from associativity failures.

In the discrete two-unit category, Empty(A);Empty(B) with A≠B fails, whereas
Empty(A);Empty(A) succeeds. Deleting both anchors maps both words to[], losing the
distinction. Anchored identity-arrow flattening restores it. A nonunit Empty is
also rejected, even if its label is a present arrow.

## 8. Information controls and validation

A lawless isolated present arrow and an absent arrow can have the same all-None
padded table; this breaks carrier recovery when local units are removed. Under the
lawful premise it cannot occur. ENCODINGS §4 gives the independent object-map
collision and its paired-code repair. Coherent object/arrow permutations and valid
unit insertion are positive controls, never evidence of information loss.

Finite structural validation must reject malformed suffixes after semantic failure,
bool/int aliases, non-tuple trees and invalid map entries. These are API contracts,
not new mathematical axioms. The 16 fixed larger-category queries are separate
review evidence; their observed outcomes belong in REVIEW, not this prospective
control specification. General proof coverage belongs in FORMAL_SCOPE/FORMAL_REVIEW.
