"""Finite/exact controls and hostile inputs, not independent protected evaluation."""
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from itertools import product
import copy
import tempfile
import unittest
import mechanisms as X
import runtime_bridge as R

SOURCE='a'*64


class FailureCertificates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope=X.MethodScope(source=SOURCE)
        cls.attempt=X.prefix_search((1,1),cls.scope,'test:actual-failure')
        cls.guard=X.learn_guard(cls.attempt)

    def test_actual_failure_is_not_impossibility(self):
        self.assertEqual(self.attempt['checked_programs'],21)
        self.assertEqual(self.attempt['terminal'],'BOUNDED_METHOD_EXHAUSTED')
        self.assertIs(self.attempt['task_impossibility'],False)
        self.assertEqual(X.primitive_search((1,1))['terminal'],'VERIFIED_POLYNOMIAL_IDENTITY')

    def test_certificate_independent_complete_enumeration(self):
        self.assertEqual(X.validate_guard(self.guard,self.attempt),21)
        self.assertEqual(self.guard['feature'],'degree')

    def test_new_goals_not_task_blacklist(self):
        for target in ((3,1),(-4,2),(7,0,1)):
            self.assertNotEqual(X.wire(target),self.attempt['target'])
            self.assertTrue(X.guard_applies(self.guard,target,self.scope))
        self.assertNotIn('target',self.guard)
        self.assertNotIn('task_id',self.guard)

    def test_success_outside_scope(self):
        target=X.M.normal_form(X.MACRO)
        row=X.solve_with_guard(target,self.scope,self.guard,'test:success')
        self.assertIsNone(row['guard_consumed'])
        self.assertTrue(row['method_used'])
        self.assertEqual(row['prefix_checks'],1)

    def test_budget_change_reopens(self):
        target=X.M.normal_form(X.MACRO+('inc',)*3)
        failed=X.prefix_search(target,self.scope,'test:budget');guard=X.learn_guard(failed)
        self.assertIsNotNone(guard)
        self.assertTrue(X.guard_applies(guard,target,self.scope))
        changed=replace(self.scope,max_length=6)
        self.assertFalse(X.guard_applies(guard,target,changed))
        result=X.prefix_search(target,changed,'test:larger-budget')
        self.assertEqual(result['terminal'],'VERIFIED_POLYNOMIAL_IDENTITY')

    def test_environment_change_reopens(self):
        self.assertFalse(X.guard_applies(self.guard,(1,1),replace(self.scope,environment='new-version')))

    def test_method_and_grammar_and_budget_and_source_changes_reopen(self):
        for changed in (replace(self.scope,prefix=('inc',)),replace(self.scope,grammar=tuple(reversed(self.scope.grammar))),
                        replace(self.scope,attempts=100),replace(self.scope,source='b'*64)):
            self.assertFalse(X.guard_applies(self.guard,(1,1),changed))

    def test_exact_cap_and_cap_minus_one(self):
        full=X.prefix_search((1,1),replace(self.scope,attempts=21),'test:cap')
        cut=X.prefix_search((1,1),replace(self.scope,attempts=20),'test:cut')
        self.assertEqual(full['terminal'],'BOUNDED_METHOD_EXHAUSTED')
        self.assertEqual(cut['terminal'],'RESOURCE_BOUND')
        self.assertIsNone(X.learn_guard(cut))
        X.validate_attempt(full);X.validate_attempt(cut)

    def test_winner_cannot_be_failure_memory(self):
        success=X.prefix_search(X.M.normal_form(X.MACRO),self.scope,'test:winner')
        self.assertIsNone(X.learn_guard(success))

    def test_truncated_evidence_rejected(self):
        bad=copy.deepcopy(self.attempt);bad['visited'].pop();bad['checked_programs']-=1
        with self.assertRaises(ValueError):X.validate_guard(self.guard,bad)

    def test_duplicated_evidence_rejected(self):
        bad=copy.deepcopy(self.attempt);bad['visited'][-1]=bad['visited'][0]
        with self.assertRaises(ValueError):X.validate_attempt(bad)

    def test_forged_polynomial_rejected(self):
        bad=copy.deepcopy(self.attempt);bad['visited'][0]['coefficients']=['999']
        with self.assertRaises(ValueError):X.validate_attempt(bad)

    def test_forged_guard_range_rejected(self):
        bad=copy.deepcopy(self.guard);bad['reachable_values']=[]
        with self.assertRaises(ValueError):X.validate_guard(bad,self.attempt)

    def test_scope_laundering_rejected(self):
        bad=copy.deepcopy(self.guard);bad['scope']['max_length']=6
        with self.assertRaises(ValueError):X.validate_guard(bad,self.attempt)

    def test_attempt_boolean_count_rejected(self):
        bad=copy.deepcopy(self.attempt);bad['checked_programs']=True
        with self.assertRaises(ValueError):X.validate_attempt(bad)

    def test_relabelled_occurrence_does_not_change_search(self):
        a=X.prefix_search((1,1),self.scope,'label-A');b=X.prefix_search((1,1),self.scope,'label-B')
        self.assertEqual(a['visited'],b['visited'])
        self.assertEqual(X.learn_guard(a)['reachable_values'],X.learn_guard(b)['reachable_values'])

    def test_no_generalization_when_feature_absence_unavailable(self):
        # Failures must not silently become task-identity guards when no feature separates.
        record=X.prefix_search((1,1),replace(self.scope,attempts=1),'test:unresolved')
        self.assertIsNone(X.learn_guard(record))

    def test_import_really_is_recorded_acquired_macro(self):
        method=X.recover_method()
        self.assertEqual(method['macro'],list(X.MACRO))
        self.assertEqual(method['source_result'],X.RECORDED_RESULT)
        self.assertIs(method['historical_acquisition_paid_back'],False)


