# Complete deterministic continuation semantics V8

This is an additive repair of the R4 supplied-test semantics. Read the freeze
and [source ownership](PARENTS_V8.json); the established mathematics is
parent-owned. Implementation receipts establish only their registered corpus.

## 1. Operational model and complete responses

Fix sets S, A, O, E, observation o:S→O and deterministic partial transition
d:S×A→Option(E×S). O contains a designated UNDEFINED value if evaluation is
partial. E contains every observed edge output and cost. None in d means
ILLEGAL; it is different from an admitted state's UNDEFINED observation.
Costs are supplied by c:E→Nat. No distribution over states is required.
The function d is mathematically total into Option; None does not mean that
computing d diverges. UNDEFINED is a supplied token, not a halting oracle.

For every word w in A*, define response R(s,w) recursively:
R(s,ε)=DONE(o(s)); R(s,aw)=ILLEGAL(o(s)) if d(s,a)=None;
otherwise R(s,aw)=STEP(o(s),e,R(t,w)) when d(s,a)=Some(e,t).
The action word is the test input, so need not be duplicated in the response.
Execution stops at the first illegal input. All intermediate observations and
edge labels are retained. Python's flat OBS/EDGE/ILLEGAL token sequence and
Lean's recursive constructors encode the same record, with DONE represented
by normal exhaustion of the supplied word. Neither representation exposes
the hidden state identity.

Define s≈t iff R(s,w)=R(t,w) for every finite word, including ε.
This is an equivalence relation by equality, with no finiteness premise.
A finite test table generally defines a weaker relation.

## 2. Actual congruence, quotient and preservation

**Theorem 1.** If s≈t then o(s)=o(t), and for every a both transitions
are absent, or both are present with equal edge label and equivalent successors.
Conversely, any relation B whose pairs satisfy those observation and transition
conditions is contained in ≈. Hence ≈ is the greatest such bisimulation.

**Proof.** The empty word gives observation equality. The one-letter test
distinguishes absent from present transitions and unequal edges. In the
present/present case, compare a::w for every w and cancel the common STEP
constructor to get successor equivalence. For the converse, induction on w
preserves equal observations and edges; absent transitions end identically.
Thus closure is derived from execution, rather than assumed for a test table.

Let Q=S/≈ and q(s)=[s]. Define oQ([s])=o(s), and dQ([s],a)=None
or Some(e,[t]) according to d(s,a). Theorem 1 proves independence of the
representative, including enabledness and edge cost. **Theorem 2.**
RQ(q(s),w)=R(s,w) for every w. Proof: induction on w, using the actual
quotient transition in the step case. The quotient is behaviorally reduced:
different classes have a distinguishing finite word by the definition of ≈.

## 3. Universal sufficient representation and exact minimality

A representation z:S→Z is sufficient iff there is D:Z×A*→Response with
D(z(s),w)=R(s,w) for every s,w. Then z(s)=z(t) implies s≈t.
**Theorem 3.** There is a unique surjection F:z(S)→Q with
F(z(s))=q(s). Define it using any preimage s. Sufficiency makes that definition
independent of the preimage; every class is hit. Uniqueness follows because
every argument lies in z(S). Conversely, existence of such F gives a decoder
using quotient responses and Theorem 2 on z(S). A decoder on all of Z also
needs a default response on unused values; this is automatic if O is inhabited.
Sufficiency on the attained image is exactly the factorization property.
There is no uniqueness assertion on unused Z values.
Lean uses classical preimage choice; this does not supply an effective encoder.

This is a map of sets for arbitrary z. A sufficient z need not have an update:
a fine partition can split equivalent successor states while merging their
predecessors. An update requires the additional condition that z(s)=z(t)
preserves observations, enabledness, edge labels AND successor z-values.
Under that condition z(S) is a machine and F is a machine homomorphism.

The surjection gives |Q|≤|z(S)| in classical set theory; the quotient itself
attains this bound. For pointed machines first restrict to reachable states.
Every other reachable deterministic realization of the same initial complete
response has a unique surjective homomorphism to Q: send a state reached by u
to the original residual class after u. Equality of complete responses makes
this independent of the reaching word, by cancellation of its finite prefix.
It preserves observations/transitions and is onto since every Q state is
reachable. Therefore finite realizations with the minimum number of states
are isomorphic to Q. More generally any reachable behaviorally reduced
realization is isomorphic to Q, including infinite ones.

**Infinite boundary.** Minimum infinite cardinality alone is insufficient.
A machine on Nat observes n at state n, increments on a and stays on b.
Add for each n an observationally equivalent duplicate reached by b, whose
a-successor is n+1 and whose b-successor is itself. Both reachable machines
have the minimum countable cardinality, but the second is not reduced and
cannot be isomorphic to the first. Minimality must mean reducedness there.

## 4. Finite refinement completeness and shortest witnesses

Assume n>0 finite states, a finite action alphabet, and decidable equality
for the finite observations and edge labels actually occurring. P0 partitions
states by o. Recursively Pi+1 compares o and, for every action, either NONE
or (edge label, Pi-class of successor). Pi+1 refines Pi.

