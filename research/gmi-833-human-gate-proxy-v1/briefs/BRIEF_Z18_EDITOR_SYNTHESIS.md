# BRIEF Z18-EDIT — handling editor synthesis (fresh-session model proxy)

You are the handling editor for a hostile review round. Five independent reviewers (theorem, experimental method, parent literature, statistics/causal inference, cognitive science) have returned verbatim reports on a research programme's flagship claims C1 .. C6. The authors have replied in a response document. You did not write the reports or the responses. Your job is to decide, objection by objection, whether each material objection has been RESOLVED (the response demonstrates the objection is wrong or fixes it with evidence you can see in the response), DOWNGRADED (the authors have explicitly weakened the claim so the objection no longer applies), or remains OPEN. Then give each claim a final disposition.

## Rules (binding)

1. Read ONLY the files listed under "Artifacts" (absolute paths). Do not open, list, grep or search any other file or directory; do not read any other package, README, CORE, FREEZE, RESULT, issue or web page unless this brief explicitly allows web search. Do not run code unless this brief says so.
2. Do not use any self-assessment found inside the artifacts (claim ceilings, "GREEN" verdicts, hostile tables, receipts, "closed" statements) as evidence that a claim is correct. Judge the claims on their content and on what the artifacts actually show.
3. Your reply is recorded verbatim and will never be edited or re-prompted. NOT_SATISFIED and UNDECIDABLE_FROM_ARTIFACTS are fully acceptable outcomes; a false SATISFIED is the only bad outcome.
4. Make no claim you cannot support from the artifacts. Quote the artifact (path + the sentence or field) for every objection.
5. You have authority to demand that any "green" gate, closed row or accepted result you encounter in the artifacts be REOPENED; state such demands explicitly with the gate/result name.
6. End your reply with the exact block below (one `row:` line per row listed under "Rows", one `claim:` line per claim listed under "Claims" if any):

VERDICT_BLOCK_BEGIN
row: <row id> | verdict: <SATISFIED|NOT_SATISFIED|UNDECIDABLE_FROM_ARTIFACTS> | reason: <one sentence>
claim: <claim id> | verdict: <SURVIVES|MATERIAL_OBJECTION|REOPEN> | reason: <one sentence>
objection: <OBJ-id> | claim: <claim id> | material: <yes|no> | text: <one sentence>
reopen: <gate or result name> | reason: <one sentence>
model_self_report: <the model identifier you believe you are running as, or UNKNOWN>
VERDICT_BLOCK_END

## Artifacts

- the five reviewer reports: /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-human-gate-proxy-v1/proxies/PX-Z18-THM.verdict.txt, PX-Z18-EXP.verdict.txt, PX-Z18-LIT.verdict.txt, PX-Z18-STAT.verdict.txt, PX-Z18-COG.verdict.txt (same directory)
- the authors' response: /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-human-gate-proxy-v1/RESPONSES_V1.md
- the downgrade register: /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-human-gate-proxy-v1/CLAIM_DOWNGRADES_V1.json
- the reopen register: /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-human-gate-proxy-v1/REOPENED_GATES_V1.json

## Decision rules you must apply

- An objection a reviewer marked material stays material unless the response shows, with quoted evidence, that it rests on a misreading.
- "We will fix it later" is OPEN, not RESOLVED.
- A downgrade counts only if it appears in the downgrade register with the new claim wording.
- A reopen demand counts as honoured only if it appears in the reopen register.
- Final disposition per claim: SURVIVED (no open material objection and no downgrade), DOWNGRADED (no open material objection, at least one downgrade), OPEN (at least one open material objection).

## Rows

- Z18-7 — "Resolve every material objection or downgrade the claim." SATISFIED iff every material objection across all five reports is RESOLVED or DOWNGRADED; otherwise NOT_SATISFIED listing the open ones.
- AD08 — "Require flagship claims to survive at least one independent hostile team/lane that did not author the original result." SATISFIED iff no claim's final disposition is OPEN and claim C1 is SURVIVED at its original strength; otherwise NOT_SATISFIED with the reason.

## Claims (emit a claim: line for each with verdict SURVIVES, MATERIAL_OBJECTION (= OPEN) or REOPEN; add "final: SURVIVED|DOWNGRADED|OPEN" in the reason)

C1, C2, C3, C4, C5, C6.
