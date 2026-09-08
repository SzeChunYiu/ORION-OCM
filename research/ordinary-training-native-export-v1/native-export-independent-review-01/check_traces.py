"""Retained trace binding/interface audit; no replay or cut/alias computation."""
from collections import Counter
from read_data import *
def check(a,p1,packet,rel,records,result):
    unusable=load(OUT/'CUSTODIAN-UNUSABLE-TRACES.json'); contracts={x['label']:x for x in p1['contracts']}
    ready=[]; refused=[]; reasons=Counter(); used_checks=0
    equal('scope-binding-population',set(a['selected_scope_bindings']),{x['label'] for x in packet['roots']})
    equal('disposition-population',set(a['trace_dispositions']),set(a['selected_scope_bindings']))
    for rr,row in zip(rel['roots'],packet['roots']):
        label=row['label']; source=records[label]; scope=a['selected_scope_bindings'][label]; disp=a['trace_dispositions'][label]
        equal('root-ordinal-'+label,row['ordinal'],rr['ordinal'])
        equal('released-status-'+label,row['source_disposition'],'RELEASED'); equal('release-status-'+label,rr['source_disposition'],'RELEASED')
        equal('no-forbidden-dependencies-'+label,rr['forbidden_dependencies'],[])
        equal('root-status-'+label,row['trace_disposition'],disp['status'])
        for key in ['source_raw','proof_raw']:
            expected=source['raw' if key=='source_raw' else key]
            equal('release-raw-'+label+key,rr[key],expected); equal('scope-raw-'+label+key,scope[key],expected)
        equal('release-statement-'+label,rr['statement'],source['statement'])
        canon_bound('whole-contract-'+label,contracts[label],row['whole_contract'])
        equal('scope-whole-contract-'+label,scope['contract'],row['whole_contract'])
        if row['trace_disposition']=='TRACE_READY':
            ready.append(label); trace=row['trace']; used=row['contracts']
            equal('ready-no-reason-'+label,disp['reason'],None)
            canon_bound('trace-hash-'+label,trace,a['trace_bindings'][label]['trace'])
            canon_bound('used-contracts-hash-'+label,used,a['trace_bindings'][label]['contracts'])
            require('ready-node-limit-'+label,1<=len(trace['nodes'])<=256)
            require('ready-no-source-DV-'+label,trace['source']['dv']==[] and trace['source']['active_dv']==[])
            usedlabels={n['label'] for n in trace['nodes'] if n.get('label')}
            equal('exact-used-contract-labels-'+label,set(used),usedlabels)
            mandatory={h['label']:h for h in trace['source']['floating']+trace['source']['essential']}
            for k,c in used.items():
                used_checks+=1; sr=records[k]
                equal('used-span-'+label+'/'+k,c['span'],sr['span'])
                require('used-before-target-'+label+'/'+k,c['span'][0]<source['span'][0])
                if c['kind'] in ('$a','$p'):
                    equal('used-P1-contract-'+label+'/'+k,{x:v for x,v in c.items() if x!='span'},contracts[k])
                    equal('used-no-DV-'+label+'/'+k,c['dv'],[])
                else:
                    require('used-hypothesis-kind-'+label+'/'+k,c['kind'] in ('$f','$e'))
                    equal('used-mandatory-hypothesis-'+label+'/'+k,{'label':k,'statement':c['statement']},mandatory[k])
                    for fld in ['kind','label','statement']: equal('used-hypothesis-source-'+fld,c[fld],sr[fld])
        else:
            refused.append(label); equal('unusable-status-'+label,row['trace_disposition'],'TRACE_UNUSABLE')
            equal('unusable-no-packet-trace-'+label,row['trace'],None); equal('unusable-no-packet-contracts-'+label,row['contracts'],{})
            trace=unusable[label]['trace']; equal('unusable-reason-'+label,unusable[label]['reason'],disp['reason']); reasons[disp['reason']]+=1
        # All 128 retained native traces are bound to exact source slices and issued theorem statements.
        equal('trace-terminal-'+label,trace['terminal'],'NATIVE_VERIFIED'); equal('trace-label-'+label,trace['label'],label)
        for k,v in source.items(): equal('trace-source-'+label+'/'+k,trace['source'][k],v)
        for fld in ['active_variables','active_dv']: equal('native-scope-'+label+'/'+fld,trace['source'][fld],scope[fld])
        equal('trace-source-contract-'+label,{k:trace['source'][k] for k in contracts[label]},contracts[label])
        root=trace['root']; require('trace-root-index-'+label,type(root) is int and 0<=root<len(trace['nodes']))
        equal('trace-root-target-'+label,trace['nodes'][root]['output'],source['statement'])
    equal('ready-count',len(ready),71); equal('unusable-count',len(refused),57)
    equal('unusable-exact-population',set(refused),set(unusable)); equal('ready-authority-population',set(ready),set(a['trace_bindings']))
    equal('ready-process-order',result['trace_ready_labels'],ready)
    equal('root-process-summary',result['roots'],[{k:x[k] for k in ['label','ordinal','source_disposition','trace_disposition']} for x in packet['roots']])
    equal('unusable-reason-counts',dict(reasons),{'OUTSIDE_NO_DV_INTERFACE':53,'OUTSIDE_USED_CONTRACT_NO_DV_INTERFACE':3,'OUTSIDE_MANDATORY_HYPOTHESIS_INTERFACE':1})
    equal('partial-transport-status',a['trace_stage'],'PARTIAL_OR_UNUSABLE')
    return {'ready':len(ready),'unusable':len(refused),'reasons':dict(reasons),'used_contract_bindings_checked':used_checks}
