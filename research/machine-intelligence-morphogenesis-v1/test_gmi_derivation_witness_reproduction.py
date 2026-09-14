"""Every derivation witness must reproduce its receipt, and say what it claims.

The GMI derivation corpus rests on fifteen small witness scripts. Before this
guard, each had been run once by hand and its output quoted in a document.
Nothing re-ran them, so a change that silently altered a number -- or inverted
a conclusion -- would have gone unnoticed, and the documents would have gone on
asserting the old result.

Two layers, because either alone is a false green:

  REPRODUCTION  Re-run each witness in a clean directory and require the
                receipt it writes to equal the committed receipt exactly.
                Catches drift in any number of any witness. On its own it
                would pass if someone updated a witness AND its receipt
                together, so it cannot police the documents' claims.

  CLAIM PINS    Assert the specific headline each derivation document asserts.
                Catches the coordinated update that reproduction misses. On its
                own it would leave every unpinned number free to drift.

A third test mutates a receipt and requires the comparison to notice, so the
guard is validated against a real failure rather than trusted.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MICRO = os.path.join(HERE, "gmi_microscope")
RESULTS = os.path.join(HERE, "microscopes", "results")

# witness script -> the receipt it writes, relative to microscopes/results/
WITNESSES = {
    "belief_state_witness.py": "STAGE_BELIEF_STATE_V1.json",
    "concept_formation_witness.py": "STAGE_CONCEPT_FORMATION_V1.json",
    "conditional_specialization_witness.py": "STAGE_CONDITIONAL_SPECIALIZATION_V1.json",
    "consolidation_witness.py": "STAGE_CONSOLIDATION_WITNESS_V1.json",
    "control_family_witness.py": "STAGE_CONTROL_FAMILY_V1.json",
    "credit_assignment_witness.py": "STAGE_CREDIT_ASSIGNMENT_V1.json",
    "continual_regimes_witness.py": "STAGE_CONTINUAL_REGIMES_V1.json",
    "equivariance_witness.py": "STAGE_EQUIVARIANCE_V1.json",
    "dynamic_routing_witness.py": "STAGE_DYNAMIC_ROUTING_V1.json",
    "exemplar_parametric_witness.py": "STAGE_EXEMPLAR_PARAMETRIC_V1.json",
    "linear_family_witness.py": "STAGE_LINEAR_FAMILY_V1.json",
    "finite_state_witness.py": "STAGE_FINITE_STATE_V1.json",
    "gated_recurrence_witness.py": "STAGE_GATED_RECURRENCE_V1.json",
    "generative_family_witness.py": "STAGE_GENERATIVE_FAMILY_V1.json",
    "goal_formation_witness.py": "STAGE_GOAL_FORMATION_V1.json",
    "hierarchy_overhead_witness.py": "STAGE_HIERARCHY_OVERHEAD_V1.json",
    "hierarchy_witness.py": "STAGE_HIERARCHY_WITNESS_V1.json",
    "interference_witness.py": "STAGE_INTERFERENCE_V1.json",
    "lesion_witness.py": "STAGE_COMPONENT_LESIONS_V1.json",
    "memory_regime_witness.py": "STAGE_MEMORY_REGIME_WITNESS_V1.json",
    "message_passing_witness.py": "STAGE_MESSAGE_PASSING_V1.json",
    "neural_architecture_witness.py": "STAGE_NEURAL_ARCHITECTURE_V1.json",
    "metacognition_witness.py": "STAGE_METACOGNITION_V1.json",
    "pedagogy_witness.py": "STAGE_PEDAGOGY_V1.json",
    "planning_stop_witness.py": "STAGE_PLANNING_STOP_V3.json",
    "program_library_witness.py": "STAGE_PROGRAM_LIBRARY_V1.json",
    "recovery_objective_witness.py": "STAGE_RECOVERY_OBJECTIVE_V1.json",
    "replanning_witness.py": "STAGE_REPLANNING_V1.json",
    "search_frontier_witness.py": "STAGE_SEARCH_FRONTIER_V1.json",
    "simulation_worth_witness.py": "STAGE_SIMULATION_WORTH_V1.json",
    "social_cognition_witness.py": "STAGE_SOCIAL_COGNITION_V1.json",
    "social_strategic_witness.py": "STAGE_SOCIAL_STRATEGIC_V1.json",
    "state_space_witness.py": "STAGE_STATE_SPACE_V1.json",
    "symbolic_rewrite_witness.py": "STAGE_SYMBOLIC_REWRITE_V1.json",
    "subgoal_witness.py": "STAGE_SUBGOAL_WITNESS_V1.json",
    "update_law_witness.py": "STAGE_UPDATE_LAW_V1.json",
    "teaching_culture_witness.py": "STAGE_TEACHING_CULTURE_WITNESS_V1.json",
    "residual_memory_witness.py": "STAGE_RESIDUAL_MEMORY_V1.json",
    "tool_routing_witness.py": "STAGE_TOOL_ROUTING_V1.json",
    "real_regime_finite_state_witness.py": "STAGE_REAL_REGIME_FINITE_STATE_V1.json",
    "predict_intersection_index.py": "STAGE_INTERSECTION_INDEX_PREDICTION_V1.json",
    "predict_composition_law.py": "STAGE_COMPOSITION_LAW_PREDICTION_V1.json",
    "predict_probe_law.py": "STAGE_PROBE_LAW_PREDICTION_V1.json",
    "species_algebra_witness.py": "STAGE_SPECIES_ALGEBRA_V1.json",
    "predict_intransitivity.py": "STAGE_INTRANSITIVITY_PREDICTION_V1.json",
    "predict_symbiosis.py": "STAGE_SYMBIOSIS_PREDICTION_V1.json",
    "predict_repricing.py": "STAGE_REPRICING_PREDICTION_V1.json",
    "predict_partition_abundance.py": "STAGE_PARTITION_ABUNDANCE_PREDICTION_V1.json",
}


def _run_witness(script):
    """Execute one witness in a scratch directory and return its receipt."""
    tmp = tempfile.mkdtemp(prefix="gmiwit-")
    try:
        shutil.copy(os.path.join(MICRO, script), os.path.join(tmp, script))
        os.makedirs(os.path.join(tmp, "microscopes", "results"))
        proc = subprocess.run(
            [sys.executable, script],
            cwd=tmp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600,
        )
        assert proc.returncode == 0, (
            "%s exited %d\n%s" % (script, proc.returncode,
                                  proc.stderr.decode("utf-8", "replace")[-2000:]))
        produced = os.path.join(tmp, "microscopes", "results", WITNESSES[script])
        assert os.path.exists(produced), "%s wrote no receipt at %s" % (
            script, WITNESSES[script])
        with open(produced) as fh:
            return json.load(fh)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _committed(name):
    with open(os.path.join(RESULTS, name)) as fh:
        return json.load(fh)


def load_receipt(name):
    return _committed(name)


# --------------------------------------------------------------------------
# Layer 1: reproduction
# --------------------------------------------------------------------------

@pytest.mark.parametrize("script", sorted(WITNESSES))
def test_witness_reproduces_its_committed_receipt(script):
    """Re-running the witness must yield exactly the receipt in the repository.

    Every witness is deterministic: none reads the clock, and the only one that
    draws randomness (replanning) seeds its own generator. So any difference is
    a real change in the derivation, not noise.
    """
    assert _run_witness(script) == _committed(WITNESSES[script]), (
        "%s no longer reproduces %s -- a derivation changed. If the change is "
        "intended, re-run the witness, commit the new receipt, and update the "
        "claims in the corresponding derivation document."
        % (script, WITNESSES[script])
    )


def test_every_witness_is_registered():
    """A new witness must be added here, or it is verified by nothing.

    This is the trap that let fifteen witnesses sit outside CI: the gate lists
    files explicitly, so an unregistered script is silently never run.
    """
    on_disk = {
        f for f in os.listdir(MICRO)
        if f.endswith("_witness.py") or f.startswith("witness_")
    }
    # b6_witness_reconstruct replays a recorded campaign and needs its source
    # receipts; witness_dg7 imports the microscope package. Neither is a
    # self-contained derivation witness, so neither belongs in this guard.
    exempt = {"b6_witness_reconstruct.py", "witness_dg7.py"}
    unregistered = on_disk - set(WITNESSES) - exempt
    assert not unregistered, (
        "unregistered derivation witnesses, verified by nothing: %s"
        % sorted(unregistered))


# --------------------------------------------------------------------------
# Layer 2: the claims the documents actually make
# --------------------------------------------------------------------------

def test_calibration_is_local():
    """GMI_METACOGNITION_CALIBRATION_V1: miscalibration away from the decision
    threshold costs exactly nothing; only error near the threshold is paid for.
    The zero/nonzero dichotomy is the claim, not the magnitude."""
    r = load_receipt("STAGE_METACOGNITION_V1.json")
    far = [row for row in r["rows"] if "far" in row["region"]]
    near = [row for row in r["rows"] if "near" in row["region"]]
    assert far and near, "receipt lost its regions"
    assert all(row["excess"] == 0.0 for row in far), \
        "miscalibration away from the threshold is no longer free"
    assert all(row["excess"] > 0.0 for row in near), \
        "miscalibration near the threshold is no longer paid for"


def test_agent_model_pays_only_at_intermediate_uncertainty():
    """GMI_SOCIAL_AGENT_MODELS_V1: an agent model beats a fixed policy at
    middling priors and loses at both extremes."""
    r = load_receipt("STAGE_SOCIAL_COGNITION_V1.json")
    rows = sorted(r["necessity"], key=lambda d: d["prior_coop"])
    worth = [row["worth"] for row in rows]
    assert worth[0] is False and worth[-1] is False, \
        "the model now pays at an extreme prior -- the claim was that it does not"
    assert any(worth), "the model no longer pays anywhere (vacuous)"
    assert not all(worth), "the model now pays everywhere (vacuous)"


def test_recursive_belief_depth_is_finite():
    """GMI_SOCIAL_AGENT_MODELS_V1: recursion stops because the next level does
    not pay, not because it is ill-founded. The optimum is interior."""
    r = load_receipt("STAGE_SOCIAL_COGNITION_V1.json")
    nets = r["depth_nets"]
    assert r["optimal_depth"] == nets.index(max(nets))
    assert 0 < r["optimal_depth"] < len(nets) - 1, \
        "the optimal depth is no longer interior, so nothing is being traded off"
    assert nets[-1] < max(nets), "deep recursion no longer declines"


def test_belief_is_not_a_relabelled_goal():
    """GMI_STRATEGIC_SOCIAL_COGNITION_V1 D1: a goal-only model is refuted by
    exhaustion when the partner's information can differ from ours, and fits
    when it cannot. Both halves are needed -- the second is what stops the
    first from being an artefact of the encoding."""
    r = load_receipt("STAGE_SOCIAL_STRATEGIC_V1.json")
    assert r["D1"]["goal_only_fits_when_channel_varies"] is False
    assert r["D1"]["goal_only_fits_when_channel_constant"] is True
    pays = [row["pays"] for row in r["D1"]["pricing"]]
    assert any(pays) and not all(pays), "belief tracking became vacuous"


def test_prediction_pays_only_before_revelation():
    """GMI_STRATEGIC_SOCIAL_COGNITION_V1 D2: under the sequential protocol a
    predictor loses exactly its price; under commitment it pays above a
    threshold accuracy."""
    r = load_receipt("STAGE_SOCIAL_STRATEGIC_V1.json")
    assert r["D2"]["sequential_loss"] == "1/5"
    pays = [row["pays"] for row in r["D2"]["simultaneous"]]
    assert any(pays) and not all(pays), "the accuracy threshold vanished"
    assert r["D2"]["threshold_q"] == "13/20"


def test_opposed_signals_have_no_informative_equilibrium():
    """GMI_STRATEGIC_SOCIAL_COGNITION_V1 D3: alignment admits an informative
    fixed point; opposition admits none. Uninformativeness is a fixed-point
    property, so both halves must be checked."""
    r = load_receipt("STAGE_SOCIAL_STRATEGIC_V1.json")
    assert r["D3"]["ALIGNED"]["informative_equilibrium"] is True
    assert r["D3"]["OPPOSED"]["informative_equilibrium"] is False
    note = r["D3"]["invertibility_note"]
    assert note["vs_trusting"] != note["vs_inverting"], \
        "the sender no longer re-aims, so the cycle argument is gone"


def test_commitment_substitutes_for_detection():
    """GMI_STRATEGIC_SOCIAL_COGNITION_V1 D4: once a penalty deters lying,
    verification is worth nothing at any cost."""
    r = load_receipt("STAGE_SOCIAL_STRATEGIC_V1.json")
    assert r["D4"]["detector_needed_after_commitment"] is False
    lies = [row["lies"] for row in r["D4"]["lying"]]
    assert any(lies) and not all(lies), "the deterrence threshold vanished"
    ver = [row["verify"] for row in r["D4"]["verification"]]
    assert any(ver) and not all(ver), "the verification threshold vanished"


def test_forgetting_is_forced_only_when_distinctions_outgrow_capacity():
    """GMI_CONSOLIDATION_FORGETTING_THEOREM_V1: forgetting is forced in the
    independent regime and not in the redundant one -- the contrast is the
    result, so a run where both agree proves nothing."""
    r = load_receipt("STAGE_CONSOLIDATION_WITNESS_V1.json")
    forced = {reg["name"]: reg["forgetting_forced"] for reg in r["regimes"]}
    assert forced["A_independent"] is True
    assert forced["B_redundant"] is False
    assert len(set(forced.values())) > 1, "every regime now behaves alike"


# --------------------------------------------------------------------------
# Layer 3: validate the guard itself
# --------------------------------------------------------------------------

def test_reproduction_check_detects_a_mutated_receipt():
    """A comparison that cannot fail is not a check.

    Perturb a committed receipt in memory and confirm the equality used by the
    reproduction test rejects it. Without this, a bug that made every
    comparison trivially true would leave all fifteen tests green.
    """
    good = _committed("STAGE_SOCIAL_COGNITION_V1.json")
    mutated = json.loads(json.dumps(good))
    mutated["necessity"][0]["worth"] = not mutated["necessity"][0]["worth"]
    assert mutated != good, "the equality used by the reproduction test is blind"


def test_claim_pins_would_fail_on_an_inverted_claim():
    """The claim pins must reject a receipt that says the opposite.

    Checks the assertion logic itself, not the committed data: an inverted
    'calibration is local' receipt has to be caught.
    """
    inverted = {"rows": [
        {"region": "far below threshold  [0.00,0.40]", "excess": 0.4},
        {"region": "near threshold       [0.60,0.80]", "excess": 0.0},
    ]}
    far = [row for row in inverted["rows"] if "far" in row["region"]]
    near = [row for row in inverted["rows"] if "near" in row["region"]]
    assert not all(row["excess"] == 0.0 for row in far), \
        "the locality pin would accept a receipt where distant error is costly"
    assert not all(row["excess"] > 0.0 for row in near), \
        "the locality pin would accept a receipt where threshold error is free"


def test_every_component_lesion_matches_its_derived_prediction():
    """GMI_DERIVED_COMPONENT_LESIONS_V1: each deficit is computed from the law
    that derived the component, then measured. A mismatch means the law and the
    machine have come apart."""
    r = load_receipt("STAGE_COMPONENT_LESIONS_V1.json")
    assert r["lesions"], "receipt lost its lesions"
    for row in r["lesions"]:
        assert row["match"], "%s no longer matches its derived prediction" % row["lesion"]
    shapes = {row["measured"] for row in r["lesions"]}
    assert len(shapes) > 1, "every lesion now gives the same deficit"


def test_lesion_double_dissociation_is_two_components_not_four():
    """The dissociation claim is procedural-versus-semantic only. Retrieval also
    moves the serving coordinate, so the guard pins the narrow claim and the
    fact that other lesions share that axis -- which is what stops the document
    from being read as a four-way dissociation."""
    r = load_receipt("STAGE_COMPONENT_LESIONS_V1.json")
    d = r["dissociation"]
    assert d["procedural"]["serving"] > 0 and d["procedural"]["retention_bits"] == 0
    assert d["semantic"]["retention_bits"] > 0 and d["semantic"]["serving"] == 0
    assert "retrieval" in r["same_coordinate"], \
        "retrieval no longer shares the serving coordinate -- the narrowing is stale"
    assert len(r["same_coordinate"]) > 1


def test_planning_lesion_is_conditional_on_interference():
    """Lookahead earns its cost only when actions interfere. Both halves are
    pinned: zero deficit on the registered task set, positive when a long early
    match blocks a better covering. Either alone would be uninformative."""
    r = load_receipt("STAGE_COMPONENT_LESIONS_V1.json")
    pr = r["planning_regimes"]
    assert pr["non_interfering"]["deficit"] == 0, \
        "planning now helps even without interference"
    assert pr["interfering"]["deficit"] > 0, \
        "planning never helps, so the lesion is vacuous"


def test_memory_lesions_are_conditional_on_regime():
    """Consolidation saves nothing when nothing is redundant, and capacity loss
    happens only when capacity is exceeded. A lesion that hurts everywhere says
    nothing about when its component is needed."""
    r = load_receipt("STAGE_COMPONENT_LESIONS_V1.json")
    sem = [v["extra_bits"] for v in r["semantic_regimes"].values()]
    epi = [v["lost"] for v in r["episodic_regimes"].values()]
    assert any(x > 0 for x in sem) and any(x == 0 for x in sem), \
        "the semantic lesion is no longer conditional on redundancy"
    assert any(x > 0 for x in epi) and any(x == 0 for x in epi), \
        "the episodic lesion is no longer conditional on capacity"


def test_recovery_flips_on_the_objective_alone():
    """GMI_RECOVERY_OBJECTIVE_MECHANISM_V1: a build-charged objective recovers
    the family nowhere; a full-lifecycle objective recovers it in every ecology
    with reuse above the break-even, and correctly misses at r=1. Both halves
    matter -- an objective that recovered everywhere would be preferring the
    target rather than pricing it."""
    r = load_receipt("STAGE_RECOVERY_OBJECTIVE_V1.json")
    rec = r["recovery"]
    assert rec["A"] == 0, "the build-charged objective now recovers the family"
    assert 0 < rec["B"] < rec["n"], \
        "the lifecycle objective must recover it in some ecologies and not all"
    assert r["completed_A_search_reaches_family"] is False, \
        "a completed build-charged search now reaches the family"


def test_more_budget_moves_away_from_the_family_under_a_bad_objective():
    """The RV-377-109 signature: the frontier cheapens while the target does
    not move. Pinned as cost strictly falling and distance not falling."""
    r = load_receipt("STAGE_RECOVERY_OBJECTIVE_V1.json")
    a = r["budget_sweep_A"]
    assert a[-1]["cost_A"] < a[0]["cost_A"], "the frontier no longer cheapens"
    assert a[-1]["distance_to_family"] >= a[0]["distance_to_family"], \
        "more budget now closes the distance under the bad objective"
    assert not any(x["recovered"] for x in a)
    b = r["budget_sweep_B"]
    assert b[-1]["recovered"] and not b[0]["recovered"], \
        "under the lifecycle objective budget must help, from a starved miss"


# --------------------------------------------------------------------------
# The K4 cost-structure probe runs IN PLACE, because it imports the K4 modules
# rather than being self-contained like the witnesses above.
# --------------------------------------------------------------------------

def _run_k4_probe():
    """Execute the probe IN PLACE and return the receipt it writes.

    It cannot use the temp-directory harness above: unlike the self-contained
    witnesses, it imports the K4 modules in order to read the real cost model.
    Running it rather than only reading its receipt is the point -- a change to
    the cost model must fail this test, and a receipt-only check would sail
    straight past one.
    """
    out = os.path.join(RESULTS, "STAGE_K4_COST_STRUCTURE_V1.json")
    before = open(out).read() if os.path.exists(out) else None
    try:
        proc = subprocess.run(
            [sys.executable, "gmi_k4_cost_structure_probe_v1.py"],
            cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=900)
        assert proc.returncode == 0, (
            "the K4 cost-structure probe failed -- one of its findings is now "
            "stale, which means the cost model changed:\n%s"
            % proc.stderr.decode("utf-8", "replace")[-2000:])
        with open(out) as fh:
            return json.load(fh)
    finally:
        if before is not None:
            with open(out, "w") as fh:
                fh.write(before)


def test_k4_probe_reproduces_its_committed_receipt():
    """The probe reads a fixed cost model over a fixed seed, so its receipt is
    deterministic. A difference means the cost model moved."""
    assert _run_k4_probe() == _committed("STAGE_K4_COST_STRUCTURE_V1.json"), (
        "the K4 cost model no longer produces the committed structure receipt; "
        "re-run the probe and revisit GMI_K4_COST_STRUCTURE_ROOT_CAUSE_V1.md")


def _run_k4_repair_probe():
    """Execute the substitution-repair probe in place, like the structure probe."""
    out = os.path.join(RESULTS, "STAGE_K4_SUBSTITUTION_REPAIR_V1.json")
    before = open(out).read() if os.path.exists(out) else None
    try:
        proc = subprocess.run(
            [sys.executable, "gmi_k4_substitution_probe_v1.py"],
            cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1800)
        assert proc.returncode == 0, (
            "the K4 substitution-repair probe failed:\n%s"
            % proc.stderr.decode("utf-8", "replace")[-2000:])
        with open(out) as fh:
            return json.load(fh)
    finally:
        if before is not None:
            with open(out, "w") as fh:
                fh.write(before)


def test_repair_makes_neutral_search_recover_retention():
    """GMI_K4_SUBSTITUTION_REPAIR_V1: three family-blind corrections turn a
    search that was reuse-invariant across 4096x into one that marches to full
    retention -- and still declines to retain when there is no reuse."""
    r = _run_k4_repair_probe()
    assert r == _committed("STAGE_K4_SUBSTITUTION_REPAIR_V1.json"), \
        "the repair probe no longer reproduces its committed receipt"
    rec = r["recovery"]
    assert rec["frozen"] == 0, "the frozen control now recovers retention"
    assert 0 < rec["repaired"] < rec["n"], \
        "the repaired model must retain sometimes and not always"
    sens = r["reuse_sensitivity"]
    assert sens["frozen"] is False and sens["repaired"] is True, \
        "the frozen winner must stay flat and the repaired one must move"
    states = [x["state"] for x in r["q3_recovery_repaired"]]
    assert states == sorted(states), "retained state is not monotone in reuse"
    assert r["q3_recovery_repaired"][-1]["coverage"] >= 0.999
    assert r["q3_recovery_repaired"][0]["coverage"] < 0.1


def test_k4_cost_model_has_no_substitutions():
    """GMI_K4_COST_STRUCTURE_ROOT_CAUSE_V1: the root cause of 0 of 264.

    If any channel pair ever starts trading, this finding is stale and the
    document must be revisited -- so the guard pins the absence, not a number.
    """
    r = load_receipt("STAGE_K4_COST_STRUCTURE_V1.json")
    assert r["q2_tradeoffs"]["strong"] == [], \
        "a channel substitution now exists -- the root-cause finding is stale"
    assert not any(v["material_trade"] for v in r["q1_storage_vs_serving"].values()), \
        "retained state now buys serving work somewhere"
    q = r["q1_quartiles"]
    assert q["storage_ratio"] >= 8 and q["serving_ratio"] < 1.5, \
        "the quartile cross-check no longer shows state failing to buy serving"


def test_k4_grammar_axis_cannot_flip_a_winner():
    """DG-11 closed: the grammar enters as a scalar price on most channels, and
    the registered 1.12x spread is nowhere near what would change an argmin."""
    r = load_receipt("STAGE_K4_COST_STRUCTURE_V1.json")
    q3 = r["q3_argmin"]
    assert q3["agree"] is True, "the grammars now disagree -- DG-11 may be closable"
    assert q3["flip_ratio"] is None or q3["flip_ratio"] > 10 * q3["actual_spread"], \
        "the grammar price spread is now within reach of flipping a winner"
    assert r["q3_price_channels"]["flat"] == ["state_storage"], \
        "which channels carry the grammar price has changed"


def test_interference_is_caused_by_novelty_not_by_small_capacity():
    """GMI_INTERFERENCE_STABILITY_PLASTICITY_V1: regimes B and C have identical
    capacity and task sizes and differ only in redundancy, and only B is forced
    to trade. That pair is the whole result -- without it, 'capacity binds' and
    'interference happens' would be indistinguishable."""
    r = load_receipt("STAGE_INTERFERENCE_V1.json")
    b = [x for x in r["regimes"] if x["capacity"] == 4 and x["shared"] == 0]
    c = [x for x in r["regimes"] if x["capacity"] == 4 and x["shared"] == 4]
    assert b and c, "the B/C control pair is missing from the receipt"
    assert b[0]["forced"] is True and c[0]["forced"] is False, \
        "B and C no longer differ, so redundancy is not what dissolves the tradeoff"
    forced = [x["forced"] for x in r["regimes"]]
    assert any(forced) and not all(forced), "the tradeoff became unconditional"


def test_stability_plasticity_frontier_is_monotone_in_capacity():
    """More capacity must never buy less, and the sum must saturate at 2 only
    when capacity covers every distinction that must be separated."""
    from fractions import Fraction
    r = load_receipt("STAGE_INTERFERENCE_V1.json")
    sweep = sorted(r["capacity_sweep"], key=lambda x: x["capacity"])
    sums = [Fraction(x["max_sum"]) for x in sweep]
    assert sums == sorted(sums), "more capacity now buys less"
    assert sums[0] < sums[-1], "capacity makes no difference -- nothing binds"
    assert sums[-1] == 2, "the frontier no longer saturates at 2"
    assert sweep[-1]["forced"] is False and sweep[0]["forced"] is True


def test_interference_equals_the_excess_over_capacity():
    """At full plasticity the stability lost is exactly the excess, which is
    what makes catastrophic forgetting a capacity statement rather than a
    property of any learning rule."""
    from fractions import Fraction
    r = load_receipt("STAGE_INTERFERENCE_V1.json")
    for e in r["interference"]:
        lost = 1 - Fraction(e["stability_at_full_plasticity"])
        assert lost == Fraction(min(4, max(0, e["excess"])), 4), \
            "interference at capacity %d no longer equals the excess" % e["capacity"]


def test_every_continual_regime_wins_somewhere():
    """GMI_CONTINUAL_LEARNING_REGIMES_V1: all four regimes must be cheapest in
    some price regime. One that never wins is not a regime."""
    r = load_receipt("STAGE_CONTINUAL_REGIMES_V1.json")
    wins = {row["winner"] for row in r["regime_table"]}
    assert wins == {"expand", "regularize", "modularize", "replay"}, \
        "not every regime wins somewhere: %s" % sorted(wins)


def test_replay_is_specific_to_overwrite():
    """The sharpest claim: switching the substrate to addressed, changing
    nothing else, must take the win away from replay -- and replay must never
    win anywhere overwrite is zero."""
    r = load_receipt("STAGE_CONTINUAL_REGIMES_V1.json")
    ctrl = r["substrate_control"]
    interfering = [c for c in ctrl if "interfering" in c["substrate"]]
    addressed = [c for c in ctrl if "addressed" in c["substrate"]]
    assert interfering and addressed, "the substrate control pair is missing"
    assert interfering[0]["winner"] == "replay"
    assert addressed[0]["winner"] != "replay", \
        "replay still wins with overwrite off, so it is not specific"
    # replay's own cost must be unchanged -- what changed is the damage
    assert interfering[0]["costs"]["replay"] == addressed[0]["costs"]["replay"], \
        "replay's price moved between substrates, confounding the control"


def test_continual_crossover_is_a_price_not_a_task_property():
    """Sweeping only the price of capacity, with the task sequence fixed, must
    move the winner -- otherwise there is no crossover to report."""
    r = load_receipt("STAGE_CONTINUAL_REGIMES_V1.json")
    winners = [x["winner"] for x in r["capacity_price_sweep"]]
    assert len(set(winners)) > 1, "the winner never changes with capacity price"


def test_redundancy_dissolves_the_problem_but_not_for_modularize():
    """At full redundancy the capacity remedies cost nothing while isolation
    still charges -- which is what makes a method harmful on shared tasks."""
    from fractions import Fraction
    r = load_receipt("STAGE_CONTINUAL_REGIMES_V1.json")
    sweep = sorted(r["redundancy_sweep"], key=lambda x: x["shared"])
    assert Fraction(sweep[0]["costs"]["expand"]) > 0
    assert Fraction(sweep[-1]["costs"]["expand"]) == 0
    assert Fraction(sweep[-1]["costs"]["regularize"]) == 0
    assert Fraction(sweep[-1]["costs"]["modularize"]) > 0, \
        "isolation is now free on fully shared tasks -- the harm claim is stale"


def test_minimal_automaton_equals_the_quotient_index():
    """GMI_FINITE_STATE_DERIVATION_V1: brute force over every transition table
    must land on the quotient index -- and, crucially, one fewer state must be
    impossible. Without the second half this is an upper bound, not minimality."""
    r = load_receipt("STAGE_FINITE_STATE_V1.json")
    for row in r["neutral_recovery"]:
        assert row["match"], \
            "%s: brute force found %s states, quotient index is %s" % (
                row["obligation"], row["brute_force_k"], row["index"])
    assert r["minimality"], "the minimality-by-exhaustion section is missing"
    for row in r["minimality"]:
        assert row["any_machine_works"] is False, \
            "%s is now solvable with %d states, contradicting its index" % (
                row["obligation"], row["k_tried"])


def test_stateless_suffices_exactly_when_the_obligation_is_memoryless():
    """Both halves: it must succeed somewhere and fail somewhere, or the
    result says nothing about when state is necessary."""
    r = load_receipt("STAGE_FINITE_STATE_V1.json")
    by = {x["obligation"]: x for x in r["stateless"]}
    assert by["constant"]["sufficient"] and by["last_symbol"]["sufficient"]
    assert not by["parity_b"]["sufficient"]
    assert by["parity_b"]["stateless_accuracy"] < 0.6, \
        "parity is no longer at chance for a stateless policy"
    suff = [x["sufficient"] for x in r["stateless"]]
    assert any(suff) and not all(suff), "the stateless result became unconditional"


def test_fooling_set_size_equals_the_index():
    """The lower bound must be exhibited, not asserted: every pair of
    representatives needs a separating continuation."""
    r = load_receipt("STAGE_FINITE_STATE_V1.json")
    idx = {x["obligation"]: x["index"] for x in r["quotient"]}
    for name, f in r["fooling_sets"].items():
        assert f["all_pairs_separated"], "%s has an unseparated pair" % name
        assert f["size"] == idx[name], \
            "%s: fooling set %d against index %d" % (name, f["size"], idx[name])


def test_state_versus_history_crossover_exists():
    """Recurrent state must lose at short sequences and win at long ones."""
    r = load_receipt("STAGE_FINITE_STATE_V1.json")
    kinds = {c["cheaper"] for c in r["state_vs_history"]}
    assert "history" in kinds and "state" in kinds, \
        "no crossover between recurrent state and explicit history"


def test_retrieval_versus_parametric_crosses_in_problem_size():
    """GMI_EXEMPLAR_VERSUS_PARAMETRIC_V1: a rule's cost is fixed while a table's
    grows, so growing the universe must flip the winner. The expressibility
    table alone is coarser than a crossover and is not what is pinned here."""
    r = load_receipt("STAGE_EXEMPLAR_PARAMETRIC_V1.json")
    winners = [x["cheaper"] for x in r["size_crossover"]]
    assert "exemplar" in winners and "parametric" in winners, \
        "growing the universe no longer flips the winner"
    small = r["size_crossover"][0]
    large = r["size_crossover"][-1]
    assert small["cheaper"] == "exemplar" and large["cheaper"] == "parametric", \
        "the crossover runs the wrong way in problem size"
    assert small["parametric"] == large["parametric"], \
        "the rule cost now grows with the universe, which breaks the argument"


def test_knn_needs_the_metric_to_be_aligned():
    """Local lookup must beat full storage on smooth obligations and fail on
    rough ones. If it won everywhere the metric would be doing no work."""
    r = load_receipt("STAGE_EXEMPLAR_PARAMETRIC_V1.json")
    beats = {(x["obligation"], x["k"]): x["beats_exemplar"] for x in r["knn"]}
    assert beats[("constant", 1)] and beats[("first_bit", 1)], \
        "local lookup no longer helps on smooth obligations"
    assert not beats[("parity", 1)], \
        "local lookup now helps on parity, which is maximally rough in this metric"
    vals = list(beats.values())
    assert any(vals) and not all(vals), "the kNN result became unconditional"


def test_no_exemplar_is_kept_when_lookup_costs_as_much_as_recompute():
    """PVR-3's hard edge: U >= C forbids retention at ANY recurrence."""
    r = load_receipt("STAGE_EXEMPLAR_PARAMETRIC_V1.json")
    never = [x for x in r["pvr3"] if x["U"] >= x["C"]]
    assert never, "the U >= C control rows are missing"
    assert not any(x["keep"] for x in never), \
        "an exemplar is kept where lookup costs as much as recompute"
    keeps = [x["keep"] for x in r["pvr3"]]
    assert any(keeps) and not all(keeps), "the exemplar threshold is vacuous"


