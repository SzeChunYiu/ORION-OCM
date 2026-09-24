# Named results — `gmi-833-aa1-gap-graph-v1` (issue #839, #833 addendum AA/AD)

Claim ceiling: `GMI_833_RECURSIVE_GAP_GOVERNANCE_V1_AT_DECLARED_SCOPE`.

Every result below is an exact statement about explicitly named finite objects:
the 1140 gap records of `GAP_GRAPH_V2.json` and the registers they point into,
all pinned by blob in `FREEZE_V1.md` §3 at
`source_main = cc36a3096031f871c430c79d6fbd64890388c772`; the 9 flagship
results of the AJ0 registry; this package's own loop and result records; and
declared finite fixture spaces. These are computer-assisted exhaustive checks
over declared finite domains. **None is an analytic proof**, none says any GMI
theorem is true, and no real node is awarded a grade above `LOCALLY_CLOSED`.
Each result also has a machine-readable record in `RESULT_RECORDS_V1.json`;
exact numbers are in `RESULT_V1.json`.

---

## AA1G-1 — `GMI_GAP_GRAPH_V3`: a typed gap graph whose descendant edges are derived, not authored

**Scope.** The 1140 corpus gap records, the 6 gaps extracted by this lane's AD
loop, the 113 resolved stated-dependency edges, and the 9 + 8 result records.

**Statement.** `GMI_GAP_GRAPH_V3.json` has 2341 nodes (1146 `GAP`, 1174
`CLAIM`, 17 `RESULT`, 2 `PARENT`, 2 `ASSUMPTION`) and 2757 edges. Its 198
`DESCENDANT` edges come from three declared rules only: R1 id precedence
(46), R2 stated-dependency propagation (16) and R3 repair successor (136).
From corpus records alone (R1, R2) **41 of 1140** records gain a gap
descendant, where the census graph has **0 of 1140**; under any rule 169 do,
and 207 carry a gap or object descendant (the parent register had
gap-to-object descendants on 50). All 1094 gap claim ids have a claim node,
and 1082 of the 1174 claim nodes link to at least one unresolved descendant
gap. Gap ids are shared by 24 records under 10 ids; those records remain 24
nodes, never merged.

**Assumptions.** The 1140 records of `GAP_GRAPH_V2.json` are the gap universe;
stated dependencies reach this package only through `REGISTER_DELTA_V1`
`claim_dependencies`; gap node identity is (gap id, occurrence index in file
order).

**Dependencies.** `gmi-833-census-registration-pass-v1` (`GAP_GRAPH_V2.json`,
`REGISTER_DELTA_V1.json`); `gmi-833-corpus-census-v1` (`CORPUS_INDEX_V1.json`,
the census gap graph); `gmi-833-depgraph-adjudication-v1`
(`DEPENDENCY_GRAPH_V2.json`, the owner of the stated edges).

**Falsifiers.** A `DESCENDANT` edge no rule derives; route B's fixed-point R2
set differing from route A's read of the parent's `descendants` field; a gap
claim id without a claim node; two records merged into one node.

**Strongest parents.** `gmi-833-census-registration-pass-v1` owns the
gap-to-object descendant relation (50/1140) that R2 reads; truth maintenance
with dependency-directed retraction (Doyle, *Artificial Intelligence* 12(3)
1979, doi:10.1016/0004-3702(79)90008-0) owns the idea that a repaired premise
re-opens what depends on it. The residual here is the gap-to-gap relation over
this universe and its three rules. Absence of a stated edge is **not**
independence; that limit is the extracted gap `GAP-AD-AA1-SPARSITY`.

---

## AA1G-2 — every repaired gap records what its repair introduced

**Scope.** The 857 `GAP-DUPID` records and their adjudications.

