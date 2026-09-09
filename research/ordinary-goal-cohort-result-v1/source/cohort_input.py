"""Adapt pinned historical members; preserve physical variables and proof meaning."""
import copy
import life_native as N
import trace_source as S
from goal_library import identity,raw_identity,require
P=chr(36)+'p';F=chr(36)+'f';A=chr(36)+'a'
def adapt(cohort,base,old_suffix,cohort_pin):
    require(cohort['status']=='HISTORICAL_TRAINING_MATERIALIZATION_ONLY','historical packet')
    require(len(cohort['rows'])==22,'exact historical population')
    members=[];original_claims=[]
    for i,r in enumerate(cohort['rows']):
        cut=r['historical_cut'];p=cut['proposal'];a=r['historical_admission'];ctx=cut['context']
        require(r['canonical_id']==cut['canonical_id']==a['canonical_id'],'member identity')
        require(r['admission_index']==r['extraction_index']==i and r['label']==a['label']==f'cut-lemma-{i:02d}','issued order')
        require(a['target']==p['target'] and a['n_hypotheses']==len(p['hypotheses']) and
                a['n_proof']==len(p['proof']) and a['source_label']==r['source_root']['label'],'historical admission fields')
        ps=ctx['parameters'];require(len(ps)==3 and ctx['dv']==[],'retained three-parameter/no-DV context')
        mapping={v['id']:v['variable'] for v in ps}
        translate=lambda ts:[mapping.get(t,t) for t in ts]
        require(translate(cut['body']['query'])==p['target'] and
                [translate(x) for x in cut['body']['premises']]==[h['statement'] for h in p['hypotheses']],'retained target/essential transport')
        floating=[]
        for parameter in ps:
            f=base[parameter['floating_label']]
            require(f['kind']==F and f['statement']==[parameter['type'],parameter['variable']],'current floating contract')
            floating.append(f)
        floating.sort(key=lambda row:row['span'][0])
        require(len({f['label'] for f in floating})==3,'distinct current floating labels')
        required=set(p['target'])|{t for h in p['hypotheses'] for t in h['statement']}
        require(all(f['statement'][1] in required for f in floating),'all three floats must be mandatory')
        row={'label':r['label'],'kind':P,'statement':p['target'],
             'floating':[{'label':f['label'],'statement':f['statement']} for f in floating],
             'essential':p['hypotheses'],'dv':[]}
        origin={'cohort_file':cohort_pin,'canonical_id':r['canonical_id'],'source_root':r['source_root'],
                'historical_row':identity(r),'cut':identity(cut),'admission':identity(a),'original_proposal':identity(p)}
        members.append({'contract':copy.deepcopy(row),'proof':copy.deepcopy(p['proof']),'origin':origin})
        original_claims.append({'label':r['label'],'query':p['target'],'premises':[h['statement'] for h in p['hypotheses']],
            'holes':[h['label'] for h in p['hypotheses']],'proof':p['proof'],
            'parameters':[{'type':f['statement'][0],'variable':f['statement'][1],'floating_label':f['label']} for f in floating]})
    require(N.serialize(original_claims)==old_suffix,'exact original proposed suffix')
    return members

def transported_claims(members,transport,suffix):
    require(len(transport['bindings'])==len(members)==22,'complete transport')
    claims=[]
    for i,(m,b) in enumerate(zip(members,transport['bindings'])):
        row=m['contract'];old=[h['label'] for h in row['essential']];new=[f'cohort-e-{i}-{j}' for j in range(len(old))]
        expected=[{'old':a,'new':n,'statement':h['statement']} for a,n,h in zip(old,new,row['essential'])]
        require(b['index']==i and b['theorem_label']==row['label'] and b['original_member']==identity(m)
                and b['origin']==m['origin'] and b['essential_label_renaming']==expected,'exact scoped transport binding')
        rename=dict(zip(old,new));proof=[rename.get(t,t) for t in m['proof']]
        require(b['transported_proof']==identity(proof),'transported normal proof')
        claims.append({'label':row['label'],'query':row['statement'],'premises':[h['statement'] for h in row['essential']],
            'holes':new,'proof':proof,'parameters':[{'type':f['statement'][0],'variable':f['statement'][1],
            'floating_label':f['label']} for f in row['floating']]})
    N.validate_claims(claims);require(N.serialize(claims)==suffix,'independently issued transported suffix')
    return claims
