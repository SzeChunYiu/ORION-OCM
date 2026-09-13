"""Pinned byte authority; compile definitions and inspect them, never run candidates."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from frozen_contract_v1 import require, same, sha, strict_json

HERE = Path(__file__).resolve().parent
FROZEN = HERE / "raw/frozen"
HARNESS = "nn_nonnn_point_parity3_experiment_v6.py"
PREREG = "NN_NONNN_POINT_PARITY3_PREREG_V6.json"
VERSIONS = ("3.11.15", "3.12.3", "3.13.12")
BINDING_SHA = "d14c26c7e80e5c333c20f4b3dd3b10975d8b4bf39e16de7d47f2ab840e5f0d18"


def packet_name(version):
    require(version in VERSIONS, "unregistered historical version")
    return "NN_NONNN_POINT_PARITY3_RESULT_V6_claude-code-remote-container_CPython" + version + ".json"


def verify_inputs(base=HERE):
    raw = (base / "FROZEN_INPUTS_V1.json").read_bytes()
    require(sha(raw) == BINDING_SHA, "input authority drift")
    binding = strict_json(raw)
    for relative, row in binding["files"].items():
        data = (base / relative).read_bytes()
        require(sha(data) == row["sha256"] and len(data) == row["bytes"],
                "frozen input drift: " + relative)
    return binding


def load_authority(base=HERE):
    binding = verify_inputs(base)
    directory = base / "raw/frozen"
    path = directory / HARNESS
    prereg = strict_json((directory / PREREG).read_bytes())
    spec = importlib.util.spec_from_file_location("gmi_v6_frozen_definitions", path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    module.validate_preregistration(prereg)
    same(module.candidate_identity_record()["byte_identical_to_parent"], True,
         "source-parent candidate identity drift")
    return binding, prereg, module


def read_packet(version, base=HERE):
    verify_inputs(base)
    return strict_json((base / "raw/frozen" / packet_name(version)).read_bytes())
