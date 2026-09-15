from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class ValidationError(ValueError): pass

def load(name): return json.loads((ROOT/name).read_text())

def validate_graph(spine):
    nodes=spine['nodes']; by={}
    for n in nodes:
        if n['id'] in by: raise ValidationError(f"duplicate id {n['id']}")
        if n['kind'] not in {'AXIOM','DEFINITION','THEOREM'}: raise ValidationError(f"bad kind {n['id']}")
        by[n['id']]=n
    axioms=[n['id'] for n in nodes if n['kind']=='AXIOM']
    if axioms != ['AX-1','AX-2','AX-3','AX-4','AX-5']: raise ValidationError(f"axiom basis mismatch {axioms}")
    if any(by[a]['dependencies'] for a in axioms): raise ValidationError('primitive axioms must have no dependencies')
    for n in nodes:
        for d in n['dependencies']:
            if d not in by: raise ValidationError(f"dangling dependency {n['id']}->{d}")
    temp=set(); perm=set()
    def visit(x):
        if x in perm: return
        if x in temp: raise ValidationError(f"cycle at {x}")
        temp.add(x)
        for d in by[x]['dependencies']: visit(d)
        temp.remove(x); perm.add(x)
    for x in by: visit(x)
    memo={}
    def ancestors(x):
        if x in memo: return memo[x]
        out=set(by[x]['dependencies'])
        for d in by[x]['dependencies']: out |= ancestors(d)
        memo[x]=out; return out
    for n in nodes:
        if n['kind']=='DEFINITION' and not (ancestors(n['id']) & set(axioms)):
            raise ValidationError(f"definition not grounded in axioms: {n['id']}")
    return by

def validate_reduction(reduction, by):
    rows=reduction['rows']
    if len(rows) < 10: raise ValidationError('reduction ledger incomplete')
    for row in rows:
        if row['target'] not in by: raise ValidationError(f"unknown target {row['target']}")
        if not row['owner'].startswith('#'): raise ValidationError(f"missing owner {row['object']}")
    blobs={p['issue']:p['blob'] for p in reduction['parent_manifests']}
    expected={837:'deb8ec3ef57887790a874e01656c0cb598b2c908',846:'e3aa9f88e085478586c2c53a4f1d0a2546bb90e8',848:'58b80724ef8651f3e476fdddddf2fe3a703fd5c2',851:'01114b6e67c727575cfcff267d88eacd13274486'}
    if blobs != expected: raise ValidationError(f"parent manifest pins mismatch: {blobs}")

def validate_all():
    spine=load('AXIOM_SPINE_V1.json'); red=load('FOUNDATION_REDUCTION_V1.json')
    by=validate_graph(spine); validate_reduction(red,by)
    return {'axioms':5,'nodes':len(by),'definitions':sum(n['kind']=='DEFINITION' for n in spine['nodes']),'theorems':sum(n['kind']=='THEOREM' for n in spine['nodes']),'reduction_rows':len(red['rows'])}

if __name__=='__main__':
    print(json.dumps(validate_all(),indent=2,sort_keys=True))
