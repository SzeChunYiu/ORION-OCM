# Resource distinction V10: preregistered scope
Status: frozen before outcome-bearing implementation. Control #1068.
Parent V8 continuation semantics and V9 governance survive unchanged.
The model-level predictions below are derived candidates, not new empirical laws.
No literature priority or full-family theory claim is preregistered.

## Model
Finite nonempty states S, finite actions A, state observation o(s).
Partial deterministic edges (visible event, natural cost, successor).
All current/intermediate observations and successful edge events are retained.
Absent and unaffordable edges both emit ILLEGAL and stop.
The input action is known. Remaining resource itself is not observed.
Baseline events include exact cost; an extension permits per-action event maps.
All finite words are tested. Empty words reveal the current observation.
Natural-number resource starts equal in compared runs and decreases on success.
No silent steps, nondeterminism, probability, negative costs or divergence.
An empty action set is allowed and handled separately by the implementation.

## Frozen mathematical targets
T1: With exact visible costs, response equivalence at initial B holds iff
B<D(s,t), where D is the least resource needed for a distinguishing word,
or infinity if no word distinguishes at any finite resource.
T2: D equals reverse shortest-path distance on unordered distinct state pairs.
Different current observations cost zero to a mismatch sink.
Exactly one admitted edge contributes its cost to the sink.
Distinct visible events/costs contribute min(costs) to the sink.
Identical event and cost contribute that cost to the successor pair.
Diagonal pairs never distinguish. Include zero-cost cycles.
T3: Universal nesting over unrestricted finite machines with action-indexed
available edge payloads holds iff equal events on the SAME action imply equal
costs. Necessity permits equal state observations and a shared terminal state.
The condition need not be necessary within a restricted application class.
T4: D(s,u)>=min(D(s,t),D(t,u)). With infinity mapped to zero,
2^(-D) is a pseudoultrametric, metric after full-behavior quotient.
T5: Finite D<= (n-k)*Cmax, where k counts initial observation classes.
Proof uses existence of an unbudgeted distinguishing word of length<=n-k.
It does not bound the length of every cost-minimal witness by n-k.
A simple product witness has at most n*(n-1)/2 pair vertices.
T6: Each positive threshold strictly refines the resource-indexed partition.
There are at most n-k(0) positive thresholds. At known fixed B, k(B) codes,
ceil(log2(k(B))) bits are necessary/sufficient for response representation.
This is not a total online-memory minimum; updates change residual B.

## Implementation and independent checks
Root implements reverse Dijkstra, initializing infinity and local mismatches.
Witnesses follow already-settled successors; strict improvements prevent
zero-cycle reconstruction loops. A separately implemented oracle builds
all residual-resource states and repeatedly refines complete response signatures.
It uses no root shortest-path implementation or root pair-graph construction.
Both algorithms validate their declared input domain.

Exhaustive primary corpus: all 2-state, 2-action machines with two state
observations, two output values, costs {0,1,2}, two successor states or absence.
Count: 2^2 * (1+2*3*2)^4 = 114244 machines.
Compare every original-state pair at every integer B from 0 through the
proved finite bound; a pair not distinguished there must have D=infinity.
Execute finite witnesses at D and at D-1 when D>0, using independent response
execution. Check all larger budgets through the same bound as applicable.
Record concrete counts from actual execution, never expected counters alone.
Add deterministic seeded larger machines, zero/positive cycles, identical
states, edge absence, unequal observations/events/costs, ties, action/state
relabeling, triangle inequality, nesting and bound-attaining unary chains.
Seed and case construction are declared in test source, no outcome tuning.

Controls: hidden-cost same-event costs1/2 split at B1 and merge at B2;
same-budget successor equivalence need not be a congruence after spending;
zero self-loop with no mismatch must stay infinity, with mismatch5 must give5;
Bellman numeric fixed-point equality alone admits invalid finite answers;
same event but different costs across different actions need not break nesting.
Corrupt finite/infinite distances, invalid witnesses, costs and model inputs
must be rejected. A checker failure is diagnosed and repaired in a successor
implementation without changing the frozen scientific targets.

## Proof, custody, scope
General Lean targets: actual budgeted response contraction/nesting; threshold
relation consequences where applicable. Paper proves the graph characterization,
sharp finite bound, observation iff and storage boundary; list precisely which
claims are kernel checked. No stub, sorry or finite fixtures as general proof.
Sources: Bisping2023 energy-game spectroscopy, Rutten continuation semantics,
weighted-transition observation equivalences, classical shortest paths.
Parent ownership is explicit; closest known results are assimilated.
Normal and python -O receipts must agree, kernel and exact-head CI must pass.
Preserve frozen V1-V9 bytes and all original222 IDs. Only new local evidence
is added; R0 stays governance-earned, all other214 obligations remain unchanged.
Overall theory closure remains OPEN. No empirical novelty, general cognition,
all-family derivation, probability-free superiority or assumption-free claim.
The independently audited #1103 historical lane gaps are queued concretely
in this successor's assimilation backlog without modifying that lane.
