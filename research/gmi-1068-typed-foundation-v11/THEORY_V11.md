# Typed sequential foundations V11

Read FREEZE_V11.md first. This repairs three original law/independence
requirements, not the whole process/context programme. All constructions are
classical parent mathematics; the contribution is exact claim placement and
checked integration. PARENTS_V11.json gives the sources and reading locations.

## 1. Constructed paths and category laws

Let O be any set of objects and G(A,B) any set of individually identified
edges from A to B. Define Path_G(A,B) inductively: nil_A:A→A and, for
f:G(A,B), p:Path_G(B,C), the path cons(f,p):A→C. No edge finiteness,
acyclicity, decidable equality or uniqueness between endpoints is assumed.
Every path is finite. Parallel edges and repeated occurrences remain distinct.

Write p;q for concatenation in execution order. Define nil;q=q and
cons(f,p);q=cons(f,p;q). The constructors show by induction that p:A→B and
q:B→C yield p;q:A→C. Thus endpoint preservation is built into the operation,
not inferred from an untyped list after composition.

**T1.** Concatenation is associative and nil is a two-sided identity.
Left unit is the first defining equation. Right unit follows by induction:
nil;nil=nil; if p;nil=p then cons(f,p);nil=cons(f,p;nil)=cons(f,p).
For associativity induct on p. The nil case reduces both sides to q;r.
For p=cons(f,p'), the two sides reduce to cons(f,(p';q);r) and
cons(f,p';(q;r)); the induction hypothesis identifies them.
These operations therefore define a category on O. Empty O is permitted.

## 2. Universal interpretation, with target laws explicit

Fix a lawful category C, an object assignment F:O→Ob(C), and typed edge
maps j:G(A,B)→C(F(A),F(B)). C's associativity and both unit laws are
premises. Define E(nil_A)=id_F(A) and E(cons(f,p))=j(f);E(p).
This definition produces a well-typed arrow for every path.

**T2.** E preserves identities and concatenation, extends j, and is the
unique functor with these object and generator assignments.
Identity preservation is definitional. Induct on p for E(p;q)=E(p);E(q).
The empty case is C's left unit law. In the cons case apply the induction
hypothesis and C's associativity. The singleton [f]=cons(f,nil) evaluates
to j(f);id=j(f) by C's right unit law. If another functor K has these
assignments, then K(nil)=id and
K(cons(f,p))=K([f];p)=j(f);K(p); induction gives K(p)=E(p) for every p.
This is uniqueness after fixing all generator images, not a unique choice
of those images or a claim that interpretation is injective.

Riehl Example4.1.13 supplies the free-category/universal-extension parent.
Its target laws are assumed here exactly as in that construction.

## 3. Typed congruence quotients

For each pair A,B let ~ be an equivalence relation on Path_G(A,B), and
assume p~p' and q~q' imply p;q~p';q' whenever the endpoints match.
Define Q(A,B)=Path_G(A,B)/~, with identity [nil_A] and composition
[p];[q]=[p;q]. Equivalence makes the quotient sets meaningful; congruence
makes composition independent of representatives.

**T3.** These operations make Q a category, and the quotient map is a
functor fixing objects. Choose representatives p,q,r. Associativity is
[(p;q);r]=[p;(q;r)] by T1, and either unit equation similarly reduces to
T1. The operations were defined by representatives, so the quotient map
preserves them. The argument covers all classes by quotient induction.

If E(p)=E(p') whenever p~p', define Ebar([p])=E(p). This is well defined;
T2 gives both preservation equations. Every class is represented by a path,
so this factorization is unique. This is the same-object congruence quotient
of Awodey Definition4.12 and Theorem4.13, not a quotient identifying objects.

Congruence cannot be omitted. In the one-object free category on a,b, let
~ identify only singleton a with singleton b and otherwise use equality.
This is an equivalence relation. But a;a and b;a are different singleton
classes, so composing the identified classes depends on representatives.

## 4. Coverage of arbitrary lawful extensional cores

Let C be any small category, and let U C be its underlying typed graph,
including every arrow as an edge. Interpret objects and edges identically.
The evaluator E:Path(U C)→C of T2 is onto every Hom: E([f])=f.
Define p~q iff E(p)=E(q), separately on each endpoint pair. Equality gives
an equivalence relation; T2 implies composition stability, hence T3 applies.

**T4.** Path(U C)/ker(E) is isomorphic to C, fixing objects.
Define L([p])=E(p) and R(f)=[[f]], where the outer brackets denote a
quotient class and the inner brackets a singleton path. L is well defined
by the definition of the kernel. L(R(f))=E([f])=f. Conversely,
R(L([p]))=[[E(p)]]=[p], since E([E(p)])=E(p).
Both maps therefore are inverse on each Hom, with identical object maps.
L preserves identities/composition by T2 and the quotient construction.
R(id)=[nil] because their evaluations are id; and
R(f;g)=R(f);R(g) because evaluation of [f;g] and of [f];[g] is f;g.
Thus these inverse maps are functors, establishing an isomorphism rather
than merely equal cardinalities or an unspecified equivalence.

An involution g≠id with g;g=id illustrates why the quotient is essential.
In free paths length(p;q)=length(p)+length(q); an invertible path therefore
has length zero and is an identity. A nontrivial one-object group cannot
itself be a free path category. Its extensional equations are recovered by
T4. Awodey Corollary4.14 and Example4.15 supply this standard distinction.

## 5. Admission and presentation boundaries

T4 covers lawful categorical cores. It does not prove every physical
substrate already has adequate objects, associative operations or empty
no-change processes. These are the representation premises being declared.

V5 proves the exact unchanged-object restriction criterion: inherited
operations on admitted arrows form a category iff every identity is admitted
and admission is closed under composable composition. A one-object additive
cost model restricted to costs at most one fails: cost-one arrows are admitted
but their composite is not. Free completion of those admitted generators
would introduce forbidden runs and is not an admission-preserving repair.

Under zero identity cost and additive natural-number composition cost, V5
instead constructs objects (A,r) and arrows f:(A,r)→(B,s) with r=c(f)+s.
Sequential resource accounting makes composition lawful and projects exactly
to affordable runs. This is an explicit change of objects, not proof that
an arbitrary admission predicate closes. History-dependent and non-prefix
acceptance conditions need their own declared state/terminal semantics.

V9 proves two-sided units unique where they exist. Omitting a named identity
symbol while retaining unit existence does not remove this structure.
Neither T1–T4 nor these observations establish a primitive-symbol minimum.

## 6. Existing process/context collision

Use V9's common category: objects 0,1; identities i0,i1; distinct a,b:0→1;
composition only with matching endpoints and identities. All arrows are
admitted. The domain H consists of every finite typed path with its start,
including empty paths; H is identical for both expansions.

Use the ordered set 0<1 and total arrow evaluators
vA(i0)=vA(i1)=0, vA(a)=1, vA(b)=0 and
vB(i0)=vB(i1)=0, vB(a)=0, vB(b)=1. Extend to H by composition.
Every typed path contains at most one nonidentity arrow, so this agrees
with testing whether that path contains a, respectively b. Both are valid
special cases of the original partial evaluation into a preordered codomain.

**T5.** Process laws do not uniformly determine a context over any model
class containing these two expansions. Indeed, every retained process
component is equal but evaluation at [a] differs. If a decoder from process
data recovered both evaluators, its one common input would have to yield
both different functions, a contradiction. Moreover [a] strictly outranks
[b] under vA and strictly underperforms it under vB; thus the witness
concerns actual rankings, not merely different names for evaluators.

This is original R2 freeze target2 exactly: an explicit countermodel to
unique determination. It does not say every restricted model class lacks a
decoder, that process and context are probabilistically independent, or that
an objective cannot be externally supplied. Fixed labelled interventions
are the target; quotienting away their labels changes that target.

## 7. Evidence levels and adjudication

TypedPathsV11.lean and QuotientPathsV11.lean prove T1–T4 at arbitrary typed
graph/category scope; consult FORMAL_SCOPE_V11.md for exact declarations.
The auxiliary general quotient factorization/uniqueness in section3 remains
paper-only; Lean implements its evaluation-kernel specialization.
V9 RecoverabilityV9.lean proves the general fiber criterion, the actual
countermodel and ranking reversal supporting T5. Python independently
reproduces the disclosed finite diagnostics; it is not kernel-certified code.
The 182 histories through length12, 156 differing values, 26 identity-only
histories and 36 padded rank reversals were already explored before V11.
They are reproduced evidence, not prospective predictions or universal tests.

ADJUDICATION_V11.md maps only the three frozen original atoms to these
proofs. General proofs, finite corpus and independent review are distinct
conditions; consult the generated receipt for measured results. R1/R2 remain
open. No all-family intelligence derivation, empirical truth, novelty,
unique ontology, universal minimality or full GMI follows.
