from __future__ import annotations
import hashlib, itertools, json
from collections import Counter, deque
from pathlib import Path

HERE=Path(__file__).resolve().parent
BITS=(0,1)


def candidates():
    out=[('S',x) for x in itertools.product(BITS,repeat=2)]
    for bits in itertools.product(BITS,repeat=8):
        out.append(('M',tuple((bits[2*i],bits[2*i+1]) for i in range(4))))
    return out


def as_transducer(c):
    typ,data=c
    if typ=='S': return {(0,0):(0,data[0]),(0,1):(0,data[1])}
    return {(0,0):data[0],(0,1):data[1],(1,0):data[2],(1,1):data[3]}


def run(c,word):
    t=as_transducer(c); s=0; out=[]
    for x in word:
        s,y=t[(s,x)]; out.append(y)
    return tuple(out)


def equivalent(a,b):
    ta,tb=as_transducer(a),as_transducer(b); q=[(0,0)]; seen=set()
    while q:
        sa,sb=q.pop()
        if (sa,sb) in seen: continue
        seen.add((sa,sb))
        for x in BITS:
            na,ya=ta[(sa,x)]; nb,yb=tb[(sb,x)]
            if ya!=yb: return False
            q.append((na,nb))
    return True


def words_upto(h):
    out=[()]
    for n in range(1,h+1): out.extend(itertools.product(BITS,repeat=n))
    return out


def targets():
    def identity(w): return tuple(w)
    def neg(w): return tuple(1-x for x in w)
    def delay(w):
        p=0; o=[]
        for x in w: o.append(p); p=x
        return tuple(o)
    def toggle(w): return tuple(i%2 for i,_ in enumerate(w))
    def zero(w): return (0,)*len(w)
    return [('identity',identity),('not',neg),('delay1',delay),('toggle',toggle),('const0',zero)]


def quotient(cs):
    par=list(range(len(cs)))
    def find(x):
        while par[x]!=x:
            par[x]=par[par[x]]; x=par[x]
        return x
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b: par[b]=a
    checks=0; eqpairs=0
    for i in range(len(cs)):
        for j in range(i+1,len(cs)):
            eq=equivalent(cs[i],cs[j]); checks+=1
            if eq: eqpairs+=1; union(i,j)
    groups={}
    for i in range(len(cs)): groups.setdefault(find(i),[]).append(i)
    roots=sorted(groups,key=lambda r:min(groups[r])); cls={}
    for ci,r in enumerate(roots):
        for i in groups[r]: cls[i]=ci
    return groups,cls,checks,eqpairs


def development_distances(cs):
    index={c:i for i,c in enumerate(cs)}; adj=[set() for _ in cs]
    for i,c in enumerate(cs[:4]):
        b=list(c[1])
        for k in range(2):
            z=b.copy(); z[k]^=1; j=index[('S',tuple(z))]; adj[i].add(j); adj[j].add(i)
    for i,c in enumerate(cs[4:],start=4):
        bits=[b for row in c[1] for b in row]
        for k in range(8):
            z=bits.copy(); z[k]^=1
            rows=tuple((z[2*r],z[2*r+1]) for r in range(4)); j=index[('M',rows)]
            adj[i].add(j); adj[j].add(i)
    for i,c in enumerate(cs[:4]):
        o=c[1]; lift=('M',((0,o[0]),(0,o[1]),(0,o[0]),(0,o[1])))
        adj[i].add(index[lift])
    d=[None]*len(cs); d[0]=0; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if d[v] is None: d[v]=d[u]+1; q.append(v)
    assert all(x is not None for x in d)
    return d


def pareto(vectors):
    def dom(a,b): return all(x<=y for x,y in zip(a,b)) and any(x<y for x,y in zip(a,b))
    return [i for i,v in enumerate(vectors) if not any(dom(w,v) for j,w in enumerate(vectors) if j!=i)]


