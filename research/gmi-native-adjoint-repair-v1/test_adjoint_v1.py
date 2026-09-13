"""Primitive, native-state and independent analytic falsifiers."""
from pathlib import Path
import hashlib
import json
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_loader_v1 import ROOT,source_modules,verify_corrected_sources
from native_controls_v1 import run_control,dot_control
from adjoint_reference_v1 import scalar_census,exact_differences,sharing_controls,boundary_controls
from check_v1 import historical_packet

class AdjointTests(unittest.TestCase):
    def test_full_parent_packet_and_minimal_patch(self):
        self.assertEqual(len(historical_packet()),2)
        self.assertEqual(verify_corrected_sources()['old_main'],'ef6de91af6f6ce692e0f8bd9725f8ad4f4435e9d')

    def test_zero_input_bug_and_revived_actual_native_update(self):
        for basis in ('B0','B1'):
            old=run_control('old',0,16,basis);new=run_control('corrected',0,16,basis)
            self.assertEqual(old['tape_observations'][0]['parameter_adjoints_fx'],{'dense_w0':-16})
            self.assertEqual(new['tape_observations'][0]['parameter_adjoints_fx'],{'dense_w0':0})
            self.assertEqual(old['stages'][-1]['cells']['dense_w0'],9)
            self.assertEqual(new['stages'][-1]['cells']['dense_w0'],8)
            self.assertEqual(new['outputs'],{'before':0,'after':0})

    def test_nonzero_no_outgoing_edge_full_ledger_no_alarm(self):
        for basis in ('B0','B1'):
            old=run_control('old',1,0,basis);new=run_control('corrected',1,0,basis)
            self.assertEqual(old['stages'],new['stages'])
            self.assertEqual(new['outputs'],{'before':8,'after':7})
            self.assertEqual(new['grad_outgoing_edges'],[])

    def test_native_affine_weight_and_bias_paths(self):
        for basis in ('B0','B1'):
            r=run_control('corrected',0,0,basis,True)
            self.assertEqual(r['stages'][-1]['cells'],{'dense_w0':8,'dense_w1':15,'last_w0':16})
            self.assertEqual(r['tape_observations'][0]['parameter_adjoints_fx']['dense_w0'],0)
            self.assertEqual(r['tape_observations'][0]['parameter_adjoints_fx']['dense_w1'],16)

    def test_independent_fixed_point_census(self):
        self.assertEqual(len(scalar_census()),2197)

    def test_exact_native_finite_differences(self):
        self.assertEqual(len(exact_differences()),45)

    def test_tied_shared_composed_and_bias_controls(self):
        r=sharing_controls();self.assertEqual(len(r['tied']),27)
        self.assertEqual(r['shared_adjoints'],{'w':16})
        self.assertEqual(r['composed_adjoints'],{'w':2,'u':2})
        b=boundary_controls();self.assertEqual(len(b['bias_identity_cases']),9)
        self.assertEqual(b['ordered_clamped_tied_adjoint'],{'tied':126})

    def test_saturation_does_not_become_literal_quantizer_derivative(self):
        row=boundary_controls()['saturation']
        self.assertEqual(row['three_forward_values'],[127,127,127])
        self.assertEqual(row['central_output_difference'],0)
        self.assertEqual(row['registered_adjoint_fx'],64)
        self.assertFalse(row['literal_quantized_program_derivative_claimed'])

    def test_parameter_marker_is_weight_leaf_not_product(self):
        core,bases,_,vm=source_modules('corrected');M=core.Machine(bases.B0);M.declare('w','fx',8)
        V=vm.VM.__new__(vm.VM);V.M=M
        out=V._dot(['w'],[vm.Val(0)],True)
        product=out.parents[1][0];weight=product.parents[0][0]
        self.assertEqual(weight.parents,[('param','w')])
        self.assertFalse(any(p[0]=='param' for p in product.parents))
        plain=V._dot(['w'],[vm.Val(0)],False)
        self.assertEqual(plain.parents,[])

    def test_repeated_reverse_pass_resets_adjoint_state(self):
        core,bases,_,vm=source_modules('corrected');M=core.Machine(bases.B0);M.declare('w','fx',16)
        V=vm.VM.__new__(vm.VM);V.M=M;out=V._dot(['w'],[vm.Val(8)],True)
        self.assertEqual(V._backprop(out,16),{'w':8})
        self.assertEqual(V._backprop(out,-16),{'w':-8})
        self.assertEqual(V._backprop(out,0),{'w':0})

if __name__=='__main__':unittest.main()
