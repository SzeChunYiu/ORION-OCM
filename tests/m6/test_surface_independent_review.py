"""Independent regressions for the actual-text speech boundary review.

Each case was reproduced against the initial boundary implementation. These
are local correctness checks in the registered grammars, not an English claim.
"""
from ocm.chat.session import ChatSession
from ocm.dialogue import gate as G
from ocm.dialogue.surface_text import clause_matches
from ocm.knowledge.world import triple
from ocm.kso.warrant import Liveness
from ocm.language.bootstrap import microworld_lexicon
from ocm.language.constructions import seed_constructions
from ocm.language.interpret import interpret
from ocm.language.meaning import canonical


def world_plan(*, marker=G.Marker.ASSERTED, layer="machine", digest=None,
               source_name=None, reported_negative=False):
    meaning = triple("paris", "LOCATED_IN", "france")
    return G.ResponsePlan(
        G.Act.ANSWER, meaning,
        (G.Assertion(digest or canonical(meaning)[1], ("e1",), layer),),
        marker, source_name=source_name, reported_negative=reported_negative)


def verdict(plan, text, *, status=Liveness.LIVE):
    return G.commit_gate(plan, G.Surface(text, plan.meaning, plan.required_marker),
                         lambda _: status)


def test_assertive_act_cannot_hide_all_semantics_in_an_empty_plan():
    plan = G.ResponsePlan(G.Act.ASSERT, None)
    assert not verdict(plan, "Paris is in Germany.").committed


def test_assertion_digest_must_bind_the_actual_planned_proposition():
    plan = world_plan(digest="unrelated_proposition")
    assert not verdict(plan, "Paris is in France.").committed


def test_negative_report_cannot_render_as_a_positive_report():
    plan = world_plan(marker=G.Marker.REPORTED, layer="speaker",
                      source_name="Alice", reported_negative=True)
    assert not verdict(plan, "Alice said Paris is in France.").committed


def test_revoked_support_does_not_authorize_denial_of_the_world_proposition():
    plan = world_plan(marker=G.Marker.DENIED)
    assert not verdict(plan, "No: Paris is in France.", status=Liveness.DEAD).committed


def test_bound_source_metadata_cannot_inject_an_extra_surface_assertion():
    source = "Alice. Paris is in Germany. Bob"
    plan = world_plan(marker=G.Marker.REPORTED, layer="speaker", source_name=source)
    text = f"{source} said so (e1); I have no independent warrant."
    assert not verdict(plan, text).committed


def test_world_parser_checks_every_split_of_a_repeated_relation():
    # Both a CONTAINS (b contains c) and (a contains b) CONTAINS c are readings
    # under the initial multiword-label grammar. One regex match is insufficient.
    meaning = triple("a", "CONTAINS", "b contains c")
    assert not clause_matches("A contains B contains C.", meaning)


def test_default_water_explanation_handles_unregistered_relation_as_typed_result(tmp_path):
    session = ChatSession(tmp_path)
    reply = session.say("explain water")
    # A newly registered correct rendering or an explicit refusal is acceptable;
    # the original implementation raised ValueError out of the conversation.
    assert isinstance(reply, str) and reply
    assert "water" in reply.lower() or "cannot" in reply.lower()


def test_decoder_callback_warrant_change_is_checked_after_actual_text_parsing():
    lexicon = microworld_lexicon()
    constructions = seed_constructions()
    text = "the robot opened the door"
    meaning = interpret(text, lexicon, constructions).meaning
    plan = G.ResponsePlan(G.Act.ANSWER, meaning,
        (G.Assertion(canonical(meaning)[1], ("e1",), "machine"),), G.Marker.ASSERTED)
    current = {"status": Liveness.LIVE}
    original = lexicon.analyse

    def decoder_callback(token, revoked):
        current["status"] = Liveness.DEAD
        return original(token, revoked)

    lexicon.analyse = decoder_callback
    result = G.commit_gate(plan, G.Surface(text, meaning, G.Marker.ASSERTED),
        lambda _: current["status"], lexicon=lexicon, constructions=constructions)
    assert current["status"] is Liveness.DEAD
    assert not result.committed
