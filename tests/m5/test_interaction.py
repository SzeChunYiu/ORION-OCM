"""M5 E3 / KS-T18 / batch-3 C6: outcome observations of a registered outcome function eliminate
hypotheses and warrant the object; success bits (feedback) never do; the hostile launders them."""
from __future__ import annotations

import pytest

from ocm.learning.language import interaction as X
from ocm.learning.learner import UpdateKind, UpdateStatus

# hypotheses about what "push the X" means, as (role assignment): which object the listener acts on
CLASS = {"patient_is_object": "obj", "patient_is_subject": "subj", "patient_is_last_noun": "last"}
WORLD = {"push the box toward the door": {"obj": "box", "subj": "robot", "last": "door"}, "lift the cup near the ball": {"obj": "cup", "subj": "robot", "last": "ball"}, "open the door by the box": {"obj": "door", "subj": "robot", "last": "box"}}
outcome = X.OutcomeFunction("acted_on", "the object the listener manipulated after the utterance", lambda h, u: WORLD[u][h])


def test_registered_outcomes_eliminate_hypotheses_and_warrant_the_object():
    eps = [X.InteractionEpisode("push the box toward the door", "box", "ev:obs1", "acted_on")]
    p = X.interaction_learn(CLASS, outcome, eps, ["lift the cup near the ball", "open the door by the box"])
    assert p.status is UpdateStatus.PASS and p.kind is UpdateKind.OBJECT and p.payload["hypothesis"] == "patient_is_object"
    assert p.warrant.evidence == {"ev:obs1"}                     # the warrant is the observation, not a reward
    bad = X.OutcomeFunction("vibes", "unregistered", lambda h, u: True, registered=False)
    with pytest.raises(X.UnregisteredOutcome):
        X.interaction_learn(CLASS, bad, eps, ["lift the cup near the ball"])


def test_success_bits_never_admit_an_object_and_the_mutant_launders_them():
    bits = [X.SuccessBit("push the box toward the door", True, "ev:fb1"), X.SuccessBit("lift the cup near the ball", True, "ev:fb2")]
    p = X.feedback_only(CLASS, bits, ["open the door by the box"])
    assert p.kind is not UpdateKind.OBJECT
    m = X.mutant_success_bit_as_observation(CLASS, bits, ["open the door by the box"], lambda h, u: h == "obj")
    assert m.kind is UpdateKind.OBJECT and m.status is UpdateStatus.PASS and m.warrant.evidence == {"ev:fb1", "ev:fb2"}   # preference laundered into warrant
