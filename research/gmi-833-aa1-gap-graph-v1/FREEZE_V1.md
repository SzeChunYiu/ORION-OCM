# FREEZE — `gmi-833-aa1-gap-graph-v1` (issue #839, child of #833 addendum AA/AD)

Status: **PRE-IMPLEMENTATION FREEZE**. This file is committed alone, before any
builder, validator, oracle, test, schema, template, receipt, theorem note,
ledger or workflow file of this package exists. `git log --reverse --
research/gmi-833-aa1-gap-graph-v1/` must show this file, alone, first. If the
package is later published by a squash merge, the publishing commit must still
contain this file byte-identical.

## 1. Source pin

- `source_main` = `cc36a3096031f871c430c79d6fbd64890388c772`.
- Issue #839 ("T833-AA1: recursive gap graph, theorem/experiment ledgers, and
  scientific closure validator"), read-only, 10 acceptance items.
- Issue #833 comment `5684607872` (live `updated_at` 2026-09-18T17:31:30Z at
  freeze). Rows AA08, AA10, AA11, AA38, AA40, AA41 and AD01–AD08 are unchecked
  at freeze; the mirror `research/gmi-833-checklist-mirror-v1/comments/comment_5684607872.md`
  carries those row lines byte-identical to the live comment.

## 2. Claim ceiling and forbidden promotions

Claim ceiling: `GMI_833_RECURSIVE_GAP_GOVERNANCE_V1_AT_DECLARED_SCOPE`.

This package builds a governance instrument (a typed gap graph with derived
descendant edges, a closure-state validator, a promotion evaluator, a
parent-closure predicate, result records with counterexample-method slots, and
an AD research-loop template with its validator) and applies it to one declared
finite universe. It establishes nothing about the truth of any GMI theorem.
Every check is an exhaustive computation over a declared finite object, never an
analytic proof of an unbounded statement.

Forbidden from this package: `ALL_GAPS_EXHAUSTED`,
`INDEPENDENT_HOSTILE_REVIEW_COMPLETE`, `CORPUS_AUDIT_COMPLETE`,
`REPLICATED_CLOSED`, `REAL_SCALE_CLOSED`, `COMPLETE_GMI`; additionally
`GMI_GAP_GRAPH_COMPLETE`, `RECURSION_EXHAUSTED`, `NO_MATERIAL_GAP_REMAINS`,
`ISOLATED_GAP_IS_LEAF`, `ANALYTIC_PROOF`. No real node of the graph is awarded
`HOSTILE_CLOSED`, `REPLICATED_CLOSED` or `REAL_SCALE_CLOSED` by this package;
the only grade awarded to real records is `LOCALLY_CLOSED`, under rule 4.3.

## 3. Registered scope and pinned inputs (read-only; none is edited)

| input | blob | role |
|---|---|---|
| `research/gmi-833-census-registration-pass-v1/GAP_GRAPH_V2.json` | `20cd106f10f65e25a527a1695f1113c96cf8ac41` | the 1140 gap records, their `materiality`/`materiality_index`/`materiality_inputs`, and gap→object `descendants` (supersedes V1 by reference) |
| `research/gmi-833-census-registration-pass-v1/REGISTER_DELTA_V1.json` | `be84eb34ff9fa03dbeb21f33a4df4e41c2d44f70` | resolved `claim_dependencies` (object → parent id) |
| `research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json` | `709159c53c6284366aaf1f05380f5fada8d81a98` | register key → `object_id`; declaration statements and paths |
| `research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json` | `61006b756721c748f8dcc797c755abd25cc42956` | the census gap graph (0/1140 non-empty `descendants`); baseline only |
| `research/gmi-833-depgraph-adjudication-v1/DUPLICATE_ADJUDICATION_V1.json` | `ac6b41b4cce62f71081ede53c9c5d2ca399d5687` | per-`GAP-DUPID` verdict and reason (B1/B2/B3/B4) |
| `research/gmi-833-depgraph-adjudication-v1/OVERSTRONG_ADJUDICATION_V1.json` | `f56e1245d216c6ad93090ea2f73156c9ec0623b4` | per-`GAP-FIN2UNIV` verdict, reason, basis (annotation only) |
| `research/gmi-833-depgraph-adjudication-v1/DEPENDENCY_GRAPH_V2.json` | `41174e0557ac4fa721412e1afc06c72163c34f94` | owner of the stated-dependency edges (reached through REGISTER_DELTA) |
| `research/gmi-833-aa-gap-object-v1/OPEN_GAP_SCHEMA_V1.json` | `9050c2e01e44347aa2b19710286890be1a5eb21d` | OPEN_GAP fields, materiality threshold, closure grades, REPAIR_DELTA fields |
| `research/gmi-833-aa-gap-object-v1/gap_object_v1.py` | `4d39fbacd2acb79d8f170d844abcb8103b4bd195` | reused by route A: materiality, grades, bare-`closed` detector, REPAIR_DELTA emitter |
| `research/gmi-833-aj0-foundation-scope-v1/FOUNDATION_LAYER_REGISTRY.json` | `5caefcd3a0b812a1f2557dcc228f88de04db5cee` | the frozen list of 9 flagship results |
| `research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json` | `66c3b7e4ef91e096f0ece2720af4645bebe75238` | registered ledgers copied into the flagship result records |

