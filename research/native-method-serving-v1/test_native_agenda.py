"""Independent bounded rule-tree oracles and indexed scheduler controls."""
import functools
import importlib.util
import itertools
from pathlib import Path
import unittest
from vendor import common as C
F=C.load('finite_search')
BANK={'wff':[{'tokens':[x]} for x in ('f0','f1','f2')]}
def action(name,head,tail):return {'id':name,'kind':'primitive','label':name,'substitution':{},'query':head,'premises':tail}
def task(seeds,head):return {'premises':[['|-','f'+str(i)] for i in seeds],'query':['|-','f'+str(head)]}
def recurrence(actions,seeds,head,bound):
    costs={s:0 for s in seeds}
    for _ in range(bound):
        nxt=dict(costs)
        for a in actions:
            if all(p in costs for p in a['premises']):
                cost=1+sum(costs[p] for p in a['premises'])
                if cost<=bound:nxt[a['query']]=min(nxt.get(a['query'],bound+1),cost)
        costs=nxt
    return costs.get(head)
def enumeration(actions,seeds,head,bound):
    # Every recursive rule consumes one unit; thus positive cycles terminate by
    # decreasing remaining budget, without heap/readiness/finalization machinery.
    @functools.lru_cache(None)
    def trees(head,remaining):
        if remaining<0:return frozenset()
        result={0} if head in seeds else set()
        if remaining:
            for a in actions:
                if a['query']!=head:continue
                choices=[trees(p,remaining-1) for p in a['premises']]
                for costs in itertools.product(*choices):
                    cost=1+sum(costs)
                    if cost<=remaining:result.add(cost)
        return frozenset(result)
    values=trees(head,bound)
    return min(values) if values else None
class AgendaControls(unittest.TestCase):
    def setUp(self):
        path=C.HERE/'indexed_agenda.py'
        if not path.is_file():raise AssertionError('missing indexed agenda implementation')
        self.A=C.load('indexed_agenda')
    def check(self,actions,seeds,head,bound=8,bank=BANK):
        expected=enumeration(actions,tuple(seeds),head,bound)
        self.assertEqual(recurrence(actions,seeds,head,bound),expected)
        old=F.search(actions,bank,task(seeds,head),{},bound)
        work={};new=self.A.search(actions,bank,task(seeds,head),work,bound)
        self.assertEqual(old.get('decision_count'),expected);self.assertEqual(new.get('decision_count'),expected)
        self.assertEqual(old['terminal'],new['terminal']);return new,work
    def test_repeated_premise_multiplicity(self):
        got,work=self.check([action('a',1,[0]),action('b',2,[1,1])],[0],2)
        self.assertEqual(got['decision_count'],3);self.assertEqual(work['index_premise_incidences'],3)
        self.assertEqual(work['visited_premise_incidences'],3)
    def test_empty_rule_seeds_positive_cycle(self):
        got,_=self.check([action('a',0,[]),action('b',1,[0]),action('c',0,[1]),action('d',2,[1])],[],2)
        self.assertEqual(got['decision_count'],3)
    def test_unseeded_cycle_is_unreachable(self):
        got,_=self.check([action('a',0,[1]),action('b',1,[0]),action('c',2,[0])],[],2)
        self.assertEqual(got['terminal'],'NO_PROOF_WITHIN_BOUND')
    def test_parallel_rules_are_distinct_and_tie_stable(self):
        actions=[action('z',1,[0]),action('a',1,[0]),action('b',2,[1])]
        got,work=self.check(actions,[0],2)
        self.assertEqual(got['derivation']['parents'][0]['action']['label'],'a')
        self.assertEqual(work['index_action_records'],3)
    def test_supplied_target_has_zero_cost(self):
        got,_=self.check([action('a',1,[0])],[0,1],1);self.assertEqual(got['decision_count'],0)
    def test_cutoff_counts_repeated_tree_cost(self):
        actions=[action('a',1,[0]),action('b',2,[1,1])]
        self.assertEqual(self.check(actions,[0],2,2)[0]['terminal'],'NO_PROOF_WITHIN_BOUND')
        self.assertEqual(self.check(actions,[0],2,3)[0]['decision_count'],3)
    def test_unreachable_head(self):self.check([action('a',1,[0])],[0],2)
    def test_derived_fact_supplied_directly_wins(self):
        got,_=self.check([action('a',0,[]),action('b',1,[0]),action('c',2,[1,1])],[1],2)
        self.assertEqual(got['decision_count'],1)
    def test_exhaustive_listed_tail_two_rule_three_fact_cases(self):
        tails=[[],[0],[1],[2],[0,0],[0,1],[1,0],[1,1],[2,2]]
        rules=[action('r'+str(i),h,t) for i,(h,t) in enumerate(itertools.product(range(3),tails))]
        count=0
        for a,b in itertools.combinations(rules,2):
            for seeds in ([],[0],[1]):
                for head in range(3):self.check([a,b],seeds,head,4);count+=1
        self.assertEqual(count,3159)
    def test_exact_eight_nine_boundary(self):
        bank={'wff':[{'tokens':['f'+str(i)]} for i in range(10)]}
        actions=[action('r'+str(i),i,[i-1]) for i in range(1,10)]
        self.assertEqual(self.check(actions,[0],8,8,bank)[0]['decision_count'],8)
        self.assertEqual(self.check(actions,[0],9,8,bank)[0]['terminal'],'NO_PROOF_WITHIN_BOUND')
    def test_late_cheaper_candidate_and_stale_queue_entry(self):
        bank={'wff':[{'tokens':['f'+str(i)]} for i in range(4)]}
        actions=[action('a',1,[0]),action('z-expensive',2,[1,1,1]),
                 action('b-cheaper',2,[1]),action('c',3,[2,2])]
        got,work=self.check(actions,[0],3,8,bank)
        self.assertEqual(got['decision_count'],5);self.assertGreater(work['stale_queue_entries'],0)
    def test_bank_miss_refuses(self):
        with self.assertRaisesRegex(ValueError,'BANK_INCOMPLETE'):
            self.A.search([],BANK,{'premises':[],'query':['|-','outside']},{})
if __name__=='__main__':unittest.main(verbosity=2)
