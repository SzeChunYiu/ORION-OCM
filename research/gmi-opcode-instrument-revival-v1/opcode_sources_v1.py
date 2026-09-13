"""Load the byte-pinned parent without invoking its experiment entry point."""
import ast
import hashlib
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PARENT = HERE / "raw/frozen_parent_v5.py"
PARENT_SHA = "5b6e4993a3592e9768c68c14ac5ccfddd19ce79190402f066af1c178bd3b03f0"
COMMIT = "2ea3a617283bbe0f854f11df2ec4afcd57cbd848"
VERSION = (3, 13, 12)
INSERT_BEFORE = "            frame.f_trace_opcodes = True"
ADDED_LINE = "            frame.f_trace = tracer\n"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parent():
    if sha(PARENT) != PARENT_SHA:
        raise ValueError("frozen parent source mismatch")
    spec = importlib.util.spec_from_file_location("opcode_frozen_parent_v5", PARENT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collector_source(repaired=False):
    text = PARENT.read_text()
    node = next(n for n in ast.parse(text).body
                if isinstance(n, ast.FunctionDef) and n.name == "trace_candidate_opcodes")
    original = ast.get_source_segment(text, node)
    if original.count(INSERT_BEFORE) != 1:
        raise ValueError("single intervention site missing")
    return original.replace(INSERT_BEFORE, ADDED_LINE + INSERT_BEFORE, 1) if repaired else original


def collector(module, variant):
    if variant == "original":
        return module.trace_candidate_opcodes
    if variant != "repaired":
        raise ValueError("unknown instrument variant")
    namespace = dict(vars(module))
    exec(compile(collector_source(True), "<single-setter-intervention>", "exec"), namespace)
    return namespace["trace_candidate_opcodes"]


def require_interpreter():
    if sys.implementation.name != "cpython" or tuple(sys.version_info[:3]) != VERSION:
        raise ValueError("this execution witness requires exact CPython 3.13.12")
