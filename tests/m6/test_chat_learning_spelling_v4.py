"""End-to-end development checks; these do not measure ChatGPT equivalence."""
from pathlib import Path

import pytest

from ocm.chat.session import ChatSession
from ocm.chat.spelling import one_edit, propose


@pytest.mark.parametrize("text", ["is parsi in france", "is pariss in france", "is pariz in france", "iis paris in france"])
def test_typo_questions_are_conditional_answers_with_original_input(tmp_path, text):
    s = ChatSession(tmp_path)
    reply = s.say(text)
    assert "Assuming you meant" in reply and "Yes." in reply
    assert s.last_trace()["utterance"] == text
    assert s.last_trace()["interpretation"]["input"]["status"] == "SPELLING_GUESS"


def test_nearby_words_do_not_choose_the_most_convenient_fact(tmp_path):
    s = ChatSession(tmp_path)
    s.say("teach: cart = cart")
    s.say("teach: part = part")
    reply = s.say("the c part")  # known words never change
    assert "Assuming" not in reply
    result = propose("is bart in france", s.dialogue.lexicon, s.runtime.state.revoked)
    assert result.status == "AMBIGUOUS"
    reply = s.say("is bart in france")
    assert reply.startswith("Did you mean") and "Yes." not in reply
    assert s.say("is pars in france").startswith("Did you mean")


def test_typo_statement_needs_confirmation_before_learning(tmp_path):
    s = ChatSession(tmp_path)
    before = len(s.dialogue.workspace.active_commitments())
    assert s.say("the robto lifted the box").startswith("Did you mean")
    assert len(s.dialogue.workspace.active_commitments()) == before
    assert s.say("yes").startswith("Noted")
    assert len(s.dialogue.workspace.active_commitments()) == before + 1


@pytest.mark.parametrize("text", ["teach: robto = robot", "revoke ev:abc", "reinstate ev:abc",
    "learn method x: inc square", "run x on 12", "remember: mria is in oslo", "is mars not a planet", "is mars a planet", "is 123 in 456"])
def test_commands_negation_known_words_and_numbers_are_not_rewritten(tmp_path, text):
    s = ChatSession(tmp_path)
    assert not propose(text, s.dialogue.lexicon, s.runtime.state.revoked).candidates


def test_new_knowledge_survives_restart_and_remains_user_report(tmp_path):
    s = ChatSession(tmp_path)
    assert "not independently verified" in s.say("remember: mira is a botanist")
    evidence = s.traces[-1].warrant_ids[0]
    s = ChatSession(tmp_path)
    reply = s.say("is mira a botanist")
    assert "source" in reply.lower() and "not verified" in reply and not reply.startswith("Yes")
    s.say("revoke " + evidence)
    assert "revoked" in s.say("is mira a botanist").lower()


def test_learned_method_reuse_restart_revocation_and_new_search(tmp_path):
    s = ChatSession(tmp_path)
    assert "Learned method" in s.say("learn method next-square: inc square")
    evidence = s.traces[-1].warrant_ids[0]
    assert "= 16" in s.say("run next-square on 3")
    s = ChatSession(tmp_path)
    assert "= 25" in s.say("run next-square on 4")
    assert "next-square" in s.say("list skills")
    assert "already exists" in s.say("learn method next-square: dec")
    s.say("revoke " + evidence)
    assert "no unique live method" in s.say("run next-square on 4")
    assert "Learned method" in s.say("find method: 1,2,1")
    assert "cannot learn" in s.say("learn method bad: print square")
    assert not Path(tmp_path / "executed").exists()


def test_unsupported_negative_memory_does_not_become_positive_fact(tmp_path):
    s = ChatSession(tmp_path)
    before = len(s.world.facts)
    assert "positive statements" in s.say("remember: mira is not a botanist")
    assert len(s.world.facts) == before


def test_dead_lexical_support_is_not_restored_by_spelling(tmp_path):
    s = ChatSession(tmp_path)
    s.say("teach: lantern = lamp")
    eid = s.traces[-1].warrant_ids[0]
    assert propose("the lantren", s.dialogue.lexicon).candidates
    s.say("revoke " + eid)
    assert not propose("the lantren", s.dialogue.lexicon, s.runtime.state.revoked).candidates


def test_one_edit_is_symmetric_and_preserves_equal_words():
    for a, b in [("parsi", "paris"), ("pariz", "paris"), ("pars", "paris"), ("pariss", "paris")]:
        assert one_edit(a, b) and one_edit(b, a)
    assert not one_edit("paris", "paris") and not one_edit("paris", "pluto")
