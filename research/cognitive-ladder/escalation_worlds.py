"""The registered escalation worlds for the SEARCH_MORE versus JUMP pilot.

Eight worlds plus one hostile, one per row of the programme's escalation
requirement.  Each world's ``minimum_sufficient_level`` is true **by
construction**, not by adjudication: the world is built by deciding what the
binding constraint will be and then instantiating exactly that constraint over a
real game family.  That is what makes the level a ground truth a third party can
recheck.

Registered before any protected outcome.  The pilot draw derives from the
pre-registration commitment; see ``prereg.py``.
"""

from __future__ import annotations

from games import MultiHeapGame, SubtractionGame
from escalation import EscalationWorld, Level, Representation

__all__ = ["WORLDS", "world_by_id"]


# --------------------------------------------------------------------------
# representations
# --------------------------------------------------------------------------

HEAP_SIZE = Representation("heap_size", lambda p: p)
HEAP_TUPLE = Representation("heap_tuple", lambda p: tuple(p))
TOKEN_TOTAL = Representation("token_total", lambda p: sum(p))
GRUNDY_MULTISET = Representation("grundy_multiset", lambda p: tuple(sorted(p)))


# --------------------------------------------------------------------------
# hypothesis builders
# --------------------------------------------------------------------------


def _residue_rule(period: int, residues: frozenset[int]):
    def h(n):
        return (n % period) in residues
    return h


def _combiner_rule(fn):
    def h(position):
        acc = fn(position)
        return acc == 0
    return h


def _xor(vs):
    acc = 0
    for v in vs:
        acc ^= v
    return acc


# --------------------------------------------------------------------------
# W1 / W1H: more search solves; and the budget-exhaustion hostile
# --------------------------------------------------------------------------

_SUB123 = SubtractionGame((1, 2, 3))
_SUB123_TABLE = _SUB123.grundy_upto(64)


def _sub123_truth(n):
    return _SUB123_TABLE[n] == 0


# two rules that agree on every multiple of four and disagree at residue two
_H_TRUE = _residue_rule(4, frozenset({0}))
_H_DECOY = _residue_rule(4, frozenset({0, 2}))

W1 = EscalationWorld(
    world_id="W1_SEARCH_MORE",
    positions=tuple(range(0, 33)),
    truth=_sub123_truth,
    representation=HEAP_SIZE,
    incumbent_hypotheses=(_H_TRUE, _H_DECOY),
    allowed_probes=(2, 12, 16),
    observed=((0, True), (4, True), (8, True)),
    probe_budget=3,
    minimum_sufficient_level=Level.L1_SEARCH_MORE,
    notes="probe 2 separates the two surviving rules and budget remains",
)

W1_HOSTILE = EscalationWorld(
    world_id="W1H_BUDGET_EXHAUSTED",
    positions=W1.positions,
    truth=_sub123_truth,
    representation=HEAP_SIZE,
    incumbent_hypotheses=(_H_TRUE, _H_DECOY),
    allowed_probes=(2, 12, 16),
    observed=W1.observed,
    probe_budget=0,
    minimum_sufficient_level=Level.L1_SEARCH_MORE,
    notes=(
        "identical to W1 except the budget is spent; a machine that escalates "
        "here has treated exhaustion as an obstruction and scores a false Jump"
    ),
)


# --------------------------------------------------------------------------
# W2: additional evidence solves (the probe channel is the binding constraint)
# --------------------------------------------------------------------------

W2 = EscalationWorld(
    world_id="W2_MORE_EVIDENCE",
    positions=tuple(range(0, 33)),
    truth=_sub123_truth,
    representation=HEAP_SIZE,
    incumbent_hypotheses=(_H_TRUE, _H_DECOY),
    allowed_probes=(12, 16, 20),  # every allowed probe is a multiple of four
    observed=((0, True), (4, True), (8, True)),
    probe_budget=3,
    minimum_sufficient_level=Level.L2_MORE_EVIDENCE,
    notes="no permitted probe separates the rules; position 2, outside the channel, does",
)


# --------------------------------------------------------------------------
# W3: one local repair solves (a registered bound is one notch too tight)
# --------------------------------------------------------------------------

