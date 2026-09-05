"""Minimal-substrate language-learning calibration for N1/#54.

Start with an empty Lexicon and no Construction instances.  General data models
(`Lexeme`, `Sense`, `ConstructionFamily`, `MeaningGraph`) and the finite
version-space acquisition algorithm remain available as cognitive substrate.
Language-specific words and clause order are supplied only as explicit teacher
evidence.

The same code learns an SVO language and a conflicting SOV artificial language.
This is a bootstrap/mechanism calibration, not a natural-language result: word
category/concept lessons are strongly supervised and the semantic role template
is registered as the task family.  Those information channels are counted.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.language import acquisition as AQ
from ocm.language.constructions import Construction, Slot
from ocm.language.interpret import Verdict, interpret
from ocm.language.lexicon import Category, Lexeme, Lexicon, Sense
from ocm.language.meaning import MEdge, MNode, MeaningGraph, canonical


@dataclass
class LearnedLanguage:
    language: str
    lexicon: Lexicon = field(default_factory=Lexicon)
    constructions: list[Construction] = field(default_factory=list)
    information_events: list[str] = field(default_factory=list)

    @property
    def language_specific_objects(self) -> int:
        return len(self.lexicon.lexemes) + len(self.lexicon.rules) + len(self.constructions)


def empty_language(language: str) -> LearnedLanguage:
    return LearnedLanguage(language)


def teach_word(
    state: LearnedLanguage,
    surface: str,
    category: Category,
    concept: str,
    node_type: str,
    evidence_id: str,
) -> None:
    """Strongly supervised lexical bootstrap event; explicitly counted as information."""
    scope = Scope.of(state.language)
    warrant = WarrantProfile.of({evidence_id})
    state.lexicon.add(
        Lexeme(
            surface,
            category,
            (Sense(f"{state.language}:{surface}:{concept}", concept, node_type, warrant, scope=scope),),
            warrant=warrant,
            scope=scope,
        )
    )
    state.information_events.append(evidence_id)


def teach_core_vocabulary(state: LearnedLanguage) -> None:
    for surface, category, concept, node_type in (
        ("robot", Category.NOUN, "robot", "entity"),
        ("girl", Category.NOUN, "girl", "entity"),
        ("door", Category.NOUN, "door", "entity"),
        ("ball", Category.NOUN, "ball", "entity"),
        ("open", Category.VERB, "open", "event"),
        ("push", Category.VERB, "push", "event"),
    ):
        teach_word(
            state,
            surface,
            category,
            concept,
            node_type,
            f"lesson:{state.language}:word:{surface}",
        )


def _sense(binding, name: str) -> str:
    reading = binding[name]
    if reading.sense is None:
        raise ValueError(f"{name} has no aligned concept")
    return reading.sense.concept


def transitive_meaning(agent: str, verb: str, patient: str) -> MeaningGraph:
    return MeaningGraph(
        (
            MNode("s", "entity", agent),
            MNode("e", "event", verb),
            MNode("o", "entity", patient),
        ),
        (
            MEdge("ROLE:agent", ("e",), ("s",)),
            MEdge("ROLE:patient", ("e",), ("o",)),
        ),
        root="e",
    )


def transitive_template(binding) -> MeaningGraph:
    return transitive_meaning(
        _sense(binding, "subj"),
        _sense(binding, "verb"),
        _sense(binding, "obj"),
    )


def transitive_family(language: str, query_family: Iterable[str]) -> AQ.ConstructionFamily:
    roles = (
        ("S", Slot("subj", Category.NOUN)),
        ("V", Slot("verb", Category.VERB)),
        ("O", Slot("obj", Category.NOUN)),
    )
    return AQ.ConstructionFamily(
        "bare_transitive",
        AQ.order_hypotheses(roles),
        transitive_template,
        tuple(query_family),
        language=language,
    )


def learn_transitive(
    state: LearnedLanguage,
    teaching_utterance: str,
    teaching_meaning: MeaningGraph,
    *,
    held_out_queries: Iterable[str],
    evidence_id: str,
) -> Construction:
    family = transitive_family(state.language, held_out_queries)
    proposal = AQ.acquire(
        family,
        state.lexicon,
        (AQ.Demonstration(teaching_utterance, teaching_meaning, evidence_id),),
    )
    if proposal.status.value != "PASS":
        raise AssertionError(f"transitive acquisition failed: {proposal.status.value}: {proposal.detail}")
    construction = AQ.construction_from_proposal(
        family,
        proposal,
        f"{state.language}:bare_transitive:learned",
    )
    state.constructions.append(construction)
    state.information_events.append(evidence_id)
    return construction


def learn_language(language: str, order: str) -> tuple[LearnedLanguage, Construction]:
    if order not in {"SVO", "SOV"}:
        raise ValueError("calibration supports SVO or SOV")
    state = empty_language(language)
    teach_core_vocabulary(state)
    teaching_meaning = transitive_meaning("robot", "open", "door")
    held = "girl push ball" if order == "SVO" else "girl ball push"
    teaching = "robot open door" if order == "SVO" else "robot door open"
    construction = learn_transitive(
        state,
        teaching,
        teaching_meaning,
        held_out_queries=(held,),
        evidence_id=f"demo:{language}:transitive-order",
    )
    return state, construction


def held_out_check(state: LearnedLanguage, utterance: str, expected: MeaningGraph) -> bool:
    result = interpret(utterance, state.lexicon, state.constructions)
    return (
        result.verdict is Verdict.INTERPRETED
        and canonical(result.meaning)[1] == canonical(expected)[1]
    )


def run() -> dict:
    en, en_c = learn_language("lang-svo", "SVO")
    sov, sov_c = learn_language("lang-sov", "SOV")
    expected = transitive_meaning("girl", "push", "ball")
    en_ok = held_out_check(en, "girl push ball", expected)
    sov_ok = held_out_check(sov, "girl ball push", expected)
    # Cross-order forms must not be accepted by the wrong learned inventory.
    en_rejects_sov = interpret("girl ball push", en.lexicon, en.constructions).verdict is Verdict.UNKNOWN_CONSTRUCTION
    sov_rejects_svo = interpret("girl push ball", sov.lexicon, sov.constructions).verdict is Verdict.UNKNOWN_CONSTRUCTION
    return {
        "receipt": "N1_MINIMAL_LANGUAGE_LEARNING_CALIBRATION_V1",
        "study_role": "DEVELOPMENT_CALIBRATION_ONLY",
        "protected_claim_authority": False,
        "time_zero_language_specific_objects": 0,
        "constitutional_or_general_prior": [
            "Category schema",
            "Lexeme/Sense/Construction/MeaningGraph object schemas",
            "finite version-space acquisition algorithm",
            "registered transitive semantic-role family/template",
        ],
        "teacher_information_channel": "explicit (surface, category, concept) word lessons + one aligned clause demonstration",
        "svo": {
            "learned_hypothesis": en_c.lineage[-1][1] if en_c.lineage else "SVO",
            "language_specific_objects_after_learning": en.language_specific_objects,
            "information_events": len(en.information_events),
            "held_out_composition": en_ok,
            "rejects_conflicting_order": en_rejects_sov,
        },
        "sov": {
            "learned_hypothesis": sov_c.lineage[-1][1] if sov_c.lineage else "SOV",
            "language_specific_objects_after_learning": sov.language_specific_objects,
            "information_events": len(sov.information_events),
            "held_out_composition": sov_ok,
            "rejects_conflicting_order": sov_rejects_svo,
        },
        "same_learning_code": True,
        "construction_warrant_revocable": (
            en_c.liveness({"demo:lang-svo:transitive-order"}) is Liveness.DEAD
            and sov_c.liveness({"demo:lang-sov:transitive-order"}) is Liveness.DEAD
        ),
        "terminal": "MINIMAL_EMPTY_LANGUAGE_INVENTORY_LEARNS_SVO_AND_SOV_CALIBRATION",
        "nonclaim": (
            "This does not establish English acquisition, unsupervised grammar induction, or language meta-learning. "
            "It establishes that the general acquisition substrate need not contain an English transitive order to learn/use/revoke a small scoped clause system."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2, sort_keys=True))
