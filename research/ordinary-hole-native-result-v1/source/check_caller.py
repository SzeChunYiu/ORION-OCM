"""Six new authored caller controls; native verification is prohibited."""
from pathlib import Path
import copy,json,os,sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/"vendor")]
import life_native as N
from caller_bindings import verify_result,check_proposal,negative_at_issued,adapter_context
from caller_flow import prepare_replacement
from authored_fixture import fixture,serializable
import run_native
OBSERVATIONS={};ACTUAL_NATIVE_CALLS=0
def prohibited(*a,**k):
    global ACTUAL_NATIVE_CALLS
    ACTUAL_NATIVE_CALLS+=1
    raise AssertionError("Native verifier prohibited in authored qualification")
N.verify=prohibited
def checked(f):
    return verify_result(f["result"],f["claim"],f["prefix_raw"],f["database_raw"],
                         f["authority"],f["sources"],f["prefix_path"],f["archive"])

class Controls(unittest.TestCase):
    def positive(self):
        f=fixture();trace,used,prefix=checked(f);work={}
        context,found,proposal=prepare_replacement(f["definition"],f["result"],trace,used,prefix,f["authority"],work)
        return f,context,found,proposal,work
    def test_01_exact_composite_and_essential_arguments(self):
        f,c,m,p,w=self.positive()
        self.assertEqual(m["binding"]["floating_arguments"],[9,10,11])
        self.assertEqual(m["binding"]["essential_arguments"],[14,23])
        # Independent sequence: untouched outer arguments, lemma arguments, remaining route.
        expected=["wph","wps","wa","wps","wch","wa","wch",
                  "wph","wps","wa","wps","wch","wph","wps","simpr",
                  "native-hole-replacement-v1.h0","typed-admitted-0","wps","wch","simpr","syl"]
        self.assertEqual(p["proof"],expected);self.assertEqual(p["normal_labels"],21)
        self.assertFalse(p["native_acceptance"]);self.assertEqual(f["definition"]["eligible_method_ids"],[])
        trace,used,prefix=checked(f)
        self.assertIn("typed-admitted-0",prefix);self.assertNotIn("typed-admitted-0",used)
        OBSERVATIONS["positive"]={"inputs":serializable(f),"context":c,"match":m,"proposal":p,"work":w}
    def test_02_current_request_sources_and_used_contract_tamper(self):
        for change,reason in [
          (lambda f:f["result"].__setitem__("claims_sha256","0"*64),"claims digest"),
          (lambda f:f["result"]["sources"]["index"].__setitem__("sha256","0"*64),"native sources"),
          (lambda f:f["result"]["contracts"].pop("wa"),"complete current used"),
          (lambda f:f["result"]["contracts"]["wa"].__setitem__("span",[0,1]),"complete current used")]:
            f=fixture()
            f["sources"]=copy.deepcopy(f["sources"]);change(f)
            with self.assertRaisesRegex(ValueError,reason):checked(f)
        OBSERVATIONS["tamper_cases"]=4
    def test_03_exact_issued_target_and_ordered_hole(self):
        f,c,m,p,w=self.positive()
        for field,value,reason in [
          ("target",["|-","wrong"],"issued replacement target"),
          ("hypotheses",[{"label":"foreign-hole","statement":f["claim"]["premises"][0]}],"ordered holes"),
          ("hypotheses",[{"label":"native-hole-replacement-v1.h0","statement":["|-","wrong"]}],"ordered holes")]:
            bad=copy.deepcopy(p);bad[field]=value
            with self.assertRaisesRegex(ValueError,reason):check_proposal(f["definition"],bad)
        f=fixture();f["result"]["traces"][f["claim"]["label"]]["source"]["essential"][0]["statement"]=["|-","wrong"]
        with self.assertRaisesRegex(ValueError,"indexed trace source"):checked(f)
        OBSERVATIONS["target_or_hole_cases"]=4
    def test_04_shortcut_and_used_lemma_collision_refuse(self):
        f,c,m,p,w=self.positive()
        for label in (f["definition"]["source_claim"]["label"],f["definition"]["replacement_claim"]["label"]):
            bad=copy.deepcopy(p);bad["proof"]=[label]
            with self.assertRaisesRegex(ValueError,"target shortcut"):check_proposal(f["definition"],bad)
        trace,used,prefix=checked(f);used["typed-admitted-0"]=copy.deepcopy(f["definition"]["lemma"])
        with self.assertRaisesRegex(ValueError,"lemma already used"):
            adapter_context(f["definition"],f["result"],trace,used,prefix,f["authority"])
        self.assertIn("typed-admitted-0",used)
        OBSERVATIONS["shortcut_or_collision_cases"]=3
    def test_05_negative_attribution_requires_issued_label_and_full_prefix(self):
        f=fixture();labels=f["result"]["verified_labels"][:-1]
        good={"terminal":"NATIVE_REJECTED","native_calls":1,
              "error":{"stage":"native_check","pending":f["claim"]["label"]},"verified_labels":labels}
        self.assertTrue(negative_at_issued(good,f["claim"],labels))
        for mutation in (lambda x:x["error"].__setitem__("pending",labels[0]),
                         lambda x:x.__setitem__("verified_labels",labels[:-1]),
                         lambda x:x["error"].__setitem__("stage","post_custody"),
                         lambda x:x.__setitem__("native_calls",0)):
            bad=copy.deepcopy(good);mutation(bad);self.assertFalse(negative_at_issued(bad,f["claim"],labels))
        OBSERVATIONS["negative_cases"]=5
    def test_06_entry_refuses_missing_gate_before_prefix_or_native(self):
        with tempfile.TemporaryDirectory(prefix="hole-caller-control-") as d:
            request=Path(d)/"request.json";missing=Path(d)/"missing-root-gate.json"
            request.write_text(json.dumps({"gate":str(missing)}))
            with patch.object(sys,"argv",[str(ROOT/"run_native.py"),str(request)]):
                with self.assertRaises(FileNotFoundError):run_native.main()
            self.assertEqual(sorted(p.name for p in Path(d).iterdir()),["request.json"])
        self.assertEqual(ACTUAL_NATIVE_CALLS,0);OBSERVATIONS["missing_gate_refused"]=True

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Controls);ids=[t.id() for t in suite]
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt={"tests":ids,"tests_run":result.testsRun,"passed":result.wasSuccessful(),
      "failures":[(t.id(),v) for t,v in result.failures],"errors":[(t.id(),v) for t,v in result.errors],
      "pid":os.getpid(),"parent_pid":os.getppid(),"cwd":os.getcwd(),"python":sys.executable,
      "imported_modules":{n:str(Path(m.__file__).resolve()) for n,m in sys.modules.items() if getattr(m,"__file__",None)},
      "native_calls":ACTUAL_NATIVE_CALLS,"scope":"Synthetic native-shaped records only; their saved markers are never native evidence.",
      "observations":OBSERVATIONS}
    with Path(sys.argv[1]).open("x") as f:f.write(json.dumps(receipt,sort_keys=True,indent=2,allow_nan=False)+"\n")
    raise SystemExit(0 if result.wasSuccessful() else 1)