The gap universe is the 1140 records of `GAP_GRAPH_V2.json` in file order. The
flagship universe is the 9 `flagship_results` of the AJ0 registry.

## 4. Rules (declared before any of them is run)

### 4.1 Node identity and kinds

Node kinds: `PARENT` (a parent result or lane id named by a gap), `RESULT` (a
named result carrying a result record), `CLAIM` (a census object id), `GAP` (an
`OPEN_GAP` record), `ASSUMPTION` (an assumption newly introduced by a repair).
Node ids are `KIND:<key>`. A `GAP` node id is `GAP:<gap id>#<k>` where `k` is
the 1-based occurrence index of that gap id among the 1140 records in file
order. Gap ids are **not** unique in the universe; two records are never merged
into one node, and the number of records sharing an id is reported. A `CLAIM`
node is keyed by object id; several declarations of one id share one claim
node — that is the census semantics, and the `GAP-DUPID` gap on the id is where
the ambiguity is recorded.

Edge kinds (source → target): `PARENT_OF` (PARENT → GAP), `GAP_ON` (GAP →
CLAIM), `DEPENDS_ON` (CLAIM child → CLAIM parent, from `REGISTER_DELTA_V1`
`claim_dependencies`), `DESCENDANT` (GAP → GAP), `INTRODUCES` (GAP →
ASSUMPTION). Any other kind, or a kind whose endpoints have the wrong node
kinds, is a finding.

### 4.2 Descendant edges — derived, never authored

A `DESCENDANT` edge `g → h` means: resolving `g` can change whether `h` holds,
so `h` must be re-examined after `g` is repaired. Three rules, each mechanical:

- **R1 `ID_PRECEDENCE`** — `g` is a `GAP-DUPID` record and `h` a `GAP-FIN2UNIV`
  record with the same `claim_id`. Which declaration the universal flag is about
  is undetermined until the id collision is resolved.
- **R2 `DEPENDENCY_PROPAGATION`** — `h.claim_id` is the object id of a register
  key in `g`'s `descendants` in `GAP_GRAPH_V2.json` (the strict transitive
  dependents of `g.claim_id` under the stated-dependency relation), `h ≠ g`.
  Route B recomputes the same set from `REGISTER_DELTA_V1` by fixed-point
  iteration without reading the `descendants` field.
- **R3 `REPAIR_SUCCESSOR`** — `h` is a gap extracted by an AD loop iteration
  (4.9) whose declared `source_rule` selects `g` by one of these predicates:
  `B1_CROSS_PACKAGE` (g was closed under rule B1 and its declarations lie in two
  or more distinct `research/<package>/` directories); `B3_ALL` (g was closed
  under rule B3); `NONE`.

No descendant edge is typed by hand. The absence of an edge is not evidence of
independence (the stated-dependency relation is sparse by the parent's own
semantics), and that limit is itself an extracted gap.

### 4.3 Closure states assigned to real records

