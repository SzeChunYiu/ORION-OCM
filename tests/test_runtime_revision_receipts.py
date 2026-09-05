"""Current receipt verification cannot silently inherit historical authority or bindings."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("revision_receipt_tests", ROOT / "tools/runtime_revision_receipts.py")
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


def save(root, rel, data):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


@pytest.fixture
def evidence(tmp_path, monkeypatch):
    root = tmp_path
    source = "src/ocm/engine.py"
    path = root / source
    path.parent.mkdir(parents=True)
    path.write_text("historical engine\n")
    parent_source = R.sha(root, source)
    save(root, "research/historical.json", {"outcome": "HISTORICAL_PROTECTED"})
    configs, old = {}, {}
    for milestone in (1, 2, 12):
        paths = [source, "research/historical.json"]
        if milestone == 2:
            paths.append("docs/provenance/M1_RECEIPT_V1.json")
        if milestone == 12:
            paths.append("docs/provenance/M2_RECEIPT_V1.json")
        rel = f"docs/provenance/M{milestone}_RECEIPT_V1.json"
        old[milestone] = {"receipt": f"M{milestone}_RECEIPT_V1", "terminal": "OLD_SUPPORTED",
                          "bound_files": {p: R.sha(root, p) for p in paths},
                          "deterministic_results": {"old_protected_result": 7}}
        save(root, rel, old[milestone])
        configs[str(milestone)] = {
            "historical_path": rel, "historical_sha256": R.sha(root, rel),
            "successor_path": f"docs/provenance/{R.REVISION}/M{milestone}_CURRENT.json",
            "terminal": "CURRENT_REFERENCE_ONLY", "replay_path": None,
        }
    replay = f"docs/provenance/{R.REVISION}/M12_REPLAY.json"
    configs["12"]["replay_path"] = replay
    save(root, replay, {"study_status": "REFERENCE_REPLAY_AFTER_RUNTIME_REVISION",
                        "revalidation": {"terminal": "CURRENT_REFERENCE_ONLY"},
                        "deterministic": {"new_reference_result": 7},
                        "exit_gate_before_replication": "CANNOT_CHECK", "cannot_check": {}})
    config = {"revision": R.REVISION, "historical_parent_commit": R.PARENT_COMMIT,
              "authority": "Historical custody and current replay are separate.",
              "affected_sources": {source: parent_source}, "revision_files": [R.CONFIG_PATH],
              "milestones": configs}
    save(root, R.CONFIG_PATH, config)
    monkeypatch.setattr(R, "CONFIG_SHA256", R.sha(root, R.CONFIG_PATH))
    path.write_text("current engine\n")

    def recipe(self, milestone):
        def fresh():
            result = copy.deepcopy(old[milestone])
            result["bound_files"] = {p: R.sha(root, p) for p in result["bound_files"]}
            return result
        return fresh, tuple(old[milestone]["bound_files"])
    monkeypatch.setattr(R.CurrentReceipts, "_recipe", recipe)
    before = {v["historical_path"]: (root / v["historical_path"]).read_bytes() for v in configs.values()}
    return root, config, before


def write_all(evidence):
    root, _, _ = evidence
    current = R.CurrentReceipts(root)
    for i in (1, 2, 12):
        current.write(i)
    return current


def test_successors_bind_current_sources_and_preserve_historical_bytes(evidence):
    root, config, before = evidence
    write_all(evidence)
    R.CurrentReceipts(root).verify(12)
    second = R.read_json(root, config["milestones"]["2"]["successor_path"])
    historical_dependency = config["milestones"]["1"]["historical_path"]
    current_dependency = config["milestones"]["1"]["successor_path"]
    assert second["dependency_aliases"] == {historical_dependency: current_dependency}
    assert current_dependency in second["bound_files"] and historical_dependency not in second["bound_files"]
    assert second["historical_reference"]["terminal_at_that_revision"] == "OLD_SUPPORTED"
    assert second["terminal"] == "CURRENT_REFERENCE_ONLY"
    assert second["legacy_recipe_recheck"]["matches_historical_payload"]
    assert second["source_changes"]["src/ocm/engine.py"]["current"] != second["source_changes"]["src/ocm/engine.py"]["at_historical_parent"]
    assert all((root / p).read_bytes() == content for p, content in before.items())


@pytest.mark.parametrize("missing", [1, 2, 12])
def test_missing_active_successor_never_falls_back_to_original(evidence, missing):
    root, config, _ = evidence
    write_all(evidence)
    (root / config["milestones"][str(missing)]["successor_path"]).unlink()
    with pytest.raises(R.ReceiptError, match="MISSING required evidence"):
        R.CurrentReceipts(root).verify(12)


@pytest.mark.parametrize("field,value", [("terminal", "OLD_SUPPORTED"),
                                         ("revision", "other_revision"),
                                         ("dependency_aliases", {}),
                                         ("current_replay", {"status": "PROTECTED_SUPPORTED"})])
def test_mutated_or_relabelled_successor_is_rejected(evidence, field, value):
    root, config, _ = evidence
    write_all(evidence)
    rel = config["milestones"]["12"]["successor_path"]
    data = R.read_json(root, rel)
    data[field] = value
    save(root, rel, data)
    with pytest.raises(R.ReceiptError, match="successor DRIFT"):
        R.CurrentReceipts(root).verify(12)


def test_mutated_dependency_is_rejected_even_if_parent_hash_is_updated(evidence):
    root, config, _ = evidence
    write_all(evidence)
    child = config["milestones"]["1"]["successor_path"]
    body = R.read_json(root, child)
    body["legacy_recipe_recheck"]["payload"]["deterministic_results"]["old_protected_result"] = 999
    save(root, child, body)
    parent = config["milestones"]["2"]["successor_path"]
    parent_body = R.read_json(root, parent)
    parent_body["bound_files"][child] = R.sha(root, child)
    save(root, parent, parent_body)
    with pytest.raises(R.ReceiptError, match="M1 successor DRIFT"):
        R.CurrentReceipts(root).verify(2)


@pytest.mark.parametrize("target", ["source", "historical_receipt", "historical_artifact", "replay_label", "config"])
def test_changed_evidence_fails_closed(evidence, target):
    root, config, _ = evidence
    write_all(evidence)
    if target == "source":
        (root / "src/ocm/engine.py").write_text("unreviewed later engine\n")
    elif target == "historical_receipt":
        save(root, config["milestones"]["1"]["historical_path"], {"terminal": "new"})
    elif target == "historical_artifact":
        save(root, "research/historical.json", {"outcome": "changed"})
    elif target == "config":
        revised = copy.deepcopy(config)
        revised["historical_parent_commit"] = "0" * 40
        save(root, R.CONFIG_PATH, revised)
    else:
        rel = config["milestones"]["12"]["replay_path"]
        replay = R.read_json(root, rel)
        replay["study_status"] = "PROTECTED"
        save(root, rel, replay)
    with pytest.raises(R.ReceiptError):
        R.CurrentReceipts(root).verify(12)


def test_write_is_idempotent_and_never_overwrites_changed_evidence(evidence):
    root, config, _ = evidence
    current = write_all(evidence)
    rel = config["milestones"]["1"]["successor_path"]
    before = (root / rel).read_bytes()
    R.CurrentReceipts(root).write(1)
    assert (root / rel).read_bytes() == before
    (root / "src/ocm/engine.py").write_text("later revision\n")
    with pytest.raises(R.ReceiptError):
        current.write(1)
    assert (root / rel).read_bytes() == before


def test_no_argument_command_refuses_to_write_historical_receipt(evidence):
    root, _, before = evidence
    code = R.revision_main(root, [], 1, lambda: pytest.fail("recipe must not run"), ())
    assert code == 2
    assert all((root / p).read_bytes() == content for p, content in before.items())


def test_actual_manifest_pins_all_original_receipts_and_reference_scope():
    config = json.loads((ROOT / R.CONFIG_PATH).read_text())
    # A concurrent upstream revision legitimately uses newer receipts at the
    # shared paths. Check original bytes in the exact, verified local-parent
    # archive; never repin the original manifest to the newer observations.
    spec = importlib.util.spec_from_file_location("current_custody", ROOT / "tools/runtime_revision_receipts_v4.py")
    current = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(current)
    snapshot = current.ParentSnapshot(ROOT, current.read_json(ROOT, current.CONFIG_PATH))
    for i in range(1, 13):
        item = config["milestones"][str(i)]
        assert hashlib.sha256(snapshot.contents[item["historical_path"]]).hexdigest() == item["historical_sha256"]
    assert config["milestones"]["11"]["terminal"] == "M11_REFERENCE_REVALIDATED__HISTORICAL_ADOPTION_CELLS_REOPENED"
    assert config["milestones"]["12"]["terminal"] == "M12_REFERENCE_REPLAY__PROTECTED_REEVALUATION_REQUIRED"
