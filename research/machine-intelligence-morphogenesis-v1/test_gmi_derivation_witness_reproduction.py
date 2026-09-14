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
    "credit_assignment_witness.py": "STAGE_CREDIT_ASSIGNMENT_V1.json",
    "continual_regimes_witness.py": "STAGE_CONTINUAL_REGIMES_V1.json",
    "exemplar_parametric_witness.py": "STAGE_EXEMPLAR_PARAMETRIC_V1.json",
    "linear_family_witness.py": "STAGE_LINEAR_FAMILY_V1.json",
    "finite_state_witness.py": "STAGE_FINITE_STATE_V1.json",
    "goal_formation_witness.py": "STAGE_GOAL_FORMATION_V1.json",
    "hierarchy_overhead_witness.py": "STAGE_HIERARCHY_OVERHEAD_V1.json",
    "hierarchy_witness.py": "STAGE_HIERARCHY_WITNESS_V1.json",
    "interference_witness.py": "STAGE_INTERFERENCE_V1.json",
    "lesion_witness.py": "STAGE_COMPONENT_LESIONS_V1.json",
    "memory_regime_witness.py": "STAGE_MEMORY_REGIME_WITNESS_V1.json",
    "neural_architecture_witness.py": "STAGE_NEURAL_ARCHITECTURE_V1.json",
    "metacognition_witness.py": "STAGE_METACOGNITION_V1.json",
    "pedagogy_witness.py": "STAGE_PEDAGOGY_V1.json",
    "planning_stop_witness.py": "STAGE_PLANNING_STOP_V3.json",
    "recovery_objective_witness.py": "STAGE_RECOVERY_OBJECTIVE_V1.json",
    "replanning_witness.py": "STAGE_REPLANNING_V1.json",
    "simulation_worth_witness.py": "STAGE_SIMULATION_WORTH_V1.json",
    "social_cognition_witness.py": "STAGE_SOCIAL_COGNITION_V1.json",
    "social_strategic_witness.py": "STAGE_SOCIAL_STRATEGIC_V1.json",
    "subgoal_witness.py": "STAGE_SUBGOAL_WITNESS_V1.json",
    "update_law_witness.py": "STAGE_UPDATE_LAW_V1.json",
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
