# Target-total lower-bound transport — LST-4

Status: sufficient numerical transport and constructive finite certification.
The mature mechanism is infimum order plus CLB accounting and MSC coverage;
no scale-independent physical constant or new general optimization is claimed.

## 1. Transport to an explicitly covered target

Let nonempty source S and target T have finite real accounts a_s and a_t.
Supply a finite real certified source bound L_s<=inf_(s in S) a_s(s).
Let epsilon>=0 be finite. Suppose a relation R subseteq S x T is
target-total and every related pair obeys the accounting comparison:

    for every t in T there exists s in S with (s,t) in R;
    (s,t) in R implies a_s(s)<=a_t(t)+epsilon.

Then L_s-epsilon<=inf_(t in T) a_t(t).
Proof: choose a related s for any t. L_s<=a_s(s)<=a_t(t)+epsilon;
the resulting lower bound holds for every t, hence for their infimum.
No cardinality, compactness, enumeration or measurable selector is needed
for this pointwise existential proof. Constructing a relation may need them.

For every admitted target machine M additionally require an actual q_M in T
and a_t(q_M)<=c_target(M). This is CLB's membership/accounting premise.
Consequently

    L_s-epsilon <= inf_T a_t <= a_t(q_M) <= c_target(M).

A set named allocations, a Boolean membership flag or a witnessed source
machine does not certify target-total coverage. The target includes ALL
allocations/machines in the claimed scope; unexplored additions need coverage.
A relaxed allocation need not be a feasible machine, so its attained minimum
alone is not a feasible upper witness or a selected architecture.

## 2. The original failure and a quantitative revival

S has account set {2}; expand it to T={1,2}. Keep q_M=2 and c(M)=2.
Both old CLB premises still hold, but the infimum changes from 2 to 1.
Admitting a second machine with q=1,c=1 defeats the old universal bound 2.
The original helper actually recomputes 1; its cited large-set test only
added values above an existing minimum. The proof FORM is independent of
cardinality, but the numerical infimum depends on the entire accounted set.

For epsilon=0, no source allocation covers target value 1, so the new
certificate rejects. For epsilon=1, source 2 covers both targets and yields
the sound bound 1. This repairs transport by explicit error/coverage rather
than claiming that allocation expansion preserves the old value.

The relation is sufficient, not necessary for equal infima. S={1/n:n>=1}
and T={0} have equal infimum 0, but no source value is <= target 0.
The comparison is a useful certificate, not an equivalent characterization.

## 3. Equality, attainment and ordering are separate

If target-total comparisons exist in both directions with errors epsilon
and delta, both infima are finite and

    inf_S a_s-epsilon <= inf_T a_t <= inf_S a_s+delta.

Proof: apply the preceding argument in each direction with the respective
infimum as the source bound. At zero error, values agree. Exact attainment
does not follow: the identity relation on {1/n:n>=1} is two-way and exact,
yet no minimum exists. A finite nonempty source of actual feasible machines
with cost-preserving coverage is the stronger MSC-2 construction.

A sound shared lower bound alone does not order two candidates above it.
Actual target costs, feasible upper witnesses or a domination-preserving
mapping can establish order; EFI-4 supplies a precise sufficient transport
of complete Pareto patterns. This correction does not forbid such proofs.
Equal infima do not imply simultaneous attained optima or identical profiles.

## 4. Effective finite certificate and cost boundary

For explicitly enumerated nonempty rational source/target maps, the helper
checks the source lower bound, every supplied relation pair and full target
coverage. It also checks actual target candidate allocation membership and
sound account<=protected-cost direction. Missing coverage, an unknown pair,
overaccounting and malformed values reject; an empty candidate register is
unresolved as a constructive machine claim, even if allocation algebra holds.

Enumerating every pair satisfying a_s<=a_t+epsilon constructs a relation in
|S||T| exact comparisons. Checking it is finite. This does not decide coverage
of infinite or implicit physical sets; those need an actual analytic proof.
The receipt reports pair comparisons and candidate checks. Charge acquisition,
set enumeration, arithmetic bit lengths, verification, construction and
retention separately under the declared lifetime ledger. No native measurement
or free scalable algorithm is supplied by these rational controls.
