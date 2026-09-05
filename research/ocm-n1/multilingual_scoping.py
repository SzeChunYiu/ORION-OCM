"""Scoped multilingual coexistence calibration for N1/#52.

A single persistent wrapper may learn multiple language inventories after
initialization without changing its implementation.  The inventories are scoped,
not merged by surface coincidence.  SVO and conflicting SOV systems therefore
coexist as learned structures over the same general machine substrate.

The language id is explicit context in V1; automatic language identification is
not claimed.  This is a scope/revision calibration, and a conventional
multilingual grammar registry is a sufficient parent for the mechanism.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ocm.language.acquisition import scope_check
from ocm.language.interpret import Interpretation, Verdict, interpret
from ocm.language.meaning import canonical

from minimal_language_learning import LearnedLanguage, learn_language, transitive_meaning


@dataclass
class PersistentMultilingualMachine:
    languages: dict[str, LearnedLanguage] = field(default_factory=dict)

    def learn(self, language: str, order: str) -> None:
        if language in self.languages:
            raise ValueError(f"language already registered: {language}")
        state, _ = learn_language(language, order)
        self.languages[language] = state

    def interpret(self, language: str, utterance: str, *, revoked=()) -> Interpretation:
        try:
            state = self.languages[language]
        except KeyError as exc:
            raise KeyError(f"UNKNOWN_LANGUAGE:{language}") from exc
        return interpret(utterance, state.lexicon, state.constructions, revoked=revoked)

    @property
    def language_specific_objects(self) -> int:
        return sum(state.language_specific_objects for state in self.languages.values())


def _is_expected(result: Interpretation) -> bool:
    expected = transitive_meaning("girl", "push", "ball")
    return (
        result.verdict is Verdict.INTERPRETED
        and canonical(result.meaning)[1] == canonical(expected)[1]
    )


def run() -> dict:
    machine = PersistentMultilingualMachine()
    implementation_languages_at_start = len(machine.languages)
    machine.learn("lang-svo", "SVO")
    after_first = machine.language_specific_objects
    machine.learn("lang-sov", "SOV")
    after_second = machine.language_specific_objects

    svo = machine.interpret("lang-svo", "girl push ball")
    sov = machine.interpret("lang-sov", "girl ball push")
    wrong_svo_in_sov = machine.interpret("lang-sov", "girl push ball")
    wrong_sov_in_svo = machine.interpret("lang-svo", "girl ball push")

    svo_construction = machine.languages["lang-svo"].constructions[0]
    sov_construction = machine.languages["lang-sov"].constructions[0]
    routing_scope_refuses_cross_use = (
        scope_check(svo_construction, "lang-sov") is False
        and scope_check(sov_construction, "lang-svo") is False
    )

    revoked_svo = machine.interpret(
        "lang-svo",
        "girl push ball",
        revoked={"demo:lang-svo:transitive-order"},
    )
    unaffected_sov = machine.interpret(
        "lang-sov",
        "girl ball push",
        revoked={"demo:lang-svo:transitive-order"},
    )

    unknown_terminal = None
    try:
        machine.interpret("lang-unknown", "girl push ball")
    except KeyError as exc:
        unknown_terminal = str(exc).strip("'")

    return {
        "receipt": "N1_MULTILINGUAL_SCOPING_CALIBRATION_V1",
        "study_role": "DEVELOPMENT_CALIBRATION_ONLY",
        "protected_claim_authority": False,
        "language_registrations_at_initialization": implementation_languages_at_start,
        "languages_learned_after_initialization": sorted(machine.languages),
        "same_machine_class_reused": True,
        "state_growth": {
            "after_first_language_objects": after_first,
            "after_second_language_objects": after_second,
            "second_language_added_persistently": after_second > after_first,
        },
        "semantic_equivalence_across_surface_orders": _is_expected(svo) and _is_expected(sov),
        "conflicting_surface_order_is_scope_local": (
            wrong_svo_in_sov.verdict is Verdict.UNKNOWN_CONSTRUCTION
            and wrong_sov_in_svo.verdict is Verdict.UNKNOWN_CONSTRUCTION
        ),
        "construction_scope_check_refuses_cross_language_use": routing_scope_refuses_cross_use,
        "revision_locality": {
            "revoked_language_loses_competence": revoked_svo.verdict is Verdict.UNKNOWN_CONSTRUCTION,
            "other_language_retains_competence": _is_expected(unaffected_sov),
        },
        "unknown_language_terminal": unknown_terminal,
        "explicit_language_context_required": True,
        "isolated_terminal": "PARENT_SUFFICIENT_SCOPED_MULTILINGUAL_REGISTRY",
        "nonclaim": (
            "V1 demonstrates coexistence and local revision of incompatible learned language inventories under an explicit language context. "
            "It does not perform automatic language identification, cross-language transfer, or prove a unique Machine-Epistemics multilingual mechanism."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2, sort_keys=True))
