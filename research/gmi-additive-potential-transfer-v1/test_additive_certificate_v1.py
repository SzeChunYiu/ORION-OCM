import sys
import unittest
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parent))
from finite_model_v1 import model
from additive_certificate_v1 import certify,survival_bound
from finite_witnesses_v1 import (embedded_wtt,history_control,selected_control,terminal_control)
from transfer_oracle_v1 import stationary,best_stationary

class CertificateTests(unittest.TestCase):
    def test_positive_history_values_and_wtt_embedding(self):
        row=history_control()
        self.assertEqual(row["history_policies"],128)
        self.assertEqual(row["model_executions"],256)
        self.assertGreater(row["maximum_cost_error"],0)
        self.assertEqual(row["certificate"]["cost_error"],F(1,2)/F(1,2)+
                         2*F(1,4)/F(1,2)**2)

    def test_zero_cost_loop_requires_independent_duration_certificate(self):
        loop=model([[(1,0,0)]],[(0,)])
        with self.assertRaisesRegex(ValueError,"duration"):
            certify([loop],loop,(1,0,0),(0,0,0),(0,0,0),((0,),),(1,0,0))

    def test_unseen_row_cannot_be_omitted(self):
        nominal=model([[(0,0,1,0)],[(0,1,0,0)]],[(0,),(0,)])
        truth=model([[(0,F(1,4),F(3,4),0)],[(0,1,0,0)]],[(0,),(0,)])
        with self.assertRaisesRegex(ValueError,"duration"):
            certify([truth],nominal,(2,4,0,0),(0,0,0,0),(0,0,0,0),
                    ((0,),(0,)),(1,0,0,0))

    def test_understated_error_or_reserve_rejected(self):
        q,p,args=embedded_wtt()
        for key,value in (("r",((0,0),(0,0))),("B",(0,0,0,0))):
            bad=dict(args)
            bad[key]=value
            with self.assertRaises(ValueError):
                certify([p],q,**bad)

    def test_changed_charge_requires_error_charge(self):
        q=model([[(0,1,0)]],[(1,)])
        p=model([[(0,1,0)]],[(2,)])
        good=certify([p],q,(1,0,0),(2,0,0),(1,0,0),((1,),),(1,0,0))
        self.assertEqual(good["cost_error"],1)
        self.assertEqual(stationary(p,(0,))["cost"][0]-stationary(q,(0,))["cost"][0],1)
        with self.assertRaises(ValueError):
            certify([p],q,(1,0,0),(2,0,0),(1,0,0),((0,),),(1,0,0))

    def test_work_envelope_is_independent_obligation(self):
        m=model([[(0,1,0)]],[(2,)])
        with self.assertRaises(ValueError):
            certify([m],m,(1,0,0),(1,0,0),(0,0,0),((0,),),(1,0,0))

    def test_terminal_potential_is_optional_not_zero_error(self):
        row=terminal_control()
        self.assertEqual(row["cost_error"],0)
        self.assertEqual(row["event_bound"],1)
        self.assertEqual(row["without_A"],"NOT_CERTIFIED")

    def test_terminal_event_reserve_and_tv_must_both_hold(self):
        q=model([[(0,1,0)]],[(0,)])
        p=model([[(0,0,1)]],[(0,)])
        for A,eps in (((0,0,0),((1,),)),((1,0,0),((0,),))):
            with self.assertRaises(ValueError):
                certify([p],q,(1,0,0),(0,0,0),(0,0,0),((0,),),(1,0,0),
                        A=A,epsilon=eps)

    def test_potentials_nonnegative_zero_terminal_and_finite(self):
        q,p,args=embedded_wtt()
        for key,value in (("V",(4,-1,0,0)),("B",(3,6,1,0)),("A",(0.5,1,0,0))):
            bad=dict(args)
            bad[key]=value
            with self.assertRaises(ValueError):
                certify([p],q,**bad)

    def test_nominal_and_initial_contracts(self):
        q,p,args=embedded_wtt()
        for bad in ({**args,"initial":(0,0,0,0)},{**args,"epsilon":None}):
            with self.assertRaises(ValueError):
                certify([p],q,**bad)
        with self.assertRaises(ValueError):
            certify([],q,**args)
        with self.assertRaises(ValueError):
            model([[(0.5,0.5,0)]],[(1,)])

    def test_rowwise_convex_mixture_no_alarm(self):
        q,p,args=embedded_wtt()
        middle=model([[[F(1,3)*a+F(2,3)*b for a,b in zip(qr,pr)]
                      for qr,pr in zip(qs,ps)] for qs,ps in zip(q.rows,p.rows)],
                     [[F(1,3)*a+F(2,3)*b for a,b in zip(qc,pc)]
                      for qc,pc in zip(q.charges,p.charges)])
        cert=certify([middle],q,**args)
        self.assertGreaterEqual(min(cert["minimum_slacks"].values()),0)

    def test_transition_charge_hull_requires_joint_coefficients(self):
        q=model([[(0,1,0)]],[(1,)])
        p=model([[(F(1,2),F(1,2),0)]],[(F(1,2),)])
        mixed=model([[(F(1,4),F(3,4),0)]],[(F(3,4),)])
        args=((2,0,0),(1,0,0),(2,0,0),((1,),),(1,0,0))
        certify([p,mixed],q,*args)
        self.assertEqual(stationary(mixed,(0,))["cost"][0],1)
        hybrid=model(p.rows,[(1,)])
        self.assertEqual(stationary(hybrid,(0,))["cost"][0],2)
        with self.assertRaises(ValueError):
            certify([hybrid],q,*args)

    def test_same_data_selected_policy_and_charged_fees(self):
        row=selected_control()
        self.assertEqual(row["selected_actions"],[0,1])
        self.assertEqual(row["fee_aware_action"],1)

    def test_restricted_class_is_not_global_comparator(self):
        m=model([[(0,1,0),(0,1,0)]],[(0,1)])
        restricted=stationary(m,(1,))["cost"][0]
        _,global_best=best_stationary(m)
        self.assertEqual((restricted,global_best),(1,0))
        self.assertGreater(restricted,global_best)  # zero model error does not close this gap

    def test_common_kernel_contains_observed_charge_signal(self):
        terminal=(0,0,0,0,1,0)
        q=model([[(0,0,1,0,0,0)]]+[[terminal,terminal]]*3,
                [(1,),(0,10),(0,10),(0,10)])
        p=model([[(0,F(1,2),0,F(1,2),0,0)]]+[[terminal,terminal]]*3,
                [(1,),(0,10),(0,10),(0,10)])
        cert=certify([p],q,(2,1,1,1,0,0),(11,10,10,10,0,0),(20,0,0,0,0,0),
                     ((20,),(0,0),(0,0),(0,0)),(1,0,0,0,0,0))
        values=[stationary(m,(0,0,1,0))["cost"][0] for m in (q,p)]
        self.assertEqual(values,[11,1])
        self.assertLessEqual(abs(values[0]-values[1]),cert["cost_error"])

    def test_coverage_certification_and_data_average_are_distinct(self):
        # E has probability9/10; F selects exactly its complement.
        rows=[(F(9,10),True,False),(F(1,10),False,True)]
        both=sum(p for p,e,f in rows if e and f)
        self.assertEqual(both,0)
        self.assertEqual(sum(p for p,e,f in rows if f),F(1,10))
        self.assertEqual(sum(F(1,2**n)*2**n for n in range(1,9)),8)

    def test_mixed_initial_law_including_already_stopped_mass(self):
        q,p,args=embedded_wtt()
        args["initial"]=(F(1,4),F(1,4),F(1,2),0)
        cert=certify([p],q,**args)
        values=[stationary(m,(0,1))["cost"] for m in (q,p)]
        costs=[sum(value)/4 for value in values]
        self.assertEqual(cert["expected_steps"],F(3,2))
        self.assertEqual(cert["expected_cost"],3)
        self.assertEqual(cert["cost_error"],F(9,4))
        self.assertLessEqual(abs(costs[0]-costs[1]),cert["cost_error"])

    def test_survival_bound_is_not_a_deterministic_deadline(self):
        q,p,args=embedded_wtt()
        cert=certify([p],q,**args)
        self.assertEqual(survival_bound(cert,7),F(1,4))
        with self.assertRaises(ValueError):
            survival_bound(cert,-1)

if __name__=="__main__":
    unittest.main()