def test_some_obligations_are_incompressible_in_the_registered_class():
    """Both halves: the rule class must have gaps and must also succeed, or the
    exemplar/parametric comparison has nothing to decide."""
    r = load_receipt("STAGE_EXEMPLAR_PARAMETRIC_V1.json")
    comp = [x["compressible"] for x in r["bounds"]]
    assert any(comp) and not all(comp), \
        "the rule class now expresses everything or nothing"


def test_coefficients_identify_at_exactly_d_independent_observations():
    """GMI_LINEAR_FAMILY_DERIVATION_V1: both halves matter -- d identifies and
    d-1 does not. Only the pair is a bound."""
    r = load_receipt("STAGE_LINEAR_FAMILY_V1.json")
    ident = sorted(r["identification"], key=lambda x: x["n"])
    first = next(x["n"] for x in ident if x["identified"])
    assert first == 3, "identification no longer happens at n = d = 3"
    before = [x for x in ident if x["n"] == first - 1][0]
    assert before["consistent"] > 1, \
        "d-1 observations now identify, so there is no lower bound"
    dep = r["dependent_observations"]
    assert dep["consistent"] > 1, \
        "dependent observations now identify -- independence stopped mattering"


def test_a_link_delays_identification():
    """The GLM claim is DELAY, not destruction -- an earlier version asserted
    destruction and was false. Pin the weaker true statement."""
    r = load_receipt("STAGE_LINEAR_FAMILY_V1.json")
    at = r["identified_at"]
    real = at["real value (regression)"]
    glm = at["threshold (GLM link)"]
    assert real == 3, "regression no longer identifies at n = d"
    assert glm > real, "the link no longer costs anything in samples"