**Statement.** Exactly 154 records are `LOCALLY_CLOSED`: those whose
adjudication verdict is `DUPLICATE` under rule B1 (108) or B3 (46) — B2 has 0 —
**and** whose rule predicate is re-derived from the `CORPUS_INDEX_V1`
declarations by both routes (154/154 agree with the adjudication). Each carries
a `REPAIR_DELTA` emitted through the gap-object emitter, with a non-empty
`new_assumptions` list (`A-B1` or `A-B3`, each an `ASSUMPTION` node with an
`INTRODUCES` edge) and `new_gaps` equal to its direct `DESCENDANT` successors
(non-empty for 136). The 703 `DISTINCT` verdicts and all 283 `FIN2UNIV`
`PROPER` verdicts stay open: single-lane readings with no independent route.

**Assumptions.** The adjudication file holds the verdicts on record;
re-deriving the rule predicate from the declarations is an independent local
check of the verdict, not of its meaning.

**Dependencies.** `gmi-833-depgraph-adjudication-v1`
(`DUPLICATE_ADJUDICATION_V1.json`, rules B1–B4); `gmi-833-aa-gap-object-v1`
(`emit_repair_delta`, `REPAIR_DELTA` fields); AA1G-1.

**Falsifiers.** A `LOCALLY_CLOSED` gap without a repair record, with an empty
`new_assumptions` list, with `new_gaps` differing from its successors, or with
a re-derived rule differing from the adjudication's.

**Strongest parents.** `gmi-833-aa-gap-object-v1` AAG-5 owns the successor
interrogation and its emitter; it ran the emitter with empty lists as a
totality check. The residual is populating those lists from derived edges for
every real closure. The repairs' own assumptions are themselves gaps: 90 of the
108 B1 closures span two or more packages (`GAP-AD-AA1-B1-CONTEXT`), and the B3
pointer rule is unverified semantically (`GAP-AD-AA1-B3-POINTER`).

---

## AA1G-3 — an unresolved CRITICAL descendant blocks promotion and parent closure

**Scope.** The graph of AA1G-1 with the AAG-3 materiality of every gap.

**Statement.** 290 corpus gaps are unresolved and `CRITICAL`, plus 5 extracted
ones. Of the 154 `LOCALLY_CLOSED` gaps, **136 are held at `LOCALLY_CLOSED`** by
an unresolved `CRITICAL` gap in their descendant closure (6 by corpus-rule
descendants alone; 130 more through the repair-successor gaps their own
repairs raised) and 18 are not blocked by descendants. Local closure itself is
never blocked by descendants. Leaving `OPEN` is refused for parent
`T833-B1-AA` (292 unresolved `CRITICAL` gaps in its cone) and for `T833-AA1`
(5); `--parent-closure-gate` exits 1 for both. Over the exhaustive cubes,
3072 parent cases grant 0 closures over an open `CRITICAL` gap, and 13824 gap
cases agree between routes.

**Assumptions.** Materiality is the AAG-3 function with its declared inputs; a
gap is unresolved iff its closure state is not one of the four grades.

**Dependencies.** AA1G-1, AA1G-2; `gmi-833-aa-gap-object-v1` AAG-3
(`OPEN_GAP_SCHEMA_V1.json` grade bands and threshold).

**Falsifiers.** A node held above `LOCALLY_CLOSED` with an unresolved
`CRITICAL` gap in its closure; a parent granted closure while its cone holds
one; the two routes disagreeing on the blocked set.

**Strongest parents.** `gmi-833-aa-gap-object-v1` AAG-3/AAG-4 own the threshold
and the lattice; assurance-case argument graphs (GSN, Kelly & Weaver 2004) own
the rule that an undeveloped child goal leaves its parent claim unsupported.
Not claimed: that any GitHub issue is prevented from closure — the gate
is not bound to that action (`GAP-AD-AA1-AA40-BINDING`).

---

## AA1G-4 — closure states are five declared values; a bare closure verdict is refused

**Scope.** Every closure state held by a node, and every promotion request.

