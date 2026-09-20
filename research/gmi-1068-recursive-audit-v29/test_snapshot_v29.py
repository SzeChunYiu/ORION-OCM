"""Actual R1-only re-earning, original-record preservation and coupled cost attacks."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('checked_snapshot_v29',HERE/'check_snapshot_v29.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
COVERAGE={}


def replace(value,path,replacement):
    for part in path[:-1]:value=value[part]
    value[path[-1]]=replacement


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot=json.loads((HERE/'SCOPE_SNAPSHOT_V29.json').read_text())
        cls.receipt=json.loads((checker.ROOT/checker.CONTRACT.PACKAGE/'RESULT_V29.json').read_text())
        cls.gate=checker.load('test_gate',checker.ROOT/'research/gmi-1068-recursive-audit-v3/gate.py')

    def rebind(self,snapshot):
        for name in self.gate.NODES:
            row=snapshot['rounds'][name]
            row['parent_bindings']={p:snapshot['rounds'][p]['evidence_digest'] for p in self.gate.DAG[name]}
            row['evidence_digest']=self.gate.evidence_digest(row)
        return snapshot

    def check(self,snapshot,receipt):
        accounting=checker.CONTRACT.current_accounting(snapshot if 'rounds' in snapshot else self.snapshot,
                                                      self.receipt['amendment_carry'])
        return checker.evaluate(snapshot,receipt,accounting)

    def test_actual_snapshot_no_alarm(self):
        result=checker.evaluate()
        self.assertEqual(result['status'],'PASS');self.assertEqual(result['new_scientific_atoms_closed'],[])
        self.assertEqual(len(result['scientific_atoms_closed']),27)
        self.assertEqual((result['original_fulfilled'],result['remaining_atoms'],
                          result['qualified_replacements'],result['active_unresolved']),(35,187,2,185))
        self.assertEqual(result['earned_rounds'],['R0','R1'])
        before=json.loads(checker.BASE.read_text())
        for name in self.gate.NODES:
            self.assertEqual(self.snapshot['rounds'][name]['obligations'],before['rounds'][name]['obligations'])
        COVERAGE['valid_snapshots']=1

    def test_rehashed_snapshot_mutations(self):
        changes=[(('source_issue',),1068.0),(('source_issue',),True),(('observed_main',),'0'*40),
                 (('audited_base',),'0'*40),(('rounds','R1','status'),'OPEN')]
        for name,row in self.snapshot['rounds'].items():
            changes.extend([(('rounds',name,'scope'),'unregistered scope'),
                            (('rounds',name,'historical_reconciliation_status'),'rewritten history')])
            for index,atom in enumerate(row['obligations']):
                changes.append((('rounds',name,'obligations',index,'status'),
                                'UNKNOWN' if atom['status']=='CLOSED' else 'CLOSED'))
        for index in range(10):
            for field,value in (('title','new target'),('disposition','absolute minimality'),
                                ('evidence',[]),('historical_status','rewritten'),('id','GMI2-R1-099')):
                changes.append((('rounds','R1','obligations',index,field),value))
        for name in ('R0','R2','R3','R14','R15'):
            changes.append((('rounds',name,'status'),'OPEN' if name=='R0' else 'EARNED'))
        for name in checker.CONTRACT.REPAIR_SCOPES:
            for field,value in (('scope','unrestricted theory'),('status','PENDING_REVIEW'),
                                ('id','unregistered-repair'),('evidence',[])):
                changes.append((('rounds',name,'local_repairs',-1,field),value))
        invalid=[]
        for path,value in changes:
            bad=deepcopy(self.snapshot);replace(bad,path,value);invalid.append(bad)
        for name in self.gate.NODES:
            bad=deepcopy(self.snapshot);bad['rounds'][name]['extra']=True;invalid.append(bad)
        for key in self.snapshot:
            bad=deepcopy(self.snapshot);del bad[key];invalid.append(bad)
        bad=deepcopy(self.snapshot);bad['unsupported_top_level']=True;invalid.append(bad)
        bad=deepcopy(self.snapshot);bad['rounds']['R1']['obligations'][0]['extra']=True;invalid.append(bad)
        bad=deepcopy(self.snapshot);bad['rounds']['R1']['local_repairs'].pop();invalid.append(bad)
        bad=deepcopy(self.snapshot);bad['rounds']['R1']['artifacts'].pop();invalid.append(bad)
        for bad in invalid:
            with self.assertRaises(ValueError):self.check(self.rebind(bad) if 'rounds' in bad else bad,self.receipt)
        COVERAGE['snapshot_mutation_rejections']=len(invalid)

    def test_receipt_and_cost_mutations(self):
        helper=checker.load('receipt_mutations_v29',HERE/'receipt_mutations_v29.py')
        invalid=helper.mutations(self.receipt)
        for bad in invalid:
            with self.assertRaises(ValueError):self.check(self.snapshot,bad)
        COVERAGE['receipt_mutation_rejections']=len(invalid)

    def test_coupled_round_scope_costs_and_original_promotion(self):
        count=0
        for result in checker.CONTRACT.RESULTS:
            snapshot,receipt=deepcopy(self.snapshot),deepcopy(self.receipt)
            claim='All process ontologies have one absolute minimum.'
            snapshot['rounds']['R1']['local_repairs'][-1]['scope']=claim
            receipt['registered_results'][result]['scope']=claim
            with self.assertRaisesRegex(ValueError,'registered result adjudication drift'):
                self.check(self.rebind(snapshot),receipt)
            count+=1
        snapshot,receipt=deepcopy(self.snapshot),deepcopy(self.receipt)
        snapshot['rounds']['R1']['scope']='unregistered absolute theory'
        receipt['round_adjudication']['R1']['scope']=snapshot['rounds']['R1']['scope']
        with self.assertRaisesRegex(ValueError,'registered round adjudication drift'):self.check(self.rebind(snapshot),receipt)
        count+=1
        for owner,index in (('R2',2),('R2',6),('R4',0)):
            snapshot,receipt=deepcopy(self.snapshot),deepcopy(self.receipt)
            snapshot['rounds'][owner]['obligations'][index]['status']='CLOSED'
            receipt['round_adjudication'][owner]={'status':'VERIFIED_AT_REGISTERED_SCOPE','scope':'all complete'}
            diagnostic='qualified original promoted' if owner=='R2' else 'registered round adjudication drift'
            with self.assertRaisesRegex(ValueError,diagnostic):self.check(self.rebind(snapshot),receipt)
            count+=1
        for kind in ('codec_costs','source_costs'):
            snapshot,receipt=deepcopy(self.snapshot),deepcopy(self.receipt)
            receipt[kind]={};snapshot['rounds']['R15']['local_repairs'][-1]['scope']='zero-cost representation'
            with self.assertRaisesRegex(ValueError,'registered .* costs drift'):self.check(self.rebind(snapshot),receipt)
            count+=1
        helper=checker.load('snapshot_controls_v29',HERE/'snapshot_controls_v29.py')
        with helper.formal_source_attack(checker.ROOT,self.receipt,checker.CONTRACT) as (root,bad):
            with self.assertRaisesRegex(ValueError,'reviewed formal source drift'):
                checker.CONTRACT.validate_receipt(root,bad)
        count+=1
        COVERAGE['coupled_scope_rejections']=count

    def test_current_accounting_mutations(self):
        baseline=checker.CONTRACT.current_accounting(self.snapshot,self.receipt['amendment_carry']);invalid=[]
        for key in baseline:
            bad=deepcopy(baseline);del bad[key];invalid.append(bad)
        for path,value in [(('original_fulfilled',),36),(('original_unresolved',),186),
                (('active_unresolved',),184),(('qualified_replacements',),3),(('original_total',),222.0),
                (('original_fulfilled',),True),(('qualified_original_ids',),[]),
                (('snapshot_content_sha256',),'0'*64),(('amendment_carry','ledger_sha256'),'0'*64),
                (('scientific_truth_certified',),0),(('overall_closure',),'CLOSED')]:
            bad=deepcopy(baseline);replace(bad,path,value);invalid.append(bad)
        invalid.append(json.loads((checker.BASE.parent/'CURRENT_ACCOUNTING_V28.json').read_text()))
        bad=deepcopy(baseline);bad['unsupported']=True;invalid.append(bad)
        for bad in invalid:
            with self.assertRaises(ValueError):checker.evaluate(self.snapshot,self.receipt,bad)
        COVERAGE['accounting_mutation_rejections']=len(invalid)


if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
