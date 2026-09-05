"""Reduced-bootstrap construction-family recovery for N1/#54/#55.

The historical bounded-world machine starts with seven English Construction
objects.  This calibration starts with an empty construction inventory.  Surface
word/category/concept lessons and semantic target schemas are explicit teacher
information; finite form-order hypotheses are learned from aligned examples.

The goal is narrow but exact: recover the seven *functional construction
families* (NP, transitive, intransitive, passive, negation, yes/no question,
wh-object question), generalize each to a held-out lexical composition, and make
each learned construction unavailable when its own demonstration support is
revoked.  The function-word and inflected-form lessons are deliberately counted;
this is not raw-corpus English acquisition.
"""
from __future__ import annotations

from dataclasses import dataclass
import itertools
from typing import Any, Iterable, Mapping, Sequence

from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.language import acquisition as AQ
from ocm.language.constructions import Construction, Phrase, Slot, phrase_table
from ocm.language.interpret import Verdict, interpret, tokenize
from ocm.language.lexicon import Category, Lexeme, Sense
from ocm.language.meaning import MEdge, MNode, MeaningGraph, canonical

from minimal_language_learning import LearnedLanguage, empty_language


@dataclass(frozen=True)
class FamilyReceipt:
    family: str
    evidence_id: str
    hypothesis_count: int
    learned_pattern: tuple[str, ...]
    held_out_ok: bool
    dead_after_own_revocation: bool


def _teach(
    state: LearnedLanguage,
    surface: str,
    category: Category,
    *,
    concept: str | None = None,
    node_type: str = "function",
    features: tuple[tuple[str, str], ...] = (),
) -> None:
    evidence = f"lesson:{state.language}:token:{surface}:{category.value}"
    warrant = WarrantProfile.of({evidence})
    scope = Scope.of(state.language)
    senses = () if concept is None else (
        Sense(f"{state.language}:{surface}:{concept}", concept, node_type, warrant, scope=scope),
    )
    state.lexicon.add(
        Lexeme(surface, category, senses, features=features, warrant=warrant, scope=scope)
    )
    state.information_events.append(evidence)


def teach_inventory(state: LearnedLanguage) -> None:
    for word in ("robot", "girl", "door", "ball"):
        _teach(state, word, Category.NOUN, concept=word, node_type="entity")
    for word in ("red", "green"):
        _teach(state, word, Category.ADJ, concept=word, node_type="property")
    for word in ("open", "push", "move"):
        _teach(state, word, Category.VERB, concept=word, node_type="event", features=(("tense", "present"),))
    # Construction recovery isolates form-order learning from morphology.  These
    # inflected forms are explicit teacher items; #63 separately tests learning
    # morphology from zero rules.
    _teach(state, "opened", Category.VERB, concept="open", node_type="event", features=(("participle", "past"),))
    _teach(state, "pushed", Category.VERB, concept="push", node_type="event", features=(("participle", "past"),))
    _teach(state, "the", Category.DET)
    _teach(state, "was", Category.AUX, features=(("tense", "past"),))
    _teach(state, "did", Category.AUX, features=(("tense", "past"),))
    _teach(state, "not", Category.NEG)
    _teach(state, "by", Category.PREP)
    _teach(state, "which", Category.WH)
    _teach(state, "it", Category.PRON)


def _concept(value: Any) -> str | None:
    if isinstance(value, Phrase):
        node = next(n for n in value.meaning.nodes if n.node_id == value.head_node)
        return node.label
    return value.sense.concept if value.sense is not None else value.lemma


def _np_graph(noun: str, adjective: str | None = None, *, definite: bool = False) -> MeaningGraph:
    feats = (("definite", "yes"),) if definite else ()
    nodes = [MNode("x", "entity", noun, feats)]
    edges = []
    if adjective is not None:
        nodes.append(MNode("p", "property", adjective))
        edges.append(MEdge("MODIFIES", ("p",), ("x",)))
    return MeaningGraph(tuple(nodes), tuple(edges), root="x")


def np_template(binding: Mapping[str, Any]) -> MeaningGraph:
    return _np_graph(
        _concept(binding["n"]) or binding["n"].lemma,
        _concept(binding["a"]) if "a" in binding else None,
        definite="d" in binding,
    )


