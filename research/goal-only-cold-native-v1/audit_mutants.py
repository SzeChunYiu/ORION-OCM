"""Mutate copies of an authored observation, never an experiment or original evidence."""
import argparse
from pathlib import Path
import shutil
import tempfile
from custody import Refusal, encoded, identity, parse, store
from qualify import audit

def write(path, value):path.write_bytes(encoded(value)+b'\n')

def row(root, name, change):
    path=root/name/'observation.json';record=parse(path.read_bytes());change(record);write(path,record)
    receipt=root/(name+'.launch.json');r=parse(receipt.read_bytes())
    from custody import raw_id
    r['observation']=raw_id(path.read_bytes());write(receipt,r)

def changed_solver(record, key, value):
    record['solver'][key]=value
    record['native']['generated_result']=identity(record['solver'])

def check(source, output):
    baseline=audit(source)
    cases=[]
    def case(name, reason, change):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'copy'
            # Runtime files are not needed for a read-only audit of completed records.
            shutil.copytree(source,target,ignore=shutil.ignore_patterns('runtime'))
            change(target)
            try:audit(target)
            except Refusal as exc:
                if reason not in str(exc):raise AssertionError((name,reason,str(exc))) from exc
                cases.append({'name':name,'rejected':True,'reason':str(exc)})
            else:raise AssertionError('mutant accepted: '+name)
    case('empty-plan','COMPLETE_ORDERED',lambda r:write(r/'RUN.json',{'plan':[]}))
    case('extra-launch','LAUNCH_FILE_POPULATION',lambda r:(r/'hidden-failure.launch.json').write_text('{}'))
    case('truncated-prefix','COMPLETE_NATIVE_PREFIX',lambda r:row(r,'ordinary-enabled',lambda o:o['native']['native_result']['verified_labels'].pop()))
    case('altered-trust','TRUST_INVENTORY',lambda r:row(r,'ordinary-enabled',lambda o:o['native']['native_result']['trusted_assertions'].pop()))
    case('saved-success-without-native-call','FRESH_NATIVE_CHECK',lambda r:row(r,'ordinary-enabled',lambda o:o.update(native_calls=0)))
    case('disabled-use-forgery','NATIVE_CAUSAL_USE',lambda r:row(r,'ordinary-resident-disabled',lambda o:o['native']['selected_cohort_labels'].append('learned-cut')))
    case('missing-answer-dependency','ANSWER_SUPPORT',lambda r:row(r,'ocm-enabled',lambda o:o['ocm']['answer_support'].pop()))
    def erase_method(root):
        binding=parse((root/'producer/state-binding.json').read_bytes())
        row(root,'ocm-enabled',lambda o:o['ocm']['trace']['stages'][-1]['evidence_ids'].remove(repr(binding['method'])))
    case('missing-commitment-dependency','COMMITMENT_SUPPORT',erase_method)
    case('different-ordinary-answer','ORDINARY_OCM_PARITY',lambda r:row(r,'ordinary-enabled',lambda o:changed_solver(o,'decision_count',7)))
    def alter_bank(root):
        for route in ('ordinary','ocm'):
            row(root,route+'-resident-disabled',lambda o:changed_solver(o,'bank_identity',{'bytes':0,'sha256':'0'*64}))
    case('symmetric-term-hint-manipulation','CHANGED_TERM_HINTS',alter_bank)
    case('native-log-tampering','CONTENT_PIN',lambda r:(r/'ordinary-enabled/native/native.log').write_bytes(b'FORGED'))
    case('broken-lease-chain','BROKEN_REVISION_CHAIN',lambda r:row(r,'revoke',lambda o:o['ocm']['lease'].update(head='forged')))
    result={'schema':'ordinary.cold-native.audit-mutations.v1','baseline':baseline['terminal'],
            'tests_run':len(cases),'all_rejected':all(x['rejected'] for x in cases),'cases':cases,
            'scope':'Self-authored mutation tests; not independent review or attack-resistant remote attestation.'}
    store(output,encoded(result)+b'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    print(encoded(check(a.source,a.out)).decode())
