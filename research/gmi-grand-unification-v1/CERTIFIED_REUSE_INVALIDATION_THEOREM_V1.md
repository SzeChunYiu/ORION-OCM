# Certified reuse after invalidation — CRI-1–3

Date: 2026-09-13. Status: conditional laws and exact finite policy witnesses.
New CRI identifiers do not replace the existing RP12/RP13 semantic-state laws.

The source one-shot law at unmerged commit
[5a3c7969](https://github.com/SzeChunYiu/ORION-OCM/blob/5a3c796919e0925601ed98617124eaa1f9c90e59/research/machine-intelligence-morphogenesis-v1/GMI_EFFECTIVE_REUSE_HORIZON_LAW_V1.md)
correctly stops savings at invalidation and explicitly excludes renewal.
Its numerical checks evaluate the formula with floating-point examples.
The missing stage is **recovery of certified validity**, not that formula.
[PVR-3](PROOF_SEARCH_VERIFICATION_REUSE_THEOREM_V1.md) separately assumes
stable validity. Neither result licenses reuse after its certificate expires.

## 1. Register, correctness and complete charged lifetime

Fix H>=1 requests, exact finite nonnegative scalar costs A,R,C,U,M, U<=C,
and q in [0,1]. The scalar valuation and matched successful-answer obligation
are fixed before comparison. The three fully observed states are:

| State | Retained object | Admitted operations |
|---|---|---|
| cold | no reusable structure | fresh answer, or acquire/serve then keep or release |
| valid | certified reusable structure and its scaffold | reuse then keep or release |
| damaged | invalid certificate; repairable scaffold retained | fresh/keep or abandon; repair/use or rebuild/use, then keep or release |

C is the fully charged fresh-answer cost; U is protected service using a
valid structure. A is acquisition, indexing and initial certification cost
before such service. R is certified incremental repair and revalidation cost,
also before service. M charges holding the structure or damaged scaffold for
one between-request interval. No storage charge occurs after the final request.
Logical release immediately after service is an admitted zero-cost operation,
before any holding charge or hazard. This does not mean physical destruction
is free: nonzero release work requires its own charge in an extended graph.
Acquisition/repair work includes all candidate failures, checking and control
needed for the admitted operation. Version/validity observation costs are
included in these registered service/transition charges. If they differ by
state, use distinct charges in a larger graph instead of dropping them.

A fixed residual-store size b must fit the admitted memory allowance. It is
retained in both valid and damaged states and is charged by M under the chosen
valuation; raw bytes and time remain separate coordinates when not scalarized.
Full reacquisition has R=A under these charges. R<A requires an admitted repair and
sufficient retained information; naming a cheaper number is not a mechanism.

Correctness is a premise: acquisition and fresh answering satisfy the same
obligation; a repair maps every admitted damaged context/scaffold to a native
accepted certificate before reuse. Stale output is never served. If a repair
attempt fails, its work and subsequent fallback/retry are charged; the constant
R transition is unavailable unless its total-success/cost claim is warranted.
For the finite checker, `certified` is an explicit model-admission parameter,
not a substitute for this semantic proof. With it false, only full rebuilding
and fresh answering remain available from damage.

After each nonterminal request, holding a structure costs M; at the end of
that interval an independent Bernoulli(q) event invalidates any valid artifact.
Damage stays damaged until repaired/rebuilt. Fresh answering alone does not
construct reusable structure. There is no downtime, capacity-forced eviction, hidden validity,
terminal salvage or other uncharged action in this register. Those effects
require explicit additional states/costs. This is a finite configuration graph.

## 2. CRI-1 — a pathwise identity, then an expected renewal law

Consider the fixed policy: acquire for the first request, reuse while valid,
and repair every invalidation before serving the next request. Let K be the
number of invalidating intervals, and Delta=C-U. Its exact lifetime cost and
gain relative to H fresh answers are

    J_H = A + H U + (H-1) M + K R,
    G_H = H Delta - A - (H-1) M - K R.

Proof: charge acquisition once, service H times, holding H-1 times, and repair
once for each invalidation that precedes another request. This pathwise
identity requires no stochastic independence. If K<=k is guaranteed, its gain
is at least H Delta-A-(H-1)M-kR. A positive expectation is a different claim.

Under the stated independent constant hazard, E[K]=q(H-1), so

    E[G_H] = H Delta - A - (H-1)(M+qR).

This is an expected-benefit criterion for this policy, not its optimality.
For q>0, post-repair cycle lengths L are iid geometric with E[L]=1/q.
A cycle has service/holding cost L(U+M) and repair cost R. Renewal/reward
therefore gives long-run gain per request Delta-M-qR; the single initial A
and final holding convention vanish in that limit. For q=0, the same limiting
value follows directly from the finite identity, without a renewal argument.

One-shot acquisition instead has expected gain

    eta_H Delta - A - M eta_(H-1),
    eta_n = sum_{t=0}^{n-1}(1-q)^t, eta_0=0,

when it abandons permanently upon first invalidation. Its saturation cannot
be applied to a process with certified repair. With M=q=0 and
A=C+S-U=Delta+S, CRI-1 reduces exactly to PVR-3:
G_H=(H-1)(C-U)-S. This mapping avoids charging the first derivation twice.

## 3. CRI-2 — the stronger adaptive policy parent

Let N_h,D_h,V_h be the optimal expected costs with h requests remaining from
cold, damaged and valid states. Set all three values to zero at h=0. Write
m_h=M if h>1 and zero otherwise, and

    T_h = m_h + (1-q)V_(h-1) + qD_(h-1).
    B_h = min(T_h, N_(h-1)).   # retain, or release after current service
    N_h = min(C+N_(h-1), A+U+B_h).
    V_h = U+B_h.
    D_h = min(C+N_(h-1), C+m_h+D_(h-1), A+U+B_h, R+U+B_h).

Omit the final term if incremental repair is not admitted. The D terms are,
respectively, abandon/fresh, preserve damaged scaffold while answering fresh,
full rebuild/use, and incremental repair/use. Serving fresh while keeping an
already valid structure is dominated by reuse because U<=C; abandoning before
fresh service is dominated by reusing then releasing. No other actions are
implicitly supplied by the recurrence.

Proof: each first action pays exactly its registered stage cost and enters
its stated next-state distribution. Induction on h makes the recurrence a
lower bound on any history-based policy cost; finite action choices and
minimizing child policies attain it. Randomizing actions cannot improve an expected minimum.
The theorem is standard finite-horizon dynamic programming applied faithfully
to this fully observed register. Computing the policy is charged development
work when the controller is itself implemented, not free measured capability.

For a guaranteed support-worstcase comparison, replace the continuation
expectation by max(V,D) when 0<q<1, by V when q=0, and by D when q=1.
The corresponding adversarial finite-graph induction is separate from the
expected calculation. Zero-probability events do not belong to that support.

## 4. CRI-3 — independent finite revival and counter-controls

The retained witness is H=4,A=2,R=1,C=2,U=1,q=1/2. Compare all legal policies,
not only the fixed repair policy. Exact event execution gives:

| Holding M | One-shot expected gain | Repair expected gain | Optimal expected cost | Best guaranteed cost |
|---|---:|---:|---:|---:|
| 0 | -1/8 | +1/2 | 15/2 | 8 |
| 1/8 | -11/32 | +1/8 | 63/8 | 8 |

Fresh cost is 8. The first row's one-shot policy never recovers its acquisition
cost at any finite horizon: Delta/q=A. Rebuilding everything at R=A=2 has
expected gain -1 on that row. Retaining a sufficient scaffold and using a
certified repair at R=1 is the explicit changed mechanism. This is a conditional
finite mechanism witness; these costs are authored, not measured on a prover.

The fixed repair policy loses 1 on the all-invalidating path of the first row,
which has probability 1/8. Its positive expected gain is not a guarantee.
Abandoning/never acquiring attains the best support-worstcase cost 8.

`grand_gmi_reuse_invalidation_checks_v1.py` independently executes every
nonstationary state/action policy table against every positive-probability
invalidation history. Each four-request witness enumerates 6,633 reachable policy tables
and eight histories. At each prefix it branches only over states reachable on
those histories. Choices in unreachable states cannot alter any path; retaining
every choice in reachable states preserves all distinct policy behaviors. A separate varied census covers H=1..3, five cost tuples
and q in {0,1/2,1}, including expensive repairs, nonzero storage and zero reuse
advantage. Both expected and worstcase optima are compared against Bellman.
An unadmitted zero-price repair must not improve the result. The certificate
control rejects stale candidates and charges the failed attempt before fallback.
A high-holding control starts valid with H=2,C=2,U=1,M=100,A=3: reuse then
release, followed by fresh service, costs 3. Abandoning before fresh service
costs 4. Release after acquisition, repair and rebuilding is also admitted;
forcing unnecessary holding would compare against an artificially weak parent.

## 5. Parent assimilation and remaining boundary

[Aldous, Berkeley STAT 150 Lecture 23, pp. 6–7](https://www.stat.berkeley.edu/~aldous/150/Lectures/lecture_23_post.pdf)
gives the iid cycle reward/cost ratio and replacement-policy application.
Its mapping here is explicit: a repair starts a renewal cycle, each served
request contributes Delta-M, and the next certified repair costs R.
[Shimkin, finite-horizon dynamic programming, Theorem 2, pp. 9–10](https://webee.technion.ac.il/shimkin/LCS11/ch2_DP_finite.pdf)
provides the finite-state/action Bellman parent, including optimal deterministic
Markov policies. We adapt the state graph and charge conventions, not its proof.

No new renewal theorem, optimizer or empirical proof-system advantage is
claimed. Unknown hazards, correlated or partially observed validity, failed
repairs, shared lemma dependencies, contention and forced memory eviction require
richer registered states/transitions and fresh comparisons. The three-state
result does not discharge those obligations or establish universal completion.
