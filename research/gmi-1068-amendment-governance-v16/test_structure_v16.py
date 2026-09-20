"""Actual immutable targets and append-only revision structure controls."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ledger_test_support_v16',HERE/'ledger_test_support_v16.py')
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)
COVERAGE = {}


def replace(value,path,replacement):
    for key in path[:-1]:
        value = value[key]
    value[path[-1]] = replacement


class StructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = support.contract()

    def test_valid_unchanged_and_additive(self):
        baseline = support.baseline(self.contract)
        state = support.structure.validate_structure(baseline,None,self.contract)
        self.assertEqual(state['leaves'],{})
        initial = support.revisions(self.contract)
        state = support.structure.validate_structure(initial,None,self.contract)
        self.assertEqual(len(state['leaves']),2)
        unchanged = support.successor(initial)
        self.assertEqual(support.structure.validate_structure(unchanged,initial,self.contract),state)
        partial = support.baseline(self.contract)
        support.append(partial,'REVISION','revision-0',self.contract['permitted_revisions'][0])
        added = support.successor(partial)
        support.append(added,'REVISION','revision-1',self.contract['permitted_revisions'][1])
        self.assertEqual(len(support.structure.validate_structure(added,partial,self.contract)['leaves']),2)
        future_contract = deepcopy(self.contract)
        future = deepcopy(future_contract['permitted_revisions'][0])
        future.update(revision_id=future['revision_id'].replace('@r1','@r2'),supersedes=future['revision_id'])
        future_contract['permitted_revisions'].append(future)
        revised = support.successor(initial)
        support.append(revised,'REVISION','revision-next',future)
        state = support.structure.validate_structure(revised,initial,future_contract)
        self.assertEqual(state['leaves'][future['original_atom_id']],future['revision_id'])
        COVERAGE['valid_structure_controls'] = 5

    def test_exact_schema_history_and_scope(self):
        initial = support.revisions(self.contract)
        mutations = [
          (('control_plane',),True),(('control_plane',),1068.0),
          (('protocol_freeze_commit',),'0'*40),(('contract_sha256',),'0'*64),
          (('original_snapshot','sha256'),'0'*64),
          (('targets',0,'baseline_snapshot_record','status'),'CLOSED'),
          (('targets',0,'baseline_snapshot_record','title'),'different original'),
          (('targets',0,'baseline_snapshot_record','evidence'),[{'invented':True}]),
          (('targets',0,'original_checklist_record','closes_by_prose'),0),
          (('targets',0,'qualified_disposition'),'VERIFIED'),
          (('targets',0,'refuted_reading'),'all historical interpretations are false'),
          (('targets',0,'source_targets',0,'exact_text'),'different frozen passage'),
          (('targets',0,'source_targets',0,'text_sha256'),'0'*64),
          (('events',0,'seq'),False),(('events',0,'seq'),0.0),
          (('events',0,'type'),'CLOSE_ORIGINAL'),(('events',0,'id'),''),
          (('events',1,'id'),initial['events'][0]['id']),
          (('events',0,'payload','required_statements'),[]),
          (('events',0,'payload','explicit_changes'),['weaken observable silently']),
          (('events',0,'payload','parent_ownership'),'new universal discovery'),
          (('events',0,'payload','original_atom_id'),'GMI2-R2-007'),
          (('events',0,'payload','revision_id'),'unregistered-revision'),
        ]
        bads = []
        for path,value in mutations:
            bad = deepcopy(initial)
            replace(bad,path,value)
            bads.append(support.rebind(bad))
        for field in initial:
            bad = deepcopy(initial);del bad[field];bads.append(bad)
        for path in ((),('events',0),('events',0,'payload'),('original_snapshot',)):
            bad = deepcopy(initial);cursor = bad
            for key in path:cursor = cursor[key]
            cursor['unexpected'] = True
            bads.append(support.rebind(bad))
        bad = deepcopy(initial);bad['events'][1]['previous_sha256']='0'*64;bads.append(bad)
        bad = deepcopy(initial);bad['targets']=[];bads.append(bad)
        for bad in bads:
            with self.assertRaises((ValueError,TypeError)):
                support.structure.validate_structure(bad,None,self.contract)
        prefix_bad = []
        successor = support.successor(initial)
        for count in (True,2.0,1):
            bad = deepcopy(successor);bad['previous_ledger']['event_count']=count;prefix_bad.append(bad)
        bad = deepcopy(successor);bad['events'].pop();prefix_bad.append(bad)
        bad = deepcopy(successor);bad['events'].reverse();prefix_bad.append(support.rebind(bad))
        bad = deepcopy(successor);bad['events'][0]['id']='rewritten';prefix_bad.append(support.rebind(bad))
        for bad in prefix_bad:
            with self.assertRaises(ValueError):
                support.structure.validate_structure(bad,initial,self.contract)
        # Exact bool/int alias at a one-event checkpoint, not merely a wrong count.
        one = deepcopy(initial);one['events']=one['events'][:1]
        bad = support.successor(one);bad['previous_ledger']['event_count']=True
        with self.assertRaises(ValueError):support.structure.validate_structure(bad,one,self.contract)
        COVERAGE['structure_mutation_rejections'] = len(bads)+len(prefix_bad)+1

    def test_revision_graph_falsifiers(self):
        rejected = 0
        first,second = self.contract['permitted_revisions']
        for kind in ('self-cycle','forward-dependency','duplicate-dependency','fork','cross-original'):
            contract = deepcopy(self.contract)
            if kind=='self-cycle':
                contract['permitted_revisions'][0]['supersedes']=first['revision_id']
            elif kind=='forward-dependency':
                contract['permitted_revisions'][0]['dependency_revision_ids']=[second['revision_id']]
            elif kind=='duplicate-dependency':
                contract['permitted_revisions'][1]['dependency_revision_ids']=[first['revision_id']]*2
            else:
                future = deepcopy(first)
                future['revision_id']=first['revision_id'].replace('@r1','@r2')
                future['supersedes']=first['original_atom_id'] if kind=='fork' else second['revision_id']
                contract['permitted_revisions'].append(future)
            ledger = support.revisions(contract)
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                support.structure.validate_structure(ledger,None,contract)
            rejected += 1
        COVERAGE['revision_graph_rejections'] = rejected


if __name__=='__main__':
    program=unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
