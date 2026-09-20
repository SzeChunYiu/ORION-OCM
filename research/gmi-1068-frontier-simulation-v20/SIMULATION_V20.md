# V20 deterministic continuation simulation and resource bridge

## T3.1 — exact observation-relative greatest relation

Supply states X, actions Σ, deterministic partial transitions d_a:X→Option X,
and a base preorder B. Define run(x,[]) = some(x) and
run(x,a::w)=d_a(x).bind(fun u=>run(u,w)). None propagates failed admission.
A simulation R is contained in B and satisfies: x R y and d_a(x)=some(u)
imply ∃v,d_a(y)=some(v) and u R v.

Define G(x,y) by the following actual all-word observation condition:
for every finite w, run(x,w)=some(u) implies some v with run(y,w)=some(v)
and B(u,v). The empty word gives G⊆B. Any simulation R is contained in G
by induction on the word: the one-step clause supplies a matching successor
and its related pair, then the induction hypothesis handles the suffix.

Conversely, if G(x,y) and d_a(x)=some(u), applying G to [a] supplies the
unique successor v of y. For any suffix w with run(u,w)=some(s), apply G
to a::w. Its matching run from y must use that same v, because d_a is a
function. It supplies t with run(v,w)=some(t) and B(s,t). Thus G(u,v).
This proves G is a simulation and the greatest base-contained one.
Reflexivity follows by using the same successful run and B's reflexivity.
For G(x,y),G(y,z), any successful x-run has a matching y-run and then a
matching z-run; B's transitivity compares their endpoints. Hence G is a preorder.

The result is one-sided: extra enabled actions at y are allowed. It preserves
the SAME action word, including each independently queried prefix. It is not
the greatest relation preserving existential reachability with arbitrary changes
of action labels. The converse above relies on deterministic successors; equal
nondeterministic trace languages do not suffice for forward simulation.

## T3.2 — frontier pruning and revival

Every d_a is guarded-monotone from (X,G) to itself, by the simulation clause.
T2.3 gives this property for each run_w. For finite A and any cofinal C⊆A
under G, T2.1 gives

    ↓_G run_w[A] = ↓_G run_w[C]

for every finite word w. Applying T1 chooses actual maximal endpoints or one
representative per maximal class. Unions over any supplied word family preserve
the same downward equality: downward closure commutes with union. Existential
G-upward endpoint goals are therefore unchanged. This includes every B-upward
goal, since G is contained in B. Intermediate repeated pruning
is safe as well, by induction over update steps using cofinality at each step.
This does not assert exact sets, trace equality or infinite-run semantics.

Refining a current-value order to G can retain more candidates, which is the
necessary repair when a presently dominated candidate has a better future.
The retained order is constrained by actual continuation legality and values;
it is not fitted to make a chosen experimental outcome positive.

## T3.3 — finite descending algorithm and witness bound

For finite X and finite Σ start R_0=B and synchronously compute

    R_(i+1)={(x,y)∈R_i | for every a, d_a(x)=u implies
                              d_a(y)=v for some v with (u,v)∈R_i}.

This deletes pairs and never adds them. Every simulation is contained in R_0;
if contained in R_i, its matching successors remain in R_i, so it is contained
in R_(i+1). At stabilization the retained relation is itself a simulation,
therefore equals G by greatestness and the preceding inclusion. At most n²
pairs can be removed. A nonstable round removes at least one pair, giving at
most n² strict refinement rounds plus the final stability check. Empty state
and action sets are included; no iteration assumes an enabled action exists.

A rejected pair has a distinguishing word: either B already fails (empty word),
or an action is enabled only at its left member, or a matched-successor pair
has such a word, which is prefixed by the action. Independent breadth-first
search follows matched deterministic pair transitions and checks these failures.
A shortest witness cannot revisit an intermediate pair: removing the repeated
segment leaves the same suffix failure. There are at most n² pairs. A base-order
failure therefore needs at most n²−1 steps when n>0; an unmatched final action
can add one, so n² is a uniform bound. For n=0 no pair requires a witness.
The finite algorithm correctness argument is a general paper proof; the final
ledger distinguishes it from the kernel proof of G and from Python calibration.

## T3.4 — actual V8 budget lift and endpoint observation

For an actual V8 Machine and a supplied finite maximum budget B_max, the
existing budget_lift constructs indices (s,b) as s*(B_max+1)+b. An original
edge (output,cost,t) is admitted precisely when cost≤b, and its destination
is (t,b−cost). Drop only the EDGE payload when creating the partial endpoint
transition; retain the lifted destination and therefore the residual budget.
Induction on a word identifies its successful endpoint with the V8 lifted
execution's internal state variable, and identifies failure with an unavailable
or unaffordable step. This internal endpoint need not be recoverable from the
emitted OBS labels, which may identify distinct states.
This is an endpoint/admission bridge, not equality of full EDGE/output/cost traces.

Supply the endpoint base preorder explicitly. Applying T3.1 to these actual
lifted transitions gives the strongest same-word simulation below that order.
For an endpoint Context k with separate P and E, let O(s) return its value
exactly on P(s)∧E(s), otherwise none. To transport a STATE endpoint theorem
to attained VALUE images, require O to be guarded-monotone for the base order
(and the context's value order), or prove that property from its construction.
Then G⊆B makes O guarded for G, and T2 applies to O∘run_w. Total monotone
endpoint evaluation is a sufficient special case. Without this condition, an
ordered endpoint might be undefined or have a worse value; no value-goal theorem
would follow from state simulation alone. Admission and evaluation tags in the
Context remain available separately, although this value-image observer omits
illegal and undefined values alike. No complete tag equivalence is claimed.

The existing V8 constructor requires nonempty states/actions. That inherited
API restriction belongs only to this bridge; the generic T1–T3 constructions
include empty cases. Its finite correspondence checks are not a kernel proof
that Python implements the generic machine theorem.

## Ownership

Doyen–Raskin's simulation and antichain framework supplies the core pruning
mechanism. Here the deterministic same-word observer, base order and partial
admission are explicit. V8 supplies the actual affordability lift; none of its
stronger full-trace equivalence results are silently inherited by an endpoint
observer. No novel empirical or universal intelligence result is claimed.
