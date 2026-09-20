"""Named missing-premise controls and concrete structural revivals."""
import unittest
from support_v29 import chain, adapter, core, named, presentation, oracle, exact
COVERAGE = {}


class ControlTests(unittest.TestCase):
    def test_presentation_naming_functors_and_resource_controls(self):
        category = chain(); n = 0
        mapping = presentation.GeneratorMap((3,((0,1),(0,2))),category,(1,2))
        result = presentation.dag_presentation(mapping)
        self.assertFalse(result.generates);self.assertIsNone(result.quote)
        self.assertEqual(len(set(result.lower.arrow_map)),len(result.lower.arrow_map))
        presentation.verify_presentation(mapping,result); n += 1
        reverse = tuple(reversed(range(6)))
        rows = tuple(tuple(None if category.table.rows[f][g] is None else
                           reverse.index(category.table.rows[f][g]) for g in reverse) for f in reverse)
        permuted = core.categories.Typed(3,tuple(category.source[i] for i in reverse),
                    tuple(category.target[i] for i in reverse),tuple(reverse.index(i) for i in category.identities),
                    core.partial.Table(rows))
        mapping = presentation.GeneratorMap((3,oracle.EDGES),permuted,tuple(reverse.index(i) for i in (1,4,2)))
        result = presentation.dag_presentation(mapping)
        self.assertNotEqual(result.lower.arrow_map,tuple(range(6)))
        for path,cls in zip(result.paths,result.class_of):
            endpoint = oracle.path_endpoint(mapping.graph,path)
            expected = reverse.index(oracle.ENDPOINTS.index((path[0],endpoint)))
            exact(self,result.lower.arrow_map[cls],expected)
        presentation.verify_presentation(mapping,result); n += 1
        singleton = core.categories.Typed(1,(0,),(0,),(0,),core.partial.Table(((0,),)))
        cyclic = presentation.GeneratorMap((1,((0,0),)),singleton,(0,))
        exact(self,presentation.evaluate_path(cyclic,(0,(0,0,0))),(0,0,0))
        with self.assertRaises(ValueError):presentation.dag_presentation(cyclic)
        n += 1
        empty = core.categories.Typed(0,(),(),(),core.partial.Table(()))
        result = presentation.dag_presentation(presentation.GeneratorMap((0,()),empty,()))
        self.assertTrue(result.generates);exact(self,result.paths,());n += 1
        parallel = presentation.GeneratorMap((2,((0,1),(0,1))),
                   core.categories.Typed(2,(0,0,1),(0,1,1),(0,2),
                   core.partial.Table(((0,1,None),(None,None,1),(None,None,2)))),(1,1))
        result = presentation.dag_presentation(parallel)
        self.assertEqual(result.class_of[result.paths.index((0,(0,)))],
                         result.class_of[result.paths.index((0,(1,)))]); n += 1
        original = adapter(); swapped = named.NamedAdapter(category,7,oracle.LABELS,(0,2,1))
        self.assertNotEqual(named.named_response(original,('empty',0)),named.named_response(swapped,('empty',0)))
        for external,obj in enumerate(oracle.OBJECTS):
            repaired = ('empty',swapped.object_decoder.index(obj))
            exact(self,named.named_response(original,('empty',external)),named.named_response(swapped,repaired))
        n += 1
        unsorted = named.NamedAdapter(category,7,tuple(reversed(oracle.LABELS)),oracle.OBJECTS)
        for i,label in enumerate(unsorted.arrow_labels):
            exact(self,named.typed_query(unsorted,('arrow',label)),('arrow',i))
            exact(self,named.named_response(unsorted,('arrow',label)),label)
        n += 1
        discrete = core.categories.Typed(2,(0,1),(0,1),(0,1),core.partial.Table(((0,None),(None,1))))
        collapse = core.functors.Functor(discrete,singleton,(0,0),(0,0))
        tree = ('seq',('empty',0),('empty',1))
        self.assertIsNone(core.trees.typed_eval(discrete,tree))
        self.assertIsNotNone(core.trees.typed_eval(singleton,core.functors.map_tree(collapse,tree)))
        identity = core.functors.Functor(discrete,discrete,(0,1),(0,1))
        self.assertIsNone(core.trees.typed_eval(discrete,core.functors.map_tree(identity,tree)));n += 1
        group = core.categories.Typed(1,(0,0),(0,0),(0,),core.partial.Table(((0,1),(1,0))))
        nonfaithful = core.functors.Functor(group,singleton,(0,),(0,0))
        for left in range(2):
            for right in range(2):
                query = ('seq',('arrow',left),('arrow',right))
                exact(self,core.trees.typed_eval(singleton,core.functors.map_tree(nonfaithful,query)),
                      core.functors.map_response(nonfaithful,core.trees.typed_eval(group,query)))
        self.assertNotEqual(core.trees.typed_eval(group,('arrow',0)),core.trees.typed_eval(group,('arrow',1)))
        n += 1
        lift = core.resources.ResourceLift(category,(0,1,2,0,1,0),2)
        a,b = (lift.arrow_labels.index((i,2)) for i in (1,4))
        query = ('seq',('arrow',a),('arrow',b))
        self.assertIsNone(core.trees.typed_eval(lift.category,query))
        exact(self,core.trees.typed_eval(category,core.functors.map_tree(lift.forgetful,query)),(0,2,2));n += 1
        lifted,residual = core.resources.lift_path(lift,(0,(1,4)),2)
        exact(self,residual,0)
        exact(self,core.functors.map_path(lift.forgetful,lifted),(0,(1,4)))
        exact(self,tuple(lift.arrow_labels[i] for i in lifted[1]),((1,2),(4,1)))
        n += 1
        self.assertIsNone(core.trees.raw_table_eval(category.table,('empty',1)));n += 1
        COVERAGE['named_structural_controls'] = n
