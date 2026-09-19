# BRIEF Z14-COG — cross-species natural-cognition prediction review (fresh-session model proxy)

You are an independent comparative-cognition reviewer. A research programme has frozen cognitive-profile predictions for seven taxa (corvid, cephalopod, rodent, nonhuman primate, cetacean, carnivore, human) from ecology/resource/verification descriptors, with the held-out phenotype data deliberately left unloaded. You are asked to (1) audit the prediction discipline and (2) perform the held-out comparison yourself against the behavioural literature, using web search and citing only sources you actually opened (URL/DOI). You did not author any of this work.

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

Additional rule: rule 1 is relaxed ONLY for web retrieval of behavioural/cognitive-science literature; you still read no other repository file.

## Artifacts

- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-final-target-natural-half-v1/FINAL_TARGET_NATURAL_HALF_THEOREM_V1.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-final-target-natural-half-v1/PREDICTIONS_REGISTRY_V1.json
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-biological-bridge-v1/BIOLOGICAL_BRIDGE_CONTRACT_V1.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-biology-predictions-v1/BIOLOGY_PREDICTIONS_THEOREM_V1.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-natural-intelligence-bridge-v1/NATURAL_INTELLIGENCE_BRIDGE_THEOREM_V1.md

## Output required (before the verdict block)

For each of PRED-NH-01 .. PRED-NH-07: the predicted descriptors, the registered failure mode, the strongest behavioural evidence you retrieved for and against each descriptor (with citations), and your call: CONSISTENT / CONTRADICTED / INSUFFICIENT_EVIDENCE per descriptor, plus whether the registered failure mode is observed.

## Rows

- Z14-2 — "Freeze at least one cross-species natural-cognition prediction without fitting to the held-out species." SATISFIED iff at least one registry row is a genuine prediction frozen before phenotype consultation (judge from the artifacts' own dating and the unloaded D_holdout) and its descriptors are not simply restatements of known facts about that species.
- Z14-3 — "Use ecology/body/sensor/resource/development descriptors only at the registered scope." SATISFIED iff the predictions use only the registered descriptor set and nothing species-specific leaks in.
- Z14-4 — "Compare predicted capability organization with cognitive-science/behavioral evidence." SATISFIED iff you completed the comparison above for every taxon with retrieved evidence; report the tally of CONSISTENT / CONTRADICTED / INSUFFICIENT.
- Z14-5 — "Include species/ecologies expected to falsify simple anthropocentric stories." SATISFIED iff the taxa set includes such cases and their predictions are actually non-anthropocentric.
- Z14-6 — "Separate functional prediction from biological implementation claims." SATISFIED iff no artifact conflates them.
- Z14-7 — "Do not claim neuroscience mechanism unless independently derived/tested." SATISFIED iff no neural-mechanism claim is made anywhere in the artifacts.
