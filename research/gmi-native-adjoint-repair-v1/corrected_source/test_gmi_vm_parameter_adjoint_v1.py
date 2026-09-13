"""Focused active-runtime regression controls; no ecology or search."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gmi_microscope import core,bases,morph,vm

def machine(basis, remint_seed=None):
    graph=morph.make({'x':('INPUT',{'width':1}),'w':('DENSE',{'width':1}),
        'f':('LINEAR',{}),'out':('OUTPUT',{}),'y':('TARGET',{}),'g':('GRAD',{'lr':1})},
        [('w','f',0),('x','f',1),('f','out',0),('w','g',0),('f','g',1),('y','g',2)])
    if remint_seed is not None: graph=morph.remint(graph,remint_seed)
    M=core.Machine(basis);V=vm.VM(graph,M);V.init();return M,V

class ParameterAdjointTests(unittest.TestCase):
    def test_zero_input_has_zero_gradient_and_no_false_update(self):
        for basis in (bases.B0,bases.B1):
            M,V=machine(basis);before=M.read('w_w0')
            _,out=V.evaluate(0,tape=True)
            self.assertEqual(V._backprop(out,-16),{'w_w0':0})
            M.phase('upd');V.feedback(0,16)
            self.assertEqual(M.read('w_w0'),before)
            self.assertEqual(V.query(0),0)

    def test_no_outgoing_grad_edge_still_performs_nonzero_update(self):
        for basis in (bases.B0,bases.B1):
            M,V=machine(basis)
            self.assertFalse(any(a=='g' for a,b,p in V.g['edges']))
            self.assertEqual(V.query(1),8)
            M.phase('upd');V.feedback(1,0)
            self.assertEqual(M.read('w_w0'),7)
            self.assertEqual(V.query(1),7)

    def test_tied_weight_contributions_and_bias_identity(self):
        M=core.Machine(bases.B0);M.declare('w','fx',8);M.declare('b','fx',16)
        V=vm.VM.__new__(vm.VM);V.M=M
        out=V._dot(['w','w','b'],[vm.Val(16),vm.Val(-16)],True)
        self.assertEqual(V._backprop(out,16),{'w':0,'b':16})

    def test_downstream_sharing_and_nonunit_input_scale(self):
        M=core.Machine(bases.B0);M.declare('w','fx',16)
        V=vm.VM.__new__(vm.VM);V.M=M
        one=V._dot(['w'],[vm.Val(8)],True)
        self.assertEqual(V._backprop(one,16),{'w':8})
        two=vm.Val(M.op('ADD',one.v,one.v),[(one,16),(one,16)])
        self.assertEqual(V._backprop(two,16),{'w':16})

    def test_corrected_response_and_charges_are_remint_invariant(self):
        def response(seed):
            M,V=machine(bases.B0,seed);answers=[]
            for x,y in ((0,16),(1,0),(0,0),(1,16)):
                M.phase('exec');answers.append(V.query(x))
                M.phase('upd');V.feedback(x,y)
            return answers,dict(M.L.c)
        self.assertEqual(response(None),response(None))
        for seed in (1,5,9): self.assertEqual(response(None),response(seed))

if __name__=='__main__':unittest.main()
