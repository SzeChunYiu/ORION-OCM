# V19 roundtrips and operational information

Conventions and premises are in [THEORY_V19.md](THEORY_V19.md).

## S2.1 — from a lawful category to a partial operation

For any small category C on objects V, let A_C be the disjoint union
of Hom_C(a,b) over ordered pairs (a,b). A bundled arrow is (a,b,f).
Set (a,b,f)(c,d,g)=none if b≠c. If b=c, transport g along that equality
and return (a,d,f;g). Identity and composition are the actual operations of C.

For x:a→b,y:c→d,z:e→f, either bracketing is defined exactly when
b=c and d=e. In that case eliminating the two endpoint equalities reduces
its value equality to C's associativity; otherwise both Option values are none.
This proves strong partial associativity, including dependent transports.
The same matching conditions prove coherence. Bundled identities are units
and give every bundled arrow its local units by C's identity laws.

Conversely, if x=(a,b,f) is a unit, the product id_a*x is defined and equals
x by the category left-identity law. Right neutrality of x says this same
product equals the bundled id_a. Therefore x is precisely that identity.
Thus the units of A_C are exactly the bundled identities; endpoint uniqueness
gives l(a,b,f)=id_a and r(a,b,f)=id_b.

## S2.2 — changing-object category roundtrip

Reconstruct a category from A_C as in S1.4. The object map
j(a)=bundled id_a is injective because equality of bundles implies equality
of their source objects. It is surjective onto units by S2.1.
For each a,b, send f∈Hom_C(a,b) to its bundled arrow, considered as an
arrow from j(a) to j(b) in the reconstruction. Conversely take such a
reconstructed arrow (c,d,g). Its endpoint equations say id_c=id_a and
id_d=id_b; projecting the bundles gives c=a and d=b. Transport g along
those equalities to obtain an actual arrow of Hom_C(a,b).

Eliminating endpoint equalities proves that the two Hom maps are inverse;
proof irrelevance removes differences in stored endpoint proofs. On identities
the forward map gives the reconstructed identity j(a). On composition it
gives the reconstructed partial product, whose definition returns the bundle
of f;g. These are actual typed preservation equations, not only a bijection
of counts. This is an isomorphism with an explicit object bijection; the
object-fixing V11 CategoryIso alone would not express this result.
No nonemptiness assumption is used, so the empty-object category is included.

## S2.3 — partial-algebra roundtrip

For a lawful m on A, bundle the arrows of its reconstructed category.
Encode x as (l(x),r(x),x), with its endpoint proofs. Decode by forgetting
the two objects and proofs. Decoding an encoding is x. Encoding a decoded
bundle is the original bundle: its stored Hom endpoint equations identify
the object components, and proof irrelevance handles the proofs.

For encoded x,y, the new partial multiplication is defined iff their middle
objects agree, equivalently r(x)=l(y), equivalently Dxy by S1.3.
When xy=u its value is the encoding of u, by the reconstructed composition
definition and the composite endpoint laws. Otherwise both operations return
none. Thus the inverse maps preserve AND reflect the entire Option operation.
Surjectivity and reflected failures are essential; a mere multiplicative map
can send an identity to a nonidentity idempotent (control S4.5).

## S3.1 — actual query responses and arbitrary-length preservation

A raw query is either a nonempty list of arrows or Empty(e), where e is
any candidate arrow, including a nonunit. A singleton returns some(x).
A longer word uses the left-to-right Option fold of m; once a product fails,
its final response is none. Empty(e) returns some(e) exactly when U(e).
Every query has a tagged response; illegal words are not removed from the domain.

Let h:A→B be a bijection such that

    Option.map h (m(x,y)) = n(h(x),h(y)).

This transports the unit predicate in both directions. For example, take any
product n(h(e),b), write b=h(x) by surjectivity, and use operation reflection
and injectivity to transport defined neutrality; the self-product transports
likewise. The converse uses the inverse bijection. Induction over the word
suffix proves Option.map h commutes with its fold: the none branch propagates
failure and the some branch uses the displayed operation equation. Unit
transport gives the anchored-empty case. Therefore both S2 roundtrips preserve
responses for all finite lengths, not just the lengths in the finite corpus.
All prefix queries also belong to the raw interface; final failure does not
prevent querying an earlier successful or failed prefix separately.

## S3.2 — least sufficient information relative to this interface

Fix A and any class M of models on that carrier. Let T(M) be its partial
table and R(M) its complete response function. Define Build(t) by S3.1,
including the unit predicate derived from t. Define Extract(r)(x,y) as the
response to the length-two word [x,y]. By actual evaluation,

    R = Build ∘ T, and T = Extract ∘ R.

These identities need no category laws; they concern the declared evaluator.
Consequently for every encoding code:M→Z,

    Recoverable(code,R) iff Recoverable(code,T).

Here Recoverable is V9's decoder-on-the-attained-image notion. A decoder for
T followed by Build decodes R; a decoder for R followed by Extract decodes T.
Both composites are defined on exactly the same attained codes; there is no
need to assign values to unused codes or assume the target inhabited.
Equivalently, code collisions preserve all responses iff they preserve tables.

Order information by recoverability. Every response-sufficient encoding can
recover T, and T itself recovers R. T therefore represents the least sufficient
information equivalence class for this interface, up to mutual recoverability.
This is not a shortest encoding, a numerical count of primitive fields or a
signature-independent ontology. A coarser observation interface can identify
more tables. Conversely keeping only composability loses actual products, as
the C4/V4 control shows. Original R1 universal minimality remains unresolved.