def clause_graph(subj: str | None, verb: str, obj: str | None = None, *, negated: bool = False, question: bool = False) -> MeaningGraph:
    nodes = [MNode("s", "entity", subj, underspecified=subj is None), MNode("e", "event", verb)]
    edges = [MEdge("ROLE:agent", ("e",), ("s",))]
    if obj is not None:
        nodes.append(MNode("o", "entity", obj))
        edges.append(MEdge("ROLE:patient", ("e",), ("o",)))
    if negated:
        edges.append(MEdge("NEGATES", ("e",), ("e",)))
    if question:
        nodes.append(MNode("q", "question_variable", None, underspecified=True))
        edges.append(MEdge("ASKS", ("q",), ("e",), "polarity"))
    return MeaningGraph(tuple(nodes), tuple(edges), root="e")


def transitive_template(binding: Mapping[str, Any]) -> MeaningGraph:
    return clause_graph(_concept(binding["subj"]), _concept(binding["verb"]) or binding["verb"].lemma, _concept(binding["obj"]))


def intransitive_template(binding: Mapping[str, Any]) -> MeaningGraph:
    return clause_graph(_concept(binding["subj"]), _concept(binding["verb"]) or binding["verb"].lemma)


def passive_template(binding: Mapping[str, Any]) -> MeaningGraph:
    # Surface grammatical subject is the semantic patient in this family.
    patient = _concept(binding["patient"])
    agent = _concept(binding["agent"])
    verb = _concept(binding["verb"]) or binding["verb"].lemma
    nodes = (MNode("s", "entity", agent), MNode("e", "event", verb), MNode("o", "entity", patient))
    edges = (
        MEdge("ROLE:agent", ("e",), ("s",)),
        MEdge("ROLE:patient", ("e",), ("o",)),
        MEdge("TENSE", ("e",), ("e",), "past"),
    )
    return MeaningGraph(nodes, edges, root="e")


def negation_template(binding: Mapping[str, Any]) -> MeaningGraph:
    return clause_graph(_concept(binding["subj"]), _concept(binding["verb"]) or binding["verb"].lemma, _concept(binding["obj"]), negated=True)


def yesno_template(binding: Mapping[str, Any]) -> MeaningGraph:
    return clause_graph(_concept(binding["subj"]), _concept(binding["verb"]) or binding["verb"].lemma, _concept(binding["obj"]), question=True)


def wh_template(binding: Mapping[str, Any]) -> MeaningGraph:
    verb = _concept(binding["verb"]) or binding["verb"].lemma
    obj = _concept(binding["obj_n"])
    nodes = (
        MNode("s", "entity", None, underspecified=True),
        MNode("e", "event", verb),
        MNode("o", "entity", obj),
        MNode("q", "question_variable", None, underspecified=True),
    )
    edges = (
        MEdge("ROLE:agent", ("e",), ("s",)),
        MEdge("ROLE:patient", ("e",), ("o",)),
        MEdge("ASKS", ("q",), ("o",)),
        MEdge("TENSE", ("e",), ("e",), "past"),
    )
    return MeaningGraph(nodes, edges, root="e")


def _patterns(roles: Sequence[tuple[str, Slot]]) -> dict[str, tuple[Slot, ...]]:
    return {
        "-".join(name for name, _ in perm): tuple(slot for _, slot in perm)
        for perm in itertools.permutations(roles)
    }


def _learn_clause(
    state: LearnedLanguage,
    *,
    family_name: str,
    roles: Sequence[tuple[str, Slot]],
    template,
    teaching_utterance: str,
    teaching_meaning: MeaningGraph,
    held_out_utterance: str,
    evidence_id: str,
    helpers: Sequence[Construction] = (),
) -> tuple[Construction, int]:
    family = AQ.ConstructionFamily(
        family_name,
        _patterns(roles),
        template,
        (held_out_utterance,),
        language=state.language,
        helpers=tuple(helpers),
    )
    proposal = AQ.acquire(
        family,
        state.lexicon,
        (AQ.Demonstration(teaching_utterance, teaching_meaning, evidence_id),),
    )
    if proposal.status.value != "PASS":
        raise AssertionError(f"{family_name} acquisition failed: {proposal.status.value}: {proposal.detail}")
    construction = AQ.construction_from_proposal(
        family,
        proposal,
        f"{state.language}:{family_name}:learned",
    )
    state.constructions.append(construction)
    state.information_events.append(evidence_id)
    return construction, len(family.hypotheses)


