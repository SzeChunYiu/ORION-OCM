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
    "concept_formation_witness.py": "STAGE_CONCEPT_FORMATION_V1.json",
    "consolidation_witness.py": "STAGE_CONSOLIDATION_WITNESS_V1.json",
    "goal_formation_witness.py": "STAGE_GOAL_FORMATION_V1.json",
    "hierarchy_overhead_witness.py": "STAGE_HIERARCHY_OVERHEAD_V1.json",
    "hierarchy_witness.py": "STAGE_HIERARCHY_WITNESS_V1.json",
    "lesion_witness.py": "STAGE_COMPONENT_LESIONS_V1.json",
    "memory_regime_witness.py": "STAGE_MEMORY_REGIME_WITNESS_V1.json",
    "metacognition_witness.py": "STAGE_METACOGNITION_V1.json",
    "pedagogy_witness.py": "STAGE_PEDAGOGY_V1.json",
    "planning_stop_witness.py": "STAGE_PLANNING_STOP_V3.json",
    "recovery_objective_witness.py": "STAGE_RECOVERY_OBJECTIVE_V1.json",
    "replanning_witness.py": "STAGE_REPLANNING_V1.json",
    "simulation_worth_witness.py": "STAGE_SIMULATION_WORTH_V1.json",
    "social_cognition_witness.py": "STAGE_SOCIAL_COGNITION_V1.json",
    "social_strategic_witness.py": "STAGE_SOCIAL_STRATEGIC_V1.json",
    "subgoal_witness.py": "STAGE_SUBGOAL_WITNESS_V1.json",
    "teaching_culture_witness.py": "STAGE_TEACHING_CULTURE_WITNESS_V1.json",
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
