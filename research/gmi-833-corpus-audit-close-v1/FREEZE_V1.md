# T833-B2 — GMI corpus audit adjudication close v1

**Parent:** #833 (Section B)
**Census parent:** `research/gmi-833-corpus-census-v1` (frozen source authority `2fffb14447193cbfbed3224508a077f2d4f5d2dd`, census result SHA `861b1ba1cb871677867140d523ac49b37f15b832`)
**Claim ceiling:** `GMI_SECTION_B_ADJUDICATION_AT_FROZEN_CENSUS_SUBSET_SCOPE`

This file is the pre-adjudication authority. It is written before any verdict is
recorded. The census enumerated and dispositioned 22,553 scientific objects
mechanically; it explicitly deferred semantic review. This child performs the
first bounded semantic adjudication tranche over a frozen subset of that
census. It does **not** adjudicate the whole corpus and does not promote any
object.

## 1. Scientific question

Of the census's mechanical GREEN/AMBER/RED dispositions, which survive an
actual semantic read: are the registered claims stated at the strength their
evidence supports, distinct from their parents, backed by the proof mode they
claim, and free of undisclosed assumptions — or are they overstrong,
duplicated, computation-only, enumeration-substituted, or post-hoc?

This is an **adjudication audit**, not a proof that any theorem is true, not a
retraction action, and not a corpus-wide verdict.

## 2. Frozen adjudication target (scope)

The adjudicated subset is exactly:

**(a) Mainline GREEN population — all census objects with**
- `audit_disposition == "GREEN"` **and** `id_kind == "EXPLICIT"` (237 objects),
  **restricted to claim-bearing classes** `THEOREM, LAW, CLAIM, COROLLARY,
  PROPOSITION, LEMMA, AXIOM` — plus the 64 remaining GREEN EXPLICIT objects
  (RECEIPT_CERTIFICATE, EXPERIMENT, PROTOCOL, ALGORITHM,
  FALSIFIER_COUNTEREXAMPLE, OTHER_SCIENTIFIC_OBJECT, DEFINITION) are retained
  as **context rows** only (evidence for the claim rows, not independently
  adjudicated verdict targets).

**(b) Stratified random sample — exactly 200 objects** from the AMBER+RED
population (22,316 objects at the frozen SHA), stratified by
`(audit_disposition, object_class)` over the 28 non-empty strata. Allocation:
proportional with every stratum guaranteed >= 1, largest-remainder adjustment
to exactly 200. Selection inside a stratum: `random.Random(833200)` over the
stratum's members sorted by `(source_path, source_locator, object_id)` —
deterministic and reproducible from the census index alone.

The full AMBER+RED space (22,316) is **not** adjudicated. No object outside
(a)+(b) receives a verdict.

## 3. Verdict taxonomy (frozen)

Exactly one verdict per adjudicated object:

| verdict | meaning |
|---|---|
| `CONFIRMED` | statement, quantifier scope, and evidence mode are mutually consistent at registered scope; no taxonomy defect found |
| `OVERSTRONG` | name/ceiling language stronger than the registered quantifier/proof actually licenses (incl. universal wording on bounded-only evidence) |
| `DUPLICATE` | restatement of a parent/other-package result without registered residual (census duplicate-candidate group + textual check) |
| `COMPUTATION_ONLY` | analytic-sounding claim whose only support is a computation, with no analytic bridge and no independent implementation |
| `ENUMERATION_SUBSTITUTED` | finite enumeration stands in for an analytic proof that is plausibly available (declared enumeration is fine; undeclared substitution is not) |
| `POST_HOC_ASSUMPTION` | freeze/assumption introduced after the outcome was observed, without a typed POST_HOC marker |
| `UNKNOWN` | cannot be adjudicated from registered artifacts alone (fails open as an explicit gap, never silently) |

Mapping to Section-B "Identify …" boxes: OVERSTRONG → names stronger than
quantifiers; ENUMERATION_SUBSTITUTED → enumeration where analytic proof is
possible; COMPUTATION_ONLY → analytic claims supported only by computation and
computational claims with no independent implementation; POST_HOC_ASSUMPTION →
assumptions introduced after observing outcomes; DUPLICATE → rediscoveries of
parent mathematics; the no-smuggling A1–A6 tool outputs over adjudicated
packages → search grammars encoding target morphology / cost models
structurally forcing the winner / hidden architecture macros; textual-structural
scans → hidden independence/iid/stationarity and hidden finite-horizon
assumptions.

## 4. Evidence rules

- Every verdict cites `file:line` (or the census object id + locator) and, where
  applicable, the census gap id / duplicate statement hash.
- Green-mainline rows are adjudicated against the package's own registered
  RESULT/RECEIPT artifacts and THEOREMS documents, not against folklore.
- The `gmi-833-no-smuggling-audit-v1` A1–A6 subaudit tools are run (their
  fixtures) and their output is recorded verbatim in RESULT_V1; they are
  fixture-validated tools, so package-level application of them is recorded as
  a screened/not-screened status per adjudicated 833-mainline package, never as
  a proof of prior-freeness.
- Independent-implementation cross-reference: presence of
  `independent_oracle_v1.py` + `ORACLE_RESULT_V1.json` (g0-* pattern) counts as
  the second implementation.
- Post-hoc check: compare FREEZE vs RESULT/commit ordering where registered;
  only typed POST_HOC markers (e.g. `POST_FREEZE_*` files) make a late change
  legitimate.

## 5. Claim ceiling and forbidden promotions

This child claims exactly: `GMI_SECTION_B_ADJUDICATION_AT_FROZEN_CENSUS_SUBSET_SCOPE`.

Forbidden:

- `GMI_CORPUS_AUDIT_CLOSE_COMPLETE` — the whole corpus is NOT adjudicated;
- any object auto-promoted AMBER/RED → GREEN (the census disposition is never
  overwritten; adjudication only annotates);
- `GMI_THEORY_BASELINE_V1` frozen — that box needs the FULL corpus adjudicated;
  it stays open;
- overclaims retracted — this package FLAGS; retraction is a separate
  downstream action;
- any claim that a CONFIRMED verdict proves the theorem true (it records
  scope-consistency of statement vs evidence at registered scope only).

## 6. Determinism

`audit_close_v1.py` is stdlib-only and deterministic: the sample is seeded
(`random.Random(833200)`), all iteration is over sorted keys, and re-running
reproduces `ADJUDICATIONS_V1.json` byte-identically, including under
`python -O`. The human-judged verdicts are stored as a verdict table inside the
module (keyed by object id); the module validates every table entry against the
census and fails closed on unknown ids, unknown verdicts, seed-reproducibility
failure, or a census disposition edit without a typed reason.
