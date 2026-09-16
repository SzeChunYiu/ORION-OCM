from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations, permutations, product
from typing import Iterable, Tuple
import json

SOURCE_MAIN='43102437ebcbf6f818bb58b45470beffaf865029'
FREEZE_COMMIT='7e81a8fedb8f367238f8339200ab15c79e9429bc'
CLAIM_CEILING='GMI_FINITE_LOCAL_GLOBAL_GRAPH_OPERATOR_SEMANTICS_AT_REGISTERED_SCOPE'
FORBIDDEN_PROMOTIONS=(
 'UNIVERSAL_GRAPH_EXPRESSIVITY','GNN_DERIVED','NEURAL_ARCHITECTURE_DERIVED',
 'ARBITRARY_GROUP_EQUIVARIANCE','INFINITE_GRAPH_RESULT','STOCHASTIC_OPERATOR_COMPLETE',
 'MULTI_AGENT_COMPLETE','MORPHOLOGY_SELECTION_OPTIMAL','COMPLETE_GMI')
V=(0,1,2); Z3=(0,1,2)
ALL_EDGES=((0,1),(0,2),(1,2))

@dataclass(frozen=True)
class Graph:
    edges: frozenset[Tuple[int,int]]

@dataclass(frozen=True)
class StepResult:
    state: Tuple[int,int,int]
    resources: Tuple[int,int,int,int]  # site_reads, site_writes, edge_reads, aggregate_ops


def validate_state(state: Iterable[int]) -> Tuple[int,int,int]:
    s=tuple(state)
    if len(s)!=3: raise ValueError('STATE_DOMAIN')
    if any(type(x) is not int or x not in Z3 for x in s): raise ValueError('STATE_VALUE')
    return s


def make_graph(raw_edges: Iterable[Tuple[int,int]]) -> Graph:
    seen=set(); canon=set()
    for edge in raw_edges:
        if not isinstance(edge,(tuple,list)) or len(edge)!=2: raise ValueError('MALFORMED_EDGE')
        u,v=edge
        if type(u) is not int or type(v) is not int or u not in V or v not in V: raise ValueError('EDGE_OUTSIDE_CARRIER')
        if u==v: raise ValueError('SELF_LOOP')
        e=(min(u,v),max(u,v))
        if e in seen: raise ValueError('DUPLICATE_EDGE')
        seen.add(e); canon.add(e)
    return Graph(frozenset(canon))


def neighbors(graph: Graph, v:int) -> Tuple[int,...]:
    out=[]
    for a,b in graph.edges:
        if a==v: out.append(b)
        elif b==v: out.append(a)
    return tuple(sorted(out))


def pointwise(state: Iterable[int], graph: Graph) -> StepResult:
    s=validate_state(state)
    if not isinstance(graph,Graph): raise ValueError('INVALID_GRAPH')
    return StepResult(tuple((x+1)%3 for x in s),(3,3,0,0))


def global_broadcast(state: Iterable[int], graph: Graph, *, fold:str='sum_mod3') -> StepResult:
    s=validate_state(state)
    if not isinstance(graph,Graph): raise ValueError('INVALID_GRAPH')
    if fold!='sum_mod3': raise ValueError('NONCOMMUTATIVE_OR_UNREGISTERED_FOLD')
    agg=sum(s)%3
    return StepResult(tuple((x+agg)%3 for x in s),(6,3,0,2))


def neighbor_update(state: Iterable[int], graph: Graph, *, fold:str='sum_mod3') -> StepResult:
    s=validate_state(state)
    if not isinstance(graph,Graph): raise ValueError('INVALID_GRAPH')
    if fold!='sum_mod3': raise ValueError('NONCOMMUTATIVE_OR_UNREGISTERED_FOLD')
    out=[]; agg_ops=0
    for v in V:
        ns=neighbors(graph,v)
        vals=[s[u] for u in ns]
        agg=sum(vals)%3 if vals else 0
        agg_ops += max(len(vals)-1,0)
        out.append((s[v]+agg)%3)
    e2=2*len(graph.edges)
    return StepResult(tuple(out),(3+e2,3,e2,agg_ops))


def recount_resources(op:str, graph:Graph)->Tuple[int,int,int,int]:
    if op=='POINTWISE': return (3,3,0,0)
    if op=='GLOBAL_BROADCAST': return (6,3,0,2)
    if op=='NEIGHBOR_UPDATE':
        deg=[len(neighbors(graph,v)) for v in V]; e2=sum(deg)
        return (3+e2,3,e2,sum(max(d-1,0) for d in deg))
    raise ValueError('UNKNOWN_OPERATOR')


def validate_perm(pi: Iterable[int])->Tuple[int,int,int]:
    p=tuple(pi)
    if len(p)!=3 or set(p)!=set(V): raise ValueError('NON_BIJECTIVE_RELABELING')
    return p


def transport_state(state:Iterable[int],pi:Iterable[int])->Tuple[int,int,int]:
    s=validate_state(state); p=validate_perm(pi)
    out=[0]*3
    for old,new in enumerate(p): out[new]=s[old]
    return tuple(out)


def transport_graph(graph:Graph,pi:Iterable[int])->Graph:
    p=validate_perm(pi)
    return make_graph((p[u],p[v]) for u,v in graph.edges)


