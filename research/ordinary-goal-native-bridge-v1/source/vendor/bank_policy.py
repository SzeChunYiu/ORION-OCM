"""Unchanged published finite syntax-bank policy; no outcome-derived hints."""
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
