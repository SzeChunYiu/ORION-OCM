"""Complete the two remaining authored language cases without altering old fixtures."""
from ocm.chat.session import ChatSession


def test_bare_nominal_question_uses_warranted_world_facts(tmp_path):
    session = ChatSession(tmp_path)
    assert session.say("is ice water").startswith("Yes.")
    assert "I do not know" in session.say("is ice planet")
    session.world.revoke_source("curated:v1")
    assert not session.say("is ice water").startswith("Yes.")


def test_distinct_past_participle_is_reusable_after_teaching_and_restart(tmp_path):
    session = ChatSession(tmp_path)
    session.say("teach: gnome = garden statue")
    assert "Noted" in session.say("the cat saw the gnome")
    assert "Noted" in session.say("the gnome was seen by the cat")
    session = ChatSession(tmp_path)
    assert "Noted" in session.say("the gnome was seen by the cat")
    assert "cannot interpret" in session.say("the gnome was saw by the cat")
