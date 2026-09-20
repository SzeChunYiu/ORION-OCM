"""Every small deterministic machine versus independent shortest-word pair search."""
from itertools import product
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v20 as oracle
import simulation_v20 as core
COVERAGE={}


class SimulationTests(unittest.TestCase):
    def endpoint_check(self,machine,relation,states,retained,word):
        expected=lambda xs:tuple(sorted({v for x in xs if (v:=oracle.run(machine.transitions,x,word)) is not None}))
        full,small=core.endpoints(machine,states,word),core.endpoints(machine,retained,word)
        self.assertEqual(full,expected(states));self.assertEqual(small,expected(retained))
        self.assertEqual(oracle.downset(relation,full),oracle.downset(relation,small))

    def test_all_two_action_machines(self):
        count={key:0 for key in ('simulation_machines','pair_bfs_checks','rejected_pair_witnesses',
            'refinement_stability_checks','refinement_deleted_pairs','pruning_subsets',
            'pruned_endpoint_equations','candidate_simulation_relations','greatest_pairs')}
        longest=0
        for n in range(4):
            states=tuple(range(n))
            for base in oracle.preorders(n):
                for flat in product((None,)+states,repeat=2*n):
                    transitions=tuple((flat[2*x],flat[2*x+1]) for x in states)
                    machine=core.Machine(base,transitions,2)
                    witnesses=tuple(tuple(oracle.witness(base,transitions,x,y) for y in states) for x in states)
                    expected=tuple(tuple(w is None for w in row) for row in witnesses)
                    actual,checks,deleted=core.refine(machine)
                    self.assertEqual(actual,expected)
                    self.assertEqual(core.greatest(machine),expected)
                    self.assertTrue(core.is_simulation(machine,expected))
                    depth=max((len(witnesses[x][y]) for x in states for y in states
                               if base[x][y] and witnesses[x][y] is not None),default=0)
                    self.assertEqual(checks,depth+1)
                    self.assertEqual(deleted,sum(base[x][y] and not expected[x][y] for x in states for y in states))
                    self.assertLessEqual(deleted,n*n)
                    count['refinement_stability_checks']+=checks
                    count['refinement_deleted_pairs']+=deleted
                    for x,y in product(states,repeat=2):
                        word=witnesses[x][y]
                        if word is not None:
                            self.assertLessEqual(len(word),n*n)
                            left,right=core.run(machine,x,word),core.run(machine,y,word)
                            self.assertIsNotNone(left)
                            self.assertTrue(right is None or not base[left][right])
                            count['rejected_pair_witnesses']+=1;longest=max(longest,len(word))
                        count['pair_bfs_checks']+=1
                        count['greatest_pairs']+=int(expected[x][y])
                    for subset in oracle.subsets(states):
                        retained=core.prune(machine,subset)
                        self.assertIn(retained,oracle.minimum_covers(expected,subset))
                        for word in ((),(0,),(1,)):
                            self.endpoint_check(machine,expected,subset,retained,word)
                            count['pruned_endpoint_equations']+=1
                        count['pruning_subsets']+=1
                    retained=core.prune(machine,states)
                    for word in product(range(2),repeat=2):
                        self.endpoint_check(machine,expected,states,retained,word)
                        count['pruned_endpoint_equations']+=1
                    if n<=2:
                        for bits in product((False,True),repeat=n*n):
                            relation=tuple(tuple(bits[x*n+y] for y in states) for x in states)
                            valid=all(not relation[x][y] or (base[x][y] and all(
                                transitions[x][a] is None or (transitions[y][a] is not None and
                                relation[transitions[x][a]][transitions[y][a]]) for a in range(2)))
                                for x,y in product(states,repeat=2))
                            self.assertEqual(core.is_simulation(machine,relation),valid)
                            if valid:self.assertTrue(all(not relation[x][y] or expected[x][y] for x,y in product(states,repeat=2)))
                            count['candidate_simulation_relations']+=1
                    count['simulation_machines']+=1
        self.assertEqual((count['simulation_machines'],count['pair_bfs_checks'],count['pruning_subsets'],
                          count['pruned_endpoint_equations']),(119113,1070356,951577,3331183))
        count['maximum_distinguishing_word_length']=longest
        COVERAGE.update(count)


if __name__=='__main__':
    result=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not result.result.wasSuccessful())
