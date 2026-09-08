"""P1-shaped lemma contracts, syntax-closure bank, Mooney-limited search arms."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE.parent / "native-method-serving-v1" / "vendor"
sys.path[:0] = [str(HERE), str(VENDOR)]
import finite_search as FS  # noqa: E402
import typed_terms as T  # noqa: E402

CLASS_ATOMS = tuple("ABCDEFGHKSTUVWXYZ") + tuple("V" + str(i) for i in range(10))
CLASS_OPS = {"i^i": "cin", "u.": "cun", "\\": "cdif", "/_\\": "csymdif"}


def extend_class_syntax():
    """One matcher repair: finite_search.match uses native_match's own typed_terms."""
    orig = T.syntax

    def syntax(kind, tokens):
        tokens = tuple(tokens)
        if kind != "class":
            return orig(kind, tokens)

        def cls(i):
            if i >= len(tokens):
                raise ValueError("class ended")
            if tokens[i] == "(/)":
                return i + 1, ["c0"]
            if tokens[i] in CLASS_ATOMS:
                return i + 1, ["c" + tokens[i]]
            if tokens[i] != "(":
                raise ValueError("class type")
            j, a = cls(i + 1)
            if j >= len(tokens) or tokens[j] not in CLASS_OPS:
                raise ValueError("class operator")
            op = tokens[j]
            j, b = cls(j + 1)
            if j >= len(tokens) or tokens[j] != ")":
                raise ValueError("class scope")
            return j + 1, a + b + [CLASS_OPS[op]]

        end, proof = cls(0)
        if end != len(tokens):
            raise ValueError("trailing syntax")
        return proof

    T.syntax = syntax
    T.ATOMS = CLASS_ATOMS
    FS.T.syntax = syntax
    FS.T.ATOMS = CLASS_ATOMS
    FS.M.T.syntax = syntax
    FS.M.T.ATOMS = CLASS_ATOMS
    return "native_match_class_difference_and_empty"


def class_vars(tokens):
    used = []
    for tok in tokens:
        if tok in CLASS_ATOMS or (tok.startswith("V") and tok[1:].isdigit()):
            if tok not in used:
                used.append(tok)
    return used


def lemma_contracts(lemmas):
    """P1-shaped: floating class hyps, essential from the compiled lemma (empty if zero-premise)."""
    rows = []
    for lemma in lemmas:
        stmt = list(lemma["statement"])
        floats = list(lemma.get("floating") or [])
        if not floats:
            floats = [{"label": "c" + v, "statement": ["class", v]} for v in class_vars(stmt)]
        rows.append({
            "label": lemma["label"].replace("ocm-cut-", "cut-lemma-"),
            "kind": "$p",
            "statement": stmt,
            "floating": floats,
            "essential": list(lemma.get("essential") or []),
            "dv": list(lemma.get("dv") or []),
            "source_label": lemma.get("source_label"),
            "semantic_labels": list(lemma.get("semantic_labels") or []),
            "zero_premise": not lemma.get("essential"),
        })
    return rows


def parenthesized_spans(tokens):
    spans = []
    for i, tok in enumerate(tokens):
        if tok != "(":
            continue
        depth = 0
        for j in range(i, len(tokens)):
            if tokens[j] == "(":
                depth += 1
            elif tokens[j] == ")":
                depth -= 1
                if depth == 0:
                    spans.append(tokens[i:j + 1])
                    break
    return spans


WFF_OPS = {"->", "<->", "/\\", "\\/", "-.", "=", "C_", "e.", "=/=", "C."}


def looks_wff(tokens):
    return any(t in WFF_OPS for t in tokens)


def syntax_closure(statement):
    toks = list(statement)
    body = toks[1:] if toks and toks[0] == "|-" else toks
    out = [body]
    for span in parenthesized_spans(body):
        if looks_wff(span):
            out.append(span)
    return out


def bank_from(goal, lemma_rows, extra_wffs=None):
    """Syntax closure of the goal plus lemma conclusions. Published search bank."""
    wff = []
    seen = set()
    for tokens in syntax_closure(goal) + [list(r["statement"][1:]) for r in lemma_rows] + list(extra_wffs or []):
        key = tuple(tokens)
        if key in seen:
            continue
        seen.add(key)
        wff.append({"tokens": list(tokens)})
    return {"wff": wff, "kind": "syntax_closure_plus_lemma_conclusions"}


def walk_labels(node, labels):
    if not isinstance(node, dict):
        return
    act = node.get("action") or {}
    if act.get("label"):
        labels.append(act["label"])
    for parent in node.get("parents") or []:
        walk_labels(parent, labels)
    walk_labels(node.get("derivation"), labels)


def mooney_once(labels, prefix="cut-lemma-"):
    used = [x for x in labels if str(x).startswith(prefix)]
    return {"used": used, "ok": len(used) <= 1, "n": len(used)}


def search_arm(parent, bank, task, max_decisions, compile_limit=50000):
    work = {}
    actions = FS.compile_parent(parent, bank, work, limit=compile_limit)
    found = FS.search(actions, bank, task, work, max_decisions=max_decisions)
    labels = []
    walk_labels(found, labels)
    mooney = mooney_once(labels)
    lemma_actions = [a for a in actions if str(a.get("label", "")).startswith("cut-lemma-")]
    return {
        "terminal": found.get("terminal"),
        "decision_count": found.get("decision_count"),
        "n_actions": len(actions),
        "lemma_actions": len(lemma_actions),
        "used_labels": labels,
        "used_cut_lemma": mooney["used"],
        "mooney_once": mooney["ok"],
        "work": dict(work),
        "compile_cost": work.get("primitive_instances", 0),
        "search_cost": work.get("action_attempts", 0),
    }


def ordinary_parent_rows(lemma_rows):
    keys = ("label", "kind", "statement", "floating", "essential", "dv")
    return [{k: row[k] for k in keys} for row in lemma_rows]
