# Semantic recovery and common-domain independence V9

This repairs the representation boundary in R1/R2; it does not prove a minimum
number of primitive symbols. The original R0 governance audit is a separate
claim. Its validation neither proves these theorems nor establishes full GMI.
Source ownership and actual reading scope are in [PARENTS_V9.json](PARENTS_V9.json).

## 1. Exact recovery on an attained image

Fix sets M,P,O and maps p:M→P and o:M→O. M is the declared model class;
p is the information retained and o is the quantity to recover. Define
I_p={v∈P | ∃m,p(m)=v}. Recovery means that a function d:I_p→O satisfies
d(p(m))=o(m) for every m, where p(m) carries its membership witness.

**Theorem 1 (fiber criterion).** Recovery holds iff
p(m)=p(n) implies o(m)=o(n) for all m,n.
Proof: substitute equal inputs in a decoder for necessity. For sufficiency,
choose a preimage m of v∈I_p and set d(v)=o(m). Fiber constancy makes the
answer independent of that choice. **Theorem 2 (uniqueness).** Any two correct
decoders agree on I_p, because every argument there is p(m) for some m.

The construction in Lean uses classical choice. It asserts existence, not
an effective inference algorithm, a learnable decoder, or a finite encoding.
If M is empty, I_p is empty and recovery still holds even when O is empty.
Extending d to all P requires a default value whenever P has unused values;
a nonempty O suffices. For example M=O=∅ and P={*} admits an image decoder
but no decoder P→O. Off-image values are neither uniquely determined nor
evidence for additional information.

**Corollary (obstruction).** One pair m,n with the same p and different o
refutes every uniform decoder on the declared model class. This is semantic
nonrecoverability; it is not probabilistic independence or causal autonomy.
A restricted model class can restore recovery by removing the collision.

## 2. Invariance under declared presentation translations

Let eM:M→M', eP:P→P', eO:O→O' be bijections, with
p'(eM(m))=eP(p(m)) and o'(eM(m))=eO(o(m)).
Then recovery of o from p is equivalent to recovery of o' from p'.
Transport an image decoder as d'=eO∘d∘eP⁻¹ on I_p';
commutation and surjectivity of eM ensure eP(I_p)=I_p'. The inverse
translations give the converse. Equivalently apply Theorem 1 to both diagrams.

The Lean theorem proves a slightly stronger sufficient transport statement:
eM need only be surjective and eP,eO injective, with the same commuting
equations. For forward fiber constancy, lift two M' inputs through eM, use
injectivity of eP, then transport equal outputs. Conversely, transport equal
p values and use injectivity of eO on the resulting output equality.
Thus the frozen bijective case is included, without assuming a decoder.

A bijection alone is insufficient if it fails to preserve the specified
observations. Arbitrary categorical equivalence or Morita equivalence is not
substituted for this commuting diagram. Those are broader, separately defined
notions of theory comparison. Computable transport additionally requires
effective encoders and the needed inverse on the attained image.

Lossless packing r(m)=(p(m),o(m)) recovers both components by projection.
This can reduce the number of record fields without removing information.
It is not a decoder of o from p; replacing r by just p loses information
precisely when Theorem 1 finds a collision. No syntax-count lower bound follows.

## 3. A fixed ambient process and two independent choices

Let C have objects 0,1, identities i0,i1 and two distinct arrows a,b:0→1.
Composition exists exactly for matching endpoints, and identities do nothing.
There are six composable ordered pairs: (i0,i0),(i0,a),(i0,b),
(a,i1),(b,i1),(i1,i1), using path order. All composable triples associate:
with only identities both brackets return the identity; otherwise there is
exactly one nonidentity arrow and both brackets return it.

For every U⊆{a,b}, the arrows {i0,i1}∪U form a wide subcategory C_U.
Identities are included; every possible composite is already one of its
factors. These are all four wide subcategories of C. In particular let
C_empty contain only identities and C_full contain all arrows.
These are supplied choices of admission within one shared ambient vocabulary,
consistent with V5's identity and composition closure criterion.

Let H be ALL finite composable paths of C, with a specified start object,
including a typed empty path at each object. H is the same set for every U.
A path is admitted by C_U iff each of its arrows belongs to C_U.
Evaluation is an external function on H; its domain does not shrink to
admitted paths. Thus the evaluator's type does not disclose U.

