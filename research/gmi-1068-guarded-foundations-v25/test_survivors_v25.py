"""Actual six-survivor ledger no-alarm, omissions, type aliases and identity edits."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import audit_survivors_v25 as audit
COVERAGE={}
FIELDS=('component','original_loss','corrected_survivor','removed','preserved','model','query','response','strongest_parent','paper')

class SurvivorTests(unittest.TestCase):
    def test_real_ledger_and_mutations(self):
        ledger=json.loads((HERE/'SURVIVOR_LEDGER_V25.json').read_text())
        expected={'original_survivors':['TYPE','PROCESS','COMPOSITION','IDENTITY','ASSOCIATIVITY','IDENTITY_LAWS'],'reconciled_rows':6}
        self.assertEqual(audit.verify(ROOT),expected)
        self.assertEqual(audit.verify(ROOT,deepcopy(ledger)),expected)
        invalid=[]
        for key in ledger:
            bad=deepcopy(ledger);del bad[key];invalid.append(bad)
        bad=deepcopy(ledger);bad['extra']='unregistered';invalid.append(bad)
        for key,value in (('schema','different'),('original_source','different'),('claim',''),('claim',' '),
                          ('claim',None),('claim',True),('rows',tuple(ledger['rows'])),('rows',[])):
            bad=deepcopy(ledger);bad[key]=value;invalid.append(bad)
        for index,row in enumerate(ledger['rows']):
            self.assertEqual(set(row),set(FIELDS))
            for field in FIELDS:
                bad=deepcopy(ledger);del bad['rows'][index][field];invalid.append(bad)
                for value in ('',' ',None,True,0,1.0,[]):
                    bad=deepcopy(ledger);bad['rows'][index][field]=value;invalid.append(bad)
            for field in ('component','original_loss'):
                bad=deepcopy(ledger);bad['rows'][index][field]='unregistered substitution';invalid.append(bad)
            bad=deepcopy(ledger);bad['rows'][index]['extra']='unregistered';invalid.append(bad)
            bad=deepcopy(ledger);bad['rows'][index]=deepcopy(ledger['rows'][(index+1)%6]);invalid.append(bad)
            bad=deepcopy(ledger);del bad['rows'][index];invalid.append(bad)
        bad=deepcopy(ledger);bad['rows'].reverse();invalid.append(bad)
        for key in ('coherence','named_encoder','equivalent_encodings'):
            bad=deepcopy(ledger);del bad['additional_controls'][key];invalid.append(bad)
            for value in ('',' ',None,True,0,1.0,[]):
                bad=deepcopy(ledger);bad['additional_controls'][key]=value;invalid.append(bad)
        bad=deepcopy(ledger);bad['additional_controls']['extra']='unregistered';invalid.append(bad)
        rejected=0
        for index,bad in enumerate(invalid):
            with self.subTest(case=index),self.assertRaises(ValueError):audit.verify(ROOT,bad)
            rejected+=1
        COVERAGE.update(valid_survivor_ledger_controls=1,survivor_ledger_mutation_rejections=rejected)

if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2).result
    print(json.dumps(COVERAGE,sort_keys=True));raise SystemExit(not result.wasSuccessful())
