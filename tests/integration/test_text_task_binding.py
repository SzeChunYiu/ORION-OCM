"""Proposal mutation cannot alter the accepted task or warrant a different speech act."""
import importlib
from pathlib import Path
import sys

import pytest

pytest.importorskip("z3")
pytest.importorskip("cvc5")
pytest.importorskip("sexpdata")
HERE = Path(__file__).resolve().parents[2] / "research" / "ocm-prototype"
sys.path.insert(0, str(HERE))
T = importlib.import_module("text_task_slice")


@pytest.fixture
def session(tmp_path):
    return T.TextTaskSession(tmp_path / "state")


@pytest.mark.parametrize("field", ["task", "value", "arguments", "support_atoms", "schema"])
def test_response_plan_cannot_change_checked_task_or_support(session, monkeypatch, field):
    from clia_tasks import load_task
    before = {x for x in session.runtime.state.ks.ids if x.startswith("text:utterance:")}
    original = T.response_plan
    def corrupt(semantic, value, support):
        plan = original(semantic, value, support)
        if field == "task":
            plan["task_id"] = "jmbl_fg_mpg_guard2"
            plan["task_sha256"] = load_task(plan["task_id"])["task_sha256"]
        elif field == "value":
            plan["value"] = value + 1
        elif field == "arguments":
            plan["arguments"][0] += 1
        elif field == "support_atoms":
            plan["support_atoms"] = ["unrelated:claim"]
        else:
            plan["schema"] = "different-semantics"
        return plan
    monkeypatch.setattr(T, "response_plan", corrupt)
    result = session.ask("What is the largest of 8, 2 and 5?")
    assert result["status"] == "CANNOT_CHECK", result
    assert "response plan" in result["reason"]
    assert result["semantic"]["arguments"] == [8, 2, 5]
    assert {x for x in session.runtime.state.ks.ids if x.startswith("text:utterance:")} == before


def test_realizer_cannot_change_the_checked_speech_act(session, monkeypatch):
    from clia_tasks import load_task
    original = T.realize
    def corrupt(plan):
        plan["task_id"] = "jmbl_fg_mpg_guard2"
        plan["task_sha256"] = load_task(plan["task_id"])["task_sha256"]
        return original(plan)
    monkeypatch.setattr(T, "realize", corrupt)
    result = session.ask("What is the largest of 8, 2 and 5?")
    assert result["status"] == "CANNOT_CHECK", result
    assert not any(x.startswith("text:utterance:") for x in session.runtime.state.ks.ids)


def test_backend_cannot_change_the_accepted_input_tuple(session, monkeypatch):
    from clia_reuse_apply import CompiledProgram
    from g1_field import payload
    original = CompiledProgram.apply
    def corrupt(self, request):
        request["arguments"][0] = 999
        return original(self, request)
    monkeypatch.setattr(CompiledProgram, "apply", corrupt)
    result = session.ask("What is the largest of 7, 2 and 3?")
    assert result["status"] == "CANNOT_CHECK", result
    assert result["semantic"]["arguments"] == [7, 2, 3]
    assert not any(x.startswith(("text:utterance:", "text:checked-value:")) for x in session.runtime.state.ks.ids)
    requests = [x for x in session.runtime.state.ks.ids if x.startswith("text:request:")]
    assert len(requests) == 1
    assert payload(session.runtime.state.ks, requests[0])["semantic"]["arguments"] == [7, 2, 3]


def test_backend_revocation_cannot_leave_a_committed_candidate_trace(session, monkeypatch):
    from clia_reuse_apply import CompiledProgram
    original = CompiledProgram.apply
    def revoke_then_apply(self, request):
        session.runtime.revoke([session.evidence("jmbl_fg_max3")["specification"]])
        return original(self, request)
    monkeypatch.setattr(CompiledProgram, "apply", revoke_then_apply)
    result = session.ask("What is the largest of 7, 2 and 3?")
    assert result["status"] == "CANNOT_CHECK", result
    # Acquisition has an earlier valid commitment. The application must not.
    assert result["traces"][-1]["stages"][-1]["status"] != "PASS"
    assert not any(x.startswith(("text:utterance:", "text:checked-value:")) for x in session.runtime.state.ks.ids)
