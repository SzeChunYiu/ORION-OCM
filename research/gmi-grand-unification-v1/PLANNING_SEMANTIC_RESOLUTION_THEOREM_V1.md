# Grand GMI Planning Semantic-Resolution Theorem V1

Status: **THEOREM + EXACT FINITE WITNESSES**  
Date: 2026-09-12

## 0. Planning is not one complexity

A plan can be required at different semantic resolutions. An obligation may require:

- only whether success is possible;
- only the next action;
- a finite plan prefix;
- the entire successful trajectory.

Grand GMI therefore measures planning against the protected obligation, not against a convention that the whole latent plan must always be reconstructed.

This tranche derives two complementary planning regimes:

1. **black-box verifier search**, where goal candidates can only be tested;
2. **known transition-congruent semantic state**, where dynamic programming can operate on an exact quotient rather than a raw history tree.

---

## 1. Equality-verifier class identification

Let a unique hidden candidate lie in a finite set partitioned into semantic classes of sizes

\[
n_1,\ldots,n_K,\qquad N=\sum_i n_i.
\]

A verifier query names one candidate and returns `YES` iff it is the hidden candidate. The obligation requires only the correct semantic class, not the exact candidate.

**PSR-1 — Verifier Semantic-Class Theorem.** The minimum deterministic worst-case number of equality-verifier queries required to identify the semantic class is

\[
\boxed{
Q^*=N-\max_i n_i.
}
\]

**Upper bound.** Leave one largest class unqueried and exhaustively query every candidate in all other classes. A `YES` identifies its class immediately. If all `N-max_i n_i` queries return `NO`, the hidden candidate must belong to the unqueried class.

**Lower bound.** An adversary can answer `NO` while candidates from at least two semantic classes remain possible. To certify a class without a `YES`, every candidate outside that class must have been ruled out. The cheapest class to leave unresolved is a largest class, so at least `N-max_i n_i` negative queries are required in the worst case. QED.

This theorem is a special exact epistemic-acquisition law for a verifier-only observation channel.

---

## 2. Plan-prefix resolution law

Consider a full `b`-ary plan tree of depth `d`. Exactly one leaf is successful. A query proposes a complete leaf and receives an exact success/failure verdict. No internal node supplies information about the goal.

The obligation requires only the first `q` action symbols of the successful leaf, where

\[
0\le q\le d.
\]

There are `b^q` obligation classes, one for each prefix, and each contains `b^(d-q)` leaves. Applying PSR-1 gives:

**PSR-2 — Plan Semantic-Resolution Law.**

\[
\boxed{
Q_{plan}(b,d,q)=b^d-b^{d-q}.
}
\]

Boundary cases:

\[
Q(b,d,0)=0,
\]

because no plan symbol is required, while

\[
Q(b,d,d)=b^d-1,
\]

for exact full-leaf identification.

For only the first action (`q=1`):

\[
\boxed{
Q(b,d,1)=(b-1)b^{d-1}.
}
\]

Thus tiny output width does not imply cheap planning.

### Canonical witness

At `b=2`, `d=10`, `q=1`, the answer is one bit but

\[
Q=2^{10}-2^9=512
\]

worst-case verifier calls.

This is a planning-specific realization of the Grand-GMI information/computation separation: semantic output width is one bit while transformation/search cost grows exponentially with depth.

---

## 3. Search morphology depends on available process structure

PSR-2 is a black-box lower bound. It disappears when the physical/process boundary exposes additional structure.

A heuristic, transition model, admissible abstraction, value function, causal structure, proof certificate or intermediate verifier changes the legal information channels and therefore changes `kappa`, `tau` and the planning frontier.

Accordingly:

`EXPONENTIAL_VERIFIER_SEARCH_IS_NOT_A_UNIVERSAL_PLANNING_LAW`.

It is the exact law for the declared leaf-equality-verifier channel.

---

## 4. Transition-congruent semantic planning state

Let a finite deterministic planning process have states `S`, actions `A`, transition `T`, goal predicate `G` and finite horizon `H`.

Let `~` be an equivalence relation satisfying:

1. **goal respect**: `s~s' => G(s)=G(s')`;
2. **right congruence**: for every action `a`,

\[
s\sim s'\implies T(s,a)\sim T(s',a).
\]

Then the quotient transition

\[
\bar T([s],a)=[T(s,a)]
\]

is well-defined.

Define exact-horizon reachability recursively:

\[
V_0([s])=G(s),
\]

