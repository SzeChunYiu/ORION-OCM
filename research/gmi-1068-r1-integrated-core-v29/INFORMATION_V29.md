# Common-family information and decoder accounting

## I1 — exact attained recovery
For model class M, representation z:M→Z and observation S:M→A,
Recoverable(z,S) means a decoder on attained(z) yields S(m).
Equivalently, z(m)=z(n) implies S(m)=S(n).
Necessity follows by applying the decoder to equal codes.
For sufficiency, each attained code has a representative; fiber constancy makes
its observation independent of that choice. No unused code needs a default.

For queries Q use the observation signature Sbar(m):q↦S(m,q).
This recovers every registered response jointly, not just each response under
a different unspecified representation.

## I2 — fixed-interface equivalence
Fix i:Q→R and injective j:A→B, independent of m.
Assume T(m,i(q))=j(S(m,q)) for all m,q.
Write Tbar(m)(q)=T(m,i(q)).
If Sbar is constant on z fibers, its fixed j-image Tbar is constant there.
Conversely equal Tbar signatures give j(S(m,q))=j(S(n,q)) for each q;
injectivity of j gives equality of Sbar. Apply I1 in both directions.

There is no injectivity premise on i. Repeated source queries may select the
same target query if the commuting equation holds.
This theorem concerns T restricted along i, not the full R-signature.
When responses are Option A, use the actual None-preserving Option.map j;
it is injective whenever j is injective, so failures retain their own tag.

## I3 — model-dependent encoders do not imply I2
Let M=Bool and Q be singleton. Source response is some(m), target response
always some(false). Let j_m(b)=xor(b,m), preserving None.
Each j_m is bijective and every individual square commutes.
Under a constant representation, the target signature is recoverable and the
source signature is not: the latter differs between the two models.
Thus pointwise category presentation equivalence cannot establish I2 by itself.

Retaining the actual j_m codebook restores the missing model distinction,
since j_m(false)=m in this example. Charging that retained information is
essential; it is not a compression improvement obtained for free.

## I4 — two further missing-premise controls
Let source(m)=m, j(0)=j(1)=0 and target(m)=0.
The square commutes, but the noninjective output map erases the distinction.
A constant code cannot recover source. Restoring an injective map repairs it.

Let Q be singleton, R have two queries, source constant0,
target(m)=(0,m), and i choose the first coordinate.
With fixed identity j, I2 holds for the restricted target.
The full target remains unrecoverable under constant codes.
No claim of full-target recovery is valid without an additional coverage or
determination theorem.

## I5 — registered executable comparison
F1 contains all81 two-model/two-query arrays over None,0,1.
F2 contains nine one-query seeds duplicated as two source queries, with repeated
i=(0,0). Two code arrays give180 reports in all.
Expected decoders are independently enumerated on attained observation codes,
not copied from production recoverability Booleans.
Full-target decisions are recorded separately from the360 source/restricted
decisions. Empty model/query domains and all-None zero-output arrays are valid.

This finite schedule checks adapter semantics. The family theorem is arbitrary
in M,Q,R and does not obtain generality from enumeration.
Information sufficiency is relative to the declared observations; no shortest
program, minimal coordinate storage, learned semantic meaning or runtime bound
is inferred.
