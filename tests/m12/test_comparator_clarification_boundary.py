"""Shared clarification recognition must not block a speaker changing topic."""
import pytest

from ocm.lifetime import machine as MC


@pytest.mark.parametrize("intervening", [None, "teach", "revoke", "world", "spelling", "style"])
@pytest.mark.parametrize("arm_class", [MC.PersistentOCM, MC.WholeSystemParent])
def test_abandoned_clarification_does_not_block_supported_correction(tmp_path, arm_class, intervening):
    arm = arm_class(tmp_path)
    arm.say("teach: lantern = lamp")
    lesson = arm.last_lesson
    arm.say("the robot opened the door", speaker="Alice")
    clarification = arm.say("the robot saw the bank", speaker="Bob")
    assert "Did you mean" in clarification or "Which did you mean" in clarification
    if intervening is not None:
        text = {"teach": "teach: glim = lift", "revoke": f"revoke {lesson}",
                "world": "is paris in france", "spelling": "the robto lifted the box",
                "style": "be formal"}[intervening]
        arm.say(text)
    corrected = arm.say("correction, the robot did not open the door", speaker="Alice")
    assert "supersedes" in corrected, corrected
    assert "Alice said it did not" in arm.say("did the robot open the door")


@pytest.mark.parametrize("answer", ["yes", "1", "financial_institution"])
def test_genuine_clarification_answer_remains_explicitly_unsupported(tmp_path, answer):
    ocm = MC.PersistentOCM(tmp_path / "o")
    parent = MC.WholeSystemParent(tmp_path / "p")
    for arm in (ocm, parent):
        arm.say("the robot saw the bank", speaker="Alice")
        arm.say("is paris in france")
    assert "Noted" in ocm.say(answer)
    before = list(parent.p.memory.statements)
    parent.say(answer)
    assert parent.last_frontend["reason"] == "CANNOT_CHECK_CLARIFICATION_ANSWER_PARITY"
    assert parent.p.memory.statements == before
    assert "Noted" in parent.say("the robot opened the door", speaker="Bob")
