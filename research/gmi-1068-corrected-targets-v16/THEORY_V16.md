# Qualified target corrections: typed admission, composition and aggregation

Read FREEZE_V16 and its immutable TARGET_CONTRACT_V16. These are replacements
for two explicitly qualified historical readings, not fulfillment of false
original statements. Original R2-003/R2-007 remain UNKNOWN. Classical parents
retain ownership; no empirical or mathematical novelty is claimed.

## P1 — admission from a complete generated typed raw domain

Fix objects V, typed edge sets G(a,b), and predicates P(e) on those edges.
A raw path is an endpoint-indexed finite sequence of composable G-edges.
Define AllP(nil_a)=True and AllP(e::p)=P(e) and AllP(p).
The complete admitted raw source Raw(P)(a,b) consists exactly of paths p:a→b
with AllP(p). Evaluation may be partial on that source; its defined subdomain
is different data. A full context here retains Raw(P), not merely observed
samples or the subset where evaluation returned a value.

Let G_P(a,b)={e:G(a,b) | P(e)}. Define forget on paths in G_P recursively:
forget(nil_a)=nil_a and forget((e,h)::q)=e::forget(q).
Induction shows AllP(forget(q)); endpoints are unchanged by the constructors.
Thus forget maps Path(G_P)(a,b) to {p:Path(G)(a,b) | AllP(p)}.
Conversely, lift(nil_a,h)=nil_a; for e::p and h=(h_e,h_p), set
lift(e::p,h)=(e,h_e)::lift(p,h_p). This is well typed at every constructor.
Induction gives forget(lift(p,h))=p. A second induction gives
lift(forget(q),its AllP proof)=q; equality of proof-bearing edge subtypes follows
from equality of the underlying edges. These are inverse maps, not an assumed
identification. Their empty-path equations are definitional. Induction on the
first path proves compatibility with concatenation; the AllP witnesses combine
by the same recursion. Therefore the correspondence preserves the path-category
operations with their actual endpoint types.

For a typed edge e:a→b, single(e)=e::nil_b, so
`AllP(single(e)) iff P(e) and True iff P(e)`.
This is a decoder from the full raw-source predicate to edge admission.
If Raw(P)=Raw(Q), evaluating membership at each singleton gives P(e)↔Q(e),
hence equality of the admitted edge subsets. The fixed labelled ambient graph
and singleton encoding are essential to this comparison.

This is semantic information extraction. It does not discover physical laws or
decide an undecidable domain. Given an arbitrary callback L on paths, singleton
queries define a predicate P_L, but need not establish L=Raw(P_L): a callback
that accepts all empty/singleton paths and rejects a valid two-edge path fails
that equality. Exact generation by admitted edges is a premise of reconstruction.
No assertion is made that a context omitting its full source reveals admission.

