"""One affected authored two-slot control, with independently stated proof order."""
from pathlib import Path
import copy,json,os,sys,unittest
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/"vendor")]
from authored_fixture import fixture,context
from structural_fixture import trace_from_proof
from hole_match import match
from replacement import emit_one
OBSERVATIONS={}
def write(p,v):
    with p.open("x") as f:f.write(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n")
class Controls(unittest.TestCase):
    def test_distinct_equal_statement_slots_and_different_proofs(self):
        f=fixture();b=f["body"]
        b["premises"].append(list(b["premises"][0]))
        f["lemma"]["essential"].append({"label":"lemma-h1","statement":list(f["lemma"]["essential"][0]["statement"])})
        b["nodes"].insert(4,{"kind":"hole","slot":1,"output":list(b["premises"][1])})
        for n in b["nodes"][5:]:
            n["inputs"]=[j+1 if j>=4 else j for j in n["inputs"]]
        b["root"]+=1;b["nodes"][-1]["inputs"][-1]=4
        # First essential argument is ht itself; the second is argument(floats,ht).
        # Their statements coincide, but their emitted proof derivations differ.
        P=["fa","fb","syn","fc","fa"]
        proof=P+P+P+["ht","step1"]+P+["ht","argument","step2","outer"]
        f["trace"]=trace_from_proof(f["source"],f["target_contracts"],proof)
        f["target"]=24;c=context(f)
        inputs={k:f[k] for k in ("body","pattern","lemma","trace","target_contracts","target")}
        inputs["context"]=c;inputs["occurrence_path"]=[3]
        write(Path(sys.argv[1]).parent/"INPUTS.json",inputs)
        w={}
        r=match(f["body"],f["pattern"],f["lemma"],f["trace"],f["target_contracts"],24,c,w)
        self.assertEqual(r["status"],"MATCH_PROPOSAL")
        self.assertEqual(r["binding"]["substitution"],{"V0":["(","a","op","b",")"],"V1":["c"],"V2":["a"]})
        self.assertEqual(r["binding"]["floating_arguments"],[7,8,9])
        self.assertEqual(r["binding"]["essential_arguments"],[15,23])
        self.assertEqual(f["trace"]["nodes"][15]["output"],f["trace"]["nodes"][23]["output"])
        self.assertEqual(f["trace"]["nodes"][15]["kind"],"essential_hypothesis")
        self.assertEqual(f["trace"]["nodes"][23]["label"],"argument")
        e=emit_one(f["body"],f["pattern"],f["lemma"],f["trace"],f["target_contracts"],c,r["binding"],[3],{"ht":"issued-ht"},w)
        expected=["fa","fb","syn","fc","fa","fa","fb","syn","fc","fa","issued-ht",
                  "fa","fb","syn","fc","fa","issued-ht","argument","learned-cut","outer"]
        self.assertEqual(e["status"],"REPLACEMENT_PROPOSAL")
        self.assertEqual(e["proof"],expected)
        self.assertEqual(e["proof"].count("issued-ht"),2)
        self.assertEqual(e["proof"].count("argument"),1)
        self.assertFalse(r["native_acceptance"]);self.assertFalse(e["native_acceptance"])
        forged=copy.deepcopy(r["binding"]);forged["essential_arguments"]=[23,15]
        negative=emit_one(f["body"],f["pattern"],f["lemma"],f["trace"],f["target_contracts"],c,forged,[3],{"ht":"issued-ht"},w)
        self.assertEqual(negative["status"],"CANNOT_CHECK")
        OBSERVATIONS.update(match=r,replacement=e,swapped_binding_refusal=negative,expected_proof=expected,work=w)
if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Controls);ids=[t.id() for t in suite]
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt={"tests":ids,"tests_run":result.testsRun,"passed":result.wasSuccessful(),
      "failures":[(t.id(),v) for t,v in result.failures],"errors":[(t.id(),v) for t,v in result.errors],
      "pid":os.getpid(),"parent_pid":os.getppid(),"cwd":os.getcwd(),"python":sys.executable,
      "imported_modules":{n:str(Path(m.__file__).resolve()) for n,m in sys.modules.items() if getattr(m,"__file__",None)},
      "native_calls":0,"observations":OBSERVATIONS,"scope":"One new authored structural control; no inherited suite or native execution."}
    write(Path(sys.argv[1]),receipt)
    raise SystemExit(0 if result.wasSuccessful() else 1)
