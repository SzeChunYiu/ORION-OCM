# Resource-indexed deterministic distinctions V10

Read FREEZE_V10.md and PARENTS_V10.json first. These are direct proofs at a
specified operational scope, adapting established automata, shortest-path and
ultrametric methods. No priority, empirical novelty or general-intelligence
claim follows. This symmetric distinction threshold is not R5's directed
transformation burden: D(s,s)=infinity, not zero.

## Model and observations

Let S be finite and nonempty, A finite, o:S→O, and
δ:S×A→Option(Y×Nat×S). Write δ(s,a)=(y,c,u) for a present edge.
At resource B an edge executes iff c≤B, emits EDGE(y,c), subtracts c,
and continues at u. Otherwise execution emits ILLEGAL and stops. All current
and intermediate o-values and successful events are retained. Empty words
observe o(s). Successful, illegal and observation tokens are distinct.
Remaining resource is not separately observed. The transition function is
supplied and total into Option: divergence is not represented by absence.

Write R_B(s,w) for this complete response and s~_B t iff these responses
agree for every w∈A*. This is an equivalence relation by equality. Write
R_infty for the same semantics with every present edge affordable. Let
D(s,t)=min{B∈Nat : s is not ~_B-equivalent to t}, with min(empty)=infinity.
Extended-natural arithmetic uses c+infinity=infinity. No probability law,
silent transition, replenishment or nondeterministic matching is introduced.

## T1 — exact resource threshold and persistence

**Theorem.** For all B, s~_B t iff B<D(s,t).

**Proof.** First show that a distinguishing word at B still distinguishes at
B'≥B. Before the first response mismatch, every successful edge has equal
output and cost, so accumulated consumption and residual-resource increments
are equal on both sides. A current-observation mismatch persists. A success
versus physically absent edge persists. Two successful unequal events remain
unequal. Finally, if success versus unaffordability was the first mismatch,
one cost is at most the old residual and the other strictly greater. At the
larger residual either the mismatch remains, or both edges execute and their
unequal costs are observed. Earlier new mismatches only help. Thus distinction
is upward closed. Every nonempty subset of Nat has a minimum; upward closure
makes the distinguishing resources exactly {B:B≥D}. The empty case gives
infinity and equivalence at every finite B. Symmetry gives D(s,t)=D(t,s),
and reflexivity gives D(s,s)=infinity. ∎

## T2 — shortest path and finite witnesses, including zero cycles

Use unordered distinct pairs {s,t}, plus a sink ⊥. Diagonal successors are
omitted: a state compared to itself never distinguishes. At a pair with
unequal observations add a zero edge to ⊥; further edges there are unnecessary.
Otherwise inspect each a and add the following action-annotated edges:

| Original transitions | Product edge |
|---|---|
| Both absent | None |
| Exactly one present, cost c | To ⊥, weight c |
| Both present with unequal (y,c), costs c,d | To ⊥, weight min(c,d) |
| Both present with identical (y,c), successors u,v | To {u,v}, weight c if u≠v |

**Theorem.** D(s,t) is distance to ⊥, and is infinity for diagonal pairs or
unreachable ⊥. A shortest path supplies a finite distinguishing word.

**Proof.** A common product prefix follows equal successful events and spends
its summed weight on both runs. At its last edge the listed weight is exactly
the least additional resource making one success possible or revealing an
unequal event. If both unequal events become affordable, they remain unequal;
if just one becomes affordable, success differs from ILLEGAL. An observation
sink needs no action. Thus every sink path distinguishes at its total weight.
Conversely take a distinguishing run at B and stop at its first mismatch.
Its common successful prefix gives product edges of their common costs. The
mismatch yields the corresponding sink edge of weight no greater than its
remaining resource. Hence there is a sink path of weight≤B. Minimizing these
two inequalities proves the claim and, with T1, every larger-resource claim. ∎

Unordered pairs are sound because exchanging the compared runs preserves all
rules. With N=n(n−1)/2 pair vertices, remove repeated vertices from any
minimum-cost path; nonnegative cycle removal cannot increase its cost. A
simple witness visits at most N pair vertices, even when costs are zero.
A reverse Dijkstra computation starts with infinity and relaxes actual paths
to the sink. When recording a witness successor, require it to be already
settled and update only on strict improvement; its settlement rank decreases
along witness links. This proves reconstruction terminates through zero ties.

Bellman equality alone is insufficient: a zero self-loop with no sink gives
d=d, admitting every finite value although distance is infinity; adding a
sink of weight5 gives d=min(d,5), admitting all d≤5. Distances are the greatest
Bellman solution in numeric order: any solution is≤every finite path weight
by unfolding along that path, while the shortest-path distances satisfy the
equations, including unreachable vertices. Initialization at zero is invalid.

## T3 — exactly when the universal nesting guarantee holds

