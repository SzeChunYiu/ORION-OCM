"""Check publication evidence inventory; never infer scientific acceptance.

All paths are repository-relative. Existing files and MET assertions are
necessary bookkeeping, not proof of novelty, validity or journal fit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

STATUSES = {"MET", "PARTIAL", "UNMET", "CANNOT_CHECK"}


def assess(document, repo_root):
    root = Path(repo_root).resolve()
    errors = []
    rows = []
    gates = document.get("gates") if isinstance(document, dict) else None
    if not isinstance(gates, list) or not gates:
        errors.append("nonempty gates list required")
        gates = []
    if not isinstance(document, dict) or not document.get("schema") or not document.get("scope"):
        errors.append("schema and scope required")
    seen = set()
    for index, gate in enumerate(gates):
        problems = []
        if not isinstance(gate, dict):
            errors.append(f"gate {index}: object required")
            continue
        gid = gate.get("id")
        if not isinstance(gid, str) or not gid or gid in seen:
            problems.append("unique nonempty id required")
        else:
            seen.add(gid)
        required = gate.get("required")
        if not isinstance(required, bool):
            problems.append("explicit Boolean required flag missing")
            required = True
        status = gate.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            problems.append("unknown or missing status")
        for field in ("reason", "resolution_test"):
            if not isinstance(gate.get(field), str) or not gate[field].strip():
                problems.append(f"{field} required")
        evidence = gate.get("evidence")
        receipts = []
        if not isinstance(evidence, list):
            problems.append("explicit evidence list required")
            evidence = []
        if status == "MET" and not evidence:
            problems.append("MET without evidence")
        for item in evidence:
            if not isinstance(item, str) or not item:
                problems.append("evidence paths must be nonempty strings")
                continue
            path = (root / item).resolve()
            if Path(item).is_absolute() or not path.is_relative_to(root):
                problems.append(f"evidence outside repository: {item}")
            elif not path.is_file():
                problems.append(f"missing evidence: {item}")
            else:
                data = path.read_bytes()
                if not data:
                    problems.append(f"empty evidence: {item}")
                receipts.append({"path": item, "bytes": len(data),
                                 "sha256": hashlib.sha256(data).hexdigest()})
        blocked = required and (status != "MET" or bool(problems))
        rows.append({"id": gid, "required": required, "asserted_status": status,
                     "blocks_submission": blocked, "integrity_problems": problems,
                     "evidence_receipts": receipts})
        errors.extend(f"{gid}: {p}" for p in problems)
    blocked_ids = [r["id"] for r in rows if r["blocks_submission"]]
    return {
        "schema": "ocm.publication_inventory_assessment.v1",
        "disposition": "DO_NOT_SUBMIT_YET" if errors or blocked_ids else
                       "INVENTORY_COMPLETE_REQUIRES_INDEPENDENT_SCIENTIFIC_REVIEW",
        "scientific_acceptance": "NOT_INFERRED_FROM_CHECKLIST_OR_FILE_EXISTENCE",
        "external_review": "NOT_PERFORMED_BY_THIS_TOOL",
        "inventory_errors": errors,
        "blocking_gate_ids": blocked_ids,
        "gates": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gates", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = assess(json.loads(args.gates.read_text()), args.repo_root)
    data = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x") as f:
            f.write(data)
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
