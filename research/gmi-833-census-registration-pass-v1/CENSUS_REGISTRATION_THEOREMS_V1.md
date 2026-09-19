# Named results — `gmi-833-census-registration-pass-v1` (issue #833, section AA feeder)

Claim ceiling: `SOURCED_PROPAGATION_REGISTER_V1`.

Every result below is an exact statement about explicitly named finite
objects: the **22553** registered objects of `CORPUS_INDEX_V1.json` (frozen
source `2fffb144`, blob `709159c5`), the **1140** gaps of `GMI_GAP_GRAPH_V1.json`,
the **197** rows of `THEOREM_SCORES_V2.json` plus the **2** records of
`SCORES_V3_DELTA.json`, the **235** objects of `REGISTRATIONS_V2.json`, and the
**357** edges of `DEPENDENCY_GRAPH_V2.json`. Nothing is inferred from prose.
A populated field is a **copy** of a value `main` already carries, reachable
from the object with a pointer; it is not thereby verified. An `UNREGISTERED`
field says no committed register binds to the object; it does not say the
object has no parents or assumptions.

---

## CRP-1 — 173 scored rows bind to census objects by exact identity; 24 do not, and cannot

**Scope.** The 197 scored rows and the 22553 census objects.

**Statement.** Under rule B1 (`result_id` suffix equals an `EXPLICIT`
`object_id` inside the row's package, exactly one such object) **145** rows
bind; under rule B2 (the whole `theorem_name` equals such an id, exactly one)
**28** more bind; **173** rows bind to **173** distinct objects, and **0**
legacy rows are refused. All 173 bound objects lie in a file the row itself
cites (`source_path ∈ citation_paths`, measured, not required). The **24**
`ARRIVAL` rows and the 1 `V3_ARRIVAL` record are package-level results whose
packages hold **0** census objects — they post-date the frozen source — so they
populate nothing and are listed as package-level. A prefix-match variant of B1,
run only as a measurement, binds **0** additional rows. The v3 delta applies to
exactly **1** bound row, `GMI833_V2_LEGACY_074_W4-C`, superseding `M4/EV3` with
`M2/EV2`; the delta's other record is package-level. Two independent routes
agree on the bound set, the rule per row and every written level by dict
equality.

**Quantifiers.** For every scored row R: R binds to o iff B1(R, o) or (¬B1(R, ·)
and B2(R, o)); over the frozen corpus only.

**Assumptions.** The scoring lane's `result_id` suffix and `theorem_name` are
that lane's own identities for the objects it scored (its `citation_paths`
confirm the file in 173/173 cases). An object bound here inherits a
*placement*, not a verification: `individually_verified` is not read.

**Dependencies.** `gmi-833-corpus-census-v1` for the objects;
`gmi-833-maturity-rescore-v2-v1` for the placements;
`gmi-833-maturity-rescore-v3-w4-v1` for the W4 correction.

**Falsifiers.** A row bound under both rules; a row bound to two objects or two
rows to one object; a bound object outside its row's package; a similarity
plant (real id + `_V2`, or a strict prefix of a real id) that binds — hostile
H3 plants both and both are refused; a route-B bound set differing by one row.

**Strongest parents.** Fellegi & Sunter, "A theory for record linkage", *JASA*
64(328) 1969, doi:10.1080/01621459.1969.10501049, owns the exact-key versus
similarity distinction this rule sits on the strict side of. The scoring lane
**owns** every placement. The residual is the binding rule and its refusals.

**Forbidden extrapolations.** `ALL_OBJECTS_SCORED`, `POPULATED_MEANS_VERIFIED`,
`M4_RESTORED_TO_W4_PARENT`. 172 objects carry a maturity placement and 170 an
evidence placement (1 and 3 bound objects are scored `UNKNOWN` by the lane
itself); **22380** objects are unbound and stay `UNKNOWN`.

---

## CRP-2 — four ledgers and 113 dependency edges are propagated with one pointer per entry; 12 edges are refused

**Scope.** The 235 registrations, the `file_local` and `pointer_rollup` layers
of the dependency graph (168 records, 165 after exact de-duplication), and the
register.

