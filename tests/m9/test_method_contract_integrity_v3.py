"""A composed work method cannot spend first and check its budget afterwards."""
from dataclasses import replace

from ocm.kso.types import Authority
from ocm.kso.warrant import WarrantProfile
from ocm.work.contracts import Operator, Skill, TaskContract
from ocm.work.methods import run_skill


def setup(checker=lambda state, hidden: state["value"] == 1, budget=1):
    calls = []
    def backend(state):
        calls.append(1)
        return {"value": 1}
    op = Operator("op", "1", "test", lambda s: True, backend, (), lambda s: True, lambda s: True)
    skill = Skill("skill", ("step",), {"step": "op"}, "test", WarrantProfile.one())
    contract = TaskContract("task", "1", "test", {"value": 0}, "value=1", ("op",), (), ("value",), {}, budget, 0, Authority(), checker)
    return calls, op, skill, contract


def test_budget_is_checked_before_operator_runs():
    calls, op, skill, contract = setup(budget=0)
    result = run_skill(skill, {"op": op}, contract)
    assert not result.success and not calls and result.cost == 0


def test_truthy_cannot_check_is_not_a_success():
    _, op, skill, contract = setup(checker=lambda s, h: "CANNOT_CHECK")
    assert run_skill(skill, {"op": op}, contract).success is False


def test_checker_exception_returns_an_explicit_failed_method():
    def checker(s, h):
        raise RuntimeError("checker unavailable")
    _, op, skill, contract = setup(checker=checker)
    assert run_skill(skill, {"op": op}, contract).success is False


def test_one_shot_revocation_is_applied_to_each_operator():
    calls, op, skill, contract = setup()
    op = replace(op, warrant=WarrantProfile.of({"revoked"}))
    assert not run_skill(skill, {"op": op}, contract, revoked=iter(["revoked"])).success
    assert not calls
