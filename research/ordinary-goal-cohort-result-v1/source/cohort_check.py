"""Batch adaptation of existing exact native-result binding; one native pass."""
import life_native as N
import trace_source as S
from goal_library import Library,identity,raw_identity,require,proof_record
P=chr(36)+'p';A=chr(36)+'a';F=chr(36)+'f';E=chr(36)+'e'
def base_authority(rows,prior,base_pin):
    labels=[r['label'] for r in rows.values() if r['kind']==P]
    axioms=[{'contract':S.contract(r),'raw':r['raw']} for r in rows.values() if r['kind']==A]
    require(len(labels)==4223 and labels==prior['verified_labels'],'exact ordered base proofs')
    require(len(axioms)==100 and axioms==prior['axioms'],'exact existing axiom contracts and bytes')
    require(prior['terminal']=='FRESH_PREFIX_NATIVE_VERIFIED' and
            {k:prior['prefix'][k] for k in ('bytes','sha256')}==base_pin,'prior base identity only')
    return {'prefix':base_pin,'prefix_proof_count':4223,'trusted_assertion_count':100,
            'trusted_assertions_sha256':identity([a['contract']['label'] for a in axioms])['sha256']}

def bind_result(result,claims,base_raw,joined_raw,base,joined,authority,sources,prefix_path,archive):
    require(result['terminal']=='NATIVE_VERIFIED' and result['native_calls']==1 and result['error'] is None,'fresh native success')
    suffix=N.serialize(claims);selected=[c['label'] for c in claims]
    labels=[r['label'] for r in base.values() if r['kind']==P]
    trusted=[r['label'] for r in joined.values() if r['kind']==A]
    require(len(selected)==22 and len(labels)==4223 and len(trusted)==100,'registered populations')
    require(result['verified_labels']==labels+selected and result['trusted_assertions']==trusted,'complete ordered native coverage')
    require(identity(trusted)['sha256']==authority['trusted_assertions_sha256'],'exact trust digest')
    require(result['selected']==selected and set(result['traces'])==set(selected),'complete cohort traces')
    require(result['claims_sha256']==identity(claims)['sha256'] and result['sources']==sources,'issued request/source identities')
    require(result['closed_prefix']=={'path':str(prefix_path),**raw_identity(base_raw)} and authority['prefix']==raw_identity(base_raw),'exact base')
    require(joined_raw==base_raw+b'\n'+suffix and (archive/'database.mm').read_bytes()==joined_raw,'exact checked joined bytes')
    require(result['database']=={'path':str(archive/'database.mm'),**raw_identity(joined_raw)} and result['suffix']==raw_identity(suffix),'database/suffix receipt')
    require((archive/'suffix.mm').read_bytes()==suffix and raw_identity((archive/'native.log').read_bytes())==result['log'],'suffix and log custody')
    require((archive/'result.json').read_bytes()==N.encoded(result)+b'\n','returned/stored receipt')
    require((archive/'request.json').read_bytes()==N.encoded({'claims':claims,'sources':sources,'authority':authority})+b'\n','stored native request')
    expected_used={}
    for claim in claims:
        source=joined[claim['label']];trace=result['traces'][claim['label']]
        contract={'label':claim['label'],'kind':P,'statement':claim['query'],'dv':[],
            'floating':[{'label':p['floating_label'],'statement':[p['type'],p['variable']]} for p in claim['parameters']],
            'essential':[{'label':h,'statement':s} for h,s in zip(claim['holes'],claim['premises'])]}
        require(S.contract(source)==contract and source['proof']==claim['proof'] and source['active_dv']==[],'exact current claim/frame')
        require(trace['source']==source and trace['label']==claim['label'] and trace['terminal']=='NATIVE_VERIFIED'
                and trace['external_logical_hypotheses']==contract['essential'],'exact current trace')
        require(type(trace['nodes']) is list and 1<=len(trace['nodes'])<=256,'unchanged trace-node scope')
        for k in {n['label'] for n in trace['nodes'] if 'label' in n}:
            row=joined[k];require(row['span'][1]<=source['span'][0],'used source precedes claim')
            if row['kind'] in {F,E}:
                require({'label':k,'statement':row['statement']} in contract['floating' if row['kind']==F else 'essential'],'scoped hypothesis')
            else:require(k in base and row['kind'] in {A,P} and row['dv']==[],'ordinary base/DV scope')
            expected_used[k]={**S.contract(row),'span':row['span']}
    require(result['contracts']==expected_used,'complete union of current USED contracts')
    bp=[proof_record(r) for r in base.values() if r['kind']==P];jp=[proof_record(r) for r in joined.values() if r['kind']==P]
    require([r['label'] for r in jp]==labels+selected,'indexed joined proof order')
    manifest={'schema':'ordinary.joined-library.v1','base_prefix':raw_identity(base_raw),'joined_prefix':raw_identity(joined_raw),
        'base_proofs':bp,'joined_proofs':jp,'cohort':jp[len(bp):],
        'axioms':[{'label':r['label'],'raw':r['raw'],'contract':identity(S.contract(r))} for r in base.values() if r['kind']==A],
        'receipt':raw_identity((archive/'result.json').read_bytes())}
    library=Library(base_raw,joined_raw,manifest,identity(manifest),(archive/'result.json').read_bytes(),manifest['receipt'])
    return manifest,library.costs
