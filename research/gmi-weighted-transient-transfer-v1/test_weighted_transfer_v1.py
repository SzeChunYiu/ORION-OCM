import sys
import unittest
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parent))
from weighted_transfer_v1 import model,certificate,tails
from transfer_oracle_v1 import stationary,execute,trees,completed_cost
from transfer_witnesses_v1 import (pair,proper_error,trap_and_rescue,history_control,
    selected_policy_control,terminal_control,countable_control,observation_control,
    certification_control,controlled_models)

class TransferTests(unittest.TestCase):
    def test_unseen_trap_refused_and_paid_rescue_revives(self):
        result=trap_and_rescue()
        self.assertTrue(result["trap_refused"])
        self.assertEqual(result["rescue_cost"],F(7,4))
        self.assertEqual(result["rescue_steps"],F(5,4))

    def test_all_safe_finite_data_do_not_remove_trap(self):
        e=F(1,4)
        self.assertGreater((1-e)**20,0)
        # At H steps, cost is 1+e(H-1); positive survival e never decreases.
        charges=[1+e*(h-1) for h in (1,2,10,100)]
        self.assertEqual(charges,[1,F(5,4),F(13,4),F(103,4)])
        self.assertEqual(charges[-1]-charges[-2],90*e)

    def test_both_proper_cost_error_diverges(self):
        for e in (F(1,2),F(1,4),F(1,8)):
            row=proper_error(e)
            self.assertEqual(row["error"],1/e)
            self.assertEqual(row["true_cost"],1+1/e)

    def test_nonzero_geometric_tail_is_not_path_length_bound(self):
        m=model([[(F(1,2),F(1,2),0)]],[(1,)])
        cert=certificate([m],m,(1,),F(1,2),1,(1,0,0))
        self.assertEqual(stationary(m,(0,))["steps"],(F(2),))
        for h in (1,2,7):
            self.assertGreater(F(1,2)**h,0)
            self.assertEqual(tails(cert,h)["survival"],F(1,2)**h)

    def test_independent_history_cost_and_weighted_tails(self):
        result=history_control()
        self.assertEqual(result["history_policies"],128)
        self.assertEqual(result["exact_model_executions"],256)
        self.assertGreater(result["maximum_error"],0)

    def test_oracle_accounts_for_full_tail_not_just_prefix(self):
        q,p=controlled_models()
        node=trees(2,2,3)[0]
        prefix,leaves=execute(p,node)
        self.assertGreater(sum(leaves),0)
        self.assertGreater(completed_cost(p,node,(0,1)),prefix)

    def test_data_change_policy_and_fee_remains_payable(self):
        row=selected_policy_control()
        self.assertEqual(row["selected_actions"],[0,1])
        self.assertEqual(row["fee_aware_choice"],1)

    def test_terminal_labels_need_full_row_tv(self):
        row=terminal_control()
        self.assertEqual(row["killed_error"],0)
        self.assertEqual(row["actual_success_difference"],1)

    def test_observed_charge_is_part_of_complete_kernel(self):
        row=observation_control()
        self.assertEqual(row["costs"],[11,1])
        self.assertEqual(row["complete_signal_tv"],1)

    def test_coverage_does_not_imply_certification(self):
        row=certification_control()
        self.assertEqual(row["coverage_probability"],1)
        self.assertEqual(row["certification_probability"],0)

    def test_certification_can_select_confidence_failures(self):
        # Exact two-outcome data law: failure and certification coincide.
        outcomes=[(F(9,10),True,False),(F(1,10),False,True)]
        covered=sum(p for p,e,f in outcomes if e)
        certified=sum(p for p,e,f in outcomes if f)
        both=sum(p for p,e,f in outcomes if e and f)
        self.assertEqual((covered,certified,both),(F(9,10),F(1,10),0))
        self.assertEqual(both/certified,0)

    def test_pointwise_proper_is_not_data_averaged_integrability(self):
        for horizon in (1,2,8):
            partial=sum(F(1,2**n)*2**n for n in range(1,horizon+1))
            self.assertEqual(partial,horizon)
        self.assertEqual(sum(F(1,2**n) for n in range(1,9)),F(255,256))

    def test_charge_error_is_not_a_kernel_error(self):
        q=model([[(0,1,0)]],[(1,)])
        p=model([[(0,1,0)]],[(3,)])
        cert=certificate([p],q,(1,),0,3,(1,0,0))
        self.assertEqual(cert["eta"],0)
        self.assertEqual(cert["cost_error"],2)
        self.assertEqual(stationary(p,(0,))["cost"][0]-
                         stationary(q,(0,))["cost"][0],2)

    def test_small_tv_does_not_control_large_weighted_jump(self):
        e=F(1,1024)
        q,p=pair(e,F(1),rescue=True)
        # TV=e but the weighted difference equals 1 at s.
        cert=certificate([p],q,(2,1024),F(1,2),1,(1,0,0,0))
        self.assertEqual(cert["epsilon"],e)
        self.assertEqual(cert["eta"],F(1,2))
        self.assertGreater(cert["eta"],cert["epsilon"])

    def test_rowwise_convex_hull_no_alarm(self):
        q,p=controlled_models()
        mixed=model([[[F(1,3)*a+F(2,3)*b for a,b in zip(qr,pr)]
                      for qr,pr in zip(qs,ps)] for qs,ps in zip(q.rows,p.rows)],
                    [[F(1,3)*a+F(2,3)*b for a,b in zip(qc,pc)]
                     for qc,pc in zip(q.charges,p.charges)])
        outer=certificate([p],q,(1,2),F(1,2),2,(1,0,0,0))
        inner=certificate([mixed],q,(1,2),F(1,2),2,(1,0,0,0))
        for key in ("eta","zeta","epsilon","cost_error"):
            self.assertLessEqual(inner[key],outer[key])

    def test_countable_symbolic_contraction_coefficient(self):
        self.assertEqual(countable_control()["symbolic_worst_ratio"],F(7,8))

    def test_malformed_and_noncontractive_inputs_rejected(self):
        with self.assertRaises(ValueError):
            model([[(0.5,0.5,0)]],[(1,)])
        with self.assertRaises(ValueError):
            model([[(0,1,0)]],[(-1,)])
        q,_=pair(F(1,4),F(1),rescue=True)
        for weights,beta in [((1,1),1),((0,1),F(1,2))]:
            with self.assertRaises(ValueError):
                certificate([q],q,weights,beta,1,(1,0,0,0))
        with self.assertRaises(ValueError):
            certificate([],q,(1,1),F(1,2),1,(1,0,0,0))
        with self.assertRaises(ValueError):
            tails({"beta":F(1,2),"initial_weight":1,"ceiling":1},-1)

if __name__=="__main__":
    unittest.main()
