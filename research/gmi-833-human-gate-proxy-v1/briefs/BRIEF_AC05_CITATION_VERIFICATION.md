# BRIEF AC05 — citation verification of a terminology crosswalk (fresh-session model proxy)

You are an independent bibliographic verifier. A research programme maintains a crosswalk table mapping its internal terms to established academic terms, each row carrying one or more citations and a definition. Most citations are self-flagged "CITE-TF" (entered from field knowledge, not checked against a source). Your job is to CHECK EVERY CITATION AGAINST A LIVE SOURCE and report, row by row, whether the definition is actually backed by the cited work. You did not author the table. Web search and fetching are REQUIRED here: a citation counts as verified only if you retrieved a source (publisher page, DOI landing page, arXiv, Google Scholar/CrossRef record, library catalogue, Wikipedia article for definitional claims that cite Wikipedia) and it confirms author(s), title, year and venue as cited AND the work plausibly supports the definition in the row. Record the URL/DOI you opened for every row.

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

Additional rule: rule 1 is relaxed ONLY for web retrieval of the cited sources; you still read no other repository file.

## Artifacts

- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md (48 rows)
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-ac-lanes-harness-v1/AC_CROSSWALK_ADDENDUM_V1.md (8 supplied parent records)

## Output required (before the verdict block)

A table with one line per crosswalk row (1..48) and one per addendum record, columns:
row | citation as written | status ∈ {VERIFIED, MISMATCH, NOT_FOUND, UNVERIFIABLE} | what you opened (URL/DOI) | does the source support the row's definition? (yes/partly/no) | note

Status meanings: VERIFIED = bibliographic record confirmed and definition supported; MISMATCH = the work exists but author/title/year/venue or the claimed content differs materially (say how); NOT_FOUND = no such work located; UNVERIFIABLE = you could not reach any source (say why).

Then totals: VERIFIED / MISMATCH / NOT_FOUND / UNVERIFIABLE, and the list of rows whose definition rests on NO verified citation.

## Rows

- AC05 — "Maintain citation-backed definitions rather than model-generated definitions." SATISFIED iff every definition row has at least one VERIFIED citation that supports it and no row's definition rests on a NOT_FOUND or materially MISMATCHED citation; NOT_SATISFIED otherwise, naming the failing rows. Do not close the row on the basis of the table's own "VERIFIED" flags — only on what you retrieved.
