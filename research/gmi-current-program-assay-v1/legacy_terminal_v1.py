"""Execute original bound main/verdict functions on substituted records; no campaign."""
import ast
import contextlib
import hashlib
import io
import json
import os
import random
import tempfile
import types
from call_capture_v1 import V2
from native_source_v1 import source_bytes


def terminal(tasks, expected):
    if not expected or set(tasks) != set(expected):
        return "UNRESOLVED_INCOMPLETE"
    valid = {"INFEASIBLE_AT_REGISTERED_SCOPE", "DERIVED_NEURAL", "DERIVED_NON_NEURAL",
             "DERIVED_HYBRID", "FAMILY_COEXISTENCE"}
    if any(t.get("evidence_complete") is not True or t.get("verdict_dc2") not in valid
           for t in tasks.values()):
        return "UNRESOLVED_INCOMPLETE"
    return "COMPLETE_AT_DECLARED_REGISTER_ONLY"


def original_control(native, complete):
    data = source_bytes()["nn_nonnn_packet.py"]
    tree = ast.parse(data)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name in ("main", "verdict")]
    if {n.name for n in functions} != {"main", "verdict"}:
        raise ValueError("historical source entrypoints changed")
    calls, handles = [], []
    def retained_open(*args, **kwargs):
        handle = open(*args, **kwargs)
        handles.append(handle)
        return handle
    def measure(spec, genotype):
        calls.append("substituted_measurement_record")
        caps = dict.fromkeys(V2, 1.0 if complete else None)
        return caps, (1.0 if complete else None), dict.fromkeys(("desc", "exec", "upd", "ver"), 1)
    with tempfile.TemporaryDirectory(prefix="program-assay-legacy-") as directory:
        env = {"__name__": "legacy_functions_only", "open": retained_open, "hashlib": hashlib, "json": json,
               "random": random, "os": os, "RES": directory, "THETA": .85,
               "TASKS": ("fixture",), "RESOURCE_KEYS": ("desc", "exec", "upd", "ver"),
               "ecology": types.SimpleNamespace(INTERVENTION_FAMILY_V2=V2, REGISTRY={"fixture": {}}),
               "smooth": types.SimpleNamespace(FX_ONE=16), "morph": native.morph,
               "sha256_of": native.core.sha256_of,
               "candidates": lambda: {"registered_fixture": native.zoo.program_search(grammar=1, budget=32)},
               "family_of": lambda g: "NON_NEURAL", "measure": measure,
               "best_constant": lambda spec: (0.0, 0),
               "pareto": lambda rows: sorted(rows)}
        exec(compile(ast.Module(body=functions, type_ignores=[]),
                     "archived_nn_nonnn_packet_functions", "exec"), env)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                result = env["main"]("substituted_record_control")
        finally:
            for handle in handles:
                handle.close()
    return {"source_sha256": hashlib.sha256(data).hexdigest(),
            "substituted_calls": calls, "native_candidate_calls": 0,
            "original_full_result": result,
            "successor_terminal": terminal(result["tasks"], ("fixture",))}
