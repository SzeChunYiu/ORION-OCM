# Named results — `gmi-833-aa-gap-object-v1` (issue #833, section AA)

Claim ceiling: `FINITE_EXACT_GOVERNANCE_INSTRUMENT_V1`.
Every result below is an exact statement about one explicitly named finite
universe: the 1140 records of
`research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json` at
`source_main = 91c6d2876ba80c517a186e28fce3bdbe4e3fc218`
(blob `61006b756721c748f8dcc797c755abd25cc42956`), plus two finite parameter
cubes (256 materiality points, 32 closure-evidence points). These are
computer-assisted exhaustive checks over declared finite domains. **None of
them is an analytic proof of an unbounded universal statement**, and none of
them asserts that any GMI theorem is true.

---

## AAG-1 — the `OPEN_GAP` object is realizable and realized

**Scope.** The nine field names AA01 lists, and the 1140-record universe above.

**Statement.** `OPEN_GAP_SCHEMA_V1.json` binds the nine AA01 names
(*claim, premise, inference, unresolved assumption, possible counterexample,
severity, owner, parent result, evidence needed*) to nine distinct storage keys
by a total injection. Every one of the 1140 frozen records carries all nine
keys with a non-empty string value: conforming 1140/1140, missing-field events
0, empty-cell events 0, distinct `claim_id` 1094.

**Quantifiers.** For all r in the 1140 records, for all nine schema fields f:
`f ∈ keys(r)` and `r[f]` is a non-empty string. Universally quantified over the
frozen set only.

**Assumptions.** The frozen file is the one pinned by blob sha; field presence
with a non-empty string is what "the object is realized" means here.

**Falsifiers.** Any record missing a bound key; any empty/whitespace value in a
bound key; a schema binding that is not injective; a `claim_id` column that is
constant (it is not: 1094 distinct values, exact Gini impurity 129833/129960).

**Strongest parents.** `gmi-833-corpus-census-v1` owns the record set and its
13-key shape; W3C PROV owns the provenance-record idea. Not claimed novel.

**Forbidden extrapolations.** Schema conformance says nothing about whether the
1140 gaps are the *right* gaps, whether they are exhaustive, or whether any of
them is real. AA02–AA06 (per-theorem ledgers) are NOT earned by AAG-1.

---

## AAG-2 — the incumbent grading columns carry exactly zero information

**Scope.** The same 1140 records.

**Statement.** Exact rational Gini impurity `1 - Σ(n_i/n)²` is **exactly 0/1**
for six columns — `severity`, `materiality`, `status`, `owner_role`,
`parent_result`, `descendants` — each having exactly one distinct value
(`CRITICAL`, `MATERIAL`, `OPEN`, `HOSTILE_VERIFICATION`, `T833-B1-AA`, `[]`).
Therefore **no materiality threshold can be derived from the incumbent
columns**: any threshold over a constant column either admits all 1140 records
or none, which is precisely the "terminate by arbitrary convenience" failure
AA09 names.

**Quantifiers.** For each of the six named columns, for all 1140 records, the
value is equal. Exact rational arithmetic; no floats.

**Falsifiers.** A second distinct value in any of the six columns.

**Strongest parents.** Gini/Simpson impurity (Simpson 1949; Breiman et al.,
*CART*, 1984). Not claimed novel — it is used here only as an exact
zero/non-zero information witness.

**Forbidden extrapolations.** Degeneracy is a property of this frozen export,
not proof that the census tool cannot produce graded output.

---

## AAG-3 — a declared, monotone materiality threshold that is non-degenerate on the real universe

**Scope.** The finite cube (severity × evidence-mode × scope × blast) = 4×4×4×4,
and the 1140 records.

**Statement.**
`M = severity_rank + (3 − evidence_mode_rank) + scope_rank + min(blast, 3)`,
an integer in `[0, 12]`, graded `IMMATERIAL [0,2] / MINOR [3,5] / MATERIAL [6,8]
/ CRITICAL [9,12]`, with recursion threshold `M ≥ 6`.
(i) **Monotonicity**: over all 256 domain points and all 768 unit steps, the
grade is non-decreasing in severity, scope and blast and non-increasing in
evidence strength — **0 violations**.
(ii) **Non-degeneracy on the real universe**: applying the function to the 1140
records (evidence = `ASSERTED` since all are `OPEN`; scope from the gap kind,
`DUPID→PACKAGE`, `FIN2UNIV→FLAGSHIP`; blast = claim-id multiplicity − 1) yields
**847 MATERIAL and 293 CRITICAL** — a two-class partition where the incumbent
`materiality` column had exactly one class. 0 records of unknown kind.