def _learn_np(state: LearnedLanguage) -> tuple[Construction, int]:
    D, A, N = Category.DET, Category.ADJ, Category.NOUN
    roles = (
        ("D", Slot("d", D, optional=True)),
        ("A", Slot("a", A, optional=True)),
        ("N", Slot("n", N)),
    )
    family = AQ.ConstructionFamily(
        "noun_phrase",
        _patterns(roles),
        np_template,
        ("the green girl",),
        language=state.language,
    )
    evidence = "demo:construction:np"
    proposal = AQ.acquire(
        family,
        state.lexicon,
        (AQ.Demonstration("the red robot", _np_graph("robot", "red", definite=True), evidence),),
    )
    if proposal.status.value != "PASS":
        raise AssertionError(f"noun_phrase acquisition failed: {proposal.status.value}: {proposal.detail}")
    pattern = family.hypotheses[proposal.payload["hypothesis"]]
    construction = Construction(
        f"{state.language}:noun_phrase:learned",
        "noun_phrase",
        pattern,
        np_template,
        proposal.warrant,
        language=state.language,
        produces="NP",
        head_slot="n",
        head_node="x",
        lineage=proposal.lineage,
    )
    state.constructions.append(construction)
    state.information_events.append(evidence)
    return construction, len(family.hypotheses)


def _np_held_out(state: LearnedLanguage, np: Construction, revoked=()) -> bool:
    utterance = "the green girl"
    analyses = [list(state.lexicon.analyse(token, revoked).readings) for token in tokenize(utterance)]
    table = phrase_table((np,), analyses, revoked=revoked)
    candidates = table.get((0, len(analyses)), ())
    expected = canonical(_np_graph("girl", "green", definite=True))[1]
    return any(canonical(p.meaning)[1] == expected for p in candidates)


def _clause_held_out(state: LearnedLanguage, utterance: str, expected: MeaningGraph, revoked=()) -> bool:
    result = interpret(utterance, state.lexicon, state.constructions, revoked=revoked)
    return result.verdict is Verdict.INTERPRETED and canonical(result.meaning)[1] == canonical(expected)[1]


