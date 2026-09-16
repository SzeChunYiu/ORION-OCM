from __future__ import annotations
from fractions import Fraction
import importlib.util,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('stoch',ROOT/'stochastic_update_v1.py')
if spec is None or spec.loader is None: raise RuntimeError
M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M;spec.loader.exec_module(M)
F=Fraction
class T(unittest.TestCase):
  def test_freeze(self): self.assertEqual(M.FREEZE_COMMIT,'e05a2849d3bf71b0130085d880c7607ce0f507fa')
  def test_rows(self): self.assertEqual(len(M.row_family()),6)
  def test_kernels(self): self.assertEqual(len(M.kernel_family()),216)
  def test_float_rejected(self):
    with self.assertRaisesRegex(ValueError,'PROBABILITY_NOT_FRACTION'): M.distribution((0.5,0.5,0.0))
  def test_integer_rejected(self):
    with self.assertRaisesRegex(ValueError,'PROBABILITY_NOT_FRACTION'): M.distribution((1,0,0))
  def test_negative_rejected(self):
    with self.assertRaisesRegex(ValueError,'NEGATIVE_PROBABILITY'): M.distribution((F(-1,2),F(3,2),F(0)))
  def test_bad_sum(self):
    with self.assertRaisesRegex(ValueError,'DISTRIBUTION_NOT_NORMALIZED'): M.distribution((F(1,2),F(0),F(0)))
  def test_bad_dim(self):
    with self.assertRaisesRegex(ValueError,'DISTRIBUTION_DIMENSION'): M.distribution((F(1),F(0)))
  def test_kernel_dim(self):
    with self.assertRaisesRegex(ValueError,'KERNEL_DIMENSION'): M.kernel(((F(1),F(0),F(0)),))
  def test_kernel_row(self):
    with self.assertRaisesRegex(ValueError,'DISTRIBUTION_NOT_NORMALIZED'): M.kernel(((F(1),F(0),F(0)),(F(1),F(0),F(0)),(F(1,2),F(0),F(0))))
  def test_bad_perm(self):
    with self.assertRaisesRegex(ValueError,'NON_BIJECTIVE_RELABELING'): M.validate_perm((0,0,2))
  def test_state_outside(self):
    with self.assertRaisesRegex(ValueError,'STATE_OUTSIDE_CARRIER'): M.point_mass(3)
  def test_identity(self):
    I=M.identity_kernel()
    for K in M.kernel_family(): self.assertEqual(M.compose(I,K).value,K); self.assertEqual(M.compose(K,I).value,K)
  def test_update_resource(self): self.assertEqual(M.update(M.point_mass(0),M.identity_kernel()).resources,(3,9,9,6,3))
  def test_comp_resource(self): self.assertEqual(M.compose(M.identity_kernel(),M.identity_kernel()).resources,(0,54,27,18,9))
  def test_cycle(self):
    K=M.deterministic_kernel((1,2,0)); self.assertEqual(M.update(M.point_mass(2),K).value,M.point_mass(0))
  def test_stochastic(self):
    K=M.kernel(((M.HALF,M.HALF,M.ZERO),(M.ZERO,M.HALF,M.HALF),(M.HALF,M.ZERO,M.HALF)))
    self.assertEqual(M.update(M.point_mass(0),K).value.mass,(M.HALF,M.HALF,M.ZERO))
  def test_quarter(self): self.assertTrue(M.positive_controls()['quarter_after_composition'])
  def test_law_count(self):
    c=M.exact_census(); self.assertEqual(c['law_preservation_checks'],1296); self.assertEqual(c['law_preservation_failures'],0)
  def test_cov_count(self):
    c=M.exact_census(); self.assertEqual(c['one_step_covariance_checks'],7776); self.assertEqual(c['one_step_covariance_failures'],0)
  def test_pair_count(self):
    c=M.exact_census(); self.assertEqual(c['composition_pair_checks'],46656); self.assertEqual(c['composition_invalid_failures'],0)
  def test_seq_count(self):
    c=M.exact_census(); self.assertEqual(c['sequential_basis_checks'],139968); self.assertEqual(c['sequential_basis_failures'],0)
  def test_comp_cov(self): self.assertEqual(M.exact_census()['composition_covariance_failures'],0)
  def test_independent_comp(self): self.assertEqual(M.exact_census()['composition_implementation_mismatches'],0)
  def test_det_count(self):
    c=M.exact_census(); self.assertEqual(c['deterministic_specialization_checks'],81); self.assertEqual(c['deterministic_specialization_failures'],0)
  def test_controls(self): self.assertTrue(all(M.positive_controls().values()))
  def test_boundaries(self):
    h=M.hostile_results(); self.assertEqual(h['confidence_boundary'],'CANNOT_COERCE_PREDICTIVE_LAW_WITHOUT_CONFIDENCE_PREMISE'); self.assertEqual(h['latent_boundary'],'CANNOT_DECOMPOSE_WITHOUT_LATENT_SEMANTICS')
  def test_hostiles(self): self.assertNotIn('ACCEPTED',M.hostile_results().values())
  def test_receipt(self): self.assertEqual(M.build_receipt()['terminal'],'GMI_833_FINITE_STOCHASTIC_UPDATE_V1_ALL_GREEN')
  def test_committed(self): self.assertEqual(M.canonical_json(M.build_receipt()),(ROOT/'RESULT_V1.json').read_text())
  def test_oracle(self):
    cp=subprocess.run([sys.executable,'-I','-B',str(ROOT/'independent_oracle_v1.py')],check=True,text=True,capture_output=True)
    o=json.loads(cp.stdout);c=M.exact_census()
    for k in ('row_family_count','kernel_count','law_preservation_checks','law_preservation_failures','one_step_covariance_checks','one_step_covariance_failures','composition_pair_checks','composition_invalid_failures','sequential_basis_checks','sequential_basis_failures','composition_covariance_failures','identity_kernel_failures','deterministic_specialization_checks','deterministic_specialization_failures'): self.assertEqual(o[k],c[k])
    self.assertEqual(o['terminal'],'GREEN')
if __name__=='__main__': unittest.main()
