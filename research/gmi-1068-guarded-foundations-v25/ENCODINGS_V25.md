# Commuting encodings and named object information

## 1. Tree transport lemma

Suppose arrow maps f:A→B and object maps g:O→Q commute with identities and partial
multiplication: f(id_o)=id'_(g(o)), and
m'(f(x),f(y))=Option.map f (m(x,y)). Map both types of tree leaves and preserve Seq.
Structural induction gives T'(map(g,f,t))=Option.map f(T(t)). Leaves use the two
binding equations; Seq uses commutation of Option.map with bind and multiplication.
If f,g are bijective with inverse commuting maps, the inverse equation proves
reflection as well as preservation. A None result therefore cannot become a success.
No equality of untransported external names is asserted.

## 2. Actual category roundtrips

V19 proves actual object↔true-unit and bundled-arrow↔reconstructed-arrow bijections,
with identity and partial-product equations in both directions. Instantiating §1
with those maps proves tree observer roundtrips, including Empty and failed joins.
For a reconstructed category, unpacking an arrow gives its original carrier label;
unpacking an object gives its true-unit label. The resulting raw tree observer
agrees with the unpacked reconstructed-category response, by the same induction.
The matching of endpoints is earned by V19's defined-iff-matched theorem, not a
comparison of finite object counts.

A coherent renaming of both object and arrow labels is a positive control. Keeping
raw names fixed while altering only their meaning asks a different observational
question; it is not a counterexample to the commuting transport theorem.

## 3. Named presentations and exact paired recovery

Fix ambient arrow labels L and object names O. A NamedPresented is a Presented L
with i:O→L landing in the actual true padded units. Define N(Arrow x) by the raw
membership rule; N(Empty o)=some i(o); Seq binds through padded p.
All these equations also follow by mapping Empty leaves through i into the raw
observer. For complete category presentations require i bijective onto all units.
The recovery theorem below needs only the stated unit-landing premise.

For any two named presentations on fixed O,L, N=N' iff (p,i)=(p',i').
Forward: Empty(o) extracts i(o), while Seq(Arrow x,Arrow y) extracts p(x,y).
Reverse: equal p determines equal S by Y2a, equal units, and equal binary operation;
equal i gives equal empty responses. Structural induction gives equality on all
named trees. V9's attained-fiber criterion now yields, for any family and any code,
Recoverable(code,N) iff Recoverable(code,(p,i)).
Recovering the pair does not require independently stored map bits when an additional
application convention already determines the map from the table. The theorem concerns
recoverability of both observables, not a storage lower bound.

This statement includes empty O or L. A complete category with no arrows has no
objects; the general unit-landing interface can use O empty and nonempty carrier.

## 4. Same-table collision and revival

Take L={0,1} with discrete product p(0,0)=0,p(1,1)=1, off-diagonal None.
Use O={A,B}. Both i(A)=0,i(B)=1 and j(A)=1,j(B)=0 are bijections onto all units.
The table and carrier agree, but Empty(A) observes 0 in one and 1 in the other.
Thus code=p alone cannot recover named observation across this two-model family.
Adding the actual identity map separates the collision, and §3 provides the decoder.

The raw-unit observer remains recoverable from p alone because its Empty(0) query
already names the unit label, not the external name A. Neither result contradicts
the other. Replacing the paired theorem by table-only recovery would erase a
registered observable. The category specialization gets its actual encoder and
bijection from V19, rather than assuming externally chosen names are canonical.

## 5. Finite scope

Python NamedPresented enforces a bijection onto every actual unit, a stronger
premise than the general named theorem. Its named_eval translates object anchors
through that checked tuple; named_word uses the same mapping and actual guarded
fold. Its finite paired signature retains both the padded rows and ordered map.
Validation checks unused map entries too. Equality of finite fiber signatures is a
finite certificate, not a proof of arbitrary encodings or an identity-map inference.
