"""Authored engineering controls; no protected corpus or historical study rerun."""
from __future__ import annotations
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import lifecycle as L
import allocation as A
PARENT = REPO / "research/ordinary-goal-native-bridge-v1/source"
sys.path[:0] = [str(PARENT), str(PARENT / "vendor")]
import authored_fixture as F

class PureControls(unittest.TestCase):
    def test_empty_population(self):
        with self.assertRaises(ValueError): L.validate_population([])
    def test_duplicate_population(self):
        with self.assertRaises(ValueError): L.validate_population([F.task(), F.task()])
    def test_oracle_field_rejected(self):
        t = F.task(); t['official_proof'] = ['learned-cut']
        with self.assertRaises(ValueError): L.validate_population([t])
    def test_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'x.json'; p.write_text('{"x":NaN}')
            with self.assertRaises(ValueError): L.read_json(p)
    def test_duplicate_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'x.json'; p.write_text('{"x":1,"x":2}')
            with self.assertRaises(ValueError): L.read_json(p)
    def test_source_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x';p.write_bytes(b'new')
            with self.assertRaises(ValueError): L.checked_file(p,L.raw_id(b'old'))
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'a';b=Path(d)/'b';a.write_bytes(b'a');b.symlink_to(a)
            with self.assertRaises(ValueError): L.checked_file(b,L.raw_id(b'a'))
    def test_path_escape(self):
        with self.assertRaises(ValueError): L.relative(Path('/tmp'), '../x')
    def test_durable_write_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x';L.write_new(p,b'a')
            with self.assertRaises(FileExistsError): L.write_new(p,b'b')
            self.assertEqual(p.read_bytes(),b'a')
    def test_boundary_denies_undeclared_read(self):
        blocked,hook=L.audit_boundary(set(),Path('/tmp/isolated-output'))
        with self.assertRaises(PermissionError): hook('open',('/tmp/answer-oracle','r',0))
        self.assertEqual(len(blocked),1)
    def test_boundary_denies_outside_write(self):
        _,hook=L.audit_boundary({'/tmp/pinned'},Path('/tmp/isolated-output'))
        with self.assertRaises(PermissionError): hook('open',('/tmp/pinned','w',os.O_WRONLY))
    def test_boundary_denies_network(self):
        _,hook=L.audit_boundary(set(),Path('/tmp/isolated-output'))
        with self.assertRaises(PermissionError): hook('socket.connect',('example.invalid',443))
    def test_boundary_denies_child(self):
        _,hook=L.audit_boundary(set(),Path('/tmp/isolated-output'))
        with self.assertRaises(PermissionError): hook('subprocess.Popen',('solver',))
    def test_boundary_allows_exact_inputs(self):
        blocked,hook=L.audit_boundary({'/tmp/pinned'},Path('/tmp/isolated-output'))
        hook('open',('/tmp/pinned','r',0));hook('open',('/tmp/isolated-output/result','w',os.O_WRONLY))
        self.assertEqual(blocked,[])
    def test_independent_boolean_oracle(self):
        # Exhaust all assignments; identities include complement-sensitive difference.
        self.assertEqual(A.mask(('i^i','A','B')), A.mask(('i^i','B','A')))
        self.assertNotEqual(A.mask(('\\','A','B')), A.mask(('\\','B','A')))
        self.assertEqual(A.mask(('\\','A',('u.','B','C'))),A.mask(('i^i',('\\','A','B'),('\\','A','C'))))
    def test_alpha_canonicalization(self):
        a=['|-','(','A','\\','B',')','=','C']
        b=['|-','(','C','\\','A',')','=','B']
        self.assertEqual(A.canonical(a),A.canonical(b))

class ColdProcessControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.temp.name);bundle=cls.root/'bundle';bundle.mkdir()
        b=F.bundle()
        for name,raw in [('base.mm',b['base']),('joined.mm',b['joined']),('manifest.json',L.encoded(b['manifest'])),('receipt.json',b['receipt'])]:
            (bundle/name).write_bytes(raw)
        t1=F.task();t2=F.task();t2['limits']['max_decisions']=1
        t3=F.task();t3['query']=['|-','(','ch','->','(','ph','/\\','ps',')',')']
        cls.tasks=[t1,t2,t3];p=cls.root/'tasks.json';p.write_bytes(L.encoded(cls.tasks))
        cls.result=L.run(REPO,bundle,p,cls.root/'run',hard_wall=20)
        if cls.result['comparison'] is None:
            raise AssertionError((cls.root/'run/arm-0/stderr.txt').read_text())
        cls.reports=[L.read_json(cls.root/f'run/arm-{i}/output/WORKER.json') for i in range(3)]
        cls.manifest=b['manifest']
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def test_distinct_processes(self):
        pids=[r['pid'] for r in self.reports]
        self.assertEqual(len(set(pids)),3);self.assertNotIn(os.getpid(),pids)
    def test_native_success_all_arms(self):
        self.assertEqual(self.result['comparison']['rows'][0]['native_verified'],[True]*3)
    def test_actual_method_consumption(self):
        self.assertEqual(self.result['comparison']['rows'][0]['decision_counts'],[1,2,1])
        self.assertEqual(self.result['comparison']['rows'][0]['selected_cohort_labels'],['learned-cut'])
    def test_bounded_absence(self):
        r=self.result['comparison']['rows'][1]
        self.assertEqual(r['native_verified'],[True,False,True]);self.assertTrue(r['causal_decision_witness'])
        self.assertEqual(r['terminals'][1],'NO_PROOF_IN_REGISTERED_FINITE_BANK')
    def test_renamed_goal_complete_native(self):
        self.assertEqual(self.result['comparison']['rows'][2]['native_verified'],[True]*3)
    def test_same_preparation_and_restoration(self):
        self.assertTrue(self.result['comparison']['all_preparation_parity']);self.assertTrue(self.result['comparison']['all_restored'])
    def test_no_blocked_events(self): self.assertTrue(all(not r['blocked_events'] for r in self.reports))
    def test_no_allocation_module_in_worker(self):
        for r in self.reports:
            self.assertFalse(any('allocation' in m['path'] for m in r['imports'].values()))
    def test_empty_arm_rejected(self):
        r=copy.deepcopy(self.reports);r[1]['rows']=[]
        with self.assertRaises(ValueError): L.reconcile(self.tasks,r)
    def test_truncated_arm_rejected(self):
        r=copy.deepcopy(self.reports);r[1]['rows'].pop()
        with self.assertRaises(ValueError): L.reconcile(self.tasks,r)
    def test_repeated_occurrence_rejected(self):
        r=copy.deepcopy(self.reports);r[1]['occurrence']=r[0]['occurrence']
        with self.assertRaises(ValueError): L.reconcile(self.tasks,r)
    def test_cross_arm_source_drift_rejected(self):
        r=copy.deepcopy(self.reports);r[1]['source']['sha256']='0'*64
        with self.assertRaises(ValueError): L.reconcile(self.tasks,r)
    def test_wrong_row_identity_rejected(self):
        r=copy.deepcopy(self.reports);r[1]['rows'][0]['task']=r[1]['rows'][1]['task']
        with self.assertRaises(ValueError): L.reconcile(self.tasks,r)
    def test_forged_native_success_rejected(self):
        r=copy.deepcopy(self.reports);r[0]['rows'][0]['native']['native_result']['terminal']='NATIVE_REJECTED'
        with self.assertRaises(ValueError): L.reconcile(self.tasks,r)
    def test_forged_proof_rejected(self):
        r=copy.deepcopy(self.reports);r[0]['rows'][0]['native']['issued_claim']['proof']=[]
        with self.assertRaises(ValueError): L.reconcile(self.tasks,r)
    def test_forged_use_rejected(self):
        r=copy.deepcopy(self.reports);r[0]['rows'][0]['native']['selected_cohort_labels']=[]
        with self.assertRaises(ValueError): L.reconcile(self.tasks,r)
    def test_unknown_is_not_capability_effect(self):
        r=copy.deepcopy(self.reports);row=r[1]['rows'][0];row['native']=None
        row['solve'].update(terminal='UNKNOWN',generated_proof=None)
        self.assertFalse(L.reconcile(self.tasks,r)['rows'][0]['causal_decision_witness'])
    def test_failed_native_is_not_capability_effect(self):
        r=copy.deepcopy(self.reports);r[1]['rows'][0]['native']['terminal']='CANNOT_CHECK'
        self.assertFalse(L.reconcile(self.tasks,r)['rows'][0]['causal_decision_witness'])
    def test_forged_retained_row_rejected(self):
        r=copy.deepcopy(self.reports[0]);r['rows'][0]['wall_seconds']+=1
        with self.assertRaises(ValueError): L.verify_retained_outputs(self.root/'run/arm-0/output',self.tasks,r,self.manifest)
    def test_stale_request_refused_before_execution(self):
        with self.assertRaises(ValueError): L._worker(self.root/'run/arm-0/REQUEST.json','0'*64)

if __name__=='__main__': unittest.main(verbosity=2)
