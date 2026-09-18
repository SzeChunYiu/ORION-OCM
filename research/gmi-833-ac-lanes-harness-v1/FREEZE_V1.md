# FREEZE — `gmi-833-ac-lanes-harness-v1` (issue #833, section AC)

Status: **PRE-IMPLEMENTATION FREEZE**. Committed before any executor, test,
receipt, theorem note, register or workflow file of this package exists.
`git log --reverse -- research/gmi-833-ac-lanes-harness-v1/` must show this
file, alone, first.

## 1. Source pin

- `source_main` = `5e57d4292266bccf435136e1f7d72caa32e920a0`
- issue comment under reconciliation: `5684607872`, anchor
  `### AC. Literature saturation / terminology authority`
- live comment bytes at freeze: 28361 (LF only).

## 2. Claim ceiling

`REGISTERED_LITERATURE_STRUCTURE_VERIFIED_V1`

This package is an **exact instrument over structure**. It verifies that the
frozen lanes index and the frozen crosswalk carry, per lane and per row, the
structure the AC rows demand — lane coverage, canonical-term preference,
cross-field synonyms with one primary term, an earliest/strongest parent
record, and a contribution kind. **It verifies nothing about whether any
citation is correct.** Citation correctness is AC05 and is explicitly out of
scope.

## 3. The AC05 firewall (declared before implementation)

The parent lanes file and crosswalk self-flag the great majority of their
references `CITE-TF` — entered from field knowledge, not checked against a live
source. Every result in this package therefore carries the citation
verification status as a **disclosed field**, and no result may be stated in a
form that implies the citations were verified. Concretely:

- AC06 (`Record earliest/strongest known parent for each mathematical idea`) is
  earned on the **presence, uniqueness and structure** of a parent record per
  idea, with the `VERIFIED` / `CITE-TF` split reported alongside. It is NOT
  earned on the parents being the true earliest, and the result text must say
  so.
- AC05 (`Maintain citation-backed definitions rather than model-generated
  definitions`) is NOT in scope and NOT earned. Closing it off this table would
  be closing it by narrowing its meaning.

## 4. Rows this tranche may reconcile

Verbatim from comment 5684607872 under the anchor above:

    - [ ] Create expert literature lanes: theoretical CS/formal languages; statistical learning/information theory; optimization/algorithm selection; program synthesis; neural architectures; RL/control; Bayesian/causal inference; evolutionary computation/ALife; cognitive science/neuroscience; formal methods; philosophy of science.
    - [ ] Prefer canonical field terminology when definitions coincide.
    - [ ] When terminology differs across fields, state the cross-field synonyms and choose one primary paper term.
    - [ ] Record earliest/strongest known parent for each mathematical idea.
    - [ ] Record whether GMI contribution is theorem, synthesis, generalization, new selection law, new empirical result, or only terminology.

**No neighboring row is earned here.** Explicitly NOT earned:

    - [ ] For every core GMI construct, collect canonical and modern parent literature before naming it.
    - [ ] Maintain citation-backed definitions rather than model-generated definitions.
    - [ ] Require a `WHAT_IS_ACTUALLY_NEW.md` table that survives all literature lanes.
    - [ ] Re-run literature search before manuscript freeze because terminology and neighboring work can change.

and no row of AA, AB or AD.

The last of the five in-scope rows (`Record whether GMI contribution is ...`)
is earned **only if** the declared typing rule below types the whole declared
flagship set with an explicitly counted, disclosed `UNTYPED` residual that the
result text carries. If the rule cannot type the set, the row stays open and
is reported as such. That decision is made by the measurement, not chosen
afterwards.

## 5. What will be checked (declared before the numbers are read)

- **Lane coverage.** The eleven lane names the row itself spells out, split on
  `;`, are extracted from the row text — not from the lanes file — and each
  must bind to exactly one lane heading in `EXPERT_LITERATURE_LANES_V1.md`.
  The binding is injective in both directions: no lane may serve two row items,
  no row item may match two lanes. Entry counts per lane are reported.
