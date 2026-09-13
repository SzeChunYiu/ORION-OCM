# Memory, external access and lifecycle selection

Status: exact conditional laws for a static independent-bit workload, including arbitrary coded retained state and adaptive probes.
The proof uses standard entropy and prefix-coding inequalities; see [sources](ECOLOGY_SOURCES.md).
This is a resource law for mechanisms, not a claim that caches, retrieval, or information bounds originated in GMI.

## M1. Interface and all side information

Let X=(X_1,…,X_n) be independent fair bits, n≥1.
Let R contain all random seeds and fixed public information, independent of X.
Preprocessing reads X only through one-bit external probes and retains state S, a function of R and its completed transcript.
For each R, S has at most 2^M possible values, where M is a fixed nonnegative integer.
All X-dependent parameters, generated code, addresses, retained transcripts and metadata count in S.
X-independent program/index descriptions and random seeds are not information about X, but their physical storage and execution still cost resources.

In a query, J is independent of (X,R), with known probabilities p_i, and the required answer is X_J.
The algorithm receives (S,J,R), can perform adaptive external one-bit probes, terminates almost surely and returns the exact bit almost surely.
Each probe address and the stop decision are functions only of its present view and previously returned bits.
There are no answer-revealing timing channels, uncharged side information, external writes carrying preprocessing results, or hidden multibit responses.
Preprocessing state is frozen for the query phase; each query starts from that state and retains no new X-dependent information across queries.
This static assumption is essential for the lifecycle optimum M4, which is not a theorem about general online caching.

## M2. Entropy lower bound for arbitrary adaptive query programs

For any fixed (s,j,r), let T be the finite string of returned probe bits until termination.
The set of possible completed strings is prefix-free: if the program stops after t, the same fixed view and t cannot also demand another probe.
Addresses need no additional transcript symbols because they are determined by the fixed view and preceding returned bits.
The standard binary prefix inequality gives H(T|S,J,R)≤E|T|, including countable variable-depth trees.
For completeness, Kraft gives K=Σ_t 2^{−|t|}≤1. With q_t=2^{−|t|}/K, nonnegativity of relative entropy yields

    H(T) ≤ E|T| + log₂K ≤ E|T|.

Apply this conditionally; if expected length is infinite the lower bound is immediate, otherwise integrate the conditional inequality.
Since the exact answer is determined by (S,J,R,T), data processing gives

    r_query := E|T| ≥ H(X_J|S,J,R)
                       = 1−Σ_i p_i d_i,
    d_i := I(X_i;S|R).                                     (9)

Here 0≤d_i≤1. Independence of X's bits and R gives

    Σ_i d_i = n−Σ_i H(X_i|S,R)
             ≤ n−H(X|S,R)=I(X;S|R)≤H(S|R)≤M.              (10)

Thus, after sorting p_(1)≥…≥p_(n),

    r_query ≥ 1−Σ_{i=1}^{min(M,n)}p_(i).                   (11)

Proof of the last step: a linear weighted sum on 0≤d_i≤1, Σd_i≤M is maximized by filling the largest weights first.
Swapping mass from a smaller to an unfilled larger weight never decreases the sum; iterate to a vertex.
Retaining the top min(M,n) database bits attains (11): answer a hit from state, otherwise probe exactly X_J once.
The selected indices are fixed from p, so they carry no additional X-information; their real address/lookup/code costs remain in the implementation ledger.
For uniform requests, (11) is r_query≥max(0,1−M/n).
The lower bound covers coded S and multistep adaptive queries, rather than assuming a cache in its hypothesis.

## M3. Acquisition cannot create retained information for free

Let T_A be preprocessing's returned-bit transcript and A=E|T_A|.
For fixed R it is again a prefix code, so H(T_A|R)≤A.
As S is a function of (T_A,R), data processing and (10) give

    A ≥ I(X;S|R) ≥ Σ_i d_i.                                (12)

Repeated reads and discarded discoveries are charged in A even when they contribute no retained information.
A procedure supplied the whole database as its initial input violates this acquisition interface; its input ingestion must be modeled separately.

