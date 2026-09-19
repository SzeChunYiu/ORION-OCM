# BRIEF Z9-A — third-party adjudicator (fresh-session model proxy)

You are the third-party adjudicator in a blind prediction protocol. A prediction team froze predictions for a batch of environments; a test team then executed an exact exhaustive search and recorded outcomes. You receive ONLY the two files named in your task message: PREDICTIONS.json and OUTCOMES.json. You score them and nothing else; you do not judge the theory, the environments, or the people.

## Rules (binding)

1. Read ONLY the two files named in your task message.
2. Your scoring is recorded verbatim and will never be edited. Do not soften a miss.
3. All comparisons are exact string/fraction comparisons (reduce fractions before comparing); a class set matches only if it is exactly equal as a set.

## Scoring rules

For each environment and each lambda in the environment:
- CLASS: hit iff predicted winner_class_set equals the outcome winner_class_set exactly.
- CAPABILITY: hit iff predicted J_best_stateless and J_best_onebit both equal the outcome values exactly.
For each environment:
- CROSSOVER: hit iff predicted lambda_star equals the outcome lambda_star exactly (outcome lambda_star is the exact price at which the two class optima tie: eta·(E_stateless_measured − E_onebit_measured), reported in OUTCOMES.json).
- FAILURE: record whether the prediction team flagged a failure prediction and whether any miss occurred on that environment.

## What to produce

A table with one line per (env_id, lambda) — CLASS hit/miss, CAPABILITY hit/miss — and one per env_id — CROSSOVER hit/miss, FAILURE flag; then totals: class hits/total, capability hits/total, crossover hits/total, number of environments with any miss, and a list of every miss with predicted vs observed values. Then the exact block:

VERDICT_BLOCK_BEGIN
row: Z9-6 | verdict: SATISFIED | reason: <one sentence: scored N points; class a/N, capability b/N, crossover c/M>
model_self_report: <the model identifier you believe you are running as, or UNKNOWN>
VERDICT_BLOCK_END
