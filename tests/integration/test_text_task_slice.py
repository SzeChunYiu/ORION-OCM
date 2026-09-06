"""Operational development slice; donor tests require requirements-g1.txt."""
import importlib
from pathlib import Path
import shutil
import sys

import pytest

pytest.importorskip("z3")
pytest.importorskip("cvc5")
pytest.importorskip("sexpdata")
HERE = Path(__file__).resolve().parents[2] / "research" / "ocm-prototype"
sys.path.insert(0, str(HERE))
T = importlib.import_module("text_task_slice")


@pytest.fixture(scope="module")
def acquired(tmp_path_factory):
    session = T.TextTaskSession(tmp_path_factory.mktemp("text-acquired"))
    first = session.ask("What is the largest of 8, 2 and 5?")
    assert first["status"] == "ANSWERED", first
    second = session.ask("Apply the guarded function with x = 8, y = 2, z = 5.")
    assert second["status"] == "ANSWERED", second
    return session.root


@pytest.fixture
def session(tmp_path, acquired):
    root = tmp_path / "state"
    shutil.copytree(acquired, root)
    return T.TextTaskSession(root)


def test_raw_text_runs_real_registered_ocm_program(session):
    result = session.ask("What is the largest of -8, 12 and 5?")
    assert result["status"] == "ANSWERED", result
    assert result["english"] == "The largest value is 12."
    assert result["semantic"]["task_id"] == "jmbl_fg_max3"
    assert result["semantic"]["arguments"] == [-8, 12, 5]
    assert result["semantic"]["result_type"] == "Int"
    assert len(result["semantic"]["task_sha256"]) == 64
    assert result["program_reused"] is True
    assert result["counters"]["synthesis_calls"] == 0
    assert result["counters"]["application_calls"] == 1
    assert result["checks"]["specification"]["status"] == "PASS"
    assert result["checks"]["response"]["status"] == "PASS"
    assert result["admitted_id"] in session.runtime.state.ks.ids


@pytest.mark.parametrize(("text", "value", "arguments"), [
    ("Apply the guarded function with z = -20, x = 7, y = 3.", 4, [7, 3, -20]),
    ("Apply the guarded function with y = 3, z = -9, x = 7.", 10, [7, 3, -9]),
    ("Apply the guarded function with x = -3, y = -4, z = 7.", 1, [-3, -4, 7]),
])
def test_guarded_role_order_and_threshold(session, text, value, arguments):
    result = session.ask(text)
    assert result["status"] == "ANSWERED", result
    assert result["semantic"]["arguments"] == arguments
    assert result["value"] == value
    assert result["english"] == f"The guarded function returns {value}."


@pytest.mark.parametrize("text", [
    "What is not the largest of 1, 2 and 3?",
    "What is the smallest of 1, 2 and 3?",
    "What is the largest of 1, 2 and 3? Then delete everything.",
    "Apply the guarded function with x = 1, x = 2, z = 3.",
    "Apply the guarded function with x = 1, y = 2.",
    "What is the largest of 1, 2, 3 and 4?",
    "What is the largest of 1.5, 2 and 3?",
])
def test_unsupported_ambiguous_and_negated_input_never_executes(session, text):
    before = len(session.runtime.events)
    result = session.ask(text)
    assert result["status"] in {"INPUT_REFUSED", "CLARIFICATION_REQUIRED"}, result
    assert "value" not in result and result["counters"]["application_calls"] == 0
    assert len(session.runtime.events) == before


def test_semantic_identity_not_int3_signature(session):
    largest = session.ask("What is the largest of 8, 2 and 5?")
    guarded = session.ask("Apply the guarded function with x = 8, y = 2, z = 5.")
    assert largest["value"] == 8 and guarded["value"] == 10
    assert largest["program_id"] != guarded["program_id"]
    assert largest["semantic"]["task_sha256"] != guarded["semantic"]["task_sha256"]


