"""FROZEN PREDICTION: does symbiosis occur?  Phase one, no measuring code.

Section G box 10 asks for a symbiosis criterion.  GMI_SPECIES_ECOLOGY_V1.md
recorded box 10 as open because "the taxonomy has no cooperative outcome" --
R10 reports COEXIST, INVADER_REPLACES and RESIDENT_HOLDS, and COEXIST is not
symbiosis.  Coexisting means both survived.  Symbiosis means both did BETTER
together than alone.

That distinction is measurable from data already on disk, which is why this is a
prediction rather than a new experiment: R10's receipt carries
`capability_invader` and `capability_resident` for all 192 competition cells,
and `solo_baseline_by_pool` carries each carrier's capability when it develops
alone out of the same pool.

THE CRITERION, fixed here
    A pair (A, B) in a pool is SYMBIOTIC iff BOTH capabilities in competition
    strictly exceed the same carriers' solo capabilities in that pool.
    It is MUTUALLY HARMFUL iff both are strictly lower.
    Anything else is one-sided and is neither.

THE PREDICTIONS
    P1  symbiosis NEVER occurs: zero symbiotic pairs in any pool.
    P2  mutual harm DOES occur: at least one pair in at least one pool where
        both competitors end below their solo capability.

REASONING
    The two carriers develop out of ONE shared charged pool.  Charge spent by
    one is charge the other cannot spend, so the interaction is close to
    zero-sum in resources; for both to improve, competition would have to
    generate capability that neither could buy alone.  Mutual harm is the
    natural consequence of the same sharing -- each is poorer than it would have
    been alone.

    P1 is the risky half.  It could fail: competition forces earlier stopping,
    and a carrier that would have overspent alone might do better under
    pressure.  If BOTH benefit that way, symbiosis is real and box 10 has a
    positive instance instead of a negative one.

WHY BOTH PREDICTIONS ARE STATED
    P1 alone is unfalsifiable-looking: "nothing was found" is what a broken
    measurement also reports.  P2 is the control.  If mutual harm is also zero,
    the comparison is not detecting joint effects at all and neither result
    should be believed -- the adjudicator asserts that rather than reporting a
    clean-looking zero.

FALSIFIERS
    P1 fails if any pair has both capabilities strictly above solo.
    P2 fails if no pair has both strictly below solo.
"""

import json
import os

OUT = {
    "registration": "GMI_SYMBIOSIS_PREDICTION_V1",
    "phase": "prediction -- no measurement performed or available in this script",
    "source_evidence": "STAGE_R10_INVASION_V1.json: cells + solo_baseline_by_pool",
    "criterion_symbiotic": (
        "both competitors' capability in competition strictly exceeds their own "
        "solo capability in the same pool"),
    "criterion_mutually_harmful": "both strictly below their solo capability",
    "P1": "symbiosis never occurs: zero symbiotic pairs in any pool",
    "P2": "mutual harm occurs: at least one pair with both below solo",
    "reasoning": (
        "the carriers develop out of ONE shared charged pool, so charge spent by "
        "one is charge the other cannot spend; for both to improve, competition "
        "would have to generate capability neither could buy alone"),
    "risk": (
        "P1 can fail -- competition forces earlier stopping, and a carrier that "
        "would have overspent alone might do better under pressure; if both "
        "benefit that way, box 10 gains a positive instance"),
    "why_two_predictions": (
        "P1 alone looks unfalsifiable because 'nothing found' is also what a "
        "broken measurement reports; P2 is the control, and if mutual harm is "
        "also zero the comparison is not detecting joint effects at all"),
    "falsifiers": [
        "P1 fails if any pair has both capabilities strictly above solo",
        "P2 fails if no pair has both strictly below solo",
    ],
}

print("=" * 78)
print("FROZEN PREDICTION -- does symbiosis occur? (section G box 10)")
print("=" * 78)
print("  COEXIST is not symbiosis.  Coexisting means both survived.")
print("  Symbiosis means both did BETTER together than alone.")
print()
print("  P1  symbiosis NEVER occurs  -- zero symbiotic pairs in any pool")
print("  P2  mutual harm DOES occur  -- at least one pair, both below solo")
print()
print("  P2 is the control.  If mutual harm is ALSO zero, the comparison is not")
print("  detecting joint effects at all and neither result should be believed.")
print()
print("  P1 is the risky half: competition forces earlier stopping, and a carrier")
print("  that would have overspent alone might do better under pressure.")
print()
print("  This script performs NO measurement.")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_SYMBIOSIS_PREDICTION_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print("  receipt: microscopes/results/STAGE_SYMBIOSIS_PREDICTION_V1.json")
