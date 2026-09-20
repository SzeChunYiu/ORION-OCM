# AB1 — the actual unchanged process

## AB1-A: free paths and the interpreter

Take the directed graph with one object * and two distinct loops a0,a1.
Its category C has finite words as arrows, empty word as identity and
concatenation as composition. Concatenation is associative and empty is a
two-sided unit, so this is an actual lawful category. Words of different
length or different letters remain different arrows.

Map * to the singleton state set and each generator to original processStep,
the unique function Unit→Unit. The interpreter maps a word to the corresponding
function composite. It preserves identity and concatenation by recursion.
Every interpreted word acts identically on the unique state; this does not
identify the source arrows. In particular a0 is not the empty path.

The implementation uses actual V11 paths and their interpreter. Its process
observation contains the fixed graph, singleton state domain and generator maps.
This finite presentation describes the complete free category; the two sampled
singleton histories do not exhaust its arrows.

## AB1-B: actual partial contexts

Let H be all words, P(h)=True and E(h) mean length(h)=1.
For m=0,1 define k_m on E by k_m([a])=ctx_m(a), with ordinary numeric order.
Use the actual V15 partial-context representation. The evaluator is undefined
on [] and on every word of length at least two. These words remain admitted.

Set h0=[a0], h1=[a1]. Their values are:
k0(h0)=1, k0(h1)=0; k1(h0)=0, k1(h1)=1.
Thus h1≤_k0 h0 and not h0≤_k0 h1, whereas h0≤_k1 h1 and not h1≤_k1 h0.
Consequently the value functions differ and the actual induced order functions
differ. P, E, the complete category and its state interpreter are unchanged.

This proves both original rankings after embedding them in actual histories.
It also proves actual context inequality: equality of the partial contexts would
force equality at h0, contradicting 1≠0. Order inequality follows from the displayed
opposite truth values on the same ordered pair of history labels.

## AB1-C: attained-image nonrecovery

Let M={0,1}, o(m)=the fixed complete process and t(m)=k_m, or alternatively
t(m)=the induced history-order relation. Then o(0)=o(1) and t(0)≠t(1).
If a decoder d existed, t(0)=d(o(0))=d(o(1))=t(1), a contradiction.
This is the actual V9 collision criterion, applied to constructed functions.

Context-value equality and induced-order equality are distinct targets.
For example, evaluators with singleton values (1,0) and (2,0) differ but induce
the same order on the two selected histories. A certificate must compute both
targets separately; it cannot infer value recovery from order recovery.

The converse is the fiber criterion: if a target is constant on each attained
process-observation fiber, define its decoder by the common target value.
Uniqueness holds on that attained domain. For an empty model domain the decoder
is the empty function. No target value on an unattained process code is needed.

## Generic separation assumptions

V15 generalizes the displayed construction to two distinct active histories,
a strict pair low<high in the declared value preorder, and an Allowed class
containing the two actual indicator evaluators. Its domain is P∩E.
The first indicator is low at the first history and high elsewhere on that domain;
the second reverses these values. Membership concerns precisely those evaluations.

A constant-only Allowed class, collapsed histories or an indiscrete value order
does not satisfy these premises. Neither do illegal or unevaluated selected
histories. A finite counterexample with unrestricted evaluators does not prove
separation for every restricted application-specific evaluator class.

## Parent and finite correspondence

Riehl, Category Theory in Context, Example 4.1.13 supplies the classical free-path
construction. V11 implements typed paths; V15 supplies partial contexts/separation;
V9 supplies recovery on attained images. The original finite source supplies
the exact Action, processStep and ctx equations.

The frozen Python population uses nine reward vectors on the two singleton
histories and 81 ordered pairs. It independently asks whether a process decoder
recovers values and whether it recovers the order: 162 distinct decisions.
Empty and two-step controls test the separate infinite-history observer.
Counts describe the registered population; actual execution is recorded in RESULT.
