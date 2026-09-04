"""Thought -> speech V0: method selection produces the message; LanguageKSO realizes it.

This witness deliberately contains no user-text continuation path. A TaskContext is evaluated in the
Wisdom/Method KSO first. The selected method is mapped to a tiny registered semantic message, then
the Language KSO constructs a SentencePlan and surface sentence.

The purpose is architectural: speech externalizes a cognitive result rather than predicting the
input string. The finite messages are calibration-only and do not establish open-domain reasoning.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
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


wm = _load("kso_wisdom_methods_v0")
lang = _load("kso_language_v0")


@dataclass(frozen=True)
class ThoughtSpeechResult:
    task_id: str
    method_id: str
    active_principles: tuple[str, ...]
    semantic_frame: object
    sentence_plan: object
    surface: str
    trace: tuple[str, ...]


def build_speaker() -> object:
    m = lang.LanguageKSO()
    lex = (
        ("THE", "the", lang.Pos.DETERMINER),
        ("RESEARCHER", "researcher", lang.Pos.NOUN),
        ("EVIDENCE", "evidence", lang.Pos.NOUN),
        ("UNCERTAINTY", "uncertainty", lang.Pos.NOUN),
        ("TEST", "test", lang.Pos.VERB),
        ("REPORT", "report", lang.Pos.VERB),
    )
    for i, (concept, lemma, pos) in enumerate(lex):
        m.teach_lexeme("en", concept, lemma, pos, 5000 + i)
    m.teach_construction("en", "CLAUSE_TRANSITIVE", ("S", "V", "O"), 5100)
    m.teach_construction("en", "NP", ("D", "A", "N"), 5101)
    m.admit_morph_rule(
        "en",
        "PRES_3SG",
        lang.InductionReceipt("MORPH", 5102, 5, 1, 2, "LEARNED_WARRANTED", transform="ADD_S"),
    )
    return m


def message_for_method(method_id: str) -> object:
    subject = lang.NPConcept("RESEARCHER", "THE", (), lang.Number.SINGULAR)
    if method_id == "safe-probe":
        return lang.SemanticFrame(
            "en",
            subject,
            "TEST",
            lang.NPConcept("EVIDENCE", "THE", (), lang.Number.SINGULAR),
        )
    if method_id == "report-unknown":
        return lang.SemanticFrame(
            "en",
            subject,
            "REPORT",
            lang.NPConcept("UNCERTAINTY", "THE", (), lang.Number.SINGULAR),
        )
    raise ValueError(f"no registered message for method {method_id}")


def think_and_speak(task: object, *, wisdom=None, speaker=None) -> ThoughtSpeechResult:
    wisdom = wisdom or wm.build_demo_space()
    speaker = speaker or build_speaker()
    selection = wisdom.select_method(task)
    frame = message_for_method(selection.selected_method)
    generation = speaker.speak(frame)
    if generation.status != "PASS" or generation.plan is None or generation.surface is None:
        raise RuntimeError(f"language realization failed after thought: {generation.reason or generation.status}")
    trace = (
        *selection.thought_trace,
        f"message_predicate={frame.predicate_concept}",
        "sentence_sketch=" + "->".join(generation.plan.sketch),
        "surface=" + generation.surface,
    )
    return ThoughtSpeechResult(
        task.task_id,
        selection.selected_method,
        selection.active_principles,
        frame,
        generation.plan,
        generation.surface,
        trace,
    )


def run_thought_speech_v0() -> dict[str, object]:
    open_task = wm.TaskContext(
        "open-search",
        frozenset({"uncertain", "search-open", "valuable-next-step"}),
        0.9,
        0.9,
        0.1,
        2,
    )
    risky_task = wm.TaskContext(
        "unsafe-search",
        frozenset({"uncertain", "high-risk"}),
        0.9,
        0.05,
        0.95,
        0,
    )
    a = think_and_speak(open_task)
    b = think_and_speak(risky_task)
    assert a.method_id == "safe-probe"
    assert a.surface == "The researcher tests the evidence."
    assert b.method_id == "report-unknown"
    assert b.surface == "The researcher reports the uncertainty."
    assert a.sentence_plan.sketch == ("S", "V", "O")
    assert b.sentence_plan.sketch == ("S", "V", "O")

    # Same language machinery, different thought => different message. No input text exists here to
    # continue or imitate, which is the exact architectural discriminator this V0 is meant to show.
    assert a.surface != b.surface
    assert a.semantic_frame.predicate_concept != b.semantic_frame.predicate_concept

    return {
        "terminal": "THOUGHT_TO_SPEECH_V0_CONTROLLED_GREEN",
        "open_search": {
            "principles": list(a.active_principles),
            "method": a.method_id,
            "semantic_predicate": a.semantic_frame.predicate_concept,
            "sentence_sketch": list(a.sentence_plan.sketch),
            "surface": a.surface,
            "trace": list(a.trace),
        },
        "unsafe_search": {
            "principles": list(b.active_principles),
            "method": b.method_id,
            "semantic_predicate": b.semantic_frame.predicate_concept,
            "sentence_sketch": list(b.sentence_plan.sketch),
            "surface": b.surface,
            "trace": list(b.trace),
        },
        "discriminator": {
            "surface_depends_on_selected_cognitive_method": True,
            "user_text_continuation_path_absent": True,
            "sentence_plan_precedes_surface": True,
        },
        "authority": {
            "open_domain_thinking": False,
            "human_level_speech": False,
            "superiority_over_language_models": False,
            "novelty": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path)
    a = p.parse_args(argv)
    try:
        r = run_thought_speech_v0()
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"terminal": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    text = json.dumps(r, indent=2, sort_keys=True)
    if a.out:
        a.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
