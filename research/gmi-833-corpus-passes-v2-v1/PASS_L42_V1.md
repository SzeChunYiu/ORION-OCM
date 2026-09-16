# PASS-L42 — duplicated results under different terminology

**Detector:** `detector_l42_v1.py` — masked-hash grouping over the crosswalk migration
table's equivalence classes (18 rows parsed from
`gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md`, 230 compiled spans with
deterministic inflection/separator expansion). Two objects with equal masks differ only
inside crosswalk-class spans (all other text preserved verbatim by construction), so a
bucket with >= 2 distinct raw statements is a terminology-variant candidate. CLASS_A
(legacy surface on one side) vs CLASS_B (replacement<->replacement). O(N); no pairwise scan.

**Validation (all four protocol plants pass, BEFORE the real run):**

| plant | result |
|---|---|
| (a) recall on real statements + crosswalk swap | 20/20 flagged (rows R1,R3,R5,R7,R8,R12,R15) |
| (b) no-alarm on 200 real same-file non-crosswalk pairs | 0 flagged; cry-wolf control (shared generic word, differs elsewhere) 0/1 |
| (c) semantics anchor: raw-hash grouping | 1,652 multi-buckets / 7,202 objects == #949 exactly |
| (d) specificity: candidate groups with <2 raw keys; dupid-DISTINCT 200-sample | 0; 0/200 |

**Run over all 22,553 census objects: 1 candidate group (CLASS_A, row R10), 0 CLASS_B.**
Adjudicated DISTINCT — "## Ablation theorem" (gmi-capability-perturbations-v1) vs
"## Negative-twin theorem" (gmi-capability-real-regime-v1): a heading-label collision
unified by R10's legacy/replacement pair; the underlying theorems are different results in
different packages. A label match is not a restatement.

**Why so few (consistency check):** the terminology migration edited ~290 lines across
packages in single snapshots — pre-edit and post-edit versions never coexist in one census —
so intra-snapshot terminology variants are structurally rare. The single hit is exactly the
residual class (two packages independently naming the same concept on different sides of
the migration).

**Diagnostic (adjacent class, explicitly NOT terminology variants):** a
punctuation/case/plural-relaxed mask yields 128 additional near-duplicate groups —
receipt-vs-source echoes of the same line differing in quoting style, casing, or plural
(e.g. a LAW restated uppercase inside a .py checker vs title-case in its .md). These
escape BOTH the strict terminology mask AND #949's exact statement.lower() grouping.
Recommendation: a v2 content-normalization detector (quote/case/plural-canonicalized hash)
with its own plants; 128 groups is a tractable adjudication population.

**Claim:** the "same result under different terminology" duplicate class now HAS a
validated detector and a corpus-wide disposition at frozen-census scope; the class content
itself is empty (1 candidate, DISTINCT) at this snapshot.