For each a fix a set P_a of available payloads, a cost c_a:P_a→Nat and an
emitted event e_a:P_a→E_a. Machines may use arbitrary available payloads.
Replace the successful token by EDGE(e_a(payload)): cost is used internally
for admission/subtraction and is NOT separately emitted. Current/intermediate
state observations, ILLEGAL and stopping behavior are retained. Quantify over
all finite partial deterministic machines on these payload sets, allowing
equal state observations and a common terminal state.

**Theorem.** The universal law B≤B' ⇒ (~_B' ⊆ ~_B) holds iff
for every a,p,q, e_a(p)=e_a(q) ⇒ c_a(p)=c_a(q).

**Proof.** Sufficiency repeats T1: equal events on the common input action
imply equal costs; newly affordable unequal costs cannot emit equal events.
For necessity suppose one action has p,q with equal events and c<d. Use
states s,t,z with equal observations, only s--a,p→z and t--a,q→z, and no
edges at z. At B=c one succeeds and the other is illegal. At B=d they emit
the same event and enter z; every other first action is illegal on both.
Thus all words agree at d despite a distinction at c, contradicting nesting. ∎

Cost need only be recoverable from (action,event); different actions may emit
the same event at different costs. The necessity quantifier matters: a
restricted application class can enjoy nesting without this payload property.
Separately visible remaining resource or extra distinguishing observations
can defeat the counterexample. This theorem does not remove those hypotheses.

## T4 — similarity threshold and pseudoultrametric

**Theorem.** D(s,u)≥min(D(s,t),D(t,u)). Set d(s,t)=2^(-D(s,t)), with
2^(-infinity)=0. Then d is a pseudoultrametric and an ultrametric after
quotienting by complete unbudgeted response equivalence.

**Proof.** If D(s,u)<min(D(s,t),D(t,u)), put B=D(s,u). At B the latter two
pairs are equivalent by T1; transitivity contradicts the first distinction.
Symmetry and zero diagonal for d follow from T1. Exponentiation reverses the
threshold inequality into d(s,u)≤max(d(s,t),d(t,u)). A zero distance means
equality at every finite resource. Every finite unbudgeted execution fits
some finite resource, so this is exactly complete unbudgeted equivalence;
conversely identical unbudgeted responses have equal costs and guards at every
resource. The strong triangle inequality makes distances independent of the
chosen equivalent representatives; distinct quotient classes have positive
distance. ∎ The base 2 is a chosen scale, not a uniquely derived physical unit.
Rutten's approximation-depth construction is an explicit mathematical parent.

## T5 — sharp finite-resource bound

Let n=|S|, k=|o(S)| and Cmax be the largest edge cost, or0 if no edges exist.
**Theorem.** Every finite D(s,t) satisfies D(s,t)≤(n−k)Cmax.

**Proof.** In the unbudgeted machine, partition P0 by observations. Define
P_(i+1) by observations and per-action absence or (event,P_i-successor class).
Induction on words proves P_i means agreement on all words of length≤i.
Each P_(i+1) refines P_i. If equal, the partition is a bisimulation and word
induction proves full response equivalence. Each strict refinement adds at
least one block, so P_(n−k) is stable. Finite D implies unbudgeted inequivalence
by equal-cost guard preservation. Hence some distinguishing word has length
L≤n−k. Resource L*Cmax makes every present edge along either run affordable,
so their unbudgeted distinction remains; taking the least resource proves
the bound. This asserts existence of some short word, not that a cheapest
resource witness has length≤n−k. ∎

Sharpness: a unary n-state chain ending in a state without an edge, with all
observations equal and every edge of cost C>0 and common output, distinguishes
its first two states only after n−1 actions at resource(n−1)C. Here k=1.
For n=1 there is no distinct pair. Empty A or Cmax=0 causes no exception:
finite thresholds are then0. T2 also supplies the valid bound N*Cmax.

## T6 — representation steps and their boundary

Let k(B)=|S/~_B|. T1 makes these partitions successively finer. Every distinct
positive finite threshold D(s,t)=b separates a pair equivalent at b−1, so
strictly increases k. There are at most n−k(0) such thresholds.

For known fixed B, any code z(s) decoding all R_B(s,w) must separate different
~_B classes: equal codes would produce equal responses. Thus at least k(B)
codes are necessary; class encoding with its response function attains the
bound. Fixed-length binary encoding requires exactly ceil(log2 k(B)) bits.
This excludes the cost of the externally supplied B and decoder. A class-count
increase need not cross a power of2 or increase the rounded bit count.

This is not an online update theorem at unchanged B. For example s,t both
have cost1 equal-event edges to u,v; u has a cost1 edge and v none, all
observations equal. Then s~_1t but u is not ~_1v: actual successors are compared
at residual0. Use resource-indexed classes or lifted (state,resource) states.
Formal proof scope is listed separately; these paper proofs do not assert
that the Python shortest-path implementation is kernel verified. The frozen
independent tests check a finite corpus; all 214 scientific requirements and
overall theory closure remain open.
