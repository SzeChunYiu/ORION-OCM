"""A named lesson revocation must disclose independent surviving lexical supports."""
from ocm.chat.session import ChatSession
from ocm.language.lexicon import AnalysisStatus


def teach(session, word, concept):
    session.say(f"teach: {word} = {concept}")
    return session.traces[-1].warrant_ids[0]


def test_named_revocation_reports_surviving_lesson(tmp_path):
    s = ChatSession(tmp_path / "chat")
    first = teach(s, "crate", "container")
    second = teach(s, "crate", "container")
    unrelated = teach(s, "parcel", "package")
    reply = s.say(f"revoke {second}")
    assert "still supported" in reply and first in reply
    assert second in s.runtime.state.evidence.revoked
    assert first not in s.runtime.state.evidence.revoked
    assert unrelated not in s.runtime.state.evidence.revoked
    s2 = ChatSession(tmp_path / "chat")
    assert s2.dialogue.lexicon.analyse("crate", s2.runtime.state.evidence.revoked).readings
    s2.say(f"revoke {first}")
    assert s2.dialogue.lexicon.analyse("crate", s2.runtime.state.evidence.revoked).status is AnalysisStatus.NO_LIVE_READING
    s2.say(f"reinstate {second}")
    assert s2.dialogue.lexicon.analyse("crate", s2.runtime.state.evidence.revoked).readings


def test_same_lemma_different_sense_is_reported_separately(tmp_path):
    s = ChatSession(tmp_path / "chat")
    bank = teach(s, "newbank", "river edge")
    finance = teach(s, "newbank", "financial institution")
    reply = s.say(f"revoke {finance}")
    assert "river edge" in reply and bank in reply
    assert "financial institution' still supported" not in reply


def test_single_support_has_no_false_remainder(tmp_path):
    s = ChatSession(tmp_path / "chat")
    e = teach(s, "crate", "container")
    assert "still supported" not in s.say(f"revoke {e}")
