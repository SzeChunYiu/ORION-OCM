"""Bounded finite-bank search: P1 vs P1+zero-premise lemmas on a P1-closed held-out."""
import json
import sys
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE.parent / "native-method-serving-v1" / "vendor"
sys.path[:0] = [str(HERE), str(VENDOR)]
import extract as E  # noqa: E402
import finite_search as FS  # noqa: E402

RAW = HERE.parent / "ordinary-cut-opportunity-result-v1" / "RAW.zip"
GOAL = ["|-", "(", "(", "A", "i^i", "B", ")", "C_", "C", "<->", "(", "A", "i^i", "(", "B", "\\", "C", ")", ")", "=", "(/)", ")"]


def load_p1():
    with zipfile.ZipFile(RAW) as archive:
        return json.loads(archive.read("prospective-run-01/opportunity-01/P1-CONTRACTS.json"))


def lemma_contracts():
    rows = []
    for i, lemma in enumerate(E.unique_negatives()):
        if lemma["hypotheses"]:
            continue
        used = []
        for tok in lemma["target"]:
            if tok in ("A", "B", "C", "V") or (tok.startswith("V") and tok[1:].isdigit()):
                if tok not in used:
                    used.append(tok)
        # V in ssdifim target
        floats = [{"label": "c" + v, "statement": ["class", v]} for v in used]
        rows.append({
            "label": "cut-lemma-" + str(i).zfill(2),
            "kind": "$p",
            "statement": lemma["target"],
            "floating": floats,
            "essential": [],
            "dv": [],
        })
    return rows


def subformulas(stmt):
    """Every parenthesized |- wff plus the whole statement."""
    toks = list(stmt)
    out = {tuple(toks)}
    i = 0
    while i < len(toks):
        if toks[i] == "(":
            depth = 0
            for j in range(i, len(toks)):
                if toks[j] == "(":
                    depth += 1
                elif toks[j] == ")":
                    depth -= 1
                    if depth == 0:
                        piece = toks[i:j + 1]
                        out.add(tuple(["|-"] + piece if piece[0] != "|-" else piece))
                        break
        i += 1
    extra = [
        ["|-", "A", "C_", "B"],
        ["|-", "A", "C_", "C"],
        ["|-", "B", "C_", "C"],
        ["|-", "(", "A", "i^i", "B", ")", "C_", "C"],
        ["|-", "(", "A", "i^i", "(", "B", "\\", "C", ")", ")", "=", "(/)"],
        ["|-", "(", "B", "\\", "C", ")"],
    ]
    for row in extra:
        out.add(tuple(row if row[0] == "|-" else ["|-"] + row))
    bank = {"wff": [{"tokens": list(t[1:])} for t in sorted(out, key=lambda x: (len(x), x)) if t[0] == "|" and False]}
    # tokens are wff without |-
    wff = []
    seen = set()
    for t in sorted(out, key=lambda x: (len(x), x)):
        if not t or t[0] != "|-":
            continue
        key = tuple(t[1:])
        if key in seen:
            continue
        seen.add(key)
        wff.append({"tokens": list(key)})
    return {"wff": wff}


def actions_contain(actions, prefix):
    return [a for a in actions if str(a.get("label", "")).startswith(prefix)]


def search_arm(parent, bank, task, max_decisions=4):
    work = {}
    start = time.monotonic()
    actions = FS.compile_parent(parent, bank, work, limit=50000)
    found = FS.search(actions, bank, task, work, max_decisions=max_decisions)
    elapsed = time.monotonic() - start
    labels = []

    def walk(node):
        if not isinstance(node, dict):
            return
        act = node.get("action") or {}
        if act.get("label"):
            labels.append(act["label"])
        for p in node.get("parents") or []:
            walk(p)
        walk(node.get("derivation"))

    walk(found)
    return {
        "terminal": found.get("terminal"),
        "decision_count": found.get("decision_count"),
        "n_actions": len(actions),
        "lemma_actions": len(actions_contain(actions, "cut-lemma-")),
        "used_labels": labels,
        "used_cut_lemma": [x for x in labels if str(x).startswith("cut-lemma-")],
        "work": work,
        "wall_s": elapsed,
    }


def main():
    p1 = load_p1()
    lemmas = lemma_contracts()
    bank = subformulas(GOAL)
    task = {"query": GOAL, "premises": []}
    print("bank", len(bank["wff"]), "lemmas", len(lemmas), flush=True)
    p1_result = search_arm(p1, bank, task)
    print("P1", p1_result["terminal"], "dec", p1_result["decision_count"], "actions", p1_result["n_actions"], "wall", round(p1_result["wall_s"], 2), flush=True)
    p2_result = search_arm(p1 + lemmas, bank, task)
    print("P2", p2_result["terminal"], "dec", p2_result["decision_count"], "actions", p2_result["n_actions"], "used", p2_result["used_cut_lemma"], "wall", round(p2_result["wall_s"], 2), flush=True)
    out = {
        "schema": "g2.causal-lemma-reuse.search.v1",
        "goal": GOAL,
        "held_out_label": "inssdif0",
        "n_p1": len(p1),
        "n_lemmas": len(lemmas),
        "n_bank": len(bank["wff"]),
        "P1": {k: v for k, v in p1_result.items() if k != "work"} | {"work": p1_result["work"]},
        "P2": {k: v for k, v in p2_result.items() if k != "work"} | {"work": p2_result["work"]},
        "causal_invocation": bool(p2_result["used_cut_lemma"]) and p2_result["terminal"] == "PROVED",
        "removal_changes_outcome": p1_result["terminal"] != p2_result["terminal"],
    }
    dest = HERE / "records" / "admit-01" / "SEARCH.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("held_out_label", "n_bank", "n_lemmas", "causal_invocation", "removal_changes_outcome")}, indent=2))


if __name__ == "__main__":
    main()
