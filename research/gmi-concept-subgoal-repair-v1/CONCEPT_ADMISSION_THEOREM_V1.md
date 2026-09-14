# Adequate representations before retention

## CSG-4: the boundary is relative to the full query contract

Let nonempty finite E be the supplied experiences/configurations and finite Q
the supplied query set. Require the exact output f(e,q), and suppose all
information about e available at service is the retained encoder state z(e).
Then equal z values require equal response rows f(e,·). Conversely retaining
a response-row index and a fixed complete decoder table implements the quotient.
Thus the minimum state alphabet is the number of distinct rows. This is the
existing CSR/DQ exact-interface argument; it does not price the decoder table,
its acquisition, the routing information, or the encoder's construction.

For dynamic experiences, present-output equality is insufficient. The intended
future-event relation must also respect legal actions, successors and protected
cost/output traces. Two states can emit0 now while one update takes only the
first state to an emit1 state; update then query separates them. Exact finite
Mealy minimization uses the full future interface. The source script instead
groups supplied response functions on16 fixed inputs: that finite table is
valid at its static query scope, not a certificate for arbitrary future events.

Even abstract task equivalence need not permit raw artifact substitution.
A reuse decoder/transport must be correct for every promised target query,
as already required by PVR-2. Acquiring a response table is an explicit oracle
or enumeration contract, not free learning from a few observed examples.

## CSG-5: the complete single-class condition

For r>=1 known occurrences, nonnegative finite fully charged independent costs
C (fresh derivation), S (one-time installation/indexing), U (valid subsequent
lookup/transport/check), stable validity and no eviction/invalidation:

    F=rC, R=C+S+(r-1)U,
    R<F iff (r-1)(C-U)>S.

If C<=U, strict gain is impossible. Only when C>U may one divide to obtain
r>1+S/(C-U). At equality both policies tie. For C=1,S=1,U=2,r=2 the unguarded
divided condition says2>0, but retention4 loses to fresh2.
This is PVR-3 verbatim in mathematical content, not a new formation law.

For several independent classes with supplied counts and unlimited capacity,
select every strictly positive gain (ties optional). The sum identity proves
optimality over these static retain-after-first versus always-rederive policies.
With retained sizes and a hard capacity, use PVR-4's full feasible-subset problem;
individual positive gain no longer implies simultaneous admission. Shared
compilation/recognition costs require a coupled model, not independent thresholds.
The exact finite schedule emits equal response traces in all admitted policies.
It can attain the source's48/75/57 reconstruction ledger before common costs.

## CSG-6: prospective decisions charge only future savings

At a checkpoint, if a valid artifact currently exists in charged temporary
storage, installation costs S and k further occurrences are supplied, retaining
it is strictly preferable to discarding and rederiving iff k(C-U)>S.
Any extra release/holding difference is included in these complete action costs;
discard has no additional unmatched charge in this register. Past derivations are sunk costs. Without a model for future demand, observed
past recurrence cannot imply this future inequality.

Example: after two derivations with C5,S3,U1, one continuation stops and another
has two more occurrences. The shared past is identical. Immediate retention
loses3 in the first continuation and saves5 in the second. A policy using only
the shared past cannot identify which continuation will happen.
Under a supplied finite conditional workload distribution and the same
independence assumptions, linearity gives E[k](C-U)>S for the two fixed actions.
This is an expected comparison, not a per-run guarantee; adaptive subsequent
admission is a larger policy class with its own state/DP, already covered by
CRI/SMR where their premises apply. There is no new online guarantee here.

The cost trigger decides among already adequate executable choices. It does
not construct concepts, meanings, labels, validity certificates or new skills.
