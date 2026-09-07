"""Test-only host gates must skip before repository or worker creation."""
from types import SimpleNamespace
import pytest
from test_materialize_phase import modules


def test_git_version_skip_before_fixture_setup(tmp_path, monkeypatch):
    import test_materialize_git as fixtures
    monkeypatch.setattr(fixtures.subprocess, "run", lambda *a, **k:
                        SimpleNamespace(returncode=0, stdout=b"git version 2.99.0\n", stderr=b""))
    monkeypatch.setattr(fixtures, "command", lambda *a, **k: pytest.fail("fixture setup reached"))
    with pytest.raises(pytest.skip.Exception, match="Git 2.25.1"):
        fixtures.fixture(tmp_path)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("pin", ["python", "git"])
def test_unqualified_worker_host_skips_before_setup(tmp_path, monkeypatch, pin):
    import materialize_test_support as support
    loaded = modules()
    if pin == "python": monkeypatch.setattr(loaded["acquisition_contract"], "PYTHON", "0" * 64)
    else: monkeypatch.setattr(loaded["materialize_phase"], "GIT", "0" * 64)
    monkeypatch.setattr(support, "modules", lambda: loaded)
    monkeypatch.setattr(support, "fixture", lambda *a: pytest.fail("fixture setup reached"))
    with pytest.raises(pytest.skip.Exception, match="exact qualified Python/Git"):
        support.prepared(tmp_path, monkeypatch)
    assert list(tmp_path.iterdir()) == []
