"""GMI_THEORY_BASELINE_V1 tamper-evidence validator (#833 Section B capstone).

Re-derives every sha256 recorded in BASELINE_MANIFEST_V1.json from the live
tree and FAILS if any bound artifact drifted. Also re-derives the headline
counts from the bound JSONs and cross-checks the manifest's revival-ticket
register against the pinned REVIVAL_TICKETS_V1.json.

Post-freeze changes to bound artifacts are forbidden (BASELINE_V1.md §5);
they must land as supplements + a later BASELINE_MANIFEST_V<n>.json, which
this validator then checks the same way.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PKG = REPO / "research" / "gmi-833-theory-baseline-v1"
MANIFEST_V1 = PKG / "BASELINE_MANIFEST_V1.json"
GIT = "/usr/bin/git"

EXPECTED_PINNED_HEAD = "c4def870df287a476672e47219134832a0c2f380"
EXPECTED_ARTIFACT_COUNT = 132
EXPECTED_COMPONENT_COUNT = 11


def _load_manifest() -> dict:
    assert MANIFEST_V1.is_file(), "BASELINE_MANIFEST_V1.json missing"
    manifest = json.loads(MANIFEST_V1.read_text())
    assert manifest["schema"] == "GMI_833_THEORY_BASELINE_MANIFEST_V1"
    assert manifest["baseline"] == "GMI_THEORY_BASELINE_V1"
    assert manifest["parent_issue"] == 833
    return manifest


def _artifacts(manifest: dict) -> list[dict]:
    arts = [a for comp in manifest["components"] for a in comp["artifacts"]]
    assert len(arts) == manifest["bound_artifact_count"]
    return arts


def _latest_manifests() -> list[Path]:
    """All baseline manifests present, version-ordered (V1 first)."""
    paths = sorted(PKG.glob("BASELINE_MANIFEST_V*.json"))
    assert paths, "no BASELINE_MANIFEST file found"
    return paths


def _git_ls_files(package: str) -> set[str]:
    out = subprocess.run(
        [GIT, "-C", str(REPO), "ls-files", "--", package],
        check=True,
        capture_output=True,
        text=True,
    )
    return {line for line in out.stdout.splitlines() if line.strip()}


def test_manifest_pin_and_shape():
    manifest = _load_manifest()
    assert manifest["pinned_head_sha"] == EXPECTED_PINNED_HEAD
    assert manifest["claim_ceiling"] == "GMI_THEORY_BASELINE_V1_AT_PINNED_FROZEN_CORPUS_SCOPE"
    assert manifest["bound_artifact_count"] == EXPECTED_ARTIFACT_COUNT
    assert len(manifest["components"]) == EXPECTED_COMPONENT_COUNT
    assert len(manifest["assertion_dependencies"]) == 14
    forbidden = manifest["governance"]["forbidden_promotions"]
    for promo in ("ALL_GMI_THEOREMS_TRUE", "COMPLETE_GMI", "SILENT_EDIT_OF_BOUND_ARTIFACT"):
        assert promo in forbidden
    rule = manifest["arrival_absorption_rule"]["statement"]
    assert "U-NEW" in rule and "gmi-833-*" in rule


def test_every_bound_artifact_hash_matches_live_tree():
    """The freeze is tamper-evident: any drift in any bound file fails here."""
    for mpath in _latest_manifests():
        manifest = json.loads(mpath.read_text())
        for art in _artifacts(manifest):
            path = REPO / art["path"]
            assert path.is_file(), f"bound artifact deleted: {art['path']} ({mpath.name})"
            data = path.read_bytes()
            assert len(data) == art["bytes"], (
                f"bound artifact size drifted: {art['path']} ({mpath.name}): "
                f"{len(data)} != {art['bytes']}"
            )
            digest = hashlib.sha256(data).hexdigest()
            assert digest == art["sha256"], (
                f"bound artifact content drifted: {art['path']} ({mpath.name})"
            )


def test_assertion_dependencies_are_bound():
    manifest = _load_manifest()
    bound = {a["path"] for a in _artifacts(manifest)}
    for assertion, paths in manifest["assertion_dependencies"].items():
        for p in paths:
            assert p in bound, f"{assertion} references unbound artifact {p}"


def test_headline_counts_rederived_from_bound_artifacts():
    """Independent re-derivation: the counts must come from the live files,
    not from trusting the manifest numbers."""
    manifest = _load_manifest()
    vc = manifest["verified_counts"]

    def load(rel: str):
        return json.loads((REPO / rel).read_text())

    census = load("research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json")
    audit = load("research/gmi-833-corpus-census-v1/AUDIT_V1.json")
    dg2 = load("research/gmi-833-depgraph-adjudication-v1/DEPENDENCY_GRAPH_V2.json")
    cyc = load("research/gmi-833-depgraph-adjudication-v1/CYCLE_REPORT_V1.json")
    dup = load("research/gmi-833-depgraph-adjudication-v1/DUPLICATE_ADJUDICATION_V1.json")
    ovr = load("research/gmi-833-depgraph-adjudication-v1/OVERSTRONG_ADJUDICATION_V1.json")
    rag = load("research/gmi-833-depgraph-adjudication-v1/MASTER_RAG_TABLE_V1.json")
    reg2 = load("research/gmi-833-claim-discipline-v1/REGISTRATIONS_V2.json")
    res2 = load("research/gmi-833-claim-discipline-v1/RESULT_V2.json")
    tickets = load("research/gmi-833-corpus-passes-v2-v1/REVIVAL_TICKETS_V1.json")
    ogaps = load("research/gmi-833-blind-recovery-v2-v1/OPEN_GAPS.json")

    assert len(census["scientific_objects"]) == vc["census_scientific_objects"] == 22553
    assert audit["summary"]["dispositions"] == vc["census_dispositions"]
    assert audit["summary"]["dependency_cycles"] == 0

    layers = {k: len(v) for k, v in dg2["edges"].items()}
    assert layers == vc["dependency_edges_by_layer"]
    assert sum(layers.values()) == vc["dependency_edges_total"] == 357
    assert cyc["union"]["cycle_count"] == 0 and not cyc["union"]["cycles"]

    assert dup["candidate_groups"]["count"] == vc["duplicate_candidate_groups"]
    collapsed = dup["content_collapse"]["collapsed_away"]
    assert vc["content_collapse"] == {
        "from": 22553,
        "to": 22553 - collapsed,
        "collapsed_away": collapsed,
    }
    assert vc["content_collapse"]["to"] == 17258

    assert ovr["population"] == vc["overstrong_population"] == 283
    assert ovr["verdict_distribution"] == vc["overstrong_verdicts"] == {"PROPER": 283}
    assert len(rag["strata"]) == vc["master_rag_strata"] == 39

    assert len(reg2["objects"]) == vc["claim_discipline_objects_v2"] == 235
    assert res2["registered_gap_v2"] == vc["claim_discipline_registered_gap_v2"] == 0
    assert res2["field_slots"] == vc["claim_discipline_slots_v2"] == 1175

    assert len(ogaps["remaining"]) == vc["blind_recovery_open_gaps"] == 6
    assert vc["revival_tickets_total"] == 9
    assert vc["revival_tickets_closed"] == 3
    assert vc["revival_tickets_open"] == 6
    assert vc["theorem_scores_rows"] == 197
    assert vc["terminology_edits_tranche1"] == 255
    assert vc["terminology_edits_tranche2"] == 217
    assert vc["terminology_aj_lane_residual_hits"] == 35


def test_revival_register_matches_pinned_tickets():
    manifest = _load_manifest()
    tickets = json.loads(
        (REPO / "research/gmi-833-corpus-passes-v2-v1/REVIVAL_TICKETS_V1.json").read_text()
    )
    register = manifest["revival_ticket_register"]
    live_closed = {t["id"] for t in tickets["tickets"] if t.get("status") == "DONE_IN_SWEEP"}
    live_open = {t["id"] for t in tickets["tickets"] if t.get("status") is None}
    assert {t["id"] for t in register["closed"]} == live_closed
    assert {t["id"] for t in register["open"]} == live_open
    assert len(register["open"]) == 6
    # every open ticket must carry its revival chain: attribution, lever, owner
    for entry in register["open"]:
        for field in ("attribution", "lever", "owner_lane", "retest_at_original_strength"):
            assert entry[field], f"{entry['id']} missing {field}"


def test_no_unregistered_tracked_files_in_frozen_dirs():
    """Frozen packages are closed sets: a tracked file that no manifest binds
    is an unregistered post-freeze change (must arrive with a supplement +
    later manifest, which this check then accepts)."""
    accepted: set[str] = set()
    for mpath in _latest_manifests():
        accepted.update(a["path"] for a in _artifacts(json.loads(mpath.read_text())))
    for comp in _load_manifest()["components"]:
        tracked = _git_ls_files(comp["package"])
        unregistered = tracked - accepted
        assert not unregistered, (
            f"unregistered tracked files in frozen package {comp['package']}: "
            f"{sorted(unregistered)}"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
