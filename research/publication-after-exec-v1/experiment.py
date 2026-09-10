"""Harvest #165 §15 after-execution receipts already on this checkout.

Does not invent E4, a second machine, independent authorship, or an
independent scorer. Does not overwrite publication-constitution RESULT.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

SCHEMA = "ocm.publication-after-exec.result.v1"
TERMINAL = "PUBLICATION_AFTER_EXEC_RECEIPTS_PRESENT_WITH_GAPS"
ISSUE = 165
SECTION = 15

FORBIDDEN_EVIDENCE = frozenset({"E4", "E5"})
CONSTITUTION_RESULT_PATHS = (
    "research/publication-constitution-v1/RESULT.json",
    "research/publication-constitution-v2/RESULT.json",
)

AFTER_BOXES = (
    "raw_traces",
    "failures",
    "crashes_timeouts",
    "machine_readable_receipts",
    "raw_cost_vectors",
    "immutable_figure_tables",
    "exclusions_with_reasons",
    "checksum_manifest",
    "fresh_host_rerun",
    "disjoint_replication",
    "independent_scorer_checker",
    "red_team_reviewer_simulation",
    "claim_result_correspondence_review",
)

EARNED_BOXES = (
    "raw_traces",
    "failures",
    "crashes_timeouts",
    "machine_readable_receipts",
    "raw_cost_vectors",
    "immutable_figure_tables",
    "exclusions_with_reasons",
    "checksum_manifest",
    "claim_result_correspondence_review",
)

CANNOT_CHECK_STATUS = {
    "fresh_host_rerun": {
        "status": "CANNOT_CHECK_NO_SECOND_MACHINE",
        "conversion": (
            "Need a second machine / fresh host to rerun a frozen protocol. "
            "This checkout is not that host. Do not relabel same-head CI as E4."
        ),
    },
    "disjoint_replication": {
        "status": "CANNOT_CHECK_NO_E4_DISJOINT_REPLICATION",
        "conversion": (
            "E4 disjoint replication is not invented from same-host harvest "
            "or additional internal generator worlds."
        ),
    },
    "independent_scorer_checker": {
        "status": "CANNOT_CHECK_NO_INDEPENDENT_SCORER",
        "conversion": (
            "In-ecology checkers (G3.4 independent_truth, polynomial coefficient "
            "checker, math-n4 kernel) are not an independent scorer. Need a "
            "disjoint human/scorer identity."
        ),
    },
    "red_team_reviewer_simulation": {
        "status": "CANNOT_CHECK_NO_INDEPENDENT_RED_TEAM",
        "conversion": "No independent red-team reviewer simulation is in this repository.",
    },
}

# Explicitly cited receipts. Roles record which after-execution box they support.
CITED_RECEIPTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("research/cinv-audit-v1/RESULT.json", ("machine_readable_receipts", "checksum_manifest")),
    ("research/cinv-audit-v1/CORE.md", ("claim_result_correspondence_review",)),
    (
        "research/publication-constitution-v1/PROTOCOL.json",
        ("machine_readable_receipts", "checksum_manifest"),
    ),
    (
        "research/publication-constitution-v2/PROTOCOL.json",
        ("machine_readable_receipts", "checksum_manifest"),
    ),
    (
        "research/publication-constitution-v2/CORE.md",
        ("claim_result_correspondence_review",),
    ),
    ("research/g3-failure-memory-v1/RESULT.json", (
        "raw_traces",
        "failures",
        "machine_readable_receipts",
        "raw_cost_vectors",
        "exclusions_with_reasons",
        "checksum_manifest",
    )),
    ("research/g3-failure-memory-v1/CORE.md", ("claim_result_correspondence_review",)),
    ("research/g3-representation-diagnosis-v1/RESULT.json", (
        "crashes_timeouts",
        "machine_readable_receipts",
        "checksum_manifest",
    )),
    ("research/g3-representation-diagnosis-v1/CORE.md", ("claim_result_correspondence_review",)),
    ("research/g5-packed-field-v1/RESULT.json", (
        "machine_readable_receipts",
        "raw_cost_vectors",
        "immutable_figure_tables",
        "checksum_manifest",
    )),
    ("research/g5-packed-field-v1/SUMMARY.json", (
        "machine_readable_receipts",
        "immutable_figure_tables",
        "checksum_manifest",
    )),
    ("research/g5-packed-field-v1/results/scaling_raw.json", (
        "raw_cost_vectors",
        "immutable_figure_tables",
        "checksum_manifest",
    )),
    ("research/g5-packed-field-v1/CORE.md", ("claim_result_correspondence_review",)),
    ("research/g2-process-restart-v1/RESULT.json", (
        "machine_readable_receipts",
        "raw_cost_vectors",
        "checksum_manifest",
    )),
    ("research/g2-process-restart-v1/CORE.md", ("claim_result_correspondence_review",)),
    ("research/p1-causal-reuse-v1/RESULT.json", (
        "machine_readable_receipts",
        "raw_cost_vectors",
        "checksum_manifest",
    )),
    ("research/p1-causal-reuse-v1/CORE.md", ("claim_result_correspondence_review",)),
    ("research/h1-amortized-rewrite-v2/RESULT.json", (
        "failures",
        "machine_readable_receipts",
        "checksum_manifest",
    )),
    ("research/h1-amortized-rewrite-v2/CORE.md", ("claim_result_correspondence_review",)),
    ("research/h2-sparse-cognition-v1/RESULT.json", (
        "machine_readable_receipts",
        "checksum_manifest",
    )),
    ("research/h2-sparse-cognition-v1/CORE.md", ("claim_result_correspondence_review",)),
    ("research/h3-local-revision-v1/RESULT.json", ("machine_readable_receipts", "checksum_manifest")),
    ("research/h4-exact-revocation-v1/RESULT.json", ("machine_readable_receipts", "checksum_manifest")),
    ("research/h4-exact-revocation-v1/CORE.md", ("claim_result_correspondence_review",)),
    ("research/kso-general-field-v1/RESULT.json", ("machine_readable_receipts", "checksum_manifest")),
    ("research/kso-general-field-nk-v2/RESULT.json", ("machine_readable_receipts", "checksum_manifest")),
    ("research/l1-linguistic-g2-v3/RESULT.json", (
        "failures",
        "exclusions_with_reasons",
        "machine_readable_receipts",
        "checksum_manifest",
    )),
    ("research/l1-linguistic-g2-v3/CORE.md", ("claim_result_correspondence_review",)),
    ("research/l1-linguistic-g2-v2/RESULT.json", ("machine_readable_receipts", "checksum_manifest")),
    ("research/g1-duplicate-cores-v1/RESULT.json", ("machine_readable_receipts", "checksum_manifest")),
    ("research/g6-intervention-parents-v2/RESULT.json", ("machine_readable_receipts", "checksum_manifest")),
    (
        "research/issue-165-p0-disposition-v1/SHA256SUMS",
        ("checksum_manifest",),
    ),
    (
        "research/ocm-prototype/results/native-generation-diagnostic-20260906/raw/SHA256SUMS",
        ("raw_traces", "checksum_manifest"),
    ),
    (
        "research/ocm-prototype/results/native-generation-timeout-20260906/SHA256SUMS",
        ("crashes_timeouts", "checksum_manifest"),
    ),
    (
        "research/ocm-prototype/results/native-generation-diagnostic-20260906/raw/controls-final/timeout/result.json",
        ("raw_traces", "crashes_timeouts", "machine_readable_receipts", "raw_cost_vectors"),
    ),
    (
        "research/ocm-prototype/results/native-generation-diagnostic-20260906/raw/controls-final/error/result.json",
        ("raw_traces", "crashes_timeouts", "failures", "machine_readable_receipts"),
    ),
    (
        "research/ocm-prototype/results/native-generation-diagnostic-20260906/raw/controls-final/watchdog/result.json",
        ("raw_traces", "crashes_timeouts", "machine_readable_receipts"),
    ),
    (
        "research/ocm-prototype/results/native-generation-timeout-20260906/raw/timeout-localization-v4/capture-v4/explicit_macro/result.json",
        ("raw_traces", "crashes_timeouts", "machine_readable_receipts", "raw_cost_vectors"),
    ),
)

EXISTING_SHA256SUMS = (
    "research/issue-165-p0-disposition-v1/SHA256SUMS",
    "research/ocm-prototype/results/native-generation-diagnostic-20260906/raw/SHA256SUMS",
    "research/ocm-prototype/results/native-generation-timeout-20260906/SHA256SUMS",
)

CORRESPONDENCE_CAPSULES = (
    "research/cinv-audit-v1",
    "research/publication-constitution-v2",
    "research/g3-failure-memory-v1",
    "research/g3-representation-diagnosis-v1",
    "research/g5-packed-field-v1",
    "research/g2-process-restart-v1",
    "research/p1-causal-reuse-v1",
    "research/h1-amortized-rewrite-v2",
    "research/h2-sparse-cognition-v1",
    "research/h4-exact-revocation-v1",
    "research/l1-linguistic-g2-v3",
    "research/kso-general-field-v1",
    "research/g1-duplicate-cores-v1",
)

G24_TRACE_GAPS = (
    "research/g2-macro-operator-v1/RESULT.json",
    "research/g3-independent-composition-v1/RESULT.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_terminals(payload: Any) -> list[str]:
    found: list[str] = []

    def walk(obj: Any, key: str | None = None) -> None:
        if isinstance(obj, dict):
            for child_key, value in obj.items():
                walk(value, child_key)
            return
        if key in {"terminal", "execution_terminal", "cinv_terminal", "publication_terminal"}:
            text = str(obj or "").strip()
            if text and text not in found:
                found.append(text)

    walk(payload)
    return found


def parse_sha256sums(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        digest, rel = stripped.split(None, 1)
        rows.append((digest, rel))
    return rows


def verify_sha256sums(rel_path: str) -> dict[str, Any]:
    path = REPO / rel_path
    ok = 0
    missing = 0
    mismatch = 0
    for digest, rel in parse_sha256sums(path):
        target = path.parent / rel
        if not target.is_file():
            missing += 1
            continue
        if sha256_file(target) == digest:
            ok += 1
        else:
            mismatch += 1
    return {
        "path": rel_path,
        "entries": ok + missing + mismatch,
        "ok": ok,
        "missing": missing,
        "mismatch": mismatch,
        "verified": missing == 0 and mismatch == 0 and ok > 0,
    }


def inspect_cited(rel_path: str, roles: tuple[str, ...]) -> dict[str, Any]:
    path = REPO / rel_path
    if not path.is_file():
        raise FileNotFoundError(rel_path)
    record: dict[str, Any] = {
        "path": rel_path,
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "roles": list(roles),
    }
    if path.suffix == ".json":
        payload = load_json(path)
        record["json_keys"] = sorted(payload.keys()) if isinstance(payload, dict) else []
        if isinstance(payload, dict):
            if "failure_attempts_v1" in payload:
                record["failure_attempts_n"] = len(payload["failure_attempts_v1"])
            if "accounting" in payload:
                record["accounting_keys"] = sorted(payload["accounting"].keys())
            if "scaling" in payload:
                record["scaling_n"] = len(payload["scaling"])
            if "partition" in payload and isinstance(payload["partition"], dict):
                record["prior_exposed_length6_n"] = payload["partition"].get(
                    "prior_exposed_length6_n"
                )
            terminals = collect_terminals(payload)
            if terminals:
                record["terminals"] = terminals
            if "gnu_timeout_exit" in payload or "exit_code" in payload:
                record["exit_code"] = payload.get("exit_code")
                record["gnu_timeout_exit"] = payload.get("gnu_timeout_exit")
                record["supervisor_timeout"] = payload.get("supervisor_timeout")
                record["elapsed_ns"] = payload.get("elapsed_ns")
            if payload.get("jump_refused_on_timeout") is True:
                record["jump_refused_on_timeout"] = True
            held = payload.get("held_out_construction_families")
            if held is None and isinstance(payload.get("checklist"), dict):
                held = payload["checklist"].get("held_out_construction_families")
            if isinstance(held, str) and held:
                record["held_out_construction_families"] = held
            if "claim_ceiling" in payload:
                record["claim_ceiling"] = payload["claim_ceiling"]
    return record


def _inline_terminal_claims(core: str) -> list[str]:
    claims: list[str] = []
    for match in re.finditer(r"\*\*Terminal:\s*`([^`]+)`", core):
        claims.append(match.group(1).strip())
    for match in re.finditer(
        r"This capsule may support:\s*```text\s*\n([A-Z][A-Z0-9_]+)\s*\n```",
        core,
    ):
        claims.append(match.group(1).strip())
    if "PUBLICATION_CONSTITUTION_FROZEN_WITH_GAPS" in core:
        claims.append("PUBLICATION_CONSTITUTION_FROZEN_WITH_GAPS")
    return claims


def review_correspondence(rel_dir: str) -> dict[str, Any]:
    capsule = REPO / rel_dir
    core_path = capsule / "CORE.md"
    if not core_path.is_file():
        return {"capsule": rel_dir, "status": "NO_CORE"}
    core = core_path.read_text(encoding="utf-8")
    receipt_path = None
    payload = None
    for name in ("RESULT.json", "PROTOCOL.json"):
        candidate = capsule / name
        if candidate.is_file():
            receipt_path = name
            payload = load_json(candidate)
            break
    if payload is None:
        return {"capsule": rel_dir, "status": "NO_MACHINE_RECEIPT"}

    terminals = collect_terminals(payload)
    deferred = bool(re.search(r"RESULT\.json", core))
    inline = _inline_terminal_claims(core)
    present = [term for term in terminals if term and term in core]
    contradictions = [term for term in inline if term and term not in set(terminals) and term not in present]

    # Predecessor terminals are labeled as such and are allowed not to match
    # the current RESULT terminal.
    if contradictions:
        predecessor_ok = []
        for term in list(contradictions):
            if re.search(rf"Predecessor[^\n]*`{re.escape(term)}`", core) or re.search(
                rf"\*\*v[12] frozen:\*\*[^\n]*`{re.escape(term)}`", core
            ):
                predecessor_ok.append(term)
        contradictions = [term for term in contradictions if term not in predecessor_ok]

    status = "NO_CORE_TERMINAL_STRING"
    if contradictions:
        status = "CONTRADICTION"
    elif present:
        status = "MATCH"
    elif deferred and terminals:
        status = "DEFERRED_TO_RESULT"
    elif payload.get("jump_refused_on_timeout") is True and "JUMP" in core and "not" in core.lower():
        status = "MATCH_TIMEOUT_NOT_JUMP"
    elif "MISSING" in core and any("FROZEN_WITH_GAPS" in term for term in terminals):
        status = "MATCH_GAPS_DOCUMENTED"

    return {
        "capsule": rel_dir,
        "receipt": receipt_path,
        "status": status,
        "result_terminals": terminals,
        "core_inline_terminals": inline,
        "terminals_in_core": present,
        "contradictions": contradictions,
    }


def harvest_g24_trace_gaps() -> dict[str, Any]:
    rows = []
    for rel in G24_TRACE_GAPS:
        path = REPO / rel
        rows.append(
            {
                "path": rel,
                "present": path.is_file(),
                "code": "MISSING_ON_THIS_HEAD_CI_ARTIFACT",
            }
        )
    return {
        "note": (
            "MISSING_ON_THIS_HEAD_CI_ARTIFACT: G2.4/G3.1 confirmatory "
            "RESULT.json traces are CI artifacts not present on this head. "
            "Prototype raw archives and later capsules are not a substitute "
            "G2.4 trace dump."
        ),
        "rows": rows,
        "all_absent": all(not row["present"] for row in rows),
    }


def classify_boxes(
    cited: list[dict[str, Any]],
    checksums: list[dict[str, Any]],
    correspondence: list[dict[str, Any]],
    g24_gaps: dict[str, Any],
) -> dict[str, Any]:
    by_role: dict[str, list[str]] = {box: [] for box in AFTER_BOXES}
    for record in cited:
        for role in record["roles"]:
            by_role[role].append(record["path"])

    failure_attempts = next(
        (record["failure_attempts_n"] for record in cited if record.get("failure_attempts_n")),
        0,
    )
    timeout_rows = [
        record
        for record in cited
        if record.get("gnu_timeout_exit") is True or record.get("supervisor_timeout") is True
        or record.get("exit_code") in {124, -9, 7}
    ]
    scaling_n = next((record["scaling_n"] for record in cited if record.get("scaling_n")), 0)
    prior_exposed = next(
        (record["prior_exposed_length6_n"] for record in cited if "prior_exposed_length6_n" in record),
        None,
    )
    held_out = next(
        (
            record["held_out_construction_families"]
            for record in cited
            if record.get("held_out_construction_families")
        ),
        None,
    )
    checksums_ok = all(row["verified"] for row in checksums)
    contradictions = [row for row in correspondence if row["status"] == "CONTRADICTION"]
    correspondence_ok = (not contradictions) and any(
        row["status"] in {"MATCH", "DEFERRED_TO_RESULT", "MATCH_TIMEOUT_NOT_JUMP", "MATCH_GAPS_DOCUMENTED"}
        for row in correspondence
    )

    boxes: dict[str, Any] = {}
    boxes["raw_traces"] = {
        "status": "EARNED",
        "sources": by_role["raw_traces"],
        "g24_g31_confirmatory": g24_gaps,
        "note": (
            "Earned from G3.2 failure_attempts_v1 and prototype raw archives. "
            "G2.4/G3.1 confirmatory CI artifacts remain missing on this head."
        ),
        "failure_attempts_n": failure_attempts,
    }
    boxes["failures"] = {
        "status": "EARNED",
        "sources": by_role["failures"],
        "failure_attempts_n": failure_attempts,
        "negative_terminals": [
            record["terminals"]
            for record in cited
            if record.get("terminals")
            and any(
                term in {
                    "LIBRARY_ACQUISITION_EXCEEDS_LATER_SAVINGS",
                    "NO_CROSS_FAMILY_TRANSFER",
                    "COMPOSITIONAL_LANGUAGE_LEARNING_ONLY",
                }
                for term in record["terminals"]
            )
        ],
        "crash_error_exit_code": next(
            (record["exit_code"] for record in cited if record.get("exit_code") == 7),
            None,
        ),
    }
    boxes["crashes_timeouts"] = {
        "status": "EARNED",
        "sources": by_role["crashes_timeouts"],
        "retained_timeout_or_crash_n": len(timeout_rows),
        "note": (
            "Prototype timeout/error/watchdog captures plus G3.4 timeout-only "
            "diagnosis. Not a confirmatory G2.4 crash ledger on a fresh host."
        ),
    }
    boxes["machine_readable_receipts"] = {
        "status": "EARNED",
        "sources": by_role["machine_readable_receipts"],
        "n": len(by_role["machine_readable_receipts"]),
    }
    boxes["raw_cost_vectors"] = {
        "status": "EARNED",
        "sources": by_role["raw_cost_vectors"],
    }
    boxes["immutable_figure_tables"] = {
        "status": "EARNED",
        "sources": by_role["immutable_figure_tables"],
        "scaling_n": scaling_n,
    }
    boxes["exclusions_with_reasons"] = {
        "status": "EARNED",
        "sources": by_role["exclusions_with_reasons"],
        "prior_exposed_length6_n": prior_exposed,
        "held_out_construction_families": held_out,
    }
    boxes["checksum_manifest"] = {
        "status": "EARNED" if checksums_ok else "CANNOT_CHECK_CHECKSUM_MISMATCH",
        "sources": by_role["checksum_manifest"],
        "existing_sha256sums_verified": checksums_ok,
    }
    boxes["claim_result_correspondence_review"] = {
        "status": "EARNED" if correspondence_ok else "CANNOT_CHECK_CORRESPONDENCE_CONTRADICTION",
        "kind": "MECHANICAL_AUTHOR_SIDE_CORE_VS_RESULT",
        "not": "independent human reviewer",
        "n_reviewed": len(correspondence),
        "n_contradictions": len(contradictions),
    }
    for key, spec in CANNOT_CHECK_STATUS.items():
        boxes[key] = {
            "status": spec["status"],
            "conversion": spec["conversion"],
            "sources": [],
        }

    earned = [name for name in AFTER_BOXES if boxes[name]["status"] == "EARNED"]
    cannot_check = [
        name for name in AFTER_BOXES if str(boxes[name]["status"]).startswith("CANNOT_CHECK")
    ]
    if set(earned) != set(EARNED_BOXES) or boxes["checksum_manifest"]["status"] != "EARNED":
        raise RuntimeError(
            "harvest did not earn the registered after-execution set: "
            f"earned={earned} cannot_check={cannot_check}"
        )
    if failure_attempts < 1 or not timeout_rows or scaling_n < 1 or not checksums_ok:
        raise RuntimeError("required after-execution evidence missing")
    if not correspondence_ok:
        raise RuntimeError("CORE/RESULT correspondence has a contradiction")
    return {"boxes": boxes, "earned": earned, "cannot_check": cannot_check}


def run() -> dict[str, Any]:
    for rel in CONSTITUTION_RESULT_PATHS:
        if (REPO / rel).exists():
            raise RuntimeError(f"refusing to proceed while {rel} exists; this capsule must not overwrite it")

    cited = [inspect_cited(path, roles) for path, roles in CITED_RECEIPTS]
    checksums = [verify_sha256sums(path) for path in EXISTING_SHA256SUMS]
    correspondence = [review_correspondence(path) for path in CORRESPONDENCE_CAPSULES]
    g24_gaps = harvest_g24_trace_gaps()
    classified = classify_boxes(cited, checksums, correspondence, g24_gaps)

    v2 = load_json(REPO / "research/publication-constitution-v2/PROTOCOL.json")
    v1 = load_json(REPO / "research/publication-constitution-v1/PROTOCOL.json")
    if v2.get("closes_issue_144") is True:
        raise RuntimeError("constitution v2 must not close #144")
    if str(v2.get("terminal")) != "PUBLICATION_CONSTITUTION_FROZEN_WITH_GAPS":
        raise RuntimeError("constitution v2 terminal drifted")
    section16 = v2.get("section16") or v1.get("section16") or {}
    authorship = section16.get("independently_authored_families_E3")
    if not str(authorship).startswith("CANNOT_CHECK"):
        raise RuntimeError("independent authorship must remain CANNOT_CHECK")

    result = {
        "schema": SCHEMA,
        "issue": ISSUE,
        "section": SECTION,
        "terminal": TERMINAL,
        "closes_issue_144": False,
        "evidence_class": "E3_INTERNAL_GENERATOR_ONLY",
        "claim_ceiling": (
            "After-execution receipts harvested from this repository. Not E4, "
            "not a second machine, not independent authorship or independent "
            "scorer. Does not close #144. Does not promote polynomial results "
            "to general cognition. G2.4/G3.1 confirmatory traces remain "
            "MISSING_ON_THIS_HEAD_CI_ARTIFACT."
        ),
        "section16": {
            "independently_authored_families_E3": "CANNOT_CHECK_NO_INDEPENDENT_AUTHORSHIP",
            "conversion": (
                "Need a human independent author to donate world/task families; "
                "internal generators remain audit-only."
            ),
        },
        "earned": classified["earned"],
        "cannot_check": classified["cannot_check"],
        "boxes": classified["boxes"],
        "cited_receipts": cited,
        "checksum_manifest": {
            "cited_n": len(cited),
            "cited": [{"path": row["path"], "sha256": row["sha256"], "bytes": row["bytes"]} for row in cited],
            "existing_sha256sums": checksums,
        },
        "correspondence": correspondence,
        "g24_g31_raw_traces": g24_gaps,
        "constitution_not_overwritten": {
            "v1_protocol_sha256": sha256_file(REPO / "research/publication-constitution-v1/PROTOCOL.json"),
            "v2_protocol_sha256": sha256_file(REPO / "research/publication-constitution-v2/PROTOCOL.json"),
            "v2_core_sha256": sha256_file(REPO / "research/publication-constitution-v2/CORE.md"),
            "result_json_absent": list(CONSTITUTION_RESULT_PATHS),
        },
    }
    if result["evidence_class"] in FORBIDDEN_EVIDENCE:
        raise RuntimeError("must not invent E4/E5")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=HERE / "RESULT.json")
    args = parser.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "terminal": result["terminal"],
                "earned": result["earned"],
                "cannot_check": result["cannot_check"],
                "cited_n": result["checksum_manifest"]["cited_n"],
            }
        )
    )


if __name__ == "__main__":
    main()
