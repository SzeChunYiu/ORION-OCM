"""Real local provider catalogue controls; no hosted model inference."""
import pytest


def test_claude_removes_builtin_file_shell_and_network_tools(tmp_path):
    try:
        from hosted_claude import audit_catalogue
    except ImportError:
        pytest.fail("Claude catalogue gate is not implemented")
    r = audit_catalogue(tmp_path)
    assert r["hosted_inference_requests"] == 0
    assert r["captured_requests"] >= 1
    assert r["passed"] is True
    assert r["unexpected_tools"] == []
    assert r["dummy_auth_verified"] is True
    assert set(r["captured_models"]) == {"claude-fable-5"}


def test_claude_catalogue_rejects_every_extra_or_missing_tool():
    try:
        from hosted_claude import catalogue_verdict
    except ImportError:
        pytest.fail("Claude catalogue gate is not implemented")
    assert catalogue_verdict([{"name": "Read"}], [])["passed"] is False
    assert catalogue_verdict([], ["mcp__g1__public_task"])["passed"] is False


def test_claude_sees_exact_native_mcp_catalogue(tmp_path):
    from hosted_claude import audit_catalogue
    from hosted_stage import stage, mcp_config
    from hosted_tools import TOOL_NAMES
    from clia_tasks import load_task
    from test_hosted_native import MODEL, MODEL_SHA
    if not MODEL.is_file():
        pytest.skip("explicit real model custody not present")
    items = [{"id": "s", "request": {"kind": "syntax", "tokens": ["A", "dog", "runs", "."]}},
             {"id": "p", "request": {"kind": "clia", "task": load_task("jmbl_fg_max3")}}]
    staged = stage(items, MODEL, MODEL_SHA, tmp_path / "stage")
    expected = ["mcp__g1__" + name for name in TOOL_NAMES]
    r = audit_catalogue(tmp_path / "audit", mcp_config=mcp_config(staged), expected_names=expected)
    assert r["passed"] is True
    assert r["unexpected_tools"] == []
    assert r["missing_tools"] == []
