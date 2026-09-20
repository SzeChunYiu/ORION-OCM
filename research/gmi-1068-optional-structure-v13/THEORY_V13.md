# Optional parallelism and symmetry: precise obstructions

Read [FREEZE_V13.md](FREEZE_V13.md) first. These are classical mathematical
countermodels and a replay of existing general proofs, not empirical discoveries.
The process category and its equality remain fixed when testing existence of tensor.
Write `f*g = g∘f`: execute f first, then g. Tensor, when postulated, is `⋄`.
The original atom dispositions are in [ADJUDICATION_V13.md](ADJUDICATION_V13.md).

## M1-A — an actual noncommutative process category

On the two-element set B={0,1}, let e(b)=b and z_i(b)=i. Put M={e,z_0,z_1}.
These are distinct functions: e differs from z_0 at 1 and from z_1 at 0;
the two constants differ at either input. Their complete multiplication is:

| * | e | z_0 | z_1 |
|---|---|---|---|
| e | e | z_0 | z_1 |
| z_0 | z_0 | z_0 | z_1 |
| z_1 | z_1 | z_0 | z_1 |

The table follows by actual function composition, hence proves closure.
For every f,g,h and b, both `(f*g)*h` and `f*(g*h)` send b to h(g(f(b)));
e is the two-sided identity. Thus one object B with Hom(B,B)=M is a category C.
The only invertible arrow is e: every composite with a constant factor is constant,
whereas e is not constant. Conversely e is its own inverse.
Finally z_0*z_1=z_1 differs from z_1*z_0=z_0.

