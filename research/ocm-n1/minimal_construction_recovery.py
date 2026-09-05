"""Reduced-bootstrap construction-family recovery for N1/#54/#55.

The historical bounded-world machine starts with seven English Construction
objects. This calibration starts with an empty construction inventory. Surface
word/category/concept lessons and semantic target schemas are explicit teacher
information; finite form-order hypotheses are learned from aligned examples.

The exact target is deliberately narrower than English acquisition: recover the
seven historical *functional families* (NP, transitive, intransitive, passive,
negation, yes/no question, wh-object question), generalize each to a held-out
lexical composition, and make each learned construction unavailable when its own
demonstration support is revoked. Function-word and inflected-form lessons are
counted; morphology is tested separately in #63.
"""
from __future__ import annotations

from dataclasses import dataclass
import itertools
from typing import Any, Mapping, Sequence

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
    state.lexicon.add(Lexeme(surface, category, senses, features=features, warrant=warrant, scope=scope))
    state.information_events.append(evidence)


def teach_inventory(state: LearnedLanguage) -> None:
    for word in ("robot", "girl", "door", "ball"):
        _teach(state, word, Category.NOUN, concept=word, node_type="entity")
    for word in ("red", "green"):
        _teach(state, word, Category.ADJ, concept=word, node_type="property")
    for word in ("open", "push", "move"):
        _teach(state, word, Category.VERB, concept=word, node_type="event", features=(("tense", "present"),))
    _teach(state, "opened", Category.VERB, concept="open", node_type="event", features=(("participle", "past"),))
    _teach(state, "pushed", Category.VERB, concept="push", node_type="event", features=(("participle", "past"),))
    for surface, category, features in (
        ("the", Category.DET, ()),
        ("was", Category.AUX, (("tense", "past"),)),
        ("did", Category.AUX, (("tense", "past"),)),
        ("not", Category.NEG, ()),
        ("by", Category.PREP, ()),
        ("which", Category.WH, ()),
        ("it", Category.PRON, ()),
    ):
        _teach(state, surface, category, features=features)


def _concept(value: Any) -> str | None:
    if isinstance(value, Phrase):
        node = next(n for n in value.meaning.nodes if n.node_id == value.head_node)
        return node.label
    return value.sense.concept if value.sense is not None else value.lemma


def _np_graph(noun: str, adjective: str | None = None, *, definite: bool = False) -> MeaningGraph:
    feats = (("definite", "yes"),) if definite else ()
    nodes = [MNode("x", "entity", noun, feats)]
    edges: list[MEdge] = []
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


def clause_graph(
    subj: str | None,
    verb: str,
    obj: str | None = None,
    *,
    negated: bool = False,
    question: bool = False,
) -> MeaningGraph:
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


def transitive_template(b: Mapping[str, Any]) -> MeaningGraph:
    return clause_graph(_concept(b["subj"]), _concept(b["verb"]) or b["verb"].lemma, _concept(b["obj"]))


def intransitive_template(b: Mapping[str, Any]) -> MeaningGraph:
    return clause_graph(_concept(b["subj"]), _concept(b["verb"]) or b["verb"].lemma)


def _passive_expected(patient: str, verb: str, agent: str) -> MeaningGraph:
    return MeaningGraph(
        (MNode("s", "entity", agent), MNode("e", "event", verb), MNode("o", "entity", patient)),
        (
            MEdge("ROLE:agent", ("e",), ("s",)),
            MEdge("ROLE:patient", ("e",), ("o",)),
            MEdge("TENSE", ("e",), ("e",), "past"),
        ),
        root="e",
    )


def passive_template(b: Mapping[str, Any]) -> MeaningGraph:
    return _passive_expected(
        _concept(b["patient"]) or "",
        _concept(b["verb"]) or b["verb"].lemma,
        _concept(b["agent"]) or "",
    )


def negation_template(b: Mapping[str, Any]) -> MeaningGraph:
    return clause_graph(_concept(b["subj"]), _concept(b["verb"]) or b["verb"].lemma, _concept(b["obj"]), negated=True)


def yesno_template(b: Mapping[str, Any]) -> MeaningGraph:
    return clause_graph(_concept(b["subj"]), _concept(b["verb"]) or b["verb"].lemma, _concept(b["obj"]), question=True)