A `GAP-DUPID` record whose adjudication verdict is `DUPLICATE` with reason
`B1_VERBATIM_REDECLARATION`, `B2_CANONICAL_REDECLARATION` or
`B3_POINTER_TO_SAME_CONTENT` is `LOCALLY_CLOSED` **iff** this package re-derives
the reason's predicate from the declarations in `CORPUS_INDEX_V1.json` (B1: two
or more declarations, all statements byte-identical; B2: not B1, equal after
whitespace collapse and lower-casing; B3: neither, and some declaration's
statement contains another declaration's file basename), by both routes. Its
closure evidence is `local_checks_pass` and `independent_route`. Every other
record is `OPEN`; the `FIN2UNIV` `PROPER` verdicts and the `DUPID` `DISTINCT`
verdicts are attached as annotations and do not close anything (single-lane
reading; no independent route).

### 4.4 Repair records of closed gaps

Every `LOCALLY_CLOSED` gap carries a `REPAIR_DELTA` (fields of
`OPEN_GAP_SCHEMA_V1.json`, emitted through the gap-object emitter) whose
`new_assumptions` is non-empty and whose `new_gaps` equals the sorted set of its
direct `DESCENDANT` successors. The assumption each rule introduces is fixed now:

- `A-B1`: "byte-identical statement text at distinct declaration sites denotes one semantic object".
- `A-B2`: "statements equal after whitespace collapse and lower-casing denote one semantic object".
- `A-B3`: "a declaration whose statement names another declaration's file basename points to that declaration's content".

Each is an `ASSUMPTION` node with an `INTRODUCES` edge from every gap closed
under its rule.

### 4.5 Materiality enforcement and parent closure

Materiality is the `gmi-833-aa-gap-object-v1` AAG-3 function, inputs unchanged
(corpus gaps take `materiality_inputs` from `GAP_GRAPH_V2.json`). A gap is
**unresolved** iff its closure state is `OPEN`. A node may hold, or be promoted
to, any grade above `LOCALLY_CLOSED` only if no `CRITICAL` gap in its transitive
`DESCENDANT` closure is unresolved. A `PARENT` node may leave `OPEN` only if no
`CRITICAL` gap in its cone (`PARENT_OF` then `DESCENDANT`*) is unresolved; the
predicate is exposed as a command that exits non-zero on refusal.

### 4.6 Closure states and bare `closed`

A closure state is one of `OPEN`, `LOCALLY_CLOSED`, `HOSTILE_CLOSED`,
`REPLICATED_CLOSED`, `REAL_SCALE_CLOSED`. A value the gap-object bare-`closed`
detector flags (e.g. `closed`, `Closed`) is refused as `BARE_CLOSED`; any other
unknown value is refused as `UNKNOWN_CLOSURE_STATE`. A grade is held only with
the evidence flags the gap-object lattice requires for it.

### 4.7 Counterexample-method slots

Declared method classes: `BOUNDED_EXHAUSTIVE_ENUMERATION`,
`SAT_SMT_MODEL_CHECKING`, `PROPERTY_BASED_RANDOMIZED`, `PROOF_ASSISTANT`,
`HAND_CONSTRUCTED_ADVERSARIAL`, `INDEPENDENT_IMPLEMENTATION_DIFFERENTIAL`. A
result record carries a list of slots; a flagship record carries at least two.
A slot is filled when it names a declared class, a non-empty evidence pointer, a
non-empty search scope and an outcome in `NO_COUNTEREXAMPLE_FOUND` /
`COUNTEREXAMPLE_FOUND`. `HOSTILE_CLOSED` or higher for a flagship result is
refused unless two filled slots name distinct classes and no slot records a
counterexample. Fail-closed: a missing or non-boolean flagship flag is read as
flagship; a slot list that is not a list, or a slot that is not an object, is a
refusal, never a pass.

### 4.8 Deterministic validation

The validator returns a sorted list of `(code, subject)` findings. Codes:
`DUPLICATE_NODE_ID`, `UNKNOWN_KIND`, `EDGE_ENDPOINT_KIND`, `MISSING_PARENT`
(any reference to an absent node), `ORPHAN_GAP` (no `PARENT_OF`),
`ORPHAN_ASSUMPTION` (no `INTRODUCES`), `ORPHAN_CLAIM` (no incident edge),
`CYCLE` (a strongly connected component of size ≥ 2 in the `DESCENDANT` or the
`DEPENDS_ON` subgraph, reported with all its members, never condensed),
`SELF_LOOP`, `BARE_CLOSED`, `UNKNOWN_CLOSURE_STATE`,
`CLOSED_WITHOUT_REPAIR_DELTA`, `CLOSED_WITHOUT_NEW_ASSUMPTIONS`,
`DESCENDANT_RECORD_MISMATCH`, `LATTICE_EVIDENCE_MISSING`,
`CRITICAL_DESCENDANT_BLOCKS_PROMOTION`, `FLAGSHIP_METHODS_MISSING`,
`FORBIDDEN_GRADE_AWARDED`, `PARENT_CLOSED_WITH_CRITICAL_DESCENDANT`,
`MATERIALITY_MISMATCH`, `RESULT_RECORD_INVALID`. Each code has a planted
positive that must fire and a clean case that must stay silent, under
`python3 -I -B` and `python3 -I -O -B`. The built graph is written in a fixed
byte order; two builds must be byte-identical.