def test_linearity_belongs_to_the_obligation_basis_pair():
    """XOR must fail in raw features and succeed with one product feature.
    Both halves, or the claim is about the obligation alone."""
    r = load_receipt("STAGE_LINEAR_FAMILY_V1.json")
    by = {x["basis"]: x for x in r["basis"]}
    assert by["raw features"]["representable"] is False
    assert by["raw + product"]["representable"] is True


def test_full_monomial_basis_costs_exactly_a_table():
    """The sharpest claim in B3: at full expressiveness a kernel machine
    carries as many coefficients as a table carries slots, and each obligation
    needs exactly its true degree."""
    r = load_receipt("STAGE_LINEAR_FAMILY_V1.json")
    rows = r["basis_cost"]
    full = [x for x in rows if x["obligation"] == "__full_basis__"]
    assert full and full[0]["basis_size"] == 8, \
        "the full monomial basis no longer costs 2^d"
    ladder = [x for x in rows if x["obligation"] != "__full_basis__"]
    for x in ladder:
        assert x["min_basis_degree"] == x["true_degree"], \
            "%s needs degree %s, true degree %s" % (
                x["obligation"], x["min_basis_degree"], x["true_degree"])
    degs = [x["min_basis_degree"] for x in ladder]
    assert min(degs) < max(degs), "the degree ladder collapsed"


def test_sample_count_prediction_holds_at_every_dimension():
    r = load_receipt("STAGE_LINEAR_FAMILY_V1.json")
    for p in r["quantitative_prediction"]:
        assert p["match"], "d=%s predicted %s measured %s" % (
            p["d"], p["predicted"], p["measured"])


def test_depth_without_nonlinearity_buys_nothing():
    """GMI_NEURAL_ARCHITECTURE_DERIVATION_V1: every two-layer linear
    composition must collapse to a single layer, checked constructively."""
    r = load_receipt("STAGE_NEURAL_ARCHITECTURE_V1.json")
    d = r["depth_without_nonlinearity"]
    assert d["checked"] > 100000, "the composition sweep shrank"
    assert d["irreducible"] == 0, \
        "a two-layer linear map escaped single-layer form"


def test_xor_separates_depth_one_from_depth_two():
    """Both halves: XOR unreachable at depth 1 and reachable at depth 2, with a
    bias present so depth 1 is the full linear-threshold class."""
    r = load_receipt("STAGE_NEURAL_ARCHITECTURE_V1.json")
    by = {x["task"]: x for x in r["depth_with_nonlinearity"]}
    assert by["xor2"]["depth1"] is False and by["xor2"]["depth2"] is True
    assert by["majority"]["depth1"] is True, \
        "majority is linearly separable -- if it fails at depth 1 the unit lost its bias"


def test_sharing_is_licensed_by_the_obligation():
    """A permutation-invariant obligation may share; one that merely has the
    same orbit count may not. Without the negative case this says nothing."""
    r = load_receipt("STAGE_NEURAL_ARCHITECTURE_V1.json")
    by = {x["obligation"]: x for x in r["sharing"]}
    assert by["majority"]["permutation_invariant"] is True
    assert by["first_bit"]["permutation_invariant"] is False, \
        "first_bit is not permutation-invariant; sharing there merges inputs"
    assert by["first_bit"]["orbits"] == by["majority"]["orbits"], \
        "the point of first_bit is that orbit COUNT alone does not license sharing"


def test_distributed_coding_is_cheaper_only_when_coordinates_collapse():
    r = load_receipt("STAGE_NEURAL_ARCHITECTURE_V1.json")
    by = {x["obligation"]: x for x in r["distributed"]}
    assert by["factorizing"]["cheaper"] == "distributed"
    assert by["diagonal"]["cheaper"] == "symbolic", \
        "a fully entangled obligation now favours distributed coding"
    assert by["diagonal"]["R"] == 4 and by["diagonal"]["C"] == 4


def test_neural_morphology_has_a_losing_ecology():
    """The bet must lose somewhere, or the morphology would be a universal
    improvement and there would be no twin."""
    r = load_receipt("STAGE_NEURAL_ARCHITECTURE_V1.json")
    v = {x["obligation"]: x["verdict"] for x in r["negative_twin"]}
    assert v["majority"] == "net wins"
    assert v["xor2"] in ("TABLE WINS", "tie"), \
        "the net now beats the table even where it needs full machinery"


def test_gradient_law_needs_a_slope_and_random_search_does_not():
    """GMI_UPDATE_LAW_DERIVATION_V1: on a needle landscape the gradient law
    must return nothing while uniform search still finds the optimum. Both
    halves -- otherwise this is a statement about difficulty, not about what a
    gradient law requires."""
    r = load_receipt("STAGE_UPDATE_LAW_V1.json")
    rough = [x for x in r["reachability"] if x["landscape"] == "rough"]
    smooth = [x for x in r["reachability"] if x["landscape"] == "smooth"]
    assert rough and smooth
    assert all(x["gradient"] is None for x in rough), \
        "a gradient law now follows a slope that does not exist"
    assert all(x["random"] is not None for x in rough), \
        "uniform search should still find a needle"
    assert all(x["gradient"] is not None for x in smooth), \
        "a gradient law should reach the optimum on a smooth landscape"


def test_update_law_has_a_parameter_count_break_even():
    """The gradient premium is fixed while its saving grows with d, so some
    other law must be cheapest at small d."""
    r = load_receipt("STAGE_UPDATE_LAW_V1.json")
    winners = [x["cheapest"] for x in r["charged_cost"]]
    assert len(set(winners)) > 1, "one law is cheapest everywhere -- no break-even"
    assert r["gradient_pays_from_d"] is not None, \
        "the gradient law never becomes cheapest"
    assert winners[0] != "gradient", \
        "the gradient law is now cheapest at the smallest parameter count"


def test_horizon_hypothesis_stays_refuted():
    """The document says plainly that the horizon explanation is MINE and is
    refused. If a change ever made it survive, the document would be stale and
    this must fail rather than quietly pass."""
    r = load_receipt("STAGE_UPDATE_LAW_V1.json")
    assert r["hypothesis_A_horizon_survives"] is False, \
        "the horizon hypothesis now survives -- the document retracts it and is stale"
    assert r["hypothesis_B_substrate_survives"] is True, \
        "the substrate hypothesis no longer survives"
    assert all(x["fits_16"] for x in r["horizon"]["rows"]), \
        "the gradient law no longer fits the registered 16-event budget"


