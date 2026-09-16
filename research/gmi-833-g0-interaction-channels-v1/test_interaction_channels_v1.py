from __future__ import annotations
import importlib.util,json,subprocess,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('ic',R/'interaction_channels_v1.py')
if sp is None or sp.loader is None:raise RuntimeError
M=importlib.util.module_from_spec(sp);sys.modules[sp.name]=M;sp.loader.exec_module(M)
class T(unittest.TestCase):
 def test_freeze(self):self.assertEqual(M.FREEZE_COMMIT,'d7d2c0dc99fefa3b175925d3c7884510086bee69')
 def test_channels(self):self.assertEqual(len(M.CHANNELS),6)
 def test_self(self):
  with self.assertRaisesRegex(ValueError,'SELF_CHANNEL'):M.send(M.Machine.empty(),0,0,1)
 def test_agent(self):
  with self.assertRaisesRegex(ValueError,'AGENT_OUTSIDE_CARRIER'):M.send(M.Machine.empty(),0,3,1)
 def test_msg(self):
  with self.assertRaisesRegex(ValueError,'MESSAGE_OUTSIDE_ALPHABET'):M.send(M.Machine.empty(),0,1,2)
 def test_empty_recv(self):
  st,val,res=M.recv(M.Machine.empty(),0,1);self.assertEqual(val,M.NO_MESSAGE);self.assertNotEqual(val,0);self.assertEqual(res,(0,1,0,0,0,0,0))
 def test_send_resources(self):self.assertEqual(M.send(M.Machine.empty(),0,1,1)[1],(1,0,0,0,0,0,0))
 def test_apply_resources(self):self.assertEqual(M.apply_received(M.Machine.empty(),1,1)[1],(0,0,1,1,0,0,0))
 def test_call_resources(self):self.assertEqual(M.call('ROT',1)[1],(0,0,0,0,1,1,1))
 def test_apply_external_resources(self):self.assertEqual(M.apply_external(M.Machine.empty(),0,M.call('ROT',1)[0])[1],(0,0,1,1,0,0,0))
 def test_rot(self):self.assertEqual([M.call('ROT',x)[0].value for x in M.Z3],[1,2,0])
 def test_double(self):self.assertEqual([M.call('DOUBLE',x)[0].value for x in M.Z3],[0,2,1])
 def test_unknown_tool(self):
  with self.assertRaisesRegex(ValueError,'UNKNOWN_TOOL'):M.call('NOPE',0)
 def test_bad_arg(self):
  with self.assertRaisesRegex(ValueError,'TOOL_ARGUMENT'):M.call('ROT',3)
 def test_forged(self):
  with self.assertRaisesRegex(ValueError,'FORGED_EXTERNAL_DATA'):M.apply_external(M.Machine.empty(),0,M.ExternalData('ROT',0,2))
 def test_bad_perm(self):
  with self.assertRaisesRegex(ValueError,'NON_BIJECTIVE_AGENT_REMINT'):M.validate_perm((0,0,2))
 def test_census_remint(self):self.assertEqual((M.census()['remint_checks'],M.census()['remint_failures']),(72,0))
 def test_fifo(self):self.assertEqual((M.census()['fifo_checks'],M.census()['fifo_failures']),(24,0))
 def test_tool(self):self.assertEqual((M.census()['tool_checks'],M.census()['tool_failures']),(6,0))
 def test_order(self):self.assertTrue(M.census()['tool_composition_order_distinct'])
 def test_dest(self):self.assertEqual(M.census()['destination_isolation_failures'],0)
 def test_bcast(self):self.assertEqual(M.census()['implicit_broadcast_failures'],0)
 def test_send_local(self):self.assertEqual(M.census()['send_local_mutation_failures'],0)
 def test_sep(self):self.assertTrue(all(M.separation().values()))
 def test_hostiles(self):self.assertNotIn('ACCEPTED',M.hostiles().values())
 def test_external_status(self):self.assertEqual(M.call('ROT',0)[0].status,'EXTERNAL_DATA')
 def test_receipt(self):self.assertEqual(M.build_receipt()['terminal'],'GMI_833_INTERACTION_CHANNELS_V1_ALL_GREEN')
 def test_committed(self):self.assertEqual(M.canonical_json(M.build_receipt()),(R/'RESULT_V1.json').read_text())
 def test_oracle(self):
  o=json.loads(subprocess.run([sys.executable,'-I','-B',str(R/'independent_oracle_v1.py')],check=True,text=True,capture_output=True).stdout);c=M.census()
  for k in ('remint_checks','remint_failures','destination_isolation_failures','implicit_broadcast_failures','fifo_checks','fifo_failures'):self.assertEqual(o[k],c[k])
  self.assertEqual(o['tool_compositions'],c['tool_compositions']);self.assertEqual(o['terminal'],'GREEN')
if __name__=='__main__':unittest.main()
