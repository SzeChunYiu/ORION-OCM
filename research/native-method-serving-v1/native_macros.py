"""Six atomic bijections from sealed recipes; constructor and recipe must agree."""
import copy,itertools
from vendor import common as C
from native_contract import require
H=C.load("native_recipe");T=C.load("typed_terms")
def compile_macros(methods,eligible,removed,bank,constructor,work):
    require(len(eligible)==len(set(eligible)) and set(eligible)<=set(methods),'eligible IDs')
    require(set(removed)<=set(eligible),'removed ID outside eligibility')
    formulas=[['|-']+r['tokens'] for r in bank['wff']];lookup={tuple(t):i for i,t in enumerate(formulas)}
    actions=[]
    for key in sorted(set(eligible)-set(removed)):
        payload=methods[key];body=payload['body'];trace=payload['trace'];contracts=payload['contracts']
        for perm in itertools.permutations(T.ATOMS):
            mapping=dict(zip(T.ATOMS,perm));holes=['macro-hole-'+str(i) for i in range(len(body['premises']))]
            renamed=copy.deepcopy(body)
            for field in ('premises',):renamed[field]=[T.rename(p,mapping) for p in body[field]]
            renamed['query']=T.rename(body['query'],mapping)
            for node in renamed['nodes']:
                node['output']=T.rename(node['output'],mapping)
                if 'substitution' in node:node['substitution']={k:T.rename(v,mapping) for k,v in node['substitution'].items()}
            hypotheses=[{'label':h,'statement':p} for h,p in zip(holes,renamed['premises'])]
            emitted=constructor.construct(trace,contracts,mapping,hypotheses,4096)
            expected=H.emit(renamed,contracts,holes,work)
            require(emitted['proof']==expected['proof'] and emitted['target']==renamed['query'],'admitted constructor/recipe equality')
            for node in renamed['nodes']:
                if node['output'][0]=='|-':require(tuple(node['output']) in lookup,'BANK_INCOMPLETE: learned intermediate')
            require(tuple(renamed['query']) in lookup and all(tuple(p) in lookup for p in renamed['premises']),'BANK_INCOMPLETE: learned boundary')
            action={'kind':'macro','method_id':key,'substitution':{k:[v] for k,v in mapping.items()},
                    'query':lookup[tuple(renamed['query'])],'premises':[lookup[tuple(p)] for p in renamed['premises']],
                    'template':emitted['proof'],'holes':holes}
            action['id']=C.raw_id(C.canonical(action))['sha256'];actions.append(action)
            H.count(work,'macro_instances');H.count(work,'constructor_node_validations',len(trace['nodes']))
    return actions