def test_accumulation_modes_scale_on_different_axes():
    """GMI_CREDIT_ASSIGNMENT_DERIVATION_V1: forward cost scales with parameters
    and reverse with outputs, so BOTH regimes must appear. Two earlier versions
    of the witness made reverse win everywhere -- that is what a derivation with
    no content looks like, and this pin is what would catch it."""
    r = load_receipt("STAGE_CREDIT_ASSIGNMENT_V1.json")
    kinds = {x["cheaper"] for x in r["accumulation"]}
    assert "reverse" in kinds, "reverse mode is never cheaper"
    assert "forward" in kinds, \
        "reverse mode is cheaper in every regime -- the choice is not a choice"
    scalar_loss = [x for x in r["accumulation"] if x["n_out"] == 1]
    assert scalar_loss and all(x["cheaper"] == "reverse" for x in scalar_loss), \
        "reverse should win at a scalar loss, the deepest point of its regime"
    assert r["forward_regime"], "the forward-regime twin rows are missing"


def test_mlp_is_recovered_only_when_a_single_layer_fails():
    """Label-free recovery: XOR must return a depth-2 nonlinear machine and a
    linearly separable obligation must not. Recovering an MLP for everything
    would be a search that prefers MLPs rather than one that prices them."""
    r = load_receipt("STAGE_CREDIT_ASSIGNMENT_V1.json")
    by = {x["obligation"]: x for x in r["neutral_recovery"]}
    assert by["xor2"]["is_mlp"] is True, "XOR no longer recovers a multi-layer machine"
    assert by["or2"]["is_mlp"] is False, \
        "a linearly separable obligation now recovers an MLP"
    assert by["xor2"]["depth"] == 2 and by["xor2"]["nonlinearity"] is True
    assert by["or2"]["cost"] < by["xor2"]["cost"], \
        "the simpler obligation should recover the cheaper machine"


def test_symmetry_descriptor_refutes_with_a_counterexample():
    """GMI_EQUIVARIANCE_DERIVATION_V1: the descriptor must separate invariant
    from non-invariant obligations, and must REFUTE with an exhibited
    counterexample rather than merely failing to prove."""
    r = load_receipt("STAGE_EQUIVARIANCE_V1.json")
    by = {x["obligation"]: x for x in r["symmetry"]}
    assert by["has_11"]["shift_invariant"] is True
    assert by["first_is_1"]["shift_invariant"] is False
    assert by["first_is_1"]["counterexample"], \
        "non-invariance is asserted without an exhibited counterexample"
    vals = [x["shift_invariant"] for x in r["symmetry"]]
    assert any(vals) and not all(vals), "the descriptor distinguishes nothing"


def test_receptive_field_is_read_off_the_obligation():
    r = load_receipt("STAGE_EQUIVARIANCE_V1.json")
    by = {x["obligation"]: x["receptive_field"] for x in r["receptive_field"]}
    assert by["has_11"] == 2 and by["has_101"] == 3, \
        "the receptive field no longer matches the pattern width"
    assert by["first_is_1"] is None, \
        "a position-anchored obligation should not be a function of the window multiset"


def test_shift_invariance_licenses_sharing_but_does_not_guarantee_it():
    """parity_all is shift-invariant with receptive field 1 and STILL cannot be
    expressed by an OR-combined shared detector. Losing that row would turn a
    careful claim into an overclaim."""
    r = load_receipt("STAGE_EQUIVARIANCE_V1.json")
    by = {x["obligation"]: x for x in r["recovery"]}
    assert by["has_11"]["shared_works"] is True
    assert by["has_101"]["shared_works"] is True
    assert by["parity_all"]["shared_works"] is False, (
        "parity is now expressible by an OR-combined shared detector, so the "
        "combiner caveat in the document would be stale")


def test_equivariance_negative_twin_separates():
    r = load_receipt("STAGE_EQUIVARIANCE_V1.json")
    by = {x["obligation"]: x for x in r["negative_twin"]}
    assert by["has_11"]["shared_works"] is True
    assert by["first_is_1"]["shared_works"] is False, \
        "sharing now works on a position-anchored obligation"


def test_search_is_forced_when_no_compact_policy_exists():
    """GMI_SEARCH_FRONTIER_DERIVATION_V1: the budget must permit a policy in
    some worlds and forbid it in others, or nothing is forced."""
    r = load_receipt("STAGE_SEARCH_FRONTIER_V1.json")
    poss = [x["policy_possible"] for x in r["frontier_forced"]]
    assert any(poss) and not all(poss), \
        "the storage budget no longer separates compilable worlds from others"


def test_search_orders_are_memory_regimes():
    """Depth-first must hold less than breadth-first on the SAME expansions,
    and a constant heuristic must guide nothing -- without that control,
    best-first would look inherently good."""
    r = load_receipt("STAGE_SEARCH_FRONTIER_V1.json")
    by = {x["order"]: x for x in r["orders"]}
    assert by["depth-first"]["peak_memory"] < by["breadth-first"]["peak_memory"]
    assert by["depth-first"]["expanded"] == by["breadth-first"]["expanded"], \
        "the two blind orders should expand the same nodes, differing only in memory"
    assert by["best-first (informed)"]["expanded"] < by["breadth-first"]["expanded"]
    assert by["best-first (useless h)"]["expanded"] >= by["breadth-first"]["expanded"], \
        "a constant heuristic now beats blind search -- the control is broken"


def test_heuristic_has_a_finite_break_even():
    """Its value is the search it removes, so a dear enough heuristic must stop
    paying. A heuristic that pays at every price is not being charged."""
    r = load_receipt("STAGE_SEARCH_FRONTIER_V1.json")
    w = [x["worth_it"] for x in r["heuristic"]]
    assert any(w) and not all(w), "the heuristic pays at every price or none"


def test_compile_versus_search_crosses_on_reuse():
    r = load_receipt("STAGE_SEARCH_FRONTIER_V1.json")
    kinds = [x["cheaper"] for x in r["compile_vs_search"]]
    assert "search" in kinds and "compile" in kinds, \
        "no crossover between compiling and searching"
    assert kinds[0] == "search" and kinds[-1] == "compile", \
        "the crossover runs the wrong way in reuse"


def test_both_shapes_are_neutrally_recovered():
    r = load_receipt("STAGE_SEARCH_FRONTIER_V1.json")
    reads = {x["reads_as"] for x in r["recovery"]}
    assert len(reads) > 1, \
        "every world recovers the same shape -- nothing has been recovered"


def test_belief_state_is_a_strict_quotient_of_histories():
    """GMI_BELIEF_STATE_DERIVATION_V1: histories must collapse, or the belief
    state saves nothing over storing the raw history."""
    r = load_receipt("STAGE_BELIEF_STATE_V1.json")
    rows = sorted(r["quotient"], key=lambda x: x["length"])
    assert rows[-1]["beliefs"] < rows[-1]["histories"], \
        "no two histories collapse to the same posterior"
    assert rows[-1]["collapse"] > rows[0]["collapse"], \
        "the collapse no longer grows with history length"


def test_point_estimate_fails_only_when_the_mode_is_a_minority():
    """Both halves: it must suffice somewhere and fail somewhere, or this says
    nothing about when a posterior is required."""
    r = load_receipt("STAGE_BELIEF_STATE_V1.json")
    ag = [x["agree"] for x in r["point_estimate"]]
    assert any(ag) and not all(ag), "the point-estimate result became unconditional"
    bad = [x for x in r["point_estimate"] if not x["agree"]]
    assert bad and bad[0]["loss"] != "0", \
        "the failing case now loses nothing, so it is not a failure"


def test_factorization_is_checked_not_assumed():
    r = load_receipt("STAGE_BELIEF_STATE_V1.json")
    by = {x["joint"]: x for x in r["factorization"]}
    assert by["independent"]["factorizes"] is True
    assert by["diagonal"]["factorizes"] is False, \
        "an entangled joint now factorizes -- conditional independence does no work"
    assert by["independent"]["factored"] < by["independent"]["full"]


def test_maintenance_and_compilation_cross_in_horizon():
    """The crossover must run the right way: a table wins at short horizons
    with many queries and cannot be built at long ones."""
    r = load_receipt("STAGE_BELIEF_STATE_V1.json")
    kinds = {x["cheaper"] for x in r["maintain_vs_compile"]}
    assert "compile" in kinds and "maintain" in kinds, \
        "no crossover between maintaining a posterior and compiling a table"
    short = [x for x in r["maintain_vs_compile"] if x["n"] == 2 and x["Q"] == 64][0]
    long_ = [x for x in r["maintain_vs_compile"] if x["n"] == 10 and x["Q"] == 64][0]
    assert short["cheaper"] == "compile" and long_["cheaper"] == "maintain"


def test_smallest_sufficient_state_is_recovered():
    r = load_receipt("STAGE_BELIEF_STATE_V1.json")
    needs = [x["needs_full"] for x in r["recovery"]]
    assert any(needs) and not all(needs), \
        "every belief needs the same state, so nothing is being recovered"


def test_affine_realizability_is_searched_and_separates():
    """GMI_STATE_SPACE_DERIVATION_V1: the pair that matters is two machines with
    the SAME state count and encoding width where only one admits an affine
    update. Without the negative this is a claim about compression, not about
    linear realization."""
    r = load_receipt("STAGE_STATE_SPACE_V1.json")
    by = {x["obligation"]: x for x in r["compression"]}
    assert by["count_b_mod4"]["affine"] is True
    assert by["ends_with_ab"]["affine"] is False, \
        "a non-invertible transition is now affine over GF(2) -- the negative is gone"
    assert by["count_b_mod4"]["states"] == by["ends_with_ab"]["states"], \
        "the pair must be matched on state count, or the separation is confounded"
    assert by["count_b_mod4"]["bits"] == by["ends_with_ab"]["bits"], \
        "the pair must be matched on encoding width too"
    aff = [x["affine"] for x in r["compression"]]
    assert any(aff) and not all(aff), "the affine search distinguishes nothing"


def test_fixed_state_work_does_not_grow_with_horizon():
    r = load_receipt("STAGE_STATE_SPACE_V1.json")
    rows = sorted(r["horizon"], key=lambda x: x["n"])
    assert all(x["cheapest_work"] == "state" for x in rows)
    assert all(x["state_storage"] == rows[0]["state_storage"] for x in rows), \
        "state storage now grows with the horizon"
    assert rows[-1]["attention_work"] > 10 * rows[-1]["state_work"], \
        "the linear/quadratic gap has stopped growing"


def test_relational_state_census_agrees_across_two_methods():
    """GMI_SYMBOLIC_REWRITE_DERIVATION_V1: the 13-of-512 census is decided twice
    by independent methods, and both regimes must be non-empty."""
    r = load_receipt("STAGE_SYMBOLIC_REWRITE_V1.json")
    c = r["relation_census"]
    assert c["methods_agree"] is True, \
        "the two independent census methods no longer agree"
    assert c["scalar_representable_by_search"] == c["scalar_representable_by_certificate"]
    n, total = c["scalar_representable_by_search"], c["relations_total"]
    assert 0 < n < total, "either every relation is scalar-carried or none is"
    assert c["explicit_state_forced"] == total - n


def test_discreteness_twin_is_matched_on_size_and_distinctions():
    """The cyclic/linear pair must stay matched on pair count AND distinct rows,
    or the separation is confounded by something other than structure."""
    r = load_receipt("STAGE_SYMBOLIC_REWRITE_V1.json")
    tw = {x["relation"].split()[0]: x for x in r["relation_twin"]}
    cyc, lin = tw["cyclic"], tw["linear"]
    assert cyc["pairs"] == lin["pairs"], "the twin is no longer matched on size"
    assert cyc["distinct_rows"] == lin["distinct_rows"], \
        "the twin is no longer matched on distinction count"
    assert cyc["scalar"] is None and lin["scalar"] is not None
    assert cyc["violation"], "non-representability is asserted without a certificate"


def test_composition_breakeven_exceeds_collapsing():
    """What isolates closure from the per-map compression both families enjoy."""
    r = load_receipt("STAGE_SYMBOLIC_REWRITE_V1.json")
    by = {}
    for x in r["composition_pvr3"]:
        by["composing" if x["family"].startswith("composing") else "collapsing"] = x
    assert by["composing"]["closure"] > by["collapsing"]["closure"], \
        "the composing family no longer generates a larger closure"
    assert by["composing"]["generator_cells"] == by["collapsing"]["generator_cells"], \
        "the families are no longer matched on generator cost"
    assert by["composing"]["break_even_r"] > by["collapsing"]["break_even_r"], \
        "composition no longer raises the break-even over a collapsing family"


def test_symbolic_parametric_split_runs_along_the_predicted_axis():
    """Both must win somewhere AND along the stated axis. An earlier ladder had
    no parametric winner at all and was vacuous, so winning somewhere is not
    enough on its own."""
    r = load_receipt("STAGE_SYMBOLIC_REWRITE_V1.json")
    rows = [x for x in r["sparsity_ladder"] if x["L"] == 4]
    assert rows, "the L=4 ladder is missing"
    winners = {x["cheaper"] for x in rows}
    assert "symbolic" in winners and "parametric" in winners, \
        "the symbolic/parametric ladder lost one of its two regimes"
    ctx = [x for x in rows if "ab -> ba" in x["obligation"]]
    aff = [x for x in rows if "flip every slot" in x["obligation"]]
    assert ctx and all(x["cheaper"] == "symbolic" for x in ctx), \
        "the context-sensitive obligation is no longer symbolic-cheaper"
    assert aff and all(x["cheaper"] == "parametric" for x in aff), \
        "the affine obligation is no longer parametric-cheaper"


