"""Actual gated V8 traces, all unary words and every cut."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle_v22 as o
import core_v22 as core
import execution_v22 as e
COVERAGE={}


class ExecutionTests(unittest.TestCase):
    def test_exhaustive(self):
        counts=dict(tables=0,executions=0,word_cuts=0,successful_traces=0,failed_traces=0)
        for rows,requirements in o.machines(2,1,2):
            base=core.LegacyMachine((0,1),rows)
            spec=core.PermissionMachine(base,2,requirements)
            counts['tables']+=1
            for enabled in o.subsets(range(2)):
                gated=e.gate(spec,enabled)
                self.assertEqual(gated.observations,base.observations)
                for s in range(2):
                    expected=rows[s][0] if rows[s][0] is not None and set(requirements[s][0])<=set(enabled) else None
                    self.assertEqual(gated.transitions[s][0],expected)
                    for length in range(5):
                        word=(0,)*length
                        trace,run=o.execute((0,1),rows,requirements,s,word,enabled)
                        raw,base_run=o.execute((0,1),rows,requirements,s,word)
                        self.assertEqual(e.support(spec,s,word),base_run)
                        self.assertEqual(core.legacy.run(gated,s,word),trace)
                        enabled_run=base_run is not None and set(base_run[1])<=set(enabled)
                        self.assertEqual(run is not None,enabled_run)
                        if run is not None:
                            self.assertEqual(trace,raw);counts['successful_traces']+=1
                        else:counts['failed_traces']+=1
                        for cut in range(length+1):
                            first=e.support(spec,s,word[:cut])
                            second=None if first is None else e.support(spec,first[0],word[cut:])
                            composed=None if second is None else (second[0],tuple(sorted(set(first[1])|set(second[1]))))
                            self.assertEqual(composed,base_run);counts['word_cuts']+=1
                        counts['executions']+=1
        self.assertEqual((counts['tables'],counts['executions'],counts['word_cuts']),(81,3240,9720))
        self.assertEqual(counts['successful_traces']+counts['failed_traces'],3240)
        COVERAGE.update(counts)


if __name__=='__main__':
    import json
    r=unittest.main(exit=False,verbosity=2);print(json.dumps(COVERAGE,sort_keys=True))
    raise SystemExit(not r.result.wasSuccessful())
