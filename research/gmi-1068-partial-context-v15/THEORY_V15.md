# Partial contexts and a general fixed-process reversal theorem

This is classical order/partial-map mathematics under FREEZE_V15, not a novel
empirical prediction. H is an arbitrary history type, P⊆H admission, E⊆H
an ambient evaluation domain, W a preorder with relation ≤, and ν:E→W.

## O1-A — original partial context and three observation cases

Define D=P∩E and restrict ν along D→E. This is a partial map on P with
defined domain D⊆P, exactly preserving the original R2 definition. Conversely,
a partial map on P with domain D⊆P is represented by E=D and the same map.
Ambient extensions outside P are permitted but observationally immaterial:
for each h, return ILLEGAL if h∉P, UNDEFINED if h∈P and h∉E, and
VALUE(ν(h)) if h∈P∩E. These cases are disjoint and exhaustive.
Changing ν only outside P leaves every such observation unchanged.
VALUE is a tagged constructor: a value named 'undefined' inside W is still a
value, distinct from absence of a defined evaluator result.
An implementation must retain P,E and endpoints; no bottom value is required.
For finite indexed H, the Allowed encoding below reads only values on D,
ordered by increasing history index, never values on illegal histories.

**Assumptions.** Declared sets P,E and an actual function on E; observation case distinction is classical unless predicates are decidable.
**Dependencies.** Set intersection and restriction; no process-law recovery result.
**Falsifiers.** Evaluating an illegal history as VALUE, merging a value with UNDEFINED, or allowing ambient illegal values to affect Allowed.
**Strongest parents.** [Fiore–Plotkin §3 Definition3.2](https://homepages.inf.ed.ac.uk/gdp/publications/Ax_FPC.pdf), partial maps with explicit domains; used here in sets, without importing their computational-adequacy theorem.

## O1-B — contextual preorder and its quotient

For x,y∈D put x≼νy iff ν(x)≤ν(y). Reflexivity of ≤ gives x≼νx;
transitivity applied to ν(x),ν(y),ν(z) gives transitivity of ≼ν.
Let x~νy iff x≼νy and y≼νx. Reflexivity is inherited, symmetry swaps
conjuncts, and transitivity composes the two forward and two reverse comparisons.
Thus ~ν is an equivalence relation, without antisymmetry of W.

Comparison respects representatives: if x~νx' and y~νy', then x≼νy
implies x'≼νx≼νy≼νy', hence x'≼νy'; the converse uses x≼νx'
and y'≼νy. Therefore define [x]≤Q[y] iff x≼νy on Q=D/~ν.
The equivalence just proved makes this well-defined. Reflexivity and
transitivity descend; if [x]≤Q[y] and [y]≤Q[x], then x~νy, so [x]=[y].
Hence Q is partially ordered, and its comparison agrees exactly with the
original contextual comparison. This also uniquely determines the order on Q
because every quotient element has a representative.

No comparison is assigned to absent evaluations. Declaring comparison false
outside D on all H would fail reflexivity for every h∉D. If D is empty,
its preorder and quotient order are valid vacuously. If W is empty, a supplied
ν:E→W entails E empty; no hidden default is needed. Different W-values may be
mutually comparable and therefore yield the same contextual class. Distinct
histories in that class need not share dynamics, observations or continuations.
This quotient is not behavioral equivalence or process minimization.

**Assumptions.** A genuine preorder on W and the actual restricted evaluator on D.
**Dependencies.** Pullback comparison, the proved equivalence and representative invariance.
**Falsifiers.** Comparing undefined histories, treating equal classes as equal histories, or using one-way comparison as equivalence.
**Strongest parents.** [Stacks Remark4.21.3](https://stacks.math.columbia.edu/tag/002Z), classical antisymmetrization; [Mathlib Antisymmetrization](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Order/Antisymmetrization.html) is a mature construction reference, not a Lean4.19 dependency.

## O2-A — actual opposite rankings under an unchanged process

Fix an actual complete C∈Proc, including its process laws and admission
P=admitted(C). Fix D⊆P and a,b∈D with a≠b. Suppose lo,hi∈W satisfy
lo≤hi and not hi≤lo. Thus lo and hi are strictly ordered, not merely distinct.
Let Allowed be a predicate on actual functions D→W. Define

`ν0(x) = lo if x=a, otherwise hi`,
`ν1(x) = hi if x=a, otherwise lo`.

Assume Allowed(ν0) and Allowed(ν1). Equality tests can be classical; a finite
implementation computes them. Since a≠b, the four evaluations are
ν0(a)=lo, ν0(b)=hi, ν1(a)=hi, ν1(b)=lo. Therefore
`a≼ν0b and not b≼ν0a`, while `b≼ν1a and not a≼ν1b`.
The actual ordering functions o_i(x,y):=(ν_i(x)≤ν_i(y)) disagree at (a,b).
Also ν0≠ν1: equality at a would imply lo=hi, contradicting the strict pair.
Neither process C, admission P, domain D nor codomain preorder changes.
This is the general schema behind an admitted two-history AJ7 countermodel.
It does not assert separation for every allowed evaluator class.

An alternative sufficient premise is Allowed(ν), ν(a)<ν(b), and closure of
Allowed under precomposition with the transposition τ swapping a,b and fixing
other histories. Then ν∘τ is allowed and reverses the pair. τ is a bijection
and keeps D fixed. This is an alternative theorem, not an implicit assumption
that arbitrary Allowed classes contain either indicator or swapped maps.

**Assumptions.** Fixed complete C, a≠b in D⊆admitted(C), a strict codomain pair, and explicit Allowed membership of both constructed maps.
**Dependencies.** Indicator evaluation and the definition of strict comparison; swap alternative needs its stated closure.
**Falsifiers.** Constant-only classes, observation-collapsed classes, a singleton domain, an unadmitted witness or a mutually comparable lo/hi pair.
**Strongest parents.** Elementary separation by indicator functions and the original AJ7 witness; reward ambiguity in [Ng–Russell](https://ai.stanford.edu/~ang/papers/icml00-irl.pdf) is a comparison parent, not a proof of this distinct process-to-order claim.

## O2-B — nonrecovery from the complete fixed process

Let M={ν:D→W | Allowed(ν)}. Define p:M→Proc by p(m)=C, e(m)=m.val,
and o(m)(x,y):=(m.val(x)≤m.val(y)). These are maps on the same actual model
space, not selector names. O2-A supplies m0,m1∈M with p(m0)=p(m1) and
o(m0)≠o(m1), while e(m0)≠e(m1) as well.

A decoder for o from p means d:Image(p)→(D→D→Prop) with d(p(m))=o(m)
for every m, where Image(p) retains an attained-value witness. Such a decoder
would assign the same output to equal p(m0),p(m1), contradicting the differing
orders. Thus ordering is not recoverable from the whole fixed C on this model
class. The same collision excludes recovery of the evaluator itself.
No probability distribution on M is supplied; this is not statistical independence.

More generally, an output o is recoverable from p exactly when it is constant
on every p-fiber. Necessity follows by applying a decoder to equal inputs.
For sufficiency, for each attained value select a preimage m and output o(m);
fiber constancy makes this independent of that selection. This needs classical
choice for arbitrary sets, and only defines a decoder on Image(p), not all Proc.
V9's existing theorem proves this criterion and its collision corollary; V15
must freshly register the exact reused types and bind the unchanged source.
A constant full-process map has one attained value, so an output is recoverable
from it iff that output is constant over M. Empty M is harmless; O2-A provides
two actual witnesses for the nonrecovery conclusion.

**Assumptions.** O2-A and actual observation maps on the allowed-model subtype.
**Dependencies.** V9 recoverable_iff_fiber_constant and no_recovery_of_collision; no reduced-process observation is substituted.
**Falsifiers.** Different complete process payloads, an ordering constant over M, a witness outside Allowed, or a decoder defined only for a selected evaluator.
**Strongest parents.** Classical factorization through fibers, reused as [RecoverabilityV9](../gmi-1068-r0-foundation-repair-v9/RecoverabilityV9.lean); no new nonidentifiability principle is claimed.

## O3 — exact examples, controls and scope

A lawful fixed example is the one-object category with arrows Z/3Z,
identity 0 and composition addition modulo3. Associativity and units follow
from modular addition; all arrows are admitted. Its two nonidentity arrows
supply distinct admitted histories. Taking D to be all three arrows, ordinary
0<1 and unrestricted Allowed realizes O2-A while the entire category table,
identity, endpoints, admission and law data remain unchanged.
A partial-context corpus may separately use arbitrary admission subsets;
those subsets are not claimed to form composition-closed subcategories.

The disclosed finite calibration enumerates all 29 preorders on three labelled
values and all 125 five-way status/value assignments on three histories.
Its 3625 proposed contexts are a planned exhaustive finite construction, not
prospective empirical novelty. Actual receipts must count observations,
comparisons, equivalence classes, quotient orders and executed law checks.
Nonantisymmetric preorders and empty defined domains must remain in the corpus.

The failed-premise controls have precise causes. Constant evaluators tie every
pair. If every allowed evaluator factors through q with q(a)=q(b), then each
assigns equal values to a,b, preventing strict reversal. Empty/singleton D
has no distinct pair. Distinct lo,hi with both directions comparable cannot
produce strict ranking. Histories outside P or E are outside D; their ambient
values cannot supply a legal witness. These controls restrict the theorem's
applicability; they do not refute it or warrant selecting a new value theory.

**Assumptions.** Declared finite enumeration and unchanged lawful witness; independent algorithms for calibration.
**Dependencies.** O1/O2 and ordinary finite category/order calculations.
**Falsifiers.** Skipped preorders, silently sanitized false laws, a changed process payload, or counting illegal/undefined values as witnesses.
**Strongest parents.** Classical finite orders and cyclic-group category; the corpus and controls are registered exact diagnostics, not new architecture or intelligence mechanisms.

Only R2-001 and R2-004 are eligible for closure. No reverse-admission theorem,
complete context-family classification, unique universal value scale, objective
prior selection or full intelligence unification follows. Exact kernel coverage
and any paper-only alternative are stated separately in FORMAL_SCOPE_V15.
