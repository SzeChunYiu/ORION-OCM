# Named results — `gmi-833-ac-lanes-harness-v1` (issue #833, section AC)

Claim ceiling: `REGISTERED_LITERATURE_STRUCTURE_VERIFIED_V1`.

Every result below is an exact statement about explicitly named finite objects
at `source_main = 5e57d4292266bccf435136e1f7d72caa32e920a0`: the **11** lanes
and **74** entries of `EXPERT_LITERATURE_LANES_V1.md`
(blob `37a4f314f2a4693227d094bb6d7b0f01b7c5ff0e`), the **48** rows of
`GMI_TERMINOLOGY_CROSSWALK_V2.md`
(blob `9f4d25a5f59cdf83f86bc484cda7efb46a8bc054`), the five verbatim AC row
strings of comment 5684607872, and 200 seeded permutations.

**These are statements about structure, never about correctness.** Nothing here
verifies a citation. The parent artifacts self-flag most of their references
`CITE-TF` — entered from field knowledge, not checked against a live source —
and every result below carries that split as a disclosed field. **AC05 is out of
scope and is not earned.**

---

## ACL-1 — the eleven lanes AC01 names bind one-to-one to the eleven registered lanes

**Scope.** The eleven items of AC01's own text and the eleven `## Lane N` headings.

**Statement.** The lane list is extracted from the **row's** verbatim text, not
from the lanes file, by splitting on `;`. Under a declared normalization
(lowercase; `/`, `-` and `,` read as spaces; whitespace collapsed) each of the
**11** row items matches exactly **one** lane heading, and each of the **11**
headings serves exactly **one** row item: the binding is injective in both
directions, with **0** unbound items and **0** lanes serving two items. The
lanes carry **74** entries in total, minimum **6** per lane.

**Quantifiers.** For every row item i there is exactly one lane l with
`norm(l) = norm(i)`, and for every lane l exactly one such i.

**Assumptions.** "Create expert literature lanes: …" is discharged by the lanes
existing, being named as the row names them, and being non-empty. Entry counts
measure population, not saturation.

**Dependencies.** `gmi-833-tranche-ab-ac-lit` owns the lanes file and every
entry. No dependency on any GMI theorem.

**Falsifiers.** A row item matching zero or two headings; a heading serving two
items; a lane with fewer entries than reported; a twelfth lane heading.

**Strongest parents.** The lanes file **owns** the lanes. The residual is that
the coverage is checked against **AC01's own eleven-item list** rather than
against the file's self-description, and that the binding is required to be
injective both ways — a file could otherwise satisfy a one-directional check by
duplicating a lane.

**Forbidden extrapolations.** `LITERATURE_SATURATED` and `NO_PARENT_MISSED` are
forbidden. Eleven populated lanes is coverage of a registered list; it is not
exhaustion of eleven fields.

---

## ACL-2 — every `EXACT` crosswalk row adopts a canonical term

**Scope.** The **27** crosswalk rows whose match column begins `EXACT`; the
remaining **21** are outside the row's antecedent and are counted, not judged.

**Statement.** AC03's antecedent is "when definitions coincide", which the
crosswalk's own key spells as `EXACT` = "an established academic term
accurately matches the object (adopt it in paper-facing text)". Two structural
witnesses of adoption are checked: the migration rule begins `RENAME` or
`PAPER-RENAME` (**25** of 27), or the proposed paper term shares a content token
with one of the row's own canonical terms (**19** of 27). **27 of 27** satisfy
at least one. **0** violations.

**Quantifiers.** For every `EXACT` row.

**Assumptions.** Either witness is sufficient. Two rows adopt the canonical term
while carrying a `QUALIFY` rule (`quotient`, `open-ended`); the token witness is
what recognizes them, and a single-witness test would have reported them as
false positives. A false positive costs more than a miss: a checker that cries
wolf on its first real run gets switched off.

**Dependencies.** The crosswalk's match column and migration-rule key, both
owned by `gmi-833-tranche-ab-ac-lit`.

**Falsifiers.** An `EXACT` row proposing a coined term with a `DEFINE` rule and
no canonical overlap — the hostile H2 constructs exactly that and moves the
count 27 → 26.

**Strongest parents.** The crosswalk owns every verdict. The residual is the
first machine-checkable audit of its own stated adoption rule.

**Forbidden extrapolations.** Adoption of a canonical *term* is not agreement of
*definitions*; the crosswalk's `EXACT` verdict is itself unverified.

---

## ACL-3 — every multi-synonym row resolves to exactly one primary paper term

**Scope.** The **40** crosswalk rows whose canonical column lists two or more
distinct synonyms; the other **8** are outside the antecedent.