**Statement.** A closure state is `OPEN` or one of the four gap-object grades.
A bare token (any case of the word alone) is refused as `BARE_CLOSED`, any
other undeclared value as `UNKNOWN_CLOSURE_STATE`, both by the graph validator
and by the promotion evaluator; a grade is held only with the evidence flags
the lattice requires (`LATTICE_EVIDENCE_MISSING` otherwise), and
`REPLICATED_CLOSED` / `REAL_SCALE_CLOSED` are refused on the real graph. On the
real graph 0 nodes hold a grade above `LOCALLY_CLOSED`. The exhaustive cubes —
13824 gap, 1000 flagship and 3072 parent cases, bare and undeclared requests
included — agree exactly between the routes.

**Assumptions.** The gap-object detector defines the bare token; the gap-object
lattice defines what each grade requires.

**Dependencies.** `gmi-833-aa-gap-object-v1` (`bare_closed_hits`,
`closure_grades`); route B re-implements both without importing them.

**Falsifiers.** A bare value accepted as a state; a grade held without its
flags; any route disagreement on a promotion case.

**Strongest parents.** `gmi-833-aa-gap-object-v1` AAG-4 owns the four grades,
the chain property and the detector; this result enforces them at the only
place a grade is recorded in this graph.

---

## AA1G-5 — flagship results need two distinct counterexample methods before `HOSTILE_CLOSED`

**Scope.** Result records; the 9 flagship results of the AJ0 registry.

**Statement.** Every flagship record carries at least two
counterexample-method slots over six declared classes. `HOSTILE_CLOSED` or
higher is refused (`FLAGSHIP_METHODS_MISSING`) unless two filled slots name
distinct classes and no slot records a counterexample. The check refuses on doubt:
a missing or non-boolean flagship flag is read as flagship; a slot field that
is not a list, or a slot that is not an object, is a refusal. Over the
exhaustive 1000-case cube, 0 flagship grants occur without two distinct
methods. On the real records, 0 slots are filled and `HOSTILE_CLOSED` is
refused 9/9.

**Assumptions.** The AJ0 `flagship_results` list is the flagship universe; a
filled slot's evidence pointer is taken as given (its content is not audited).

**Dependencies.** `gmi-833-aj0-foundation-scope-v1`
(`FOUNDATION_LAYER_REGISTRY.json`); AA1G-8.

**Falsifiers.** A flagship record granted `HOSTILE_CLOSED` with fewer than two
distinct filled methods; a malformed slot list accepted.

**Strongest parents.** The #833 method rows AA12–AA15 name the classes
(bounded exhaustive, SAT/SMT/model checking, property-based, proof assistant);
property-based testing is Claessen & Hughes, "QuickCheck", ICFP 2000,
doi:10.1145/351240.351266. The residual is the refuse-on-doubt slot contract and
its measured state (`GAP-AD-AA1-FLAGSHIP-SLOTS`).

---

## AA1G-6 — validation is deterministic and reports cycles instead of collapsing them

**Scope.** The real graph; 39 planted positives and 6 clean cases; all 4608
digraphs on 3 labelled gap nodes with self-loops and on 4 without; 300 seeded
random graphs.

**Statement.** The real graph has 0 findings and 0 cycles or self-loops in the
`DESCENDANT` and `DEPENDS_ON` subgraphs, in both routes. Each of the 21 finding
codes has at least one planted positive; all 39 fire in both routes with
identical finding lists, and all 6 clean cases are silent. A cycle is reported
with every member, never condensed. The cycle report agrees with a brute-force
mutual-reachability oracle on all 4608 small digraphs (3865 with a cycle, 448
with a self-loop). Over 300 random graphs (103 clean, 197 with findings, all 21
codes exercised) the routes never disagree. Two builds are byte-identical, and
the tests pass under `python3 -I -B` and `python3 -I -O -B`.

**Assumptions.** The 21 codes of `GAP_GRAPH_SCHEMA_V1.json` are the validation
contract; subjects are compared as exact strings.

**Dependencies.** AA1G-1; `GAP_GRAPH_SCHEMA_V1.json`.

**Falsifiers.** A planted positive that does not fire; a clean case that
alarms; a cycle merged or unreported; any byte difference between two builds.

