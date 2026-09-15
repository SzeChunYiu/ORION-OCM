"""R: which tiny-world microscopes exist, and do they satisfy R's two rules?

Section R asks for exact tiny-world microscopes across fourteen domains, plus
two rules: every microscope fully enumerable with a certificate, and every
positive microscope paired with a minimal negative twin.

The corpus has 41 witnesses.  Rather than build new worlds, this maps what
exists onto R's fourteen domains and reports the two rules from measurements
already made -- the twin rule was quantified by the B1 audit, and the
certificate rule has a worked instance in the real-regime replication.

Mapping is by EXPLICIT assignment, not by pattern matching over names.  Three
audits in this corpus have now been wrong because a pattern found a common
unrelated word, so where the set is small enough to assign by hand, it is
assigned by hand and a reader can check each row.
"""

import json
import glob
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(ROOT, "microscopes", "results")

# R's fourteen world types -> witnesses assigned by hand.
WORLDS = {
    "architecture derivation": ["neural_architecture", "linear_family",
                                "gated_recurrence", "state_space"],
    "learning-law": ["update_law", "credit_assignment"],
    "memory differentiation": ["memory_regime", "residual_memory",
                               "exemplar_parametric", "consolidation"],
    "concept-formation": ["concept_formation"],
    "planning": ["planning_stop", "replanning", "subgoal", "simulation_worth"],
    "causal": [],
    "social / theory-of-mind": ["social_cognition", "social_strategic"],
    "teaching": ["pedagogy"],
    "culture": ["teaching_culture"],
    "multi-species ecology": [],
    "domain-collision": [],
    "capability-ceiling": ["species_algebra"],
    "development / evolvability": ["hierarchy", "hierarchy_overhead", "lesion",
                                   "interference"],
    "reachability / search-bias": ["search_frontier", "goal_formation"],
}

present = {os.path.basename(p)[:-len("_witness.py")]
           for p in glob.glob(os.path.join(HERE, "*_witness.py"))}

print("=" * 96)
print("R: TINY-WORLD MICROSCOPE COVERAGE")
print("=" * 96)
print("  witnesses present: %d" % len(present))

covered, empty, missing = [], [], []
for world, ws in WORLDS.items():
    have = [w for w in ws if w in present]
    gone = [w for w in ws if w not in present]
    missing.extend((world, w) for w in gone)
    if have:
        covered.append((world, have))
    else:
        empty.append(world)

print()
print("-" * 96)
print("WORLD TYPES")
print("-" * 96)
for world, ws in WORLDS.items():
    have = [w for w in ws if w in present]
    mark = "COVERED  " if have else "--       "
    print("  %s%-30s %s" % (mark, world, ", ".join(have) if have else ""))

print()
print("  covered   : %d of %d" % (len(covered), len(WORLDS)))
print("  no witness: %d  (%s)" % (len(empty), ", ".join(empty)))
assert not missing, (
    "a hand-assigned witness does not exist: %s -- the assignment is stale"
    % missing[:3])
assert covered and empty, (
    "coverage is total or zero; either would mean the hand assignment is not "
    "discriminating between what exists and what does not")

# --- R's two rules, from measurements already made ----------------------
pc = json.load(open(os.path.join(RESULTS, "STAGE_PROTOCOL_CONFORMANCE_V1.json")))
twin_families = pc["control_synonyms"]["families"]
twin_names = pc["control_synonyms"]["names"]
audited = pc["protocol_block"]["total"]

rr_path = os.path.join(RESULTS, "STAGE_REAL_REGIME_FINITE_STATE_V1.json")
rr = json.load(open(rr_path)) if os.path.exists(rr_path) else None

print()
print("-" * 96)
print("R's TWO RULES")
print("-" * 96)
print("  minimal negative twin: %d of %d audited families carry one"
      % (twin_families, audited))
print("    under %d different names, no shared token -- which is why the B1"
      % len(twin_names))
print("    audit could not find them by pattern and had to adjudicate by hand.")
assert 0 < twin_families < audited, (
    "the twin count is total or zero; the B1 audit measured it strictly between")

if rr:
    print()
    print("  fully enumerable with certificate: one worked instance exists.")
    print("    %d executed pair tests certify a %d-state lower bound against an"
          % (rr["certificate"]["pairs_checked"], rr["certificate"]["fooling_set_size"]))
    print("    enumeration of 10^%.0f machines -- impossible, not merely slow."
          % rr["exhaustion_avoided"]["log10_machine_count"])
    print("    The UPPER bound does not scale, which the receipt records as")
    print("    upper_bound_replicates=false.  So the rule has a demonstrated")
    print("    method for lower bounds and an open one for upper bounds.")
    assert rr["certificate"]["pairs_failed"] == 0

OUT = {
    "corpus_audit": True,
    "witnesses_present": len(present),
    "world_types": len(WORLDS),
    "world_types_covered": len(covered),
    "world_types_without_a_witness": empty,
    "assignment": {w: [x for x in ws if x in present] for w, ws in WORLDS.items()},
    "twin_rule": {"families_with_a_twin": twin_families,
                  "families_audited": audited,
                  "distinct_names": len(twin_names)},
    "certificate_rule": ({"pairs_checked": rr["certificate"]["pairs_checked"],
                          "lower_bound_replicates": True,
                          "upper_bound_replicates": rr["verdict"]["upper_bound_replicates"]}
                         if rr else None),
    "method": (
        "world types are assigned to witnesses BY HAND, not by pattern matching "
        "over names; three audits in this corpus have been wrong because a "
        "pattern found a common unrelated word"),
    "scope": (
        "presence of a witness is not evidence that the world is EXACT, fully "
        "enumerable, or twinned; those are the rules, measured separately"),
}
os.makedirs(RESULTS, exist_ok=True)
with open(os.path.join(RESULTS, "STAGE_MICROSCOPE_COVERAGE_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("=" * 96)
print("  %d of %d world types have at least one witness.  Three have none:"
      % (len(covered), len(WORLDS)))
print("  %s." % ", ".join(empty))
print()
print("  NOT established: that a present witness is exact, fully enumerable, or")
print("  twinned.  Presence is not conformance -- those are R's two rules and")
print("  they are measured separately above, at %d of %d for the twin rule."
      % (twin_families, audited))
print()
print("  receipt: microscopes/results/STAGE_MICROSCOPE_COVERAGE_V1.json")
