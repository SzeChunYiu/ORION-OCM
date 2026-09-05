"""Exercise the built wheel in an empty cwd and fresh venv, without repository tests."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def installed_wheel(tmp_path_factory):
    base = tmp_path_factory.mktemp("ocm-wheel")
    source = base / "source"
    source.mkdir()
    shutil.copytree(ROOT / "src", source / "src", ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    for name in ("pyproject.toml", "LICENSE", "NOTICE"):
        shutil.copyfile(ROOT / name, source / name)
    wheelhouse = base / "wheels"
    wheelhouse.mkdir()
    # CI uses the declared build dependencies. The Work runtime also exposes an
    # installed build interpreter; no test downloads dependencies from a network.
    builder = sys.executable
    if importlib.util.find_spec("setuptools") is None or importlib.util.find_spec("wheel") is None:
        builder = os.environ.get("CODEX_PRIMARY_RUNTIME_PYTHON", builder)
    built = subprocess.run(
        [builder, "-c", "from setuptools.build_meta import build_wheel; import sys; build_wheel(sys.argv[1])", str(wheelhouse)],
        cwd=source, capture_output=True, text=True,
    )
    assert built.returncode == 0, built.stdout + built.stderr
    wheel, = wheelhouse.glob("*.whl")
    env_root = base / "venv"
    venv.EnvBuilder(with_pip=True).create(env_root)
    python = env_root / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    cli = env_root / ("Scripts/ocm.exe" if os.name == "nt" else "bin/ocm")
    environment = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
    cwd = base / "outside-repository"
    cwd.mkdir()
    installed = subprocess.run(
        [str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
        cwd=cwd, env=environment, capture_output=True, text=True,
    )
    assert installed.returncode == 0, installed.stdout + installed.stderr
    def run(args, *, stdin=None):
        return subprocess.run(
            [str(arg) for arg in args], cwd=cwd, env=environment,
            input=stdin, capture_output=True, text=True, timeout=120,
        )
    return python, cli, cwd, run


def test_clean_wheel_chat_learns_queries_and_restarts(installed_wheel):
    python, cli, cwd, run = installed_wheel
    absent = run([python, "-c", "import importlib.util; assert importlib.util.find_spec('tests') is None"])
    assert absent.returncode == 0, absent.stderr
    script = cwd / "learn.txt"
    script.write_text("is paris in france\nteach: crate = shipping container\nthe robot lifted the crate\ndid the robot lift the crate\n", encoding="utf-8")
    first = run([python, "-m", "ocm.chat", "--state", "state", "--script", script])
    assert first.returncode == 0, first.stdout + first.stderr
    assert "UNKNOWN_LEXEME" not in first.stdout
    assert "'crate' means shipping container" in first.stdout, first.stdout
    assert (cwd / "state" / "learned.json").exists()
    script.write_text("did the robot lift the crate\nis berlin in germany\n", encoding="utf-8")
    second = run([cli, "chat", "--state", "state", "--script", script])
    assert second.returncode == 0, second.stdout + second.stderr
    assert "UNKNOWN_LEXEME" not in second.stdout
    assert "said so" in second.stdout, second.stdout
    state_check = run([python, "-c", "from pathlib import Path; from ocm.chat.session import ChatSession; s=ChatSession(Path('state')); assert 'crate|N' in s.dialogue.lexicon.lexemes; assert s.dialogue.lexicon.analyse('crate').status == 'READINGS'; assert s.world.facts"])
    assert state_check.returncode == 0, state_check.stdout + state_check.stderr


@pytest.mark.parametrize("command", ["status", "demo"])
def test_repository_audit_routes_report_absent_custody_without_traceback(installed_wheel, command):
    _, cli, _, run = installed_wheel
    result = run([cli, command])
    assert result.returncode == 2, result.stdout + result.stderr
    receipt = json.loads(result.stdout)
    assert receipt["terminal"] == "CANNOT_CHECK_REPOSITORY_CUSTODY"
    assert "Traceback" not in result.stderr


def test_clean_wheel_help_describes_chat_and_audit_scopes(installed_wheel):
    _, cli, _, run = installed_wheel
    result = run([cli, "--help"])
    assert result.returncode == 0
    assert "chat" in result.stdout and "repository" in result.stdout
    chat_help = run([cli, "chat", "--help"])
    assert chat_help.returncode == 0
    assert "--knowledge-manifest" in chat_help.stdout and "--state" in chat_help.stdout


def test_installed_method_learning_needs_no_repository_or_test_imports(installed_wheel):
    _, cli, _, run = installed_wheel
    result = run([cli, "methods"])
    assert result.returncode == 0, result.stdout + result.stderr
    receipt = json.loads(result.stdout)
    assert receipt["validation"]["accepted"]
    assert receipt["revocation"] == "REUSE_REFUSED_AFTER_RESTART"
    assert receipt["external_science"] == "NOT_RUN"


def test_runtime_package_has_no_test_module_imports():
    import ast

    forbidden = []
    for path in (ROOT / "src" / "ocm").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            modules = [node.module] if isinstance(node, ast.ImportFrom) else [a.name for a in node.names] if isinstance(node, ast.Import) else []
            if any(name and (name == "tests" or name.startswith("tests.")) for name in modules):
                forbidden.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert not forbidden, forbidden


def test_installed_comparator_and_evaluation_bootstraps_use_runtime_only(installed_wheel):
    python, _, _, run = installed_wheel
    result = run([python, "-c", "from ocm.chat.session import DEFAULT_MANIFEST; from ocm.comparators.matched_parent import MatchedParent; from ocm.evaluation.m3_microworld_eval import lexicon_for_corpus; from ocm.evaluation.m4_dialogue_eval import dialogue_lexicon; from ocm.evaluation.m5_acquisition_eval import frozen_lexicon; assert MatchedParent(DEFAULT_MANIFEST).say('is paris in france') == 'Yes.'; assert lexicon_for_corpus().lexemes; assert dialogue_lexicon().lexemes; assert frozen_lexicon().lexemes"])
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("name", ["microworld", "acquisition"])
def test_runtime_seed_preserves_historical_lexemes_and_morphology(name):
    from ocm.language.bootstrap import acquisition_lexicon, microworld_lexicon
    from tests.m3.test_acquisition import _lexicon
    from tests.m3.test_microworld import _lexicon_for

    old, new = (_lexicon_for(()), microworld_lexicon()) if name == "microworld" else (_lexicon(), acquisition_lexicon())
    assert old.lexemes == new.lexemes
    assert len(old.rules) == len(new.rules)
    probes = {x.lemma for x in old.lexemes.values()} | {"saw", "held", "found", "did", "was", "opened", "pushed", "lifted", "kicked", "unknown", ""}
    for a, b in zip(old.rules, new.rules):
        for field in ("rule_id", "kind", "category", "features", "warrant", "scope", "lemmas"):
            assert getattr(a, field) == getattr(b, field)
        assert {p: (a.apply(p), a.analyse(p)) for p in probes} == {p: (b.apply(p), b.analyse(p)) for p in probes}
    assert {p: old.analyse(p) for p in probes} == {p: new.analyse(p) for p in probes}


def test_packaged_manifest_is_byte_identical_to_its_registered_source():
    import hashlib
    from ocm.data import default_manifest_path

    assert default_manifest_path().read_bytes() == (ROOT / "research/ocm-m6/KNOWLEDGE_MANIFEST_V1.json").read_bytes()
    custody = json.loads((ROOT / "src/ocm/data/RESOURCE_CUSTODY_V1.json").read_text())
    for source, expected in custody["source_sha256"].items():
        assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == expected


def test_missing_or_tampered_packaged_manifest_cannot_silently_seed_an_empty_world(tmp_path, monkeypatch):
    from ocm import data

    monkeypatch.setattr(data, "files", lambda _: tmp_path)
    with pytest.raises(FileNotFoundError):
        data.default_manifest_path()
    (tmp_path / data.MANIFEST_NAME).write_text('{"facts": []}')
    with pytest.raises(ValueError, match="CANNOT_CHECK_PACKAGED_RESOURCE_CUSTODY"):
        data.default_manifest_path()


def test_selected_manifest_supplies_its_own_vocabulary(tmp_path):
    from ocm.chat.session import ChatSession

    manifest = tmp_path / "custom.json"
    manifest.write_text(json.dumps({"documents": [{"source_id": "custom", "title": "Custom", "licence": "Apache-2.0", "kind": "hand_authored", "revision": "1"}], "facts": [{"fact_id": "custom:animal", "subject": "capybara", "relation": "IS_A", "object": "animal", "topic": "biology", "sources": ["custom"], "verified_by": "curator", "gloss": "a capybara is an animal"}]}))
    session = ChatSession(tmp_path / "state", manifest=manifest)
    assert "capybara|N" in session.dialogue.lexicon.lexemes
    assert "geo:paris:france" not in session.world.facts


def test_each_default_session_rechecks_resource_custody_after_import(tmp_path, monkeypatch):
    from ocm import data
    from ocm.chat import session as chat

    package_data = tmp_path / "package-data"
    package_data.mkdir()
    manifest = package_data / data.MANIFEST_NAME
    manifest.write_bytes(data.default_manifest_path().read_bytes())
    monkeypatch.setattr(data, "files", lambda _: package_data)
    monkeypatch.setattr(chat, "DEFAULT_MANIFEST", manifest)
    assert chat.ChatSession(tmp_path / "before", manifest=manifest).world.facts
    manifest.write_text('{"facts": [], "documents": []}')
    with pytest.raises(ValueError, match="CANNOT_CHECK_PACKAGED_RESOURCE_CUSTODY"):
        chat.ChatSession(tmp_path / "after", manifest=manifest)