**Assumptions.** Two distinct bit values, extensional function equality, exactly M as arrows.
**Dependencies.** Function composition; displayed exhaustive table.
**Falsifiers.** Nonclosed composition, collapsed reset maps, or a nonidentity invertible arrow.
**Strongest parents.** Ordinary categories and monoids; [Riehl E.2](https://emilyriehl.github.io/files/context.pdf) supplies the enrichment definition, not a GMI novelty claim.

## M1-B — common-unit interchange forces equality and commutativity

Let * and ⋄ be any two binary operations on any carrier, with common two-sided
unit e, and suppose `(a*b)⋄(c*d)=(a⋄c)*(b⋄d)` for all a,b,c,d.
Then, for all a,b,

`a⋄b = (a*e)⋄(e*b) = (a⋄e)*(e⋄b) = a*b`,

`a⋄b = (e*a)⋄(b*e) = (e⋄b)*(a⋄e) = b*a`.

Thus the operations coincide and are commutative. This argument does not assume
associativity of either operation; the category application supplies it for *.
The quantification is over every operation satisfying the premises.

**Assumptions.** Both two-sided units agree; the full interchange equation holds.
**Dependencies.** Only the two displayed substitutions.
**Falsifiers.** Missing a unit side or interchange invalidates this inference; testing one proposed tensor is insufficient.
**Strongest parents.** [Baez, Week 258](https://math.ucr.edu/home/baez/week258.html), discussion of End(I) and Eckmann–Hilton; classical mechanism unchanged.

## M1-C — C admits no monoidal structure, including weak unitors

Suppose a monoidal structure exists on the unchanged category C. There is only
one object, so the tensor unit I and all tensor objects must be B. A tensor
bifunctor therefore induces some operation ⋄:M×M→M on arrows.
Its unitors λ:I⊗B→B and ρ:B⊗I→B are isomorphisms in M, hence both equal e
by M1-A. This derives their identity values; strict unitors were not assumed.
Unitor naturality gives, for every f in M,

`(e⋄f)*λ = λ*f`, and `(f⋄e)*ρ = ρ*f`.

Substitution of λ=ρ=e and the sequential identity laws gives e⋄f=f=f⋄e.
Bifunctoriality gives exactly the interchange equation of M1-B, since a pair
of arrows composes componentwise. M1-B would make * commutative, contradicting
M1-A. Thus there is no monoidal structure on C. This excludes every possible
arrow tensor and every possible weak coherence datum on the fixed category.
Associator, pentagon and triangle laws need not be tested: necessary unitor
and bifunctor laws already contradict the actual arrow compositions.
A monoidal enlargement with new objects or arrows is a different category.

**Assumptions.** Standard monoidal category definition with invertible natural unitors; C is unchanged.
**Dependencies.** M1-A, M1-B; unitor naturality and bifunctor composition preservation.
**Falsifiers.** A purported escape must preserve the exact carrier and exhibit genuine two-sided inverse unitors and all naturality/interchange laws.
**Strongest parents.** [Riehl E.2, pp255–256](https://emilyriehl.github.io/files/context.pdf) and [Baez's End(I) argument](https://math.ucr.edu/home/baez/week258.html); the reset category specializes this classical obstruction.

## M2-A — a lawful tensor need not admit braiding

Let D be the discrete category with objects M: Hom(x,y) is a singleton if x=y
and empty otherwise. The only arrow at x is id_x; composition is forced.
Define x⊗y=x*y, and id_x⊗id_y=id_(x*y), with unit object e.
This is a bifunctor: every composable pair consists of identities, which it
preserves. Object associativity and unit equalities follow from M1-A; on arrows
both sides are the unique identities. Take associators and unitors to be these
identity arrows. Naturality, pentagon and triangle diagrams commute because
all their parallel arrows are the unique identities. Hence D is strict monoidal.
Any braiding, even without imposing its hexagon or symmetry law, needs a
component z_0⊗z_1→z_1⊗z_0. This is an arrow z_1→z_0, whose hom-set is empty.
Therefore this particular lawful tensor has no braiding and consequently no symmetry.

**Assumptions.** Tensor on objects is the displayed noncommutative monoid product; D is discrete.
**Dependencies.** M1-A; the component type required of any braiding.
**Falsifiers.** Object collapse or an added cross-object arrow destroys this empty-hom witness.
**Strongest parents.** [Riehl E.2, pp255–256](https://emilyriehl.github.io/files/context.pdf), discrete monoid construction and coherence data; here the monoid is deliberately noncommutative.

## M2-B — the obstruction persists with nonidentity processes

Let E=D×BC2. Its objects can be identified with M. Hom_E(x,y) is empty for
x≠y, and consists of bits p∈{0,1} for x=y. Identity is 0 and composition
is XOR, written ⊕. XOR associativity and unit 0 prove category laws; each
loop 1 is nonidentity and is its own inverse.
Set x⊗y=x*y and `(x,p)⊗(y,q)=(x*y,p⊕q)`. Identity preservation is 0⊕0=0.
For composable loops p,p' at x and q,q' at y, functoriality reduces to

`(p⊕p')⊕(q⊕q') = (p⊕q)⊕(p'⊕q')`,

which follows from associativity and commutativity of XOR. Tensor associativity
on objects is that of M and on arrows is that of XOR. Tensoring with the unit
object e and its identity 0 preserves each object and arrow. Choose associators
and unitors to be loop 0. Their naturality follows from these arrow equalities;
pentagon and triangle paths are composites of zeros and hence agree.
Thus E is strict monoidal with genuine nonidentity arrows. Nevertheless,
Hom_E(z_1,z_0) is still empty, excluding a braiding for the registered tensor.
As a separate no-alarm control, BC2 alone has XOR as both composition and
tensor, identity unitors/associator, and identity braiding: the same XOR laws
verify naturality and all coherence equations. Nonidentity loops alone cause
no obstruction. Neither M2 result rules out alternative tensors on D or E.

**Assumptions.** Exact object set M; loops C2; no cross-object arrows; registered tensor above.
**Dependencies.** M1-A, XOR abelian group laws, standard monoidal/braiding data.
**Falsifiers.** A failed typed functoriality/coherence equation, or a claimed braiding component in an empty hom-set.
**Strongest parents.** [Riehl E.2](https://emilyriehl.github.io/files/context.pdf); product and discrete category constructions adapted explicitly, without empirical or novelty promotion.

## M3 — universal category-law scope and its mechanization

The original R1 freeze result 7 asks to mechanize universal category-law
consequences. V11 supplies arbitrary endpoint-indexed finite paths in any typed
graph, including empty graphs, parallel generators and loops. Concatenation
is associative with empty paths as identities, proved by structural recursion.
For any lawful target category and typed generator assignment, recursive path
evaluation preserves identities/composition; induction on paths proves uniqueness.
Any typed congruence stable under concatenation gives a quotient category:
changing representatives preserves a composite, so path laws descend.
For any lawful small category C, evaluate paths over its underlying graph.
Every arrow is the value of a singleton path. Quotient by equality of evaluation;
the induced evaluator and singleton map are inverse and preserve identities
and composition. Thus Path(U C)/ker(eval) is isomorphic to C fixing objects.
This covers all such categories, rather than assuming every process category is free.
V11's exact registered types include the constructed path laws, eval_unique,
eval_append, presentationIso, lower_quote, quote_lower and both maps' identity
and composition preservation. V13 must replay those registrations with their
actual source bindings; existence of declaration names is insufficient.

**Assumptions.** Well-typed graph; a lawful target category when interpreting paths; an actual typed congruence for quotienting.
**Dependencies.** V11 constructive proofs and exact kernel registrations; source laws are constructed, target laws are explicit premises.
**Falsifiers.** Noncomposable concatenation, noncongruence quotient, an invalid inverse/law equation, or a weakened theorem passing registration.
**Strongest parents.** [Riehl Example4.1.13, p137](https://emilyriehl.github.io/files/context.pdf), [Awodey chapter4, pp73–76](https://pages.jh.edu/rrynasi1/NewFoundations4Math/Literature/Textbooks/Awodey2016CategoryTheory.LectureNotes/notes/chap04.pdf), and V11's exact realization.

## Boundaries and evidence interpretation

The category countermodels invalidate universal tensor/symmetry necessity in the
registered mathematical class. They do not show that useful physical parallelism
is impossible, or that these tiny categories recover any AI architecture.
V5 still requires admitted identities and composition closure; syntax completion
cannot silently create physically forbidden executions. Process adequacy,
absolute primitive minimality, stochastic and higher-cell necessity remain separate.
The finite exhaustive tensor search checks necessary equations; the general
paper/Lean obstruction establishes the universal quantifier over arrow tensors.
General monoidal-category-to-WeakTensorData extraction remains a paper argument.
The M2 Lean modules prove typed composition/tensor laws, structural inverses,
unitor and associator naturality, pentagon, triangle and the empty-hom obstruction
for the C2 product; the discrete model has unique parallel arrows. Identifying
these concrete data with the standard bundled monoidal-category definition is
paper-level. Exact kernel registration and FORMAL_SCOPE_V13 delimit that evidence.
CLOSED dispositions require all frozen receipts and independent checks; this
document by itself is not a test result or a declaration of complete GMI.
