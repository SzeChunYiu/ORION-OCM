# Parent-ownership disclosure — `gmi-833-ac05-citation-revival-v1`

Assimilation-first: every parent below is absorbed, and the residual of this
tranche is named at the end.

## Internal parents (pinned in `MANIFEST_V1.json`)

| parent | owns | what this tranche adds |
|---|---|---|
| `gmi-833-tranche-ab-ac-lit` (#844), `GMI_TERMINOLOGY_CROSSWALK_V2.md` @ blob `9f4d25a5` | the 48 rows, terms, match verdicts, definitions, migration rules, and the original citations column with its `VERIFIED`/`CITE-TF` convention | a citations column in which every row has an in-place, dated, rule-verified primary anchor; no other cell changes (tested) |
| `gmi-833-ac-lanes-harness-v1` (ACL-1..ACL-5), `AC_CROSSWALK_ADDENDUM_V1.md` | the parent choices for rows 16, 19, 21, 23, 34, 41, 47 and the AC05 firewall | the parents are verified and merged into the table; Hempel & Oppenheim retired for row 48; the harness is re-pinned to its frozen blob (its `AMENDMENT_01`) |
| route-B proxy verdict on AC05 (NOT_SATISFIED, four objections) | the diagnosis: eight rows, unmerged addendum, row 48 non-support, Harel venue | each objection is closed in the artifact and re-judged by a fresh proxy |
| `WHAT_IS_ACTUALLY_NEW_TEMPLATE_V1.md` @ `acb38c8b` | the six contribution kinds | named as the primary source of row 48, with the kinds traced verbatim to issue row AC07 |

## External parents (all resolved 2026-09-19; DOIs in the register)

Citation verification practice: Crossref metadata matching and DOI
resolution are the standard mechanised checks (Crossref REST API,
api.crossref.org); OpenAlex abstracts (api.openalex.org) supplied
abstract-level passages. Nothing here is novel methodology: the four-clause
rule (identifier + metadata match + passage + in place) is ordinary
reference-checking discipline written down so a stdlib script can hold the
table to it.

Substantive parents newly added to the crosswalk (each verified in the
register): Sangiorgi 2009 (bisimulation origins), Blumer et al. 1989
(VC dimension and learnability), Ernst 2004 (permutation methods), Deb et
al. 2002 (Pareto-optimal front), Hüllermeier & Waegeman 2021
(aleatoric/epistemic), Tulving 1985 (memory systems), Lehman & Stanley 2011
(novelty search, replacing the 2008 proceedings anchor without a stable
identifier), Simon 1973 (logic of discovery), Wobbrock & Kientz 2016
(contribution types), Cook 1971 (reduction), Harel 1987 (statecharts).

## What is NOT claimed novel

- No definition is new; no term is renamed; no match verdict changes.
- No claim that any cited parent is the earliest, or that the eleven lanes
  are saturated (AC02/AC09 stay open).
- The verification is dated (2026-09-19) and structural in CI: the
  workflow re-checks that the table and the register agree, not that the
  web still resolves.

## Residual contribution of this tranche

An in-place, per-row, rule-verified citations column with a machine-readable
register (HTTP status, metadata match, passage, locator, route, role per
anchor), an honest programme-internal citation form for coinages, the Harel
venue fix, and a two-route structural checker with seven detected hostiles
and a 200-draw null — enough for a fresh proxy to re-judge AC05 from the
artifact alone.