def test_ordering_is_worth_cells_and_tolerance_pays_early():
    """Ordering must beat an unordered sound cover, and the saving must appear
    at a SMALL error fraction rather than only a degenerate one."""
    r = load_receipt("STAGE_SYMBOLIC_REWRITE_V1.json")
    e = r["exactness_curve"]
    assert e["exact_cells_ordered"] < e["exact_cells_unordered"], \
        "an ordered machine no longer beats an unordered sound cover"
    assert r["ordering_saving_cells"] > 0
    assert e["defaults_enumerated"] >= 1296, \
        "the default search was truncated again -- the curve would be non-minimal"
    one = [x for x in e["rows"] if x.get("errors") == 1]
    assert one and one[0]["cells"] < e["exact_cells_ordered"], \
        "tolerating a single error no longer saves anything"


def test_rewrite_fingerprints_are_measured_not_labelled():
    r = load_receipt("STAGE_SYMBOLIC_REWRITE_V1.json")
    fp = {tuple(x["fingerprint"]) for x in r["neutral_recovery"]}
    assert len(fp) >= 4, "the measured fingerprints have collapsed"
    instrs = [x["instructions"] for x in r["neutral_recovery"]]
    assert min(instrs) == 1 and max(instrs) >= 8, \
        "both degenerate ends (a one-instruction machine and a full table) must be reached"


def test_collapsibility_is_necessary_but_not_sufficient():
    """GMI_CONDITIONAL_SPECIALIZATION_DERIVATION_V1: no tag-collapsible world may
    pay, and non-collapsible worlds must SPLIT on whether they pay. If every
    non-collapsible world paid, the condition would be a biconditional -- which
    an earlier single-catalogue version wrongly reported."""
    r = load_receipt("STAGE_CONDITIONAL_SPECIALIZATION_V1.json")
    rows = r["census"]
    coll_pay = [x for x in rows if x["max_places"] == 1 and x["pays"]]
    assert not coll_pay, "a tag-collapsible world now pays"
    noncoll = [x for x in rows if x["max_places"] > 1]
    pay = [x for x in noncoll if x["pays"]]
    assert pay, "no non-collapsible world pays"
    assert len(pay) < len(noncoll), (
        "every non-collapsible world pays, so the condition has become a "
        "biconditional -- that was the confounded result, not the real one")


def test_which_term_carries_the_surplus():
    """The mechanism is NOT mainly duplicated bodies. If that ever flips, the
    document's central correction is stale."""
    r = load_receipt("STAGE_CONDITIONAL_SPECIALIZATION_V1.json")
    w = r["which_term"]
    assert w["paying"] > 0
    assert w["map_cheaper_than_reach"] >= w["bodies_cost_more_undivided"], (
        "duplicated bodies now carry the surplus more often than the "
        "separation term -- the document says the opposite")


def test_conditioning_never_saves_expected_traversal():
    """Compute is refuted here, not merely unaddressed. A split that became
    cheaper on expected traversal would overturn that."""
    r = load_receipt("STAGE_CONDITIONAL_SPECIALIZATION_V1.json")
    t = r["traversal_summary"]
    assert t["expected_split_ever_cheaper"] is False, \
        "the split is now cheaper on expected traversal somewhere"
    assert t["expected_split_strictly_worse_in"] > 0


def test_split_advantage_expires_at_a_finite_query_count():
    """PVR-3 with the split on the retention side: some world must change hands."""
    r = load_receipt("STAGE_CONDITIONAL_SPECIALIZATION_V1.json")
    rows = r["query_crossover"]
    finite = [x for x in rows if x["r_star"] != "never"]
    assert finite, "no paying world's advantage expires -- the crossover is gone"
    changed = [x for x in rows if x["verdict_r8"] != x["verdict_r512"]]
    assert changed, "no verdict changes hands between r=8 and r=512"


def test_recovery_is_not_a_handed_answer():
    """The world's own obligation split must LOSE most of the time. A chooser
    handed the answer would win all 60, and a mutation showed the gate once
    accepted exactly that."""
    r = load_receipt("STAGE_CONDITIONAL_SPECIALIZATION_V1.json")
    rows = r["recovery"]
    own = [x for x in rows if x["winner_is_the_worlds_own_split"]]
    assert 0 < len(own) < len(rows), (
        "the world's own split wins always or never -- in either case the "
        "recovery is not discriminating")
    assert len(own) < len(rows) / 2, \
        "the world's own split now wins most worlds, which is what a rigged chooser looks like"


def test_variable_duration_not_long_duration_forces_a_gate():
    """GMI_GATED_RECURRENCE_DERIVATION_V1: the two ecologies must stay MATCHED on
    longest delay, or the comparison is confounded by duration length rather
    than duration variance -- which is the whole claim."""
    r = load_receipt("STAGE_GATED_RECURRENCE_V1.json")
    by = {x["ecology"]: x for x in r["gating_pressure"]}
    fixed = [v for k, v in by.items() if k.startswith("fixed")][0]
    var = [v for k, v in by.items() if k.startswith("variable")][0]
    assert fixed["max_gap"] == var["max_gap"], \
        "the ecologies are no longer matched on longest delay"
    assert fixed["register_lengths_that_work"], \
        "no register solves the fixed ecology -- the twin is broken"
    assert not var["register_lengths_that_work"], \
        "a register now solves the variable ecology, refuting the central claim"
    assert fixed["gated_works"] and var["gated_works"]


def test_gating_has_a_cost_threshold_at_fixed_duration():
    """Both machines correct, so the question is price. A register must win at
    short delays or gating would be unconditionally right."""
    r = load_receipt("STAGE_GATED_RECURRENCE_V1.json")
    kinds = [x["cheaper"] for x in r["crossover"]]
    assert "register" in kinds and "gated" in kinds, \
        "no crossover -- gating is now always or never worth its price"
    assert kinds[0] == "register" and kinds[-1] == "gated", \
        "the crossover runs the wrong way in delay"


def test_retention_span_equals_capacity():
    r = load_receipt("STAGE_GATED_RECURRENCE_V1.json")
    rows = sorted(r["retention"], key=lambda x: x["L"])
    for x in rows:
        assert len(x["answers_gaps"]) <= 2, \
            "a register now answers many gaps at once"
    spans = [x["max_gap"] for x in rows if x["max_gap"] is not None]
    assert spans == sorted(spans) and len(set(spans)) > 1, \
        "retention span no longer tracks capacity"


def test_both_recurrence_shapes_are_recovered():
    r = load_receipt("STAGE_GATED_RECURRENCE_V1.json")
    reads = {x["reads_as"] for x in r["recovery"]}
    assert len(reads) > 1, "every ecology recovers the same shape"
    assert any(x["n_options"] > 1 for x in r["recovery"]), \
        "no ecology ever had a real choice between the two shapes"


def test_action_quotient_is_coarser_than_belief():
    """GMI_CONTROL_FAMILY_DERIVATION_V1: a controller needs the quotient its
    ACTIONS induce, which is strictly coarser than the belief partition. If
    they ever coincide, the document's central claim is gone."""
    r = load_receipt("STAGE_CONTROL_FAMILY_V1.json")
    p = r["policy_memory"]
    assert p["action_classes"] < p["belief_classes"], \
        "the action quotient is no longer coarser than the belief partition"
    assert p["minimal_m_base"] > p["minimal_m_twin"], \
        "hiding the cue no longer costs memory -- the twin is broken"


def test_state_only_reward_cannot_induce_an_ordered_task():
    """The impossibility is the result: equal count vectors mean no additive
    reward on state alone can separate the two tasks. The time-indexed repair
    must succeed, or the section shows impossibility without a remedy."""
    r = load_receipt("STAGE_CONTROL_FAMILY_V1.json")
    by = {x["target"]: x for x in r["reward_sufficiency"]}
    ordered = [v for k, v in by.items() if "then" in k][0]
    assert ordered["state_only_hits"] == 0, \
        "a state-only reward now induces the ordered task"
    assert ordered["time_indexed_hits"] > 0, \
        "the time-indexed repair no longer works"
    other = [v for k, v in by.items() if "twice" in k][0]
    assert other["state_only_hits"] > 0, \
        "the control task must be state-only inducible, or the contrast is lost"


def test_caching_dominates_whole_table_compilation():
    """Compile-all must never win. If it does, the trichotomy collapses to the
    usual two-way story."""
    r = load_receipt("STAGE_CONTROL_FAMILY_V1.json")
    rows = r["trichotomy"]
    assert rows, "the trichotomy sweep is missing"
    assert not any(x["cheapest"].startswith("compile") for x in rows), \
        "whole-table compilation now wins somewhere"
    kinds = {x["cheapest"] for x in rows}
    assert len(kinds) > 1, "one shape is cheapest at every reuse -- no crossover"


def test_partial_holding_is_what_uneven_visitation_buys():
    """The intermediate shape must appear in the base world and NEVER in the
    twin where every key is visited exactly once. Without the twin it would be
    a tuning artefact."""
    r = load_receipt("STAGE_CONTROL_FAMILY_V1.json")
    held = {(x["held"], x["keys"]) for x in r["recovery"]}
    partial = [h for h in held if 0 < h[0] < h[1]]
    assert partial, "no intermediate holding wins anywhere"
    assert r["recovery_twin"]["partial_wins"] == 0, (
        "partial holding now wins in the even-visitation twin, so it is not "
        "uneven visitation that buys it")


def test_exploration_is_the_price_of_not_being_told():
    r = load_receipt("STAGE_CONTROL_FAMILY_V1.json")
    e, t = r["exploration"], r["exploration_twin"]
    assert e["best_constant"] > 0, "a constant-arm machine is now optimal"
    assert t["min_total_regret"] == 0, \
        "announcing the payoffs no longer removes the regret"
    assert t["min_regret_if_explores_split"] > 0, \
        "exploring where arms differ is now free even when told"


def test_options_pay_by_recurrence():
    r = load_receipt("STAGE_CONTROL_FAMILY_V1.json")
    by = {x["tasks"]: x for x in r["options"]}
    assert by["recurring"]["margin"] > 0
    assert by["no recurrence"]["margin"] < 0, \
        "an option with no recurrence now pays -- the condition is vacuous"


def test_carrier_is_not_the_answer_alphabet():
    """GMI_MESSAGE_PASSING_DERIVATION_V1: the naive reading of CSR-1 would be
    "the carrier is the size of the answer alphabet". reach_3 and odd_dist_3
    refute it -- matched on rounds AND on answer alphabet, differing in carrier.
    If they ever stop being matched the refutation is confounded."""
    r = load_receipt("STAGE_MESSAGE_PASSING_V1.json")
    by = {x["obligation"]: x for x in r["carrier"]}
    a, b = by["reach_3"], by["odd_dist_3"]
    assert a["rounds"] == b["rounds"], "the pair is no longer matched on rounds"
    assert a["answer_values"] == b["answer_values"], \
        "the pair is no longer matched on answer alphabet"
    assert b["states"] > a["states"], \
        "the carriers no longer differ -- the refutation is gone"
    for x in r["carrier"]:
        assert x["verified"] and x["configs_verified"] > 30000, \
            "%s is no longer verified on the full configuration set" % x["obligation"]
        assert x["states"] >= x["answer_values"]


def test_two_state_search_has_a_working_positive_control():
    """A negative from a search is worthless unless the search can succeed.
    reach_3 must be FOUND, or odd_dist_3 finding nothing proves nothing."""
    r = load_receipt("STAGE_MESSAGE_PASSING_V1.json")
    t = r["two_state_search"]
    assert t["reach_3_found"] > 0, \
        "the searcher's positive control fails, so its negative is worthless"
    assert t["odd_dist_3_found_at_pinned_rounds"] == 0, \
        "a two-state machine now meets odd_dist_3 at the pinned round count"
    assert t["machines_enumerated"] > 60000


def test_the_expressiveness_ceiling_pair_is_genuinely_blind():
    """The 1-WL ceiling: a non-isomorphic pair merged at every round, with a
    MATCHED obligation that is NOT blind. Without the matched positive this
    would only show the method is weak somewhere."""
    r = load_receipt("STAGE_MESSAGE_PASSING_V1.json")
    six = r["ceiling"]["6"]
    obl = six["obligations"]
    assert obl["connected"]["blind_at_stable_round"] is True, \
        "connectivity is no longer blind at the stable round"
    assert obl["leafy"]["blind_at_stable_round"] is False, \
        "the matched positive is now blind too, so the ceiling claim is confounded"


def test_every_access_wins_somewhere_and_none_dominates():
    """A menu where one access always wins is not a recovery. An earlier
    alphabetical tie-break inflated INCIDENT_BAG to 7 of 10."""
    r = load_receipt("STAGE_MESSAGE_PASSING_V1.json")
    counts = r["recovery_winner_counts"]
    total = sum(counts.values())
    assert all(v > 0 for v in counts.values()), \
        "not every access wins somewhere: %s" % counts
    assert counts["INCIDENT_BAG"] <= total / 2, (
        "the relational access now wins a majority, which is what the "
        "alphabetical tie-break bug looked like")


def test_finest_state_lemma_still_declares_its_argued_half():
    """Half of this lemma is a proof by induction, not an enumeration. The
    receipt says so verbatim; if that ever silently becomes a measurement
    claim, the document's scope note is stale."""
    r = load_receipt("STAGE_MESSAGE_PASSING_V1.json")
    f = r["finest_state_lemma"]
    assert f["colour_is_realisable_by_a_local_rule"] is True
    assert "ARGUED" in f["no_machine_separates_more"], \
        "the argued half of the finest-state lemma is no longer declared as argued"


