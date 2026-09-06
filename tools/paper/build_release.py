#!/usr/bin/env python3
"""Build or verify the manuscript release package binding (RELEASE_PLAN.md §1–2).

  python tools/paper/build_release.py            # write docs/paper/release/SHA256SUMS, RELEASE_MANIFEST.json and docs/provenance/PAPER_RELEASE_RECEIPT_V1.json
  python tools/paper/build_release.py --verify   # recompute and compare; exit 1 on any drift

Package = every file under docs/paper/manuscript/ plus every ORION-OCM path named in the claims map's
Source column (receipts, evaluation results, registries).  ORION-V2 paths (prefix ``V2:``) are recorded
by name only, with the ORION-V2 commit the manuscript names, because they are not in this repository.
The manifest lists, for every claims row, the phrase, the source file and the check clause; the
deterministic block is the claim-verification count (rows, OK) re-run at build time.  No claim is made
here beyond byte identity; the persistent identifier is the operator's action (RELEASE_PLAN.md §3).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAN = ROOT / "docs" / "paper" / "manuscript"
OUT = ROOT / "docs" / "paper" / "release"
RECEIPT = ROOT / "docs" / "provenance" / "PAPER_RELEASE_RECEIPT_V1.json"
V2_COMMIT_NOTE = "ORION-V2 paths are bound by the batch documents' merge commits named in main.md (Data and code availability); not hashed here"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def claims_rows() -> list[dict]:
    rows = []
    for line in (MAN / "claims_map.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (\d+) \| ([^|]*) \| (.*) \| ([^|]*) \| (.*) \|\s*$", line)
        if not m:
            continue
        rows.append({"row": int(m.group(1)), "section": m.group(2).strip(), "phrase": m.group(3).strip(),
                     "source": m.group(4).strip(), "check": m.group(5).strip()})
    return rows


def package_paths(rows: list[dict]) -> tuple[list[str], list[str]]:
    local, v2 = set(), set()
    for p in sorted(MAN.rglob("*")):
        if p.is_file():
            local.add(p.relative_to(ROOT).as_posix())
    for r in rows:
        for src in re.split(r"[;,]\s*", r["source"]):
            src = src.strip().strip("`")
            if not src:
                continue
            if src.startswith("V2:"):
                v2.add(src[3:])
                continue
            src = src.removeprefix("main:")
            if any(ch in src for ch in "*?"):
                for q in sorted(ROOT.glob(src)):
                    if q.is_file():
                        local.add(q.relative_to(ROOT).as_posix())
                continue
            if (ROOT / src).is_file():
                local.add(src)
    return sorted(local), sorted(v2)


def verification_counts() -> dict:
    out = subprocess.run([sys.executable, str(ROOT / "tools/paper/verify_claims.py")], capture_output=True, text=True, cwd=ROOT)
    last = [l for l in out.stdout.splitlines() if l.startswith("rows:")]
    counts = {}
    if last:
        for tok in last[-1].split()[1:]:
            k, _, v = tok.partition("=")
            if v.isdigit():
                counts[k] = int(v)
            elif k.isdigit():
                counts["rows"] = int(k)
    counts["exit_code"] = out.returncode
    return counts


def build() -> dict:
    rows = claims_rows()
    local, v2 = package_paths(rows)
    local = [p for p in local if not p.startswith("docs/paper/release/")]
    sums = {p: sha(ROOT / p) for p in local}
    try:
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "UNKNOWN"
    manifest = {"schema": "ocm.paper-release-manifest.v1", "ocm_commit": head, "orion_v2": {"paths": v2, "note": V2_COMMIT_NOTE},
                "package": sums, "claims": rows, "claim_verification": verification_counts(),
                "identifier": {"status": "PENDING", "label": "HUMAN_GATE_BYPASSED__MODEL_PROXY", "note": "the operator's upload replaces this with the DOI"}}
    return manifest


def receipt_of(manifest: dict, manifest_bytes: bytes) -> dict:
    return {"receipt": "PAPER_RELEASE_RECEIPT_V1", "terminal": "PACKAGE_BOUND__IDENTIFIER_PENDING" if manifest["claim_verification"].get("exit_code") == 0 and manifest["claim_verification"].get("rows") == manifest["claim_verification"].get("OK") else "CANNOT_CHECK (claim verification not clean)",
            "git_head": manifest["ocm_commit"], "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "bound_files": dict(manifest["package"]), "deterministic_results": {"claim_verification": manifest["claim_verification"], "package_files": len(manifest["package"]), "claims_rows": len(manifest["claims"])},
            "authority": "byte identity of the manuscript package and the receipt-bound files it reads; no scientific claim; persistent identifier is a human action recorded under HUMAN_GATE_BYPASSED__MODEL_PROXY until minted"}


def main(argv: list[str]) -> int:
    manifest = build()
    mbytes = (json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    sums_text = "".join(f"{d}  {p}\n" for p, d in sorted(manifest["package"].items()))
    rec = receipt_of(manifest, mbytes)
    if "--verify" in argv:
        problems = []
        if not (OUT / "RELEASE_MANIFEST.json").exists() or not RECEIPT.exists():
            print("MISSING release manifest or receipt")
            return 1
        old_m = json.loads((OUT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        old_r = json.loads(RECEIPT.read_text(encoding="utf-8"))
        for p, d in manifest["package"].items():
            if old_m["package"].get(p) != d:
                problems.append(p)
        if set(old_m["package"]) - set(manifest["package"]):
            problems.append("package shrank: " + ",".join(sorted(set(old_m["package"]) - set(manifest["package"]))))
        if old_r["deterministic_results"] != rec["deterministic_results"]:
            problems.append("deterministic_results")
        if (OUT / "SHA256SUMS").read_text(encoding="utf-8") != sums_text:
            problems.append("SHA256SUMS")
        if problems:
            print("DRIFT:", problems)
            return 1
        print("paper release receipt verified; package files:", len(manifest["package"]), "; claims rows:", len(manifest["claims"]))
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "RELEASE_MANIFEST.json").write_bytes(mbytes)
    (OUT / "SHA256SUMS").write_text(sums_text, encoding="utf-8")
    RECEIPT.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("wrote", OUT / "RELEASE_MANIFEST.json", OUT / "SHA256SUMS", RECEIPT, "| files", len(manifest["package"]), "| terminal", rec["terminal"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
