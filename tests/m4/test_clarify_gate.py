"""M4 §4 clarification value, §7 feedback events, §8 external commitment gate, §14 hostiles."""
from __future__ import annotations

from ocm.dialogue import clarify as CL
from ocm.dialogue import gate as G
from ocm.kso.warrant import Liveness
from ocm.language import meaning as M


def _queries(relevant: bool):
    # candidates: two doors; the pending task asks "is it red?" — relevant iff the doors differ in colour
    colour = {"d1": "red", "d2": "red" if not relevant else "blue"}
    return {"is_red": lambda c: colour[c] == "red", "is_door": lambda c: True}


def test_irrelevant_ambiguity_is_not_asked_and_consequential_ambiguity_is():
    cands = ["d1", "d2"]
    qs = CL.binary_questions(cands, lambda c: f"door {c}")
    d0 = CL.decide(cands, _queries(relevant=False), qs)
    assert d0.ask is False and "irrelevant" in d0.reason
    d1 = CL.decide(cands, _queries(relevant=True), qs, repeat_penalty=1.0)
    assert d1.ask is True and d1.value > 0
    # the hostiles: always-ask loops on irrelevant ambiguity; never-ask ignores consequential ambiguity
    assert CL.mutant_always_ask(cands).ask is True and CL.mutant_never_ask(cands).ask is False


def test_question_separating_more_hypotheses_is_preferred_and_repeats_are_penalised():
    cands = ["a", "b", "c"]
    ans = {"a": 1, "b": 2, "c": 3}
    queries = {"q1": lambda c: ans[c], "q2": lambda c: ans[c] % 2}
    is_a = CL.Question("is:a", "a?", (frozenset({"a"}), frozenset({"b", "c"})), cost=0.5)
    menu = CL.Question("menu", "a, b or c?", (frozenset({"a"}), frozenset({"b"}), frozenset({"c"})), cost=0.5)
    d = CL.decide(cands, queries, [is_a, menu])
    assert d.question.question_id == "menu" and d.values["menu"] >= d.values["is:a"]
    d2 = CL.decide(cands, queries, [menu], asked_before=["menu"], repeat_penalty=5.0)
    assert d2.ask is False and d2.value <= 0


def _plan_and_surface(liveness, layer="machine"):
    m = M.example_meanings()["the robot did not open the door"]
    dg = M.canonical(m)[1]
    marker = G.required_marker(liveness, layer)
    plan = G.ResponsePlan(G.Act.ANSWER, m, (G.Assertion(dg, ("ev:1",), layer),), marker, referents=("ent:robot",))
    text = {G.Marker.ASSERTED: "The robot did not open the door.", G.Marker.UNCERTAIN: "I am not sure whether the robot opened the door.", G.Marker.REPORTED: "Alice said the robot did not open the door.", G.Marker.DENIED: "No: the robot did not open the door."}[marker]
    return plan, G.Surface(text, m, marker)


def test_gate_commits_only_when_meaning_marker_warrant_and_referents_agree():
    live = lambda ev: Liveness.LIVE  # noqa: E731
    plan, surf = _plan_and_surface(Liveness.LIVE)
    assert G.commit_gate(plan, surf, live, resolved=["ent:robot"]).committed
    # missing referent → structured reopen of the reference stage
    v = G.commit_gate(plan, surf, live, resolved=[])
    assert not v.committed and v.events[0].kind is G.FeedbackKind.MISSING_REFERENT and v.events[0].reopen_stage == "reference"
    # assertion whose evidence is UNKNOWN cannot be ASSERTED: unsupported-assertion event reopens warrant
    v2 = G.commit_gate(plan, surf, lambda ev: Liveness.UNKNOWN, resolved=["ent:robot"])
    assert any(e.kind is G.FeedbackKind.UNSUPPORTED_ASSERTION and e.reopen_stage == "warrant" for e in v2.events)
    # uncertain plan rendered correctly commits; the dropped-uncertainty mutant is refused
    plan_u, surf_u = _plan_and_surface(Liveness.UNKNOWN)
    assert G.commit_gate(plan_u, surf_u, lambda ev: Liveness.UNKNOWN, resolved=["ent:robot"]).committed
    bad = G.commit_gate(plan_u, G.mutant_drop_uncertainty(surf_u), lambda ev: Liveness.UNKNOWN, resolved=["ent:robot"])
    assert not bad.committed and any(e.kind is G.FeedbackKind.MARKER_MISMATCH for e in bad.events)
    # speaker-layer assertion must be REPORTED, never ASSERTED
    plan_s, surf_s = _plan_and_surface(Liveness.LIVE, layer="speaker")
    assert plan_s.required_marker is G.Marker.REPORTED and G.commit_gate(plan_s, surf_s, live, resolved=["ent:robot"]).committed
    flat = G.Surface(surf_s.text, surf_s.meaning, G.Marker.ASSERTED)
    assert not G.commit_gate(plan_s, flat, live, resolved=["ent:robot"]).committed


def test_renderer_cannot_mint_facts_leak_protected_content_or_hold_the_store():
    live = lambda ev: Liveness.LIVE  # noqa: E731
    plan, surf = _plan_and_surface(Liveness.LIVE)
    inj = G.commit_gate(plan, G.mutant_renderer_injects_fact(surf, "digest:extra"), live, resolved=["ent:robot"])
    assert not inj.committed and any(e.kind is G.FeedbackKind.MEANING_DRIFT for e in inj.events)
    other = M.example_meanings()["the robot opened the red door"]
    drift = G.commit_gate(plan, G.Surface("The robot opened the red door.", other, G.Marker.ASSERTED), live, resolved=["ent:robot"])
    assert not drift.committed and drift.events[0].kind is G.FeedbackKind.MEANING_DRIFT
    leak = G.commit_gate(plan, G.Surface(surf.text, surf.meaning, surf.marker, content_ids=("hash:protected",)), live, resolved=["ent:robot"], protected_ids=["hash:protected"])
    assert not leak.committed and any(e.kind is G.FeedbackKind.PROTECTED_LEAK for e in leak.events)
    cap = G.commit_gate(plan, G.Surface(surf.text, surf.meaning, surf.marker, renderer_had_store=True), live, resolved=["ent:robot"])
    assert not cap.committed and any(e.kind is G.FeedbackKind.RENDERER_CAPABILITY for e in cap.events)
