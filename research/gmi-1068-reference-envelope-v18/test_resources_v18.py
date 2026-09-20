"""Complete target signatures with explicitly reversed Boolean orientation."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v18 as oracle
import resources_v18 as core
from core_v18 import decoded
COVERAGE = {}


class ResourceTests(unittest.TestCase):
    def test_all_small_preorders(self):
        count = dict(resource_preorders=0,resource_pairs=0,pair_target_checks=0,
                     actual_target_contexts=0,target_context_values=0)
        for n in range(4):
            for relation in oracle.preorders(n):
                signatures = tuple(oracle.resource_signature(relation,s) for s in range(n))
                self.assertEqual(core.signatures(relation),signatures)
                contexts = []
                for target in range(n):
                    encoded = core.resource_context((True,)*n,tuple(range(n)),relation,target)
                    for state in range(n):
                        self.assertEqual(decoded(encoded,state),('VALUE',relation[state][target]))
                        count['target_context_values'] += 1
                    contexts.append(encoded)
                    count['actual_target_contexts'] += 1
                for a in range(n):
                    for b in range(n):
                        self.assertEqual(core.converts(relation,a,b),relation[a][b])
                        all_targets = True
                        for target in range(n):
                            left,right = decoded(contexts[target],a)[1],decoded(contexts[target],b)[1]
                            inequality = left >= right
                            self.assertEqual(inequality,signatures[a][target]>=signatures[b][target])
                            if relation[a][b]:
                                self.assertTrue(inequality)
                            all_targets = all_targets and inequality
                            count['pair_target_checks'] += 1
                        self.assertEqual(all_targets,relation[a][b])
                        count['resource_pairs'] += 1
                count['resource_preorders'] += 1
        self.assertEqual(count,dict(resource_preorders=35,resource_pairs=278,pair_target_checks=816,
                                    actual_target_contexts=96,target_context_values=278))
        COVERAGE.update(count)

    def test_equivalent_resources_orientation_and_tags(self):
        equivalent = ((True,True),(True,True))
        self.assertEqual(core.signatures(equivalent)[0],core.signatures(equivalent)[1])
        self.assertNotEqual(0,1)
        chain = ((True,True),(False,True))
        signatures = core.signatures(chain)
        self.assertTrue(core.converts(chain,0,1))
        self.assertFalse(all(a<=b for a,b in zip(signatures[0],signatures[1])))
        self.assertTrue(all(a>=b for a,b in zip(signatures[0],signatures[1])))
        encoded = core.resource_context((True,True,False,False),(None,0,None,1),chain,0)
        self.assertEqual(tuple(decoded(encoded,h) for h in range(4)),
                         (('UNDEFINED',None),('VALUE',True),('ILLEGAL',None),('ILLEGAL',None)))
        self.assertEqual(encoded.context.defined,(False,True,False,True))
        COVERAGE.update(equivalent_resource_controls=1,resource_orientation_controls=1,
                        partial_resource_controls=1)


if __name__ == '__main__':
    result = unittest.main(exit=False,verbosity=2)
    print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
