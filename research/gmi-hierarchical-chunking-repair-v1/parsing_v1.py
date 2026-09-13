"""Exact supplied-dictionary parsing and independent full tokenization oracle."""
from hierarchy_v1 import price


def contract(text, primitives, chunks):
    if type(text) is not str or any(type(a) is not str or len(a)!=1 for a in primitives):
        raise ValueError("string/primitive contract")
    if any(a not in primitives for a in text):
        raise ValueError("missing primitive")
    if any(type(p) is not str or not p for p in chunks):
        raise ValueError("empty or malformed chunk")
    for c in tuple(primitives.values())+tuple(chunks.values()): price(c)


def parse(text, primitives, chunks):
    contract(text, primitives, chunks)
    values=[None]*(len(text)+1);values[-1]=(0,())
    edges=0
    for i in range(len(text)-1,-1,-1):
        options=[(text[i],primitives[text[i]])]
        options.extend((p,c) for p,c in chunks.items() if text.startswith(p,i))
        best=None
        for p,c in options:
            edges+=1
            tail,path=values[i+len(p)]
            candidate=(price(c)+tail,(p,)+path)
            if best is None or candidate<best:best=candidate
        values[i]=best
    cost,tokens=values[0]
    return dict(cost=cost,tokens=tokens,states=len(values),edges=edges)


def all_parses(text, primitives, chunks):
    contract(text,primitives,chunks)
    found=[]
    def walk(rest, tokens, cost):
        if not rest:
            found.append((cost,tokens));return
        for p,c in list(primitives.items())+list(chunks.items()):
            if rest.startswith(p):walk(rest[len(p):],tokens+(p,),cost+price(c))
    walk(text,(),0)
    return found