def _wh_expected(obj: str, verb: str) -> MeaningGraph:
    return MeaningGraph(
        (
            MNode("s", "entity", None, underspecified=True),
            MNode("e", "event", verb),
            MNode("o", "entity", obj),
            MNode("q", "question_variable", None, underspecified=True),
        ),
        (
            MEdge("ROLE:agent", ("e",), ("s",)),
            MEdge("ROLE:patient", ("e",), ("o",)),
            MEdge("ASKS", ("q",), ("o",)),
            MEdge("TENSE", ("e",), ("e",), "past"),
        ),
        root="e",
    )


def wh_template(b: Mapping[str, Any]) -> MeaningGraph:
    return _wh_expected(_concept(b["obj_n"]) or "", _concept(b["verb"]) or b["verb"].lemma)


def _patterns(roles: Sequence[tuple[str, Slot]]) -> dict[str, tuple[Slot, ...]]:
    return {
        "-".join(name for name, _ in perm): tuple(slot for _, slot in perm)
        for perm in itertools.permutations(roles)
    }


def _learn_np(state: LearnedLanguage) -> tuple[Construction, int]:
    roles = (
        ("D", Slot("d", Category.DET, optional=True)),
        ("A", Slot("a", Category.ADJ, optional=True)),
        ("N", Slot("n", Category.NOUN)),
    )
    family = AQ.ConstructionFamily(
        "noun_phrase", _patterns(roles), np_template, ("the green girl",), language=state.language
    )
    evidence = "demo:construction:np"
    proposal = AQ.acquire(
        family,
        state.lexicon,
        (AQ.Demonstration("the red robot", _np_graph("robot", "red", definite=True), evidence),),
    )
    if proposal.status.value != "PASS":
        raise AssertionError(f"noun_phrase acquisition failed: {proposal.status.value}: {proposal.detail}")
    construction = Construction(
        f"{state.language}:noun_phrase:learned",
        "noun_phrase",
        family.hypotheses[proposal.payload["hypothesis"]],
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


def _learn_clause(
    state: LearnedLanguage,
    np: Construction | None,
    *,
    family_name: str,
    roles: Sequence[tuple[str, Slot]],
    template,
    teaching_utterance: str,
    teaching_meaning: MeaningGraph,
    held_out_utterance: str,
    evidence_id: str,
) -> tuple[Construction, int]:
    family = AQ.ConstructionFamily(
        family_name,
        _patterns(roles),
        template,
        (held_out_utterance,),
        language=state.language,
        helpers=() if np is None else (np,),
    )
    proposal = AQ.acquire(
        family,
        state.lexicon,
        (AQ.Demonstration(teaching_utterance, teaching_meaning, evidence_id),),
    )
    if proposal.status.value != "PASS":
        raise AssertionError(f"{family_name} acquisition failed: {proposal.status.value}: {proposal.detail}")
    construction = AQ.construction_from_proposal(family, proposal, f"{state.language}:{family_name}:learned")
    state.constructions.append(construction)
    state.information_events.append(evidence_id)
    return construction, len(family.hypotheses)


def _np_ok(state: LearnedLanguage, np: Construction, revoked=()) -> bool:
    utterance = "the green girl"
    per = [list(state.lexicon.analyse(token, revoked).readings) for token in tokenize(utterance)]
    candidates = phrase_table((np,), per, revoked=revoked).get((0, len(per)), ())
    target = canonical(_np_graph("girl", "green", definite=True))[1]
    return any(canonical(p.meaning)[1] == target for p in candidates)


def _clause_ok(state: LearnedLanguage, utterance: str, expected: MeaningGraph, revoked=()) -> bool:
    result = interpret(utterance, state.lexicon, state.constructions, revoked=revoked)
    if result.verdict not in {Verdict.INTERPRETED, Verdict.NEEDS_CONTEXT} or len(result.candidates) != 1:
        return False
    return canonical(result.candidates[0].meaning)[1] == canonical(expected)[1]


def _receipt(
    state: LearnedLanguage,
    construction: Construction,
    family: str,
    evidence: str,
    hypothesis_count: int,
    held_utterance: str,
    expected: MeaningGraph | None,
    *,
    np: bool = False,
) -> FamilyReceipt:
    held = _np_ok(state, construction) if np else _clause_ok(state, held_utterance, expected)
    after = _np_ok(state, construction, {evidence}) if np else _clause_ok(state, held_utterance, expected, {evidence})
    return FamilyReceipt(
        family,
        evidence,
        hypothesis_count,
        tuple(slot.name for slot in construction.pattern),
        held,
        not after and construction.liveness({evidence}) is Liveness.DEAD,
    )


def learn_all() -> tuple[LearnedLanguage, tuple[FamilyReceipt, ...]]:
    state = empty_language("construction-cal")
    teach_inventory(state)
    if state.constructions:
        raise AssertionError("construction inventory must start empty")
    receipts: list[FamilyReceipt] = []

    np, n = _learn_np(state)
    receipts.append(_receipt(state, np, "noun_phrase", "demo:construction:np", n, "the green girl", None, np=True))
    NP = lambda name: Slot(name, Category.NOUN, phrase="NP")  # noqa: E731

    specs = (
        (
            "transitive",
            (("S", NP("subj")), ("V", Slot("verb", Category.VERB)), ("O", NP("obj"))),
            transitive_template,
            "the robot open the door",
            clause_graph("robot", "open", "door"),
            "the girl push the ball",
            clause_graph("girl", "push", "ball"),
            "demo:construction:transitive",
            np,
        ),
        (
            "intransitive",
            (("S", NP("subj")), ("V", Slot("verb", Category.VERB))),
            intransitive_template,
            "the robot move",
            clause_graph("robot", "move"),
            "the girl move",
            clause_graph("girl", "move"),
            "demo:construction:intransitive",
            np,
        ),
        (
            "passive",
            (
                ("P", NP("patient")),
                ("AUX", Slot("aux", Category.AUX, lemma="was")),
                ("V", Slot("verb", Category.VERB, features=(("participle", "past"),))),
                ("BY", Slot("by", Category.PREP, lemma="by")),
                ("AG", NP("agent")),
            ),
            passive_template,
            "the door was opened by the robot",
            _passive_expected("door", "open", "robot"),
            "the ball was pushed by the girl",
            _passive_expected("ball", "push", "girl"),
            "demo:construction:passive",
            np,
        ),
        (
            "negation",
            (
                ("S", NP("subj")),
                ("AUX", Slot("aux", Category.AUX, lemma="did")),
                ("NEG", Slot("neg", Category.NEG, lemma="not")),
                ("V", Slot("verb", Category.VERB)),
                ("O", NP("obj")),
            ),
            negation_template,
            "the robot did not open the door",
            clause_graph("robot", "open", "door", negated=True),
            "the girl did not push the ball",
            clause_graph("girl", "push", "ball", negated=True),
            "demo:construction:negation",
            np,
        ),
        (
            "yes_no_question",
            (
                ("AUX", Slot("aux", Category.AUX, lemma="did")),
                ("S", NP("subj")),
                ("V", Slot("verb", Category.VERB)),
                ("O", NP("obj")),
            ),
            yesno_template,
            "did the robot open the door",
            clause_graph("robot", "open", "door", question=True),
            "did the girl push the ball",
            clause_graph("girl", "push", "ball", question=True),
            "demo:construction:yesno",
            np,
        ),
        (
            "wh_question",
            (
                ("WH", Slot("wh", Category.WH, lemma="which")),
                ("O", Slot("obj_n", Category.NOUN)),
                ("AUX", Slot("aux", Category.AUX, lemma="did")),
                ("S", Slot("subj_n", Category.PRON, lemma="it")),
                ("V", Slot("verb", Category.VERB)),
            ),
            wh_template,
            "which door did it open",
            _wh_expected("door", "open"),
            "which ball did it push",
            _wh_expected("ball", "push"),
            "demo:construction:wh",
            None,
        ),
    )

    for family, roles, template, teach_u, teach_m, held_u, held_m, evidence, helper_np in specs:
        construction, n = _learn_clause(
            state,
            helper_np,
            family_name=family,
            roles=roles,
            template=template,
            teaching_utterance=teach_u,
            teaching_meaning=teach_m,
            held_out_utterance=held_u,
            evidence_id=evidence,
        )
        receipts.append(_receipt(state, construction, family, evidence, n, held_u, held_m))

    return state, tuple(receipts)


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
            "note": "semantic target schemas and supervised function-word/inflected-form lessons are explicit teacher information",
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