_SUB134 = SubtractionGame((1, 3, 4))
_SUB134_TABLE = _SUB134.grundy_upto(64)


def _sub134_truth(n):
    return _SUB134_TABLE[n] == 0


# SUB(1,3,4) has Grundy period 7.  The incumbent language admits periods up to
# five only, so every incumbent hypothesis is refuted while a single relaxation
# of the period bound admits the true rule.
_INCUMBENT_SHORT_PERIODS = tuple(
    _residue_rule(p, frozenset(r for r in range(p) if r % 2 == 0))
    for p in range(2, 6)
) + tuple(_residue_rule(p, frozenset({0})) for p in range(2, 6))

W3 = EscalationWorld(
    world_id="W3_LOCAL_REPAIR",
    positions=tuple(range(0, 33)),
    truth=_sub134_truth,
    representation=HEAP_SIZE,
    incumbent_hypotheses=_INCUMBENT_SHORT_PERIODS,
    allowed_probes=tuple(range(15, 30)),
    observed=tuple((n, _sub134_truth(n)) for n in range(0, 15)),
    probe_budget=5,
    local_repair_available=True,
    minimum_sufficient_level=Level.L3_LOCAL_REPAIR,
    notes="true period is 7; the incumbent period bound of 5 is the only defect",
)


# --------------------------------------------------------------------------
# W4: one missing operator solves (vocabulary insufficiency, witnessed)
# --------------------------------------------------------------------------

_NIM2 = MultiHeapGame.nim(2, 8)


def _nim2_truth(position):
    return _xor(position) == 0


_NIM_POSITIONS = tuple((a, b) for a in range(0, 7) for b in range(0, 7))

# the incumbent vocabulary lacks XOR
_INCUMBENT_COMBINERS = (
    _combiner_rule(lambda vs: sum(vs) % 3),
    _combiner_rule(lambda vs: max(vs)),
    _combiner_rule(lambda vs: min(vs)),
    _combiner_rule(lambda vs: sum(vs)),
)
_WIDENED_COMBINERS = _INCUMBENT_COMBINERS + (_combiner_rule(_xor),)

W4 = EscalationWorld(
    world_id="W4_OPERATOR_INSUFFICIENT",
    positions=_NIM_POSITIONS,
    truth=_nim2_truth,
    representation=HEAP_TUPLE,
    incumbent_hypotheses=_INCUMBENT_COMBINERS,
    widened_hypotheses=_WIDENED_COMBINERS,
    allowed_probes=_NIM_POSITIONS,
    observed=tuple((p, _nim2_truth(p)) for p in [(1, 1), (1, 2), (2, 3), (3, 3), (2, 2)]),
    probe_budget=8,
    minimum_sufficient_level=Level.L4_OPERATOR_INSUFFICIENT,
    notes="XOR is absent from the incumbent vocabulary; adding it alone fits the evidence",
)


# --------------------------------------------------------------------------
# W5: the representation is genuinely non-identifying (exhibited witness)
# --------------------------------------------------------------------------

# Under a token-total representation, (1,3) and (2,2) share the image 4 and carry
# different labels.  No method over this representation can separate them, and
# the pair is the witness.
_TOTAL_HYPOTHESES = tuple(
    (lambda thr: (lambda p: sum(p) % thr == 0))(t) for t in range(2, 9)
)

W5 = EscalationWorld(
    world_id="W5_REPRESENTATION_NON_IDENTIFYING",
    positions=_NIM_POSITIONS,
    truth=_nim2_truth,
    representation=TOKEN_TOTAL,
    incumbent_hypotheses=_TOTAL_HYPOTHESES,
    widened_hypotheses=_TOTAL_HYPOTHESES,
    refined_hypotheses=(_combiner_rule(_xor),),
    allowed_probes=_NIM_POSITIONS,
    observed=((( 1, 3), _nim2_truth((1, 3))), ((2, 2), _nim2_truth((2, 2)))),
    probe_budget=8,
    minimum_sufficient_level=Level.L5_REPRESENTATION_CHANGE,
    notes="(1,3) and (2,2) both total four and differ in label; the witness is exhibited",
)


