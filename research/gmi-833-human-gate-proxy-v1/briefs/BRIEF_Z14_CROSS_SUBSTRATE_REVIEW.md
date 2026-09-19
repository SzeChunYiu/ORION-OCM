# BRIEF Z14-SUB — cross-substrate law review (fresh-session model proxy)

You are an independent reviewer. A research programme claims a law — a resource-priced search chooses a persistent-state machine iff the price per state bit is below a closed-form threshold — and is required to test whether THE SAME law predicts across MULTIPLE COMPUTATIONAL SUBSTRATES. You must decide whether the artifacts contain such a test. A "substrate" here means a materially different computational medium or model class in which the search and the machines are realized (for example: exhaustively enumerated finite transducers; trained neural networks on a CPU; a register-machine program space), not merely different parameter values within one medium. You did not author any of this work.

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

- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-heldout-20-transitions-v1/HELDOUT_TRANSITION_FORMALIZATION_V1.md (substrate A: exhaustively enumerated one-bit transducers)
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-real-transition-receipts-v1/CORE.md (substrate B: trained torch systems)
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-real-transition-receipts-v1/FREEZE_V2_AMENDMENT.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-real-transition-receipts-v1/RECEIPTS_V1.json
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-capability-predictor-evaluation-v1/CORE.md (substrate C?: the registered machine universe of the capability predictor; decide from the text whether it is a distinct substrate)
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-capability-predictor-evaluation-v1/SCOPE_V1.md

## Questions

Is it the SAME law (same closed form, same predicted quantity) that is tested in each substrate, or a re-parameterized variant (note any change of formula between substrates and whether it was registered before or after outcomes)? How many genuinely distinct substrates carry a prospective test? Does the evidence show the law predicting, or fitting?

## Rows

- Z14-1 — "Test whether the same GMI law predicts across multiple computational substrates." SATISFIED iff the artifacts show the same law prospectively tested in at least two materially distinct substrates; NOT_SATISFIED otherwise with the reason.
