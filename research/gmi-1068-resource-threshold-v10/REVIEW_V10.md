# Independent V10 implementation and theorem review

Verdict: no actionable defect found in the reviewed threshold solver,
certificate verifier or T1-T6 statements under their declared scope.
This is an independent bounded review, not a universal implementation proof.
The exhaustive primary corpus is separate; it was not repeated here.

## Reviewed source bindings

- threshold_v10.py SHA256:
  `bd94e82da766f693e22f0c2490d21c9cc39a348bc5851001b190701668f30041b`
- certificate_v10.py SHA256:
  `2902233dc743b9711c14f622fc8f34d2b62cb5f01a181031f873954f30bce791`

Executable review: test_independent_review_v10.py. Its COVERAGE dictionary is
populated from executed loops, rather than printing anticipated counts.
The laptop Python3.12 standalone suite passed all four tests both normally
and under optimization, with identical counters. Assertions use unittest
methods and remain active under -O.

## Third comparison route and actual coverage

The review's equivalent() explores paired residual-resource configurations.
It compares current observations, computes each concrete edge's affordability,
compares actual emitted output/cost pairs and follows the residual successors.
It neither constructs threshold sink edges nor calls the root solver to decide
equivalence. Exhausting the finite reachable pair relation proves equality of
all finite response words for that particular resource. This is a different
route from both root Dijkstra and the primary oracle's partition refinement.

The fixed seed106810 constructs200 machines with1-5 states,0-3 actions,
binary observations/outputs, costs0-3, absent edges, list-valued edges and
mixed list/tuple row containers. For every distinct original-state pair,
comparison runs through (n-k)*Cmax+2, including resources beyond the finite
threshold bound. Executed results:

| Check | Actual count |
|---|---:|
| Generated machines and valid certificates | 200 |
| Independent pair/resource comparisons | 6109 |
| Rejected distance/type corruptions | 6601 |
| Rejected coherent finite-to-infinity corruptions | 705 |
| Rejected malformed models | 8 |
| Rejected malformed certificate structures | 8 |
| Rejected mandatory-coverage counter/module mutations | 100 |
| Zero-cycle controls | 2 |
| Valid delayed but nonminimal witness rejected | 1 |

The coherent infinity mutants erase both symmetric distance entries AND both
witness entries. Their rejection therefore exercises reachability constraints,
not merely the requirement that infinity carry no witness.

Zero self-loops with no mismatch retain infinity. Zero self-loops with a
mismatch available at resource5 produce5 and a valid terminating witness.
The delayed-witness hostile pays1 on a common self-loop then distinguishes
with another cost1 action: it distinguishes at2 and not1, yet another word
already distinguishes at1. The local sink inequality rejects its claimed2.
Thus checking only the submitted witness's own first resource would be
insufficient; the implemented optimality conditions close that gap.

## Certificate soundness argument

Let d be an accepted claimed table. Each local sink gives d(p)≤sink_cost;
each edge to a finite successor gives d(p)≤edge_cost+d(q). Induction backwards
along any finite sink path forces all its predecessor entries finite and
bounds d(p) by that path's total. Hence d(p)≤true_D(p), and a claimed infinity
cannot reach a sink. Each finite accepted entry also has an actually executed
distinguishing witness at d(p), proving true_D(p)≤d(p). Equality follows.
A false finite value on an unreachable zero cycle cannot have a distinguishing
witness. Arbitrary Bellman fixed points therefore do not pass this certificate.

Matrix dimensions, required field set, natural-number types, symmetry,
infinity/no-witness consistency, diagonal behavior and action ranges are
checked. Bool is excluded from integer costs/states/actions. Mixed list/tuple
model edges are compared through their scalar output/cost fields, avoiding
container-identity differences. Implementation labels are natural integers;
finite abstract observations can be encoded injectively into that domain.
The classes() helper consumes a solved/verified result; it is not itself a
replacement for certificate verification on untrusted matrices.

## Solver and mathematical scope

Reverse settlement records a witness successor only after settling it.
Strict improvements and frozen settled vertices make settlement rank decrease
along reconstructed links, even when weights are zero. Extra outgoing edges
at a pair whose observations already differ do not alter its distance0.

T1's first-mismatch proof covers the only subtle case: an old success versus
unaffordability can become two successes at larger resource, but their
unequal observed costs preserve distinction. T3 replaces explicit costs with
recoverability from the same input action and emitted event. Its converse
requires the unrestricted machine class permitting equal observations and a
shared terminal state, as stated.

T5 includes observations in P0 and presence/absence in every next signature.
Stabilization therefore gives actual unbudgeted response equivalence.
The n-k word bound guarantees existence of SOME short distinction, whose
resource is at most(n-k)*Cmax; it does not limit the length of every cheapest
resource witness. Empty alphabets, zero costs and diagonal pairs are handled.
T6 concerns codes for snapshots with known resource; online transitions change
that resource. No empirical or all-family conclusion follows from this review.

Integration review identified an ambiguous T3 transition from full-cost events
to mapped events. The theorem now explicitly replaces the successful token
by EDGE(e_a(payload)); cost remains internal to admission/subtraction and is
not separately emitted. Retaining EDGE(output,cost) would invalidate the
necessity counterexample, so this is an essential semantic clarification.

Integration review also found dynamic test discovery required only one passing
test, permitting a regenerated receipt after omission of the primary corpus.
The driver now loads three explicit mandatory modules and validates their
actual coverage counters. The review guard test rejects every missing module,
every missing/changed/Boolean/None mandatory counter and zero/None/Boolean
positive-witness counts:100 executed rejections. Its constructed valid mapping
is only a positive schema control, not reported as primary execution evidence.
Production counts come from the actual three suites; checks include repeated
ordered pairs and diagonals only where their counter names explicitly say so.
The200 review cases are seeded generated cases, not a claim of200 unique
canonical machines. No inflation of unique-model or independent-team claims
is licensed by the receipt.
