"""Every small family, available universe, intervention and private witness."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v22 as o
import families_v22 as f
COVERAGE={}


class FamilyTests(unittest.TestCase):
    def test_exhaustive(self):
        counts=dict(families=0,enabled_cases=0,addition_candidates=0,deletion_candidates=0,
                    private_member_probes=0,minimal_addition_sets=0,minimal_blocker_sets=0,relabel_cases=0)
        for q in range(4):
            for records in o.families(q):
                counts['families']+=1
                self.assertEqual(f.minimal_supports(records,q),o.minimal_supports(records))
                reduced=tuple((j,s) for j,(s,_) in enumerate(o.minimal_supports(records)))
                for available in o.subsets(range(q)):
                    self.assertEqual(f.survivors(records,available,q),o.survivors(records,available))
                    self.assertEqual(bool(o.survivors(records,available)),bool(o.survivors(reduced,available)))
                    counts['enabled_cases']+=1
                    blockers=o.blockers(records,available)
                    self.assertEqual(f.minimal_blockers(records,available,q),blockers)
                    counts['minimal_blocker_sets']+=len(blockers)
                    for blocked in o.subsets(available):
                        expected=not o.survivors(records,tuple(x for x in available if x not in blocked))
                        self.assertEqual(f.blocks(records,available,blocked,q),expected)
                        cert=f.blocker_certificate(records,available,blocked,q)
                        self.assertEqual(cert,o.certificate(records,available,blocked))
                        private=all(any(set(s)<=set(available) and set(s)&set(blocked)=={b} for _,s in records) for b in blocked)
                        self.assertEqual(blocked in blockers,expected and private)
                        counts['deletion_candidates']+=1;counts['private_member_probes']+=len(blocked)
                    for baseline in o.subsets(available):
                        additions=o.additions(records,baseline,available)
                        self.assertEqual(f.minimal_additions(records,baseline,available,q),additions)
                        counts['minimal_addition_sets']+=len(additions)
                        for added in o.subsets(x for x in available if x not in baseline):
                            actual=bool(f.survivors(records,tuple(sorted(baseline+added)),q))
                            self.assertEqual(actual,any(set(s)<=set(available) and set(s)-set(baseline)<=set(added) for _,s in records))
                            counts['addition_candidates']+=1
                    renamed=tuple((i,tuple(q-1-x for x in s)) for i,s in reversed(records))
                    r_available=tuple(q-1-x for x in available)
                    self.assertEqual(f.survivors(renamed,r_available,q),o.survivors(records,available))
                    self.assertEqual(f.minimal_blockers(renamed,r_available,q),tuple(sorted(tuple(sorted(q-1-x for x in b)) for b in blockers)))
                    counts['relabel_cases']+=1
        self.assertEqual(tuple(counts[k] for k in ('families','enabled_cases','addition_candidates','deletion_candidates','private_member_probes')),(278,2122,16658,7070,7012))
        COVERAGE.update(counts)


if __name__=='__main__':
    import json
    r=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not r.result.wasSuccessful())
