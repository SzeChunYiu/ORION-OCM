"""Separate authored class/inclusion/conjunction syntax and joint semantics."""
import hashlib
import itertools
import json

ATOMS = ("A","B","C")
def syntax(kind, tokens):
    tokens = tuple(tokens)
    def cls(i):
        if i >= len(tokens): raise ValueError("class ended")
        if tokens[i] in ATOMS: return i+1, ["c"+tokens[i]]
        if tokens[i] != "(": raise ValueError("class type")
        j, a = cls(i+1)
        if j >= len(tokens) or tokens[j] not in ("i^i","u."): raise ValueError("class operator")
        op=tokens[j]; j,b=cls(j+1)
        if j>=len(tokens) or tokens[j]!=")": raise ValueError("class scope")
        return j+1,a+b+[{"i^i":"cin","u.":"cun"}[op]]
    def wff(i):
        try:
            j,a=cls(i)
            if j<len(tokens) and tokens[j]=="C_":
                j,b=cls(j+1); return j,a+b+["wss"]
        except ValueError:
            pass
        if i>=len(tokens) or tokens[i]!="(": raise ValueError("wff type")
        j,a=wff(i+1)
        if j>=len(tokens) or tokens[j]!="/\\": raise ValueError("wff operator")
        j,b=wff(j+1)
        if j>=len(tokens) or tokens[j]!=")": raise ValueError("wff scope")
        return j+1,a+b+["wa"]
    if kind not in ("class","wff"): raise ValueError("ground type has no syntax proof")
    end,proof=(cls if kind=="class" else wff)(0)
    if end!=len(tokens): raise ValueError("trailing syntax")
    return proof

def rename(tokens, mapping):
    return [mapping.get(t,t) for t in tokens]

# Independent token decomposition, not the syntax parser or unary solver.
def split(tokens, operators):
    depth=0
    for i,t in enumerate(tokens):
        if t=="(": depth+=1
        elif t==")": depth-=1
        elif depth==0 and t in operators: return i,t
    return None
def membership(tokens, valuation):
    if len(tokens)==1 and tokens[0] in ATOMS: return bool(valuation[ATOMS.index(tokens[0])])
    if len(tokens)<5 or tokens[0]!="(" or tokens[-1]!=")": raise ValueError("oracle class")
    inside=tokens[1:-1]; pair=split(inside,("i^i","u."))
    if pair is None: raise ValueError("oracle class operator")
    i,op=pair; a=membership(inside[:i],valuation); b=membership(inside[i+1:],valuation)
    return a and b if op=="i^i" else a or b
def point_formula(tokens, valuation):
    pair=split(tokens,("C_",))
    if pair:
        i,_=pair
        return not membership(tokens[:i],valuation) or membership(tokens[i+1:],valuation)
    if tokens[0]!="(" or tokens[-1]!=")": raise ValueError("oracle formula")
    inside=tokens[1:-1]; pair=split(inside,("/\\",))
    if pair is None: raise ValueError("oracle formula operator")
    i,_=pair
    return point_formula(inside[:i],valuation) and point_formula(inside[i+1:],valuation)
def truth_rows(premises, query):
    statements=premises+[query]
    if any(s[0]!="|-" for s in statements): raise ValueError("oracle assertion type")
    truth=[[point_formula(s[1:], v) for s in statements] for v in itertools.product((0,1),repeat=3)]
    return [[all(truth[v][j] for v in range(8) if world>>v&1) for j in range(len(statements))]
            for world in range(1,256)]
def meaning(premises, query, roles=False):
    values=[]
    for perm in itertools.permutations(ATOMS):
        mapping=dict(zip(ATOMS,perm))
        rows=truth_rows([rename(p,mapping) for p in premises],rename(query,mapping))
        values.append(json.dumps(rows if roles else [[all(row[:-1]),row[-1]] for row in rows],separators=(",",":")))
    return hashlib.sha256(min(values).encode()).hexdigest()
def semantic_checks(premises, query):
    rows=truth_rows(premises,query)
    return {"valid":all(not all(r[:-1]) or r[-1] for r in rows),
            "essential":[any(all(v for j,v in enumerate(r[:-1]) if j!=i) and not r[-1]
                             for r in rows) for i in range(len(premises))],
            "satisfiable_premises":any(all(r[:-1]) for r in rows),
            "non_tautological_query":any(not r[-1] for r in rows),
            "joint_sha256":meaning(premises,query),"role_sha256":meaning(premises,query,roles=True),"world_rows":rows}
