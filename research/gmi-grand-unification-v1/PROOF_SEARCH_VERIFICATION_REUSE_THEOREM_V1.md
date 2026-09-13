# Proof search, verification and resource-feasible reuse

Date: 2026-09-13. Status: scoped theorems, constructive finite checks.
Adapted from unmerged commits `af02237b`, `e63ead17`, `699f438e` on
`gmi/grand-proof-search-v1`; this revision preserves the laws while repairing
their interpretation and replacing formula-recitation checks.

## PVR-1: finding an accepted certificate

Let there be `N>=1` candidates, a deterministic equality-style binary verifier,
and no other proof-specific information. If the admitted worlds contain each
possible unique accepted candidate **and** the all-rejected world, deciding
whether this finite candidate set contains an accepted certificate has exact
deterministic worst-case query cost `N`. On the all-rejected transcript, every
unqueried candidate could still be the unique accepted one. Exhaustion attains
the bound. Under the promise of exactly one accepted candidate, identification
instead costs `N-1`: the last candidate is forced. Requiring an observed positive
verification before delivery adds the final query on that worst-case path.

This decides finite verifier acceptance, not mathematical truth. Soundness and
completeness relative to a theorem predicate are separate premises; see
[GP5–GP6](FORMAL_REASONING_PROOF_SEARCH_THEOREM_V1.md).
With uniform positive verification cost `v`, the corresponding verification
work is `Nv` or `(N-1)v`; controller and candidate-generation costs are additional.
Thus one cheap verification does not make discovery cheap. Rich tactic errors,
known proof grammar, multiple accepted candidates or quantum oracle access
change the registered problem and require different bounds.

## PVR-2: exact semantic reuse requires a certificate transport

Equality of every legal future response defines a proof-state quotient.
Executable quotient search additionally needs class-consistent legal actions,
successors and protected costs. Raw certificate substitution is a stronger
operation. For source context `x`, target context `x'` and proof `p`, require an
admitted transport `t` with `V(x,p)=1 => V(x',t(x,x',p))=1`. Its construction,
lookup, adaptation and validation costs must be charged. Without a transport
proof, check the transported certificate before accepting it.

Counterexample: contexts `0,1` have certificates `p0,p1`, with `V(i,pj)=[i=j]`.
Their sole registered tactic `solve` succeeds in both, so those acceptance-only
continuation profiles agree. Reusing `p0` verbatim in context `1` fails.
Refining the profile to individual certificate attempts distinguishes the
contexts; alternatively the justified transport `pi -> pj` preserves acceptance.
Neither abstract solvability nor a shared lemma name licenses substitution.

## PVR-3: the single-class break-even law

For `r>=1` occurrences of a valid reusable lemma, let `C,S,U>=0` be the
fully charged scalar derivation, one-time storage/indexing, and subsequent
lookup/transport/check costs. Assume no invalidation or eviction, stable
validity and constant independent costs. Then

`fresh = r C`, `retain = C + S + (r-1) U`.

Subtracting gives strict reuse benefit exactly when
`S < (r-1)(C-U)`. If `U>=C` it cannot be strictly beneficial; if `U<C`,
the threshold is `r > 1 + S/(C-U)`. Equality ties these two registered policies
only. A third implementation could dominate both; no global frontier claim
follows. Memory and time may instead be separately retained Pareto coordinates.
The independent request-by-request scheduler in the finite check allows
derivation, delayed admission and reuse and verifies the optimum, including
cost regimes where retaining knowledge is harmful.

## PVR-4: capacity couples individually useful lemmas

Consider `m` independent classes with known multiplicities `r_j` and fixed
positive integer retained sizes `b_j`. Register a **static** admission policy:
each selected class is retained after its first derivation for the workload,
with reserved memory `sum b_j <= B`; unselected classes are always rederived.
No class shares derivation work or storage with another, and all ancillary
costs are included in `(C_j,S_j,U_j)`. Define

`g_j = (r_j-1)(C_j-U_j)-S_j`, `F = sum_j r_j C_j`.

The exact optimum over these admitted policies is

`J*(B) = F - max_{K subset {1..m}, sum_{j in K} b_j <= B} sum_{j in K} g_j`.

Proof: each legal subset has cost `F-sum_{j in K}g_j` by the independent
cost identities. Subset admission implements each feasible point, so minimizing
those costs is precisely the displayed maximization. The empty subset is legal;
negative gains never have to be taken. Finite subsets ensure attainment.

With integer memory, the standard 0–1 knapsack recurrence is
`V_j(b)=max(V_{j-1}(b),g_j+V_{j-1}(b-b_j))`, omitting the second term when
`b<b_j`, and `V_0(b)=0`. Splitting optimal subsets by membership of class `j`
proves the recurrence and supplies a constructive schedule by backtracking.
Its computation is itself a charged development cost if used by the machine.

Concrete falsifier for independent/greedy admission: gains `(7,5,5)`, sizes
`(4,3,3)`, capacity `6`. All are individually useful; only the second and third
fit together and save `10`. Descending gain and gain-per-byte both choose the
first, saving only `7`. The memory constraint changes the optimal morphology.

## Parent mathematics and exact boundary

Minton's [utility analysis of explanation-based learning](https://doi.org/10.1016/0004-3702(90)90059-9)
already makes learned knowledge pay for its use; the break-even comparison
is an application of that established problem. The capacity solution is the
standard [0–1 knapsack recurrence](https://courses.csail.mit.edu/6.006/fall11/rec/rec21_knapsack.pdf),
not a new optimization algorithm. GMI adds the explicit mapping from certified
semantic reuse to retained resource coordinates and constructible policies.

General proof-DAG scheduling does **not** satisfy independent fixed costs.
[Pebbling and proof-space tradeoffs](https://arxiv.org/abs/1307.3913)
model shared dependencies, eviction and recomputation; the mature
[pebble implementation](https://github.com/MassimoLauria/pebble) searches those
configuration graphs. That is the appropriate parent when these effects occur.
The static theorem gives a legal policy upper bound there only after its
actual schedule is shown feasible; it is not a universal optimality theorem.

The finite witness checks exact query trees against PVR-1, exhaustive request
traces against PVR-3, and direct subset execution against PVR-4. It tests the
certificate-transport and greedy counterexamples. These authored exact cases
establish neither large-scale proof improvement nor measured acquisition costs.
Unknown future multiplicities, dependent lemmas and invalidation require a
registered online/dependency model and fresh comparison before deployment.
