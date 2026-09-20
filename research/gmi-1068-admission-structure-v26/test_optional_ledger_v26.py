"""Actual six removed-component rows: complete identities, source binding and malformed controls."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import audit_optional_v26 as audit
COVERAGE={}
FIELDS=('component','status','claim','assumptions','witness','retained_observer',
        'information_not_recovered','proof_level','falsifier','strongest_parent','dependencies','details')


class OptionalLedgerTests(unittest.TestCase):
    def test_real_ledger_and_mutations(self):
        ledger=json.loads((HERE/'OPTIONAL_LEDGER_V26.json').read_text())
        expected={'original_removed_components':['TENSOR','SYMMETRY','STOCHASTICITY',
                    'NONDETERMINISTIC_CHOICE','HIGHER_CELLS','EXTERNAL_ADMISSIBILITY_PREDICATE'],'reconciled_rows':6}
        self.assertEqual(audit.verify(ROOT),expected)
        self.assertEqual(audit.verify(ROOT,deepcopy(ledger)),expected)
        invalid=[]
        for key in ledger:
            bad=deepcopy(ledger);del bad[key];invalid.append(bad)
        bad=deepcopy(ledger);bad['extra']='unregistered';invalid.append(bad)
        for key,value in (('schema','different'),('source','different'),('source',{}),
                          ('rows',tuple(ledger['rows'])),('rows',[])):
            bad=deepcopy(ledger);bad[key]=value;invalid.append(bad)
        for field in ('observer','boundary'):
            for value in ('',' ',None,True,0,1.0,[]):
                bad=deepcopy(ledger);bad[field]=value;invalid.append(bad)
        for field in ('path','sha256','pointer'):
            bad=deepcopy(ledger);del bad['source'][field];invalid.append(bad)
            for value in ('different','',None,True,0,1.0,[]):
                bad=deepcopy(ledger);bad['source'][field]=value;invalid.append(bad)
        bad=deepcopy(ledger);bad['source']['extra']='unregistered';invalid.append(bad)
        for index,row in enumerate(ledger['rows']):
            self.assertEqual(set(row),set(FIELDS))
            for field in FIELDS:
                bad=deepcopy(ledger);del bad['rows'][index][field];invalid.append(bad)
                for value in ('',' ',None,True,0,1.0,[]):
                    bad=deepcopy(ledger);bad['rows'][index][field]=value;invalid.append(bad)
            for field in ('component','status'):
                bad=deepcopy(ledger);bad['rows'][index][field]='unregistered substitution';invalid.append(bad)
            bad=deepcopy(ledger);bad['rows'][index]['extra']='unregistered';invalid.append(bad)
            bad=deepcopy(ledger);bad['rows'][index]=deepcopy(ledger['rows'][(index+1)%6]);invalid.append(bad)
            bad=deepcopy(ledger);del bad['rows'][index];invalid.append(bad)
        bad=deepcopy(ledger);bad['rows'].reverse();invalid.append(bad)
        rejected=0
        for index,bad in enumerate(invalid):
            with self.subTest(case=index),self.assertRaises(ValueError):audit.verify(ROOT,bad)
            rejected+=1
        COVERAGE.update(valid_optional_ledger_controls=1,optional_ledger_mutation_rejections=rejected)