**Strongest parents.** Strongly connected components: Tarjan, *SIAM J.
Comput.* 1(2) 1972, doi:10.1137/0201010 (route A) and Kosaraju's two-pass
method (route B); `gmi-833-depgraph-adjudication-v1` `CYCLE_REPORT_V1.json` owns
the cycle report for the stated-dependency union, which collapses ambiguous
ids; here nothing is collapsed and the report is on the gap relation.

---

## AA1G-7 — the AD research loop as a template whose iterations must extract gaps

**Scope.** `AD_LOOP_TEMPLATE_V1.json`, `AD_LOOP_RECORDS_V1.json` and 200
seeded mutations of it.

**Statement.** The template lists the twelve steps of the #833 AD text block
in order (checked against the comment's own block) with a status contract per
step. The validator rejects an iteration whose new-gap extraction step is not
`DONE` or extracts no gap, an extracted gap missing an `OPEN_GAP` field or
materiality inputs, any assumption edit not paired with a gap extracted in the
same iteration, any drift between one iteration's `assumptions_after` and the
next one's `assumptions_before`, and a stop for an undeclared reason. The
worked instance for this lane (2 iterations, 6 extracted gaps, 5 paired
assumption changes, stopped at `DECLARED_EVIDENCE_CEILING_REACHED`) validates
in both routes and its gaps are ingested into the graph. All 200 mutations over
22 classes are rejected, with 0 route disagreements.

**Assumptions.** The twelve steps are those of the AD text block; replication
and real-scale steps may be `NOT_RUN` with a reason when they exceed the claim
ceiling.

**Dependencies.** `AD_LOOP_TEMPLATE_V1.json`; `gmi-833-aa-gap-object-v1`
(`OPEN_GAP` fields, materiality); AA1G-1.

**Falsifiers.** An iteration with no extracted gap accepted; a silent
assumption edit accepted; a stop for an undeclared reason accepted.

**Strongest parents.** Preregistration (Nosek et al., *PNAS* 115(11) 2018,
doi:10.1073/pnas.1708274114) owns the frozen-prediction step; Lakatos's
methodology of research programmes owns the distinction between repair and
degeneration that the paired-change rule operationalises. Not claimed: that
every major claim has run the loop, or that any loop reached a
no-new-material-gap fixpoint.

---

## AA1G-8 — one machine-readable result record

**Scope.** The 9 flagship records and this package's 8 records.

**Statement.** A result record carries result id, statement, scope, flagship
flag, assumptions, dependencies, falsifiers, counterexample-method slots,
strongest parents, prior disclosure (freeze pointer and outcome timing:
pre-outcome, scoping-observed, post-outcome or unverified), evidence and
maturity, forbidden extrapolations, closure state and evidence, and provenance.
A list field is a non-empty list of strings or the sentinel `UNREGISTERED`,
never an empty list. The 9 flagship records are copied from the AJ0 registry
and `REGISTRATIONS_V2.json` by exact package equality with a pointer per field
(0 list fields left `UNREGISTERED`; evidence level `UNREGISTERED` 9/9; a freeze
pointer for 8/9); all 17 records validate in both routes and every planted
invalid record is rejected by both.

**Assumptions.** Exact package equality is the only binding between a flagship
id and a registration; a copied ledger is taken as registered, not verified.

**Dependencies.** `gmi-833-claim-discipline-v1` (`REGISTRATIONS_V2.json`);
`gmi-833-aj0-foundation-scope-v1`; `gmi-833-aa-ledger-gate-v1` (the ledger
predicates this file itself satisfies).

**Falsifiers.** A record missing a field accepted; an empty list accepted in
place of the sentinel; a flagship-scoped record not flagged as flagship.

**Strongest parents.** `gmi-833-aa-ledger-gate-v1` LG-1..LG-4 own the ledger
emission predicates; `gmi-833-claim-discipline-v1` owns the registered ledgers;
model cards (Mitchell et al., FAT* 2019, doi:10.1145/3287560.3287596) own
structured result reporting. The residual is one validated record joining all
of them, with prior disclosure and closure state.
