"""Independent exported identity/order checks, not native proof interpretation."""
from read_data import *
def check(q,result):
    a=load(OUT/'NATIVE-AUTHORITY.json'); p1=load(OUT/'P1-INVENTORY.json'); packet=load(OUT/'TEACHING-PACKET-CANDIDATE.json')
    rel=load(q['release']['path']); ac=load(q['authority_contract']['path']); p0=load(OUT/'P0-CONTRACTS.json')
    raw=read(q['prefix']['path']); records,order=lexical_records(raw)
    proofs=[x for x in order if records[x]['kind']=='$p']; axioms=[x for x in order if records[x]['kind']=='$a']
    equal('source-proof-count',len(proofs),4223); equal('source-axiom-count',len(axioms),100)
    equal('complete-authority-proof-order',a['verified_labels'],proofs)
    equal('native-log-two-complete-orders',read(OBS/'stderr.log').decode().splitlines(),['Verify: '+x for x in proofs]*2)
    progress=[parse(line) for line in read(OUT/'CUSTODIAN-PROGRESS.jsonl').splitlines()]
    equal('progress-lines',len(progress),4351)
    equal('fresh-pass-progress',progress[:4223],[{'label':x,'stage':'native_prefix','status':'FRESH_NATIVE_VERIFIED'} for x in proofs])
    released=proofs[4095:]; equal('observer-progress',progress[4223:],[{'label':x,'stage':'trace_observer','status':'TRACE_READY'} for x in released])
    equal('authority-status',a['terminal'],'FRESH_PREFIX_NATIVE_VERIFIED'); equal('authority-proof-count',a['proof_ordinal_count'],4223)
    equal('authority-old-receipt',a['old_native_receipt_inherited'],False)
    equal('authority-new-contract-policy',ac['base_policy'],'ALL_PREFIX_AXIOMS')
    equal('authority-new-contract-count',ac['proof_ordinal_count'],4223)
    for k in ['release','prefix','registry_scope','corpus','python','verifier']:
        equal('authority-input-'+k,a[k],q[k]); equal('new-contract-input-'+k,ac[k],q[k])
    equal('authority-contract',a['authority_contract'],q['authority_contract']); equal('authority-source-map',a['sources'],q['sources'])
    equal('authority-P0',a['P0_contracts'],q['P0_contracts'])
    require('release-corpus-inherited-only',rel['corpus']==q['corpus'])
    equal('release-closed-prefix',rel['closed_source'],identity(raw))
    equal('release-boundary',raw[rel['source_end_exclusive']:],b'\n')
    equal('release-no-synthetic-closures',rel['synthetic_scope_closures'],0)
    axids=[{'label':x,'raw':records[x]['raw']} for x in axioms]
    equal('new-contract-source-axioms',ac['axiom_identities'],axids)
    equal('release-source-axioms',rel['axiom_identities'],axids)
    equal('authority-source-axioms',[{'label':x['contract']['label'],'raw':x['raw']} for x in a['axioms']],axids)
    c=p1['contracts']; require('P1-unique',len({x['label'] for x in c})==len(c)); by={x['label']:x for x in c}
    equal('P1-count',len(c),4323); equal('P0-count',len(p0),4191)
    equal('P1-source-order',[x['label'] for x in c],[x for x in order if records[x]['kind'] in ('$a','$p')])
    keys={'label','kind','statement','floating','essential','dv'}
    for row in c:
        equal('P1-exact-fields',set(row),keys)
        for key in ['label','kind','statement']: equal('P1-lexical-'+key,row[key],records[row['label']][key])
    for row in p0: equal('P0-retained-'+row['label'],by[row['label']],row)
    for row in a['axioms']: equal('axiom-contract-P1-'+row['contract']['label'],by[row['contract']['label']],row['contract'])
    oldax={x['label'] for x in p0 if x['kind']=='$a'}; equal('P0-axiom-count',len(oldax),96)
    extra=[x for x in axioms if x not in oldax]; equal('new-axiom-labels',a['additional_axiom_labels'],extra)
    equal('new-axiom-exact-set',set(extra),{'csymdif','df-symdif','c0','df-nul'})
    equal('P1-released-order',p1['released_labels'],released)
    equal('P1-base-order',p1['base_labels'],[x['label'] for x in c if x['label'] not in set(released)])
    equal('P1-base-count',len(p1['base_labels']),4195)
    equal('P1-policy',p1['inventory_policy'],'ALL_PREFIX_AXIOMS_PLUS_P0_THEOREMS_PLUS_RELEASED_TRAINING_THEOREMS')
    equal('P1-authority-chain',p1['native_trace_authority'],result['artifacts']['native_authority'])
    equal('packet-authority-chain',packet['native_trace_authority'],result['artifacts']['native_authority'])
    equal('packet-P1-chain',packet['P1_inventory'],result['artifacts']['P1_inventory'])
    for x in [p1,packet]: equal('release-chain',x['release'],q['release'])
    equal('packet-ordinals',packet['ordinals'],list(range(4096,4224)))
    equal('release-ordinals',rel['ordinals'],packet['ordinals'])
    equal('released-label-order',[x['label'] for x in rel['roots']],released)
    equal('packet-label-order',[x['label'] for x in packet['roots']],released)
    return a,p1,packet,rel,records,extra