class AlgebraAndRepresentations(unittest.TestCase):
    def test_incremental_semantics_matches_existing_checker_exhaustively(self):
        for p,poly in X.all_states(4):
            self.assertEqual(poly,X.M.normal_form(p))
            self.assertTrue(X.scalar_check(p,poly))

    def test_scalar_checker_detects_wrong_coefficient(self):
        self.assertFalse(X.scalar_check(('square',),(1,0,1)))
        self.assertFalse(X.scalar_check(('foreign',),(0,1)))

    def test_two_coarse_representations_fit_same_training(self):
        ps=(('inc','dec'),('dec','inc'),('double','inc','dec'),('double','dec','inc'))
        states=[(p,X.M.normal_form(p)) for p in ps]
        for name in X.REPRESENTATIONS:
            self.assertTrue(X.validate_representation(name,'coefficients',3,states)['valid'])

    def test_misleading_training_fit_rejected_by_counterexamples(self):
        for name in ('value0','value01'):
            trial=X.validate_representation(name,'coefficients',4)
            self.assertFalse(trial['valid']);self.assertIsNotNone(trial['witness'])

    def test_full_coefficients_preserve_declared_transition_contract(self):
        result=X.validate_representation('coefficients','coefficients',5)
        self.assertTrue(result['valid'])
        self.assertGreater(result['comparisons'],0)
        self.assertGreater(result['transition_checks'],0)

    def test_new_observer_breaks_old_quotient(self):
        old=X.select_representation('coefficients',4)
        self.assertEqual(old['name'],'coefficients')
        with self.assertRaises(ValueError):X.validate_representation_certificate(old,'coefficients-last',4)
        changed=X.select_representation('coefficients-last',4)
        self.assertEqual(changed['name'],'coefficients-last')

    def test_remaining_budget_is_not_discarded(self):
        p=();q=('inc','dec');poly=(Fraction(0),Fraction(1))
        self.assertNotEqual(X.representation_key(p,poly,'coefficients'),X.representation_key(q,poly,'coefficients'))

    def test_order_and_inventory_binding(self):
        cert=X.select_representation('coefficients',3);cert['grammar'].reverse()
        with self.assertRaises(ValueError):X.validate_representation_certificate(cert,'coefficients',3)

    def test_raw_and_quotient_shortest_answers_exhaustive_small_scope(self):
        targets={poly for _,poly in X.all_states(3)}
        for target in targets:
            a=X.primitive_search(target,3);b=X.primitive_search(target,3,'coefficients')
            self.assertEqual(a['terminal'],b['terminal']);self.assertEqual(a['program'],b['program'])
            self.assertLessEqual(b['checked_programs'],a['checked_programs'])

    def test_bounded_absence_is_not_timeout(self):
        missing=(Fraction(1,3),Fraction(1))
        self.assertEqual(X.primitive_search(missing,2)['terminal'],'EXHAUSTED_DECLARED_GRAMMAR')
        self.assertEqual(X.primitive_search(missing,2,max_checks=1)['terminal'],'RESOURCE_BOUND')

    def test_timeout_diagnosis_never_jump(self):
        scope=X.MethodScope(source=SOURCE,attempts=1)
        attempt=X.prefix_search((1,1),scope,'test:resource')
        self.assertEqual(X.diagnose({'kind':'attempt','attempt':attempt})['terminal'],'RESOURCE_BOUND')
        self.assertEqual(X.diagnose({'kind':'unknown'})['terminal'],'CANNOT_CHECK')

    def test_alias_diagnosis_requires_actual_distinction(self):
        packet={'kind':'representation','left':['inc','dec'],'right':['dec','inc'],
                'representation':'coefficients','observer':'coefficients-last','bound':2}
        self.assertEqual(X.diagnose(packet)['terminal'],'REPRESENTATION_INSUFFICIENT')
        packet['observer']='coefficients'
        with self.assertRaises(ValueError):X.diagnose(packet)

    def test_strict_json(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json'
            for raw in ('{"a":1,"a":2}','{"a":NaN}'):
                p.write_text(raw)
                with self.assertRaises(ValueError):X.read_json(p)

    def test_scope_rejects_malformed_contracts(self):
        for kwargs in ({'attempts':True},{'max_length':True},{'grammar':('inc','inc')},
                       {'prefix':('bad',)},{'source':'bad'},{'environment':''}):
            args={'source':SOURCE,**kwargs}
            with self.assertRaises(ValueError):X.MethodScope(**args)


class RuntimeControls(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'runtime'
        self.binding,self.rt=R.install(self.root,SOURCE)
    def tearDown(self):self.tmp.cleanup()

    def test_guard_persists_revokes_restores_without_logical_nogood(self):
        binding,_=R.acquire_failure(self.rt,self.binding);expected=R.lease(self.rt)
        rt=R.load(self.root,binding,SOURCE,expected);g,n=R.active_guard(rt,binding)
        self.assertIsNotNone(g);self.assertEqual(n,21)
        before=rt.state.nogoods.as_dict()
        revoked=R.change_guard_permission(rt,binding,False)
        self.assertEqual(revoked['guard_liveness'],'DEAD')
        self.assertEqual(revoked['method_liveness'],'LIVE')
        self.assertEqual(before,rt.state.nogoods.as_dict())
        rt=R.load(self.root,binding,SOURCE,R.lease(rt))
        self.assertIsNone(R.active_guard(rt,binding)[0])
        restored=R.change_guard_permission(rt,binding,True)
        self.assertEqual(restored['guard_liveness'],'LIVE')

    def test_stale_state_and_source_rejected(self):
        expected=R.lease(self.rt)
        with self.assertRaises(ValueError):R.load(self.root,self.binding,'b'*64,expected)
        self.rt.persist()
        with self.assertRaises(ValueError):R.load(self.root,self.binding,SOURCE,expected)

    def test_actual_check_commit_and_support(self):
        target={'coefficients':['1','1'],'identity':X.digest(['1','1']),'minimum_length':1}
        def generate():return {'rows':[{'target':target['identity'],'result':X.primitive_search((1,1))}]}
        result=R.commit_batch(self.rt,self.binding,'unit-valid',[target],generate)
        self.assertTrue(result['committed'],result)
        self.assertEqual(result['verified_goals'],1)
        self.assertIn(self.binding['environment'],result['answer_support'])
        self.assertNotIn(self.binding['method_permission'],result['answer_support'])

    def test_wrong_proof_is_not_committed(self):
        target={'coefficients':['1','1'],'identity':X.digest(['1','1']),'minimum_length':1}
        def generate():return {'rows':[{'target':target['identity'],'result':{'terminal':'VERIFIED_POLYNOMIAL_IDENTITY','program':['dec']}}]}
        result=R.commit_batch(self.rt,self.binding,'unit-wrong',[target],generate)
        self.assertFalse(result['committed'])

    def test_missing_population_not_committed(self):
        target={'coefficients':['1','1'],'identity':X.digest(['1','1']),'minimum_length':1}
        result=R.commit_batch(self.rt,self.binding,'unit-missing',[target],lambda:{'rows':[]})
        self.assertFalse(result['committed'])

    def test_duplicate_and_forged_task_identity_rejected(self):
        target={'coefficients':['1','1'],'identity':X.digest(['1','1']),'minimum_length':1}
        with self.assertRaises(ValueError):R.commit_batch(self.rt,self.binding,'unit-dup',[target,target],lambda:{'rows':[]})
        target['identity']='forged'
        with self.assertRaises(ValueError):R.commit_batch(self.rt,self.binding,'unit-id',[target],lambda:{'rows':[]})

    def test_representation_revision_uses_real_evidence(self):
        binding,r1=R.acquire_representation(self.rt,self.binding,'coefficients')
        rt=R.load(self.root,binding,SOURCE,R.lease(self.rt));self.assertEqual(R.active_representation(rt,binding)['name'],'coefficients')
        binding,r2=R.acquire_representation(rt,binding,'coefficients-last')
        self.assertEqual(r2['old_liveness'],'DEAD')
        self.assertEqual(r2['invalidation']['terminal'],'REPRESENTATION_INSUFFICIENT')
        self.assertEqual(R.active_representation(rt,binding)['name'],'coefficients-last')


if __name__=='__main__':unittest.main(verbosity=2)
