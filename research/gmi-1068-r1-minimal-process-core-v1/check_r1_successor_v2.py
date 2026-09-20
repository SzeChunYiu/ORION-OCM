#!/usr/bin/env python3
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parent

TYPES=("A","B","C","D")
PRIM={
    "f":("A","B"),
    "g":("B","C"),
    "h":("C","D"),
}

def need(cond,msg):
    if not cond:
        raise RuntimeError(msg)

def path_end(start,path,prim=PRIM):
    cur=start
    for name in path:
        if name not in prim:
            return None
        src,dst=prim[name]
        if src!=cur:
            return None
        cur=dst
    return cur

def valid(start,path,prim=PRIM):
    return path_end(start,path,prim) is not None

def compose(start,p,q,prim=PRIM):
    mid=path_end(start,p,prim)
    if mid is None or path_end(mid,q,prim) is None:
        return None
    return tuple(p)+tuple(q)

def enumerate_paths(max_len=3,prim=PRIM):
    out=[]
    names=tuple(prim)
    def rec(start,path):
        out.append((start,tuple(path),path_end(start,path,prim)))
        if len(path)==max_len:
            return
        cur=path_end(start,path,prim)
        if cur is None:
            return
        for n in names:
            if prim[n][0]==cur:
                rec(start,path+(n,))
    for start in TYPES:
        rec(start,())
    return out

def reachable(paths):
    return sorted({(s,e) for s,p,e in paths if e is not None})

def direct_category_reachability():
    # An extensional category-style presentation of the same registered
    # reachability semantics. Identities/composites are already named.
    morphisms={
        "idA":("A","A"),"idB":("B","B"),"idC":("C","C"),"idD":("D","D"),
        "f":("A","B"),"g":("B","C"),"h":("C","D"),
        "gf":("A","C"),"hg":("B","D"),"hgf":("A","D"),
    }
    return sorted(set(morphisms.values()))

def main():
    paths=enumerate_paths()
    reach=reachable(paths)
    direct=direct_category_reachability()
    need(reach==direct,f"PRESENTATION_MISMATCH:{reach}!={direct}")

    # Empty paths derive identities without requiring primitive self-loops.
    empties=[(s,path_end(s,())) for s in TYPES]
    need(empties==[(x,x) for x in TYPES],"EMPTY_IDENTITIES")

    # Associativity is inherited from sequence concatenation.
    left=compose("A",compose("A",("f",),("g",)),("h",))
    right=compose("A",("f",),compose("B",("g",),("h",)))
    need(left==right==("f","g","h"),"PATH_ASSOCIATIVITY")

    # Requirement-bearing removal/hostile witnesses.
    untyped=("f","f")
    typed_reject=not valid("A",untyped)

    no_f={k:v for k,v in PRIM.items() if k!="f"}
    no_process_ab=("A","B") not in reachable(enumerate_paths(3,no_f))

    one_step=reachable(enumerate_paths(1))
    no_sequence_ad=("A","D") not in one_step and ("A","D") in reach

    no_positive_stasis_primitives=all(src!=dst for src,dst in PRIM.values())
    empty_still_identity=all(path_end(t,())==t for t in TYPES)

    category_not_unique_encoding=(reach==direct and len(paths)!=len(direct))

    hostiles=[
        typed_reject,
        no_process_ab,
        no_sequence_ad,
        no_positive_stasis_primitives and empty_still_identity,
        left==right,
        category_not_unique_encoding,
    ]
    need(all(hostiles),f"HOSTILES:{hostiles}")

    result=json.loads((ROOT/"RESULT_V2.json").read_text())
    expected={
        "types":4,
        "primitive_processes":3,
        "derived_reachable_pairs":10,
        "independent_requirement_bearing_components":3,
        "derived_category_laws":3,
        "hostiles_caught":6,
    }
    for k,v in expected.items():
        need(result.get(k)==v,f"RESULT_DRIFT:{k}:{result.get(k)}!={v}")

    print(json.dumps({
        "status":"GREEN",
        "reachable_pairs":[list(x) for x in reach],
        "path_records":len(paths),
        "direct_category_morphisms":len(direct),
        "empty_identities":empties,
        "assoc_path":list(left),
        "hostiles_caught":6,
    },sort_keys=True))

if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print("R1_S1_RED:"+repr(exc),file=sys.stderr)
        sys.exit(1)
