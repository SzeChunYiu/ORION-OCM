from dataclasses import replace
import pytest
from ocm.chat.session import ChatSession
from ocm.dialogue import gate as G
from ocm.kso.warrant import Liveness
from ocm.language.meaning import example_meanings, canonical


def plan():
    m = example_meanings()['the robot did not open the door']
    return G.ResponsePlan(G.Act.ANSWER,m,(G.Assertion(canonical(m)[1],('ev:1',),'machine'),),G.Marker.ASSERTED)


@pytest.mark.parametrize('text', ['The robot opened the door.', 'The robot did not open the door. The cat flew.', 'The robot did not open the red door.'])
def test_renderer_metadata_cannot_hide_actual_text_change(text):
    p=plan()
    assert not G.commit_gate(p,G.Surface(text,p.meaning,p.required_marker),lambda _:Liveness.LIVE).committed


def test_marker_none_does_not_bypass_truth_requirement():
    p=replace(plan(),required_marker=G.Marker.NONE)
    assert not G.commit_gate(p,G.Surface('The robot did not open the door.',p.meaning,G.Marker.NONE),lambda _:Liveness.DEAD).committed


def test_actual_protected_identifier_cannot_be_omitted_from_metadata():
    p=G.ResponsePlan(G.Act.ACKNOWLEDGE,None)
    assert not G.commit_gate(p,G.Surface('hidden:gold',None,G.Marker.NONE),lambda _:Liveness.LIVE,protected_ids=('hidden:gold',)).committed


@pytest.mark.parametrize('question',['is paris in france','explain paris'])
def test_actual_chat_output_is_checked_after_renderer_returns(tmp_path,question):
    s=ChatSession(tmp_path)
    s._render_item=lambda _: 'Paris is in Germany.'
    response=s.say(question)
    assert not response.startswith('Yes.') and response != 'Paris is in Germany.'
    assert 'cannot' in response.lower()


def test_render_callback_revocation_is_rechecked_for_explanation(tmp_path):
    s=ChatSession(tmp_path)
    original=s._render_item
    def render(item):
        s.runtime.revoke(item.evidence)
        return original(item)
    s._render_item=render
    assert 'cannot' in s.say('explain paris').lower()


def test_malformed_teaching_does_not_crash_or_create_evidence(tmp_path):
    s=ChatSession(tmp_path)
    for request in ['teach: construction broken', 'teach: example => too few', 'teach: =', 'teach: word without definition']:
        before=len(s.runtime.state.evidence.records)
        response=s.say(request)
        assert 'cannot' in response.lower() or 'format' in response.lower()
        assert len(s.runtime.state.evidence.records)==before


@pytest.mark.parametrize('subject',['moon','sun','earth'])
def test_registered_astronomical_determiners_preserve_graph_identity(subject):
    from ocm.dialogue.surface_text import world_clause, clause_matches
    from ocm.knowledge.world import triple
    m=triple(subject,'ORBITS','galactic center')
    text=world_clause(m)
    assert text.startswith('The '+subject)
    assert clause_matches(text,m)
    assert not clause_matches(text,triple(subject,'ORBITS','unrelated center'))
