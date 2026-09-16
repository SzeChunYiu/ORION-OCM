from __future__ import annotations
import json
from collections import Counter,defaultdict,deque
from pathlib import Path
HERE=Path(__file__).resolve().parent
ALLOWED_CLASS={'FOUNDATIONAL','SPECIALIZATION','PARENT_OWNED','EMPIRICAL_LAW','SUPERSEDED_REDUNDANT'}
INTERFACES={'GEN','DEV','REQ','REL','CAP','SEL','EVID'}

def load(name): return json.loads((HERE/name).read_text())

def main():
    dag=load('GMI_THEORY_DEPENDENCY_DAG.json'); cross=load('NOTATION_CROSSWALK.json')
    nodes={n['id']:n for n in dag['nodes']}
    assert len(nodes)==len(dag['nodes'])
    assert set(dag['canonical_interfaces'])==INTERFACES
    assert dag['integration_spine']=='ISSUE_833' and nodes['ISSUE_833']['role']=='INTEGRATION_SPINE'
    assert dag['no_new_umbrella_gate']=='NO_NEW_GMI_UMBRELLA_UNTIL_CONVERGENCE_V1'
    for n in nodes.values():
        assert n['class'] in ALLOWED_CLASS
        assert isinstance(n['owner'],str) and n['owner']
        assert n['interfaces'] and set(n['interfaces'])<=INTERFACES
        assert all(d in nodes for d in n['deps'])
    # DAG acyclicity.
    indeg={k:0 for k in nodes}; children=defaultdict(list)
    for k,n in nodes.items():
        for d in n['deps']: indeg[k]+=1; children[d].append(k)
    q=deque(k for k,v in indeg.items() if v==0); seen=[]
    while q:
        x=q.popleft(); seen.append(x)
        for y in children[x]:
            indeg[y]-=1
            if indeg[y]==0:q.append(y)
    assert len(seen)==len(nodes)
    # Required theory-to-interface ownership.
    required={
      'HSG_DEV':'DEV','REQ_PROVENANCE':'REQ','REL_EQUIVALENCE':'REL',
      'CAPABILITY_CORE':'CAP','SEL_MORPHOLOGY':'SEL','AJ_PROCESS_BOTTOM':'GEN','EVID_AA_AD':'EVID'
    }
    for node,iface in required.items(): assert iface in nodes[node]['interfaces']
    # Barrier calculus must be cross-cutting and not itself an integration spine.
    b=nodes['BARRIER_CALCULUS']; assert len(b['interfaces'])>=5 and b['role']=='CROSS_CUTTING_BOUNDARY_CALCULUS'
    assert [n['id'] for n in nodes.values() if n['role']=='INTEGRATION_SPINE']==['ISSUE_833']
    # Authority reconciliation is frozen exactly.
    assert dag['authority_reconciliation']['#233']=='developmental-dynamics formal module'
    assert dag['authority_reconciliation']['#373']=='convergence/governance module'
    assert 'historical' in dag['authority_reconciliation']['#602']
    # Parent-owned mathematics has external parent ownership and is not relabelled as GMI novelty.
    assert nodes['PARENT_BLACKWELL']['class']=='PARENT_OWNED'
    assert nodes['PARENT_NFL']['class']=='PARENT_OWNED'
    # Discriminator: universal G0 neutrality does not survive the registered counterexample package.
    assert nodes['G0_STRUCTURAL_BIAS_BOUNDARY']['role']=='DISCRIMINATOR_COUNTEREXAMPLE'
    # Crosswalk covers every canonical interface at least once (cross-cutting excluded).
    covered={e['interface'] for e in cross['entries'] if e['interface'] in INTERFACES}
    assert covered==INTERFACES
    hist=Counter(n['class'] for n in nodes.values())
    result={
      'status':'GREEN','registered_material_nodes':len(nodes),'dag_acyclic':True,
      'topological_nodes':len(seen),'class_histogram':dict(sorted(hist.items())),
      'canonical_interfaces':sorted(INTERFACES),'notation_entries':len(cross['entries']),
      'single_integration_spine':'ISSUE_833','development_authority':'#233','governance_authority':'#373','historical_baseline':'#602',
      'barrier_role':'CROSS_CUTTING_BOUNDARY_CALCULUS','parent_owned_nodes':['PARENT_BLACKWELL','PARENT_NFL'],
      'registered_discriminator':'G0_STRUCTURAL_BIAS_BOUNDARY',
      'gate':'NO_NEW_GMI_UMBRELLA_UNTIL_CONVERGENCE_V1',
      'claim_ceiling':'AI0_CANONICAL_GMI_CONVERGENCE_SPINE_AND_AUTHORITY_DAG_V1'
    }
    (HERE/'RESULT_V1.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__': main()
