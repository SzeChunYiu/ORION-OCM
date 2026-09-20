"""A: every small total map, independent lawful classification and full tree comparisons."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from itertools import product
import unittest
from support_v26 import core,oracle,actual
import functors_v26 as api
COVERAGE={}


class FunctorTests(unittest.TestCase):
    def test_all_small_functors(self):
        counts=dict(candidate_maps=0,endpoint_rejected=0,identity_rejected=0,composition_rejected=0,
                    accepted_functors=0,tree_queries=0,successful_tree_queries=0,noninjective_witnesses=0,
                    object_injective_functors=0,nonfaithful_injective_functors=0)
        models=tuple(c for n in range(3) for c in oracle.models(n));self.assertEqual(len(models),7)
        for c,d in product(models,repeat=2):
            source,target=actual(c),actual(d)
            for objects in product(range(len(d[3])),repeat=len(c[3])):
                for arrows in product(range(len(d[0])),repeat=len(c[0])):
                    counts['candidate_maps']+=1;verdict=oracle.functor_failure(c,d,objects,arrows)
                    if verdict!='accepted':
                        with self.assertRaises(ValueError):api.Functor(source,target,objects,arrows)
                        counts[verdict+'_rejected']+=1;continue
                    f=api.Functor(source,target,objects,arrows);counts['accepted_functors']+=1
                    injective=len(set(objects))==len(objects);self.assertIs(api.object_injective(f),injective)
                    counts['object_injective_functors']+=injective
                    counts['nonfaithful_injective_functors']+=injective and len(set(arrows))<len(arrows)
                    all_equal=True;queries=oracle.trees(len(c[0]),len(c[3]))
                    a=len(c[0])+len(c[3]);self.assertEqual(len(queries),a+a*a+2*a*a*a)
                    for tree in queries:
                        expected=oracle.evaluate(c,tree);mapped=oracle.map_tree(tree,objects,arrows)
                        expected_image=oracle.map_response(expected,objects,arrows)
                        target_result=oracle.evaluate(d,mapped)
                        oracle.certify(core.trees.typed_eval(source,tree),expected)
                        oracle.certify(api.map_tree(f,tree),mapped)
                        oracle.certify(api.map_response(f,expected),expected_image)
                        oracle.certify(core.trees.typed_eval(target,mapped),target_result)
                        all_equal &= target_result==expected_image
                        if expected is not None:
                            oracle.certify(target_result,expected_image);counts['successful_tree_queries']+=1
                        counts['tree_queries']+=1
                    self.assertIs(all_equal,injective)
                    if not injective:
                        a,b=next((a,b) for a in range(len(objects)) for b in range(a+1,len(objects))
                                 if objects[a]==objects[b])
                        tree=('seq',('empty',a),('empty',b))
                        self.assertIsNone(core.trees.typed_eval(source,tree))
                        self.assertIsNotNone(core.trees.typed_eval(target,api.map_tree(f,tree)))
                        counts['noninjective_witnesses']+=1
        self.assertEqual(counts['candidate_maps'],153)
        self.assertEqual(sum(counts[k] for k in ('endpoint_rejected','identity_rejected','composition_rejected','accepted_functors')),153)
        self.assertGreater(counts['nonfaithful_injective_functors'],0)
        COVERAGE.update(counts)