- **Canonical preference.** For every crosswalk row whose match column begins
  `EXACT` (definitions coincide), the proposed paper term must be one of the
  row's own canonical terms, up to a declared normalization. Rows that are not
  `EXACT` are outside the row's antecedent and are counted, not judged.
- **Cross-field synonyms.** For every crosswalk row carrying more than one
  canonical term, the canonical list must be non-degenerate (distinct entries)
  and the proposed paper term column must resolve to exactly one primary term.
- **Parent record.** Every crosswalk row must carry a non-empty citations cell
  naming at least one dated or authored parent, with its verification status
  extracted and reported.
- **Contribution kind.** The six kinds the row itself names are extracted from
  the row text and must be the exact kind vocabulary of the typing register.

Whatever these numbers turn out to be is what is reported, including
violations. A violation found is disclosed and either repaired in an artifact
owned by this package or left as a named residual.

## 6. The anti-invention guard

Every required lane name, every required contribution kind and every required
comparison string used by this package must literally occur in the verbatim
text of the AC row that demands it. A test asserts this. A requirement cannot
be invented to make a row pass, and a row-named item cannot be quietly
dropped. This is the guard the AB tranche proved necessary: it caught two of
that package's own first-draft requirements.

## 7. Forbidden promotions

- `CITATIONS_VERIFIED`, `CITATION_BACKED`, `AC05_CLOSED` — see the firewall.
- `LITERATURE_SATURATED`, `ALL_PARENTS_EXHAUSTED`, `NO_PARENT_MISSED` — lane
  membership is coverage of a registered list, never exhaustion of a field.
- `WHAT_IS_ACTUALLY_NEW_COMPLETE` — only a template exists on `main`; AC08 is
  not earned.
- `PARENT_IS_EARLIEST` — the recorded parent is the earliest *known to the
  register*, and the register is not verified.
- `ANALYTIC_PROOF`.

## 8. Parent ownership (declared before implementation)

- `research/gmi-833-tranche-ab-ac-lit/EXPERT_LITERATURE_LANES_V1.md`
  blob `37a4f314f2a4693227d094bb6d7b0f01b7c5ff0e` — **owns** the eleven lanes
  and every entry in them. Not claimed novel here.
- `research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md`
  blob `9f4d25a5f59cdf83f86bc484cda7efb46a8bc054` — **owns** the 48-row
  crosswalk, its match column, its citations column and its migration rules.
- `research/gmi-833-tranche-ab-ac-lit/WHAT_IS_ACTUALLY_NEW_TEMPLATE_V1.md`
  blob `e4f1116182d16e6e74f971510b0ef883aaf16d15` — **owns** the six
  contribution kinds and the surviving-literature table template.
- `research/gmi-833-ab-terminology-harness-v1/` — owns the per-AB-row
  requirement table and the anti-invention guard pattern reused here.

External parents restated, not claimed novel: Rice, "The algorithm selection
problem", *Advances in Computers* 15 (1976),
doi:10.1016/S0065-2458(08)60520-3; Wolpert & Macready, "No free lunch theorems
for optimization", *IEEE TEC* 1(1) 1997, doi:10.1109/4235.585893; Mitchell,
"The need for biases in learning generalizations" (1980); Myhill (1957) and
Nerode (1958); van Glabbeek, "The linear time — branching time spectrum I"
(1990); Hales, "Formal proof", *Notices of the AMS* 55(11) 2008.

**Residual contribution claimed here:**
(a) a machine-checkable binding from each AC row's **own** verbatim text to the
    structure it demands, with the anti-invention guard;
(b) an exact injective lane-coverage verification against the row's own
    eleven-item list, rather than against the lanes file's self-description;
(c) the first per-row canonical-preference and primary-term audit of the
    crosswalk, including any violations it exposes;
(d) a contribution-kind register with an explicit, counted `UNTYPED` residual
    and a declared deterministic typing rule.

## 9. Evidence standard binding this package

Two materially independent routes for every computational claim; hostiles that
are detected AND whose perturbed quantity is asserted to have moved; a null the
true result beats; exact arithmetic only; stdlib only; runnable under
`python3 -I -B` and `python3 -I -O -B`; Python 3.8-compatible.
