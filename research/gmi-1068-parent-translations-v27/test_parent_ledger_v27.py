"""Actual seven historical parent rows and coupled source/ledger mutation controls."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import audit_parents_v27 as audit
COVERAGE={}
OLD=('name','parents','native','additional_or_external','status')
NEW=('map','operations','observer','lost_data','inverse_scope','premises',
     'proof_level','falsifier','strongest_parent','details')
IDS=['categorical_process_theory','operational_probabilistic_theory','relations',
     'stochastic_kernels','labelled_transition_systems','coalgebra','constructor_theory']


class ParentLedgerTests(unittest.TestCase):
    def test_real_rows_and_source_mutations(self):
        ledger=json.loads((HERE/'PARENT_TRANSLATIONS_V27.json').read_text())
        expected={'original_parent_ids':IDS,'reconciled_rows':7}
        self.assertEqual(audit.verify(ROOT),expected)
        self.assertEqual(audit.verify(ROOT,deepcopy(ledger)),expected)
        invalid=[]
        for key in ledger:
            bad=deepcopy(ledger);del bad[key];invalid.append(bad)
        bad=deepcopy(ledger);bad['extra']='unregistered';invalid.append(bad)
        for field,values in (('scope',('', ' ',None,True,0,1.0,[])),
               ('schema',('different',None,True,0)),('rows',([],tuple(ledger['rows']),None))):
            for value in values:
                bad=deepcopy(ledger);bad[field]=value;invalid.append(bad)
        for field in ('path','sha256','pointer'):
            bad=deepcopy(ledger);del bad['source'][field];invalid.append(bad)
            for value in ('different','',None,True,0,1.0,[]):
                bad=deepcopy(ledger);bad['source'][field]=value;invalid.append(bad)
        bad=deepcopy(ledger);bad['source']['extra']='unregistered';invalid.append(bad)
        for index,row in enumerate(ledger['rows']):
            self.assertEqual(set(row),set(OLD+NEW))
            for field in OLD+NEW:
                bad=deepcopy(ledger);del bad['rows'][index][field];invalid.append(bad)
                for value in ('',' ',None,True,0,1.0,[]):
                    bad=deepcopy(ledger);bad['rows'][index][field]=value;invalid.append(bad)
            for field in OLD:
                bad=deepcopy(ledger);bad['rows'][index][field]='unregistered substitution';invalid.append(bad)
            bad=deepcopy(ledger);bad['rows'][index]['parents']=tuple(row['parents']);invalid.append(bad)
            bad=deepcopy(ledger);bad['rows'][index]['extra']='unregistered';invalid.append(bad)
            bad=deepcopy(ledger);bad['rows'][index]=deepcopy(ledger['rows'][(index+1)%7]);invalid.append(bad)
            bad=deepcopy(ledger);del bad['rows'][index];invalid.append(bad)
        bad=deepcopy(ledger);bad['rows'].reverse();invalid.append(bad)
        rejected=0
        for index,bad in enumerate(invalid):
            with self.subTest(case=index),self.assertRaises(ValueError):audit.verify(ROOT,bad)
            rejected+=1
        with tempfile.TemporaryDirectory(prefix='gmi-v27-parent-ledger-') as temp:
            root=Path(temp);source=root/audit.ORIGINAL
            source.parent.mkdir(parents=True)
            original=json.loads((ROOT/audit.ORIGINAL).read_text())
            original['formalisms'][0]['name']='coupled replacement'
            bad=deepcopy(ledger);bad['rows'][0]['name']='coupled replacement'
            source.write_text(json.dumps(original))
            import hashlib
            bad['source']['sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):audit.verify(root,bad)
            rejected+=1
        COVERAGE.update(valid_parent_ledger_controls=1,parent_ledger_mutation_rejections=rejected)
