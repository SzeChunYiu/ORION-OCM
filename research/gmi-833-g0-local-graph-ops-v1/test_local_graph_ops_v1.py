from __future__ import annotations
import importlib.util, json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('ops',ROOT/'local_graph_ops_v1.py')
if spec is None or spec.loader is None: raise RuntimeError
M=importlib.util.module_from_spec(spec); sys.modules[spec.name]=M; spec.loader.exec_module(M)

class T(unittest.TestCase):
  def test_freeze(self): self.assertEqual(M.FREEZE_COMMIT,'7e81a8fedb8f367238f8339200ab15c79e9429bc')
  def test_all_graphs(self): self.assertEqual(len(tuple(M.all_graphs())),8)
  def test_state_valid(self): self.assertEqual(M.validate_state((0,1,2)),(0,1,2))
  def test_state_short(self):
    with self.assertRaisesRegex(ValueError,'STATE_DOMAIN'): M.validate_state((0,1))
  def test_state_value(self):
    with self.assertRaisesRegex(ValueError,'STATE_VALUE'): M.validate_state((0,1,3))
  def test_edge_outside(self):
    with self.assertRaisesRegex(ValueError,'EDGE_OUTSIDE_CARRIER'): M.make_graph(((0,3),))
  def test_self_loop(self):
    with self.assertRaisesRegex(ValueError,'SELF_LOOP'): M.make_graph(((1,1),))
  def test_duplicate_edge(self):
    with self.assertRaisesRegex(ValueError,'DUPLICATE_EDGE'): M.make_graph(((0,1),(1,0)))
  def test_bad_perm(self):
    with self.assertRaisesRegex(ValueError,'NON_BIJECTIVE_RELABELING'): M.validate_perm((0,0,2))
  def test_bad_fold(self):
    with self.assertRaisesRegex(ValueError,'NONCOMMUTATIVE_OR_UNREGISTERED_FOLD'): M.global_broadcast((0,1,2),M.make_graph(()),fold='left_projection')
  def test_pointwise_exact(self): self.assertEqual(M.pointwise((0,1,2),M.make_graph(())).state,(1,2,0))
  def test_global_exact(self): self.assertEqual(M.global_broadcast((1,0,1),M.make_graph(())).state,(0,2,0))
  def test_neighbor_exact(self): self.assertEqual(M.neighbor_update((1,1,0),M.make_graph(((0,1),))).state,(2,2,0))
  def test_pointwise_resources(self): self.assertEqual(M.pointwise((0,0,0),M.make_graph(())).resources,(3,3,0,0))
  def test_global_resources(self): self.assertEqual(M.global_broadcast((0,0,0),M.make_graph(())).resources,(6,3,0,2))
  def test_neighbor_resource_hist(self): self.assertEqual(M.graph_resource_histogram(),{'0':[[3,3,0,0]],'1':[[5,3,2,0]],'2':[[7,3,4,1]],'3':[[9,3,6,3]]})
  def test_recount_all_graphs(self):
    for g in M.all_graphs():
      for name,fn in [('POINTWISE',M.pointwise),('GLOBAL_BROADCAST',M.global_broadcast),('NEIGHBOR_UPDATE',M.neighbor_update)]: self.assertEqual(fn((0,1,2),g).resources,M.recount_resources(name,g))
  def test_transport_state(self): self.assertEqual(M.transport_state((0,1,2),(2,0,1)),(1,2,0))
  def test_transport_graph(self): self.assertEqual(M.transport_graph(M.make_graph(((0,1),)),(2,0,1)).edges,frozenset({(0,2)}))
  def test_equiv_counts(self): self.assertEqual(M.equivariance_census()['comparisons'],{'POINTWISE':1296,'GLOBAL_BROADCAST':1296,'NEIGHBOR_UPDATE':1296})
  def test_equiv_zero(self): self.assertEqual(M.equivariance_census()['equivariance_mismatches'],{'POINTWISE':0,'GLOBAL_BROADCAST':0,'NEIGHBOR_UPDATE':0})
  def test_resource_zero(self): self.assertEqual(M.equivariance_census()['resource_mismatches'],{'POINTWISE':0,'GLOBAL_BROADCAST':0,'NEIGHBOR_UPDATE':0})
  def test_topology_separation(self): self.assertTrue(all(M.separation_hostiles()['topology'].values()))
  def test_remote_separation(self): self.assertTrue(all(M.separation_hostiles()['remote'].values()))
  def test_neighbor_separation(self): self.assertTrue(all(M.separation_hostiles()['neighbor'].values()))
  def test_edge_separation(self): self.assertTrue(all(M.separation_hostiles()['edge'].values()))
  def test_malformed_exact(self): self.assertNotIn('ACCEPTED',M.malformed_hostiles().values())
  def test_receipt_green(self): self.assertEqual(M.build_receipt()['terminal'],'GMI_833_LOCAL_GLOBAL_GRAPH_OPS_V1_ALL_GREEN')
  def test_forbidden(self): self.assertEqual(len(M.FORBIDDEN_PROMOTIONS),9)
  def test_committed_receipt(self): self.assertEqual(M.canonical_json(M.build_receipt()),(ROOT/'RESULT_V1.json').read_text())
  def test_oracle(self):
    cp=subprocess.run([sys.executable,'-I','-B',str(ROOT/'independent_oracle_v1.py')],check=True,text=True,capture_output=True)
    o=json.loads(cp.stdout); r=M.build_receipt()
    self.assertEqual(o['comparisons'],r['equivariance_census']['comparisons'])
    self.assertEqual(o['equivariance_mismatches'],r['equivariance_census']['equivariance_mismatches'])
    self.assertEqual(o['resource_mismatches'],r['equivariance_census']['resource_mismatches'])
    self.assertEqual(o['neighbor_resource_histogram'],r['neighbor_resource_histogram'])
    self.assertEqual(o['terminal'],'GREEN')

if __name__=='__main__': unittest.main()
