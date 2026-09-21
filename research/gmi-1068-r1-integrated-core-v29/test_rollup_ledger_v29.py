"""Actual source-specific original crosswalk and all three inherited row ledgers."""
from copy import deepcopy
import json
import unittest
from support_v29 import ROOT, HERE, core
import audit_rollup_v29 as audit
COVERAGE = {}


def nodes(value,path=()):
    yield path,value
    if type(value) is dict:
        for key,item in value.items():yield from nodes(item,path+(key,))
    elif type(value) is list:
        for i,item in enumerate(value):yield from nodes(item,path+(i,))


def replace_at(value,path,replacement):
    result=deepcopy(value)
    if not path:return replacement
    target=result
    for part in path[:-1]:target=target[part]
    target[path[-1]]=replacement
    return result


class RollupLedgerTests(unittest.TestCase):
    def test_original_results_atoms_and_inherited_rows(self):
        baseline=json.loads((HERE/'ORIGINAL_CROSSWALK_V29.json').read_text())
        good=audit.verify(ROOT,baseline)
        self.assertEqual(good,dict(original_results=['R1-RESULT-'+str(i) for i in range(1,9)],
                         original_atoms=['GMI2-R1-'+str(i).zfill(3) for i in range(1,11)],
                         survivor_rows=6,optional_rows=6,parent_rows=7,source_records=41,located_records=88))
        rejected=0
        for path,value in nodes(baseline):
            if type(value) is str:replacement='altered '+value
            elif type(value) is int:replacement=float(value)
            elif type(value) is list:replacement=value[:-1] if value else ['extra']
            elif type(value) is dict:replacement={**value,'unexpected':None}
            else:replacement='invalid'
            mutation=replace_at(baseline,path,replacement)
            with self.subTest(path=path),self.assertRaises(ValueError):audit.verify(ROOT,mutation)
            rejected+=1
        inherited=0
        cases=((core.survivor_audit,'research/gmi-1068-guarded-foundations-v25/SURVIVOR_LEDGER_V25.json'),
               (core.optional_audit,'research/gmi-1068-admission-structure-v26/OPTIONAL_LEDGER_V26.json'),
               (core.parent_audit,'research/gmi-1068-parent-translations-v27/PARENT_TRANSLATIONS_V27.json'))
        for guard,name in cases:
            ledger=json.loads((ROOT/name).read_text())
            good=guard.verify(ROOT,ledger);self.assertEqual(good['reconciled_rows'],len(ledger['rows']))
            mutations=[]
            for row in range(len(ledger['rows'])):
                deleted=deepcopy(ledger);del deleted['rows'][row];mutations.append(deleted)
                for key in ledger['rows'][row]:
                    bad=deepcopy(ledger);bad['rows'][row][key]=None;mutations.append(bad)
            bad=deepcopy(ledger);bad['rows'].reverse();mutations.append(bad)
            for bad in mutations:
                with self.assertRaises(ValueError):guard.verify(ROOT,bad)
                inherited+=1
        COVERAGE.update(valid_rollup_ledgers=4,crosswalk_mutation_rejections=rejected,
                        inherited_ledger_mutation_rejections=inherited)
