"""Named functor, restriction, enrichment and fixed-map observation boundaries."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fractions import Fraction
from itertools import product
import importlib.util
import unittest
from support_v26 import core,oracle,actual,make,unpack
import oracle_resource_v26 as independent
import functors_v26 as functors
import restrictions_v26 as restrictions
COVERAGE={}


def parent(name,folder):
    path=Path(__file__).resolve().parents[1]/folder/(name+'.py')
    if name in sys.modules:
        if Path(sys.modules[name].__file__).resolve()!=path:raise ValueError('parent module collision')
        return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module


class ControlTests(unittest.TestCase):
    def test_indiscrete_equivalence_and_fixed_encoders(self):
        c=independent.category((0,1),tuple(product(range(2),repeat=2)))
        d=oracle.models(1)[0];source,target=make(c),actual(d)
        f=functors.Functor(source,target,(0,0),(0,0,0,0))
        for a,b in product(range(2),repeat=2):
            self.assertEqual(sum(s==a and t==b for s,t in zip(c[1],c[2])),1)
        self.assertFalse(functors.object_injective(f));count=failures=0
        for tree in oracle.trees(4,2):
            left=oracle.evaluate(c,tree);mapped=oracle.map_tree(tree,(0,0),(0,0,0,0))
            right=oracle.evaluate(d,mapped)
            oracle.certify(core.trees.typed_eval(source,tree),left)
            oracle.certify(core.trees.typed_eval(target,functors.map_tree(f,tree)),right)
            if left is not None:oracle.certify(functors.map_response(f,left),right)
            else:self.assertIsNotNone(right);failures+=1
            count+=1
        self.assertEqual(count,474);self.assertGreater(failures,0)
        collapse=('seq',('empty',0),('empty',1))
        self.assertIsNone(core.trees.typed_eval(source,collapse))
        self.assertIsNotNone(core.trees.typed_eval(target,functors.map_tree(f,collapse)))
        c2=next(c for c in oracle.models(2) if c[0]==((0,1),(1,0)))
        nonfaithful=functors.Functor(actual(c2),target,(0,),(0,0))
        self.assertTrue(functors.object_injective(nonfaithful))
        self.assertNotEqual(oracle.evaluate(c2,('arrow',0)),oracle.evaluate(c2,('arrow',1)))
        self.assertEqual(functors.map_tree(nonfaithful,('arrow',0)),functors.map_tree(nonfaithful,('arrow',1)))
        expected=(('empty',0),oracle.evaluate(c,('empty',0)))
        identity=functors.Functor(source,source,(0,1),(0,1,2,3))
        oracle.certify((functors.map_tree(identity,('empty',0)),core.trees.typed_eval(source,('empty',0))),expected)
        mutations=[(('empty',1),oracle.evaluate(c,('empty',1))),
                   (('empty',0),None),(('empty',0),(0,0,1)),(('empty',False),(0,0,0))]
        arrow_expected=(('arrow',1),oracle.evaluate(c,('arrow',1)))
        for bad in mutations:
            with self.assertRaises(ValueError):oracle.certify(bad,expected)
        with self.assertRaises(ValueError):oracle.certify((('arrow',2),oracle.evaluate(c,('arrow',2))),arrow_expected)
        with self.assertRaises(ValueError):oracle.certify((0,0,False),(0,0,0))
        with self.assertRaises(ValueError):oracle.certify((0,0,0.0),(0,0,0))
        COVERAGE.update(indiscrete_tree_controls=count,indiscrete_failed_join_controls=failures,
                        semantic_mutation_rejections=len(mutations)+3,valid_fixed_map_certificates=1,
                        nonfaithful_named_controls=1)

    def test_admission_failure_and_original_units(self):
        count=0
        c,costs=independent.chain();category=make(c)
        oracle.certify(restrictions.admission_laws(category,tuple(i for i,v in enumerate(costs) if v<=1)),(True,False));count+=1
        oracle.certify(restrictions.admission_laws(category,tuple(i for i,v in enumerate(costs) if v>0)),(False,True));count+=1
        idempotent=next(c for c in oracle.models(2) if c[0]==((0,1),(1,1)))
        cat=actual(idempotent);sub,f=restrictions.wide_restriction(cat,(1,0))
        oracle.certify(unpack(sub),idempotent);oracle.certify(f.arrow_map,(0,1))
        self.assertEqual(sub.identities,(0,));self.assertEqual(sub.table.rows[1][1],1);count+=1
        for allowed in ((1,),()):
            with self.assertRaises(ValueError):restrictions.wide_restriction(cat,allowed)
            count+=1
        empty=actual(oracle.models(0)[0]);restricted,inclusion=restrictions.wide_restriction(empty,())
        self.assertEqual(restricted,empty);self.assertTrue(functors.object_injective(inclusion));count+=1
        COVERAGE.update(admission_named_controls=count)

    def test_actual_optional_parent_boundaries(self):
        count=0
        optional=parent('optional_v13','gmi-1068-optional-structure-v13')
        stochastic=parent('stochastic_v14','gmi-1068-stochastic-process-v14')
        funcs=((0,1),(0,0),(1,1))
        expected=tuple(tuple(funcs.index(tuple(g[f[x]] for x in range(2))) for g in funcs) for f in funcs)
        oracle.certify(optional.RESET_COMPOSITION,expected);count+=1
        self.assertEqual(optional.inverses(expected,0),((0,0),));count+=1
        witness=next((a,b,c,d) for a,b,c,d in product(range(3),repeat=4)
                     if expected[expected[a][b]][expected[c][d]]!=expected[expected[a][c]][expected[b][d]])
        self.assertEqual(optional.interchange_failure(expected,expected),witness);count+=1
        self.assertNotEqual(expected[1][2],expected[2][1]);count+=1
        self.assertEqual(optional.tensor('product',(1,1),(2,0)),(2,1));count+=1
        self.assertEqual(optional.tensor('product',(2,0),(1,1)),(1,1));count+=1
        self.assertEqual(optional.hom('product',2,1),());count+=1
        a=stochastic.Kernel(1,2,((Fraction(1,3),Fraction(2,3)),))
        b=stochastic.Kernel(1,2,((Fraction(2,3),Fraction(1,3)),))
        self.assertEqual(stochastic.support(a),stochastic.support(b));self.assertNotEqual(a,b);count+=1
        branching=stochastic.Relation(1,2,((0,1),));deterministic=stochastic.graph(1,2,(0,))
        self.assertEqual(branching.rows,(frozenset((0,1)),));self.assertNotEqual(branching,deterministic);count+=1
        self.assertEqual(stochastic.support(stochastic.dirac(1,2,(0,))),deterministic);count+=1
        COVERAGE.update(optional_parent_controls=count)