# --------------------------------------------------------------------------
# W6: the problem formulation is wrong (misere play mistaken for normal play)
# --------------------------------------------------------------------------


def _misere_nim_truth(position):
    """Misere Nim: with every heap of size at most one, the condition flips."""
    if all(h <= 1 for h in position):
        return sum(1 for h in position if h == 1) % 2 == 1
    return _xor(position) == 0


_MISERE_POSITIONS = tuple(
    (a, b, c) for a in range(0, 4) for b in range(0, 4) for c in range(0, 4)
)

_NORMAL_PLAY_HYPOTHESES = (
    _combiner_rule(_xor),
    _combiner_rule(lambda vs: sum(vs) % 2),
    _combiner_rule(lambda vs: max(vs)),
)

W6 = EscalationWorld(
    world_id="W6_FORMULATION_CHANGE",
    positions=_MISERE_POSITIONS,
    truth=_misere_nim_truth,
    representation=HEAP_TUPLE,
    incumbent_hypotheses=_NORMAL_PLAY_HYPOTHESES,
    widened_hypotheses=_NORMAL_PLAY_HYPOTHESES,
    allowed_probes=_MISERE_POSITIONS,
    observed=tuple(
        (p, _misere_nim_truth(p)) for p in [(1, 1, 0), (1, 1, 1), (2, 3, 1), (0, 1, 0), (1, 0, 0)]
    ),
    probe_budget=8,
    formulation_defect=True,
    minimum_sufficient_level=Level.L6_FORMULATION_CHANGE,
    notes=(
        "the world is misere; every normal-play hypothesis over an identifying "
        "representation is refuted, so the play convention is the defect"
    ),
)


# --------------------------------------------------------------------------
# W7: a Jump would be harmful overreach (the incumbent already identifies)
# --------------------------------------------------------------------------

W7 = EscalationWorld(
    world_id="W7_NO_ESCALATION",
    positions=tuple(range(0, 33)),
    truth=_sub123_truth,
    representation=HEAP_SIZE,
    incumbent_hypotheses=(_H_TRUE, _H_DECOY),
    allowed_probes=(12, 16),
    observed=((0, True), (2, False), (4, True), (8, True)),
    probe_budget=3,
    minimum_sufficient_level=Level.L0_NO_ESCALATION,
    notes="position 2 already eliminated the decoy; any escalation here is overreach",
)


# --------------------------------------------------------------------------
# W8: saturation without a representational defect (vocabulary is binding)
# --------------------------------------------------------------------------

# Every position is representationally distinct and every allowed probe leaves
# the surviving set intact, so the machine is saturated within (R, O, A).  The
# correct reading is vocabulary insufficiency, and crucially the terminal is
# SATURATED_WITHIN_REGISTERED_SPACE, never PROBLEM_IMPOSSIBLE.
_SAT_POSITIONS = tuple((a, b) for a in range(0, 5) for b in range(0, 5))
_SAT_OBSERVED = tuple((p, _nim2_truth(p)) for p in _SAT_POSITIONS)

W8 = EscalationWorld(
    world_id="W8_SATURATED_VOCABULARY_BINDING",
    positions=_SAT_POSITIONS,
    truth=_nim2_truth,
    representation=HEAP_TUPLE,
    incumbent_hypotheses=(_combiner_rule(_xor), _combiner_rule(_xor)),
    widened_hypotheses=(_combiner_rule(_xor),),
    allowed_probes=_SAT_POSITIONS,
    observed=_SAT_OBSERVED,
    probe_budget=4,
    minimum_sufficient_level=Level.L4_OPERATOR_INSUFFICIENT,
    notes=(
        "two extensionally identical hypotheses survive every probe; the space is "
        "saturated within the registered contract and no probe can ever separate them"
    ),
)


WORLDS = (W1, W1_HOSTILE, W2, W3, W4, W5, W6, W7, W8)


def world_by_id(world_id: str) -> EscalationWorld:
    for w in WORLDS:
        if w.world_id == world_id:
            return w
    raise KeyError(world_id)