def learn_all() -> tuple[LearnedLanguage, tuple[FamilyReceipt, ...]]:
    state = empty_language("construction-cal")
    teach_inventory(state)
    if state.constructions:
        raise AssertionError("construction inventory must start empty")
    receipts: list[FamilyReceipt] = []

    np, n_h = _learn_np(state)
    np_eid = "demo:construction:np"
    receipts.append(FamilyReceipt(
        "noun_phrase", np_eid, n_h, tuple(slot.name for slot in np.pattern),
        _np_held_out(state, np),
        not _np_held_out(state, np, {np_eid}) and np.liveness({np_eid}) is Liveness.DEAD,
    ))

    NP = lambda name: Slot(name, Category.NOUN, phrase="NP")  # noqa: E731
    helper = (np,)

    trans, n_h = _learn_clause(
        state,
        family_name="transitive",
        roles=(("S", NP("subj")), ("V", Slot("verb", Category.VERB)), ("O", NP("obj"))),
        template=transitive_template,
        teaching_utterance="the robot open the door",
        teaching_meaning=clause_graph("robot", "open", "door"),
        held_out_utterance="the girl push the ball",
        evidence_id="demo:construction:transitive",
        helpers=helper,
    )
    receipts.append(FamilyReceipt(
        "transitive", "demo:construction:transitive", n_h, tuple(slot.name for slot in trans.pattern),
        _clause_held_out(state, "the girl push the ball", clause_graph("girl", "push", "ball")),
        not _clause_held_out(state, "the girl push the ball", clause_graph("girl", "push", "ball"), {"demo:construction:transitive"})
        and trans.liveness({"demo:construction:transitive"}) is Liveness.DEAD,
    ))

    intr, n_h = _learn_clause(
        state,
        family_name="intransitive",
        roles=(("S", NP("subj")), ("V", Slot("verb", Category.VERB))),
        template=intransitive_template,
        teaching_utterance="the robot move",
        teaching_meaning=clause_graph("robot", "move"),
        held_out_utterance="the girl move",
        evidence_id="demo:construction:intransitive",
        helpers=helper,
    )
    receipts.append(FamilyReceipt(
        "intransitive", "demo:construction:intransitive", n_h, tuple(slot.name for slot in intr.pattern),
        _clause_held_out(state, "the girl move", clause_graph("girl", "move")),
        not _clause_held_out(state, "the girl move", clause_graph("girl", "move"), {"demo:construction:intransitive"})
        and intr.liveness({"demo:construction:intransitive"}) is Liveness.DEAD,
    ))

    passive, n_h = _learn_clause(
        state,
        family_name="passive",
        roles=(
            ("P", NP("patient")),
            ("AUX", Slot("aux", Category.AUX, lemma="was")),
            ("V", Slot("verb", Category.VERB, features=(("participle", "past"),))),
            ("BY", Slot("by", Category.PREP, lemma="by")),
            ("AG", NP("agent")),
        ),
        template=passive_template,
        teaching_utterance="the door was opened by the robot",
        teaching_meaning=passive_template({"patient": _fake_phrase("door"), "verb": _fake_reading("open", Category.VERB), "agent": _fake_phrase("robot")}),
        held_out_utterance="the ball was pushed by the girl",
        evidence_id="demo:construction:passive",
        helpers=helper,
    )
    expected_passive = _passive_expected("ball", "push", "girl")
    receipts.append(FamilyReceipt(
        "passive", "demo:construction:passive", n_h, tuple(slot.name for slot in passive.pattern),
        _clause_held_out(state, "the ball was pushed by the girl", expected_passive),
        not _clause_held_out(state, "the ball was pushed by the girl", expected_passive, {"demo:construction:passive"})
        and passive.liveness({"demo:construction:passive"}) is Liveness.DEAD,
    ))

    neg, n_h = _learn_clause(
        state,
        family_name="negation",
        roles=(
            ("S", NP("subj")),
            ("AUX", Slot("aux", Category.AUX, lemma="did")),
            ("NEG", Slot("neg", Category.NEG, lemma="not")),
            ("V", Slot("verb", Category.VERB)),
            ("O", NP("obj")),
        ),
        template=negation_template,
        teaching_utterance="the robot did not open the door",
        teaching_meaning=clause_graph("robot", "open", "door", negated=True),
        held_out_utterance="the girl did not push the ball",
        evidence_id="demo:construction:negation",
        helpers=helper,
    )
    expected_neg = clause_graph("girl", "push", "ball", negated=True)
    receipts.append(FamilyReceipt(
        "negation", "demo:construction:negation", n_h, tuple(slot.name for slot in neg.pattern),
        _clause_held_out(state, "the girl did not push the ball", expected_neg),
        not _clause_held_out(state, "the girl did not push the ball", expected_neg, {"demo:construction:negation"})
        and neg.liveness({"demo:construction:negation"}) is Liveness.DEAD,
    ))

    yesno, n_h = _learn_clause(
        state,
        family_name="yes_no_question",
        roles=(
            ("AUX", Slot("aux", Category.AUX, lemma="did")),
            ("S", NP("subj")),
            ("V", Slot("verb", Category.VERB)),
            ("O", NP("obj")),
        ),
        template=yesno_template,
        teaching_utterance="did the robot open the door",
        teaching_meaning=clause_graph("robot", "open", "door", question=True),
        held_out_utterance="did the girl push the ball",
        evidence_id="demo:construction:yesno",
        helpers=helper,
    )
    expected_yesno = clause_graph("girl", "push", "ball", question=True)
    receipts.append(FamilyReceipt(
        "yes_no_question", "demo:construction:yesno", n_h, tuple(slot.name for slot in yesno.pattern),
        _clause_held_out(state, "did the girl push the ball", expected_yesno),
        not _clause_held_out(state, "did the girl push the ball", expected_yesno, {"demo:construction:yesno"})
        and yesno.liveness({"demo:construction:yesno"}) is Liveness.DEAD,
    ))

    wh, n_h = _learn_clause(
        state,
        family_name="wh_question",
        roles=(
            ("WH", Slot("wh", Category.WH, lemma="which")),
            ("O", Slot("obj_n", Category.NOUN)),
            ("AUX", Slot("aux", Category.AUX, lemma="did")),
            ("S", Slot("subj_n", Category.PRON, lemma="it")),
            ("V", Slot("verb", Category.VERB)),
        ),
        template=wh_template,
        teaching_utterance="which door did it open",
        teaching_meaning=_wh_expected("door", "open"),
        held_out_utterance="which ball did it push",
        evidence_id="demo:construction:wh",
    )
    expected_wh = _wh_expected("ball", "push")
    receipts.append(FamilyReceipt(
        "wh_question", "demo:construction:wh", n_h, tuple(slot.name for slot in wh.pattern),
        _clause_held_out(state, "which ball did it push", expected_wh),
        not _clause_held_out(state, "which ball did it push", expected_wh, {"demo:construction:wh"})
        and wh.liveness({"demo:construction:wh"}) is Liveness.DEAD,
    ))

    return state, tuple(receipts)