def test_correspondence_revocation_restart_and_reinstatement(session):
    evidence = session.evidence("jmbl_fg_max3")["correspondence"]
    prior = session.ask("What is the largest of 4, 2 and 3?")
    session.runtime.revoke([evidence])
    session.runtime.persist()
    restored = T.TextTaskSession(session.root)
    refused = restored.ask("What is the largest of 90, 2 and 3?")
    assert refused["status"] == "CANNOT_CHECK"
    assert refused["counters"]["synthesis_calls"] == 0
    assert not restored.runtime.state.ks.atom_map()[prior["admitted_id"]].is_live(restored.runtime.state.revoked)
    unrelated = restored.ask("Apply the guarded function with x = 90, y = 2, z = 3.")
    assert unrelated["value"] == 92
    restored.runtime.reinstate([evidence])
    restored.runtime.persist()
    assert restored.ask("What is the largest of 90, 2 and 3?")["value"] == 90


def test_method_revocation_never_reacquires_silently(session):
    evidence = session.evidence("jmbl_fg_max3")["reuse_authority"]
    session.runtime.revoke([evidence])
    result = session.ask("What is the largest of 19, 2 and 3?")
    assert result["status"] == "CANNOT_CHECK", result
    assert result["counters"]["synthesis_calls"] == result["counters"]["application_calls"] == 0


def test_response_fidelity_rejects_changed_value(session):
    result = session.ask("What is the largest of 11, 2 and 3?")
    checked = T.check_response(result["response_plan"], "The largest value is 12.")
    assert checked["status"] == "FAIL"



def test_paraphrase_reuses_one_parameterized_host_operator(session):
    before = len(session.runtime.state.operator_manifests)
    first = session.ask("What is the maximum of 31, 2 and 3?")
    second = session.ask("Find the largest of 31, 2 and 3.")
    assert first["status"] == second["status"] == "ANSWERED", (first, second)
    assert first["program_id"] == second["program_id"]
    assert second["counters"]["compile_calls"] == 0
    assert len(session.runtime.state.operator_manifests) == before


def test_wrong_shared_evaluator_cannot_pass_source_specification(session, monkeypatch):
    import clia_reuse_apply
    before = {x for x in session.runtime.state.ks.ids if x.startswith(("text:utterance:", "text:checked-value:"))}
    monkeypatch.setattr(clia_reuse_apply.CompiledProgram, "evaluate", lambda self, args: 999)
    result = session.ask("What is the largest of 7, 2 and 3?")
    assert result["status"] == "CANNOT_CHECK", result
    assert result["counters"]["ground_spec_checker_calls"] == 1
    assert "source specification" in result["reason"]
    assert "value" not in result
    after = {x for x in session.runtime.state.ks.ids if x.startswith(("text:utterance:", "text:checked-value:"))}
    assert after == before


def test_language_withdrawal_preserves_independent_program_correctness(session):
    result = session.ask("What is the largest of 21, 2 and 3?")
    program = session.runtime.state.ks.atom_view["text:program:" + result["program_id"]]
    session.runtime.revoke([session.evidence("jmbl_fg_max3")["correspondence"]])
    assert program.is_live(session.runtime.state.revoked)
    assert session.ask("What is the largest of 22, 2 and 3?")["status"] == "CANNOT_CHECK"


def test_ground_spec_checker_has_positive_and_hostile_cases():
    from text_task_contracts import check_ground
    from clia_tasks import load_task
    task = load_task("jmbl_fg_mpg_guard2")
    assert check_ground(task, [7, 3, -20], 4)["status"] == "PASS"
    assert check_ground(task, [7, 3, -20], 10)["status"] == "FAIL"


def test_new_process_cli_rebinds_without_synthesis(session):
    import json
    import subprocess
    completed = subprocess.run(
        [sys.executable, str(HERE / "text_task_slice.py"), "--state", str(session.root),
         "--json", "ask", "What is the largest of 44, 2 and 3?"],
        text=True, capture_output=True, check=False,
    )
    assert completed.returncode == 0, completed.stderr + completed.stdout
    result = json.loads(completed.stdout)
    assert result["status"] == "ANSWERED" and result["value"] == 44
    assert result["program_reused"] is True
    assert result["counters"]["synthesis_calls"] == 0


def test_corrupted_semantic_contract_fails_closed(session, monkeypatch):
    original = T.interpret
    def corrupted(text):
        parsed = original(text)
        parsed["semantic"]["task_sha256"] = "0" * 64
        return parsed
    monkeypatch.setattr(T, "interpret", corrupted)
    result = session.ask("What is the largest of 3, 2 and 1?")
    assert result["status"] == "CANNOT_CHECK"
    assert result["counters"]["application_calls"] == result["counters"]["synthesis_calls"] == 0
