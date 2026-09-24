from __future__ import annotations

import itertools, json
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE=Path(__file__).resolve().parent
BITS=(0,1)


def stateless_candidates():
    return [("S",outs) for outs in itertools.product(BITS,repeat=2)]


def stateful_candidates():
    out=[]
    for bits in itertools.product(BITS,repeat=8):
        rows=tuple((bits[2*i],bits[2*i+1]) for i in range(4))
        out.append(("M",rows))
    return out


def as_transducer(c):
    typ,data=c
    if typ=="S": return 1,{(0,0):(0,data[0]),(0,1):(0,data[1])}
    return 2,{(0,0):data[0],(0,1):data[1],(1,0):data[2],(1,1):data[3]}


def run(c,word,initial=0):
    _,t=as_transducer(c); s=initial; ys=[]
    for x in word:
        s,y=t[(s,x)]; ys.append(y)
    return tuple(ys)


def equivalent_all_words(a,b):
    _,ta=as_transducer(a); _,tb=as_transducer(b)
    stack=[(0,0)]; seen=set()
    while stack:
        sa,sb=stack.pop()
        if (sa,sb) in seen: continue
        seen.add((sa,sb))
        for x in BITS:
            na,ya=ta[(sa,x)]; nb,yb=tb[(sb,x)]
            if ya!=yb: return False
            stack.append((na,nb))
    return True


def frozen_tasks():
    tasks={}
    tasks['IDENTITY1']=[((x,),(x,)) for x in BITS]
    tasks['NOT1']=[((x,),(1-x,)) for x in BITS]
    delay=[]; parity=[]
    for n in (1,2,3):
        for w in itertools.product(BITS,repeat=n):
            prev=0; yd=[]
            p=0; yp=[]
            for x in w:
                yd.append(prev); prev=x
                p ^= x; yp.append(p)
            delay.append((w,tuple(yd))); parity.append((w,tuple(yp)))
    tasks['DELAY1_H3']=delay
    tasks['PARITY_H3']=parity
    return tasks


def error(c,cases):
    return sum(sum(y!=t for y,t in zip(run(c,w),target)) for w,target in cases)


def bits_repr(c):
    typ,data=c
    return tuple(data) if typ=='S' else tuple(v for row in data for v in row)


def canonical_embed(s):
    out=s[1]
    return ('M',((0,out[0]),(0,out[1]),(0,out[0]),(0,out[1])))


def dominates(a,b):
    return all(x<=y for x,y in zip(a,b)) and any(x<y for x,y in zip(a,b))


