"""Receipt mutations include every cost-record slot without trusted recomputation."""
from copy import deepcopy


def mutations(receipt):
    invalid=[]
    def change(path,value):
        bad=deepcopy(receipt);cursor=bad
        for key in path[:-1]:cursor=cursor[key]
        cursor[path[-1]]=value;invalid.append(bad)
    source=next(iter(receipt['kernel']['sources']))
    local=next(iter(receipt['inputs']));historical=next(iter(receipt['source_bindings']))
    for path,value in [(('round_adjudication',),{}),(('round_adjudication','R1','status'),'PENDING_REVIEW'),
        (('kernel','status'),'FAIL'),(('kernel','lean_version'),'4.18.0'),(('kernel','proof_entry_count'),True),
        (('kernel','proof_entry_count'),float(receipt['kernel']['proof_entry_count'])),
        (('kernel','audit_sha256'),'0'*64),(('kernel','sources',source),'0'*64),
        (('kernel','source_assumptions'),'no premises'),(('inputs',local),'0'*64),
        (('source_bindings',historical),'0'*64),(('inherited_receipts',),{}),
        (('amendment_carry','qualified_revision_ids'),[]),(('amendment_carry','ledger_sha256'),'0'*64),
        (('tests_run',),True),(('tests_run',),float(receipt['tests_run'])),(('tests_run',),14),
        (('overall_closure',),'CLOSED'),(('scientific_truth_certified',),0),
        (('claim_boundaries',),[]),(('registered_results',),{}),(('rollup_reconciliation',),{})]:change(path,value)
    for key,value in receipt['source_costs'].items():
        change(('source_costs',key),value+1);change(('source_costs',key),float(value))
    for key,value in receipt['rollup_reconciliation'].items():
        change(('rollup_reconciliation',key),[] if isinstance(value,list) else True)
    for i,model in enumerate(receipt['codec_costs']['named']['models']):
        for key,value in model.items():change(('codec_costs','named','models',i,key),[] if isinstance(value,list) else True)
    reports=receipt['codec_costs']['information']['family_reports']
    for i,report in enumerate(reports):
        change(('codec_costs','information','family_reports',i,'recovery_sizes','source',0),0)
    for key,value in reports[0].items():
        change(('codec_costs','information','family_reports',0,key),{} if isinstance(value,dict) else None)
    change(('codec_costs','information','family_reports'),reports[:-1])
    change(('codec_costs','named','models'),receipt['codec_costs']['named']['models'][:1])
    for module,values in receipt['coverage'].items():
        key=next(iter(values));change(('coverage',module,key),True)
    for key in receipt:
        bad=deepcopy(receipt);del bad[key];invalid.append(bad)
    for path in ((),('kernel',),('source_bindings',),('inputs',),('registered_results',),('codec_costs',),('source_costs',)):
        bad=deepcopy(receipt);cursor=bad
        for key in path:cursor=cursor[key]
        cursor['unexpected']=True;invalid.append(bad)
    bad=deepcopy(receipt);bad['atoms']={};invalid.append(bad)
    for index in range(len(receipt['claim_boundaries'])):change(('claim_boundaries',index),'unregistered promotion')
    change(('claim_boundaries',),tuple(receipt['claim_boundaries']))
    return invalid
