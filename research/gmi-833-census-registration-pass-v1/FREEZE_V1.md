# FREEZE — `gmi-833-census-registration-pass-v1` (issue #833, section AA feeder)

Status: **PRE-IMPLEMENTATION FREEZE**. Committed before any executor, oracle,
test, register, receipt, theorem note or workflow file of this package exists.
`git log --reverse -- research/gmi-833-census-registration-pass-v1/` must show
this file, alone, first.

## 1. Source pin

- `source_main` = `0dcdec54fbece041ee2b7cd1f630469ad85d19d3` (origin/main tip at
  freeze time, 2026-09-19T07:10Z).
- The corpus census this package supersedes by reference is frozen at
  `2fffb14447193cbfbed3224508a077f2d4f5d2dd` and is **never edited**: its four
  artifacts are sha256-bound in `research/gmi-833-theory-baseline-v1/` and every
  bound entry must still match after this package lands.
- Issue comment `5684607872`, anchor `### AA. Recursive loophole / logic-gap closure`.

## 2. Claim ceiling

`SOURCED_PROPAGATION_REGISTER_V1`

Every value this package writes into a previously empty or `UNKNOWN` field is a
**copy of a value already committed on `main`**, carried with a pointer
(`path#key` or `path:Lnn`) a reviewer can open. Nothing is inferred from prose,
nothing is scored here, nothing is adjudicated here. Where no committed evidence
binds to an object by the identity rules of section 4, the field stays
`UNKNOWN` (scalar fields) or becomes the explicit sentinel `UNREGISTERED`
(list fields), and the count of each is a headline number, not a footnote.

## 3. Rows this tranche may reconcile

**None.** This package closes no checkbox and earns no row. It supplies the
populated register that the next AA lane needs, and a per-row decidability
table for AA16–AA37. **No neighboring row is earned here.** Explicitly not
earned: AA08, AA10, AA16–AA18, AA20, AA22–AA30, AA32–AA36, AA38, AA40, and every
row of AB, AC and AD. The already-closed AA19, AA21, AA31 and AA37 are not
re-earned and not re-litigated. Item 9 of the closure standard is satisfied by
a reconciliation JSON with an **empty** `replacements` list.

## 4. The propagation rules, declared before any value is written

### 4.1 Object identity

A census object is the record at `(source_path, source_locator)` in
`CORPUS_INDEX_V1.json`; that pair is asserted unique over all 22553 objects and
is the register key. `object_id` is **not** a key: 857 ids are declared in more
than one place (the `GAP-DUPID-*` gaps), so an id alone never identifies an
object here.

### 4.2 Maturity / evidence placement (`maturity_level`, `evidence_level`)

Source: `THEOREM_SCORES_V2.json` (197 rows) with `SCORES_V3_DELTA.json`
applied by exact `result_id` equality afterwards (a delta naming a `result_id`
absent from v2 is a refusal, never a new row).

A scored row R with `package` P binds to exactly one census object o iff one of
two rules holds, tried in this order and never combined with anything looser:

- **B1 `RESULT_ID_SUFFIX_EXACT`** — R.`result_id` matches
  `GMI833_V2_LEGACY_NNN_<suffix>`, o.`object_id` == `<suffix>` byte-for-byte,
  o.`id_kind` == `EXPLICIT`, o.`source_path` starts with `research/P/`, and
  exactly one such o exists.
- **B2 `THEOREM_NAME_ID_EXACT`** — B1 fails; R.`theorem_name`, stripped of
  surrounding whitespace, is **the whole of** o.`object_id` (equality, not
  prefix, not substring), o.`id_kind` == `EXPLICIT`, o.`source_path` starts
  with `research/P/`, and exactly one such o exists.

Rows of the forms `GMI833_V2_ARRIVAL_*`, `GMI833_V3_ARRIVAL_*`,
`GMI833_RESCORE_*` and `GMI833_CD_NEW_*` are package-level results and bind to
**no** object: they are recorded in a separate package-level section with the
number of census objects under their package, and populate nothing. Any binding
by prefix, case-folding, suffix stripping (`_V1`/`_V2`), token overlap or path
proximity is **forbidden**; a hostile that plants such a near-miss must be
refused by both routes. Whether o.`source_path` is among R.`citation_paths` is
measured and reported; it is not a binding condition.

