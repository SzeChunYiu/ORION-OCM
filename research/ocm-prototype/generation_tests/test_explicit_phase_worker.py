"""Mocked instrumentation controls; no native solver calls."""
import importlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
D = importlib.import_module("explicit_phase_worker")
W = importlib.import_module("clia_worker")


def fake(log, fail=None):
    class Solver:
        def __init__(self): log.append(("solver",))
        def setOption(self, key, value): log.append(("option", key, value))
        def getStatistics(self): log.append(("statistics",)); return []
    class Command:
        def __init__(self, index): self.index = index
        def isNull(self): return self.index == 2
        def invoke(self, solver, symbols):
            log.append(("invoke", self.index))
            if fail == "invoke": raise RuntimeError("mock interruption")
            return "(define-fun f ((x Int)) Int x)" if self.index == 1 else ""
    class Parser:
        def __init__(self, solver): self.index = 0; log.append(("parser",))
        def setStringInput(self, *args): log.append(("input", *args))
        def getSymbolManager(self): return "symbols"
        def nextCommand(self):
            log.append(("parse", self.index))
            if fail == "parse": raise RuntimeError("mock interruption")
            c = Command(self.index); self.index += 1; return c
    return SimpleNamespace(Solver=Solver, InputParser=Parser, InputLanguage=SimpleNamespace(SYGUS_2_1="sygus"))


def test_same_payload_options_native_calls_and_response(monkeypatch, capsys):
    a, b = [], []
    monkeypatch.setattr(D.metadata, "version", lambda name: "1.3.4")
    monkeypatch.setitem(sys.modules, "cvc5", fake(a))
    expected = W.synthesize({"sygus": "exact input"}, 5000)
    monkeypatch.setitem(sys.modules, "cvc5", fake(b))
    actual = D.synthesize({"sygus": "exact input"}, 5000)
    assert actual == expected and a == b
    events = [json.loads(line) for line in capsys.readouterr().err.splitlines()]
    assert events[0]["phase"] == "import.before" and events[-1]["phase"] == "statistics.after"
    assert sum(e["phase"] == "invoke.before" for e in events) == 2
    assert all(e["pid"] > 0 and e["monotonic_ns"] > 0 for e in events)


@pytest.mark.parametrize(("failure", "boundary"), [("parse", "next_command.before"), ("invoke", "invoke.before")])
def test_interruption_retains_before_event(monkeypatch, capsys, failure, boundary):
    monkeypatch.setattr(D.metadata, "version", lambda name: "1.3.4")
    monkeypatch.setitem(sys.modules, "cvc5", fake([], failure))
    with pytest.raises(RuntimeError): D.synthesize({"sygus": "input"}, 5000)
    events = [json.loads(line) for line in capsys.readouterr().err.splitlines()]
    assert events[-1]["phase"] == boundary and events[-1]["command_index"] == 0


def test_event_is_flushed_before_abrupt_process_exit():
    code = "import os; from explicit_phase_worker import phase; phase('test.before'); os._exit(17)"
    proc = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 17 and proc.stdout == ""
    assert json.loads(proc.stderr)["phase"] == "test.before"
