# V24 — complete AF profiles, selected records and erasure

## X1.3 — formal AF profile semantics

AF FORMALIZATION_V1 section2 fixes S,M0,Delta,Pi,R,H,Q,V and defines reachable
profiles g=(c,r,pi,m,h), retaining capability, raw resources, consumed provenance,
terminal machine and finite development history. Its exact process/admission and
verification contracts remain supplied data. Let P admit precisely those histories,
E specify defined profile evaluation, and W retain ALL five coordinates. The
context image is exactly this Gamma by witness membership in each direction.
Projections/slices require their declared coordinate maps and restrictions.
Current capability is the capability projection of the development_steps=0 slice;
it is not generally enough to recover the developmental envelope.
Generic pi can represent a declared set or multiset; the concrete helper below
chooses a set. No new information, verifier or resource semantics is manufactured.

## X1.4 — actual finite helper and profile fields

The immutable af_core_v1.reachable starts with start:() and traverses ordered
outgoing edges breadth-first, recording one first-arriving action-word per terminal.
Its H_BFS is exactly the returned (terminal,action-word) records.
gamma_profiles calls that helper and returns records sorted by terminal machine.
Each profile contains its terminal machine, capability task key and exact score
string, development_steps=word length, action history, and sorted provenance set.
The set always contains INITIAL_OR_INHERITED_ORGANIZATION, unioned with the tags
of every action. external_observations/oracle_queries are Boolean tag-presence
indicators, not event counts. Repeating a tag is idempotent, not additive.
The fixed policies are C0,C1,ID,NOT and accuracy compares their two outputs to the
chosen target policy. This is a supplied finite task, not universal intelligence.

The faithful adapter calls actual reachable and gamma_profiles; its code Context
and explicit profile decoder retain these full dictionaries. A source-level equality
is between decoded image and old records, including all fields and their ordering
where the API returns an ordered list. A mere capability-set match is weaker.
No independent horizon/resource/verifier argument exists in the old helper.
Malformed unused graph/provenance input can be rejected by a stricter new boundary;
that is parser hardening, separated from faithful valid-input behavior.

## X1.5 — richer histories and an explicitly noninjective erasure

For the full finite-horizon extension, an edge is identified by its source and
stable outgoing slot. Valid histories follow actual destinations from start and
retain their edge sequence and terminal. Absent slots are skipped, not renumbered.
Map each edge to its action label; erase a full history to (terminal,action-word).
Define its old-projected profile using exactly the old constructor on that record.
Thus the old-projected profile factors through erasure by construction. Composing
this with X1.1 gives exact direct-image transport, without assuming erasure injective.

Labels may repeat, including on parallel edges. The old provenance mapping is keyed
by action string, so shared labels share tags. Distinct edge-specific provenance
under one string would be a different API. Two histories can have identical terminal
and action-word but different edge sequences, hence identical old-projected profiles.
No old-record decoder can then recover their unique edge identity. The richer
extension retains it separately; it does not silently ascribe it to legacy output.
A rich value pairs its raw history identity with this erased old profile. Projection
to the second coordinate gives the old-profile context and maps VALUE observations
while preserving illegal/undefined tags. This direct-image/observation equality
needs no order reflection: a rich equality order can distinguish paths whose
projected values agree. Any claimed comparison transport needs its own premises.

## X1.6 — BFS lifts, coverage and finite-horizon correspondence

Every record saved by reachable has some actual path lift. Initially the empty path
reaches start. When scanning an edge from an already lifted terminal cur, append
that actual edge to its path; if nxt is new, this realizes the stored word for nxt.
Induction over queue insertions proves the invariant, without unique action labels.

BFS processes depths in increasing order. Within a depth it processes retained
path slot sequences in lexicographic order, since parents are processed in that
order and each parent's outgoing slots are ordered. Dropping a later path to an
already seen terminal cannot improve a descendant's least(length,lexicographic)
path: replacing its prefix by the retained earlier/shorter path keeps its suffix
valid in this fixed graph and makes the concatenated path no later in that order.
Consequently the first saved record per terminal equals the action erasure of its
least(length,slot-sequence) path. Independent finite enumeration uses this criterion
instead of copying queue traversal. Ties in action words do not change edge ordering.

For any finite walk, delete the segment between two repeated occurrences of a
vertex. Endpoint reachability is preserved and length decreases. Repetition gives
a simple path with at most N-1 edges for N vertices. Thus every reachable terminal
is covered by horizon>=N-1. The old BFS selected paths satisfy the same bound.
The frozen horizons3 for two vertices and4 for four vertices are sufficient for
terminal coverage; smaller horizons are tested separately. Cyclic full histories
may remain arbitrarily long, so terminal coverage is not full-profile coverage.
Capability depending only on terminal therefore agrees between these covering
selected/full images, by X1.2. History/provenance/length projections need not agree.

These queue/path/horizon proofs are paper mathematics with independent finite
calibration, not a claim that the Python BFS algorithm is Lean-mechanized.
The kernel image/erasure theorems retain their exact signatures. Full-horizon
enumeration is not all-walk enumeration or a new efficient graph algorithm.
