"""Current engineering comparator: shared A/E inputs, no scientific promotion."""
from __future__ import annotations

import pytest

from ocm.lifetime import machine as MC
from ocm.lifetime import phases as PH
from ocm.kso.warrant import WarrantProfile as WP
from ocm.work import contracts as C, envs as E


@pytest.mark.parametrize("arm_class", [MC.PersistentOCM, MC.WholeSystemParent])
def test_named_reports_correction_and_restart_preserve_attribution(tmp_path, arm_class):
    arm = arm_class(tmp_path)
    assert "Alice says" in arm.say("the robot opened the door", speaker="Alice")
    assert "Bob says not" in arm.say("the robot did not open the door", speaker="Bob")
    assert "Contradictory" in arm.say("did the robot open the door")
    assert "supersedes" in arm.say("correction, the robot opened the door", speaker="Bob")
    assert "Alice said so" in arm.say("did the robot open the door")
    arm.say("__restart__")
    assert "Alice said so" in arm.say("did the robot open the door")
    assert "Unknown" in arm.say("did the door open the robot")


@pytest.mark.parametrize("arm_class", [MC.PersistentOCM, MC.WholeSystemParent])
def test_shared_lesson_revocation_reinstatement_and_relearning(tmp_path, arm_class):
    arm = arm_class(tmp_path)
    use, ask = "the girl held the lantern", "did the girl hold the lantern"
    assert "cannot interpret" in arm.say(use)
    arm.say("teach: lantern = lamp")
    first = arm.last_lesson
    assert "Noted" in arm.say(use)
    assert "said so" in arm.say(ask)
    arm.say("__restart__")
    assert "said so" in arm.say(ask)
    arm.say("__revoke_last_lesson__")
    assert "cannot interpret" in arm.say(use)
    assert arm.say("is paris in france").startswith("Yes.")
    arm.say("__restart__")
    assert "cannot interpret" in arm.say(use)
    arm.say(f"reinstate {first}")
    assert "said so" in arm.say(ask)
    arm.say(f"revoke {first}")
    arm.say("teach: lantern = lamp")
    assert arm.last_lesson != first
    assert "Noted" in arm.say(use)
    assert "said so" in arm.say(ask)


def test_stream_delivers_named_speakers_to_both_arm_interfaces():
    class RecordingArm:
        def __init__(self):
            self.inputs = []
        def say(self, utterance, speaker="user"):
            self.inputs.append((speaker, utterance))
            return "ok"
    arm = RecordingArm()
    stream = {"conversations": [{"turns": [("Alice", "report one", "ok"),
                                             ("Bob", "report two", "ok")]}],
              "factual": [], "lessons": [], "negative_transfer": []}
    PH.phase_A_stream(arm, stream)
    assert arm.inputs[:2] == [("Alice", "report one"), ("Bob", "report two")]


def test_shared_transfer_donor_receives_identical_contracts(tmp_path, monkeypatch):
    arms = [MC.PersistentOCM(tmp_path / "o"), MC.WholeSystemParent(tmp_path / "p")]
    ops = E.enterprise_operators()
    source = C.Skill("shared:enterprise", E.ROLES, PH.M7_bindings(ops),
                     "enterprise", WP.of({"shared:demo"}))
    calls = []
    original = C.transported_skill
    def traced(skill, contract, operators, *args, **kwargs):
        calls.append((skill, contract, tuple(operators)))
        return original(skill, contract, operators, *args, **kwargs)
    monkeypatch.setattr(C, "transported_skill", traced)
    results, inventories = [], []
    for arm in arms:
        arm.work.skills["enterprise"] = source
        calls.clear()
        results.append(PH.phase_E(arm, matched_cells=True))
        inventories.append(list(calls))
    assert len(inventories[0]) == len(inventories[1]) == 3
    assert inventories[0] == inventories[1]
    assert results[0]["cells"] == results[1]["cells"]
    assert all(results[1]["success"])
    assert results[1]["harmful_accepted"] == 0