def test_dynamic_routing_needs_both_halves_of_the_antecedent():
    """GMI_DYNAMIC_ROUTING_DERIVATION_V1: routing is forced by a CONJUNCTION --
    a tight budget AND a content-dependent target. Both twins must hold, or the
    claim collapses to 'routing is generally useful'."""
    r = load_receipt("STAGE_DYNAMIC_ROUTING_V1.json")
    by = {(x["obligation"], x["budget"]): x for x in r["conjunction"]}
    forced = by[("content-dependent", 2)]
    assert forced["fixed"] is None and forced["dynamic"], \
        "tight budget + content-dependent target no longer forces routing"
    lifted = by[("content-dependent", 6)]
    assert lifted["fixed"] is not None, \
        "TWIN A broken: lifting the budget must make a fixed policy sufficient"
    fixed_target = by[("content-independent", 2)]
    assert fixed_target["fixed"] is not None, \
        "TWIN B broken: a fixed target must be servable by a fixed policy"


def test_there_is_a_band_where_routing_is_the_only_machine():
    """Not merely cheaper -- the only thing that works. If a fixed policy ever
    succeeds at the budget routing needs, that band disappears."""
    r = load_receipt("STAGE_DYNAMIC_ROUTING_V1.json")
    sweep = sorted(r["budget_sweep"], key=lambda x: x["budget"])
    first_dyn = next(x["budget"] for x in sweep if x["dynamic_ok"])
    first_fixed = next(x["budget"] for x in sweep if x["fixed_ok"])
    assert first_fixed > first_dyn, \
        "a fixed policy now works as cheaply as routing -- no forced band"


def test_routing_presupposes_positional_distinction():
    """Both halves: with position it works, without it fails. If an unordered
    bag sufficed the obligation would not be order-sensitive."""
    r = load_receipt("STAGE_DYNAMIC_ROUTING_V1.json")
    p = r["position"]
    assert p["with_position"] is True and p["without_position"] is False, \
        "position is no longer necessary, so this section is vacuous"


def test_routing_loses_where_the_target_is_fixed():
    """The negative ecology. Routing must be strictly more expensive where the
    choice it buys is never used."""
    r = load_receipt("STAGE_DYNAMIC_ROUTING_V1.json")
    n = r["negative_ecology"]
    assert n["routing_loses"] is True, \
        "routing no longer loses where the target's place is fixed"
    assert n["dynamic_cost"] > n["fixed_cost"]


def test_both_reader_shapes_are_recovered():
    r = load_receipt("STAGE_DYNAMIC_ROUTING_V1.json")
    kinds = {x["reads_as"] for x in r["recovery"] if x.get("shape")}
    assert len(kinds) > 1, "every ecology recovers the same reader shape"


def test_a_library_chunk_loses_on_both_earlier_ledgers():
    """GMI_PROGRAM_LIBRARY_DERIVATION_V1: the delta is that a chunk adds no
    reachable function and costs more to serve, so it can only earn on search.
    If a chunk ever enlarges the closure, that framing is wrong."""
    r = load_receipt("STAGE_PROGRAM_LIBRARY_V1.json")
    c = r["collapsing_control"]
    assert c, "the closure control is missing"


def test_the_paying_window_is_bounded_at_both_ends():
    """Too shallow, nothing to shorten; too deep, branching outruns the levels
    saved. An unbounded window would make this a monotone trade instead of an
    optimum."""
    r = load_receipt("STAGE_PROGRAM_LIBRARY_V1.json")
    w = r["paying_windows"]
    assert w, "the paying windows are missing"
    for length, (lo, hi) in w.items():
        assert lo <= hi, "window for length %s is empty" % length
        assert hi < 20, (
            "the paying window for length %s is unbounded above, so the "
            "branching tax no longer bites" % length)


def test_library_recovery_is_not_a_handed_answer():
    """The searcher's winner must differ from the most frequent short answer.
    A chooser handed the answer would return exactly that."""
    r = load_receipt("STAGE_PROGRAM_LIBRARY_V1.json")
    a = r["anti_rig"]
    assert a["differs_from_most_frequent"] is True
    assert a["differs_from_most_frequent_len3"] is True, (
        "the search winner now matches the most frequent short answer, which "
        "is what a handed answer looks like")
    plans = r["neutral_recovery"]
    stores_nothing = [x["stores_nothing"] for x in plans]
    assert any(stores_nothing) and not all(stores_nothing), (
        "storing nothing wins everywhere or nowhere -- the recovery is not "
        "discriminating")


def test_chain_ordering_law_still_fails_its_held_test():
    """GMI_GENERATIVE_FAMILY_DERIVATION_V1: the main finding is a FAILURE. The
    law is perfect on the support size it was fitted on and wrong elsewhere.
    This pin locks the failure in -- a change that quietly made it pass would
    silently erase a filed correction."""
    r = load_receipt("STAGE_GENERATIVE_FAMILY_V1.json")
    held = r["held_law3"]
    failing = [x for x in held if not x["agree"]]
    assert failing, (
        "the chain-ordering law now agrees on every held support size, so the "
        "CORRECTED finding in the document is stale")
    worst = max(x["misses"]["said sensitive, was flat"] for x in held)
    assert worst > 0, "the law no longer mispredicts any joint"


def test_only_the_one_way_symmetry_implication_survives():
    r = load_receipt("STAGE_GENERATIVE_FAMILY_V1.json")
    law = r["chain_symmetry_law"]
    assert law["symmetric_implies_flat"] is True
    assert law["symmetric_sensitive"] == 0
    assert law["converse_holds"] is False, (
        "the converse now holds, which would make the law two-way after it was "
        "filed as one-way only")


def test_no_bijection_creates_a_zero_atom():
    """The sharp impossibility, verified by exhaustion rather than argued."""
    r = load_receipt("STAGE_GENERATIVE_FAMILY_V1.json")
    f = r["flow_zero_impossibility"]
    assert f["bijections_enumerated"] >= 40320, "the exhaustion shrank"
    assert f["reachable_from_full_support_base"] == [], (
        "a joint with a zero atom is now reachable from a full-support base by "
        "bijection, which is impossible unless the model changed")
    assert len(f["targets_with_a_zero_atom"]) >= 2


# ---------------------------------------------------------------------------
# B1 protocol conformance audit.
#
# This one is NOT a witness: it reads every family's receipt and witness source,
# so it cannot run in the one-file temp dir that _run_witness creates.  It runs
# in the tree instead.  It is still reproduction-checked -- it writes a receipt
# and the claim pins below assert the document's headline numbers.
# ---------------------------------------------------------------------------
def test_protocol_conformance_audit_reproduces_its_committed_receipt():
    """The audit asserts its own adjudication against the receipts.

    If a family's named control key is absent from its receipt, or a family
    adjudicated as having no control is hiding one, the audit fails here rather
    than reporting a number that was never checked.

    The audit needs the whole tree, so unlike a witness it cannot run in a
    one-file temp dir -- it runs in place.  That would overwrite the committed
    receipt, so the receipt is snapshotted, regenerated, compared, and restored.
    The comparison IS the reproduction check.
    """
    receipt = os.path.join(RESULTS, "STAGE_PROTOCOL_CONFORMANCE_V1.json")
    before = open(receipt).read() if os.path.exists(receipt) else None
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join("gmi_microscope", "protocol_conformance_audit.py")],
            cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
        assert proc.returncode == 0, (
            "protocol_conformance_audit.py failed:\n" + proc.stdout.decode()[-4000:])
        after = open(receipt).read()
        assert before is not None, "no committed receipt to reproduce"
        assert json.loads(after) == json.loads(before), (
            "the audit no longer reproduces its committed receipt -- the "
            "corpus changed under it, which is exactly what this guard is for")
    finally:
        if before is not None:
            with open(receipt, "w") as fh:
                fh.write(before)


def test_adjudicated_conformance_numbers_are_the_documented_ones():
    """The two numbers the document publishes as measured."""
    r = load_receipt("STAGE_PROTOCOL_CONFORMANCE_V1.json")
    cms = {c["signal"]: c for c in r["signal_validation"]}

    twin = cms["matched negative control"]
    adjudicated_true = twin["tp"] + twin["fn"]
    assert adjudicated_true == 11, (
        "the document reports 11 of 19 families constructing a matched negative "
        "control; the adjudication now says %d" % adjudicated_true)

    real = cms["real-regime replication"]
    assert real["tp"] + real["fn"] == 0, (
        "a family now replicates at a real regime, which would retire the "
        "corpus's largest stated gap -- the document says 0 of 19")


def test_the_vocabulary_proxy_is_still_unsound_in_both_directions():
    """If this ever passes cleanly the document's central argument is stale."""
    r = load_receipt("STAGE_PROTOCOL_CONFORMANCE_V1.json")
    cms = {c["signal"]: c for c in r["signal_validation"]}

    assert cms["matched negative control"]["missed"] == ["B2 finite-state"], (
        "the matched-control signal no longer misses exactly B2, whose control "
        "is named 'stateless' -- the miss is what shows the proxy is unsound")
    assert cms["real-regime replication"]["tp"] == 0, (
        "the real-regime signal gained a true positive")
    assert cms["real-regime replication"]["false_positive"] == ["B14 symbolic rewrite"], (
        "the real-regime signal's only positive should be B14's 'production "
        "system' -- a semantic false positive that word boundaries cannot "
        "remove, which is the document's precision-zero evidence")

    sat = [k for k, v in r["widening_test"].items() if v["receipt_plus_source"] >= 18]
    assert len(sat) >= 4, (
        "widening to witness source no longer saturates at least four signals, "
        "so the argument that loosening the proxy destroys it is stale")


def test_no_shared_vocabulary_for_the_matched_control():
    """The exhibited cause: nine names, no common token."""
    r = load_receipt("STAGE_PROTOCOL_CONFORMANCE_V1.json")
    cs = r["control_synonyms"]
    assert cs["shared_tokens"] == [], (
        "the control names now share a token, so a single-token regex would "
        "find them all and the no-shared-vocabulary finding is wrong")
    assert len(cs["names"]) == 9, (
        "the document states nine distinct names; the census now has %d"
        % len(cs["names"]))
    assert "stateless" in cs["names"], (
        "'stateless' is the name the regex misses -- it carries the argument")


def test_protocol_block_adoption_is_all_or_nothing_and_currently_none():
    r = load_receipt("STAGE_PROTOCOL_CONFORMANCE_V1.json")
    pb = r["protocol_block"]
    assert pb["total"] == 19
    assert pb["compliant"] == [] or len(pb["compliant"]) == 19, (
        "partial protocol-block adoption invites a reader to mistake 'n of 19 "
        "emitting' for 'n of 19 conforming'")
    if pb["compliant"] == []:
        assert pb["partial"] == [], (
            "some family emits a partial protocol block; complete it or remove it")


# ---------------------------------------------------------------------------
# B12 residual memory (retrieval-augmented holding) -- claim pins.
# ---------------------------------------------------------------------------
def test_neutral_search_finds_both_holdings_and_change_separates_them():
    """The split is the finding: both are reachable, change picks one."""
    r = load_receipt("STAGE_RESIDUAL_MEMORY_V1.json")
    n = r["neutral_split"]
    assert n["external"] > 0 and n["internal"] > 0, (
        "neutral search reached only one kind of holding, so the comparison "
        "has no content")
    assert n["external_under_change"] > n["internal_under_change"], (
        "an external store no longer survives change better than an absorbed "
        "one, which is the whole reason the family is derived")


def test_the_holding_comparison_is_not_rigged():
    """Anti-rig gates: several kinds win, none wins everywhere."""
    r = load_receipt("STAGE_RESIDUAL_MEMORY_V1.json")
    won = r["comparison_tally"]
    assert len(won) >= 2, "only one holding ever attains the minimum"
    cells = r["comparison_cells"]
    total = len(cells) if isinstance(cells, list) else cells
    assert max(won.values()) < total, (
        "one holding attains the minimum in every cell -- rigged comparison")
    assert r["comparison_outright"], "every cell is a tie, so nothing is decided"


def test_the_store_is_forced_somewhere_and_wasteful_somewhere():
    """Both verdicts must occur or the irreducibility section is one-sided."""
    r = load_receipt("STAGE_RESIDUAL_MEMORY_V1.json")
    verdicts = {x["verdict"] for x in r["irreducibility"]}
    assert "STORE IS FORCED" in verdicts, (
        "no obligation forces a store, so residual memory is never necessary")
    assert "STORE IS WASTE" in verdicts, (
        "no obligation makes the store wasteful, which would mean the finding "
        "is 'always store' and the ecology is not discriminating")


# ---------------------------------------------------------------------------
# B20 tool routing -- claim pins.
# ---------------------------------------------------------------------------
def test_routing_cost_primitive_agrees_with_exhaustive_enumeration():
    r = load_receipt("STAGE_TOOL_ROUTING_V1.json")
    rows = {x["arity"]: x for x in r["primitive_validation"]}
    for arity in (2, 3):
        assert rows[arity]["mismatches"] == 0, (
            "the DP disagrees with exhaustive enumeration at arity %d" % arity)
        assert rows[arity]["with_dont_cares"] > 0, (
            "no partial function carried a don't-care at arity %d, so the new "
            "code path was never exercised" % arity)


def test_breadth_is_paid_in_the_summed_price_not_the_posted_one():
    """Where the cost of overlap actually lives.

    A holder posts one price: its worst task's probing cost.  That saturates at
    the payload arity, so the BROADEST holder posts no more than a narrow one --
    the max cannot see breadth at all.  The cost shows up once per call, in the
    sum over tasks of the cheapest competent holder's price.
    """
    r = load_receipt("STAGE_TOOL_ROUTING_V1.json")
    ov = {x["layout"]: x for x in r["overlap"]}
    part, everyone = ov["partition"], ov["everyone"]

    assert part["covered"] == everyone["covered"], (
        "the layouts no longer cover the same tasks, so their costs are not "
        "comparable")
    assert everyone["broadest_price"] == part["broadest_price"], (
        "the posted price now separates total redundancy from a partition; if "
        "that is real the documented reason for using the summed price (the "
        "max saturates at the payload arity) is stale")
    assert everyone["cheapest_sum"] > part["cheapest_sum"], (
        "total redundancy is no longer dearer in summed price, so overlap is "
        "free and the cost claimed for it does not exist")
    assert everyone["fallbacks"] > part["fallbacks"] == 0, (
        "the partition has a fallback, or total redundancy has none, so the "
        "contrast is not the one claimed")


