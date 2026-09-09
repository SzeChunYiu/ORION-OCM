"""Data-only source index; no proof checking or include expansion."""
import hashlib
import itertools
import re

def identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}

def lex(raw):
    comment = False
    for match in re.finditer(rb"\S+", raw):
        word = match[0].decode("ascii")
        if comment:
            if word == "$)": comment = False
            continue
        if word == "$(":
            comment = True
            continue
        yield word, match.start(), match.end()
    if comment: raise ValueError("unclosed comment")

def index(raw, stop=None):
    tokens = iter(lex(raw))
    frames = [{"v": set(), "d": set(), "f": [], "e": []}]
    records = {}
    for word, start, end in tokens:
        if word == stop:
            return records, start
        if word == "${":
            frames.append({"v": set(), "d": set(), "f": [], "e": []})
            continue
        if word == "$}":
            if len(frames) == 1: raise ValueError("unbalanced scope")
            frames.pop()
            continue
        label = None
        if not word.startswith("$"):
            label, label_start = word, start
            word, start, end = next(tokens)
        if word not in {"$c", "$v", "$d", "$f", "$e", "$a", "$p"}:
            raise ValueError("unsupported source directive: " + word)
        body, proof, split = [], None, None
        body_start = end
        for tok, a, b in tokens:
            if tok == "$=":
                split = (a, b)
                proof = []
            elif tok == "$.":
                finish = b
                break
            elif proof is None: body.append(tok)
            else: proof.append(tok)
        else: raise ValueError("unterminated statement")
        if word == "$v": frames[-1]["v"].update(body)
        if word == "$d":
            frames[-1]["d"].update(tuple(sorted(p)) for p in itertools.combinations(body, 2))
        if label is None: continue
        if label in records: raise ValueError("duplicate label")
        row = {"label": label, "kind": word, "statement": body,
               "span": [label_start, finish], "raw": identity(raw[label_start:finish]),
               "statement_raw": identity(raw[body_start:split[0] if split else a])}
        if word in {"$f", "$e"}:
            frames[-1][word[1:]].append({"label": label, "statement": body})
        if word in {"$a", "$p"}:
            vs = set().union(*(fr["v"] for fr in frames))
            es = [h for fr in frames for h in fr["e"]]
            mandatory = vs.intersection(body + [t for h in es for t in h["statement"]])
            row["floating"] = [h for fr in frames for h in fr["f"] if h["statement"][1] in mandatory]
            row["essential"] = es
            row["dv"] = sorted([list(p) for p in set().union(*(fr["d"] for fr in frames))
                                if set(p) <= mandatory])
        if word == "$p":
            if proof is None: raise ValueError("missing proof")
            row.update(proof=proof, proof_raw=identity(raw[split[1]:a]),
                       active_variables=sorted(set().union(*(fr["v"] for fr in frames))),
                       active_dv=sorted([list(p) for p in set().union(*(fr["d"] for fr in frames))]))
        records[label] = row
    if stop is not None: raise ValueError("stop label absent")
    if len(frames) != 1: raise ValueError("unclosed scope")
    return records, len(raw)

def contract(row):
    result = {k: row[k] for k in ("label", "kind", "statement")}
    if row["kind"] in {"$a", "$p"}:
        result.update({k: row[k] for k in ("floating", "essential", "dv")})
    return result

def native_contract(label, step, fs):
    kind, value = step
    if kind in {"$f", "$e"}:
        return {"label": label, "kind": kind, "statement": value}
    ds, fs0, es, stmt = value
    return {"label": label, "kind": kind, "statement": stmt,
            "floating": [{"label": fs.lookup_f(v), "statement": [t, v]} for t, v in fs0],
            "essential": [{"label": fs.lookup_e(h), "statement": h} for h in es],
            "dv": sorted([list(p) for p in ds])}
