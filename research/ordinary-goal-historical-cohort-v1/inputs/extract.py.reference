"""Load unique SCREENED_NEGATIVE cuts and their reconstructed proofs."""
import json
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REVIVAL = REPO / "research" / "ordinary-cut-syntax-revival-v1" / "records" / "replay-01" / "RESULT.json"
RAW = REPO / "research" / "ordinary-cut-opportunity-result-v1" / "RAW.zip"


def unique_negatives():
    revival = json.loads(REVIVAL.read_text())
    wanted = []
    seen = set()
    for row in revival["screens"]:
        if row["status"] != "SCREENED_NEGATIVE_IN_DOMAIN":
            continue
        cid = row["canonical_id"]
        if cid in seen:
            continue
        seen.add(cid)
        wanted.append(cid)
    with zipfile.ZipFile(RAW) as archive:
        data = json.loads(archive.read("prospective-run-01/opportunity-01/RESULT.json"))
    out = []
    for root in data["roots"]:
        for cut in root.get("cuts") or []:
            cid = cut.get("canonical_id")
            if cid not in wanted:
                continue
            proposal = cut.get("proposal") or {}
            out.append({
                "canonical_id": cid,
                "source_label": root.get("label"),
                "ordinal": root.get("ordinal"),
                "query": cut["body"]["query"],
                "premises": cut["body"]["premises"],
                "target": proposal.get("target"),
                "hypotheses": proposal.get("hypotheses") or [],
                "proof": proposal.get("proof") or [],
            })
            wanted.remove(cid)
    if wanted:
        raise ValueError("missing negatives: " + ",".join(wanted[:3]))
    return out


def emit_suffix(lemma, label):
    lines = ["${"]
    for hyp in lemma["hypotheses"]:
        lines.append(hyp["label"] + " $e " + " ".join(hyp["statement"]) + " $.")
    lines.append(label + " $p " + " ".join(lemma["target"]) + " $= " + " ".join(lemma["proof"]) + " $.")
    lines.append("$}")
    return "\n".join(lines) + "\n"
