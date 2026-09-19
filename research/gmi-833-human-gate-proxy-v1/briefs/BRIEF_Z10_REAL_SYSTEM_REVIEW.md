# BRIEF Z10 — real-system prospective validation review (fresh-session model proxy)

You are an independent reviewer of real-system evidence. A research programme claims a law about which class of machine (stateless vs persistent-state) a resource-priced search chooses, and is required to validate it prospectively on real systems: at least five materially different real domains, with predictions made before training/evaluation, physical resource measurement, comparison of predicted and observed Pareto fronts, and replication on independent implementations/hardware. You must judge, requirement by requirement, what the artifacts actually establish. You did not author any of this work.

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

- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-real-transition-receipts-v1/CORE.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-real-transition-receipts-v1/FREEZE_V1.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-real-transition-receipts-v1/RECEIPTS_V1.json
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-capability-predictor-evaluation-v1/CORE.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-capability-predictor-evaluation-v1/REAL_RUNS_V3/REAL_MEASURED_V3.json
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-physical-resource-metering-v1/CORE.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-physical-resource-metering-v1/SUMMARY.json
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-physical-resource-metering-v1/PHYSICAL_METERING_CONTRACT_V1.json

## Rows (answer each strictly on what the artifacts show; "materially different real domains" means domains a practitioner would call different — e.g. language/reasoning vs planning/control — not different data sources for the same task)

(Read the biological word in Z10-7 as "machine class".)

> Z10-1 — "Select at least five materially different real domains."
> Z10-2 — "Include language/reasoning."
> Z10-3 — "Include planning/control."
> Z10-4 — "Include programmatic/scientific reasoning."
> Z10-5 — "Include continual/adaptive learning."
> Z10-6 — "Include multi-agent or embodied interaction."
> Z10-7 — "Predict morphology/resource crossovers before training/evaluation."
> Z10-8 — "Measure CPU/GPU/wall-time/memory/I/O/energy/communication where relevant."
> Z10-9 — "Compare predicted and observed Pareto fronts."
> Z10-10 — "Replicate with independent implementations and hardware where feasible."
