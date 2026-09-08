"""Inventory-derived completeness certificate for this frozen ground surface."""
import collections
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location("_scope_match",Path(__file__).with_name("native_match.py"))
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
EXPECTED={
    "wa":(["wff","(","ph","/\\","ps",")"],[["wff","ph"],["wff","ps"]]),
    "cin":(["class","(","A","i^i","B",")"],[["class","A"],["class","B"]]),
    "cun":(["class","(","A","u.","B",")"],[["class","A"],["class","B"]]),
    "wss":(["wff","A","C_","B"],[["class","A"],["class","B"]])}
def certify(parent,statements):
    if not statements:raise ValueError("UNSUPPORTED_NATIVE_SYNTAX: empty surface")
    for s in statements:M.ground_guard(s,[])
    syntax=[r for r in parent if r["statement"][0]!="|-"]
    if len(syntax)!=44 or any(r["essential"] or r["dv"] for r in syntax):
        raise ValueError("UNSUPPORTED_NATIVE_SYNTAX: syntax population/obligations")
    if any(r["statement"][0] not in ("class","wff") for r in syntax):
        raise ValueError("UNSUPPORTED_NATIVE_SYNTAX: potential setvar producer")
    if any(h["statement"][0] not in ("class","wff","setvar") for r in parent for h in r["floating"]):
        raise ValueError("UNSUPPORTED_NATIVE_SYNTAX: floating type")
    counts=[collections.Counter(s[1:]) for s in statements]
    maxima={t:max(c[t] for c in counts) for t in set().union(*(set(c) for c in counts))}
    disposition={}
    for row in syntax:
        label=row["label"];variables={h["statement"][1] for h in row["floating"]}
        fixed=collections.Counter(t for t in row["statement"][1:] if t not in variables)
        if label in EXPECTED:
            stmt,fs=EXPECTED[label]
            if row["statement"]!=stmt or [h["statement"] for h in row["floating"]]!=fs:
                raise ValueError("UNSUPPORTED_NATIVE_SYNTAX: implemented constructor changed")
            disposition[label]="implemented"
        elif any(n>maxima.get(t,0) for t,n in fixed.items()):
            disposition[label]="required literal multiplicity absent from every whole string and substring"
        elif any(h["statement"][0]=="setvar" for h in row["floating"]):
            disposition[label]="no setvar leaf in fixed A/B/C class context and no setvar constructor"
        else:
            raise ValueError("UNSUPPORTED_NATIVE_SYNTAX: unresolved native constructor "+label)
    if {n for n,d in disposition.items() if d=="implemented"}!=set(EXPECTED):
        raise ValueError("UNSUPPORTED_NATIVE_SYNTAX: missing implementation rule")
    return {"syntax_assertions":len(syntax),"implemented":sorted(EXPECTED),
            "native_syntax_contracts":syntax,"disposition":disposition,"ground_token_maxima":maxima,
            "ground_statements":len(statements),
            "ambient_floating":[["class","A"],["class","B"],["class","C"]],"ambient_dv":[],
            "argument":"All typed substrings use only cA/cB/cC leaves and these four implemented constructors. Other native constructors require an absent literal count or an unavailable setvar. All slices are therefore exhaustively typed, or invalid, under this exact pinned grammar and context."}
