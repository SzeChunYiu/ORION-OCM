"""M2b V3 — procedures as step-hyperpath data, label-only gating, threshold as exit code.

Every rule below is exercised as a planted failure AND a no-alarm control.  The expensive clean run
(30 instances, five plants, SymPy checker on 90 root claims) is computed once per module.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "research" / "orion-machine" / "reference"

sympy = pytest.importorskip("sympy")  # the EXACT_CHECKER channel is the only warrant; without it nothing here is decidable


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


v3 = _load("kso_m2b_algebra_v3", REF / "kso_m2b_algebra_v3.py")
alg = v3.alg


@pytest.fixture(scope="module")
def clean_run():
    return v3.run(per_family=5, with_plants=True)


# ---- freeze discipline ------------------------------------------------------------------------

def test_design_freeze_pins_every_producer():
    d = v3.check_design_drift()
    assert set(d["pins"]) == {"source_sha256", "generator_sha256", "module_sha256", "checker_sha256"}
    assert d["threshold"] == {"n": 30, "min_exact": 30}


def test_design_drift_is_cannot_check(tmp_path, monkeypatch):
    frozen = json.loads(v3.DESIGN_V3.read_text())
    frozen["v3"]["source_sha256"] = "0" * 64
    bad = tmp_path / "KSO_M2B_DESIGN_V3.json"
    bad.write_text(json.dumps(frozen))
    monkeypatch.setattr(v3, "DESIGN_V3", bad)
    with pytest.raises(v3.CannotCheck, match="DESIGN_DRIFT"):
        v3.check_design_drift()


# ---- the source is data ---------------------------------------------------------------------------

def test_procedures_are_hyperpaths_of_registered_steps():
    src = alg.source_atoms()
    by_id = {a["id"]: a for a in src["atoms"]}
    procs = [a for a in src["atoms"] if a["type"] == "procedure" and a.get("hyperpath")]
    assert len(procs) == 4
    for p in procs:
        for s in p["hyperpath"]:
            assert by_id[s]["type"] == "step" and by_id[s]["operation"] in src["operations"]
    assert not hasattr(v3, "apply_procedure"), "per-procedure Python must not exist"


def test_interpreter_knows_nothing_about_quadratics():
    text = (REF / "kso_m2b_algebra_v3.py").read_text()
    body = text.split("def interpret_hyperpath", 1)[1].split("\ndef ", 1)[0]
    for forbidden in ("sqrt(", "b**2", "4*a*c", "2*a"):
        assert forbidden not in body, f"the generic interpreter carries domain algebra: {forbidden!r}"


# ---- (a) corrupt a step in the source -----------------------------------------------------------

def test_plant_a_corrupt_step_changes_root_and_is_caught(clean_run):
    p = clean_run["plants"]["a_corrupt_step_in_the_source"]
    assert p["mutation_landed__root_differs_from_clean"] is True
    assert p["oracle_disagrees"] is True and p["attribution"] == "COMPOSE"
    assert p["exact_checker_invalid"] is True
    assert p["invalid_procedures"] == ["proc:quadratic_formula"], "the corruption must be local to the corrupted step"
    assert "proc:complete_square" in p["still_warranted_procedures"]
    assert p["CAUGHT"] is True


def test_plant_a_is_a_real_source_mutation():
    src = v3.corrupted_source()
    step = next(a for a in src["atoms"] if a["id"] == "step:qf:1")
    assert step["template"] == "b**2 - 3*a*c"
    with pytest.raises(AssertionError, match="no-op"):
        v3.corrupted_source(template=next(a for a in alg.source_atoms()["atoms"] if a["id"] == "step:qf:1")["template"])


# ---- (b) gating is labels only ------------------------------------------------------------------

def test_no_conditional_decides_applicability():
    text = (REF / "kso_m2b_algebra_v3.py").read_text()
    atomize = text.split("def atomize_labels", 1)[1].split("\ndef ", 1)[0]
    assert "proc:" not in atomize, "atomize_labels must decide WHICH CASE HOLDS, never which procedure applies"


def test_plant_b_one_label_flip_makes_factoring_fire_and_is_caught(clean_run):
    p = clean_run["plants"]["b_flip_one_constraint_label"]
    one = p["one_flip_irrational"]
    assert one["proc_factor_fired"] and one["exact_checker_invalid"] and one["CAUGHT"]
    assert "not in the declared domain Q" in one["reason"]
    two = p["case_licence_flip_complex"]
    assert two["proc_factor_fired"] and two["exact_checker_invalid"] and two["CAUGHT"]
    assert all("I*sqrt" in r for r in two["root_claimed_over_Q"])


def test_no_alarm_factoring_never_fires_where_it_must_not(clean_run):
    na = clean_run["no_alarm_controls"]
    assert na["proc_factor_never_fires_on_irrational"] and na["proc_factor_never_fires_on_complex"]
    assert na["nothing_fires_on_no_equation"]
    assert na["zero_invalid_root_claims"] and na["zero_cannot_check_root_claims"]


def test_case_atoms_discriminate_on_a_complex_instance():
    pop, by_id = v3.populate_from_source()
    inst = alg.Instance("cpx", "COMPLEX_PAIR", Fraction(1), Fraction(1), Fraction(1))
    row = v3.solve_instance(pop, by_id, inst, alg.oracle(inst), run_checker=False)
    assert "proc:factor" not in row["fired_procedures"]
    assert set(row["fired_procedures"]) == {"proc:quadratic_formula", "proc:complete_square"}
    assert "con:delta_neg" not in row["query_revoked_constraints"]
    assert {"con:delta_pos", "con:delta_zero", "con:rational_roots"} <= set(row["query_revoked_constraints"])


# ---- (c) the threshold is the exit code ---------------------------------------------------------

def test_plant_c_three_instance_corruption_exits_1(clean_run):
    p = clean_run["plants"]["c_three_instance_corruption_exits_1"]
    assert p["n"] == 3 and p["exact"] == 0 and p["exit_code_would_be"] == 1 and p["CAUGHT"]


def test_main_exit_codes_are_the_gate(tmp_path, capsys):
    assert v3.main(["--plant-corrupt-step", "--per-family", "5"]) == 1
    out = json.loads(capsys.readouterr().out)
    assert out["G1_exact_vs_oracle"]["met"] is False and out["G1_exact_vs_oracle"]["exact"] < 30


def test_clean_run_meets_threshold_and_exit_0(clean_run, tmp_path, capsys):
    g = clean_run["G1_exact_vs_oracle"]
    assert g == {**g, "n": 30, "exact": 30, "met": True, "attributions": {}}
    assert clean_run["terminal"] == "M2B_V3_SOLVED_FROM_THE_SOURCE_AND_WARRANTED"
    assert clean_run["G6_exact_checker_verdicts"] == {"VALID": 90, "INVALID": 0, "CANNOT_CHECK": 0}


# ---- (d) oracle disagreement is CANNOT_CHECK --------------------------------------------------

def test_plant_d_disagreement_raises_and_names_the_instance(clean_run):
    p = clean_run["plants"]["d_oracle_disagreement_is_cannot_check"]
    assert p["CAUGHT"] and p["exit_code_would_be"] == 2 and "dev-COMPLEX_PAIR-000" in p["instance_named"]


def test_no_alarm_clean_split_never_raises_and_rejections_are_split():
    pairs, rejects = alg.generate_split("dev", "ALGEBRA-DEV-20260904", 5)
    assert len(pairs) == 30
    assert set(rejects["COMPLEX_PAIR"]) == {"proposal_declined", "family_mismatch"}


# ---- (e) out-of-range is a typed rejection at both ends ---------------------------------------

def test_plant_e_out_of_range_rejected_at_oracle_and_solver(clean_run):
    p = clean_run["plants"]["e_out_of_range_is_typed_rejection"]
    assert p["CAUGHT"] and p["at_oracle"] and p["at_solver"]


def test_no_alarm_every_generated_instance_is_in_range():
    pairs, _ = alg.generate_split("dev", "ALGEBRA-DEV-20260904", 5)
    for inst, _ in pairs:
        alg.check_registered_range(inst)


# ---- the template grammar is closed -------------------------------------------------------------

@pytest.mark.parametrize("bad", ["__import__('os')", "a if b else c", "a + Z", "a ** b", "1.5*a", "max(a, b)"])
def test_unregistered_templates_are_typed_rejections(bad):
    env = {"a": alg.Exact(Fraction(1)), "b": alg.Exact(Fraction(2)), "c": alg.Exact(Fraction(3))}
    with pytest.raises(alg.TemplateRejection):
        alg.eval_template(bad, env)


def test_receipt_on_disk_matches_a_fresh_run_body(clean_run):
    on_disk = json.loads((ROOT / "research/orion-machine/results/KSO_M2B_ALGEBRA_RECEIPT_V3.json").read_text())
    fresh = json.loads(json.dumps(clean_run, default=v3._default))
    for d in (on_disk, fresh):
        d.pop("provenance", None)
    assert on_disk == fresh
