"""Actual repair-only successor plus rehashed scope, closure and custody attacks."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('checked_snapshot_v21',HERE/'check_snapshot_v21.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
COVERAGE={}


def replace(value,path,replacement):
    for component in path[:-1]:value=value[component]
    value[path[-1]]=replacement


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot=json.loads((HERE/'SCOPE_SNAPSHOT_V21.json').read_text())
        cls.receipt=json.loads((checker.ROOT/checker.CONTRACT.PACKAGE/'RESULT_V21.json').read_text())
        cls.gate=checker.load('test_gate',checker.ROOT/'research/gmi-1068-recursive-audit-v3/gate.py')

    def rebind(self,snapshot):
        for name in self.gate.NODES:
            row=snapshot['rounds'][name]
            row['parent_bindings']={p:snapshot['rounds'][p]['evidence_digest'] for p in self.gate.DAG[name]}
            row['evidence_digest']=self.gate.evidence_digest(row)
        return snapshot

    def check(self,snapshot,receipt):
        accounting=checker.CONTRACT.current_accounting(snapshot,self.receipt['amendment_carry'])
        return checker.evaluate(snapshot,receipt,accounting)

    def test_actual_snapshot_no_alarm(self):
        result=checker.evaluate()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['new_scientific_atoms_closed'],sorted(checker.CONTRACT.ATOM_SPECS))
        self.assertEqual(len(result['scientific_atoms_closed']),19)
        self.assertEqual((result['original_fulfilled'],result['remaining_atoms'],
                          result['qualified_replacements'],result['active_unresolved']),(27,195,2,193))
        self.assertEqual(result['earned_rounds'],['R0'])
        COVERAGE['valid_snapshots']=1

    def test_rehashed_snapshot_mutations(self):
        repair=lambda owner,field:('rounds',owner,'local_repairs',-1,field)
        atom=lambda owner,index,field:('rounds',owner,'obligations',index,field)
        wrong=checker.CONTRACT.witness(checker.ROOT,'WeightedExecutionV21.lean','lean_declaration','weighted_empty')
        changes=[(repair('R14','scope'),'all theories are complete'),(repair('R15','status'),'PENDING_REVIEW'),
            (repair('R3','id'),'unregistered-repair'),(repair('R3','evidence'),[wrong]),
            (atom('R1',0,'status'),'CLOSED'),(atom('R1',5,'status'),'CLOSED'),
            (atom('R1',6,'status'),'CLOSED'),(atom('R1',0,'title'),'different original requirement'),
            (atom('R1',0,'disposition'),'absolute minimality proved'),(atom('R1',0,'evidence'),[wrong]),
            (atom('R1',0,'historical_status'),'CLOSED'),(atom('R1',0,'id'),'GMI2-R1-099'),
            (atom('R1',1,'status'),'UNKNOWN'),(atom('R2',7,'status'),'UNKNOWN'),
            (atom('R3',0,'disposition'),'unrelated edited scope'),
            (atom('R3',3,'status'),'UNKNOWN'),(atom('R3',3,'title'),'all frontiers exist'),
            (atom('R3',3,'disposition'),'infinite frontiers are always finite'),
            (atom('R3',3,'evidence'),[wrong]),(atom('R3',6,'status'),'CLOSED'),
            (('rounds','R1','scope'),'unregistered scope'),(('rounds','R1','status'),'STALE'),
            (('rounds','R1','local_repairs',0,'scope'),'rewritten history')]
        for index in (0,1,2,4,5,9):
            for field,value in (('status','UNKNOWN'),('title','retargeted obligation'),
                                ('disposition','unrestricted infinite semantics'),('evidence',[wrong])):
                changes.append((atom('R3',index,field),value))
        for index in (7,8):changes.append((atom('R3',index,'status'),'CLOSED'))
        invalid=[]
        for path,value in changes:
            bad=deepcopy(self.snapshot);replace(bad,path,value);invalid.append(bad)
        bad=deepcopy(self.snapshot);bad['rounds']['R1']['obligations'][0]['unsupported_authority']=True;invalid.append(bad)
        bad=deepcopy(self.snapshot);bad['rounds']['R3']['local_repairs'].append(deepcopy(bad['rounds']['R3']['local_repairs'][-1]));invalid.append(bad)
        bad=deepcopy(self.snapshot);bad['rounds']['R3']['artifacts']=[a for a in bad['rounds']['R3']['artifacts']
            if a['path']!=checker.CONTRACT.PACKAGE+'/FREEZE_V21.md'];invalid.append(bad)
        bad=deepcopy(self.snapshot);path=HERE/'audit_contract_v21.py'
        bad['rounds']['R3']['artifacts'].append({'path':str(path.relative_to(checker.ROOT)),
                                               'sha256':checker.CONTRACT.digest(path)});invalid.append(bad)
        for bad in invalid:
            with self.assertRaises(ValueError):self.check(self.rebind(bad),self.receipt)
        self.assertEqual(len(invalid),53)
        COVERAGE['snapshot_mutation_rejections']=len(invalid)

    def test_receipt_mutations(self):
        source=next(iter(self.receipt['kernel']['sources']))
        local=next(iter(self.receipt['inputs']));historical=next(iter(self.receipt['source_bindings']))
        changes=[(('atoms',),{'GMI2-R1-001':{'status':'VERIFIED_AT_REGISTERED_SCOPE'}}),
            (('registered_results','U1','scope'),'all resources admit subtraction'),
            (('registered_results','U2','status'),'PENDING_REVIEW'),
            (('kernel','status'),'FAIL'),(('kernel','lean_version'),'4.18.0'),
            (('kernel','proof_entry_count'),True),(('kernel','proof_entry_count'),float(checker.CONTRACT.PROOF_COUNT)),
            (('kernel','audit_sha256'),'0'*64),(('kernel','sources',source),'0'*64),
            (('kernel','source_assumptions'),'no premises'),(('inputs',local),'0'*64),
            (('coverage','test_execution_v21','a_machines'),True),
            (('coverage','test_execution_v21','a_machines'),1542.0),
            (('source_bindings',historical),'0'*64),(('source_bindings',),{}),
            (('inherited_receipts',),{}),(('amendment_carry','qualified_revision_ids'),[]),
            (('amendment_carry','ledger_sha256'),'0'*64),(('amendment_carry','scope'),'originals fulfilled'),
            (('tests_run',),True),(('tests_run',),13.0),(('tests_run',),12),
            (('overall_closure',),'CLOSED'),(('scientific_truth_certified',),0),
            (('claim_boundaries',),[]),(('kernel',),[]),(('registered_results',),{})]
        for atom_id in checker.CONTRACT.ATOM_SPECS:
            for field,value in (('title','retargeted obligation'),('scope','unrestricted infinite semantics'),
                                ('status','PENDING_REVIEW')):
                changes.append((('atoms',atom_id,field),value))
        invalid=[]
        for path,value in changes:
            bad=deepcopy(self.receipt);replace(bad,path,value);invalid.append(bad)
        for key in self.receipt:
            bad=deepcopy(self.receipt);del bad[key];invalid.append(bad)
        for path in ((),('kernel',),('source_bindings',),('coverage','test_execution_v21'),('inputs',),('registered_results',)):
            bad=deepcopy(self.receipt);cursor=bad
            for key in path:cursor=cursor[key]
            cursor['unexpected']='unexpected';invalid.append(bad)
        for index in range(len(self.receipt['claim_boundaries'])):
            bad=deepcopy(self.receipt);bad['claim_boundaries'][index]='unregistered promotion';invalid.append(bad)
        bad=deepcopy(self.receipt);bad['claim_boundaries']=tuple(bad['claim_boundaries']);invalid.append(bad)
        bad=deepcopy(self.receipt);bad['coverage'][0]={};invalid.append(bad)
        for bad in invalid:
            with self.assertRaises(ValueError):self.check(self.snapshot,bad)
        self.assertEqual(len(invalid),78)
        COVERAGE['receipt_mutation_rejections']=len(invalid)

    def test_coupled_result_scope_and_original_promotion(self):
        count=0
        for result in checker.CONTRACT.RESULTS:
            snapshot,receipt=deepcopy(self.snapshot),deepcopy(self.receipt)
            claim='All ordered resources have unique residuals and least scalar costs.'
            snapshot['rounds']['R4']['local_repairs'][-1]['scope']=claim
            receipt['registered_results'][result]['scope']=claim
            with self.assertRaisesRegex(ValueError,'registered result adjudication drift'):
                self.check(self.rebind(snapshot),receipt)
            count+=1
        snapshot,receipt=deepcopy(self.snapshot),deepcopy(self.receipt)
        atom=snapshot['rounds']['R1']['obligations'][0];atom['status']='CLOSED'
        receipt['atoms'][atom['id']]={'status':'VERIFIED_AT_REGISTERED_SCOPE','scope':'minimum proved'}
        with self.assertRaisesRegex(ValueError,'registered atom adjudication drift'):
            self.check(self.rebind(snapshot),receipt)
        count+=1
        for atom_id in checker.CONTRACT.ATOM_SPECS:
            snapshot,receipt=deepcopy(self.snapshot),deepcopy(self.receipt)
            atom=next(row for row in snapshot['rounds']['R3']['obligations'] if row['id']==atom_id)
            atom['disposition']='Unconditional infinite resource theory is complete.'
            receipt['atoms'][atom_id]['scope']=atom['disposition']
            with self.assertRaisesRegex(ValueError,'registered atom adjudication drift'):
                self.check(self.rebind(snapshot),receipt)
            count+=1
        COVERAGE['coupled_scope_rejections']=count
        self.assertEqual(count,11)

    def test_current_accounting_mutations(self):
        baseline=checker.CONTRACT.current_accounting(self.snapshot,self.receipt['amendment_carry'])
        invalid=[]
        for key in baseline:
            bad=deepcopy(baseline);del bad[key];invalid.append(bad)
        for path,value in [(('original_fulfilled',),28),(('original_unresolved',),194),
                (('active_unresolved',),192),(('qualified_replacements',),3),(('original_total',),222.0),
                (('original_fulfilled',),True),(('qualified_original_ids',),[]),
                (('snapshot_content_sha256',),'0'*64),(('amendment_carry','ledger_sha256'),'0'*64),
                (('scientific_truth_certified',),0),(('overall_closure',),'CLOSED')]:
            bad=deepcopy(baseline);replace(bad,path,value);invalid.append(bad)
        invalid.append(json.loads((checker.BASE.parent/'CURRENT_ACCOUNTING_V20.json').read_text()))
        bad=deepcopy(baseline);bad['unsupported']=True;invalid.append(bad)
        for bad in invalid:
            with self.assertRaises(ValueError):checker.evaluate(self.snapshot,self.receipt,bad)
        self.assertEqual(len(invalid),24)
        COVERAGE['accounting_mutation_rejections']=len(invalid)


if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
