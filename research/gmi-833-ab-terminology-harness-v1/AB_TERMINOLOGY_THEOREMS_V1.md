# Named results — `gmi-833-ab-terminology-harness-v1` (issue #833, section AB)

Claim ceiling `REGISTERED_TERMINOLOGY_AUDIT_VERIFIED_V1`. Every result is an
exact statement about named frozen artifacts at
`source_main = 91c6d2876ba80c517a186e28fce3bdbe4e3fc218`. None asserts that any
GMI theorem is true, and none asserts that the corpus has been migrated.

---

## ABH-1 — every AB row's own named comparison terms are covered

**Scope.** The 34 in-scope AB rows of comment 5684607872 and their 153
comparison terms, quoted from the rows themselves.

**Statement.** Binding each row to its crosswalk legacy term(s) and requiring
that every comparison term the row names appears in that row's substantive
cells (proposed paper term, academic field, canonical terms, definition,
migration rule — the `legacy` cell is **excluded**, so a row cannot discharge
its own audit by repeating the name under audit):

- **149 / 153** comparison terms are covered by the frozen parent crosswalk
  (48 rows) — the parent owns the audit;
- **4 / 153** were measured absent and are supplied by
  `AB_CROSSWALK_EXTENSION_V1.md` (4 rows): `algorithm class | configuration
  class` (AB04), `possibility space` (AB12), `novel implementation` (AB24),
  `verifier feedback` (AB31);
- **153 / 153** after the extension. Every bound row additionally carries a
  match verdict in {EXACT, PARTIAL, NON, EXACT-retain}, a non-empty citations
  cell and a non-empty migration rule.
- **34 / 34** in-scope rows verdict EARNED.

**Quantifiers.** For every in-scope AB row r and every comparison term t that r
names: t occurs, normalized, in the substantive cells of r's bound crosswalk
row(s). Universally quantified over the 34 rows only.

**Assumptions.** Coverage means normalized literal occurrence (case, markdown
emphasis, hyphen/space and dash variants folded). No synonym expansion is
performed — an absent term is reported absent.

**Falsifiers.** A required term absent from the bound row's substantive cells;
a bound row with an empty citations or migration cell; a match verdict outside
the declared four; a requirement demanded that the AB row does not itself name
(asserted impossible by `test_every_required_term_occurs_in_the_row_text`).

**Strongest parents.** `gmi-833-tranche-ab-ac-lit` **owns** the crosswalk, the
banned list, the 11 literature lanes and the scanner; the external parents
(Rice 1976; Mitchell 1980; Wolpert–Macready 1997; Alur et al. 2013;
Wagner–Altenberg 1996; Hales 2008; Pearl 2000; Der Kiureghian–Ditlevsen 2009)
own the canonical terminology. **Nothing in the audit itself is claimed novel.**

**Forbidden extrapolations.** Coverage of a comparison term is not evidence
that the corpus uses the term correctly, that the cited reference has been
re-verified (most parent citations are self-flagged `CITE-TF`), or that the
legacy term is or is not novel.

---

## ABH-2 — the audit clause and the corpus-state clause are separated and both measured

**Scope.** The flagship document set: every markdown under `research/` plus
repo-root markdown, minus four declared authority/migration packages
(`gmi-833-tranche-ab-ac-lit`, `gmi-833-ab-terminology-harness-v1`,
`gmi-833-terminology-migration-v1`, `gmi-833-checklist-mirror-v1`), which quote
the banned terms definitionally.

**Statement.** Running the frozen parent gate over that scope at `source_main`
finds **9703 banned-term sites in 1400 of 2572 files**. The parent migration
package `gmi-833-terminology-migration-v1` executed the migration over the
non-`aj` `research/gmi-833-*` corpus (58 packages) and reports zero
unacknowledged hits there; the remaining debt lies **outside** that scope.
Therefore:

- the **audit clause** of each in-scope AB row is EARNED (ABH-1);
- the **corpus-state clause** is **NOT** discharged repo-wide, and the number
  above is disclosed rather than absorbed;
- **AB02**, whose governing verb is the corpus-mutating `Replace`, is
  consequently **NOT earned** and stays open.

**Falsifiers.** A measurement showing the flagship scope is already clean; a
scope definition that silently drops packages with hits.

**Forbidden extrapolations.** 9703 is a count of gate hits, not of errors: the
gate is deliberately conservative (bare `morphology`, bare `selection`, bare
`carrier` dominate) and a hit is a review obligation, not a proven misuse.

---

## ABH-3 — a blocking repo-wide ratchet, which the parent workflow is not

**Scope.** `.github/workflows/gmi-833-ab-terminology-harness-v1.yml` and
`terminology_ratchet_v1.py`.

**Statement.** The parent workflow `gmi-833-ab-ac-lit-v1.yml` triggers only on
`research/gmi-833-tranche-ab-ac-lit/**` and runs the gate with `|| true`, so a
new package can land with any banned term and nothing fails. This package adds
a gate that (i) triggers on `research/**` and repo-root markdown, (ii) scans the
whole flagship set, (iii) compares per-(file, term) counts against the frozen
baseline `TERMINOLOGY_BASELINE_V1.json`, and (iv) **exits non-zero** if any
count rises or any new file acquires a banned term, while counts that fall are
reported as progress and never fail the build. That is what AB37's
"terminology review as a CI/checklist gate for flagship documents" requires and
what the parent does not supply.

**Validated on real data.** No-alarm: the gate scores 0 on clean prose and
PASSES on the unmodified repository (0 regressions, 0 new files). Recall: an
end-to-end hostile that writes a real markdown file containing `remint`,
`obligation` and `machine species` moves the measured hit count from 0 to 3 and
is named as a new file with banned terms.

**Falsifiers.** A new banned-term site that the gate does not fail on; a
reduction in debt that the gate fails on; a baseline that is vacuous (asserted
non-vacuous: > 1000 hits, > 100 files, strictly fewer files with hits than
files scanned).

**Scope policy.** On `pull_request` the new-file rule is scoped to the PR's own
markdown diff (`--owned-files`), so a lane is failed only for files it added or
grew; unowned new files with hits are reported informationally. On `push` to
`main` the strict repo-wide rule applies. This is a deliberate choice: a gate
that fires on another lane's work is a gate that gets switched off.

**Forbidden extrapolations.** A ratchet freezes debt; it does not repay it. The
9703 acknowledged sites remain an open migration obligation owned by
`gmi-833-terminology-migration-v1`.

---

## Explicitly NOT earned

| row | reason (measured) |
|---|---|
| AB02 | corpus-mutating verb `Replace`; `obligation` sites remain in the flagship scope and the migration lane owns the repair |
| AB08 | no artifact enumerates Rice's five components (problem space, feature space, algorithm space, performance space, selection mapping) as an explicit parent subtraction; the crosswalk cites Rice 1976 but does not subtract him |
| AB25 | the six novelty-ladder levels are *named* in crosswalk row 40 and extended here with `novel implementation`, but no level carries an operational criterion, so the ladder is not yet *defined* |
