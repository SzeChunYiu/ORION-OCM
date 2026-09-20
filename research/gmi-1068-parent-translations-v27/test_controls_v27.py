"""Actual prior-library system forgetting, optional probability loss, and resource-state controls."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from fractions import Fraction as F
from itertools import product
import unittest
from support_v27 import core
COVERAGE={}


def thin_category(n,pairs):
    rows=tuple(tuple(pairs.index((a,d)) if b==c else None for c,d in pairs) for a,b in pairs)
    return core.Typed(n,tuple(a for a,b in pairs),tuple(b for a,b in pairs),
                      tuple(pairs.index((i,i)) for i in range(n)),core.Table(rows))


class BridgeControls(unittest.TestCase):
    def test_actual_system_and_parent_bridges(self):
        outputs=(False,True)
        # A singleton Bool-output system has only its singleton successor function.
        source_pairs=tuple((i,j) for i,j in product(range(2),repeat=2) if outputs[i]==outputs[j])
        source=thin_category(2,source_pairs)
        forgotten=thin_category(1,((0,0),))
        tagged=thin_category(2,tuple(product(range(2),repeat=2)))
        collapse=core.functors.Functor(source,forgotten,(0,0),(0,0))
        retain=core.functors.Functor(source,tagged,(0,1),(0,3))
        self.assertFalse(core.functors.object_injective(collapse))
        self.assertTrue(core.functors.object_injective(retain))
        # Faithfulness is Hom-wise injection, even though distinct objects collapse.
        for i,j in product(range(2),repeat=2):
            hom=tuple(k for k,(a,b) in enumerate(source_pairs) if(a,b)==(i,j))
            self.assertEqual(len({collapse.arrow_map[k] for k in hom}),len(hom))
        failed=('seq',('empty',0),('empty',1))
        eval=core.core26.trees.typed_eval
        self.assertIsNone(eval(source,failed))
        self.assertEqual(eval(forgotten,core.functors.map_tree(collapse,failed)),(0,0,0))
        self.assertIsNone(eval(tagged,core.functors.map_tree(retain,failed)))
        preserved=0
        for i in range(2):
            tree=('seq',('empty',i),('arrow',i))
            self.assertEqual(eval(tagged,core.functors.map_tree(retain,tree)),
                             core.functors.map_response(retain,eval(source,tree)))
            preserved+=1
        a=core.Kernel(1,2,((F(1,3),F(2,3)),))
        b=core.Kernel(1,2,((F(2,3),F(1,3)),))
        self.assertNotEqual(a,b);self.assertEqual(core.stochastic.support(a),core.stochastic.support(b))
        chainpairs=tuple((i,j) for i in range(3) for j in range(i,3))
        chain=thin_category(3,chainpairs)
        lift=core.resources.ResourceLift(chain,tuple(j-i for i,j in chainpairs),2)
        f,g=chainpairs.index((0,1)),chainpairs.index((1,2))
        bad=(lift.arrow_labels.index((f,2)),lift.arrow_labels.index((g,2)))
        self.assertIsNone(core.core26.old_partial.word(lift.category.table,bad))
        self.assertEqual(core.core26.old_partial.word(chain.table,(f,g)),chainpairs.index((0,2)))
        path,residual=core.resources.lift_path(lift,(0,(f,g)),2)
        self.assertEqual(residual,0)
        self.assertEqual(tuple(lift.arrow_labels[i] for i in path[1]),((f,2),(g,1)))
        self.assertIsNotNone(core.functors.path_response(lift.category,path))
        COVERAGE.update(system_failure_revivals=1,system_tagged_preservations=1,
                        lawful_system_compositions=preserved,probability_loss_controls=1,
                        resource_boundary_controls=2)