**Statement.** AC04 requires the cross-field synonyms to be stated *and* one
primary paper term chosen. **38 of 40** are resolved by the frozen crosswalk —
either the proposed term is a single term, or the migration column carries a
parenthetical, which is the parent document's own convention for a term-choice
rule. The remaining **2** (row 23 `niche`, row 33 `parent subtraction`) offer a
menu of three or four alternatives under a bare `PAPER-RENAME` with no
instruction at all; a primary term and an explicit term-choice rule for each is
supplied in `AC_CROSSWALK_ADDENDUM_V1.md`. **40/40** resolved, **0** unresolved.

**Quantifiers.** For every row in the antecedent.

**Assumptions.** "Has a parenthetical" is a *structural* test chosen precisely
because it cannot be tuned toward an outcome the way a list of instruction verbs
could — an earlier verb-list draft flagged nine rows, seven of them wrongly,
because the verb list had not been widened to include `prefer`, `adopt` and
`map`. Widening a vocabulary until the violations disappear is outcome tuning;
the structural test is not.

**Dependencies.** ACL-2's parse of the same table; the addendum, owned here.

**Falsifiers.** A multi-synonym row with neither a single proposed term nor a
parenthetical that the addendum does not cover — hostile H3 strips a
parenthetical and moves the count 38 → 37.

**Strongest parents.** The crosswalk owns 38 of the 40 resolutions and the
term-choice-rule convention. The residual is the audit and the two supplied rules.

**Forbidden extrapolations.** A stated primary term is not a migrated corpus.
AB02's corpus debt is untouched here.

---

## ACL-4 — every crosswalk row carries an earliest-or-strongest parent record

**Scope.** All **48** crosswalk rows.

**Statement.** **40 of 48** rows carry a citations cell with a dated or
authored anchor. The other **8** (rows 16, 19, 21, 23, 34, 41, 47, 48) cite the
AB audit list, a house discipline, or a sibling artifact of the same tranche —
none of which is a parent. A dated parent record is supplied for each of the 8
in `AC_CROSSWALK_ADDENDUM_V1.md`, giving **48/48**. The verification split in
the parent artifact is **15 VERIFIED**, **29 CITE-TF**, **4 UNMARKED**, and
**every one of the 8 supplied records is CITE-TF**.

**Quantifiers.** For every crosswalk row.

**Assumptions.** A parent record is *present* when the cell names a dated or
authored work. Presence is what is checked. The recorded parent is the earliest
or strongest **known to the register**, and the register is not verified.

**Dependencies.** The crosswalk's citations column; the addendum, owned here.

**Falsifiers.** A row with no dated parent after the addendum; a supplied record
without a date; a `CITE-TF` reference counted as `VERIFIED` — hostile H5 shows
that promotion would move the verified count 15 → 44, and it is refused.

**Strongest parents.** The crosswalk owns the 40 existing records and the
`VERIFIED` / `CITE-TF` convention. The residual is the audit and the 8 supplied
records.

**Forbidden extrapolations.** `CITATIONS_VERIFIED`, `CITATION_BACKED` and
`PARENT_IS_EARLIEST` are all forbidden. **AC05 is not earned here**, and closing
it off this table would be closing it by narrowing its meaning.

---

## ACL-5 — AC07 is not earned, and the reason is measured

**Scope.** The six contribution kinds AC07's own text names, and the object
fields registered by `gmi-833-corpus-census-v1`.

**Statement.** Two of the six kinds have a discriminator among the fields
registered on `main`: *theorem* (`proof_evidence_mode ∈ {ANALYTIC_DEDUCTIVE,
MECHANIZED_PROOF}`) and *new empirical result* (`∈ {EMPIRICAL_EXPERIMENT,
STATISTICAL_EXPERIMENT}`). The other **4** — *synthesis*, *generalization*,
*new selection law*, *terminology* — have **none**: each is a statement about a
claim's relation to its parents, and no parent relation is registered
(`claim_dependency_edges` is empty over all 22553 objects). A deterministic rule
cannot type the declared set, so **AC07 stays open**, exactly as
`FREEZE_V1.md` §4 said it would if the rule could not type the set.

**Quantifiers.** Over all six kinds.

**Assumptions.** A kind is *recorded* only when something determines it. A
keyword classifier over result prose would manufacture a kind rather than record
one, and would be a false positive generator at corpus scale.

**Dependencies.** `gmi-833-corpus-census-v1`'s registered field vocabulary;
ACL-1's guard for the six kind names, which are extracted from AC07's own text.

**Falsifiers.** A registered field that discriminates any of the four; a
defensible deterministic rule that types the declared flagship set with a small
counted residual.

**Strongest parents.** `WHAT_IS_ACTUALLY_NEW_TEMPLATE_V1.md` **owns** the six
kinds and the typing discipline. The residual is the measurement that no
registered field supports them — which is also the concrete reason AC08's filled
table requires authored judgement per claim and cannot be generated.

**Forbidden extrapolations.** This says nothing about whether the six kinds are
the right taxonomy, only that `main` registers nothing that decides them.
