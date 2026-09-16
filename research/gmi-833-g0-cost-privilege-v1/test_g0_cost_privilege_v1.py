import json, pathlib, subprocess, sys, unittest
from fractions import Fraction
import importlib.util

ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("m",ROOT/"g0_cost_privilege_v1.py")
m=importlib.util.module_from_spec(spec); sys.modules["m"]=m; spec.loader.exec_module(m)
ospec=importlib.util.spec_from_file_location("o",ROOT/"independent_oracle_v1.py")
o=importlib.util.module_from_spec(ospec); sys.modules["o"]=o; ospec.loader.exec_module(o)

class T(unittest.TestCase):
    def test_base_valid(self): self.assertEqual(len(m.BASE),6)
    def test_label_certificate(self):
        c=m.label_blindness_certificate(); self.assertEqual(c["point_cost_checks"],180); self.assertEqual(c["failures"],0)
    def test_isometry_certificate(self): self.assertEqual(m.isometry_certificate()["name_isometries"],720)
    def test_structural_reversal(self):
        c=m.structural_bias_counterexample(); self.assertEqual(c["GA_selection"],["ALPHA"]); self.assertEqual(c["GB_selection"],["BETA"])
    def test_dominance(self): self.assertEqual(m.dominance_certificate()["dominance_violations"],0)
    def test_incomparable_reversal(self): self.assertTrue(m.dominance_certificate()["incomparable_reversal"])
    def test_family_leak(self): self.assertEqual(m.audit_family_adjustment({"F0":Fraction(0),"F1":Fraction(1),"F2":Fraction(0)}),"FAMILY_LABEL_COST_LEAK")
    def test_constant_label_adjustment_not_differential(self): self.assertEqual(m.audit_family_adjustment({"F0":Fraction(1),"F1":Fraction(1),"F2":Fraction(1)}),"NO_LABEL_ADJUSTMENT_LEAK")
    def test_zero_macro(self): self.assertEqual(m.audit_macro(m.BASE[0],(0,0)),"ZERO_COST_FAMILY_MACRO")
    def test_tie_policy(self):
        ps=(m.Presentation("a","ALPHA","F0",1,1),m.Presentation("b","BETA","F1",1,1))
        self.assertEqual(m.selection_with_tie_policy(ps,(1,1),"family_label"),"LABEL_DEPENDENT_TIE_BREAK")
        self.assertEqual(m.selection_with_tie_policy(ps,(1,1),None),["ALPHA","BETA"])
    def test_nonpositive_weight(self):
        with self.assertRaises(m.AuditError): m.cost(m.BASE[0],(0,1))
    def test_nonbijective_remint(self):
        mp={p.presentation_id:"x" for p in m.BASE}
        self.assertEqual(m.audit_isometric_remint(m.BASE,m.BASE_EDGES,m.BASE,m.BASE_EDGES,mp),"NON_BIJECTIVE_REMINT")
    def test_hostiles(self): self.assertEqual(len(m.hostile_certificate()),5)
    def test_receipt_terminal(self): self.assertEqual(m.build_receipt()["terminal"],"GMI_833_E7_COST_PRIVILEGE_AUDIT_GREEN_AT_REGISTERED_SCOPE")
    def test_claim_ceiling(self): self.assertEqual(m.build_receipt()["claim_ceiling"],m.CLAIM_CEILING)
    def test_oracle(self):
        x=o.build(); self.assertEqual(x["dominance_violations"],0); self.assertTrue(x["reversal"]); self.assertEqual(x["point_cost_checks"],180)
    def test_oracle_subprocess_normal_optimized_equal(self):
        a=subprocess.check_output([sys.executable,"-I","-B",str(ROOT/"independent_oracle_v1.py")])
        b=subprocess.check_output([sys.executable,"-I","-O","-B",str(ROOT/"independent_oracle_v1.py")])
        self.assertEqual(a,b)
    def test_main_subprocess_normal_optimized_equal(self):
        a=subprocess.check_output([sys.executable,"-I","-B",str(ROOT/"g0_cost_privilege_v1.py")])
        b=subprocess.check_output([sys.executable,"-I","-O","-B",str(ROOT/"g0_cost_privilege_v1.py")])
        self.assertEqual(a,b)

if __name__=="__main__": unittest.main(verbosity=2)