\[
V_{t+1}([s])=\bigvee_{a\in A}V_t(\bar T([s],a)).
\]

**PSR-3 — Semantic Quotient Planning Theorem.** For every state `s` and remaining horizon `t<=H`, quotient dynamic programming returns exactly the same reachability verdict and successful first-action set as exhaustive planning over raw action histories.

**Proof.** Goal respect proves the base case. Right congruence makes each quotient successor independent of representative. Induction on `t` then makes the action-wise recursive verdict identical to the ground process. QED.

If the quotient has `m` states, the finite recursion requires at most order

\[
O(Hm|A|)
\]

quotient transition/value checks, rather than enumerating `|A|^H` raw action histories.

When the Grand-GMI exact semantic response quotient is itself right-congruent for the declared planning process, it supplies such an exact planning state automatically.

---

## 5. Raw-history explosion can be semantically null

A binary action process has `2^H` length-`H` action histories and `2^(H+1)-1` nodes in its full raw tree. Yet a finite semantic state can collapse those histories if future obligation response depends only on a small sufficient state.

The frozen microscope uses modular-state systems:

\[
s_{t+1}=(s_t+a_t)\bmod m,
\qquad a_t\in\{0,1\},
\]

with terminal goal `s=0`. Exhaustive action-sequence enumeration and quotient DP agree exactly for all tested states/horizons.

For `m=2`, depth 12 contains **4,096** complete raw histories and **8,191** raw tree nodes but only **2** process states are required by the exact quotient representation.

This does not say every planning problem has a tiny quotient. It identifies exactly what structure is needed for raw-history compression to be lawful.

---

## 6. Connection to epistemic acquisition

The black-box unique-goal problem is an epistemic-acquisition problem:

- hidden world = successful leaf;
- intervention = verifier query;
- observation = success/failure;
- obligation quotient = required plan prefix.

So PSR-2 is not a new primitive law. It is a closed-form corollary of obligation-relative epistemic acquisition for a highly symmetric hypothesis family.

This yields the recursive chain

\[
\boxed{
\text{planning obligation resolution}
\to
\text{goal-leaf semantic quotient}
\to
\eta_\Omega
\to
\tau_{search}
\to
\text{search/planner morphology}.
}
\]

---

## 7. Parent subtraction

Search theory, deterministic planning, dynamic programming, MDP/state abstraction, bisimulation/homomorphism and decision-tree/search lower bounds are established parent theories.

Grand GMI does not claim invention of those algorithms. The residual synthesis is:

1. define the plan target by the obligation's semantic resolution rather than full hidden-plan identity;
2. derive the exact verifier-search burden of that quotient;
3. separate this transformation cost from the small output-information width;
4. switch to quotient dynamic programming when the declared process supplies a lawful transition-congruent semantic state.

This explains, in one typed framework, why planning may range from exponentially hard black-box search to compact dynamic programming without changing the word `planning`.

---

## 8. Exact microscope

`grand_gmi_planning_resolution_checks_v1.py` contains deterministic exact checks:

- **1,360/1,360** class-size vectors (`2..5` classes, each size `1..4`) independently solve to `N-max n_i` under minimax equality-query dynamic programming;
- **18/18** small `b`/`d`/`q` plan-prefix cells match `b^d-b^(d-q)`;
- **180/180** modular planning reachability values match exhaustive action-sequence enumeration;
- **160/160** successful first-action sets match;
- binary depth-12 raw-tree witness: `4,096` complete histories / `8,191` nodes / `2` quotient states;
- binary depth-10 first-action witness: one output bit / `512` worst-case leaf-verifier calls.

Aggregate terminal:

`GRAND_GMI_PLANNING_RESOLUTION_TRANCHE_ALL_GREEN`.

---

## 9. Scope and falsifiers

PSR-1/2 assume a unique hidden candidate, exact equality verifier, deterministic sequential queries and worst-case exact identification. Multiple goals, noisy verifiers, approximate success, informative internal feedback or probabilistic source laws define different channels and must be re-derived.

PSR-3 assumes a declared exact deterministic transition process and a goal-respecting right congruence.

Finite falsifiers are direct:

1. an equality-verifier class instance whose minimax cost differs from `N-max n_i`;
2. a plan-prefix instance violating `b^d-b^(d-q)` under the declared channel;
3. a goal-respecting right congruence for which quotient DP changes a reachability verdict or successful first-action set;
4. any mismatch in the frozen exact receipt.