# Tiny teacher-side stand-ins used only to generate registered target meanings;
# they are not inserted into the learned language state.
@dataclass(frozen=True)
class _FakeSense:
    concept: str


@dataclass(frozen=True)
class _FakeReading:
    lemma: str
    category: Category
    sense: _FakeSense


def _fake_reading(concept: str, category: Category) -> _FakeReading:
    return _FakeReading(concept, category, _FakeSense(concept))


@dataclass(frozen=True)
class _FakePhrase:
    meaning: MeaningGraph
    head_node: str = "x"


def _fake_phrase(concept: str) -> _FakePhrase:
    return _FakePhrase(_np_graph(concept))


def _passive_expected(patient: str, verb: str, agent: str) -> MeaningGraph:
    nodes = (MNode("s", "entity", agent), MNode("e", "event", verb), MNode("o", "entity", patient))
    edges = (
        MEdge("ROLE:agent", ("e",), ("s",)),
        MEdge("ROLE:patient", ("e",), ("o",)),
        MEdge("TENSE", ("e",), ("e",), "past"),
    )
    return MeaningGraph(nodes, edges, root="e")


def _wh_expected(obj: str, verb: str) -> MeaningGraph:
    nodes = (
        MNode("s", "entity", None, underspecified=True),
        MNode("e", "event", verb),
        MNode("o", "entity", obj),
        MNode("q", "question_variable", None, underspecified=True),
    )
    edges = (
        MEdge("ROLE:agent", ("e",), ("s",)),
        MEdge("ROLE:patient", ("e",), ("o",)),
        MEdge("ASKS", ("q",), ("o",)),
        MEdge("TENSE", ("e",), ("e",), "past"),
    )
    return MeaningGraph(nodes, edges, root="e")


def run() -> dict:
    state, receipts = learn_all()
    return {
        "receipt": "N1_MINIMAL_CONSTRUCTION_RECOVERY_V1",
        "study_role": "DEVELOPMENT_CALIBRATION_ONLY",
        "protected_claim_authority": False,
        "time_zero_constructions": 0,
        "teacher_information": {
            "token_lessons": len([e for e in state.information_events if e.startswith("lesson:")]),
            "aligned_family_demonstrations": len(receipts),
            "semantic_target_schemas_registered": 7,
            "note": "semantic target schemas and strongly supervised function-word/inflected-form lessons are counted teacher information",
        },
        "families": [
            {
                "family": r.family,
                "evidence_id": r.evidence_id,
                "hypothesis_count": r.hypothesis_count,
                "learned_pattern": list(r.learned_pattern),
                "held_out_composition": r.held_out_ok,
                "dead_after_own_revocation": r.dead_after_own_revocation,
            }
            for r in receipts
        ],
        "all_seven_recovered": len(receipts) == 7 and all(r.held_out_ok for r in receipts),
        "all_seven_revocable": len(receipts) == 7 and all(r.dead_after_own_revocation for r in receipts),
        "learned_construction_objects": len(state.constructions),
        "terminal": "ZERO_CONSTRUCTION_INVENTORY_RECOVERS_SEVEN_FUNCTIONAL_FAMILIES_CALIBRATION",
        "nonclaim": (
            "This is strongly supervised finite-family recovery. It shows that the seven historical construction objects need not be executable seed state "
            "for these controlled families; it does not establish unsupervised English grammar induction or protected corpus-scale coverage."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2, sort_keys=True))
