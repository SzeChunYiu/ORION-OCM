"""Eight authored cases; no corpus data or native verifier is imported."""
from pathlib import Path
import copy,json,os,sys,unittest
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/"vendor")]
from authored_fixture import fixture,context,shared_fixture,double_shared
from hole_match import match
from replacement import emit_one

class Controls(unittest.TestCase):
    def invoke(self,f,c=None):
        work={};r=match(f["body"],f["pattern"],f["lemma"],f["trace"],f["target_contracts"],
                       f["target"],context(f) if c is None else c,work)
        self.assertFalse(r["native_acceptance"]);return r,work
    def emit(self,f,r,path=None):
        work={}
        return emit_one(f["body"],f["pattern"],f["lemma"],f["trace"],f["target_contracts"],context(f),
                        r["binding"],[3] if path is None else path,
                        {h["label"]:"issued-"+h["label"] for h in f["source"]["essential"]},work),work

    def test_01_composite_and_proof_holes_repair_flattening(self):
        f=fixture();r,w=self.invoke(f);self.assertEqual(r["status"],"MATCH_PROPOSAL")
        self.assertEqual(r["binding"]["substitution"],{"V0":["(","a","op","b",")"],"V1":["c"],"V2":["a"]})
        # Manual ordinary assertion sequence includes syn/argument inside holes.
        actual=[t for t in f["candidate_proof"] if t in f["ordinary"]]
        self.assertNotEqual(actual,["step1","step2"])
        e,_=self.emit(f,r);self.assertEqual(e["status"],"REPLACEMENT_PROPOSAL")
        expected=["fa","fb","syn","fc","fa", # untouched outer floats
                  "fa","fb","syn","fc","fa", # lemma floating arguments
                  "fa","fb","syn","fc","fa","issued-ht","argument",
                  "learned-cut","outer"]
        self.assertEqual(e["proof"],expected);self.assertFalse(e["native_acceptance"])

    def test_02_repeated_and_noninjective_bindings(self):
        f=fixture(repeated=True);r,_=self.invoke(f);self.assertEqual(r["status"],"MATCH_PROPOSAL")
        self.assertEqual(r["binding"]["substitution"]["V0"],r["binding"]["substitution"]["V1"])
        # Different target syntax proof trees for repeated V0 still have equal expressions.
        from structural_fixture import trace_from_proof
        f=fixture();proof=list(f["proof"]);loc=proof.index("step1")
        # Insert identity syntax on first candidate V0 argument, preserving its expression.
        pos=5+3;proof.insert(pos,"syntax-id");f["target_contracts"]["syntax-id"]=f["ordinary"]["syntax-id"]
        f["trace"]=trace_from_proof(f["source"],f["target_contracts"],proof);f["target"]=len(proof)-2
        r,_=self.invoke(f);self.assertEqual(r["status"],"MATCH_PROPOSAL")
        f=fixture(inconsistent=True);r,_=self.invoke(f);self.assertEqual(r["status"],"NO_MATCH")

    def test_03_exact_essentials_and_ordered_duplicate_slots(self):
        f=fixture();f["trace"]["nodes"][f["target"]]["obligations"][-1]["expected"]=["|-","wrong"]
        r,_=self.invoke(f);self.assertEqual(r["status"],"CANNOT_CHECK")
        f=fixture();r,_=self.invoke(f);self.assertEqual(r["status"],"MATCH_PROPOSAL")
        # A saved binding with a wrong essential argument cannot authorize emission.
        forged=copy.deepcopy(r);forged["binding"]["essential_arguments"]=[0]
        e,_=self.emit(f,forged);self.assertEqual(e["status"],"CANNOT_CHECK")
        e,_=self.emit(f,r);self.assertEqual(e["proof"].count("issued-ht"),1)

    def test_04_lemma_floating_order(self):
        f=fixture();fs=f["lemma"]["floating"];f["lemma"]["floating"]=[fs[2],fs[0],fs[1]]
        r,_=self.invoke(f);self.assertEqual(r["status"],"MATCH_PROPOSAL")
        e,_=self.emit(f,r);self.assertEqual(e["status"],"REPLACEMENT_PROPOSAL")
        expected=["fa","fb","syn","fc","fa","fa","fa","fb","syn","fc",
                  "fa","fb","syn","fc","fa","issued-ht","argument","learned-cut","outer"]
        self.assertEqual(e["proof"],expected)

    def test_05_assertion_kinds_and_type_scope(self):
        for kind in ("$a","$p"):
            f=fixture(root_kind=kind);r,_=self.invoke(f);self.assertEqual(r["status"],"MATCH_PROPOSAL")
        f=fixture();f["target"]=f["trace"]["root"];r,_=self.invoke(f);self.assertEqual(r["status"],"NO_MATCH")
        f=fixture();f["trace"]["nodes"][0]["output"][0]="class"
        r,_=self.invoke(f);self.assertEqual(r["status"],"CANNOT_CHECK")

    def test_06_unsupported_native_boundaries(self):
        f=fixture();f["trace"]["source"]["active_dv"]=[["a","b"]]
        r,_=self.invoke(f);self.assertEqual((r["status"],r["reason"]),("UNKNOWN","UNSUPPORTED_DV"))
        f=fixture();f["trace"]["source"]["floating"].append({"label":"fd","statement":["wff","d"]})
        r,_=self.invoke(f);self.assertEqual(r["status"],"UNKNOWN")
        f=fixture(missing=True);r,_=self.invoke(f)
        self.assertEqual((r["status"],r["reason"]),("UNKNOWN","ARGUMENT_WITNESS_MISSING"))

    def test_07_one_occurrence_in_shared_graph(self):
        f=shared_fixture();original=copy.deepcopy(f["trace"]);r,_=self.invoke(f);self.assertEqual(r["status"],"MATCH_PROPOSAL")
        e,_=self.emit(f,r,[4]);self.assertEqual(e["status"],"REPLACEMENT_PROPOSAL")
        # The first occurrence stays expanded; only the shared second occurrence changes.
        original_first=[("issued-ht" if x=="ht" else x) for x in f["candidate_proof"]]
        expected=["fa","fb","syn","fc","fa"]+original_first+[
            "fa","fb","syn","fc","fa","fa","fb","syn","fc","fa","issued-ht","argument","learned-cut","join"]
        self.assertEqual(e["proof"],expected);self.assertEqual(e["replacement_applications"],1)
        self.assertGreater(e["source_application_occurrences"],1);self.assertEqual(f["trace"],original)
        self.assertEqual(e["normal_labels"],len(expected))

    def test_08_custody_graph_and_resource_refusals(self):
        f=fixture();c=context(f);f["lemma"]["label"]="changed"
        r,_=self.invoke(f,c);self.assertEqual(r["status"],"CANNOT_CHECK")
        f=fixture();f["trace"]["nodes"][f["target"]]["inputs"][0]=f["target"]
        r,_=self.invoke(f);self.assertEqual(r["status"],"CANNOT_CHECK")
        f=fixture();f["trace"]["nodes"]*=10
        r,_=self.invoke(f);self.assertEqual(r["status"],"UNKNOWN")
        f=shared_fixture()
        for _ in range(8):double_shared(f)
        self.assertLess(len(f["trace"]["nodes"]),256)
        r,_=self.invoke(f);self.assertEqual(r["status"],"CANNOT_CHECK")
        self.assertIn("normal proof output bound",r["reason"])
        f=fixture();r,_=self.invoke(f);e,_=self.emit(f,r,[99]);self.assertEqual(e["status"],"CANNOT_CHECK")
        f=fixture();r,_=self.invoke(f);self.assertEqual(r["status"],"MATCH_PROPOSAL")

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Controls);ids=[t.id() for t in suite]
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt={"tests":ids,"tests_run":result.testsRun,"passed":result.wasSuccessful(),
      "failures":[(t.id(),v) for t,v in result.failures],"errors":[(t.id(),v) for t,v in result.errors],
      "pid":os.getpid(),"parent_pid":os.getppid(),"cwd":os.getcwd(),"python":sys.executable,
      "imported_modules":{n:str(Path(m.__file__).resolve()) for n,m in sys.modules.items() if getattr(m,"__file__",None)},
      "native_calls":0,"scope":"Authored structural replay only; legacy NATIVE_VERIFIED fixture marker is not authority."}
    with Path(sys.argv[1]).open("x") as f:f.write(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    raise SystemExit(0 if result.wasSuccessful() else 1)
