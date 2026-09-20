# V18 — reference-machine families

Scope and custody: [FREEZE_V18](FREEZE_V18.md). Context specializations and
resource theory are proved in [CONTEXTS_V18](CONTEXTS_V18.md).
Parent ownership and falsifiers are recorded per result in [PARENTS](PARENTS_V18.json).
All infinite sums and Real arguments in this file are paper proofs.

## Definitions and fixed semantics

A programme is a finite binary word. A prefix machine U is a partial computable
function from programmes to finite binary output strings whose successful domain
is prefix-free. Undefined execution includes divergence. A universal prefix
machine can simulate any prefix machine V using a fixed compiler prefix d_V:
U(d_V p)=V(p), including undefinedness. This suffices for the usual additive
programme-length overhead; nothing here computes shortest programmes.
Fix a universal base U. Its universality ensures every finite output string has
a description, by simulating the machine with the sole input ε and that output.

Fix a countable index set I of environments, fixed reward semantics, and an
injective map c:I→binary words. Each environment is represented once; distinct
semantic duplicates, if deliberately retained, instead define a different index
space and weighting convention. No effective enumeration or computability of c
is assumed. K_U(x) is the minimum length of a programme successfully outputting x.
When a nonuniversal base lacks such a programme, use weight zero and make no
finite K assertion. For universal machines every K_U(c(i)) is a natural number.

## R1-A — exact wrapper, prefix freedom and shortest lengths

Given a finite target string t and L≥2, define W(0)=t on the exact singleton
word; define W(1^L p)=U(p); leave all remaining inputs undefined. The branches
are disjoint because their first bits differ. The parser removes exactly L
leading ones. Thus dom(W)={0}∪{1^L p:p∈dom(U)}; it accepts no empty word.
For two simulation-domain words, one is a prefix of the other iff their suffixes
have that relation. Prefix freedom of U forces equal suffixes. The word0 is
prefix-incomparable with every simulation word. Hence W is prefix-free.
This argument already holds at L≥1; the main study uses L≥2 for its margins.

W is partial computable: decide the finite input branches and, in the simulation
branch, run U on the suffix; otherwise diverge. The finite string t is hardcoded,
so the procedure does not need an effective map from all indices to codes.
For any V simulated by U with compiler d_V, W(1^L d_V p)=V(p). Therefore W is
universal with compiler overhead L greater than U's. This is a paper operational
argument, not an assertion that the Lean Option denotation models a universal TM.

No empty programme succeeds in W and programme0 outputs t, so K_W(t)=1.
If x≠t, every successful description of x is uniquely1^L p with U(p)=x.
Thus description existence is equivalent for W and U; when it exists, its
least length is exactly L+K_U(x). Both bounds follow: pad a shortest base
programme, and remove the prefix from any wrapper programme. In particular,
for t=c(z), injectivity gives this equality for every i≠z.
These are actual shortest-success arguments; a postulated K-shift is insufficient.

## R1-B — Kraft and the subprobability concentration bound

For a binary word p of length n and binary integer value k, assign the half-open
dyadic interval [k/2^n,(k+1)/2^n). Its length is2^-n. Two such intervals
intersect only if one word is a prefix of the other. Thus intervals belonging
to a prefix-free set are disjoint inside[0,1). Every finite subset has lengths
summing to at most1. Taking the supremum over finite subsets proves the countable
Kraft inequality, including an empty set or the singleton{ε}.

For each described code choose the lexicographically first shortest programme.
Different codes have different chosen programmes because U is a function; the
chosen set is a subset of dom(U), hence prefix-free. Consequently
Σ_i 2^-K_U(c(i))≤1, with missing outputs contributing zero for nonuniversal U.
Multiple programmes for one output do not contribute separate code weights.
For example00 and01 producing the same output give weight1/4, not1/2.

R1-A gives w_W(z)=1/2 and w_W(i)=2^-L w_U(i) for i≠z. Therefore
Σ_{i≠z}w_W(i)≤2^-L and Σ_i w_W(i)≤1/2+2^-L≤3/4.
These weights are intentionally unnormalized. Normalizing a fixed positive
weight family multiplies all its scores by one common positive factor and
preserves its comparisons, but neither normalization nor prior choice is derived.

## R2-A — convergence and the complete machine-family envelope