def build_atlas():
    cs=candidates(); assert len(cs)==260
    groups,cls,pair_checks,eqpairs=quotient(cs)
    assert len(groups)==148 and pair_checks==33670 and eqpairs==1624
    ws=words_upto(4); ts=targets(); dist=development_distances(cs)
    caps=[]
    for c in cs:
        caps.append(tuple(all(run(c,w)==fn(w) for w in ws) for _,fn in ts))
    assert all(len({caps[i] for i in members})==1 for members in groups.values())
    rows=[]; vectors=[]
    for i,c in enumerate(cs):
        res={'state_cells':0 if c[0]=='S' else 1,'truth_rows':2 if c[0]=='S' else 4}
        rows.append({
          'candidate_id':f'M{i:03d}', 'presentation':'STATELESS' if c[0]=='S' else 'ONE_BIT_FEEDBACK',
          'operational_class':f'C{cls[i]:03d}', 'capability_exact':[int(x) for x in caps[i]],
          'resources':res, 'development_distance_from_S00':dist[i]
        })
        vectors.append(tuple(0 if x else 1 for x in caps[i])+(res['state_cells'],res['truth_rows']))
    front=pareto(vectors)
    atlas={'schema':'AJ11_COMPLETE_BOUNDED_ATLAS_V1','scope':{'candidate_count':260,'operational_class_count':148,'tasks':[n for n,_ in ts],'max_word_length':4},'rows':rows}
    canonical=json.dumps(atlas,sort_keys=True,separators=(',',':'))
    digest=hashlib.sha256(canonical.encode()).hexdigest()
    return atlas,digest,front,dist,groups,caps


def main():
    atlas,digest,front,dist,groups,caps=build_atlas()
    expected='09a99f29d2d349d7f28855d3a32776667c65cd1a707ea89129fd77c3328a16ed'
    assert digest==expected
    assert front==[0,1,2,43,169]
    cap_hist=Counter(tuple(x) for x in caps)
    result={
      'status':'GREEN',
      'bounded_scope':{'presentations':260,'operational_classes':148,'tasks':5,'protected_words':31},
      'atlas_sha256':digest,
      'operational_class_size_histogram':{str(k):v for k,v in sorted(Counter(map(len,groups.values())).items())},
      'capability_vector_histogram':{'/'.join(map(str,map(int,k))):v for k,v in sorted(cap_hist.items())},
      'development_all_260_reachable':True,
      'development_distance_histogram':{str(k):v for k,v in sorted(Counter(dist).items())},
      'development_max_distance':max(dist),
      'pareto_frontier_candidate_ids':[f'M{i:03d}' for i in front],
      'pareto_objective':'five task-failure coordinates + state_cells + truth_rows; no scalarization',
      'bounded_terminal':'COMPLETE_GMI_ATLAS_AT_BOUND_B',
      'unbounded_boundary':{
        'syntax_programs':'EFFECTIVELY_ENUMERABLE_UNDER_REGISTERED_FINITE_ALPHABET',
        'semantic_equivalence':'UNDECIDABLE_IN_GENERAL_AT_TURING_COMPLETE_SCOPE',
        'nontrivial_semantic_properties':'RICE_BOUNDARY_APPLIES_AT_STANDARD_SCOPE',
        'required_scientific_policy':'OPEN_GENERATIVITY_PLUS_BLIND_RECOVERY_PLUS_PROSPECTIVE_UNKNOWN_NOT_TERMINATING_SEMANTIC_CATALOGUE'
      },
      'forbidden_terminal':'ALL_MACHINE_INTELLIGENCES_COMPLETELY_CLASSIFIED',
      'claim_ceiling':'AJ11_COMPLETE_GMI_ATLAS_AT_REGISTERED_FINITE_BOUND_AND_UNBOUNDED_SEMANTIC_BOUNDARY'
    }
    (HERE/'ATLAS_V1.json').write_text(json.dumps(atlas,indent=2,sort_keys=True)+'\n')
    (HERE/'RESULT_V1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__': main()