def main():
    stateless=stateless_candidates(); stateful=stateful_candidates(); allc=stateless+stateful
    assert len(stateless)==4 and len(stateful)==256 and len(allc)==260

    # Exact all-word operational quotient.
    parent=list(range(len(allc)))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b: parent[b]=a
    pair_checks=0; eq_pairs=0
    for i in range(len(allc)):
        for j in range(i+1,len(allc)):
            eq=equivalent_all_words(allc[i],allc[j]); pair_checks+=1
            if eq: eq_pairs+=1; union(i,j)
    groups=defaultdict(list)
    for i in range(len(allc)): groups[find(i)].append(i)
    classes=sorted(groups.values(),key=lambda g:min(g))
    cid={i:k for k,g in enumerate(classes) for i in g}
    assert len(classes)==148 and Counter(map(len,classes))==Counter({1:144,29:4})

    # Complete finite capability/resource atlas.
    tasks=frozen_tasks(); task_names=list(tasks)
    errors=[tuple(error(c,tasks[k]) for k in task_names) for c in allc]
    resources=[(0,2) if c[0]=='S' else (1,4) for c in allc]
    vectors=[errors[i]+resources[i] for i in range(len(allc))]
    # Behavioral-equivalent presentations have identical registered capability coordinates.
    for g in classes:
        assert len({errors[i] for i in g})==1
    profile_hist=Counter(errors)

    pareto=[i for i,a in enumerate(vectors) if not any(dominates(b,a) for j,b in enumerate(vectors) if j!=i)]
    assert len(pareto)==15
    weights={
      'BALANCED':(1,1,1,1,1,1),
      'DELAY_HEAVY':(1,1,4,1,1,1),
      'RESOURCE_HEAVY':(1,1,1,1,5,2),
      'PARITY_HEAVY':(1,1,1,4,1,1),
    }
    prefs={}
    for name,w in weights.items():
        vals=[sum(x*y for x,y in zip(v,w)) for v in vectors]
        m=min(vals); inds=[i for i,v in enumerate(vals) if v==m]
        assert set(inds)<=set(pareto)
        prefs[name]={'minimum':m,'argmin':inds}
    assert prefs['BALANCED']=={'minimum':24,'argmin':[43,64]}
    assert prefs['DELAY_HEAVY']=={'minimum':24,'argmin':[43]}
    assert prefs['RESOURCE_HEAVY']=={'minimum':32,'argmin':[43,64]}
    assert prefs['PARITY_HEAVY']=={'minimum':24,'argmin':[64]}

    # Complete finite developmental graph.
    idx={c:i for i,c in enumerate(allc)}
    adj=[set() for _ in allc]
    for i,c in enumerate(allc):
        bi=bits_repr(c)
        for j in range(i+1,len(allc)):
            d=allc[j]
            if c[0]==d[0]:
                bj=bits_repr(d)
                if sum(x!=y for x,y in zip(bi,bj))==1:
                    adj[i].add(j); adj[j].add(i)
    for s in stateless:
        a=idx[s]; b=idx[canonical_embed(s)]
        adj[a].add(b); adj[b].add(a)
    edge_count=sum(map(len,adj))//2
    assert edge_count==1032
    class_edges=set()
    for i,ns in enumerate(adj):
        for j in ns:
            if cid[i]!=cid[j]: class_edges.add(tuple(sorted((cid[i],cid[j]))))
    assert len(class_edges)==660

    seed=0; dist={seed:0}; q=deque([seed])
    while q:
        u=q.popleft()
        if dist[u]==2: continue
        for v in adj[u]:
            if v not in dist: dist[v]=dist[u]+1; q.append(v)
    assert Counter(dist.values())==Counter({0:1,1:3,2:11})

    # Operational duplicate collapse must not erase resource/development distinctions.
    mixed_resource_classes=sum(1 for g in classes if len({resources[i] for i in g})>1)
    assert mixed_resource_classes==4

    result={
      'status':'GREEN',
      'finite_universe_presentations':260,
      'operational_pair_checks':pair_checks,
      'operational_equivalent_pairs':eq_pairs,
      'operational_classes':148,
      'class_size_histogram':{str(k):v for k,v in sorted(Counter(map(len,classes)).items())},
      'registered_task_family':task_names,
      'capability_profile_count':len(profile_hist),
      'complete_presentations_evaluated':260,
      'pareto_frontier_presentations':pareto,
      'pareto_frontier_size':len(pareto),
      'frozen_preference_queries':prefs,
      'development_edges':edge_count,
      'projected_operational_class_edges':len(class_edges),
      'radius2_reachability_from_constant_zero':{'total':len(dist),'distance_histogram':{str(k):v for k,v in sorted(Counter(dist.values()).items())}},
      'operational_classes_with_multiple_resource_vectors':mixed_resource_classes,
      'finite_terminal':'COMPLETE_GMI_ATLAS_AT_BOUND_B',
      'finite_terminal_scope':'frozen 260-presentation binary universe + four-task family + declared resources/development law',
      'unbounded_boundary':['syntax/enumerable does not imply semantic-decidable','halting/Rice/extensional equivalence barriers preserved under standard Turing computation','open generativity + UNKNOWN required instead of terminating semantic catalogue'],
      'forbidden_promotions':['ALL_MACHINE_INTELLIGENCES_COMPLETELY_CLASSIFIED','COMPLETE_GMI'],
      'claim_ceiling':'AJ11_COMPLETE_BOUNDED_MACHINE_CAPABILITY_DEVELOPMENT_ATLAS_AND_UNBOUNDED_SEMANTIC_OPENNESS_AT_REGISTERED_SCOPE'
    }
    (HERE/'RESULT_V1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__': main()