def test_parent_scope_and_unsupported_routes_are_explicit(tmp_path):
    arm = MC.WholeSystemParent(tmp_path)
    assert arm.info()["comparison_scope"] == "EXPOSED_A_E_ONLY_WITH_UNSUPPORTED_ROUTES"
    assert "cannot interpret" in arm.say("be formal")
    assert arm.last_frontend["parity"] == "CANNOT_CHECK"
    arm.say("the robot opened the door", speaker="Alice")
    assert arm.last_frontend["parity"] == "SUPPORTED_DONOR_ROUTE"
    arm.say("correction, the girl held the cup", speaker="Alice")
    assert arm.last_frontend["parity"] == "CANNOT_CHECK"
    assert arm.last_frontend["reason"] == "CANNOT_CHECK_TOPIC_CORRECTION_PARITY"


@pytest.mark.parametrize("lesson,category,concept", [
    ("teach: lantern = lamp as noun", "N", "lamp"),
    ("teach: glim = lift as verb", "V", "lift"),
])
def test_lexical_lesson_meaning_matches_not_just_acknowledgement(tmp_path, lesson, category, concept):
    ocm, parent = MC.PersistentOCM(tmp_path / "o"), MC.WholeSystemParent(tmp_path / "p")
    for arm in (ocm, parent):
        assert "Noted" in arm.say(lesson)
    word = lesson.split()[1]
    ocm_senses = ocm.s.dialogue.lexicon.lexemes[f"{word}|{category}"].senses
    parent_senses = parent.p.memory.lexicon.lexemes[f"{word}|{category}"].senses
    assert [(s.concept, s.node_type) for s in ocm_senses] == [(s.concept, s.node_type) for s in parent_senses]
    assert ocm_senses[-1].concept == concept


def test_parent_persistence_keeps_report_lineage_and_unsupported_accounting(tmp_path):
    arm = MC.WholeSystemParent(tmp_path)
    start = arm.state_digest()
    arm.say("the robot opened the door", speaker="Alice")
    report_digest = arm.state_digest()
    assert report_digest != start
    arm.say("correction, the robot did not open the door", speaker="Alice")
    records = arm.p.memory.statements
    assert not records[0]["active"] and records[1]["supersedes"] == records[0]["id"]
    arm.say("learn method next-square: inc square")
    assert arm.last_frontend["parity"] == "CANNOT_CHECK"
    before = arm.state_digest()
    arm.say("__restart__")
    assert arm.state_digest() == before
    assert arm.p.memory.statements == records
    assert sum(arm.info()["unsupported_routes"].values()) == 1
    assert arm.info()["whole_system_parity"] == "CANNOT_CHECK"


def test_parent_does_not_construct_ocm_runtime(tmp_path, monkeypatch):
    from ocm.runtime.ocm_runtime import OCMRuntime
    def forbidden(*args, **kwargs):
        raise AssertionError("comparator may not use OCM runtime")
    monkeypatch.setattr(OCMRuntime, "__init__", forbidden)
    parent = MC.WholeSystemParent(tmp_path)
    assert "Alice says" in parent.say("the robot opened the door", speaker="Alice")
    parent.say("__restart__")
    assert "Alice said so" in parent.say("did the robot open the door")


def test_transfer_success_requires_successful_execution(tmp_path, monkeypatch):
    parent = MC.WholeSystemParent(tmp_path)
    ops = E.enterprise_operators()
    parent.work.skills["enterprise"] = C.Skill("shared", E.ROLES, PH.M7_bindings(ops),
                                               "enterprise", WP.of({"demo"}))
    monkeypatch.setattr(PH.M, "run_skill", lambda *args, **kwargs: None)
    result = PH.phase_E(parent, matched_cells=True)
    cell = result["cells"]["representation_correspondence"]
    assert cell["result"] == "TRANSFER_EXECUTION_FAILED"
    assert not all(result["success"])