def all_graphs():
    for bits in product((0,1),repeat=3):
        yield make_graph(e for e,b in zip(ALL_EDGES,bits) if b)


def equivariance_census():
    ops=(('POINTWISE',pointwise),('GLOBAL_BROADCAST',global_broadcast),('NEIGHBOR_UPDATE',neighbor_update))
    mism={name:0 for name,_ in ops}; resource_mism={name:0 for name,_ in ops}; comparisons={name:0 for name,_ in ops}
    for g in all_graphs():
      for s in product(Z3,repeat=3):
       for p in permutations(V):
        ts=transport_state(s,p); tg=transport_graph(g,p)
        for name,op in ops:
            a=op(s,g); b=op(ts,tg)
            comparisons[name]+=1
            if transport_state(a.state,p)!=b.state: mism[name]+=1
            if a.resources!=b.resources or a.resources!=recount_resources(name,g) or b.resources!=recount_resources(name,tg): resource_mism[name]+=1
    return {'comparisons':comparisons,'equivariance_mismatches':mism,'resource_mismatches':resource_mism}


def separation_hostiles():
    s=(1,1,0); empty=make_graph(()); edge=make_graph(((0,1),))
    topology={
      'pointwise_same': pointwise(s,empty).state==pointwise(s,edge).state,
      'global_same': global_broadcast(s,empty).state==global_broadcast(s,edge).state,
      'neighbor_changes': neighbor_update(s,empty).state!=neighbor_update(s,edge).state,
    }
    base=(1,0,0); remote=(1,0,1); g01=make_graph(((0,1),))
    remote_witness={
      'pointwise_site0_same': pointwise(base,g01).state[0]==pointwise(remote,g01).state[0],
      'global_site0_changes': global_broadcast(base,g01).state[0]!=global_broadcast(remote,g01).state[0],
      'neighbor_site0_same': neighbor_update(base,g01).state[0]==neighbor_update(remote,g01).state[0],
    }
    nb0=(1,0,0); nb1=(1,1,0)
    neighbor_witness={'neighbor_state_changes_site0':neighbor_update(nb0,g01).state[0]!=neighbor_update(nb1,g01).state[0]}
    fixed=(1,1,2); g_empty=make_graph(()); g_incident=make_graph(((0,1),)); g_nonincident=make_graph(((1,2),))
    edge_witness={
      'incident_edge_changes_site0':neighbor_update(fixed,g_empty).state[0]!=neighbor_update(fixed,g_incident).state[0],
      'nonincident_edge_same_site0':neighbor_update(fixed,g_empty).state[0]==neighbor_update(fixed,g_nonincident).state[0],
    }
    return {'topology':topology,'remote':remote_witness,'neighbor':neighbor_witness,'edge':edge_witness}


def malformed_hostiles():
    out={}
    cases=[('short_state',lambda:validate_state((0,1))),('bad_value',lambda:validate_state((0,1,3))),('outside_edge',lambda:make_graph(((0,3),))),('self_loop',lambda:make_graph(((1,1),))),('duplicate',lambda:make_graph(((0,1),(1,0)))),('bad_perm',lambda:validate_perm((0,0,2))),('bad_fold',lambda:global_broadcast((0,1,2),make_graph(()),fold='left_projection'))]
    for name,fn in cases:
        try: fn(); out[name]='ACCEPTED'
        except ValueError as e: out[name]=str(e)
    return out


def graph_resource_histogram():
    out={}
    for g in all_graphs():
        key=str(len(g.edges))
        out.setdefault(key,set()).add(recount_resources('NEIGHBOR_UPDATE',g))
    return {k:[list(x) for x in sorted(v)] for k,v in sorted(out.items())}


def build_receipt():
    census=equivariance_census(); sep=separation_hostiles(); mal=malformed_hostiles(); rh=graph_resource_histogram()
    all_green=(all(v==1296 for v in census['comparisons'].values()) and all(v==0 for v in census['equivariance_mismatches'].values()) and all(v==0 for v in census['resource_mismatches'].values()) and all(all(x for x in block.values()) for block in sep.values()) and 'ACCEPTED' not in mal.values())
    return {'schema':'GMI833LocalGlobalGraphOpsReceiptV1','parent_issue':833,'issue':882,'source_main':SOURCE_MAIN,'freeze_commit':FREEZE_COMMIT,'carrier':{'sites':list(V),'values':list(Z3),'graphs':8,'states':27,'permutations':6},'operators':['POINTWISE','GLOBAL_BROADCAST','NEIGHBOR_UPDATE'],'equivariance_census':census,'separation_hostiles':sep,'malformed_hostiles':mal,'neighbor_resource_histogram':rh,'claim_ceiling':CLAIM_CEILING,'forbidden_promotions':list(FORBIDDEN_PROMOTIONS),'terminal':'GMI_833_LOCAL_GLOBAL_GRAPH_OPS_V1_ALL_GREEN' if all_green else 'RED'}


def canonical_json(obj): return json.dumps(obj,indent=2,sort_keys=True,separators=(',',': '))+'\n'
def main(): print(canonical_json(build_receipt()),end='')
if __name__=='__main__': main()