**Statement.** The **173** registrations whose `result_id` is a bound row
populate `assumptions`, `falsifiers`, `forbidden_extrapolations` and
`strongest_parents` on their objects (**173** each); the **62** package-level
registrations populate nothing. Of 165 distinct edge records, **153** resolve
their child to one object (**142** by a unique id, **11** by the citation path,
**0** needed the citation line) and **12** are refused: **6**
`AMBIGUOUS_CHILD_IDENTITY` (`FAC-CTW`, declared 6 times; `CAU-1`, declared 17
times) and **6** `NO_OBJECT_AT_CITATION` (rollup records whose child is
declared elsewhere than the cited line). The resolved edges yield **113**
object→id dependency edges on **30** objects with **104** distinct parent ids;
**40** by-name parent records go to a separate field and never into
`claim_dependencies`; **9** `STRONGEST_PARENT_DECLARED` edges add entries to
`strongest_parents`, taking that field to **179** populated objects. Every
populated entry carries a pointer; the verifier opens all **1895** pointers and
raises **0** findings, while a pointer to a missing row (H1) and a pointer to a
row with a different placement (H2) are each caught. The remaining **22380**
objects carry the string sentinel `UNREGISTERED` in each ledger field, and
**0** populated lists are empty.

**Quantifiers.** For every registration and every edge record of the two
layers; refusals are exhaustive, not sampled.

**Assumptions.** The #949 miner's `child` is the census object the relation
line belongs to (its own semantics); the citation may name a neighbouring line
of the same file, which is why UNIQUE_ID is tried before the citation. A
by-name parent is a name, not an id, and is kept out of the id-typed field.

**Dependencies.** `gmi-833-claim-discipline-v1` for the ledgers;
`gmi-833-depgraph-adjudication-v1` for the edges and their review overrides;
CRP-1 for the object each registration lands on.

**Falsifiers.** A populated entry without a pointer, or a pointer whose target
content differs from the entry; a refused edge that one of the three
resolution steps would in fact resolve; an edge resolved to an object other
than the one the citation names when several share the id; route B's edge set
or refusal set differing by one record.

**Strongest parents.** Buneman, Khanna & Tan, "Why and where: a
characterization of data provenance", ICDT 2001, doi:10.1007/3-540-44503-X_20,
owns per-cell provenance. `gmi-833-depgraph-adjudication-v1` **owns** every
edge and `gmi-833-claim-discipline-v1` every ledger. The residual is the
placement of both onto the census schema with refusals listed.

**Forbidden extrapolations.** `UNREGISTERED_MEANS_NONE`, `DEPENDENCY_GRAPH_COMPLETE`,
`ALL_PARENTS_EXHAUSTED`. The 40 by-name parents include strings the miner
lifted verbatim (a section reference, a file path); they are copied as
recorded and are not claimed to be parents in any stronger sense.

---

## CRP-3 — `materiality` becomes two-valued at exactly AAG-3's partition, and `descendants` populate 50 of 1140 gaps

**Scope.** The 1140 gaps.

**Statement.** Re-grading with the threshold `gmi-833-aa-gap-object-v1`
proved — inputs unchanged: severity rank, evidence `ASSERTED`, scope by gap
kind, blast = claim-id multiplicity − 1 capped at 3 — gives **847 MATERIAL /
293 CRITICAL / 0 / 0**, reproducing AAG-3 exactly; the old constant is kept
as `materiality_v1`, and the field's distinct-value count moves **1 → 2**. The
monotonicity check over the 256-point cube reports **0** violations, and a
table dipping to `IMMATERIAL` mid-range is caught (H7, 136 violations). From
the 113 propagated edges, **50** gaps gain a non-empty `descendants` set
(**59** direct entries, **62** after transitive closure) and **1090** remain
isolated. The descendant verifier walks all 62 entries with **0** findings and
flags a planted stranger (H8). Route B's fixed-point closure and lookup-table
grades agree per gap.

**Quantifiers.** For every gap; for every domain point of the cube.

