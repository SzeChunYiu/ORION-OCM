"""Failed reversal premises and partial-observation/type boundaries."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name+'.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

core, oracle = load('context_v15'), load('independent_oracle_v15')
COVERAGE = {}
ORDER = ((True,True),(False,True))


def valid():
    return core.Context(2,2,(True,True),(True,True),(0,1),ORDER)


class HostileTests(unittest.TestCase):
    def test_malformed(self):
        baseline = [2,2,(True,True),(True,True),(0,1),ORDER]
        mutations = []
        for index in (0,1):
            mutations.extend((index,bad) for bad in (-1,True,2.0,'2',None))
        for index in (2,3):
            mutations.extend((index,bad) for bad in ((1,True),(True,0.0),(),(True,),{},'TT',None))
        mutations.extend((4,bad) for bad in ((True,1),(0.0,1),(-1,1),(2,1),(None,1),(),{},'01'))
        mutations.extend((5,bad) for bad in ((),((True,),),((1,True),(False,True)),
                         ((True,True),(0.0,True)),((False,True),(False,True)),{},None))
        calls = []
        for index,value in mutations:
            args = baseline.copy()
            args[index] = value
            calls.append(lambda a=args: core.Context(*a))
        calls += [lambda: core.Context(2,2,(True,True),(True,False),(0,1),ORDER),
                  lambda: core.Context(1,0,(True,),(True,),(0,),()),
                  lambda: core.Context(3,3,(True,)*3,(True,)*3,(0,1,2),
                                       ((True,True,False),(False,True,True),(False,False,True)))]
        for bad in (-1,2,True,0.0,'0',None):
            calls += [lambda b=bad: core.observe(valid(),b),
                      lambda b=bad: core.compare(valid(),b,0),
                      lambda b=bad: core.compare(valid(),0,b)]
        for bad in (-1,2,True,0.0,None):
            for position in range(4):
                args = [0,1,0,1]
                args[position] = bad
                calls.append(lambda a=args: core.opposite(valid(),*a,lambda _:True))
        # Strict boolean fields reject integers even when Python equates them.
        calls.append(lambda: core.Context(1,1,[1],[True],[0],[[True]]))
        for i,call in enumerate(calls):
            with self.subTest(case=i), self.assertRaises(ValueError):
                call()
        COVERAGE['malformed_input_rejections'] = len(calls)

    def test_reversal_premises(self):
        good = valid()
        calls = [lambda: core.opposite(good,0,0,0,1,lambda _:True),
                 lambda: core.opposite(good,0,1,0,0,lambda _:True),
                 lambda: core.opposite(good,0,1,1,0,lambda _:True),
                 lambda: core.opposite(good,0,1,0,1,lambda v:len(set(v))<=1),
                 lambda: core.opposite(good,0,1,0,1,lambda v:v[0]==v[1]),
                 lambda: core.opposite(core.Context(2,2,(False,True),(True,True),(0,1),ORDER),0,1,0,1,lambda _:True),
                 lambda: core.opposite(core.Context(2,2,(True,True),(False,True),(None,1),ORDER),0,1,0,1,lambda _:True),
                 lambda: core.opposite(core.Context(2,2,(True,True),(True,True),(0,1),((True,True),(True,True))),0,1,0,1,lambda _:True),
                 lambda: core.opposite(core.Context(0,2,(),(),(),ORDER),0,1,0,1,lambda _:True),
                 lambda: core.opposite(core.Context(1,2,(True,),(True,),(0,),ORDER),0,0,0,1,lambda _:True)]
        for returned in (False,1,1.0,None,(), 'yes'):
            calls.append(lambda r=returned: core.opposite(good,0,1,0,1,lambda _:r))
        for call in calls:
            with self.assertRaises(ValueError):
                call()
        # Swap closure is an alternative to containing the two indicators.
        order3 = tuple(tuple(i<=j for j in range(3)) for i in range(3))
        allowed_set = {(0,2,1),(2,0,1)}
        contexts = [core.Context(3,3,(True,)*3,(True,)*3,v,order3) for v in sorted(allowed_set)]
        for context in contexts:
            swapped = (context.values[1],context.values[0],context.values[2])
            self.assertIn(swapped,allowed_set)
        self.assertNotEqual(core.compare(contexts[0],0,1),core.compare(contexts[1],0,1))
        with self.assertRaises(ValueError):
            core.opposite(contexts[0],0,1,0,2,lambda v:v in allowed_set)
        COVERAGE['failed_reversal_premises'] = len(calls)
        COVERAGE['swap_closure_alternative_controls'] = 1
        registered = {(0,1,1),(1,0,0)}
        base = core.Context(3,2,(True,)*3,(True,)*3,(0,0,0),ORDER)
        first,second = core.opposite(base,0,1,0,1,lambda v:v in registered)
        self.assertEqual((first.values,second.values),((0,1,1),(1,0,0)))
        other_class = {(0,1,0),(1,0,0)}
        with self.assertRaises(ValueError):
            core.opposite(base,0,1,0,1,lambda v:v in other_class)
        permitted = [core.Context(3,2,(True,)*3,(True,)*3,v,ORDER) for v in sorted(other_class)]
        self.assertNotEqual(core.compare(permitted[0],0,1),core.compare(permitted[1],0,1))
        COVERAGE['registered_indicator_class_controls'] = 1
        COVERAGE['nonmatching_indicator_class_controls'] = 1

    def test_partial_observation_boundaries(self):
        empty = core.Context(0,0,(),(),(),())
        self.assertEqual(core.domain(empty),())
        self.assertEqual(core.quotient(empty),((),()))
        no_values = core.Context(2,0,(False,True),(False,False),(None,None),())
        self.assertEqual(core.observe(no_values,0),('ILLEGAL',None))
        self.assertEqual(core.observe(no_values,1),('UNDEFINED',None))
        undefined_label = core.Context(2,1,(True,True),(False,True),(None,0),((True,),))
        labels = ('UNDEFINED',)
        self.assertEqual(labels[core.observe(undefined_label,1)[1]], 'UNDEFINED')
        self.assertNotEqual(core.observe(undefined_label,0),core.observe(undefined_label,1))
        calls = []
        for ambient in (0,1):
            context = core.Context(3,2,(True,True,False),(True,True,True),(0,1,ambient),ORDER)
            observed = []
            def allowed(values):
                observed.append(values)
                return len(values)==2 and values in ((0,1),(1,0))
            first,second = core.opposite(context,0,1,0,1,allowed)
            self.assertEqual(observed,[(0,1),(1,0)])
            self.assertEqual((first.values[2],second.values[2]),(ambient,ambient))
            self.assertEqual(core.observe(context,2),('ILLEGAL',None))
            calls.append(tuple(observed))
        self.assertEqual(calls[0],calls[1])
        rejected = 0
        for context,h in ((no_values,0),(no_values,1),(undefined_label,0)):
            with self.assertRaises(ValueError):
                core.compare(context,h,h)
            rejected += 1
        equivalent = core.Context(2,2,[True,True],[True,True],[0,1],[[True,True],[True,True]])
        self.assertEqual(core.quotient(equivalent),((frozenset((0,1)),),((True,),)))
        COVERAGE.update(empty_carrier_controls=2, outside_domain_comparison_rejections=rejected,
                        ambient_restriction_controls=2, undefined_label_controls=1,
                        equivalent_value_controls=1)

    def test_diagnostic_corruptions(self):
        model = oracle.context_tuple(valid())
        expected = core.quotient(valid())
        self.assertTrue(oracle.check_quotient(model,expected))
        bad = [((frozenset((0,1)),),((True,),)),
               ((frozenset((0,)),),((True,),)),
               (expected[0],((True,False),(False,True))),
               (expected[0],((True,True),(True,True)))]
        for candidate in bad:
            self.assertFalse(oracle.check_quotient(model,candidate))
        def audit(diagnostic):
            return diagnostic(model,expected) is True and all(diagnostic(model,x) is False for x in bad)
        self.assertTrue(audit(oracle.check_quotient))
        self.assertFalse(audit(lambda *_:True))
        COVERAGE.update(quotient_corruption_rejections=len(bad), weakened_diagnostic_rejections=1)


if __name__ == '__main__':
    program = unittest.main(exit=False, verbosity=2)
    print(json.dumps(COVERAGE, sort_keys=True))
    raise SystemExit(not program.result.wasSuccessful())