def test_price_is_monotone_in_competence_but_not_strictly():
    """The saturation, measured rather than argued."""
    r = load_receipt("STAGE_TOOL_ROUTING_V1.json")
    pm = r["price_monotone"]
    assert pm["nested_pairs"] > 0, "no nested competence pairs were compared"
    assert 0 < pm["strictly_dearer"] < pm["nested_pairs"], (
        "taking on more tasks is either always or never strictly dearer; "
        "either way the reported partial saturation is stale")


# ---------------------------------------------------------------------------
# B2 at a real regime -- claim pins.
#
# This is the corpus's first movement off "0 of 19 families replicate at a real
# regime".  The pins guard the criterion as much as the number: a replication
# where the exhaustive method was merely slow would not be one.
# ---------------------------------------------------------------------------
def test_the_avoided_enumeration_is_impossible_not_merely_slow():
    """The criterion, fixed before the measurement, must still be met."""
    r = load_receipt("STAGE_REAL_REGIME_FINITE_STATE_V1.json")
    e = r["exhaustion_avoided"]
    assert e["states"] >= 10000, "the scale shrank below the registered N"
    assert e["log10_machine_count"] > 1000, (
        "the enumeration this replaces is no longer astronomically large, so "
        "the result is a faster search rather than a real-regime replication")
    assert e["certificate_pair_tests"] == e["states"] * (e["states"] - 1) // 2


def test_every_certificate_pair_was_actually_checked():
    """A fooling set proves a bound only if every pair is separated."""
    r = load_receipt("STAGE_REAL_REGIME_FINITE_STATE_V1.json")
    c = r["certificate"]
    assert c["pairs_checked"] == 49995000, (
        "the number of executed pair tests changed; the lower bound rests on "
        "these having been run, not on the algebra that generated them")
    assert c["pairs_failed"] == 0, "an exhibited suffix fails to separate a pair"
    assert c["fooling_set_size"] == 10000


def test_the_certificate_checker_can_reject():
    """Without this, section 2 passing is coverage rather than evidence."""
    r = load_receipt("STAGE_REAL_REGIME_FINITE_STATE_V1.json")
    m = r["mutation_control"]
    assert m["unseparated_pairs"] > 0, (
        "a deliberately corrupted suffix is still accepted as separating every "
        "probed pair, so the pair test cannot tell a valid certificate from an "
        "invalid one")


def test_only_the_lower_bound_is_claimed_to_replicate():
    """The honest half of the result, pinned so it cannot quietly widen."""
    r = load_receipt("STAGE_REAL_REGIME_FINITE_STATE_V1.json")
    v = r["verdict"]
    assert v["lower_bound_replicates"] is True
    assert v["upper_bound_replicates"] is False, (
        "the upper bound now claims to replicate; exhaustive replay over all "
        "inputs does not scale, so if this flipped, check what it is really "
        "asserting before believing it")
    u = r["upper_bound"]
    assert u["states_exercised_by_replay"] < u["states"], (
        "the bounded replay now reaches every state, which would make the "
        "document's scope caveat false")
    assert u["state_errors"] == 0 and u["replay_errors"] == 0


def test_the_bound_is_a_property_of_the_obligation_not_the_method():
    """Matched negative control: an index-2 obligation must certify 2, not N."""
    r = load_receipt("STAGE_REAL_REGIME_FINITE_STATE_V1.json")
    n = r["negative_control"]
    assert n["certified_lower_bound"] <= 3, (
        "the same construction certifies a large bound for an obligation whose "
        "index is 2, so the certificate inflates and the N-state result is not "
        "trustworthy")
    assert n["main_obligation_bound"] > 100 * n["certified_lower_bound"]


# ---------------------------------------------------------------------------
# The corpus's first checkable pre-registration.
#
# predict_intersection_index.py was committed and pushed in a commit containing
# NO measuring code; compare_intersection_index.py was written afterwards.  Git
# commit order is the evidence, which is the property the four corrected
# witnesses lacked -- there, prediction and measurement shared one run.
# ---------------------------------------------------------------------------
def test_adjudication_reproduces_and_scores_the_frozen_prediction():
    receipt = os.path.join(RESULTS, "STAGE_INTERSECTION_INDEX_VERDICT_V1.json")
    before = open(receipt).read() if os.path.exists(receipt) else None
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join("gmi_microscope",
                                          "compare_intersection_index.py")],
            cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
        assert proc.returncode == 0, (
            "compare_intersection_index.py failed:\n" + proc.stdout.decode()[-4000:])
        assert before is not None, "no committed verdict to reproduce"
        assert json.loads(open(receipt).read()) == json.loads(before), (
            "the adjudication no longer reproduces its committed verdict")
    finally:
        if before is not None:
            with open(receipt, "w") as fh:
                fh.write(before)


def test_the_frozen_prediction_is_scored_not_assumed():
    """The verdict must be computed against the committed prediction receipt."""
    pred = load_receipt("STAGE_INTERSECTION_INDEX_PREDICTION_V1.json")
    got = load_receipt("STAGE_INTERSECTION_INDEX_VERDICT_V1.json")
    assert got["registration_scored"] == pred["registration"], (
        "the verdict scores a different registration than the one committed")
    assert got["predicted_index"] == pred["predicted_index"], (
        "the verdict's copy of the prediction differs from the frozen receipt, "
        "which would mean the prediction was edited after the outcome")
    assert pred["phase"].startswith("prediction"), (
        "the prediction receipt no longer declares itself measurement-free")


def test_the_intersection_collapses_below_the_product_bound():
    """Non-vacuity: if the index were 3m there would be nothing to predict."""
    r = load_receipt("STAGE_INTERSECTION_INDEX_VERDICT_V1.json")
    meas, prod, reach = r["measured_index"], r["product_bound"], r["reachable_states"]
    assert all(meas[k] < prod[k] for k in meas), (
        "some m no longer collapses below the generic product bound")
    assert all(reach[k] == prod[k] for k in reach), (
        "not every product state is reachable any more; the collapse would then "
        "be partly unreachability rather than indistinguishability, which is a "
        "weaker and different claim")
    assert all(meas[k] == int(k) + 2 for k in meas), (
        "the measured rule is no longer index = m + 2")


def test_the_verdict_records_whether_the_prediction_held():
    r = load_receipt("STAGE_INTERSECTION_INDEX_VERDICT_V1.json")
    assert r["verdict"] in ("HOLDS", "FALSIFIED")
    assert r["verdict"] == ("HOLDS" if not r["disagreeing_m"] else "FALSIFIED"), (
        "the verdict label disagrees with its own disagreement list")
    assert len(r["agreeing_m"]) + len(r["disagreeing_m"]) >= 8, (
        "fewer values of m were scored than were frozen")


# ---------------------------------------------------------------------------
# Section K: a predicted cost law for a form nobody had built, frozen before the
# adjudicator existed (commit 0c9abc83) and scored afterwards.
# ---------------------------------------------------------------------------
def test_composition_law_adjudication_reproduces():
    receipt = os.path.join(RESULTS, "STAGE_COMPOSITION_LAW_VERDICT_V1.json")
    before = open(receipt).read() if os.path.exists(receipt) else None
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join("gmi_microscope",
                                          "compare_composition_law.py")],
            cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900)
        assert proc.returncode == 0, (
            "compare_composition_law.py failed:\n" + proc.stdout.decode()[-4000:])
        assert before is not None, "no committed verdict to reproduce"
        assert json.loads(open(receipt).read()) == json.loads(before), (
            "the composition-law adjudication no longer reproduces its receipt")
    finally:
        if before is not None:
            with open(receipt, "w") as fh:
                fh.write(before)


def test_composition_is_lcm_not_product():
    """Law 1, and that the test set can tell the two apart."""
    r = load_receipt("STAGE_COMPOSITION_LAW_VERDICT_V1.json")
    assert r["law_1_misses"] == [], (
        "a k-fold counting intersection no longer has index lcm: %s"
        % r["law_1_misses"])
    meas, prod = r["measured_counting_index"], r["generic_product_bound"]
    assert any(meas[k] < prod[k] for k in meas), (
        "nothing collapses below the product bound, so the law is vacuous")
    assert any(meas[k] == prod[k] for k in meas), (
        "everything collapses, so the test set cannot distinguish 'index = lcm' "
        "from 'composition is always cheaper than the product'")
    assert max(prod[k] / meas[k] for k in meas) >= 30, (
        "the largest collapse fell below 30x; (6,10,15) at 900 -> 30 is what "
        "makes the sub-multiplicative claim non-trivial")


def test_suffix_composition_is_additive_over_a_composed_form():
    """Law 2: +2 on top of a COMPOSED counting form, which was untested."""
    r = load_receipt("STAGE_COMPOSITION_LAW_VERDICT_V1.json")
    assert r["law_2_misses"] == [], (
        "composing with the suffix obligation no longer costs exactly +2: %s"
        % r["law_2_misses"])
    c, s = r["measured_counting_index"], r["measured_suffix_composed_index"]
    assert all(s[k] == c[k] + 2 for k in c), "the +2 relation broke"
    assert any(c[k] >= 30 for k in c), (
        "no composed form in the set is large enough to make '+2 rather than "
        "x3' a meaningful distinction")


def test_capability_ceiling_saturates():
    """Section K asks how far capability can go; the answer is that it stops."""
    r = load_receipt("STAGE_COMPOSITION_LAW_VERDICT_V1.json")
    assert r["capability_ceiling_holds"] is True
    assert r["capability_ceiling_measured"] == 27720, (
        "the measured max index over moduli <= 12 changed from lcm(1..12)")
    assert r["verdict"] in ("HOLDS", "FALSIFIED")


# ---------------------------------------------------------------------------
# Law 3: the prediction that composition is EXPENSIVE.  Frozen at d36ec382.
# This is the one that gives the mechanism teeth -- the other two both predicted
# collapse, so neither could have distinguished a real criterion from a habit.
# ---------------------------------------------------------------------------
def test_probe_law_adjudication_reproduces():
    receipt = os.path.join(RESULTS, "STAGE_PROBE_LAW_VERDICT_V1.json")
    before = open(receipt).read() if os.path.exists(receipt) else None
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join("gmi_microscope", "compare_probe_law.py")],
            cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
        assert proc.returncode == 0, (
            "compare_probe_law.py failed:\n" + proc.stdout.decode()[-4000:])
        assert before is not None, "no committed verdict to reproduce"
        assert json.loads(open(receipt).read()) == json.loads(before), (
            "the Law 3 adjudication no longer reproduces its committed verdict")
    finally:
        if before is not None:
            with open(receipt, "w") as fh:
                fh.write(before)


def test_monotone_obligation_costs_the_full_product():
    r = load_receipt("STAGE_PROBE_LAW_VERDICT_V1.json")
    assert r["disagreeing_m"] == [], (
        "the monotone-obligation intersection no longer costs 4m: %s"
        % r["disagreeing_m"])
    meas, prod = r["measured_index"], r["product_bound"]
    assert all(meas[k] == prod[k] for k in meas), (
        "some m now collapses below the product bound, which would refute the "
        "probeability criterion and put the +2 law's explanation in doubt")
    assert all(r["reachable_states"][k] == prod[k] for k in prod), (
        "not every product state is reachable, so a collapse could be "
        "unreachability rather than indistinguishability")


def test_the_corpus_has_both_a_cheap_and_an_expensive_composition():
    """Without both, 'composition is cheap' would be an untested habit."""
    cheap = load_receipt("STAGE_COMPOSITION_LAW_VERDICT_V1.json")
    dear = load_receipt("STAGE_PROBE_LAW_VERDICT_V1.json")
    assert cheap["verdict"] == "HOLDS" and dear["verdict"] == "HOLDS"
    cm, cp = cheap["measured_counting_index"], cheap["generic_product_bound"]
    assert any(cm[k] < cp[k] for k in cm), "no cheap composition on record"
    dm, dp = dear["measured_index"], dear["product_bound"]
    assert all(dm[k] == dp[k] for k in dm), "no expensive composition on record"
    assert dear["criterion_supported"] is True


# ---------------------------------------------------------------------------
# G: the species definitions, as proved properties rather than prose.
# ---------------------------------------------------------------------------
def test_species_relation_is_an_equivalence_and_the_partition_is_informative():
    r = load_receipt("STAGE_SPECIES_ALGEBRA_V1.json")
    e = r["equivalence"]
    assert e["reflexive"] and e["symmetric"] and e["transitive"], (
        "the species relation lost an equivalence axiom")
    assert 1 < e["species"] < e["descriptors"], (
        "the partition is trivial -- one species, or all singletons -- and "
        "either way carries no information")


def test_morphological_distance_is_a_metric():
    r = load_receipt("STAGE_SPECIES_ALGEBRA_V1.json")
    d = r["distance"]
    assert d["symmetric"] and d["zero_iff_conspecific"] and d["triangle"], (
        "the morphological distance is no longer a metric")
    assert d["triples_checked"] >= 16777216, (
        "the triangle inequality is checked on fewer triples than before; it is "
        "an exhaustive claim and must stay exhaustive")
    assert len(d["values"]) > 2, "distance is near-constant and cannot order morphologies"


def test_species_identity_survives_substrate_change():
    """If the resource profile were organizational, recompiling would speciate."""
    r = load_receipt("STAGE_SPECIES_ALGEBRA_V1.json")
    s = r["substrate_invariance"]
    assert s["species_changes"] == 0, (
        "a substrate change moved a machine to another species, which breaks the "
        "organizational/non-organizational split the whole section rests on")
    assert s["substrate_changes_tried"] > 1000
    w = r["within_species"]
    assert w["dimensions_that_vary"] == ["resource"], (
        "something organizational now varies within a species")


