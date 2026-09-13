"""Scope-refuting and independent complete-policy controls."""
import sys
import unittest
from pathlib import Path
from dataclasses import replace
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hierarchy_v1 import Register,solve
from event_executor_v1 import replay_events
from parsing_v1 import parse
from witnesses_v1 import hierarchy_witness,policy_census,parsing_census,parsing_controls
from source_evidence_v1 import source_controls


class HierarchyTests(unittest.TestCase):
    def setUp(self):
        self.r=Register(('a',),(3,), (('a',),(0,0)),(1,1),(1,1),(0,0))

    def test_actual_nested_first_acquisition_and_full_lifecycle(self):
        got=hierarchy_witness()
        self.assertEqual([got['runs'][n]['cost'] for n in ('fresh','lower_only','both')],[3060,3032,1233])
        self.assertGreater(got['second_gain'],got['first_gain'])
        self.assertEqual([got['runs'][n]['reconstruction_cost'] for n in ('fresh','lower_only','both')],[3030,3002,1203])
        self.assertEqual([got['runs'][n]['delivery_cost'] for n in ('fresh','lower_only','both')],[30,30,30])
        self.assertEqual(sum(got['admission_price_per_artifact'].values()),1)
        self.assertEqual(got['materialized_execution']['both']['artifacts'],{0:'a',1:'a'*10})
        self.assertEqual(got['materialized_execution']['both']['output'],'a'*30)

    def test_one_use_does_not_omit_first_derivation(self):
        r=Register(('a',),(3,), (('a',),),(1,),(1,),(0,))
        got=solve(r,(0,),(0,))
        self.assertEqual(got['cost'],3)
        self.assertEqual(got['final_costs'],{0:3,1:4})

    def test_delayed_or_refused_admission_remains_admitted(self):
        r=replace(self.r,admission=(100,100))
        self.assertEqual(solve(r,(1,1),(0,1))['final_mask'],0)
        self.assertEqual(solve(r,(1,1),(0,1))['cost'],12)

    def test_rederivation_can_beat_retained_invocation(self):
        r=Register(('a',),(1,), (('a',),),(0,),(9,),(0,))
        got=solve(r,(0,0),(0,))
        self.assertEqual(got['final_costs'][1],2)
        self.assertEqual(got['cost'],2)

    def test_exact_zero_prices_and_empty_workload(self):
        r=replace(self.r,costs=(0,),admission=(0,0),invocation=(0,0))
        self.assertEqual(solve(r,(1,1),(0,1))['cost'],0)
        self.assertEqual(solve(r,(),(0,1))['events'],())

    def test_dispatch_is_charged_even_without_retention(self):
        r=replace(self.r,dispatch=(2,5))
        self.assertEqual(solve(r,(1,),())['cost'],15)
        self.assertEqual(solve(self.r,(1,),())['cost'],6)

    def test_missing_first_charge_and_unacquired_call_reject(self):
        got=solve(self.r,(1,1),(0,1));events=got['events']
        with self.assertRaises(ValueError):replay_events(self.r,(1,1),(0,1),events[1:])
        with self.assertRaises(ValueError):replay_events(self.r,(1,),(0,1),(('invoke',1,F(1)),))
        altered=tuple((k,t,F(0) if k=='primitive' else c) for k,t,c in events)
        with self.assertRaises(ValueError):replay_events(self.r,(1,1),(0,1),altered)

    def test_forward_cycle_unknown_boolean_references_reject(self):
        for bodies in (((0,),),((True,),),(('z',),), ((),)):
            with self.assertRaises(ValueError):
                Register(('a',),(1,),bodies,(1,),(1,),(0,))

    def test_inexact_negative_prices_and_unknown_workload_reject(self):
        for x in (-1,1.0,True,float('inf')):
            with self.assertRaises(ValueError):replace(self.r,costs=(x,))
        with self.assertRaises(ValueError):solve(self.r,('z',),(0,))
        with self.assertRaises(ValueError):solve(self.r,(1,),(2,))

    def test_complete_policy_oracle_final_masks(self):
        got=policy_census()
        self.assertEqual(got['complete_register_class_cases'],384)
        self.assertEqual(got['complete_executions'],3456)

    def test_nested_allowed_classes_are_monotone(self):
        for h in range(1,5):
            a,b,c=[solve(self.r,(1,)*h,k)['cost'] for k in ((),(0,),(0,1))]
            self.assertGreaterEqual(a,b);self.assertGreaterEqual(b,c)

    def test_greedy_and_overlap_countermodels(self):
        got=parsing_controls()
        self.assertEqual(got['greedy_countermodel']['cost'],2)
        self.assertEqual(got['maximum_realized_calls'],1)
        self.assertEqual(source_controls()['source_greedy'],3)
        self.assertEqual(source_controls()['source_one_request_cost'],2)

    def test_complete_parse_oracle(self):
        got=parsing_census()
        self.assertEqual(got['word_dictionary_cases'],1008)
        self.assertEqual(got['complete_parses'],3136)

    def test_empty_chunk_and_incomplete_alphabet_reject(self):
        with self.assertRaises(ValueError):parse('a',{'a':1},{'':0})
        with self.assertRaises(ValueError):parse('z',{'a':1},{})
        self.assertEqual(parse('',{}, {})['cost'],0)

    def test_positive_delivery_is_charged_for_compiled_and_fresh(self):
        r=replace(self.r,delivery=(7,))
        for allowed in ((),(0,),(0,1)):
            got=solve(r,(1,1),allowed)
            self.assertEqual(got['delivery_cost'],28)
            actual=replay_events(r,(1,1),allowed,got['events'])
            self.assertEqual(actual['delivery_charge'],28)
            self.assertEqual(actual['total'],got['cost'])

    def test_same_trace_does_not_determine_factoring(self):
        a=Register(tuple('abcde'),(1,)*5,(('a','b'),('c','d','e')),(1,1),(1,1),(0,0))
        b=Register(tuple('abcde'),(1,)*5,(('a','b','c'),('d','e')),(1,1),(1,1),(0,0))
        self.assertEqual(''.join(a.expansion(x) for x in (0,1)),''.join(b.expansion(x) for x in (0,1)))
        self.assertNotEqual(a.bodies,b.bodies)


if __name__=='__main__':unittest.main()
