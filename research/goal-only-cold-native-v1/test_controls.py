"""Authored regression controls. Native checking occurs only in the separate cycle."""
from __future__ import annotations
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from custody import (Refusal, adapter_sources, checked_read, encoded, execution_identity,
                     identity, load_bridge, parse, raw_id, read_bundle, store, validate_request,
                     write_bundle)
import qualify

class CustodyControls(unittest.TestCase):
    def test_duplicate_json(self):
        with self.assertRaisesRegex(Refusal, 'DUPLICATE'): parse(b'{"a":1,"a":2}')
    def test_nonfinite_json(self):
        for value in (b'NaN', b'Infinity', b'-Infinity'):
            with self.subTest(value=value), self.assertRaisesRegex(Refusal, 'NONFINITE'): parse(value)
    def test_exclusive_record(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x';store(p,b'original')
            with self.assertRaises(FileExistsError): store(p,b'replacement')
            self.assertEqual(p.read_bytes(),b'original')
    def test_changed_content(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x';p.write_bytes(b'changed')
            with self.assertRaisesRegex(Refusal,'CONTENT_PIN'): checked_read(p,raw_id(b'original'))
    def test_exact_cap_sentinel(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x'
            for raw in (b'abc',b'abcd',b'abcde'):
                p.write_bytes(raw)
                if len(raw)==3:self.assertEqual(checked_read(p,raw_id(b'abc')),b'abc')
                else:
                    with self.assertRaisesRegex(Refusal,'CONTENT_PIN'):checked_read(p,raw_id(b'abc'))
    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x';p.write_bytes(b'a');q=Path(d)/'q';q.symlink_to(p)
            with self.assertRaisesRegex(Refusal,'REGULAR'):checked_read(q,raw_id(b'a'))
    def test_bool_length_refused(self):
        with self.assertRaisesRegex(Refusal,'PIN_SIZE'):checked_read(Path('/missing'),{'bytes':True,'sha256':'0'*64})
    def test_maximum_length(self):
        with self.assertRaisesRegex(Refusal,'PIN_SIZE'):checked_read(Path('/missing'),{'bytes':64000001,'sha256':'0'*64})
    def test_adapter_pins(self):
        self.assertEqual(set(adapter_sources()),{'custody.py','worker.py','ocm_route.py','qualify.py','SOURCE_PINS.json'})
    def test_audit_empty_population(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'RUN.json').write_bytes(encoded({'plan':[]}))
            with self.assertRaisesRegex(Refusal,'COMPLETE_ORDERED'):qualify.audit(p)
    def test_audit_truncated_population(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'RUN.json').write_bytes(encoded({'plan':list(qualify.PLAN[:-1])}))
            with self.assertRaisesRegex(Refusal,'COMPLETE_ORDERED'):qualify.audit(p)
    def test_audit_duplicate_population(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'RUN.json').write_bytes(encoded({'plan':[qualify.PLAN[0]]*9}))
            with self.assertRaisesRegex(Refusal,'COMPLETE_ORDERED'):qualify.audit(p)

class BridgeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.GL,cls.GS,cls.GN,cls.F,cls.manifest=load_bridge(Path(cls.tmp.name)/'runtime', include_fixture=True)
        cls.guard=patch.object(cls.GN.N,'verify',side_effect=AssertionError('NATIVE_FORBIDDEN_IN_UNIT_CONTROLS'))
        cls.native=cls.guard.start()
    @classmethod
    def tearDownClass(cls):
        cls.native.assert_not_called();cls.guard.stop();cls.tmp.cleanup()
    def setUp(self):
        self.bundle=self.F.bundle();self.library=self.F.restore(self.bundle);self.task=self.F.task()
        self.p={'task':self.task,'bundle':{n:raw_id(b'') for n in ('base.mm','joined.mm','manifest.json','qualification.json')},
                'state_binding':raw_id(b'{}'),'lease':{}}
    def result(self,mode='enabled',task=None):return self.GS.solve(task or self.task,self.library,mode)
    def test_goal_only_keys(self):
        for field in ('proof','trace','target_label','expected_labels'):
            t=copy.deepcopy(self.task);t[field]=['hint'];r=self.result(task=t)
            with self.subTest(field=field):self.assertEqual(r['terminal'],'UNKNOWN')
    def test_outer_oracle_field(self):
        r=qualify.request(self.p,'enabled','ordinary');r['official_proof']=[]
        with self.assertRaisesRegex(Refusal,'REQUEST_FIELDS'):validate_request(r)
    def test_request_modes(self):
        for mode in ('enabled','resident-disabled','restored'):
            validate_request(qualify.request(self.p,mode,'ordinary'))
    def test_bad_mode(self):
        r=qualify.request(self.p,'disabled-but-hinted','ordinary')
        with self.assertRaisesRegex(Refusal,'REQUEST_MODE'):validate_request(r)
    def test_nonce(self):
        r=qualify.request(self.p,'enabled','ordinary');r['nonce']='same-invocation'
        with self.assertRaisesRegex(Refusal,'NONCE'):validate_request(r)
    def test_route_state(self):
        r=qualify.request(self.p,'enabled','ordinary');r['state']={}
        with self.assertRaisesRegex(Refusal,'REQUEST_STATE'):validate_request(r)
    def test_preloaded_bridge(self):
        with self.assertRaisesRegex(Refusal,'PRELOADED'):load_bridge(Path(self.tmp.name)/'forbidden')
    def test_bundle_extra(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bundle';pins=write_bundle(p,self.bundle);(p/'hint.json').write_bytes(b'[]')
            with self.assertRaisesRegex(Refusal,'EXTRA_OR_MISSING'):read_bundle(p,pins,self.GL)
    def test_bundle_missing(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bundle';pins=write_bundle(p,self.bundle);(p/'joined.mm').unlink()
            with self.assertRaisesRegex(Refusal,'EXTRA_OR_MISSING'):read_bundle(p,pins,self.GL)
    def test_bundle_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bundle';pins=write_bundle(p,self.bundle);(p/'joined.mm').write_bytes(b'changed')
            with self.assertRaisesRegex(Refusal,'CONTENT_PIN'):read_bundle(p,pins,self.GL)
    def test_three_arms(self):
        rr=[self.result(mode) for mode in qualify.MODES]
        self.assertEqual([r['decision_count'] for r in rr],[1,2,1])
        for k in ('bank_identity','grounded_actions_identity','emission_syntax_identity'):
            self.assertEqual(rr[0][k],rr[1][k]);self.assertEqual(rr[1][k],rr[2][k])
    def test_bounded_failure_not_impossibility(self):
        t=copy.deepcopy(self.task);t['limits']['max_decisions']=1;r=self.result('resident-disabled',t)
        self.assertEqual(r['terminal'],'NO_PROOF_IN_REGISTERED_FINITE_BANK')
        self.assertIsNone(r['generated_proof']);self.assertFalse(r['native_acceptance'])
    def test_resource_limit_is_unknown(self):
        t=copy.deepcopy(self.task);t['limits']['max_instances']=1;r=self.result(task=t)
        self.assertEqual(r['terminal'],'UNKNOWN');self.assertFalse(r['native_acceptance'])
    def test_boolean_limit(self):
        t=copy.deepcopy(self.task);t['limits']['max_decisions']=True
        self.assertEqual(self.result(task=t)['terminal'],'UNKNOWN')
    def test_unsupported_context(self):
        t=copy.deepcopy(self.task);t['context']['dv']=[['ph','ps']]
        self.assertEqual(self.result(task=t)['terminal'],'UNKNOWN')
    def test_foreign_syntax(self):
        t=copy.deepcopy(self.task);t['query']=['|-','UNSUPPORTED']
        self.assertEqual(self.result(task=t)['terminal'],'UNKNOWN')
    def test_modified_packet_pin(self):
        r=self.result();pin=identity(r);r['generated_proof']=['learned-cut']
        with self.assertRaisesRegex(ValueError,'result pin'):self.GN.prepare(self.task,r,pin,self.library,'new-goal',['new-h'])
    def test_changed_goal(self):
        r=self.result();t=copy.deepcopy(self.task);t['query']=['|-','ph']
        with self.assertRaisesRegex(ValueError,'goal/library'):self.GN.prepare(t,r,identity(r),self.library,'new-goal',['new-h'])
    def test_target_shortcut(self):
        r=self.result()
        with self.assertRaisesRegex(ValueError,'shortcut'):self.GN.prepare(self.task,r,identity(r),self.library,'learned-cut',['new-h'])
    def test_disabled_proof_relabel(self):
        r=self.result();r['mode']='resident-disabled'
        with self.assertRaisesRegex(ValueError,'disabled cohort'):self.GN.prepare(self.task,r,identity(r),self.library,'new-goal',['new-h'])
    def test_wrong_hole_count(self):
        r=self.result()
        with self.assertRaisesRegex(ValueError,'hole count'):self.GN.prepare(self.task,r,identity(r),self.library,'new-goal',[])
    def test_synthetic_flag_not_native_authority(self):
        r=self.result();r['native_acceptance']=True
        with self.assertRaisesRegex(ValueError,'generated result'):self.GN.prepare(self.task,r,identity(r),self.library,'new-goal',['new-h'])
    def test_native_sources_before_entry(self):
        r=self.result()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);prefix=p/'prefix';prefix.write_bytes(self.bundle['joined'])
            n=self.GN.execute(self.task,r,identity(r),self.library,'new-goal',['new-h'],prefix,p/'native',
                              {'index':{'path':str(prefix),**raw_id(b'wrong')}})
            self.assertEqual(n['terminal'],'CANNOT_CHECK');self.assertEqual(n['native_calls'],0)
    def runtime(self,d):
        import ocm_route as R
        root=Path(d)/'state';source=execution_identity(self.manifest);pins=self.p['bundle']
        binding=R.produce(root,pins,source)
        request=qualify.request({**self.p,'state_binding':identity(binding)},'enabled','ocm',binding['initial_lease'])
        return R,root,source,binding,request
    def test_stale_runtime_lease(self):
        with tempfile.TemporaryDirectory() as d:
            R,root,src,binding,r=self.runtime(d);r['state']['lease']['head']='stale'
            with self.assertRaisesRegex(Refusal,'STALE_OCM_LEASE'):
                R.solve(root,binding,r,self.library,src,lambda:self.fail('dispatched'),lambda x:self.fail('checked'))
    def test_disabled_mode_requires_revocation(self):
        with tempfile.TemporaryDirectory() as d:
            R,root,src,binding,r=self.runtime(d);r['mode']='resident-disabled'
            with self.assertRaisesRegex(Refusal,'MODE_LIVENESS'):
                R.solve(root,binding,r,self.library,src,lambda:self.fail('dispatched'),lambda x:self.fail('checked'))
    def test_runtime_bundle_binding(self):
        with tempfile.TemporaryDirectory() as d:
            R,root,src,binding,r=self.runtime(d);r['bundle']={}
            with self.assertRaisesRegex(Refusal,'SOURCE_OR_BUNDLE'):
                R.solve(root,binding,r,self.library,src,lambda:self.fail('dispatched'),lambda x:self.fail('checked'))
    def test_revoked_environment(self):
        with tempfile.TemporaryDirectory() as d:
            R,root,src,binding,r=self.runtime(d);rt=R.OCMRuntime(root);rt.revoke([binding['environment']]);rt.persist()
            r['state']['lease']=R.lease(rt)
            with self.assertRaisesRegex(Refusal,'ENVIRONMENT_NOT_LIVE'):
                R.solve(root,binding,r,self.library,src,lambda:self.fail('dispatched'),lambda x:self.fail('checked'))
    def test_runtime_unknown_withheld(self):
        with tempfile.TemporaryDirectory() as d:
            R,root,src,binding,r=self.runtime(d)
            answer=R.solve(root,binding,r,self.library,src,lambda:{'terminal':'UNKNOWN'},lambda x:self.fail('checked'))
            self.assertFalse(answer['committed']);self.assertIsNone(answer['native'])
    def test_native_refusal_withheld(self):
        with tempfile.TemporaryDirectory() as d:
            R,root,src,binding,r=self.runtime(d)
            answer=R.solve(root,binding,r,self.library,src,self.result,lambda x:{'terminal':'CANNOT_CHECK','native_calls':0})
            self.assertFalse(answer['committed'])
    def test_bound_check_double_support(self):
        # Explicit double tests the OCM commitment dependency, NOT mathematical validity.
        with tempfile.TemporaryDirectory() as d:
            R,root,src,binding,r=self.runtime(d)
            answer=R.solve(root,binding,r,self.library,src,self.result,
                          lambda x:{'terminal':'GENERATED_PROOF_NATIVE_VERIFIED','selected_cohort_labels':['learned-cut'],'native_calls':0})
            self.assertTrue(answer['committed']);self.assertIn(binding['method'],answer['answer_support'])
            self.assertIn(repr(binding['method']),answer['trace']['stages'][-1]['evidence_ids'])
    def test_revoke_restore_state(self):
        with tempfile.TemporaryDirectory() as d:
            R,root,src,binding,r=self.runtime(d)
            dead=R.revise(root,binding,r['bundle'],src,r['state']['lease'],'revoke')
            self.assertEqual(dead['method_liveness'],'DEAD')
            live=R.revise(root,binding,r['bundle'],src,dead['lease'],'reinstate')
            self.assertEqual(live['method_liveness'],'LIVE')

if __name__ == '__main__':unittest.main(verbosity=2)