**Assumptions.** Fixed typed graph/labels and singleton embedding; full source exactly AllP; evaluator partiality separately represented.
**Dependencies.** V11 typed paths, structural induction and subtype proof irrelevance; no physical inference assumption.
**Falsifiers.** Wrong endpoints, missing empty paths, a non-generated domain callback, or replacing the full source by the defined evaluation subset.
**Strongest parents.** [Riehl Example4.1.13](https://emilyriehl.github.io/files/context.pdf), free typed paths; the admission extraction and subtype correspondence are direct constructions at that classical interface.

## P2 — same nonconstant full context, different actual composition

Use one object and the fixed labels A={0,1,2,3}. C4 has operation
c(a,b)=(a+b) mod4, identity0. V4 has v(a,b)=a XOR b on their two-bit
representations, identity0. Modular addition is associative with unit0;
bitwise XOR is associative with unit0 in each bit. Both therefore give lawful
one-object categories on exactly the same labelled arrows. All raw words A*
are admitted and evaluated; the empty word evaluates to0.

Let π(a) be the low bit, interpreted as Bool with false≤true. For C4,
π(c(a,b))=π(a) XOR π(b): reduction modulo4 preserves parity, and the parity
of an integer sum is the XOR of its parities. For V4 the same equation is
the defining low-bit rule for XOR. Also π(0)=false.
Evaluate a word by folding the actual category operation from unit0.
Induction on the word, using these two homomorphism equations, proves
`π(eval_C4(w)) = XOR-fold(π(labels of w)) = π(eval_V4(w))`
for every finite word, not merely words in the calibration corpus.
The full contexts agree extensionally: same raw domain, total definedness,
Bool codomain/preorder and evaluated function. They are nonconstant, since
[] evaluates false while [1] evaluates true. No external evaluator label is
substituted for parity of the actual products.

The composition functions differ at (1,1): c(1,1)=2 but v(1,1)=0.
Their evaluation kernels also differ. C4 gives eval([1,1])=eval([2])=2;
V4 gives0 versus2, so these words are not kernel-equivalent there.
Consequently the process-dependent quotient-history sources cannot be silently
identified. Equal raw syntax and equal contextual values do not mean equal
product equality relations.

Take the two actual models as the model space M. Let contextObs return the
entire context tuple above and compositionObs return the actual binary table.
The proved all-word equality gives equal contextObs values; the (1,1) entry
gives unequal compositionObs values. Any decoder on attained context values
would output one composition at their common input, contradicting that difference.
This is precisely V9's generic collision theorem, applied to actual observations.
It establishes composition nonrecovery, while admission is identical and remains
recoverable by P1. No reverse-admission theorem is rescued by changing its name.

**Assumptions.** Shared labelled raw syntax/domain and identity; actual C4/V4 laws/folds; parity evaluated after each actual fold; shared Bool order.
**Dependencies.** Classical one-object group categories, parity homomorphisms, word induction and V9 collision.
**Falsifiers.** Unequal labels/domains, constant or supplied selector-only contexts, a false homomorphism, or identifying different evaluation-kernel quotients.
**Strongest parents.** [Stacks Example4.2.6](https://stacks.math.columbia.edu/tag/0013) and V9's classical fiber-factorization obstruction; the finite groups supply an explicit instance.

## P3 — finite basis representation and the exact probability-weight boundary

Let α satisfy the primitive ordered commutative ring laws of ScalarV12,
including0<1. Let n be any finite natural number, including0. For
F:α^n→α assume F(x+y)=F(x)+F(y) and F(c*x)=c*F(x) for every x,y,c.
The domain is all vectors and homogeneity is for all α-scalars. Define e_i
as the coordinate basis and w_i=F(e_i).

First F(0)=0: additivity gives F(0)=F(0)+F(0), then additive cancellation
removes one F(0). Induction extends additivity to finite sums, starting at0.
Coordinatewise evaluation gives v=Σ_i v_i e_i because each coordinate has one
nonzero basis contribution. Applying finite additivity and scalar homogeneity,
`F(v)=Σ_i F(v_i e_i)=Σ_i v_i F(e_i)=Σ_i w_i v_i`.
If coefficients u also represent F on every vector, substituting each e_i
gives u_i=F(e_i)=w_i; representation is unique, including the empty family.

If F is coordinatewise monotone, 0≤e_i implies0=F(0)≤F(e_i)=w_i.
Conversely, suppose every w_i≥0 and x≤y coordinatewise. Each y_i-x_i≥0,
so w_i(y_i-x_i)≥0. A finite sum of nonnegative terms is nonnegative, hence
F(y)-F(x)≥0 and F(x)≤F(y). Thus monotonicity is equivalent to nonnegative
coefficients, under the stated linearity. Substituting the all-ones vector
gives F(ones)=Σ_i w_i, so normalization is exactly Σ_i w_i=1.
Conversely a fixed weighted sum is additive and homogeneous by distributivity;
nonnegative coefficients with unit sum make it monotone and normalized.
For n=0, ones is the empty zero vector, so a linear F gives0 and cannot be
normalized to1. Zero coefficients are valid; strict positivity is unnecessary.

These steps use only primitive scalar laws and finite induction. They apply
on paper to ordinary real and rational carriers. The kernel's actual Int
instance demonstrates consistency; it does not implement arbitrary real or
rational scalar laws. In the Int instance nonnegative unit-sum coefficients
are highly restricted, which does not restrict the generic conditional theorem.

Extracting F(e_i) is not a test of universal linearity. With n=2 and
w=(1/2,1/2), let J(v)=w·v+v0*v1*(v0-v1)^2. Its nonlinear term vanishes
at each basis vector and at ones. But J(e0+2e1)=7/2, whereas
J(e0)+J(2e1)=3/2. A basis/ones-only check therefore accepts an impostor.
For n=0 an arbitrary function returning1 at the empty vector is likewise
normalized but not linear. Finite samples cannot replace the universal premises.

**Assumptions.** Full finite vector domain, primitive ordered ring, actual additivity and full scalar homogeneity; monotonicity/normalization are separately characterized.
**Dependencies.** Finite basis expansion and sum laws; V12 scalar primitives and V5's existing paper boundary.
**Falsifiers.** Omitted homogeneity, a restricted profile domain, negative weights, nonunit total, empty-dimension normalization or nonlinear basis impostors.
**Strongest parents.** Classical coordinate-basis linear algebra; [V5 R2-B](../gmi-1068-foundation-repair-v5/THEORY_V5.md) already gives the real theorem. This round mechanizes its declared algebraic assumptions.

## P4 — nonlinear aggregation retains declared choices without fixed weights

On real pairs set L(v)=min(v0,v1), U(v)=max(v0,v1). If x≤y coordinatewise,
each coordinate of y is at least min(x), so L(x)≤L(y). Each coordinate of x
is at most max(y), so U(x)≤U(y). Swapping coordinates leaves both unchanged;
constant inputs (t,t) produce t. Thus both are monotone, symmetric and preserve
constants. For p=(2,0),q=(1,1), L(p)=0<1=L(q) but U(p)=2>1=U(q).
These properties and profiles do not select a unique ranking.

Neither equals one fixed weighted sum on all real pairs. Such a sum is additive.
L(e0)=L(e1)=0, yet L(e0+e1)=1. U(e0)=U(e1)=1, yet U(e0+e1)=1 rather than2.
This refutes the fixed-linear-weight reading, not the necessity of specifying
an aggregation functional. Min/max can themselves be expressed by extrema over
a declared set of weights; no theorem excludes such broader interpretations.
The meaning of 'measure/weighting' must therefore remain explicitly qualified.

**Assumptions.** Ordinary real order and arithmetic; a fixed weight vector independent of the profile when asserting weighted-sum representation.
**Dependencies.** Elementary min/max calculations; V5 Nat reversal/nonadditivity are separately replayed exact instances.
**Falsifiers.** Profile-dependent weights disguised as a fixed vector, missing additivity, or presenting Nat computation as a general Real kernel theorem.
**Strongest parents.** [V5 R2-A](../gmi-1068-foundation-repair-v5/THEORY_V5.md); [Legg–Hutter §3.3](https://arxiv.org/html/0712.3329v1) supplies a declared weighted comparison specialization, not a universal aggregation representation theorem.

## Authority and evidence

The frozen revision IDs are GMI2-R2-003@r1 and GMI2-R2-007@r1. Their statements
and changed assumptions/observables are fixed by TARGET_CONTRACT_V16.
The additive ledger preserves the original claims, qualified refutations and
all revision/attestation/retraction history. A verified replacement is never
original fulfillment. Original accounting remains18 fulfilled/204 unresolved;
only verified replacements separately reduce active unresolved work.
Exact kernel coverage is recorded in FORMAL_SCOPE/FORMAL_REVIEW; bounded
Fraction/path/word calibration and independent diagnostics are separate evidence.
No physical admission oracle, canonical objective, fixed universal prior,
complete context classification or complete GMI theory follows.
