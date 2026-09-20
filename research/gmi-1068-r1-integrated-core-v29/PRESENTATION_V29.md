# Evaluation-kernel presentation

## P1 — interpretation and quotient
Let G:O→O→Type be a typed graph and C a category on O.
Choose e:G(a,b)→C(a,b). For a path p define E recursively by
E(nil_a)=id_a and E(p appended q)=E(p);E(q), with E(single g)=e(g).
Existence follows by recursion. Any interpretation respecting these equations
agrees on all paths by induction. Laws of C justify reassociation.

For p,q with the SAME endpoints put p~q iff E(p)=E(q).
Reflexivity, symmetry and transitivity are equality laws. If p~p' and q~q',
functoriality gives E(pq)=E(p)E(q)=E(p')E(q')=E(p'q').
Thus composition [p][q]=[pq] is independent of representatives.
The empty class is the identity, and quotient induction transfers path laws.
This is the actual V11 typed congruence construction; no cross-Hom quotient.

## P2 — faithful lower and generated inverse
Define L[p]=E(p). Equality of representatives modulo the kernel makes L
well-defined. Its identity/composition equations are exactly those of E.
If L[p]=L[q], kernel equality gives [p]=[q]; L is faithful without generation.

Assume for every f:C(a,b) there is a typed path p with E(p)=f.
Define K(f) as the class of any such path. It is independent of the choice:
two witnesses evaluate to f, hence have equal classes.
L(K(f))=f by its witness; K(L[p])=[p] by kernel equality.
To prove K(id)=id and K(fg)=K(f)K(g), apply injective L and its laws;
the resulting equalities hold in C. Thus K is a functor inverse to L.
This proof is classical if witnesses are selected without an effective algorithm;
it does not promise a computable generating-word search.

For G=C.Hom with e(f)=f, choose single(f). This is V11 ownKernel/presented.
For the three-generator DAG use the generic evaluation kernel instead.
Identity loops in C.Hom make the ownKernel graph different from that finite DAG.

## P3 — observer and tree roundtrips
L and K fix objects, so their object maps are injective.
The V26 raw-response theorem applies in both directions to the V25 observer.
Mapping a tree along L and then K returns the original quotient-arrow tree:
induct on its Empty, Arrow and Seq constructors, using K(L(f))=f.
The other tree roundtrip uses L(K(f))=f similarly.
Responses therefore correspond, including empty anchors and failed joins.

This inverse is on quotient arrows. It cannot recover the original raw path
from its evaluated arrow: in the fixture single(c) and a appended b differ
as paths but agree as classes. A chosen representative is not a raw-path inverse.

## P4 — exact finite refinement
The target has objects0,1,2 and the six arrows ordered lexicographically by
endpoints: id0,a,c,id1,b,id2. The seven graph paths include the three nil paths.
Parent enumeration determines class IDs; L explicitly relates those IDs to
target-arrow indices. Do not equate these numeric orders.

Independent endpoint chaining verifies every generator/path image, all path
pairs and all quotient products. Omit b to exhibit faithful but non-surjective
L. Reverse target-arrow labels to defeat an identity-map shortcut.
An empty category is valid. A cyclic graph still has valid finite input paths;
only the finite DAG enumeration API rejects cycles.
No finite enumeration is substituted for the arbitrary-graph theorem.
