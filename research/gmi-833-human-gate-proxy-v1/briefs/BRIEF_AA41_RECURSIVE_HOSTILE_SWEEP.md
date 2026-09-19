# BRIEF AA41 — final recursive hostile sweep (fresh-session model proxy)

You are an independent hostile auditor performing a RECURSIVE sweep before a manuscript freeze: start from every flagship claim in the register, follow each to the assumptions and results it depends on, and at each step ask what unresolved gap, unstated assumption, or unfulfilled promise remains beneath it. Stop only when every branch terminates in an explicitly open item or in a claim you find sound. You did not author any of this work.

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

## Artifacts

- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-theory-baseline-v1/BASELINE_V1.md (the claims register: assertions A1 .. A14, section 3 CI-U, section 4 open-items register)
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-capability-interaction-partition-v1/CORE.md (a correction to CI-U)
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-z-z15-decisive-falsifiers-v1/FREEZE_V1.md (the flagship theory in four sentences and its falsifiers)
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-aa-gap-object-v1/AA_GAP_OBJECT_THEOREMS_V1.md (the gap-object and closure-grade definitions)
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-aa-gap-object-v1/OPEN_GAP_SCHEMA_V1.json
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-corpus-census-v1/GMI_GAP_GRAPH_V1.json (1140 open gap records; sample it, you need not read every record, but report how many you read)

## Output required (before the verdict block)

A sweep tree: for each of A1 .. A14 and the flagship theory, the chain of dependencies you followed and, at the leaves, either SOUND or a finding with an id SWEEP-<n>: {claim, the unresolved descendant gap, why it is material or not, whether it is already registered as open in section 4 of the baseline or in the gap graph}.

Then: the list of findings that are NOT already registered anywhere in the artifacts.

## Rows

- AA41 — "Run a final recursive hostile sweep before any flagship manuscript freeze." SATISFIED iff you completed the recursive sweep over every register entry and every material finding is either registered as open in the artifacts or listed by you; NOT_SATISFIED if you could not complete the sweep. State whether, at this pin, calling the sweep "final" is honest (i.e. whether the register is stable enough that a later sweep would be a re-run rather than a first sweep).
