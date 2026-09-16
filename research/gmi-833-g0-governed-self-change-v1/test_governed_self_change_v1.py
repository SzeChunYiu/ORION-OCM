from __future__ import annotations
import importlib.util,json,subprocess,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('gsc',R/'governed_self_change_v1.py')
if sp is None or sp.loader is None: raise RuntimeError
M=importlib.util.module_from_spec(sp);sys.modules[sp.name]=M;sp.loader.exec_module(M)
class T(unittest.TestCase):
 def test_freeze(self): self.assertEqual(M.FREEZE_COMMIT,'b3afee5e0c8e70812653cf92ef9fd703d77b9d18')
 def test_candidate_space(self): self.assertEqual(len(M.candidate_space()),27)
 def test_policy_counts(self):
  v=M.fixture_verifier(); ds=[v.policy(c) for c in M.candidate_space()]; self.assertEqual((ds.count(M.ACCEPT),ds.count(M.REJECT)),(9,18))
 def test_propose_inert(self):
  for c in M.candidate_space():
   s=M.base_state();ns,p,r=M.propose(s,c);self.assertEqual(ns.active,s.active);self.assertEqual(r,M.PROPOSE_RESOURCES);self.assertEqual(p.base_version,0)
 def test_verify_resources(self):
  s,p,_=M.propose(M.base_state(),(0,2,1));r,res=M.fixture_verifier().verify(p);self.assertEqual(res,M.VERIFY_RESOURCES);self.assertEqual(r.authority_id,M.AUTHORITY_ID)
 def test_accept_once(self):
  v=M.fixture_verifier();s,p,_=M.propose(M.base_state(),(0,2,1));r,_=v.verify(p);a=M.adopt(s,p,r,v);self.assertEqual((a.terminal,a.state.active),('ADOPTED',M.ActiveMachine((0,2,1),1)))
 def test_replay(self):
  v=M.fixture_verifier();s,p,_=M.propose(M.base_state(),(0,2,1));r,_=v.verify(p);a=M.adopt(s,p,r,v);rr=M.adopt(a.state,p,r,v);self.assertEqual(rr.terminal,'PROPOSAL_ALREADY_CONSUMED');self.assertEqual(rr.state,a.state)
 def test_reject_no_active_change(self):
  v=M.fixture_verifier();base=M.base_state();s,p,_=M.propose(base,(1,0,0));r,_=v.verify(p);a=M.adopt(s,p,r,v);self.assertEqual(a.terminal,'REJECTED_BY_VERIFIER');self.assertEqual(a.state.active,base.active)
 def test_stale(self): self.assertTrue(M.exact_census()['stale_receipt_control'])
 def test_two_gen(self): self.assertTrue(M.exact_census()['two_generation_control'])
 def test_counts(self):
  c=M.exact_census();self.assertEqual((c['candidate_count'],c['accepted'],c['rejected']),(27,9,18))
 def test_no_census_failures(self):
  c=M.exact_census()
  for k in ('proposal_inert_failures','accepted_adoption_failures','rejected_mutation_failures','replay_failures'):self.assertEqual(c[k],0)
 def test_authority_hostile(self): self.assertEqual(M.hostiles()['authority'],'AUTHORITY_MISMATCH')
 def test_signature_hostile(self): self.assertEqual(M.hostiles()['signature'],'SIGNATURE_INVALID')
 def test_decision_hostile(self): self.assertEqual(M.hostiles()['decision'],'RECEIPT_DECISION_INVALID')
 def test_digest_hostile(self): self.assertEqual(M.hostiles()['digest'],'RECEIPT_BINDING_MISMATCH')
 def test_version_hostile(self): self.assertEqual(M.hostiles()['version'],'RECEIPT_BINDING_MISMATCH')
 def test_swap_hostile(self): self.assertEqual(M.hostiles()['candidate_swap'],'PROPOSAL_STATE_MISMATCH')
 def test_forged_accept(self): self.assertEqual(M.hostiles()['forged_accept'],'RECEIPT_DECISION_INVALID')
 def test_malformed(self): self.assertEqual(M.hostiles()['malformed_candidate'],'MALFORMED_BEHAVIOR')
 def test_negative_version(self): self.assertEqual(M.hostiles()['negative_version'],'INVALID_VERSION')
 def test_no_signature_in_proposal(self): self.assertEqual(M.hostiles()['proposal_has_signature_field'],'False')
 def test_no_secret_in_proposal(self): self.assertEqual(M.hostiles()['verifier_secret_on_proposal'],'False')
 def test_propose_resource(self): self.assertEqual(M.PROPOSE_RESOURCES,(1,0,0,0,0,0))
 def test_verify_resource(self): self.assertEqual(M.VERIFY_RESOURCES,(0,1,1,0,0,0))
 def test_success_resource(self): self.assertEqual(M.ADOPT_SUCCESS_RESOURCES,(0,0,0,1,1,1))
 def test_failure_resource(self): self.assertEqual(M.ADOPT_FAILURE_RESOURCES,(0,0,0,1,0,0))
 def test_receipt_green(self): self.assertEqual(M.build_receipt()['terminal'],'GMI_833_GOVERNED_SELF_CHANGE_V1_ALL_GREEN')
 def test_committed(self): self.assertEqual(M.canonical_json(M.build_receipt()),(R/'RESULT_V1.json').read_text())
 def test_oracle(self):
  o=json.loads(subprocess.run([sys.executable,'-I','-B',str(R/'independent_oracle_v1.py')],check=True,text=True,capture_output=True).stdout);c=M.exact_census()
  for k in ('candidate_count','accepted','rejected','proposal_inert_failures','accepted_adoption_failures','rejected_mutation_failures','replay_failures','stale_receipt_control','two_generation_control'):self.assertEqual(o[k],c[k])
  self.assertEqual(o['terminal'],'GREEN')
if __name__=='__main__':unittest.main()
