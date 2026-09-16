from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
import importlib.util
import json
import sys


def load_parent():
    p = Path(__file__).resolve().parents[1] / 'gmi-833-g0-register-core-v1' / 'g0_register_core_v1.py'
    spec = importlib.util.spec_from_file_location('g0_oracle_parent', p)
    if spec is None or spec.loader is None:
        raise RuntimeError('parent unavailable')
    m = importlib.util.module_from_spec(spec); sys.modules[spec.name] = m; spec.loader.exec_module(m); return m

P = load_parent()
INPUTS=((),(0,),(1,)); BUDGET=6


def ik(i):
    if isinstance(i,P.Halt): return ('H',)
    if isinstance(i,P.Read): return ('R',i.next_label)
    if isinstance(i,P.Inc): return ('I',i.next_label)
    if isinstance(i,P.Emit): return ('E',i.next_label)
    if isinstance(i,P.DecJz): return ('D',i.nonzero_label,i.zero_label)
    raise TypeError


def opts(labels):
    out=[P.Halt()]
    out += [P.Read('r',x) for x in labels]
    out += [P.Inc('r',x) for x in labels]
    out += [P.Emit('r',x) for x in labels]
    out += [P.DecJz('r',x,y) for x in labels for y in labels]
    return tuple(out)


def build():
    rows=[]
    for a in opts(('L0',)):
        rows.append((1,(ik(a),),P.Program(('r',),'L0',{'L0':a})))
    o2=opts(('L0','L1'))
    for a,b in product(o2,repeat=2):
        rows.append((2,(ik(a),ik(b)),P.Program(('r',),'L0',{'L0':a,'L1':b})))
    return rows


def sem(program):
    return tuple((x.terminal,tuple(x.output)) for x in (P.execute(program,i,BUDGET) for i in INPUTS))


def adjacent(a,b):
    la,ka,_=a; lb,kb,_=b
    if la==lb:
        return sum(x!=y for x,y in zip(ka,kb))==1
    one,two=(a,b) if la==1 else (b,a)
    if one[0]!=1 or two[0]!=2: return False
    # deletion is legal iff L0 of the two-label program is exactly a one-label legal instruction.
    return one[1][0] == two[1][0]


def main():
    rows=build(); n=len(rows)
    if n!=126: raise SystemExit('presentation census drift')
    # Floyd-Warshall from direct independently derived adjacency.
    INF=10**9
    d=[[INF]*n for _ in range(n)]
    edge_count=0
    for i in range(n):
        d[i][i]=0
        for j in range(i+1,n):
            if adjacent(rows[i],rows[j]):
                d[i][j]=d[j][i]=1; edge_count+=1
    for k in range(n):
        dk=d[k]
        for i in range(n):
            via=d[i][k]
            if via>=INF: continue
            di=d[i]
            for j in range(n):
                nv=via+dk[j]
                if nv<di[j]: di[j]=nv
    start=next(i for i,r in enumerate(rows) if r[0]==1 and r[1]==(('H',),))
    from_start=[d[start][i] for i in range(n)]
    if any(x>=INF for x in from_start): raise SystemExit('unexpected unreachable presentation')
    by=defaultdict(list)
    for idx,r in enumerate(rows): by[sem(r[2])].append(idx)
    mult=Counter(len(v) for v in by.values())
    L=Counter(min(rows[i][0] for i in ids) for ids in by.values())
    cd=Counter(min(from_start[i] for i in ids) for ids in by.values())
    out={
      'schema':'GMI833G0GrammarBiasIndependentOracleV1',
      'presentation_count':n,
      'semantic_class_count':len(by),
      'undirected_edge_count':edge_count,
      'presentation_distance_histogram':{str(k):v for k,v in sorted(Counter(from_start).items())},
      'class_multiplicity_histogram':{str(k):v for k,v in sorted(mult.items())},
      'class_shortest_length_histogram':{str(k):v for k,v in sorted(L.items())},
      'class_distance_histogram':{str(k):v for k,v in sorted(cd.items())},
      'terminal':'GREEN'
    }
    print(json.dumps(out,indent=2,sort_keys=True,separators=(',', ': ')))

if __name__=='__main__': main()