Every path has at most one a or b: after one such arrow the current object
is1, where only i1 can follow. Its ambient composite is i0 or i1 when there
is no nonidentity arrow, and otherwise that unique a or b. Consequently
admission is unchanged by inserting/removing identities and is determined
by the composite. Any arrow evaluator ν:C.arrows→W extends to H by ν∘comp.
These facts justify the finite implementation's four-arrow normal forms.
They do not identify arbitrary history-dependent evaluators with arrow maps;
duration, identity-count or path-sensitive objectives would need richer H data.

Take W={0,1}, ordered 0<1, and the TWO total ambient arrow evaluators
νA(i0)=νA(i1)=0, νA(a)=1, νA(b)=0;
νB(i0)=νB(i1)=0, νB(a)=0, νB(b)=1.
Extend both to the same H as above. Total maps are valid special cases of
partial evaluation; they can be wrapped in a VALUE constructor without
changing any argument. Undefined evaluation and nonadmission stay distinct.

**Countermodel A.** Hold C_full fixed. Under νA, a strictly beats b;
under νB, b strictly beats a. The process observations are identical and
the evaluation functions differ at the valid singleton history[a].
Theorem 1 rules out recovery of this objective from this process across
a model class containing both expansions.

**Countermodel B.** Hold literally the same H,νA and order fixed. Compare
C_empty and C_full. History[a] is forbidden in one and admitted in the other.
From start 0, attainable values are respectively{0} and{0,1}, and reaching
object 1 is respectively impossible and possible. Theorem 1 rules out recovery
of admission from this full fixed ambient context across those expansions.
Unlike the earlier state-value witness, equality here includes the evaluator's
entire declared domain.

The two-axis model class {C_empty,C_full}×{νA,νB} contains both collisions.
Lean's process and objective maps return the actual History→Bool functions,
not selector names. Typed histories use source/target checks, including empty
paths. The kernel also proves that no admitted identity-only history has
νA-value 1, and that[a] supplies an admitted full-process success witness.

## 4. Attainability and the observable comparison boundary

On C_full, both νA and νB have the SAME attainable value set{0,1}, although
their preferred labelled actions differ. Value-set membership answers a
capability question; selecting its witness needs the witnessed relation
{(h,ν(h)) | h admitted}, or the retained process/evaluator maps.
This supports the explicit qualification already present in original R3,
[THEORY_V1.md section R3-3](../gmi-1068-r3-contextual-attainability-v1/THEORY_V1.md);
it does not invalidate that qualified attainable-value construction.

The ambient automorphism swapping a,b carries νA into νB. Our question
concerns fixed, declared labelled interventions; translating the whole
observation diagram preserves the recovery verdict. Quotienting away those
labels changes the target being recovered and is not the same question.
This is why semantic independence requires specified observations and a
translation class, rather than an unrestricted claim about all presentations.

## 5. Identity symbol versus identity law

In a typed associative composition presentation, omit the named identity
operation but retain: at every object x there exists a two-sided unit e:x→x,
acting identically on every arrow into or out of x. If e,f are two such units,
e=e∘f=f. Thus each object has exactly one unit. Define id(x) to be that
unique arrow. Every model has a unique expansion by this identity operation;
forgetting the added symbol recovers the original model.

The identity symbol can therefore be explicitly defined without weakening
the unit requirement. The generic kernel lemma needs only a binary operation
on each endomorphism set; associativity is not needed for unit uniqueness.
The full typed expansion argument follows by applying it at each object.

Dropping unit existence/laws changes the model class. A one-object system
with two arrows{false,true} and composition x⋅y=false is associative, but
has no unit: e⋅true=false≠true for either e. Lean checks both claims.
This separates a removable name from indispensable structure for a chosen
empty-history semantics. It does not establish that every intelligence
formalism must start with a category or use a specified number of symbols.

## 6. Evidence level and precise scope

Kernel checked: fiber criterion, decoder uniqueness, collision obstruction,
commuting-translation invariance, unique units, associative nonunital model,
both fixed-domain nonrecoverability countermodels, actual ranking reversal,
and identity-only impossibility/full-process success over typed finite paths.
Paper proved: ambient category laws, all four wide subcategories, arbitrary
path normalization and its admission/evaluation factorization, typed identity
expansion, off-image extension boundary and value-set/witness distinction.

The executable corpus tests all 3^3 · 2^3 = 216 map pairs and independently
enumerates decoder assignments, plus the frozen finite category/context
checks. These analytic counts are design quantities, not an assertion of
successful execution; consult the generated receipt for measured outcomes.
Python is not kernel-certified code. No all-family derivation, empirical truth,
signature-independent minimality or finished process/context fixed point follows.
R1/R2 statements earned here are only these specified semantic subclaims;
R0 governance delivery is independently adjudicated by its successor audit.
