"""Independent no-alarm controls and exact refusal/cost countercontrols."""
from pathlib import Path
from fractions import Fraction
from itertools import product
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cost_contracts_v1 import additive_bounds, python_contract, refinement, separation
from independent_oracle_v1 import trace_native
from typed_machine_v1 import execute
from typed_program_v1 import Program, Alias, Refusal
from witnesses_v1 import register, historical, wrapper_program

class TypedCostTests(unittest.TestCase):
    def test_fresh_first_instruction_trace_without_priming(self):
        program = Program({'main': 'def f(x):\n    return x+1\n'})
        value, events = trace_native(program, 'main', 2)
        self.assertEqual(value, 3)
        self.assertEqual(events, ('py:LOAD_FAST','py:LOAD_CONST','py:BINARY_OP','py:RETURN_VALUE'))

    def test_extended_arguments_are_not_lost(self):
        source='def f(x):\n'+''.join(f'    a{i}=x\n' for i in range(260))+'    return a259\n'
        program=Program({'main':source})
        result=execute(program,'main',7)
        value,events=trace_native(program,'main',7)
        self.assertEqual(value,result.value)
        self.assertEqual(events,result.events)
        self.assertIn('py:EXTENDED_ARG',events)

    def test_native_source_and_partial_no_alarm(self):
        old, programs = register()
        for name, program in programs.items():
            for x in old.INPUTS:
                result = execute(program, 'main', x)
                value, events = trace_native(program, 'main', x)
                self.assertEqual(value, result.value, name)
                self.assertEqual(events, tuple(e for e in result.events if e.startswith('py:')), name)

    def test_partial_preserves_native_obligations_and_cost(self):
        old = historical(); source = old.REGISTERED['WRITTEN_SHARED_SUM_NET']
        parent, wrapped = Program({'main': source}), wrapper_program(source, True)
        for x in old.INPUTS:
            a, b = execute(parent,'main',x), execute(wrapped,'main',x)
            self.assertEqual((a.python_opcodes,b.python_opcodes),(39,43))
            self.assertEqual([e for e in a.events if e.startswith('native:')],
                             [e for e in b.events if e.startswith('native:')])
            self.assertTrue(refinement(a.events,b.events))

    def test_python_object_and_subclass_refused_without_dispatch(self):
        calls=[]
        class Hidden:
            def __getitem__(self,x): calls.append(x); return 0
        class IntSubclass(int):
            def __add__(self,x): calls.append(x); return 0
        with self.assertRaises(Refusal): Program({'main':'def f(x):\n    return table[x]\n'}, data={'table':Hidden()})
        with self.assertRaises(Refusal): execute(Program({'main':'def f(x):\n    return x+1\n'}),'main',IntSubclass(0))
        self.assertEqual(calls,[])

    def test_exact_tuple_lookup_positive_and_bad_index_negative(self):
        p=Program({'main':'def f(x):\n    return table[x]\n'},data={'table':(4,7)})
        self.assertEqual(execute(p,'main',1).value,7)
        with self.assertRaises(Refusal): execute(p,'main',True)
        with self.assertRaises(Refusal): execute(p,'main',2)

    def test_builtin_callback_contracts_are_enforced(self):
        for source,arg in [('def f(x):\n    return int(x)\n',(1,)),
                           ('def f(x):\n    return sum(x)\n',((1,),))]:
            with self.assertRaises(Refusal): execute(Program({'main':source}),'main',arg)
        with self.assertRaises(Refusal): Program({'int':'def f(x):\n    return x\n'})

    def test_opaque_unbound_method_and_recursion_refused(self):
        for source in ['def f(x):\n    return missing(x)\n', 'def f(x):\n    return x.count(1)\n',
                       'def f(x):\n    return main(x)\n']:
            with self.assertRaises(Refusal): execute(Program({'main':source}),'main',(1,))
        with self.assertRaises(Refusal): Program({'main':'def f(x):\n    return x\n'},{'a':Alias('missing')})

    def test_control_flow_and_definition_effects_refused(self):
        for source in ['def f(x):\n    return x if x else 0\n', 'def f(x=print(1)):\n    return x\n',
                       '@print\ndef f(x):\n    return x\n', 'def f(x):\n    return [a for a in x]\n',
                       'def int(x):\n    return x\n', 'def f(x):\n    y=x\n    y=x\n    return y.__class__\n']:
            with self.assertRaises((Refusal,SyntaxError)): Program({'main':source})

    def test_callable_local_alias_and_call_depth_refused(self):
        p=Program({'main':'def f(x):\n    y=int\n    return y(x)\n'})
        with self.assertRaises(Refusal): execute(p,'main',1)
        sources={f'p{i}':f'def f(x):\n    return p{i+1}(x)\n' for i in range(8)}
        sources['p8']='def f(x):\n    return x\n'
        with self.assertRaises(Refusal): execute(Program(sources),'p0',1)

    def test_negative_and_missing_contracts(self):
        with self.assertRaises(Refusal): additive_bounds(('x',),{'x':(-1,2)})
        with self.assertRaises(Refusal): additive_bounds(('x',),{'x':(2,1)})
        with self.assertRaises(Refusal): additive_bounds(('x',),{'x':(True,2)})
        self.assertEqual(additive_bounds(('x','x'),{}),(0,None))
        self.assertEqual(separation(('x',),('y',),{'y':(9,9)}),'UNVERIFIABLE')
        self.assertEqual(separation(('x',),('y',),{'x':(1,2),'y':(3,4)}),'CERTIFIED_STRICTLY_LOWER')

    def test_refinement_against_independent_cost_assignments(self):
        parent=('a','b','a');child=('c','a','b','c','a')
        self.assertEqual(refinement(parent,child),{'c':2})
        for weights in product((0,1,3),repeat=3):
            contract={k:(v,v) for k,v in zip('abc',weights)}
            pa=sum(dict(zip('abc',weights))[x] for x in parent)
            ch=sum(dict(zip('abc',weights))[x] for x in child)
            self.assertEqual(additive_bounds(parent,contract),(pa,pa))
            self.assertEqual(additive_bounds(child,contract),(ch,ch))
            self.assertGreaterEqual(ch,pa)
        with self.assertRaises(Refusal): refinement(parent,('c','a'))
        with self.assertRaises(Refusal): refinement(parent,('a','a','b'))

    def test_fractional_contracts_and_zero_cost_tie(self):
        self.assertEqual(additive_bounds(('a','a'),{'a':(Fraction(1,3),Fraction(2,3))}),
                         (Fraction(2,3),Fraction(4,3)))
        self.assertEqual(separation(('a',),('a','b'),{'a':(1,1),'b':(0,0)}),'UNVERIFIABLE')

if __name__=='__main__': unittest.main()
