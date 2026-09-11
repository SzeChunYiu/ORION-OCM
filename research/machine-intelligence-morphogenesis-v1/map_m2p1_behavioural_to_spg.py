"""Map the real #323 M2-P1 behavioural receipt into GMI Semantic Proposal Geometry.

This adapter is deliberately conservative.  It does not re-score the underlying
arm traces and it cannot promote the evidence beyond K1/C2.  It verifies the
reviewed source file identities, the registered pre-solution rank semantics, and
aggregate arithmetic before emitting a compact SPG evidence capsule.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import median
from typing import Any, Mapping


SOURCE_JSON = Path("research/m2-traversal-capital-v1/m2p1/records/BEHAVIOURAL_RECEIPT.json")
SOURCE_MD = Path("research/m2-traversal-capital-v1/m2p1/BEHAVIOURAL_RECEIPT.md")
SOURCE_JSON_GIT_BLOB = "e63c6dc53344111f7fbdaf7cc30092ba0ba90a6f"
SOURCE_MD_GIT_BLOB = "8bde38ec43419af18904a83b8a46e4ee084115e4"

EXPECTED_WORLDS = 29
EXPECTED_TARGETS = 2741
EXPECTED_EARLIER = 2536
EXPECTED_LATER = 202
EXPECTED_EQUAL = 3
EXPECTED_FRAC_EARLIER = 0.9252
EXPECTED_MEDIAN_BITS = 1.91


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _load_bound(path: Path, expected_blob: str) -> bytes:
    data = path.read_bytes()
    actual = git_blob_sha(data)
    if actual != expected_blob:
        raise ValueError(
            f"source identity mismatch for {path}: expected {expected_blob}, got {actual}"
        )
    return data


def _require_text(haystack: str, needle: str, label: str) -> None:
    if needle not in haystack:
        raise ValueError(f"registered source no longer states {label}: {needle!r}")


def _validate_definition(definition: str) -> None:
    required = {
        "pre-solution proposal rank": "RANK at",
        "continued/history rank": "rank_H",
        "reset/history-free rank": "rank_0",
        "fresh target guard": "absent from the developmental history",
        "leakage fail-close": "LEAKAGE_ALARM",
        "new-target interpretation": "not reuse of a stored answer",
    }
    for label, needle in required.items():
        _require_text(definition, needle, label)


def _world_aggregates(per_world: list[Mapping[str, Any]]) -> dict[str, Any]:
    if len(per_world) != EXPECTED_WORLDS:
        raise ValueError(f"expected {EXPECTED_WORLDS} worlds, got {len(per_world)}")

    world_names = [str(row.get("world")) for row in per_world]
    if len(world_names) != len(set(world_names)):
        raise ValueError("duplicate world names in source receipt")

    targets = 0
    earlier = 0
    later = 0
    all_earlier_worlds = 0
    baseline_identity_failures = []

    for row in per_world:
        try:
            t = int(row["targets"])
            e = int(row["rank_H_earlier"])
            l = int(row["rank_H_later"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"malformed per-world row: {row!r}") from exc
        if min(t, e, l) < 0 or e + l > t:
            raise ValueError(f"invalid counts in world {row.get('world')!r}")
        targets += t
        earlier += e
        later += l
        if e == t:
            all_earlier_worlds += 1
        if float(row.get("reset_equals_baseline_index_frac", -1.0)) != 1.0:
            baseline_identity_failures.append(str(row.get("world")))

    equal = targets - earlier - later
    if equal < 0:
        raise ValueError("aggregate equal-rank count became negative")

    return {
        "worlds": len(per_world),
        "targets": targets,
        "earlier": earlier,
        "later": later,
        "equal": equal,
        "all_earlier_worlds": all_earlier_worlds,
        "baseline_identity_failures": baseline_identity_failures,
    }


def build_capsule(repo_root: Path) -> dict[str, Any]:
    json_path = repo_root / SOURCE_JSON
    md_path = repo_root / SOURCE_MD

    json_bytes = _load_bound(json_path, SOURCE_JSON_GIT_BLOB)
    md_bytes = _load_bound(md_path, SOURCE_MD_GIT_BLOB)
    source = json.loads(json_bytes)
    if not isinstance(source, Mapping):
        raise ValueError("behavioural receipt must be a JSON object")

    definition = str(source.get("definition", ""))
    _validate_definition(definition)

    per_world = source.get("per_world")
    if not isinstance(per_world, list):
        raise ValueError("source receipt per_world must be a list")
    aggregate = _world_aggregates(per_world)

    expected_counts = {
        "worlds": EXPECTED_WORLDS,
        "targets": EXPECTED_TARGETS,
        "earlier": EXPECTED_EARLIER,
        "later": EXPECTED_LATER,
        "equal": EXPECTED_EQUAL,
        "all_earlier_worlds": 18,
        "baseline_identity_failures": [],
    }
    if aggregate != expected_counts:
        raise ValueError(f"aggregate source counts changed: {aggregate!r}")

    frac_earlier = float(source.get("frac_earlier_pooled"))
    median_bits = float(source.get("median_bits_saved_pooled"))
    if abs(frac_earlier - EXPECTED_FRAC_EARLIER) > 1e-12:
        raise ValueError(f"pooled earlier fraction changed: {frac_earlier}")
    if abs(median_bits - EXPECTED_MEDIAN_BITS) > 1e-12:
        raise ValueError(f"pooled median bits changed: {median_bits}")

    # Cross-check the human-readable receipt still states the same custody and
    # aggregate headline rather than silently drifting from the machine file.
    md = md_bytes.decode("utf-8")
    for needle, label in (
        ("targets                        : 2,741", "target count"),
        ("rank_H earlier than rank_0     : 2,536", "earlier count"),
        ("rank_H later                   : 202", "later count"),
        ("median bits of search saved    : 1.91", "median information shift"),
        ("m\* ∉ history", "fresh-target guard"),
        ("C2 signature", "claim rung"),
        ("nothing about K2/K3", "K2/K3 boundary"),
    ):
        _require_text(md, needle, label)

    # Source uses log2(rank_0 / rank_H) colloquially in prose, while the JSON
    # definition describes log2(rank) as a search-surprisal proxy.  We preserve
    # the source's own 1.91-bit aggregate and do not reinterpret it as a
    # normalized probability distribution.
    return {
        "schema": "GMIRealSPGEvidenceCapsuleV1",
        "evidence_id": "OCM_M2P1_HISTORY_INDUCED_SEARCH_GEOMETRY",
        "source": {
            "scope": "M2-P1 / #323",
            "machine_receipt_path": str(SOURCE_JSON),
            "machine_receipt_git_blob_sha1": SOURCE_JSON_GIT_BLOB,
            "narrative_receipt_path": str(SOURCE_MD),
            "narrative_receipt_git_blob_sha1": SOURCE_MD_GIT_BLOB,
        },
        "spg_mapping": {
            "native_candidate_space": (
                "real integrated-controller / BeamSolver proposal stream after admissibility "
                "and before target verification, exactly as registered by the source receipt"
            ),
            "semantic_candidate_map": (
                "native proposal -> canonical expression / eventual verified fresh-target solution identity"
            ),
            "semantic_target_set_per_task": (
                "singleton class containing the eventual externally verified canonical target solution m*"
            ),
            "reset_geometry": "rank_0: history-free RESET baseline proposal position",
            "continued_geometry": "rank_H: charged continued/history proposal position",
            "primary_first_hit_coordinate": "native proposal rank before target success/verification",
            "information_proxy": "source-registered log-rank search information; not treated as normalized probability",
            "verification_separate_from_proposal": True,
        },
        "freshness_and_causality_guards": {
            "target_solution_absent_from_development_history": True,
            "leakage_fail_closed_by_runner": "LEAKAGE_ALARM",
            "reset_rank_equals_recorded_baseline_index_every_target": True,
            "measurement_is_pre_solution_proposal_geometry": True,
            "library_only_explanation_excluded_by_source_lane": True,
        },
        "aggregate": {
            "worlds": aggregate["worlds"],
            "targets": aggregate["targets"],
            "continued_rank_earlier": aggregate["earlier"],
            "continued_rank_equal": aggregate["equal"],
            "continued_rank_later": aggregate["later"],
            "fraction_earlier": frac_earlier,
            "median_source_registered_bits_saved": median_bits,
            "worlds_every_target_earlier": aggregate["all_earlier_worlds"],
        },
        "developmental_attribution": {
            "candidate_capital_level": "K1",
            "claim_rung": "C2",
            "causal_attribution_terminal": "HISTORY_INDUCED_SEARCH_GEOMETRY_MEASURED_AT_REGISTERED_SCOPE",
            "k2_status": "NOT_ESTABLISHED_BY_THIS_RECEIPT",
            "k3_status": "NOT_ESTABLISHED_BY_THIS_RECEIPT",
        },
        "gmi_terminal": "REAL_OCM_SEMANTIC_PROPOSAL_GEOMETRY_SHIFT_SUPPORTED_AT_REGISTERED_SCOPE",
        "claim_ceiling": (
            "Real authored-program-search K1/C2 behavioural evidence: history changed pre-solution semantic "
            "proposal rank on fresh targets at the registered #323 scope. This is not K2/K3, not an "
            "independent-authorship replication, and not a cross-paradigm GMI law."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    capsule = build_capsule(args.repo_root.resolve())
    if args.out.exists():
        raise SystemExit("refusing to overwrite existing output")
    args.out.write_text(json.dumps(capsule, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(capsule["gmi_terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
