"""Diff replay-02 vs replay-01 negatives and compile extra cuts as ordinary $p."""
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
REVIVAL = REPO / "research" / "ordinary-cut-syntax-revival-v1" / "records"
RAW = REPO / "research" / "ordinary-cut-opportunity-result-v1" / "RAW.zip"
CONSUMER = REPO / "research" / "ordinary-cut-source-evidence-v1" / "consumer-v3"

import sys
sys.path[:0] = [str(CONSUMER), str(CONSUMER / "donor")]
import typed_context as TC  # noqa: E402
import typed_emit as E  # noqa: E402

COMMUTE = {"incom", "uncom"}
CONG = {
    "difeq1", "difeq2", "difeq1i", "difeq2i", "difeq12i",
    "uneq12d", "uneq12i", "ineq12i", "eqsstrid", "ssinss1",
}
DEFN = {"df-symdif", "dfss4", "eleq2i"}
CHAIN = {
    "eldif", "orbi12i", "elun", "bitri", "ex", "ssdifim",
    "birani", "bilani", "sseq12d", "eqcomd",
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_screens(name):
    return json.loads((REVIVAL / name / "RESULT.json").read_text())["screens"]


def negatives(screens):
    rows = []
    seen = []
    unique = []
    for row in screens:
        if row["status"] != "SCREENED_NEGATIVE_IN_DOMAIN":
            continue
        rows.append(row)
        cid = row["canonical_id"]
        if cid not in seen:
            seen.append(cid)
            unique.append(row)
    return rows, unique


def extra_unique():
    r1, u1 = negatives(load_screens("replay-01"))
    r2, u2 = negatives(load_screens("replay-02"))
    admitted = {row["canonical_id"] for row in u1}
    extra = [row for row in u2 if row["canonical_id"] not in admitted]
    return {
        "replay01_occurrences": len(r1),
        "replay01_unique": len(u1),
        "replay02_occurrences": len(r2),
        "replay02_unique": len(u2),
        "admitted_ids": [row["canonical_id"] for row in u1],
        "extra": extra,
        "replay01_ids": [row["canonical_id"] for row in r1],
        "replay02_ids": [row["canonical_id"] for row in r2],
    }


def semantic_labels(body):
    return [n["label"] for n in body["nodes"]
            if n["kind"] == "apply" and n["output"][0] == "|-"]


def classify(sem):
    if any(x in COMMUTE for x in sem) and any(x in CONG for x in sem):
        return "COMMUTE_TRANSPORT"
    if any(x in DEFN for x in sem):
        return "DEFINITION_UNFOLDING"
    if sem and all(x in CHAIN or x in CONG for x in sem):
        return "P1_CHAIN"
    return "P1_COMPOSITION"


def float_contracts():
    rows = {}
    for i, pid in enumerate(TC.IDS):
        lab = "cut-f" + str(i)
        rows[lab] = {"label": lab, "kind": "$f", "statement": ["class", pid]}
    return rows


def identity_context():
    return {
        "schema": "native.typed-context.v1",
        "dv": [],
        "parameters": [
            {"id": key, "type": "class", "variable": key, "floating_label": "cut-f" + str(i)}
            for i, key in enumerate(TC.IDS)
        ],
    }


def load_opportunity():
    with zipfile.ZipFile(RAW) as archive:
        return json.loads(archive.read("prospective-run-01/opportunity-01/RESULT.json"))


def load_p1():
    with zipfile.ZipFile(RAW) as archive:
        return json.loads(archive.read("prospective-run-01/opportunity-01/P1-CONTRACTS.json"))


def extra_lemmas():
    """#179 path: unique extra negatives from RAW CUT_PROPOSAL bodies + proposal.proof."""
    inventory = extra_unique()
    wanted = [row["canonical_id"] for row in inventory["extra"]]
    remaining = list(wanted)
    data = load_opportunity()
    out = []
    for root in data["roots"]:
        for cut in root.get("cuts") or []:
            cid = cut.get("canonical_id")
            if cid not in remaining:
                continue
            proposal = cut.get("proposal") or {}
            body = cut["body"]
            sem = semantic_labels(body)
            out.append({
                "canonical_id": cid,
                "source_label": root.get("label"),
                "ordinal": root.get("ordinal"),
                "query": body["query"],
                "premises": body["premises"],
                "target": proposal.get("target"),
                "hypotheses": proposal.get("hypotheses") or [],
                "proof": proposal.get("proof") or [],
                "semantic_labels": sem,
                "semantic_applications": sum(
                    1 for n in body["nodes"]
                    if n["kind"] == "apply" and n["output"][0] == "|-"
                ),
                "abstraction": classify(sem),
                "nodes": len(body["nodes"]),
            })
            remaining.remove(cid)
    if remaining:
        raise ValueError("missing extra negatives: " + ",".join(remaining[:3]))
    return inventory, out


def emit_suffix(lemma, label):
    lines = ["${"]
    for hyp in lemma["hypotheses"]:
        lines.append(hyp["label"] + " $e " + " ".join(hyp["statement"]) + " $.")
    lines.append(label + " $p " + " ".join(lemma["target"]) + " $= " + " ".join(lemma["proof"]) + " $.")
    lines.append("$}")
    return "\n".join(lines) + "\n"


def named_p1_match(lemma, p1):
    """Exact statement match of compiled target against P1 $p rows (deeper named alias)."""
    target = tuple(lemma["target"])
    hits = []
    for row in p1:
        if row.get("kind") != "$p":
            continue
        if tuple(row.get("statement") or []) == target:
            hits.append(row["label"])
    return hits


def reemit_check(lemma, body_by_id, p1):
    """Confirm proposal.proof equals typed_emit of the frozen DAG (same #179 source)."""
    body = body_by_id[lemma["canonical_id"]]
    catalogue = {row["label"]: row for row in p1}
    catalogue.update(float_contracts())
    hyps = lemma["hypotheses"]
    work = {}
    emitted = E.emit(body, catalogue, identity_context(), hyps, work)
    return {
        "proof_equals_typed_emit": emitted["proof"] == lemma["proof"],
        "target_equals_typed_emit": emitted["target"] == lemma["target"],
        "semantic_applications_expanded": emitted["semantic_applications_expanded"],
    }


def bodies_by_id():
    data = load_opportunity()
    found = {}
    for root in data["roots"]:
        for cut in root.get("cuts") or []:
            cid = cut.get("canonical_id")
            if cid and cid not in found:
                found[cid] = cut["body"]
    return found
