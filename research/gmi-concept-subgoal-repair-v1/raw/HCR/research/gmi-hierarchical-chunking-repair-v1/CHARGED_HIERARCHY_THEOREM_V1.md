# Charged hierarchy construction and exact parsing — HCR-1–4

Status: finite parent specialization and falsifying repair. No novel
compression, compilation, shortest-path or hierarchy principle is claimed.

## HCR-1: exact parsing for a fixed retained dictionary

Fix a finite alphabet, a finite word x of length n, and a finite dictionary
of nonempty words. Primitive a has finite nonnegative cost c_a; each retained
word p has finite nonnegative complete invocation cost u_p. Parsing must emit
x exactly in order, without overlap or omission. Dictionary construction is
already paid separately; no semantic adequacy claim is inferred from a price.

Build vertices0,...,n. Add i→i+1 with c_(x_i), and i→i+|p| with u_p when p
matches at i. Every legal parse is a path and conversely. The backward
recurrence D(n)=0, D(i)=min_(i→j)[cost(i,j)+D(j)] is therefore exact.
Induction on n-i proves the lower bound; choosing a minimizing edge gives
an attaining parse. There are n+1 states and at most n(1+|dictionary|) edges;
matching/representation work is additional. Nonnegative zero-cost edges are
safe because every word is nonempty and position strictly advances.

Greedy longest-match fails even with all invocation and primitive costs1:
x=abcde, dictionary={abc,ab,cde}. Greedy costs3 (abc,d,e); exact costs2
(ab,cde). In aaa, aa has two overlapping occurrences but at most one call
in a legal parse. Raw substring counts are not realized reuse demands.

## HCR-2: finite acyclic acquisition with actual child calls

Supply primitives and topologically ordered rules j=0,...,m-1. Each body is a
nonempty finite sequence of primitives or earlier rule indices. Thus every
rule has a unique finite expanded primitive trace E_j. The complete finite
workload is an ordered token sequence; its full trace is known. This is an
exposed exact-output register, not learning from unknown obligations.

An initially empty retained set M records valid self-contained compiled
artifacts. Rules may always be expanded by executing their bodies, paying a
nonnegative expansion/dispatch charge d_j. A retained rule may instead be
invoked for u_j, emitting E_j exactly. For an allowed missing rule, after
its first chosen body execution one may pay s_j and retain the resulting
artifact. Admission may be delayed or refused. An already retained rule may
still be expanded when cheaper. No eviction, invalidation or other mutation
occurs. All c,d,s,u are finite nonnegative rationals for executable synthesis.

Primitive delivery a additionally costs v_a≥0 each time emitted, independent
of route. Thus all exact policies pay the SAME sum of v_a over the workload
trace; this amount is added to every recurrence endpoint and every ledger.
A compiled call emits and charges all descendant primitive actions.

The supplied compilation contract is load-bearing: s includes the construction,
validation, indexing and storage not already in the body execution; u includes
all later invocation and decoding work beyond separately charged delivery. Body execution emits its first
useful result, so retention does not charge a duplicate first service. An upper
body really calls lower artifacts when available. Later upper invocation is a
compiled implementation with its own admitted call cost, not a promise that a
recursive interpreter avoids executing its children. The model checks trace
identity but does not validate real hardware prices or an arbitrary compiler.

Separate initial/controller/synthesis costs A, terminal costs T and holding
costs must be supplied when incurred. The finite witnesses declare A=T=0 and
no holding or time-based cost; their event meter is explicit. Counted analysis
operations and description sizes are reported separately, never presented as
free physical setup. Nonzero common A,T add to every matched policy; unequal
setup or missing physical terms require a new full-lifetime comparison.

For token t and initial M, let F_t(M,N) be the minimum execution charge ending
with retained set N. Primitive execution preserves M. For rule j, concatenate
the child relations in order using min-plus composition, add d_j, and allow
an optional final s_j admission when j was missing and is allowed. Also offer
the direct u_j invocation when j∈M. Compose these relations over the workload.
The minimum over final N is the exact optimum over ALL legal history policies.

Proof: structural induction on rule order enumerates every legal token
execution, including every child-admission combination and refused/delayed
admission. For concatenation, split any execution at the actual intermediate
retained sets. Its charge is at least the min-plus expression. Conversely,
each finite minimizing child execution can be concatenated, so it is attained.
Future feasibility and cost depend only on remaining tokens and M; retaining
only the cheapest prefix to the SAME M is sound. Randomization cannot improve
a scalar minimum among these deterministic finite executions. Empty workload
costs0. This makes no claim about all grammars or all possible implementations.

The register has at most2^m retained sets, and exponentially many possible
executions; no scalable grammar-search claim is made. The checker reports
cached token states, considered transitions and execution events. Those
operation categories are not an instruction-complete physical work meter.

## HCR-3: matched classes and a refutation of universal shallowness

Primitive a reconstruction costs101; delivery of a costs1 in EVERY arm.
Rule L→a has d=0,s=1,u=100 (call work excludes the separate delivery).
Rule H→L L L L L L L L L L has d=0,s=1,u=100.
Demand H three times, starting empty in every arm. The legal action sets are
nested: no admission; admission of L only; admission of L and H.
Each admission s=1 comprises compiler1/3, check1/3 and index/storage1/3.
Every arm emits a^30 and pays30 delivery. Reconstruction charges below count
every first body execution; full totals add that same30:

- No retention: 30×101=3030; total3060.
- Lower-only optimum: 101+1+29×100=3002; total3032, saving28.
- Both optimum: 101+1+9×100+1+2×100=1203; total1233, additional saving1799.

For the lower-only lower bound, the first a costs101; each later a costs at
least100 and using a retained L requires its one storage charge. Delaying
admission cannot help because101>100. For both, if H is never admitted the
previous bound applies. If first admitted after request k≥1, that prefix
costs at least1000k+2 (the best lower-only cost for10k leaves), then H storage1
and remaining3-k calls cost at least100 each. Its lower bound is900k+303,
minimized at k=1, attained by the displayed child-call trace. Choosing not to
retain L is more expensive. These cover every admitted policy, not one heuristic.

PVR's threshold is nondecreasing when C decreases at the SAME S,U and C>U;
the increase is strict only when S>0.
It does not compare different levels with different sequences, demands or
charges. Here the lower threshold is2; after L is retained the upper body
costs1000 and its threshold is1+1/900. The second saving is the majority.
All event prices are constant, but effective upper derivation depends on
lower availability (first1002, resident1000). PVR applies conditionally to
fixed lower availability; its independent-item formula does not govern the
entire coupled hierarchy. Even two separately valid fixed-C comparisons
with (C,S,U,r)=(101,1,100,30) and (1000,1,100,3) have gains28 and1799:
there is no algebraic cross-level ordering. The actual coupled lifecycle is
proved above. No physical implementation of a 100-unit upper call is claimed.

## HCR-4: quotient identity does not choose a program factorization

The developmental quotient minimizes future-response STATE classes under a
supplied event interface. It does not identify a unique substring dictionary
or grammar. The same finite trace abcde is generated by a direct primitive
body, an {ab,cde} body or an {abc,de} body; all emit the same trace. Their
representation and execution costs need separate contracts. SEQUITUR already
permits multiple grammars satisfying its constraints. A retained sub-quotient
requires legal entry/exit and transport assumptions; its name supplies none.

The repair is a useful finite resource comparison, not a derivation of
subgoals, hierarchical planning, unknown-dynamics learning or universal depth.
