"""Project SCREENED_NEGATIVE cuts to ordinary $p contracts from the frozen DAG."""
import sys

from load_inputs import CONSUMER

sys.path[:0] = [str(CONSUMER), str(CONSUMER / "donor")]

import typed_context as TC
import typed_emit as E

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


def compile_one(body, p1_contracts, work, index):
    catalogue = {row["label"]: row for row in p1_contracts}
    catalogue.update(float_contracts())
    hyps = [{"label": "cut-h" + str(i), "statement": p} for i, p in enumerate(body["premises"])]
    emitted = E.emit(body, catalogue, identity_context(), hyps, work)
    sem = semantic_labels(body)
    label = "ocm-cut-" + str(index).zfill(2)
    return {
        "label": label,
        "kind": "$p",
        "statement": list(body["query"]),
        "floating": [{"label": "cut-f" + str(i), "statement": ["class", TC.IDS[i]]} for i in range(3)],
        "essential": hyps,
        "dv": [],
        "proof": emitted["proof"],
        "semantic_labels": sem,
        "semantic_applications": emitted["semantic_applications_expanded"],
        "abstraction": classify(sem),
        "native_acceptance": "UNKNOWN",
    }


def compile_all(unique_rows, bodies, p1, work):
    lemmas = []
    for i, row in enumerate(unique_rows):
        payload = bodies[row["canonical_id"]]
        lemma = compile_one(payload["body"], p1, work, i)
        lemma.update({
            "canonical_id": row["canonical_id"],
            "source_label": payload["source_label"],
            "source_ordinal": payload["source_ordinal"],
            "source_index": row["index"],
        })
        lemmas.append(lemma)
    return lemmas


def ordinary_parent_rows(lemmas):
    keys = ("label", "kind", "statement", "floating", "essential", "dv")
    return [{k: row[k] for k in keys} for row in lemmas]
