# BRIEF AA15 — proof-assistant targets for the flagship mathematical spine (fresh-session model proxy)

You are an independent formal-methods reviewer (Lean 4 experience). A research programme has a small "mathematical spine" of finite, exact results. You must judge, result by result, whether a proof-assistant target is PRACTICAL (statable in Lean 4 core without Mathlib, with a realistic prospect of a full proof), and for every practical one WRITE the Lean 4 statement as a target stub with the proof left as `sorry`. You did not author any of this work. You may run `lean` locally only if it is on PATH; otherwise write the stubs carefully and say they are unchecked.

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

Additional rule: you may write files, but ONLY into the directory /tmp/claude-501/revive-gates/aa15_targets/ (create it). Write nothing anywhere else.

## The spine (statements you are targeting)

- S1 — the state-class choice law at the registered finite scope: for the 65,552-candidate universe and exact objective in the artifacts, the exhaustive argmin is in the persistent-state class iff lambda < eta·p/2, stateless iff lambda > eta·p/2, tie at equality.
- S2 — the capability-interaction partition CIP-1: on the region N ∧ M, the four conditions {J = s}, {J = m ∧ m < s}, {m < J < s}, {J > s} are mutually exclusive and jointly exhaustive.
- S3 — the descent-stack acyclicity AG1-4: the 37-arrow derived-from relation on 32 nodes has no cycle and no upward arrow.
- S4 — the AJ13 stopping predicate: the six-conjunct predicate as a decidable proposition over a finite record.

## Artifacts

- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-heldout-20-transitions-v1/HELDOUT_TRANSITION_FORMALIZATION_V1.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-heldout-20-transitions-v1/full_enumeration_v1.py (the exact semantics of the universe and objective)
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-capability-interaction-partition-v1/CAPABILITY_INTERACTION_PARTITION_THEOREMS_V1.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-ag1-descent-stack-v1/AG1_THEOREMS_V1.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-ag1-descent-stack-v1/FOUNDATION_DEPENDENCY_DAG_V1.json
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-aj13-stopping-rule-v1/THEORY.md
- /Users/billy/Desktop/projects/ORION-OCM-wt-833/revive-gates/research/gmi-833-aj13-stopping-rule-v1/check_aj13.py

## Output required

1. For each of S1..S4: PRACTICAL or NOT_PRACTICAL with a one-paragraph justification (what would have to be formalized, expected difficulty, what the Python semantics leaves ambiguous).
2. For each PRACTICAL target: a file /tmp/claude-501/revive-gates/aa15_targets/<Sn>_<name>.lean containing the Lean 4 core statement (definitions + `theorem ... := by sorry`), self-contained, no imports beyond Lean core.
3. A file /tmp/claude-501/revive-gates/aa15_targets/TARGETS.json listing {id, file, statement_summary, practicality, checked_locally: true/false}.

## Rows

- AA15 — "Add proof-assistant/formal-verification targets for the flagship mathematical spine where practical." SATISFIED iff at least one spine result is PRACTICAL and you wrote its target stub; NOT_SATISFIED iff none is practical (say why).
