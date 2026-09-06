"""Real MCP/native lifecycle and namespace boundary controls."""
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest

MODEL = Path(os.environ.get(
    "OCM_HOSTED_MODEL_PATH",
    "/home/billy/orion-director-work/20260906/udpipe-g1/repeat90/ewt-train-default.udpipe",
))
MODEL_SHA = "7bc9a92586cbac6ebd599b035f2f4d686edb7b000ffbed776a93d8e4a23eeea9"


def test_public_schema_rejects_extra_outcome_fields():
    try:
        from hosted_stage import validate_items
    except ImportError:
        pytest.fail("hosted donor stage is not implemented")
    with pytest.raises(ValueError):
        validate_items([{"id": "s", "request": {"kind": "syntax", "tokens": ["A"], "gold": []}}])


def test_real_mcp_tools_persist_and_match_native_capability(tmp_path):
    try:
        from hosted_stage import stage
        from hosted_controls import exercise
        from clia_tasks import load_task
    except ImportError:
        pytest.fail("hosted donor stage is not implemented")
    if not MODEL.is_file():
        pytest.skip("explicit real model custody not present on this host")
    rows = [{"id": "s", "request": {"kind": "syntax", "tokens": ["A", "dog", "runs", "."]}},
            {"id": "p", "request": {"kind": "clia", "task": load_task("jmbl_fg_max3")}}]
    staged = stage(rows, MODEL, MODEL_SHA, tmp_path / "stage")
    receipt = asyncio.run(exercise(staged, tmp_path / "controls"))
    assert receipt["passed"] is True
    assert receipt["syntax"]["status"] == "PREDICTED"
    assert receipt["clia"]["status"] == "SOLUTION"
    assert receipt["clia_check"]["status"] == "PASS"
    assert receipt["memory_reload"]["text"] == "PUBLIC_MEMORY_CONTROL"
    assert receipt["duplicate_submit_denied"] is True
    assert receipt["custom_answer_allowed"] is True


def test_namespace_denies_outside_read_symlink_write_and_network(tmp_path):
    try:
        from hosted_stage import stage
        from hosted_controls import namespace_controls
    except ImportError:
        pytest.fail("hosted donor stage is not implemented")
    if not MODEL.is_file():
        pytest.skip("explicit real model custody not present on this host")
    rows = [{"id": "s", "request": {"kind": "syntax", "tokens": ["A"]}}]
    staged = stage(rows, MODEL, MODEL_SHA, tmp_path / "stage")
    receipt = namespace_controls(staged, tmp_path / "controls")
    assert receipt["passed"] is True
    assert all(receipt["checks"].values())
