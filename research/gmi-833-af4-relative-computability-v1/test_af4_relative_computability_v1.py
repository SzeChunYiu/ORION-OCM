from __future__ import annotations
import importlib.util, sys, unittest, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('af4',HERE/'af4_relative_computability_v1.py'); af4=importlib.util.module_from_spec(spec); sys.modules['af4']=af4; spec.loader.exec_module(af4)

class AF4Tests(unittest.TestCase):
    def test_01_six_adjacent_displacements(self): self.assertEqual(len(af4.certificate()['adjacent_displacements']),6)
    def test_02_universal_halting_forbidden(self):
        with self.assertRaisesRegex(ValueError,'FORBIDDEN_PROMOTION'): af4.validate_claim_terminal('HALTING_PROBLEM_SOLVED_UNIVERSALLY')
    def test_03_missing_residual(self):
        d=af4.adjacent_displacement(0); bad=af4.Displacement(**{**d.__dict__,'nearest_residual':''})
        with self.assertRaisesRegex(ValueError,'RESIDUAL'): af4.validate_displacement(bad)
    def test_04_missing_oracle_provenance(self):
        d=af4.adjacent_displacement(0); bad=af4.Displacement(**{**d.__dict__,'provenance':'NONE'})
        with self.assertRaisesRegex(ValueError,'PROVENANCE'): af4.validate_displacement(bad)
    def test_05_free_oracle_rejected(self):
        d=af4.adjacent_displacement(0); bad=af4.Displacement(**{**d.__dict__,'oracle_access_charge':0})
        with self.assertRaisesRegex(ValueError,'CHARGED'): af4.validate_displacement(bad)
    def test_06_finite_information_bits_on_infinite_oracle_rejected(self):
        d=af4.adjacent_displacement(0); bad=af4.Displacement(**{**d.__dict__,'finite_advice_bits':1024})
        with self.assertRaisesRegex(ValueError,'FINITE_INFORMATION_BITS'): af4.validate_displacement(bad)
    def test_07_nonadjacent_jump_rejected(self):
        d=af4.adjacent_displacement(0); bad=af4.Displacement(**{**d.__dict__,'target_level':2})
        with self.assertRaisesRegex(ValueError,'NON_ADJACENT'): af4.validate_displacement(bad)
    def test_08_physical_promotion_rejected(self):
        with self.assertRaisesRegex(ValueError,'FORBIDDEN_PROMOTION'): af4.validate_claim_terminal('PHYSICAL_HYPERCOMPUTATION_ESTABLISHED')
    def test_09_godel_escape_rejected(self):
        c=af4.ProofContext('T','A','R','U',('CONSISTENT',),'SEARCH')
        with self.assertRaisesRegex(ValueError,'INCOMPLETENESS_ESCAPE'): af4.audit_godel_machine_claim(c,'GODEL_INCOMPLETENESS_ESCAPED',axioms_changed=True)
    def test_10_missing_proof_context_rejected(self):
        with self.assertRaisesRegex(ValueError,'CANNOT_AUDIT_PROOF_SYSTEM'): af4.audit_godel_machine_claim(None,'SCOPED')
    def test_11_unprovable_not_false(self): self.assertIn('TRUTH_NOT_INFERRED',af4.interpret_unprovable('UNPROVABLE_IN_T'))
    def test_12_executor_not_parent_proof(self): self.assertEqual(af4.certificate()['parent_theorem']['ownership'],'PARENT_OWNED_NOT_PROVED_BY_EXECUTOR')
    def test_13_base_hostile_residual(self): self.assertTrue(af4.certificate()['base_halting_hostile']['residual_preserved'])
    def test_14_godel_changed_axioms_context_change(self):
        c=af4.ProofContext('T','A','R','U',('CONSISTENT',),'SEARCH'); self.assertIn('CONTEXT_CHANGED',af4.audit_godel_machine_claim(c,'SCOPED',axioms_changed=True))
    def test_15_no_physical_claim(self): self.assertEqual(af4.certificate()['physical_scope'],'NO_PHYSICAL_HYPERCOMPUTATION_CLAIM')
    def test_16_parent_ledger_sources(self):
        o=json.loads((HERE/'PARENT_LEDGER_V1.json').read_text())
        self.assertEqual(len(o['rows']),5)
        self.assertTrue(any(r['id']=='AF4-P1-TURING-JUMP' and 'recursive-functions' in r['url'] for r in o['rows']))
        self.assertTrue(any(r['id']=='AF4-P3-GODEL-MACHINE' and 'cs/0309048' in r['url'] for r in o['rows']))

if __name__=='__main__': unittest.main()