**Why this answers "arbitrary convenience".** The threshold is a *declared total
function of four registered inputs*, fixed before the data is read, monotone
by exhaustive check. It cannot be lowered for one gap without lowering it for
every gap with the same four inputs.

**Assumptions.** The scope map `DUPID→PACKAGE`, `FIN2UNIV→FLAGSHIP` is a
declared modelling choice (a finite-to-universal extrapolation gap threatens
flagship claim language; an identifier collision is package-local). It is
stated, not derived.

**Falsifiers.** A monotonicity violation anywhere in the 256-point cube; a
record whose four inputs are defined but whose grade differs between the
sum-and-bucket route and the 256-entry lookup route; a one-class partition.

**Strongest parents.** Ordinal risk matrices (ISO 31000 / FMEA risk-priority
ordering) own the "rank × exposure" idea. Not claimed novel. The residual is
the exact monotone binding to the #833 recursion-stop rule.

**Forbidden extrapolations.** 847/293 is a grading of the *registered* gap
export, not a claim that 293 critical gaps exist in GMI. AA08 (recursion to
fixpoint) is NOT earned.

---

## AAG-4 — the four closure grades form a total chain, and bare `closed` is detectable

**Scope.** The 32 points of the closure-evidence cube; the markdown corpus at
`source_main`.

**Statement.**
`LOCALLY_CLOSED ⟸ local_checks_pass ∧ independent_route`;
`HOSTILE_CLOSED ⟸ LOCALLY_CLOSED ∧ hostiles_detected`;
`REPLICATED_CLOSED ⟸ HOSTILE_CLOSED ∧ independent_replication`;
`REAL_SCALE_CLOSED ⟸ REPLICATED_CLOSED ∧ real_scale_run`.
Over all 2⁵ = 32 evidence points the satisfied-grade set is always an **initial
segment** of that chain — **0 violations**. No evidence configuration can award
a higher grade while a lower one fails.
The bare-`closed` detector (a `closed` token is admissible only when
immediately prefixed by `LOCALLY_`, `HOSTILE_`, `REPLICATED_` or `REAL_SCALE_`)
finds **1490 bare-`closed` sites in 178 packages across 2577 markdown files**
at `source_main`. Recall on planted positives 3/3; **no-alarm case 0/4** on a
fixture containing all four qualified forms plus the distractors "enclosure"
and "closure".

**Falsifiers.** An evidence point whose satisfied set is not an initial
segment; a qualified form flagged by the detector; a bare form missed.

**Strongest parents.** Evidence-level ladders (GRADE; TRL; the #833
constitution's own `INDEPENDENT_REPLICATION` clause in
`gmi-833-corpus-census-v1/AUDIT_PROTOCOL_V1.md`). Not claimed novel.

**Forbidden extrapolations.** Defining the grades awards none of them. **No GMI
result is declared HOSTILE_CLOSED, REPLICATED_CLOSED or REAL_SCALE_CLOSED by
this package.** The 1490 measured sites are a disclosed backlog, not a claim
that they are all wrong.

---

## AAG-5 — the repair-successor interrogation is automatic and total

**Scope.** The 1140 records.

**Statement.** `REPAIR_DELTA` is a six-field record
(`closed_gap_id`, `repair_description`, `new_assumptions`, `new_gaps`,
`interrogation_answered`, `closure_grade_awarded`). The emitter is a **total**
function on well-formed gaps: 1140/1140 emitted. It **refuses** (raises) when
the gap has no id, when the repair description is empty, or when the awarded
grade is not one of the four declared grades — so "the gap was closed" cannot
be recorded without answering "what did the repair introduce?" and "at which
grade?". This is what makes AA07's question automatic rather than optional.

**Falsifiers.** A closure recordable without a `new_gaps` field; an emitter
that accepts the bare grade string `closed`; a well-formed gap the emitter
cannot process.

**Strongest parents.** Change-impact / regression-obligation records in
configuration management. Not claimed novel.

**Forbidden extrapolations.** The emitter guarantees the *question is asked and
its answer is structurally recorded*. It does not verify that the answer is
complete or correct. AA08 and AA10 are NOT earned.

---

## Explicitly NOT earned (measured, disclosed)

- **AA38** (`GMI_GAP_GRAPH` linking every claim to unresolved descendants):
  **0 of 1140** records carry a non-empty `descendants` list. The incumbent
  graph is a flat list with a descendants field. This package does not repair
  it; the repair needs a justified edge relation and is scheduled separately.
- **AA40** (block parent closure on a critical descendant) depends on AA38.
- **AA02–AA06, AA08, AA10–AA37, AA41**: out of the frozen row scope.