Induction shows: Pi-equivalence iff responses agree on all words of length
at most i. The base is ε. For a::w the signature checks exactly the
enabledness, edge and successor response needed by the recursive definition.
If Pi+1=Pi then Pi is a bisimulation, so Theorem 1 makes it ≈.
Starting with k nonempty P0 blocks, every strict refinement adds a block.
There are at most n−k strict refinements; the stabilized partition is Pn−k.
Consequently every inequivalent pair has a distinguishing word of length
at most n−k≤n−1. Checking stabilization may require one additional round.
For n=0 there are no pairs or reachable pointed machine; handle it separately.

Independent pair breadth-first search starts from (s,t), checks current
observations, then each action for enabledness, edge AND successor-observation
differences before enqueuing an equal-observation successor pair. This prevents
returning a longer edge witness while a shorter observation witness is queued.
It returns a shortest distinguishing word; if its
finite queue exhausts, the visited relation is a bisimulation. The stronger
n−k bound above follows from refinement, not merely the pair count.
No computability claim follows for arbitrary infinite state presentations.

## 5. Actual residual-budget lifting and attainability

Construct SB=S×Nat, oB(s,b)=o(s).
If d(s,a)=Some(e,t) and c(e)≤b, let
dB((s,b),a)=Some(e,(t,b−c(e))); otherwise it is None.
This observes budget inadmissibility and physical absence as the same ILLEGAL
token. It does not preserve a requested diagnostic distinguishing their causes.

**Theorem 4.** s≈t implies RB((s,b),w)=RB((t,b),w) for every b,w.
Proof: induction on w. Theorem 1 gives matching edges and successors.
Equal costs yield equal guards and residual budgets; apply induction to the
successors. This is kernel checked for the actual guard/subtraction definition.
Replacing S by Q commutes with budget lifting under (s,b)↦([s],b).

For a physically legal finite word, Nat nonnegativity gives:
all guards pass iff the sum of its edge costs is ≤b.
Proof by induction, using c+rest≤b iff c≤b and rest≤b−c.
Therefore b≤b' gives inclusion of legal word sets. For any common partial
evaluator ν of the complete response, define A_b(s) as its defined values
on those legal words. Then A_b(s)⊆A_b'(s); A_b(s)=A_b(q(s)).
Capability/intersection predicates and any declared order's finite frontiers
are consequently preserved. This does not manufacture an order, a barrier
cause, or an attained infinite-horizon limit. If ν inspects hidden state
identity rather than the response, this preservation premise fails.

## 6. Multiple contexts and the observation contract

For a nonempty set K of contexts with the SAME process/actions/enabledness, use
o(s)=(oκ(s))κ and edge observation e=(eκ)κ. Each context may have a
different observation type; the product is a dependent family where needed.
Then ≈K equals the intersection of all context response equivalences.
Proof: response equality is componentwise, with shared legality; induction
on words handles the common branch structure. A representation is sufficient
for every context iff it decodes their joint response, using the family of
decoders pointwise. Theorem 3 thus gives the unique coarsest jointly sufficient
quotient. Enlarging K refines it and yields a surjection from the finer quotient
to the coarser. No context-free architecture classification or finite encoding follows.
Budget consequences require cost to be determined by the joint edge labels;
erasing unequal costs in every context can destroy budget-guard preservation.
If contexts alter transitions, allowed interventions or hidden memory, first
specify a joint process containing those distinctions; the product argument
alone does not establish congruence.

## 7. Falsifiers, evidence levels and remaining requirements

Costs (2,0) versus (0,2) along a two-edge chain have equal completed total,
but different first responses and different first-step admission at budget1.
Equal terminal outputs likewise omit intermediate observations. Same o(s)
with an absent edge versus an edge entering UNDEFINED defeats conflating
illegality and undefined evaluation. Long chains defeat bounded test families.
Nondeterministic trace equivalence need not be bisimulation: a.(b+c) and
a.b+a.c have the same finite action traces but incompatible a-successors.

Lean checks equivalence, actual transition congruence and quotient definition,
quotient responses, sufficient-representation separation, unique/surjective
attained-image factorization, and Nat residual-budget preservation.
Finite refinement/bound, reachable-model isomorphism, the converse decoder,
multi-context product and attainability consequences are paper proofs here.
Python is independently checked, not translated into kernel-certified code.
No stochastic, approximate, continuous-state effective minimization, hidden
internal divergence, learning, architectural discovery or empirical semantics
claim follows. Finite trace semantics does not add an infinite reward,
fairness, almost-sure event or topology.

Local evidence targets R4-001/002/003/004/006/007 and the deterministic part
of R4-005; R3-001/002/003/005/006 under response-based evaluation; and
R14-002/006 for these definitions/proofs. Broader original atoms remain open.
The fixed-point closure of finite refinement is a greatest behavioral
equivalence for this supplied process, not a self-justifying theory of intelligence.
