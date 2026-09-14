# Shared dependencies and memory-bounded certified reuse — SMR-1–4

Date: 2026-09-13. Status: exact registered configuration/renewal synthesis.

## 1. Strongest parents and concrete GMI contribution

[Hong and Kung (STOC 1981), §2, p.327](https://www.eecs.harvard.edu/~htk/publication/1981-stoc-hong-kung.pdf)
uses DAG configurations, predecessor-resident computation and deletion to model
memory constraints. We inherit those mechanisms, use weighted artifacts and
workspace, charge recomputation, and admit no uncharged external spill store.
We do not transplant their I/O lower bounds to proof systems.
[Checkmate (MLSys 2020), §§4.1–4.7](https://proceedings.mlsys.org/paper_files/paper/2020/file/0b816ae8f06f8dd3543dc3d9ef196cab-Paper.pdf)
explicitly optimizes weighted DAG rematerialization with peak-memory constraints.
Its implemented stage/order restrictions are acknowledged; this small exact
configuration graph is not a reproduction or performance comparison to Checkmate.
No neural component is used in the present mechanism or checker.

[CRI](CERTIFIED_REUSE_INVALIDATION_THEOREM_V1.md)'s one-artifact renewal and
finite-horizon policy laws remain valid in their scope. The missing bridge is
joint acquisition/retention under shared dependencies and transient workspace.
We apply standard finite shortest paths and CRI's adaptive dynamic-programming
parent to an explicit richer state. No new pebbling theorem or optimizer is
claimed. The result is a constructive GMI resource boundary with finite witnesses.

## 2. Fully charged finite register

Fix a finite topologically indexed DAG V. Node v has predecessor set P_v,
positive integer retained size w_v, nonnegative integer build scratch z_v, and
finite nonnegative exact rational build/certification c_v, service u_v and release
d_v costs. Holding costs h per retained unit per interval; observing an interval
event costs o. All build operations must be admitted, uniformly successful and
fully charged, including search failures and native checking needed for that
operation. Build cost includes allocation and temporary-workspace release.
An unchecked Boolean is not semantic proof of this admission.

A resident set C records **currently certified valid** artifacts. A constructed
artifact remains usable after its operands are evicted: w_v must cover whatever
self-contained representation its later use requires. A dangling reference to
an evicted proof does not satisfy this premise. The DAG records computational
and context-validity dependencies, not compulsory permanent operand residence.

The artifact arena has finite integer allowance M≥0. Controller, program,
validity metadata, base runtime and service-interface workspace require separate
reserved memory under [BCR](BOUNDED_CONTROLLER_RESOURCE_THEOREM_V1.md). For a
physical total allowance, M is the verified residual after that reservation.
Service uses no additional variable arena workspace in this register; a different
service implementation needs its own explicit workspace condition. No external
precomputation, transfer or spill store supplies artifacts for free. Initial C0
must fit and be certified; its prior acquisition is paid separately or common.
All principal witnesses start empty and acquire under the same M throughout.

Admitted within-request transitions, including after service, are:

- Drop v∈C: C→C\{v}, cost d_v.
- Build missing admitted v with P_v⊆C and w(C)+w_v+z_v≤M:
  C→C∪{v}, cost c_v. Operands and new output coexist; no implicit sliding or
  in-place overwrite is allowed. Temporary scratch is released afterward.
- Serve the current request r only when r∈C, paying u_r exactly once.

Each request has finite preparation, service and finite post-service work;
post-service prefetch and release are both admitted. The controller then commits
to the interval. For every nonfinal interval t, pay h·w(C)+o, observe a registered
finite event e of probability p_t(e), and remove I(e)∩C. Here I(e) contains its
seed nodes and **all DAG descendants**, even through absent/evicted ancestors.
Pay Σ_(v∈I(e)∩C)d_v for this forced cleanup; then the next request begins. There is no final holding/observation charge.
No terminal cleanup or salvage obligation is part of this request register.
No stale scaffold outside C is retained in this register; valid shared nodes
supply the repair scaffold. Retained damaged objects require additional states.

Requests r_0,...,r_(H−1) are fixed. Event distributions are independent across
intervals, exactly normalized, and events arrive only at interval boundaries.
Everything affecting future feasibility, costs or event law is in (t,C).
Unknown/context-dependent dynamics need an augmented state, not this formula.
Zero logical-release or event costs are authored model premises, not measured
claims that physical deletion or validity inspection is free.

## 3. SMR-1 — exact memory-feasible configuration shortest paths

Let C_M={C⊆V:w(C)≤M}. Form the directed graph of admitted build/drop moves and
let d_M(C,P) be its minimum total work, +∞ when no path exists. Every feasible
within-phase execution is a graph path, and every graph path is executable with
its declared peak workspace. Thus d_M is its exact optimal work.

**Proof.** The edge conditions are precisely the operation prerequisites and
instantaneous memory condition. Induct over transitions for both directions.
Nonnegative edge costs let us erase repeated-configuration cycles without
increasing work. A finite optimum, when feasible, is attained by a simple path
of at most |C_M|−1 moves. This also handles zero-cost cycles. Shortest-path
algorithms supply both a value and a concrete instruction sequence.
A set fitting M need not be reachable from the admitted initial configuration.

## 4. SMR-2 — strongest exact adaptive lifecycle comparison

Set V_H(C)=0. For t<H let

    K_t(Q)=0                                      if t=H−1;
    K_t(Q)=h·w(Q)+o+Σ_e p_t(e)[d(Q∩I(e))+V_(t+1)(Q\I(e))] otherwise.
    V_t(C)=min_(P,Q∈C_M, r_t∈P)
               [d_M(C,P)+u_(r_t)+d_M(P,Q)+K_t(Q)].

Here d(B)=Σ_(v∈B)d_v. Only positive-probability events enter the sum; an infeasible supported child
makes that candidate infeasible. Empty minima are +∞. The implementation uses
None for impossibility, never a feasible infinite resource allowance.

**Proof.** An arbitrary successful history policy induces some pre-service P
and pre-interval Q. Its two phase costs are at least their respective shortest
paths. Conditional continuation is bounded below by V_(t+1) at each observed
successor, by induction on remaining requests. Taking the minimum gives a lower
bound for every history policy. Conversely, minimizing finite choices, their
concrete shortest paths and minimizing child policies attain the recurrence.
Thus no prescribed eviction, repair or prefetch heuristic is the comparator.
It is the entire admitted adaptive policy class. Nonnegative cycles can be
erased separately before/after service; a configuration may repeat across the
service boundary, which changes the request-completion state.

For support-worstcase work replace the expectation by the maximum over its
positive-probability children. This is a separate objective. Varying M gives
constructively attained work/memory tradeoffs within this representation; it
does not certify controller/code feasibility beyond the reserved ledger.
Development shortest-path and policy-search operations are charged separately
from execution. Receipts count settled configurations, inspected edges, terminal
configuration choices and path comparisons; these are explicit categories,
not a claim to count every parser/allocation instruction or all wall time.

## 5. SMR-3 — falsifying independent caching, then constructive revival

Let p→a and p→b, all sizes 1, build costs (4,1,1), leaf service cost 1, no
scratch, release, holding or observation work. Start empty; request a,b,a,b.
The knapsack set {a,b} has size 2 but is unreachable with M=2. To create the
first configuration containing both leaves, its last leaf build would require
p, the other leaf and its new output simultaneously: size 3. This contradicts
M=2. At M=3, build p,a,b and drop p; joint acquisition costs 6, whereas summing
two independent acquisitions gives 5+5=10. Both reachability and costs couple.
This refutes an independent-item extension, not CRI's stated one-artifact law.

At M=1 no leaf can be built. At M=2 retain shared p and evict/rebuild the
alternating leaf: build p once, four leaves and serve four requests, total 12.
This is optimal: p must be built, and the two leaves can never coexist, so
alternation requires four leaf constructions. At M=3 build both leaves once
and retain them, total 10, matching the necessary two constructions. A matched
forced-release policy costs 24. That policy is a reference, not the strong
adaptive parent; the independent complete-policy oracle below is the latter.

Now independently invalidate seed p with probability q between requests,
thereby invalidating every retained descendant. For M=2, optimal path work is
12+4K, where K counts the three invalidating intervals. For M=3 it is
10+4K+1_(e1 or e2)+1_(e2 or e3): each repeated leaf needs rebuilding precisely
when its certificate was invalidated since its previous request. No policy
can omit those required builds, and on-demand construction attains them.
Hence exact expected optima are

    J_2(q)=12+12q;    J_3(q)=10+16q−2q²;
    J_2(q)−J_3(q)=2(1−q)².

At q=1/2 these are 18 and 35/2; both support-worstcase optima are 24. A positive
expected memory benefit does not improve this worstcase. For requests a,a,
invalidating only a after the first service costs 8 (shared p survives), while
invalidating p costs 12. Removing only resident seed p and serving a stale
cached descendant is inadmissible, even if p was already evicted.

## 6. SMR-4 — post-service prefetch must not be omitted

Change p's size to 2, set h=1, M=3 and request a,b without invalidation.
After serving a, drop a, build b from retained p, then drop p. Hold only b;
total work is 9. Mandatory builds and services cost at least 8; a nonempty
interval store adds at least 1 holding, while an empty one forces rebuilding p.
Thus 9 is optimal. If post-service actions are restricted to release, the best
choice retains p alone, pays holding 2, then builds b, total 10. Both leaves
cannot coexist during construction at M=3 because p+a+b needs 4. Retaining
nothing instead requires rebuilding p. Thus prefetch is a genuine additional
optimal action here, and is included by d_M(P,Q), not forbidden by comparison.

## 7. Exact finite evidence and remaining boundary

The checker compares configuration shortest paths against independently
constructed simple action traces on all eight topologically indexed three-node
DAGs, three memory values and 1,032 configuration pairs. Separately, 24 two-node
lifecycle instances vary dependencies, memory, costs and hazard q∈{0,1/2,1}.
Every complete history-policy tree with simple within-phase traces is enumerated,
then run against every positive-probability event history: 43,968 policy trees,
84,400 direct executions, 18 feasible instances and six true negatives.
Cycle erasure proves that this finite policy class contains an optimum.
Expected and support-worstcase values match independently; synthesized policies
are directly re-executed with workspace and certificate-availability checks.

Fifteen tests also cover forced cleanup, scratch, no final holding, invalid builders, descendant
invalidation, zero-cost cycles, malformed/nonfinite resources, a matched CRI
repair instance, and standalone `-I -B` execution. Evidence is
`GRAND_GMI_SHARED_REUSE_RECEIPT_V1.json`. The scripts and authored costs are not
measurements on a prover. Shared damaged scaffolds, unknown hazards, concurrency,
external storage and concrete physical/controller deployment remain separate
registered obligations; no universal GMI or proof-performance closure is claimed.
