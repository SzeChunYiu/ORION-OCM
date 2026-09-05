"""Reduced-bootstrap morphology calibration for N1/#54.

The language starts with lexical verb concepts but zero MorphRule objects.  Three
explicit paradigm observations are supplied: two regular English-style past
forms and one irregular.  The existing finite HYBRID morphology learner must
induce a productive suffix rule plus an evidence-scoped exception, generalize the
productive rule to a held-out verb, and lose the corresponding competence when
support is revoked.

This is supervised morphology calibration, not corpus-scale English acquisition.
"""
from __future__ import annotations

from ocm.kso.types import Scope
from ocm.kso.warrant import Liveness, WarrantProfile
from ocm.language.lexicon import AnalysisStatus, Category, Lexeme, Lexicon, Sense
from ocm.learning.language import morphology as MO


def empty_morph_lexicon(language: str = "lang-en-cal") -> Lexicon:
    lexicon = Lexicon()
    scope = Scope.of(language)
    for verb in ("open", "push", "jump", "see"):
        evidence = f"lesson:{language}:verb:{verb}"
        warrant = WarrantProfile.of({evidence})
        lexicon.add(
            Lexeme(
                verb,
                Category.VERB,
                (Sense(f"{language}:{verb}", verb, "event", warrant, scope=scope),),
                warrant=warrant,
                scope=scope,
            )
        )
    return lexicon


def learn_past(lexicon: Lexicon) -> tuple[MO.Induction, tuple[str, ...]]:
    pairs = (
        MO.Pair("open", "opened", "morph:open:past"),
        MO.Pair("push", "pushed", "morph:push:past"),
        MO.Pair("see", "saw", "morph:see:past"),
    )
    induction = MO.induce(pairs, MO.Strategy.HYBRID)
    ids = MO.install(
        lexicon,
        induction,
        Category.VERB,
        (("tense", "past"),),
        "learned-past",
    )
    return induction, tuple(ids)


def _reading(lexicon: Lexicon, token: str, revoked=()):
    analysis = lexicon.analyse(token, revoked)
    if analysis.status not in {AnalysisStatus.READINGS, AnalysisStatus.AMBIGUOUS}:
        return None
    return next((r for r in analysis.readings if ("tense", "past") in r.features), None)


def run() -> dict:
    lexicon = empty_morph_lexicon()
    zero_rules = len(lexicon.rules)
    induction, rule_ids = learn_past(lexicon)
    jumped = _reading(lexicon, "jumped")
    saw = _reading(lexicon, "saw")
    opened = _reading(lexicon, "opened")
    jumped_after_regular_revocation = _reading(lexicon, "jumped", {"morph:open:past"})
    saw_after_exception_revocation = _reading(lexicon, "saw", {"morph:see:past"})
    exception_rules = [r for r in lexicon.rules if r.rule_id.endswith(":exc:see")]
    productive_rules = [r for r in lexicon.rules if r.rule_id.startswith("learned-past:") and ":exc:" not in r.rule_id]
    return {
        "receipt": "N1_MINIMAL_MORPHOLOGY_RECOVERY_V1",
        "study_role": "DEVELOPMENT_CALIBRATION_ONLY",
        "protected_claim_authority": False,
        "time_zero_morph_rules": zero_rules,
        "teacher_paradigm_pairs": 3,
        "learned_rule_ids": list(rule_ids),
        "productive_rule": None if induction.rule is None else induction.rule.name,
        "covered_pairs": len(induction.covered),
        "exceptions": len(induction.exceptions),
        "held_out_jump_generalizes": jumped is not None and jumped.lemma == "jump",
        "regular_seen_open_recognized": opened is not None and opened.lemma == "open",
        "irregular_see_recognized": saw is not None and saw.lemma == "see",
        "productive_rule_objects": len(productive_rules),
        "exception_rule_objects": len(exception_rules),
        "productive_support_revocation_removes_held_out_form": jumped_after_regular_revocation is None,
        "exception_support_revocation_removes_irregular_form": saw_after_exception_revocation is None,
        "exception_live_before_revocation": bool(exception_rules) and exception_rules[0].liveness(()) is Liveness.LIVE,
        "exception_dead_after_revocation": bool(exception_rules) and exception_rules[0].liveness({"morph:see:past"}) is Liveness.DEAD,
        "terminal": "ZERO_MORPHOLOGY_RULES_RECOVER_PRODUCTIVE_PLUS_EXCEPTION_CALIBRATION",
        "nonclaim": (
            "The paradigm pairs are explicit supervised information. This calibration shows recovery, held-out productive generalization, "
            "and evidence-scoped revocation; it does not establish corpus-scale morphology induction or a Machine-Epistemics residual."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2, sort_keys=True))
