"""Current engineering selection is source-bound; fixtures never attest a real run."""
from pathlib import Path
import importlib
import json
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


@pytest.fixture
def current(tmp_path, monkeypatch):
    E = importlib.import_module("engineering_receipts")
    for name in ("src", "tests", "tools"): (tmp_path / name).mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    (tmp_path / "src/example.py").write_text("value=1\n")
    config = tmp_path / E.V4.CONFIG_PATH
    config.parent.mkdir(parents=True)
    config.write_bytes((ROOT / E.V4.CONFIG_PATH).read_bytes())
    anchor = {"manifest": E.P.MANIFEST, "sha256": "fixture-only",
              "legacy_recipe_execution": "NOT_EXECUTED", "current_scientific_promotion": "NOT_ESTABLISHED"}
    monkeypatch.setattr(E.P, "verify", lambda _: anchor)
    inventory = E.V4.source_inventory(tmp_path)
    E.archive_current(tmp_path, inventory)
    run = E.DIRECTORY + "/runs/" + E.source_id(inventory) + "/" + "a" * 16
    (tmp_path / run).mkdir(parents=True)
    executions = []
    for label, spec in E.gates(tmp_path, run).items():
        n = spec["minimum_tests"]
        cases = "".join('<testcase classname="fixture_only" name="case_%s"/>' % i for i in range(n))
        (tmp_path / spec["artifact_path"]).write_text(
            '<testsuites><testsuite tests="%s" failures="0" errors="0" skipped="0">%s</testsuite></testsuites>' % (n, cases))
        (tmp_path / spec["log_path"]).write_text("Synthetic test fixture; no real execution claim.\n")
        executions.append({"label": label, "argv": spec["argv"], "artifact_path": spec["artifact_path"], "log_path": spec["log_path"], "exit_code": 0})
    receipt = E.build_record(tmp_path, run, inventory, executions, anchor)
    path = run + "/RECEIPT.json"
    (tmp_path / path).write_bytes(E.P.encoded(receipt))
    E.select(tmp_path, path)
    return E, tmp_path, path


def test_selection_verifies_all_milestones_without_promoting_history(current):
    E, root, _ = current
    for milestone in (1, 10, 12):
        result = E.verify(root, milestone)
        assert result["current_scientific_promotion"] == "NOT_ESTABLISHED"
        assert result["protected_reevaluation"] == "NOT_RUN"
        assert result["legacy_recipe_execution"] == "NOT_EXECUTED"


@pytest.mark.parametrize("mutation", ["source", "receipt", "artifact", "pointer", "extra_source", "archive"])
def test_current_binding_changes_are_refused(current, mutation):
    E, root, path = current
    if mutation == "source": (root / "src/example.py").write_text("value=2\n")
    elif mutation == "extra_source": (root / "src/added.py").write_text("value=1\n")
    elif mutation == "archive":
        r = json.loads((root / path).read_text())
        (root / r["source_archive"]["path"]).write_bytes(b"changed archive")
    elif mutation == "receipt": (root / path).write_text("{}\n")
    elif mutation == "artifact":
        r = json.loads((root / path).read_text())
        (root / r["executions"][0]["artifact_path"]).write_text("<testsuites/>")
    else:
        (root / E.CURRENT).write_text(json.dumps({"schema": E.SCHEMA, "receipt_path": "../outside", "receipt_sha256": "x"}))
    with pytest.raises((E.V4.ReceiptError, E.zipfile.BadZipFile)): E.verify(root, 1)


@pytest.mark.parametrize("mutation", ["wrong_command", "failed_exit", "missing_gate", "promotion", "no_cases", "skipped"])
def test_invalid_attestation_cannot_be_selected(current, mutation):
    E, root, path = current
    old_pointer = (root / E.CURRENT).read_bytes()
    r = json.loads((root / path).read_text())
    if mutation == "wrong_command": r["executions"][0]["argv"] = ["true"]
    elif mutation == "failed_exit": r["executions"][0]["exit_code"] = 1
    elif mutation == "missing_gate": r["executions"].pop()
    elif mutation == "promotion": r["scientific_promotion"] = "SUPPORTED"
    else:
        artifact = r["executions"][0]["artifact_path"]
        text = (root / artifact).read_text()
        text = "<testsuites/>" if mutation == "no_cases" else text.replace('skipped="0"', 'skipped="1"').replace('name="case_0"/>', 'name="case_0"><skipped/></testcase>')
        (root / artifact).write_text(text)
        r["validation_artifacts"][artifact] = E.V4.sha(root, artifact)
    (root / path).write_bytes(E.P.encoded(r))
    with pytest.raises(E.V4.ReceiptError): E.select(root, path)
    assert (root / E.CURRENT).read_bytes() == old_pointer


def test_real_frozen_v4_and_v5_bindings_verify_without_recipe_execution():
    P = importlib.import_module("engineering_predecessor")
    result = P.verify(ROOT)
    assert result["source_files"] == 302
    assert result["legacy_recipe_execution"] == "NOT_EXECUTED"
    assert result["current_scientific_promotion"] == "NOT_ESTABLISHED"