The value written is R.`maturity_M` / R.`evidence_EV` verbatim, with pointer
`research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json#<result_id>` and,
where the v3 delta applies, a second pointer into `SCORES_V3_DELTA.json`.

### 4.3 The four list ledgers (`assumptions`, `falsifiers`,
`forbidden_extrapolations`, `strongest_parents`)

Source: `REGISTRATIONS_V2.json` (235 objects). A registration binds to the same
census object as the scored row carrying the same `result_id` (rule 4.2); a
registration whose `result_id` is package-level binds to no object. Each list is
copied verbatim with pointer
`research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json#<result_id>.fields.<field>`
plus the registration's own declared `source` / `derivation` carried through as
a second-hop pointer. An object with no binding registration gets the sentinel
string `UNREGISTERED` in each of the four fields — a string, deliberately not a
list, so that an empty list can never be mistaken for it.

`strongest_parents` is additionally fed from `DEPENDENCY_GRAPH_V2.json` edges
whose `relation` is `STRONGEST_PARENT_DECLARED` and whose child resolves under
4.4; each such entry carries the edge's own `citation` as its pointer.

### 4.4 Dependencies (`claim_dependencies`) and by-name parents

Source: the `file_local` and `pointer_rollup` layers of
`DEPENDENCY_GRAPH_V2.json` (the 357-edge graph of PR #949). Identical edge
records are counted once. An edge's child id resolves to a census object by:

1. **UNIQUE_ID** — exactly one census object carries the child id; or
2. **CITATION_PATH** — several do, and exactly one of them has `source_path`
   equal to the path part of the edge's `citation`; or
3. **CITATION_LINE** — several are at that path, and exactly one has
   `source_locator` equal to its line part;

otherwise the edge is **refused** and listed with its reason
(`AMBIGUOUS_CHILD_IDENTITY` or `NO_OBJECT_AT_CITATION`). A resolved edge with
`parent_kind == CORPUS_CLAIM` appends the parent **id** to the child's
`claim_dependencies` (census semantics: an id, possibly one declared in several
places — that ambiguity is exactly what the gap graph records). A resolved edge
with `parent_kind == CORPUS_CLAIM_BY_NAME` appends to a separate field
`dependency_parents_by_name` and never to `claim_dependencies`. The
`parent_family_anchor`, `external_literature` and `corpus_package` layers name
no census object as child and populate nothing on objects; they are counted.

### 4.5 Gap graph: `descendants` and `materiality`

For each of the 1140 gaps with claim id c: `descendants_direct` = the register
keys of objects whose `claim_dependencies` contains c; `descendants` = the
transitive closure, following each descendant's own `object_id` back into the
edge set, with cycle protection. Both are reported per gap and in aggregate
(gaps with a non-empty set, gaps still isolated).

`materiality` is re-graded by the threshold the AA lane already proved
(`gmi-833-aa-gap-object-v1`, AAG-3), with the inputs that lane declared and
nothing else: severity rank from the gap's own `severity`; evidence
`ASSERTED` for `status == OPEN`; scope from the gap kind
(`DUPID → PACKAGE`, `FIN2UNIV → FLAGSHIP`); blast = claim-id multiplicity − 1,
capped at 3; index `M = severity + (3 − evidence) + scope + min(blast, 3)`;
grades from `OPEN_GAP_SCHEMA_V1.json`. The old constant is kept as
`materiality_v1`; `severity` (an input) is not rewritten. The result must
reproduce AAG-3's partition exactly or the package fails. Descendant counts are
**not** fed into the grade: that would be a new threshold, not the proved one.

### 4.6 Decidability of AA16–AA37

For each of the 22 rows a metadata predicate is declared **here** (in
`DECIDABILITY_V1.json`'s schema, mirrored below), naming the register field(s)
it reads. A row has a `REGISTERED_DISCRIMINATOR` after the pass iff its
predicate reads only register fields (no statement-prose parse) and is
evaluable on at least one object. The pre-declared classification:

- `ALREADY_DECIDED`: AA19, AA21, AA31, AA37 (closed on `main`).
- Candidate `REGISTERED_DISCRIMINATOR` via the `assumptions` ledger
  (predicate: evidence mode requires the named assumption class AND the
  registered ledger does not name it): AA24, AA25, AA26, AA27; via
  package-family count of registered statistical claims plus the
  `assumptions` ledger: AA33.
- Expected `NO_REGISTERED_DISCRIMINATOR` (the needed input is carried by no
  committed register: logical form, causal assertion, identifiability of the
  model, equivariance test outcome, objective form, search budget, ecology
  sample, leakage ledger, sample size, latent structure): AA16, AA17, AA18,
  AA20, AA22, AA23, AA28, AA29, AA30, AA32, AA34, AA35, AA36.

The deliverable number is the count of the 19 rows the fallacy lane left
undecidable (22 minus its 3) that now carry a `REGISTERED_DISCRIMINATOR`, with
the field whose sparsity bounds each one. If that number is small it is
reported as small. Ledger vocabulary hits are **measured** for the four
assumption rows and published as measurements; no queue is emitted and no
detector is claimed validated here.

## 5. Predictions, fixed before the executor exists

The rules above were fixed after a read-only look at the shapes of the inputs
(key names, id forms, layer names); no propagated value was written before this
commit. What is predicted:

- P1. Every `GMI833_V2_LEGACY_*` row either binds under B1 or B2 or appears in
  the refusal list with a reason; no row binds under both.
- P2. No `ARRIVAL`, `RESCORE` or `CD_NEW` row binds to any object.
- P3. The re-graded `materiality` partition equals AAG-3's 847 / 293 exactly.
- P4. A prefix/substring variant of B1 (run only as a measurement) binds
  strictly more rows than B1∪B2 **or** exactly as many; either way the planted
  near-miss hostiles are refused by both routes.
- P5. `evidence_level` and `maturity_level` populated counts are equal, and are
  at most 197; the four ledgers' populated counts are each at most 235.
- P6. Gaps with a non-empty `descendants` set are at most the number of distinct
  parent ids in the resolved dependency edges.

## 6. Hostiles (planted, must be DETECTED by both routes)

- H1 wrong pointer, missing target: a register entry whose pointer names a
  `result_id` absent from the scores file.
- H2 wrong pointer, wrong content: a pointer to a real `result_id` whose stored
  `maturity_M` differs from the value written.
- H3 similarity plant: a synthetic scored row whose `theorem_name` is a real
  census id with `_V2` appended, and one whose `result_id` suffix is a strict
  prefix of a real id — both must bind to nothing.
- H4 orphan delta: a v3 delta record naming a `result_id` not in v2 — refused.
- H5 duplicate register key — flagged.
- H6 ambiguous child edge — the real `FAC-CTW` edge is refused; a fixture that
  forces two objects at one citation line is refused.
- H7 grade-table dip — a table that dips to `IMMATERIAL` mid-range is caught by
  the monotonicity check.
- H8 planted descendant that does not depend on the claim — flagged by the
  descendant verifier.

No-alarm cases asserted on real data: the true register passes the pointer
verifier with 0 findings; the real 173 legacy bindings raise 0 similarity
refusals; the real grade table has 0 dips.

## 7. Null

200 seeded draws permuting the `package` column of the scored rows among
themselves; the number of rows that still bind under B1∪B2 is recorded per
draw. The true binding count must exceed every draw's count. A second null
appends a random suffix to each `result_id` suffix and must bind 0 rows in
every draw; that one is a construction guarantee and is reported as such, not
as evidence of selectivity.

## 8. Hand-check protocol

Twenty objects are read by hand against their pointers and recorded in
`HANDCHECK_V1.md`: twelve populated (covering B1, B2, the v3 delta row, a
dependency-edge child, a by-name parent, a `STRONGEST_PARENT_DECLARED` edge)
and eight that must remain `UNKNOWN` / `UNREGISTERED` (including an object in a
scored package whose file is cited but whose id is not the scored one, an
arrival package's object, and an object whose id collides across packages).

## 9. Parent ownership (declared before implementation)

- `research/gmi-833-corpus-census-v1/` — **owns** the corpus, the object
  schema, every field name, and the 1140-gap graph. Blobs pinned:
  `CORPUS_INDEX_V1.json` `709159c53c6284366aaf1f05380f5fada8d81a98`,
  `GMI_GAP_GRAPH_V1.json` `61006b756721c748f8dcc797c755abd25cc42956`,
  `DEPENDENCY_GRAPH_V1.json` `3371b3b48a3460cb667d237c3fb642ef783a1e88`,
  `corpus_census_v1.py` `e35f1ae92ea9d140675e01750252dca0a36d2b6e`.
- `research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json`
  `0cfca31894960e24c1c12bb7bf05f9e13e63f4aa` — **owns** every maturity and
  evidence placement copied here (PR #938 / #948).
- `research/gmi-833-maturity-rescore-v3-w4-v1/SCORES_V3_DELTA.json`
  `d8f6d02ecb61b83c20a10c5fe0fab67fbcfd5493` — **owns** the W4 correction and
  the supersede-by-reference convention this package follows.
- `research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json`
  `66c3b7e4ef91e096f0ece2720af4645bebe75238` — **owns** the 235 registered
  ledgers copied here.
- `research/gmi-833-depgraph-adjudication-v1/DEPENDENCY_GRAPH_V2.json`
  `41174e0557ac4fa721412e1afc06c72163c34f94` — **owns** the 357 cited edges
  (PR #949), their review overrides and their layer semantics.
- `research/gmi-833-aa-gap-object-v1/OPEN_GAP_SCHEMA_V1.json`
  `9050c2e01e44347aa2b19710286890be1a5eb21d` and `RESULT_V1.json`
  `e857a82fe9c30af6466e3be258c724e76c39422c` — **own** the materiality
  threshold, its monotonicity proof and the 847/293 partition.
- `research/gmi-833-aa-fallacy-detectors-v1/` (`RESULT_V1.json`
  `ed4045e835ea7b980bb3b04ced00132e4130e830`) — **owns** the finding that the
  five list fields are empty and the two level fields `UNKNOWN` on all 22553
  objects, and the metadata-not-prose discipline for AA detectors.
- `research/gmi-833-aa-ledger-gate-v1/ledger_gate_v1.py`
  `96c184bf270c05bf178cd19402c1dddf5d5a426b` — owns the ledger predicate the
  theorem note of this package must satisfy.

External parents restated, not claimed novel: provenance-carrying data
integration (Buneman, Khanna & Tan, "Why and where: a characterization of data
provenance", ICDT 2001, doi:10.1007/3-540-44503-X_20) owns the idea that every
derived cell names its source; record linkage by exact key (Fellegi & Sunter,
"A theory for record linkage", *JASA* 64(328) 1969, doi:10.1080/01621459.1969.10501049)
owns the distinction between exact-key and similarity linkage that rule 4.2
sits on the strict side of. Both `CITE-TF`; AC05 is not earned.

**Residual contribution claimed here:** (a) a sourced propagation of five
existing registers into the census object schema under exact-identity rules,
with every refusal listed; (b) a re-derived gap graph whose `descendants` and
`materiality` fields discriminate; (c) a per-row decidability table for the 22
AA fallacy rows naming, for each, the register field that supplies or fails to
supply its discriminator.

## 10. What is NOT claimed

- That any populated placement is *correct*: it is the placement `main` already
  carries, now reachable from the object.
- That an `UNREGISTERED` object has no parents or assumptions: it has none
  **registered**.
- That a gap with an empty `descendants` set is a leaf: the edge set is the
  stated-dependency mining of #949, whose own semantics say absence of an edge
  is not independence.
- Any statement about the correctness of the census's object extraction.

## 11. Forbidden promotions

`CENSUS_FULLY_REGISTERED`, `ALL_OBJECTS_SCORED`, `ALL_PARENTS_EXHAUSTED`,
`DEPENDENCY_GRAPH_COMPLETE`, `GMI_GAP_GRAPH_COMPLETE`, `ISOLATED_GAP_IS_LEAF`,
`UNREGISTERED_MEANS_NONE`, `POPULATED_MEANS_VERIFIED`, `AA_ROW_EARNED`,
`RECURSION_EXHAUSTED`, `ANALYTIC_PROOF`, `M4_RESTORED_TO_W4_PARENT`.

## 12. Evidence standard binding this package

Two materially independent routes for every count (route B imports nothing
from route A, resolves identities by a different traversal, grades by a lookup
table rather than sum-and-bucket, and closes descendants by fixed-point
iteration rather than depth-first search); hostiles detected with the moved
quantity asserted; a null the true result beats; exact arithmetic only (`int`
and `fractions.Fraction`); stdlib only; runnable under `python3 -I -B` and
`python3 -I -O -B`; Python 3.8-compatible; no edit to any frozen artifact.
