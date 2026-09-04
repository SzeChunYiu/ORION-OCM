"""Controlled integration: the English LanguageKSO is a child fibre of RecursiveKSO.

One global revocation set is shared by the recursive organism and the language fibre. A grammar
macro exported to the parent therefore dies when its child evidence dies, while the same evidence
also stops sentence generation inside the child. Reinstatement restores both.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Sequence

HERE = Path(__file__).resolve().parent


def _load(name: str):
    if name in sys.modules:
        return sys.modules[name]
    path = HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


lang = _load("kso_language_v0")
rec = _load("recursive_kso_v0")


def build_language_fibre():
    organism = rec.RecursiveKSO()
    organism.add_scope("cognition", "DOMAIN")
    organism.add_scope("language", "SUBJECT", ("cognition",))
    organism.add_scope("english", "FIELD", ("language",))

    english = lang.LanguageKSO()
    # One live revocation state for the organism. This assignment is deliberate and load-bearing.
    english.revoked = organism.revoked
    lang._teach_demo_lexicon(english, 8000)

    clause_rec = lang.induce_clause_order(
        "en",
        (
            lang.ClauseDemo("alice", "likes", "bob", ("alice", "likes", "bob")),
            lang.ClauseDemo("robots", "help", "people", ("robots", "help", "people")),
        ),
        8100,
    )
    np_rec = lang.induce_np_order(
        "en",
        (
            lang.NPDemo("the", "red", "door", ("the", "red", "door")),
            lang.NPDemo("a", "small", "robot", ("a", "small", "robot")),
        ),
        8101,
    )
    m3 = lang.induce_morph_rule("en", "PRES_3SG", (lang.MorphDemo("walk", "walks"), lang.MorphDemo("jump", "jumps")), 8102)
    past = lang.induce_morph_rule("en", "PAST", (lang.MorphDemo("walk", "walked"), lang.MorphDemo("jump", "jumped")), 8103)
    clause = english.admit_induced_construction("en", clause_rec)
    english.admit_induced_construction("en", np_rec)
    english.admit_morph_rule("en", "PRES_3SG", m3)
    english.admit_morph_rule("en", "PAST", past)

    # Attach only after construction so the scope points at the latest immutable KnowledgeSpace value.
    organism.attach_space("english", english.space)
    grammar_macro = organism.publish_macro(
        "english",
        "language",
        (
            "lang:en:construction:CLAUSE_TRANSITIVE",
            "lang:en:construction:NP",
            "lang:en:morph:PRES_3SG",
        ),
        8200,
    )
    return organism, english, clause, grammar_macro


def run_language_recursive_demo() -> dict[str, object]:
    organism, english, clause, macro = build_language_fibre()
    frame = lang._target_frame()
    pre = english.speak(frame)
    if pre.status != "PASS" or pre.plan is None:
        raise AssertionError("integrated language fibre did not speak before revocation")
    if not organism.macro_live(macro.macro_id):
        raise AssertionError("parent grammar macro is not live before revocation")

    organism.revoke(clause.evidence_id)
    dead = english.speak(frame)
    if dead.status != "GAP_REVOKED_CLAUSE_TRANSITIVE_CONSTRUCTION":
        raise AssertionError("child speech did not stop after shared revocation")
    if organism.macro_live(macro.macro_id):
        raise AssertionError("parent macro stayed live after child grammar revocation")

    organism.reinstate(clause.evidence_id)
    post = english.speak(frame)
    if post.surface != pre.surface or not organism.macro_live(macro.macro_id):
        raise AssertionError("reinstatement did not restore child and parent together")

    return {
        "terminal": "LANGUAGE_RECURSIVE_KSO_V0_CONTROLLED_GREEN",
        "meaning": {
            "agent": frame.agent.noun_concept,
            "predicate": frame.predicate_concept,
            "patient": frame.patient.noun_concept if frame.patient else None,
            "tense": frame.tense.value,
        },
        "plan": {
            "sentence_sketch": list(pre.plan.sketch),
            "subject": list(pre.plan.slots()["S"]),
            "verb": list(pre.plan.slots()["V"]),
            "object": list(pre.plan.slots()["O"]),
            "morphology": list(pre.plan.morphology),
        },
        "surface": pre.surface,
        "organism": {
            "english_is_child_of_language": "language" in organism.scopes["english"].parents,
            "parent_macro_live_before": True,
            "parent_macro_live_after_revoke": False,
            "child_status_after_revoke": dead.status,
            "parent_and_child_restored": True,
        },
        "authority": {
            "human_level_speech": False,
            "open_domain": False,
            "novelty": False,
        },
    }


def print_human(r: dict[str, object]) -> None:
    meaning = r["meaning"]
    plan = r["plan"]
    print("Language KSO — meaning -> sketch -> detail -> surface")
    print("=" * 59)
    print("Meaning:", meaning)
    print("Sentence sketch:", " -> ".join(plan["sentence_sketch"]))
    print("Subject phrase:", " ".join(plan["subject"]))
    print("Verb phrase:", " ".join(plan["verb"]), plan["morphology"])
    print("Object phrase:", " ".join(plan["object"]))
    print("Surface:", r["surface"])
    print("After grammar-evidence revocation:", r["organism"]["child_status_after_revoke"])
    print("Reinstatement restores parent macro + speech: YES")


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        r = run_language_recursive_demo()
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"terminal": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    if a.json:
        print(json.dumps(r, indent=2, sort_keys=True))
    else:
        print_human(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
