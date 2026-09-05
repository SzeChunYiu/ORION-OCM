"""M6 §15 product demonstration as a test: the eleven required points on a clean state, plus the
hostiles the gate must catch."""
from __future__ import annotations

import json
from pathlib import Path

from ocm.chat.session import ChatSession
from ocm.chat.__main__ import run_demo


def test_alpha_demonstration_points(tmp_path):
    s = ChatSession(tmp_path / "alpha")
    # 1 normal conversation + 2 reference
    assert "Noted" in s.say("the robot opened the door")
    assert "said so" in s.say("did the robot open the door")
    s.say("the cat pushed the box")
    assert "Which do you mean" in s.say("which box did it push") or "I do not know what" in s.say("which box did it push")
    # 3 explanation over the bounded world (verified facts, cites evidence)
    ex = s.say("explain paris")
    assert "Paris is in france" in ex or "paris is in france" in ex.lower()
    assert s.say("is paris in france").startswith("Yes.")
    # 5 unknown is honest; a wrong source is reported as unverified, never asserted
    assert s.say("is paris in spain").startswith("I do not know")
    g = s.say("is paris in germany")
    assert g.startswith("A source (rumour:v1) says so, but I have not verified it")
    # 4 consequential ambiguity → clarification → collapse by answer
    c = s.say("the robot saw the bank")
    assert "Did you mean" in c or "Which did you mean" in c
    assert "Noted" in s.say("2")
    # 6–7 learn a new word and reuse it compositionally
    t = s.say("teach: crate = shipping container")
    assert t.startswith("Noted: 'crate' means shipping container")
    lesson = s.traces[-1].warrant_ids[0]
    assert "Noted" in s.say("the robot lifted the crate") and "said so" in s.say("did the robot lift the crate")
    # 8 restart retains the lesson and the record
    s.runtime.persist()
    s2 = ChatSession(tmp_path / "alpha")
    assert "said so" in s2.say("did the robot lift the crate")
    # 9 revoke the lesson: the word stops working; 10 unrelated knowledge intact
    assert s2.say(f"revoke {lesson}").startswith("Revoked")
    r = s2.say("the robot lifted the crate")
    assert "cannot interpret" in r and "UNKNOWN_LEXEME" in r
    assert s2.say("is berlin in germany").startswith("Yes.")
    # reinstating restores the capability
    s2.say(f"reinstate {lesson}")
    assert "Noted" in s2.say("the robot lifted the crate")
    # 11 the trace ties speech to actual ledger events and warrant ids
    tr = s2.last_trace()
    assert tr["committed_response"].startswith("Noted") and tr["ledger_events"] and tr["warrant_ids"]
    # style shift keeps facts invariant
    s2.say("be brief")
    assert s2.say("is paris in france").startswith("Yes.")


def test_scripted_demo_runs_clean(tmp_path, capsys):
    assert run_demo(tmp_path / "demo", diagnostic=False) == 0
    out = capsys.readouterr().out
    for label in ("## 1 normal", "## 5 genuine unknown", "## 8 restart", "## 9 revoke", "## 11 diagnostic"):
        assert label in out
    assert "I do not know whether paris located in spain" in out and "process restarted" in out


def test_compare_summary_and_source_revocation(tmp_path):
    s = ChatSession(tmp_path / "alpha")
    cmp = s.say("compare paris and berlin")
    assert "share" in cmp and "differ" in cmp
    s.say("the robot opened the door")
    assert s.say("summarize").startswith("So far: user said")
    # revoking the curated source's verification for one fact is done by evidence id; the world's revoke test
    rep = s.world.revoke_source("rumour:v1")
    assert rep["facts_dead"] == ["rum:paris:germany"]
    assert s.say("is paris in germany").startswith("I do not know") or "revoked" in s.say("is paris in germany")
    assert s.say("is paris in france").startswith("Yes.")