### 4.9 The AD research-loop template

The twelve steps are those of the #833 AD text block, in order:
claim, formalize, parent search, derive, counterexample search,
repair/downgrade, architecture-prior audit, independent implementation, frozen
prediction, replication, real-scale test, new-gap extraction; then repeat or
stop. An iteration record lists all twelve with status `DONE` (evidence
pointer), `NOT_RUN` or `NOT_APPLICABLE` (reason). The validator rejects: a
missing or out-of-order step; a `DONE` step without evidence or a skipped step
without reason; **an iteration whose new-gap extraction is not `DONE` or
extracts no gap**; an extracted gap missing an `OPEN_GAP` field or materiality
inputs; an assumption edit between `assumptions_before` and `assumptions_after`
not covered by a declared change paired with a gap extracted in that iteration
(a silent edit); an iteration whose `assumptions_before` differs from the
previous iteration's `assumptions_after`; a stop whose reason is not
`DECLARED_EVIDENCE_CEILING_REACHED` or `NO_MATERIAL_GAP_AT_THRESHOLD`, or the
latter while an extracted gap of that iteration has materiality index ≥ 6.

Extracted gaps are ingested into the graph as `GAP` nodes under their declared
parent. Their materiality inputs follow a rule fixed now: severity `CRITICAL`
if, realised, the gap reverses a recorded verdict of a flagship result; `MAJOR`
if it can reverse a recorded closure grade or gate verdict of this graph;
`MINOR` if it affects identity or bookkeeping only; `INFO` otherwise. Evidence
`FINITE_EXACT` if its extent is an exact count in this package's receipt, else
`ASSERTED`. Scope `FLAGSHIP` if it touches a flagship result, `SECTION` if it
spans more than one package, `PACKAGE` if within one, else `LOCAL`. Blast = the
number of graph nodes whose grade or gate verdict it can change, capped at 3.

### 4.10 The result record

One machine-readable record per named result, with: `result_id`, `statement`,
`scope`, `is_flagship`, `assumptions`, `dependencies`, `falsifiers`,
`counterexample_methods`, `strongest_parents`, `prior_disclosure`
(`freeze_pointer`, `outcome_timing` ∈ `PRE_OUTCOME` / `SCOPING_OBSERVED` /
`POST_OUTCOME` / `UNVERIFIED`), `evidence` (`evidence_level`,
`maturity_level`), `forbidden_extrapolations`, `closure_state`,
`closure_evidence`, `provenance`. A list field holds strings or is the sentinel
string `UNREGISTERED`, never an empty list. Flagship records are built from the
AJ0 registry and `REGISTRATIONS_V2.json` by exact package equality, with a
pointer per copied field; a field with no source is `UNREGISTERED`.

## 5. Observations and predictions

**Scoping observations** (measured read-only while scoping, before this file;
registered as expected values, labelled `SCOPING_OBSERVED`, not as blind
predictions): R1 yields 46 edges from 32 source records; R2 yields 16 edges
from 10 source records; 41 of the 1140 records gain a corpus-rule descendant;
the 1140 records carry 1126 distinct gap ids (10 ids shared by 24 records); rule
4.3 closes 154 records (108 B1, 0 B2, 46 B3) with the re-derived predicate
agreeing on 154/154; 90 of the 108 B1 closures span two or more packages; 290
`CRITICAL` corpus records remain unresolved; 6 closed records have an
unresolved `CRITICAL` descendant under R1/R2 alone.