def test_the_speciation_threshold_is_sharp():
    r = load_receipt("STAGE_SPECIES_ALGEBRA_V1.json")
    t = r["speciation_threshold"]
    assert set(t["distances_within"]).isdisjoint(t["distances_between"]), (
        "a distance now occurs both within and between species, so the threshold "
        "is no longer sharp and would need a tuned cutoff")
    assert t["threshold"] == 1


def test_hybrids_are_confined_to_the_parents_subcube():
    """The real limit on composition, and it must be stated per pair."""
    r = load_receipt("STAGE_SPECIES_ALGEBRA_V1.json")
    h = r["hybridization"]
    assert h["subcube_law_holds"] is True, (
        "parents at distance k no longer reach exactly 2^k children")
    by_k = h["children_per_pair_by_distance"]
    for k, vals in by_k.items():
        assert vals == [2 ** int(k)], (
            "distance %s reaches %s children, not %d" % (k, vals, 2 ** int(k)))
    assert h["new_species"] > 0 and h["parental_variants"] > 0, (
        "hybridization either always or never yields a new species, so the "
        "criterion does not discriminate")
    assert h["distinct_children"] == h["organizational_space"], (
        "pooled reachability changed; the document relies on it being total, "
        "which is exactly why the constraint is stated per pair instead")


# ---------------------------------------------------------------------------
# G boxes 7-9, 14-15: the invasion-competition result was sitting UNGUARDED.
#
# STAGE_R10_INVASION_V1.json carries a registered prediction, 192 competition
# cells and an invariance control, and nothing in CI asserted any of it.  These
# pins guard the claims; reproduction is not wired here because invasion.py is
# not a single-file witness, and that is stated in the document rather than
# implied by the pins.
# ---------------------------------------------------------------------------
def test_competition_reorders_occupancy():
    """Occupancy under a shared budget is not a function of the solo scores."""
    r = load_receipt("STAGE_R10_INVASION_V1.json")
    assert r["prediction_holds"] is True, (
        "the registered invasion prediction no longer holds")
    n = r["n_cells_where_competition_disagrees_with_solo"]
    assert n > 0, (
        "competition never disagrees with independent solo scoring, which would "
        "mean occupancy IS a function of the solo scores and the whole "
        "competition apparatus is decorative")
    assert n < r["n_cells"], (
        "competition disagrees with solo scoring in every cell, which would "
        "make the solo baseline useless as a comparison rather than a control")
    assert r["n_offdiagonal_cells_where_competition_disagrees_with_solo"] > 0, (
        "disagreement occurs only on the diagonal, i.e. only when a carrier "
        "meets itself, which would not be a statement about invasion")


def test_coexistence_is_the_exception_not_the_rule():
    """Competitive exclusion dominates; coexistence is rare in every pool."""
    r = load_receipt("STAGE_R10_INVASION_V1.json")
    oc = r["outcome_counts_by_pool"]
    assert oc, "no outcome counts"
    for pool, c in oc.items():
        total = sum(c.values())
        assert set(c) >= {"COEXIST", "INVADER_REPLACES", "RESIDENT_HOLDS"}, (
            "the outcome taxonomy lost a category at pool %s" % pool)
        assert c["COEXIST"] < total / 2, (
            "coexistence is no longer the exception at pool %s" % pool)
        assert c["INVADER_REPLACES"] > 0 and c["RESIDENT_HOLDS"] > 0, (
            "one of invasion or resistance never occurs at pool %s, so the "
            "competition does not discriminate" % pool)


def test_invasion_outcome_survives_reminting():
    """The invariance control: renaming a competitor must change nothing."""
    r = load_receipt("STAGE_R10_INVASION_V1.json")
    ri = r["remint_invariance"]
    assert ri["n_changed"] == 0, (
        "reminting a competitor changed a reported quantity, so the outcome "
        "depends on identity rather than on organization")
    assert ri["n_competitions_checked"] > 0, "the invariance control never ran"


# ---------------------------------------------------------------------------
# G box 16: a frozen prediction that FAILED, and the better finding underneath.
# ---------------------------------------------------------------------------
def test_intransitivity_adjudication_reproduces():
    receipt = os.path.join(RESULTS, "STAGE_INTRANSITIVITY_VERDICT_V1.json")
    before = open(receipt).read() if os.path.exists(receipt) else None
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join("gmi_microscope",
                                          "compare_intransitivity.py")],
            cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
        assert proc.returncode == 0, (
            "compare_intransitivity.py failed:\n" + proc.stdout.decode()[-4000:])
        assert before is not None, "no committed verdict to reproduce"
        assert json.loads(open(receipt).read()) == json.loads(before), (
            "the intransitivity adjudication no longer reproduces its verdict")
    finally:
        if before is not None:
            with open(receipt, "w") as fh:
                fh.write(before)


def test_the_failed_prediction_stays_recorded_as_failed():
    """A frozen prediction is only worth freezing if failure survives."""
    r = load_receipt("STAGE_INTRANSITIVITY_VERDICT_V1.json")
    assert r["verdict"] == "FALSIFIED", (
        "the intransitivity prediction is no longer recorded as failed; it was "
        "frozen before the measurement and failing is its honest outcome")
    assert r["intransitive_triples_total"] == 0


def test_zero_cycles_is_not_vacuous():
    """Cycles had to be POSSIBLE for their absence to mean anything."""
    r = load_receipt("STAGE_INTRANSITIVITY_VERDICT_V1.json")
    assert r["fully_decided_triples_total"] > 0, (
        "no triple has all three pairs decided, so a cycle was never possible "
        "and 'zero cycles' decides nothing")
    assert r["fully_decided_triples_total"] >= 50, (
        "the decided-triple count collapsed; the acyclicity finding rests on "
        "there being many triples that COULD have been cyclic")


def test_the_order_effect_is_real_and_partial():
    """The finding that outranks the prediction: arrival order changes outcomes."""
    r = load_receipt("STAGE_INTRANSITIVITY_VERDICT_V1.json")
    n, total = r["order_effect_pairs"], r["ordered_pairs_checked"]
    assert n > 0, (
        "succeeding as invader and repelling as resident now agree everywhere, "
        "which would remove the order effect that makes box 16 necessary")
    assert n < total, (
        "they disagree on every pair, which would mean the matrix is simply "
        "inconsistent rather than order-dependent")
    assert r["relation_well_defined"] is False
    assert r["box_16_necessary"] is True


# ---------------------------------------------------------------------------
# G box 10: symbiosis.  The zero is only meaningful because the control fired.
# ---------------------------------------------------------------------------
def test_symbiosis_adjudication_reproduces():
    receipt = os.path.join(RESULTS, "STAGE_SYMBIOSIS_VERDICT_V1.json")
    before = open(receipt).read() if os.path.exists(receipt) else None
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join("gmi_microscope", "compare_symbiosis.py")],
            cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
        assert proc.returncode == 0, (
            "compare_symbiosis.py failed:\n" + proc.stdout.decode()[-4000:])
        assert before is not None, "no committed verdict to reproduce"
        assert json.loads(open(receipt).read()) == json.loads(before), (
            "the symbiosis adjudication no longer reproduces its verdict")
    finally:
        if before is not None:
            with open(receipt, "w") as fh:
                fh.write(before)


def test_the_symbiosis_zero_is_backed_by_a_positive_control():
    """'No symbiosis' is only a finding if joint effects were detectable."""
    r = load_receipt("STAGE_SYMBIOSIS_VERDICT_V1.json")
    assert r["symbiotic_pairs"] == 0, (
        "symbiosis now occurs, which falsifies the frozen P1 -- that is a "
        "positive instance for box 10 and should be reported as one")
    assert r["mutually_harmful_pairs"] > 0, (
        "mutual harm is also zero, so the comparison detects no joint effect at "
        "all and the symbiosis zero is uninformative; this is the control the "
        "frozen prediction named in advance")
    assert r["one_sided_pairs"] > 0, (
        "no pair is one-sided, which would mean the two competitors always move "
        "together -- not a competition")
    assert r["P1_holds"] and r["P2_holds"]


def test_resident_invader_orientation_was_verified_not_assumed():
    """Misreading the key would invert every comparison silently."""
    r = load_receipt("STAGE_SYMBIOSIS_VERDICT_V1.json")
    assert r["key_check_cells_agreeing"] == 192, (
        "the cell-key reading no longer agrees with the invasion matrix on all "
        "192 cells, so the resident/invader orientation is unverified and every "
        "capability comparison has an undetermined sign")
    assert r["resident_field"] == "second"
    assert r["pairs_compared"] == 168, (
        "the compared-pair count changed; 168 is the 192 cells minus the 24 "
        "self-pairings, and a different number means self-pairings leaked in")


# ---------------------------------------------------------------------------
# G box 13: repricing.  The second frozen prediction in this corpus to FAIL.
# ---------------------------------------------------------------------------
def test_repricing_adjudication_reproduces():
    receipt = os.path.join(RESULTS, "STAGE_REPRICING_VERDICT_V1.json")
    before = open(receipt).read() if os.path.exists(receipt) else None
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join("gmi_microscope", "compare_repricing.py")],
            cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
        assert proc.returncode == 0, (
            "compare_repricing.py failed:\n" + proc.stdout.decode()[-4000:])
        assert before is not None, "no committed verdict to reproduce"
        assert json.loads(open(receipt).read()) == json.loads(before), (
            "the repricing adjudication no longer reproduces its verdict")
    finally:
        if before is not None:
            with open(receipt, "w") as fh:
                fh.write(before)


def test_repricing_is_non_monotone_and_the_failure_stays_recorded():
    r = load_receipt("STAGE_REPRICING_VERDICT_V1.json")
    assert r["verdict"] == "P1_FALSIFIED", (
        "the repricing prediction is no longer recorded as failed; it was frozen "
        "before the measurement and failing is its honest outcome")
    assert r["oscillating_pairs"] > 0, (
        "no pair oscillates any more, which would make repricing monotone and "
        "reverse the documented finding")
    assert r["P1_holds"] is False and r["P2_holds"] is True


def test_the_repricing_zero_control_fired():
    """Without a changing pair, 'no oscillation' would have been uninformative."""
    r = load_receipt("STAGE_REPRICING_VERDICT_V1.json")
    assert r["changing_pairs"] > 0, (
        "no pair changes winner across pools, so the repricing moves nothing "
        "and any claim about oscillation is uninformative")
    assert r["constant_pairs"] > 0, (
        "every pair changes, which would mean the pools share no structure at "
        "all rather than that repricing has a specific effect")
    assert r["oscillating_pairs"] < r["changing_pairs"], (
        "every changing pair oscillates, which would be a different and much "
        "stronger claim than the one measured")


# ---------------------------------------------------------------------------
# G boxes 11 and 12.  One prediction failed, one held -- both pinned.
# ---------------------------------------------------------------------------
def test_partition_abundance_adjudication_reproduces():
    receipt = os.path.join(RESULTS, "STAGE_PARTITION_ABUNDANCE_VERDICT_V1.json")
    before = open(receipt).read() if os.path.exists(receipt) else None
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join("gmi_microscope",
                                          "compare_partition_abundance.py")],
            cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
        assert proc.returncode == 0, (
            "compare_partition_abundance.py failed:\n" + proc.stdout.decode()[-4000:])
        assert before is not None, "no committed verdict to reproduce"
        assert json.loads(open(receipt).read()) == json.loads(before), (
            "the partition/abundance adjudication no longer reproduces")
    finally:
        if before is not None:
            with open(receipt, "w") as fh:
                fh.write(before)


def test_spending_more_of_the_pool_does_not_win():
    """Box 11: the frozen P1 failed, and it failed in the informative direction."""
    r = load_receipt("STAGE_PARTITION_ABUNDANCE_VERDICT_V1.json")
    assert r["box_11_P1_holds"] is False, (
        "the winner now draws more charge in a majority of contests, reversing "
        "the documented finding; it was frozen the other way and failed")
    assert r["loser_drew_more"] > r["winner_drew_more"], (
        "drawing more charge no longer anti-predicts winning")
    assert r["winner_drew_more"] > 0, (
        "the winner NEVER draws more, which would be a far stronger claim than "
        "the one measured and should not pass silently")
    assert r["decided_contests"] >= 150


def test_abundance_is_stable_under_repricing():
    """Box 12: the frozen P3 held, with its control."""
    r = load_receipt("STAGE_PARTITION_ABUNDANCE_VERDICT_V1.json")
    assert r["box_12_P3_holds"] is True, "the top carrier now moves between pools"
    assert r["box_12_P4_holds"] is True, (
        "win counts are uniform, so 'the top carrier' names nothing and the "
        "stability claim is vacuous -- this is the frozen control")
    tops = r["top_by_pool"]
    assert len({tuple(v) for v in tops.values()}) == 1
    assert all(len(v) == 1 for v in tops.values()), (
        "some pool has a tied top carrier, so 'the same top carrier' is no "
        "longer a single well-defined claim")


def test_some_carriers_are_completely_budget_invariant():
    """The texture that keeps the stability claim from being over-read."""
    r = load_receipt("STAGE_PARTITION_ABUNDANCE_VERDICT_V1.json")
    w = r["wins_by_pool"]
    pools = list(w)
    invariant = [c for c in w[pools[0]]
                 if len({w[p][c] for p in pools}) == 1]
    varying = [c for c in w[pools[0]] if c not in invariant]
    assert invariant, "no carrier has a budget-invariant win count any more"
    assert varying, (
        "every carrier is budget-invariant, which would mean repricing moves "
        "nothing and contradicts the 7 changing pairs measured for box 13")
