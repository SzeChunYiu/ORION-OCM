"""KSO M2b — registered quadratic generator/oracle and the algebra source (``kso_algebra_quadratic_v1.py``)."""

from __future__ import annotations

import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_algebra_quadratic_v1.py"


def _load():
    spec = importlib.util.spec_from_file_location("kso_algebra_quadratic_v1", MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


def test_self_test_pins(mod):
    res = mod.self_test()
    assert res["source_atoms"] == 23 and res["instances"] == 30 and res["worked_examples_agree"] == 3
    assert res["instance_ids_sha256"] == "75de2299f6c9c8e5493a03df3746a9eade8595d6da5254f33e4a636061888a17"
    assert res["planted_wrong_root_rejected_by_vieta"] == 1


def test_source_is_well_formed_and_constraints_are_explicit_atoms(mod):
    src = mod.source_atoms()
    ids = {a["id"] for a in src["atoms"]}
    for needed in ("con:a_nonzero", "con:a_zero", "con:b_nonzero", "con:delta_pos", "con:delta_zero", "con:delta_neg", "proc:linear", "proc:quadratic_formula", "proc:complete_square", "proc:factor"):
        assert needed in ids
    assert {a["type"] for a in src["atoms"]} == {"definition", "representation", "constraint", "procedure", "worked_example"}
    assert all(a["warrant"]["root_warrant"] == "EXACT_CHECKER" for a in src["atoms"] if a["type"] == "procedure" and a["produces"])


def test_oracle_cases_and_vieta(mod):
    I = mod.Instance
    o = mod.oracle
    assert o(I("t", "x", Fraction(1), Fraction(-5), Fraction(6))).roots == ("3", "2")
    assert o(I("t", "x", Fraction(1), Fraction(-4), Fraction(4))).case == "Delta==0"
    assert o(I("t", "x", Fraction(1), Fraction(1), Fraction(1))).real_root_count == 0
    assert o(I("t", "x", Fraction(1), Fraction(0), Fraction(-2))).case == "Delta>0 irrational"
    assert o(I("t", "x", Fraction(0), Fraction(2), Fraction(-4))).roots == ("2",)
    assert o(I("t", "x", Fraction(0), Fraction(0), Fraction(1))).status == "CANNOT_CHECK"


def test_two_oracle_implementations_agree_on_every_dev_instance(mod):
    pairs, _ = mod.generate_split("dev", "ALGEBRA-DEV-20260904", 5)
    for inst, ans in pairs:
        ans2 = mod.oracle_independent(inst)
        assert (ans.case, ans.real_root_count, ans.rational_roots) == (ans2.case, ans2.real_root_count, ans2.rational_roots), inst.instance_id


def test_generation_is_byte_reproducible(mod):
    a, ra = mod.generate_split("dev", "ALGEBRA-DEV-20260904", 2)
    b, rb = mod.generate_split("dev", "ALGEBRA-DEV-20260904", 2)
    assert [(i.instance_id, i.a, i.b, i.c) for i, _ in a] == [(i.instance_id, i.a, i.b, i.c) for i, _ in b] and ra == rb


def test_unregistered_precondition_is_cannot_check(mod, tmp_path, monkeypatch):
    src = json.loads(mod.SOURCE.read_text(encoding="utf-8"))
    src["atoms"][0]["preconditions"] = ["def:nope"]
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(src), encoding="utf-8")
    monkeypatch.setattr(mod, "SOURCE", bad)
    with pytest.raises(mod.CannotCheck):
        mod.source_atoms()


def test_cli_exit_codes(mod, monkeypatch, capsys):
    assert mod.main(["--self-test"]) == 0
    monkeypatch.setattr(mod, "self_test", lambda: (_ for _ in ()).throw(mod.CannotCheck("planted")))
    assert mod.main([]) == 2
    monkeypatch.setattr(mod, "self_test", lambda: (_ for _ in ()).throw(AssertionError("planted")))
    assert mod.main([]) == 1
    capsys.readouterr()