Let v:I→[0,B], with finite B≥0. Finite score sums are nonnegative, increase
under inclusion, and are bounded by B using R1-B. Define S_U(v) by their
supremum; on any exhaustive nonrepeating listing it is the limit of the partial sums. Nonnegativity
makes the value independent of enumeration. It lies in[0,B]. For v,w in this
same interval, Σ_i w_U(i)|v(i)-w(i)|≤B, so their difference is absolutely
summable and S_U(v)-S_U(w)=Σ_i w_U(i)(v(i)-w(i)). One can also derive this
identity by subtracting the two convergent finite partial sums along an enumeration.
No operation here asserts effective evaluation of the resulting real number.

For the target wrapper, all nontarget contributions lie between0 and B·2^-L.
Hence (1/2)v(z)≤S_W(v)≤(1/2)v(z)+B·2^-L, uniformly over bounded profiles.
In particular, the wrapper scores converge uniformly to half the target coordinate
as L increases. If v≤w pointwise, each finite weighted sum preserves that order;
pass to limits to obtain S_U(v)≤S_U(w) for every universal U.

Conversely take v,w:I→[0,1] and suppose v(z)-w(z)=δ>0. The Archimedean
property of the reals and decay of2^-L give L≥2 with2^-L<δ/2.
Use R1-A to build W from any fixed universal base. Then
S_W(v)-S_W(w)≥δ/2-Σ_{i≠z}w_W(i)≥δ/2-2^-L>0.
Thus v≤w iff every universal prefix reference-machine score orders v below w.
The empty index set is harmless: the pointwise condition is vacuous and all
scores are zero. For a machine subfamily this converse is justified only if
it contains the target/padding wrappers used in the argument. A finite test
family is not automatically complete.

Apply the same theorem separately to two injective codings of the same fixed
index set and unchanged profiles. Both envelope orders equal pointwise order,
so these orders agree. This proves coding invariance of the envelope relation,
not of individual scores, machine rankings, chosen environments or rewards.
For incomparable profiles, each violated direction can be separated by a
possibly different wrapper. No universal single score is selected by the family.

## R2-B — actual reward-summable policy ranking reversal

Use a singleton observation alphabet and actions A,B. Environment μ_A emits
initial reward0, then after the first action emits reward1 if it was A and0
otherwise, and thereafter emits reward0 at every step. Define μ_B by swapping
A and B. These are deterministic computable environmental measures: each
conditional distribution is a point mass calculated from the finite history.
They emit only rewards0,1 and every trajectory's cumulative reward is≤1.
This matches LH2007 environment-first timing and reward summability.

Let π_A always choose A and π_B always choose B. Their expected returns in
μ_A are1,0 and in μ_B are0,1. Include these two distinct environments in the
fixed codebook; other environments may give any returns in[0,1]. A wrapper
concentrating μ_A gives S(π_A)-S(π_B)≥1/2-2^-L≥1/4 for L≥2.
A wrapper concentrating μ_B gives the reversed inequality. The policies and
environment class are fixed throughout; only the universal reference machine
changes. No discounted forever-reward environment is substituted into this proof.

Insufficient concentration is a genuine boundary: for the nonuniversal base
ε→nontarget, padding L=2 yields weights(1/2,1/4). Profiles(1/2,0) and(0,1)
have equal scores although the former improves the target coordinate. At L=3
the former scores1/4 and the latter1/8. This falsifies separation without a
strict target-gap versus residual-mass condition, not prefix validity at L=1.

## Relation to the parents and proof levels

LH2007 §§3.2–3.3 supplies the bounded-return weighted measure; §3.5 itself
states reference-machine ranking dependence. Leike–Hutter2015 Lemma1 and
Corollary14 establish the concentration limitation in their discounted LSCCCS
setting. R1/R2 adapt that mechanism to exact shortest-code weights and the
LH reward-summable witness; no mathematical originality is asserted.
Their Theorem18 concerns Pareto optimality in the LSCCCS model. It is not
silently transferred to a narrower environment class or used to identify an
optimal architecture. Our arbitrary-profile theorem does not imply that every
profile is realized by a policy; the separate two-policy witness is actual.

The kernel scope consists of actual finite-word wrapper/domain/shortest laws
and finite algebraic bounds, with its scalar model stated in FORMAL_SCOPE.
Countable Kraft, Real convergence, the universal-TM interpretation and the
complete Real envelope in this file are paper-level. Exhaustive finite books
calibrate those implementations but cannot certify universality or infinite sums.

For a finite rational vector, choose positive common denominators D,E and write
weights a_i/D and profile values b_i/E. Its score is the integer dot product
Σa_i b_i divided by DE. Multiplication by DE>0 preserves comparisons; clearing
these denominators transports finite rational inequalities to integer ones.
This is an explicit paper interpretation of the Int bounds, not a kernel claim
that general rational normalization or arbitrary Real profiles have been instantiated.
