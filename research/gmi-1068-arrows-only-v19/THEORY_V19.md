# V19 theory — partial multiplication reconstructs typed processes

## S1.1 — declared primitives

Let A be any small set, possibly empty, and m:A×A→A⊔{none}.
Write xy=u for m(x,y)=some(u), and Dxy for existence of such a value.
Composition is written in execution order: x followed by y.
Define U(e) by ee=e and both neutrality clauses:
ex defined implies ex=x; xe defined implies xe=x.
The following are premises, not reconstruction conclusions.

(A) Strong partial associativity: (xy)z and x(yz), evaluated with failure
propagation, are equal as Option values. Thus their definedness agrees.
(L) Every x has e,f with U(e),U(f), ex=x and xf=x.
(C) Coherence: Dxy and Dyz imply D((xy),z).
No probability, reward, tensor, physical admission or computational effectiveness
is inferred from these three algebraic laws. Infinite constructions below may
use classical choice and equality decisions; the finite implementation computes them.

## S1.2 — unique endpoints

Suppose U(e),U(f), ex=x and fx=x. Applying (A) to (f,e,x), the
right-associated expression f(ex)=x is defined; hence fe is defined.
Neutrality of f gives fe=e, and neutrality of e gives fe=f. Therefore e=f.
If xe=x and xf=x, (A) on (x,e,f) similarly forces ef defined;
neutrality gives ef=f and ef=e. Right units are unique as well.
Let l(x),r(x) denote these uniquely determined units. For U(e), ee=e
makes e both its own endpoints; uniqueness gives l(e)=r(e)=e.
This argument uses (A),(L) and U, but not (C).

## S1.3 — exact matching and composite endpoints

If xy is defined, write f=r(x). Since xf=x, (A) applied to (x,f,y)
forces fy defined. Neutrality of f gives fy=y, so uniqueness gives f=l(y).
Conversely, if r(x)=l(y)=e, then xe=x and ey=y. Coherence applied to
(x,e,y) gives D((xe),y), which is Dxy. Consequently

    Dxy iff r(x)=l(y).

If xy=u, associativity applied to (l(x),x,y) gives l(x)u=u;
uniqueness gives l(u)=l(x). Applying it to (x,y,r(y)) gives ur(y)=u
and r(u)=r(y). These equations are statements about actual returned arrows,
not only about composability flags.

## S1.4 — actual reconstructed category

Take objects E={e∈A | U(e)} and Hom(e,f)={x∈A | l(x)=e and r(x)=f}.
The identity at e is the arrow e. Define composition of x:e→f and y:f→g
as the unique returned value u of m(x,y); S1.3 guarantees existence and
that u:e→g. The uniqueness here is ordinary functionality of m.
Neutrality proves both category identity laws. For x:e→f,y:f→g,z:g→h,
both triple products are defined by matching, and (A) proves their equality.
Subtype equality then proves the typed associativity equation. This constructs
all the fields and laws of the V11 Category interface from m.
If A is empty, E and every Hom are empty; all quantified laws hold and
no choice of an actual arrow or object is needed.

The converse and object-changing roundtrips are proved in
[ROUNDTRIPS_V19.md](ROUNDTRIPS_V19.md). Together they identify the retained
information; they do not make arbitrary partial magmas into categories.

## S1.5 — exact parent-premise mapping

The reconstruction mechanism and coherence distinction are classical:
Cranch–Doherty–Struth (2020), Sections 3–4, and Riccardi CAT_6.
Our U is a self-composing, two-sided conditional neutral element.
This is equivalent, under local existence, to the following side-specific
identity formulation: every x has a left-neutral e with ex=x and a
right-neutral f with xf=x. To prove the nontrivial direction, take any
left-neutral e and a local right-neutral f for e. Then ef=e by the local
right-identity condition, while left neutrality gives ef=f. Thus e=f,
so e is also right-neutral and ee=e. The symmetric argument handles f.
Conversely our U and (L) directly supply those side-specific identities.
No associativity is required for this particular equivalence.

The displayed v1 wording of Cranch–Doherty–Struth defines a unit as left
OR right neutral, and Definition 3.2 asks only for two such units with
appropriate products defined. Read literally, those clauses are weaker:
a two-element total right projection satisfies them but lacks right units.
[The exact control](CONTROLS_V19.md#s46--one-sided-parent-reading) records
this attribution precisely. We do not claim equivalence with that weaker
reading or import its uniqueness conclusion without our stronger premises.
Riccardi's side-specific left/right identity conditions provide the direct
premise match; its current online theorem numbers are recorded separately.

## Scope of the mathematical result

The complete derivations above and in the linked details are paper proofs
for arbitrary small carriers. The final formal review separately identifies
which actual constructions and equations the fresh Lean audit checks.
Finite enumeration is an independent calibration of the executable interface;
it cannot establish the arbitrary-carrier theorem by itself.
