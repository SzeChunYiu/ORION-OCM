from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "research" / "orion-machine" / "reference" / "kso_thought_speech_v0.py"


def load():
    name = "kso_thought_speech_v0"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_thought_precedes_surface_realization():
    mod = load()
    r = mod.run_thought_speech_v0()
    assert r["terminal"] == "THOUGHT_TO_SPEECH_V0_CONTROLLED_GREEN"
    assert r["open_search"]["method"] == "safe-probe"
    assert r["open_search"]["surface"] == "The researcher tests the evidence."
    assert r["unsafe_search"]["method"] == "report-unknown"
    assert r["unsafe_search"]["surface"] == "The researcher reports the uncertainty."
    assert all(r["discriminator"].values())


def test_same_speaker_realizes_different_cognitive_results():
    mod = load()
    wm = mod.wm
    speaker = mod.build_speaker()
    wisdom = wm.build_demo_space()
    a = mod.think_and_speak(
        wm.TaskContext("a", frozenset({"uncertain", "search-open", "valuable-next-step"}), 0.9, 0.9, 0.1, 1),
        wisdom=wisdom,
        speaker=speaker,
    )
    b = mod.think_and_speak(
        wm.TaskContext("b", frozenset({"uncertain", "high-risk"}), 0.9, 0.0, 1.0, 0),
        wisdom=wisdom,
        speaker=speaker,
    )
    assert a.method_id != b.method_id
    assert a.semantic_frame.predicate_concept != b.semantic_frame.predicate_concept
    assert a.surface != b.surface


def test_main_returns_zero():
    mod = load()
    assert mod.main([]) == 0