## M4. Exact optimum for three specified static resource coordinates

Assume a hard retained-state bound M≤M_max with M_max integer, deterministic future query count H≥0, and nonnegative prices c_A,c_M,c_R.
Each query has request law p independent of X,R; it starts from the frozen S. Equivalently H may be a nonnegative real external economic multiplier, without a stochastic-lifetime claim.
An expected random count may replace H only for an exogenous count independent of the database, preprocessing and query outcomes, with conditional request law p for each included query; adaptive stopping does not justify multiplying unconditional r_query by E[H].
Here c_M is the total retention charge per retained bit for this lifecycle, not an uncharged per-time storage rent.
Consider only the projected resource score

    C = c_A A + c_M M + H c_R r_query.                     (13)

The optimum over all M1 algorithms is

    min_{0≤m≤min(M_max,n), m integer}
      [(c_A+c_M)m + H c_R(1−P_m)],   P_m=Σ_{i=1}^m p_(i).  (14)

Proof: let a=c_A+c_M. Equations (9), (10), (12) lower-bound (13) by

    H c_R + Σ_i (a−H c_R p_i)d_i,
    0≤d_i≤1,  Σ_i d_i≤M_max.                               (15)

This polytope has integral vertices: if two coordinates are fractional, move equal mass between them until one becomes integral; if one is fractional, move it to 0 or 1, since the integer sum bound cannot be uniquely tight there.
A linear objective attains its minimum at a vertex. Exchange larger p first, and include only beneficial coordinates, up to M_max; this gives (14).
Conversely the corresponding static cache uses A=m, M=m and r_query=1−P_m, attaining every candidate in (14).
Ties admit multiple optima. For uniform p, each extra allowed bit is beneficial exactly when H c_R/n>c_A+c_M.
At equality all retained sizes tie in this projected score; below it m=0 is optimal, above it m=min(M_max,n) is optimal.

Equation (14) optimizes exactly the acquisition/retention/external-bit-probe coordinates defined in (13).
CPU, routing, fixed code, index construction, addresses, intermediate workspace, synchronization and measurement overhead are not zero; the complete GMI score must include them separately.
Those extra terms can change the winning realization. Adding arbitrary implementation-specific overhead does not preserve a universal optimum claim without another proof.
No lifetime gain is realized until the queries actually occur; a changed workload or invalidation requires updated accounting.

## M5. Approximate answers without external query probes

Suppose J is uniform and the binary predicted answer has error probability ε≤1/2, with no query-time probe.
Given the view and the error indicator E, the target bit is determined: it is the prediction if E=0 and its complement otherwise.
Thus H(X_J|S,J,R)≤H(E|S,J,R)≤h₂(ε), by concavity of binary entropy.
Combining (9)'s entropy expression and (10) yields

    M ≥ n[1−h₂(ε)].                                        (16)

This is a necessary condition, not a finite-n attainment theorem. The output is binary; abstention must be assigned an explicit loss/obligation.

## M6. Exact residual state and counterexamples

More generally, if N reachable histories are pairwise distinguishable by admitted common future continuations requiring distinct outputs, an exact deterministic state machine needs at least N retained states.
If two such histories shared one state, the same continuation with the same side information would generate the same response, contradicting distinguishability.
Hence at least ceil(log₂N) state bits are necessary. A finite residual quotient realizes the bound in number of states when its transitions are well-defined and executable.
This inherited automata fact forces memory, not recurrent neural parameterization or a particular state encoding.

If X_i=B for every i, one bit stores the entire database: the independence premise in (10) is indispensable.
If J leaks information about X, (9)'s uniform one-bit prior entropy need not hold.
An infinite-precision real encoding X is not one bit of state. Uncharged generated code and external preprocessing writes also invalidate M1.
Carrying a miss's returned bit into the next query changes the static premise; M4 cannot be applied unchanged.
Any admitted coded scheme violating (11), or achieving a lower (13) than (14), would falsify the implementation/accounting of these exact scoped laws.