**Predictions** (`PRE_OUTCOME`): 0 cycles and 0 self-loops in the real
`DESCENDANT` and `DEPENDS_ON` subgraphs; every one of the 1094 gap claim ids
gets a claim node with an incident edge; the real graph validates with 0
findings; parent closure of `T833-B1-AA` is refused; `HOSTILE_CLOSED` is refused
for 9/9 flagship results; every planted positive fires and every clean case is
silent in both routes and both interpreter modes; the two routes agree on every
edge set, closure set, blocked set and finding list by set equality; two builds
are byte-identical.

**Falsifiers.** A cycle in the real graph; a closed record without a repair
record; a route disagreement; a planted positive that does not fire; a clean
case that alarms; a non-deterministic build. Each is reported as found, not
tuned away; a changed rule would need a dated amendment committed before the
receipt.

## 6. Rows this lane may reconcile, and the criterion

A #833 row counts as **directly earned** only if (i) the object or rule it names
is implemented here as a machine-readable artifact with a fail-closed validator,
(ii) its planted positives fire and clean cases stay silent in both modes, (iii)
it is applied to the real records at declared scope with the numbers disclosed,
and (iv) its text does not name an event or actor outside this repository (an
issue-close action, an independent team, replication, a real-scale run, a
manuscript freeze) or a completed recursion. Candidates under this criterion:

    - [ ] Maintain a live `GMI_GAP_GRAPH` linking every claim to unresolved descendants.
    - [ ] Require at least two distinct counterexample-generation methods for flagship theorems.
    - [ ] Implement the loop as a standard research template.
    - [ ] Require each iteration to create explicit new-gap records rather than silently editing assumptions.

Declared **not earnable here** under (iv), whatever the instrument does:

    - [ ] Prevent parent issue closure while any critical descendant gap remains unresolved.
    - [ ] Recurse until no new **material** gap is found under the declared scope.
    - [ ] Require independent hostile review before a gap can be marked exhausted.
    - [ ] Stop only at the declared evidence ceiling, never because the checklist is long.

and no other AA, AB, AC or AD row. The reconciliation JSON lists only rows that
meet the criterion after the receipt exists.

## 7. Parent ownership

- `gmi-833-aa-gap-object-v1` owns `OPEN_GAP`, the materiality function, the
  four-grade lattice, the bare-`closed` detector and `REPAIR_DELTA`; reused, not
  re-derived.
- `gmi-833-census-registration-pass-v1` owns `GAP_GRAPH_V2` (gap→object
  descendants on 50 of 1140 records, two-valued materiality) and the resolved
  dependency register; this package adds gap→gap edges, closure states and the
  validator on top of it.
- `gmi-833-depgraph-adjudication-v1` owns the stated-dependency edges, their
  cycle report and the DUPID/FIN2UNIV verdicts.
- `gmi-833-aa-ledger-gate-v1` owns the theorem and experiment ledger
  predicates this package's notes must satisfy.
- `gmi-833-aa-fallacy-detectors-v1`, `gmi-833-aa-logical-form-register-v1` and
  `gmi-833-aa-finite-universal-harness-v1` own the static claim-label hostiles.
- `gmi-833-aj0-foundation-scope-v1` owns the flagship list.

External parents restated, not claimed novel: strongly connected components by
Tarjan, "Depth-first search and linear graph algorithms", *SIAM J. Comput.*
1(2) 1972, doi:10.1137/0201010, and topological peeling by Kahn, "Topological
sorting of large networks", *CACM* 5(11) 1962, doi:10.1145/368996.369025;
truth-maintenance with dependency-directed retraction by Doyle, "A truth
maintenance system", *Artificial Intelligence* 12(3) 1979,
doi:10.1016/0004-3702(79)90008-0; assurance-case argument graphs (GSN, Kelly &
Weaver 2004). The residual claimed here is the typed gap graph over this
universe, its derived edge rules, the closure/promotion/parent-closure
predicates and the loop validator — not the algorithms.

## 8. Evidence standard

Two materially independent routes (route B imports nothing from route A or from
the gap-object module, recomputes R2 by fixed-point iteration, detects cycles by
Kahn peeling where route A uses Tarjan, grades by lookup table); hostiles that
fire; clean cases that stay silent; a bounded exhaustive and a seeded randomized
differential between the routes; exact integers only; stdlib only; runnable
under `python3 -I -B` and `python3 -I -O -B`.
