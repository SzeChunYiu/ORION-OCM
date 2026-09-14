"""FROZEN PREDICTION: morphology transitions under repricing.  Phase one, no measuring code.

Section G box 13 asks for predicted morphology transitions when resources are
repriced.  R10 already ran the same 8 carriers at THREE budget pools -- 20 000,
60 000, 200 000 -- which is a repricing of exactly the kind box 13 names.  So
the question is answerable from data on disk, and this is a prediction rather
than a new experiment.

THE STRUCTURE UNDER TEST
    For each ordered pair, read a WINNER at each pool:
        RESIDENT_HOLDS   -> the resident
        INVADER_REPLACES -> the invader
        COEXIST          -> neither
    Ordering the pools by size gives each pair a winner SEQUENCE of length 3.

    A pair OSCILLATES if that sequence is X, Y, X with X and Y both actual
    carriers and X != Y -- the outcome reverses as the budget grows and then
    reverses back.

THE PREDICTIONS
    P1  no ordered pair oscillates: zero X,Y,X sequences.
    P2  at least one ordered pair CHANGES winner across the pools.

WHY P1 IS THE INTERESTING HALF
    If no pair oscillates, repricing has a DIRECTION: a carrier that loses its
    advantage as the budget grows never gets it back, so transitions are
    one-way and box 13 becomes predictable in principle -- knowing the outcome
    at two pools constrains the third.

    If pairs DO oscillate, repricing is non-monotone: an outcome at a small and
    a large budget tells you nothing about the middle, and morphology
    transitions cannot be extrapolated from endpoints.  That is the harder
    world, and it is a real possibility because the pools interact with
    allocation, which the R10 receipt flags as a modelling choice.

WHY P2 IS NEEDED
    P1 alone is the same trap box 10 had: "no oscillation" is also what a
    repricing that changes NOTHING would report.  P2 is the control -- if no
    pair ever changes winner, the budget is not moving outcomes and P1's zero
    carries no information.  The adjudicator asserts P2 rather than reporting a
    clean-looking zero.

FALSIFIERS
    P1 fails if any pair has winner sequence X, Y, X with X != Y, both carriers.
    P2 fails if every pair has the same winner at all three pools.
"""

import json
import os

OUT = {
    "registration": "GMI_REPRICING_PREDICTION_V1",
    "phase": "prediction -- no measurement performed or available in this script",
    "source_evidence": "STAGE_R10_INVASION_V1.json: invasion_matrix_by_pool at 3 pools",
    "winner_rule": {
        "RESIDENT_HOLDS": "resident", "INVADER_REPLACES": "invader",
        "COEXIST": "neither"},
    "oscillation_definition": (
        "winner sequence across pools ordered by size is X, Y, X with X != Y "
        "and both actual carriers"),
    "P1": "no ordered pair oscillates: zero X,Y,X sequences",
    "P2": "at least one ordered pair changes winner across the pools",
    "why_P1_matters": (
        "no oscillation means repricing has a direction -- transitions are "
        "one-way and knowing two pools constrains the third; oscillation means "
        "morphology transitions cannot be extrapolated from endpoints"),
    "why_P2_needed": (
        "P1 alone is the box-10 trap: 'no oscillation' is also what a repricing "
        "that changes nothing would report, so P2 is the control"),
    "falsifiers": [
        "P1 fails if any pair has winner sequence X,Y,X with X != Y",
        "P2 fails if every pair has the same winner at all three pools",
    ],
    "caveat_carried": (
        "the R10 receipt states the allocation rule is a modelling choice and a "
        "different rule can reorder outcomes; whatever is found here is a "
        "property of this ecology under that rule"),
}

print("=" * 78)
print("FROZEN PREDICTION -- morphology transitions under repricing (box 13)")
print("=" * 78)
print("  R10 ran the same 8 carriers at pools 20000 / 60000 / 200000.")
print("  Each ordered pair therefore has a WINNER SEQUENCE of length 3.")
print()
print("  P1  no pair OSCILLATES (no X,Y,X)  -- repricing has a direction")
print("  P2  at least one pair CHANGES winner -- the control")
print()
print("  If P1 holds, transitions are one-way and knowing two pools constrains")
print("  the third.  If it fails, morphology transitions cannot be extrapolated")
print("  from endpoints, which is the harder world.")
print()
print("  P2 is needed because 'no oscillation' is also what a repricing that")
print("  changes NOTHING would report -- the same trap box 10 had.")
print()
print("  This script performs NO measurement.")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_REPRICING_PREDICTION_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print("  receipt: microscopes/results/STAGE_REPRICING_PREDICTION_V1.json")
