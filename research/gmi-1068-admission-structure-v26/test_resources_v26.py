"""C: actual resource category projection and the same supplied path, not reachability."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from itertools import product
import unittest
from support_v26 import core,oracle,make,unpack
import oracle_resource_v26 as independent
import functors_v26 as functors
import resource_v26 as api
COVERAGE={}


class ResourceTests(unittest.TestCase):
    def test_registered_chain(self):
        c,costs=independent.chain();expected,objects,arrows=independent.resource(c,costs,2)
        base=make(c);model=api.ResourceLift(base,costs,2)
        oracle.certify(unpack(model.category),expected)
        oracle.certify(model.object_labels,objects);oracle.certify(model.arrow_labels,arrows)
        self.assertEqual((len(objects),len(arrows)),(9,14));self.assertFalse(functors.object_injective(model.forgetful))
        objmap=tuple(o for o,r in objects);arrmap=tuple(f for f,r in arrows)
        oracle.certify(model.forgetful.object_map,objmap);oracle.certify(model.forgetful.arrow_map,arrmap)
        counts=dict(resource_pairs=0,successful_pair_projections=0,failed_pair_revivals=0,
                    path_attempts=0,typed_base_paths=0,successful_lifts=0,unaffordable_paths=0,ill_typed_paths=0,
                    empty_word_lifts=0)
        for f,g in product(range(len(arrows)),repeat=2):
            tree=('seq',('arrow',f),('arrow',g));response=oracle.evaluate(expected,tree)
            projected=oracle.evaluate(c,oracle.map_tree(tree,objmap,arrmap))
            oracle.certify(core.trees.typed_eval(model.category,tree),response)
            oracle.certify(core.trees.typed_eval(base,functors.map_tree(model.forgetful,tree)),projected)
            if response is not None:
                oracle.certify(functors.map_response(model.forgetful,response),projected)
                counts['successful_pair_projections']+=1
            elif projected is not None:counts['failed_pair_revivals']+=1
            counts['resource_pairs']+=1
        for start in range(3):
            for balance in range(3):
                for length in range(4):
                    for word in product(range(6),repeat=length):
                        request=(start,word);base_result=oracle.path(c,request)
                        oracle.certify(functors.path_response(base,request),base_result)
                        expected_lift=independent.lift(c,costs,2,request,balance)
                        actual_lift=api.lift_path(model,request,balance);oracle.certify(actual_lift,expected_lift)
                        counts['path_attempts']+=1
                        if base_result is None:
                            self.assertIsNone(actual_lift);counts['ill_typed_paths']+=1;continue
                        counts['typed_base_paths']+=1;total=sum(costs[f] for f in word)
                        self.assertEqual(actual_lift is not None,total<=balance)
                        if actual_lift is None:counts['unaffordable_paths']+=1;continue
                        path,residual=actual_lift;self.assertEqual(residual,balance-total)
                        oracle.certify(functors.map_path(model.forgetful,path),request)
                        response=functors.path_response(model.category,path)
                        oracle.certify(response,oracle.path(expected,path))
                        oracle.certify(functors.map_response(model.forgetful,response),base_result)
                        counts['successful_lifts']+=1;counts['empty_word_lifts']+=length==0
        self.assertEqual(counts['resource_pairs'],196);self.assertEqual(counts['path_attempts'],2331)
        self.assertEqual(counts['empty_word_lifts'],9);self.assertGreater(counts['failed_pair_revivals'],0)
        word=(1,4);self.assertEqual(tuple((c[1][f],c[2][f]) for f in word),((0,1),(1,2)))
        self.assertIsNone(api.lift_path(model,(0,word),1))
        self.assertEqual(api.lift_path(model,(0,word),2)[1],0)
        f=arrows.index((1,1));g=arrows.index((4,1));bad=('seq',('arrow',f),('arrow',g))
        self.assertIsNone(core.trees.typed_eval(model.category,bad))
        self.assertIsNotNone(core.trees.typed_eval(base,functors.map_tree(model.forgetful,bad)))
        COVERAGE.update(counts)
