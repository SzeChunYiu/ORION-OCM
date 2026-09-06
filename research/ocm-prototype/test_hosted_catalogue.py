"""Actual local-provider payload control; no hosted inference."""
from pathlib import Path
import pytest


def test_pinned_codex_correctly_refuses_unsupported_builtin_surface(tmp_path):
    try:
        from hosted_codex import audit_catalogue
    except ImportError:
        pytest.fail("hosted catalogue gate is not implemented")
    receipt = audit_catalogue(tmp_path)
    assert receipt["provider_requests"] == 0
    assert receipt["captured_requests"] >= 1
    assert {t["name"] for t in receipt["tools"]} == {"update_plan", "request_user_input", "apply_patch", "view_image"}
    assert receipt["passed"] is False  # Preserved negative, never a boundary PASS.


def test_catalogue_refuses_unexpected_builtin():
    try:
        from hosted_codex import validate_catalogue
    except ImportError:
        pytest.fail("hosted catalogue gate is not implemented")
    assert validate_catalogue([{"type": "function", "name": "exec_command"}], []) is False
