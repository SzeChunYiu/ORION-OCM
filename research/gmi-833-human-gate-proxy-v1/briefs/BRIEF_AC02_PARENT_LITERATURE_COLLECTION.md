# BRIEF AC02 — canonical AND modern parent literature per core construct (fresh-session model proxy)

You are an independent literature reviewer. A research programme names ~48 core constructs (the "legacy GMI term" column of a crosswalk) and, for each, is required to have collected both CANONICAL parent literature (the origin or standard reference of the idea) and MODERN parent literature (recent work, roughly 2015 onward, where the idea is currently developed) BEFORE naming the construct. You must judge, construct by construct, whether that collection exists in the crosswalk, and where it does not, find the missing literature yourself with web search (cite only sources you actually opened, with URL/DOI). You did not author the crosswalk.

## Rules (binding)

1. Read ONLY the files listed under "Artifacts" (absolute paths). Do not open, list, grep or search any other file or directory; do not read any other package, README, CORE, FREEZE, RESULT, issue or web page unless this brief explicitly allows web search. Do not run code unless this brief says so.
2. Do not use any self-assessment found inside the artifacts (claim ceilings, "GREEN" verdicts, hostile tables, receipts, "closed" statements) as evidence that a claim is correct. Judge the claims on their content and on what the artifacts actually show.
3. Your reply is recorded verbatim and will never be edited or re-prompted. NOT_SATISFIED and UNDECIDABLE_FROM_ARTIFACTS are fully acceptable outcomes; a false SATISFIED is the only bad outcome.
4. Make no claim you cannot support from the artifacts. Quote the artifact (path + the sentence or field) for every objection.
5. You have authority to demand that any "green" gate, closed row or accepted result you encounter in the artifacts be REOPENED; state such demands explicitly with the gate/result name.
6. End your reply with the exact block below (one `row:` line per row listed under "Rows"):

VERDICT_BLOCK_BEGIN
row: <row id> | verdict: <SATISFIED|NOT_SATISFIED|UNDECIDABLE_FROM_ARTIFACTS> | reason: <one sentence>
objection: <OBJ-id> | material: <yes|no> | text: <one sentence>
reopen: <gate or result name> | reason: <one sentence>
model_self_report: <the model identifier you believe you are running as, or UNKNOWN>
VERDICT_BLOCK_END

Additional rule: rule 1 is relaxed ONLY for web search/retrieval of literature; you still read no other repository file.

## Artifacts

- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-ac-lanes-harness-v1/AC_CROSSWALK_ADDENDUM_V1.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-tranche-ab-ac-lit/WHAT_IS_ACTUALLY_NEW_TEMPLATE_V1.md

## Output required (before the verdict block)

A table, one line per crosswalk row (1..48):
row | construct | canonical parent present in crosswalk? (yes/no, which) | modern parent (>=2015) present? (yes/no, which) | missing parent you located (author, title, year, venue, URL/DOI) or "none needed" | ordering: was the literature collected before or at naming (from the document's own dating and provenance notes), after, or undeterminable

Totals for each column.

## Rows

- AC02 — "For every core GMI construct, collect canonical and modern parent literature before naming it." SATISFIED iff every construct has both a canonical and a modern parent recorded in the crosswalk (or addendum) and nothing in the artifacts shows the literature was collected only after naming; NOT_SATISFIED otherwise, listing the constructs that fail and why. UNDECIDABLE_FROM_ARTIFACTS if the ordering question cannot be settled for a material number of constructs.