**Assumptions.** Descendant counts are **not** an input to the grade: the
proved threshold is applied as proved. A gap's descendants are the objects
whose *stated* dependencies reach its claim id; absence is not independence
(the #949 semantics).

**Dependencies.** `gmi-833-aa-gap-object-v1` for the threshold; CRP-2 for the
edges.

**Falsifiers.** Any grade count other than 847/293; a violation in the cube; a
descendant that does not reach the claim id; a gap listed isolated that has a
resolved edge into its claim id.

**Strongest parents.** `gmi-833-aa-gap-object-v1` **owns** the threshold and
the partition; ordinal risk matrices own the rank-sum idea. The residual is
applying the proved grade to the graph and populating descendants from
committed edges.

**Forbidden extrapolations.** `ISOLATED_GAP_IS_LEAF`, `GMI_GAP_GRAPH_COMPLETE`,
`RECURSION_EXHAUSTED`. AA38 and AA40 are **not** earned: 1090 of 1140 gaps have
no stated descendant in the corpus's own dependency mining.

---

## CRP-4 — 5 of the 19 undecidable fallacy rows gain a registered discriminator; the `assumptions` ledger at 173/22553 is the binding sparsity

**Scope.** The 22 rows AA16–AA37 and the populated register.

**Statement.** Under the criterion declared in the freeze — a row is decidable
from the register iff a metadata predicate reading only register fields is
evaluable on at least one object — **4** rows were already decided on `main`
(AA19, AA21, AA31, AA37), **5** gain a registered discriminator (AA24, AA25,
AA26, AA27 through the `assumptions` ledger; AA33 through the registered
package-family count of statistical claims plus that ledger), and **13** have
no register field that carries the input they need. Of the 19 the fallacy lane
counted undecidable, 1 (AA21) was already decided elsewhere, so the count of
newly decidable rows is **5**, and the population on which each is evaluable is
bounded by `assumptions`: **173** of **22553** objects (`173/22553`); AA24/AA25
are evaluable on the **15** registered objects whose evidence mode is a run
experiment, AA26/AA27 on all **173**, AA33 on the **10** registered statistical
claims in **2** package families (one of size 9). Ledger vocabulary is
measured, not queued: the registered ledgers name a dependence-class
assumption on **4** of 15, a stationarity-class assumption on **0** of 15, a
horizon bound on **8** of 173 and a finiteness bound on **61** of 173. Route B
reproduces every evaluable count.

**Quantifiers.** For each of the 22 rows; over the register after the pass.

**Assumptions.** The pre-declared classification (freeze 4.6) is what was
scored; no row was moved after the numbers were read. The rows' discriminating
predicates are declared here and remain **unvalidated as detectors**: no
planted positives, no no-alarm case, no queue.

**Dependencies.** CRP-2 for the populated ledgers; `gmi-833-aa-fallacy-detectors-v1`
for the metadata-not-prose criterion and the 3-of-22 baseline.

**Falsifiers.** A row classified `NO_REGISTERED_DISCRIMINATOR` for which some
committed register field does carry the needed input; a row classified
`REGISTERED_DISCRIMINATOR` whose predicate in fact needs a statement-prose
parse; an evaluable count exceeding 173.

**Strongest parents.** `gmi-833-aa-fallacy-detectors-v1` **owns** the
decidability framing and the finding that 19 rows lacked a discriminator;
`gmi-833-aa-ledger-gate-v1` owns ledger emission as a decidable predicate. The
residual is the per-row table and the identification of `assumptions` as the
binding field.

**Forbidden extrapolations.** `AA_ROW_EARNED` — none of the 22 rows is earned
here. A row with a registered discriminator is *decidable on 173 objects*, not
decided, and not decidable on the other 22380.

---

## CRP-5 — the register is verified by pointer, every hostile is detected, and the binding beats its null

**Scope.** The register, the hostiles H1–H8, and 200 seeded permutations.

**Statement.** The pointer verifier raises **0** findings on the real register
(1895 pointers) and the descendant verifier **0** on the real graph (62
entries); the same verifiers catch H1 (missing target), H2 (wrong content) and
H8 (planted descendant). H3's similarity plants (`DT-2A_V2`, `DT-2`) bind
nothing; H4's orphan delta is refused without changing any count; H5's
duplicated object aborts the load; H6 refuses the real `FAC-CTW` and `CAU-1`
edges and a fixture forcing two objects at one line; H7's dipping grade table
yields 136 violations against 0. Permuting the package column across the 197
rows binds **42–69** rows per draw (exact mean **11787/200**) against the true
**173**, with **0** of 200 draws at or above it; the random-suffix null binds
**0** in every draw and is reported as a construction guarantee only.

**Quantifiers.** Over the eight hostiles and all 200 draws.

**Assumptions.** The permutation null keeps each row's id and destroys only
its package, which is the right null for a rule that requires the id to be
declared *inside that package*: what it measures is how much of the binding is
carried by the package conjunct.

**Dependencies.** CRP-1 to CRP-3 for the quantities each hostile moves.

**Falsifiers.** A hostile whose quantity does not move; a finding on the real
register; a null draw reaching 173.

**Strongest parents.** Permutation nulls and planted-defect validation are
standard practice and not claimed novel; `gmi-833-aa-gap-object-v1` and
`gmi-833-aa-fallacy-detectors-v1` established the hostile-plus-null form this
package follows.

**Forbidden extrapolations.** `POPULATED_MEANS_VERIFIED`: a pointer that opens
to the right value proves the copy is faithful, not that the copied placement
or ledger is correct.
