"""Only changed cached output/history/import branches; authored JSON, no parser imports."""
from pathlib import Path
import copy,hashlib,json,os,sys,tempfile,unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from output_contract import inspect_outputs
def write(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+"\n")
def bound(p):
 raw=p.read_bytes();return {"path":str(p),"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
class OutputControls(unittest.TestCase):
 def setUp(self):
   self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.out=self.base/"outputs";self.out.mkdir()
   self.root=self.base/"project";self.runtime=self.base/"runtime";self.pin={"bytes":1,"sha256":"authored"}
   self.body={"parameters":[],"query":["toy"],"premises":[]}
   parent=[{"label":"syntax"},{"label":"whole-demonstrated"},{"label":"ordinary"},{"label":"other"}]
   pp=self.base/"P1.json";write(pp,parent)
   before={"roots":[{"ordinal":4120,"label":"root","cuts":[{"status":"CUT_PROPOSAL","canonical_id":"repeated","body":self.body} for _ in range(76)]}],
    "P1_contracts":{k:v for k,v in bound(pp).items() if k!="path"},"wall_s":0.5,"work":{"original":7}}
   pr=self.base/"prior.json";write(pr,before)
   outer=self.base/"outer.json";write(outer,{"window":1.0})
   caller=self.base/"caller.json";write(caller,{"window":1.5})
   prior_screen=self.base/"prior-screen.json";write(prior_screen,{"measured_driver_wall_s":60.004,"work":{"parse_calls":11},"contexts":[{"parameter":"authored","parse_calls":11}]})
   prior_outer=self.base/"prior-screen-outer.json";write(prior_outer,{"window":60.5})
   prior_caller=self.base/"prior-screen-caller.json";write(prior_caller,{"window":61.0})
   self.request={"syntax_method":"functools.cache.completed-syntax-results.v1","inputs":{"previous_result":bound(pr),"P1_contracts":bound(pp),"previous_outer_process":bound(outer),"previous_caller_process":bound(caller),"prior_screen_result":bound(prior_screen),"prior_screen_outer_process":bound(prior_outer),"prior_screen_caller_process":bound(prior_caller)},
    "P1_count":4,"proposal_occurrences":76,"sources":{"run_screening.py":{},"source/screen.py":{},"source/syntax_memo.py":{}},
    "runtime":{"path":str(self.runtime),"files":{"lark/__init__.py":{}}},
    "python":{"path":sys.executable}}
   h=hashlib.sha256(json.dumps(self.body,sort_keys=True,separators=(",",":")).encode()).hexdigest()
   rows=[{"occurrence_index":i,"root_index":0,"root_ordinal":4120,"root_label":"root","cut_index":i,"canonical_id":"repeated","body_sha256":h,
     "screen":{"status":"UNKNOWN","coverage_complete":False,"grammar_coverage_complete":True,"P1_total":4,"P1_visited":2,
      "aliases":[],"native_acceptance":False,"new_native_admissions":0}} for i in range(76)]
   self.result={"contexts":[{"error":None,"syntax_cache":{"namespace":["authored-library","authored-context"],"primitive":"functools._lru_cache_wrapper","cache_info":{"hits":2,"misses":3,"currsize":3,"maxsize":None}}}],"syntax_method":self.request["syntax_method"],"schema":"ordinary.retained-screening-result.v1","terminal":"ALL_RETAINED_SCREENING_OCCURRENCES_RECORDED","rows":rows,"pid":99,
    "request":self.pin,"cwd":str(self.root),"inputs":self.request["inputs"],"P1_count":4,"occurrence_count":76,"native_calls":0,"new_native_admissions":0,
    "previous_costs":{"driver_wall_s":0.5,"work":{"original":7},"outer_process":{"window":1.0},"caller_process":{"window":1.5}},
    "prior_screen_costs":{"driver_wall_s":60.004,"work":{"parse_calls":11},"contexts":[{"parameter":"authored","parse_calls":11}],"outer_process":{"window":60.5},"caller_process":{"window":61.0}},
   "imported_modules":{"__main__":str(self.root/"run_screening.py"),"screen":str(self.root/"source/screen.py"),"syntax_memo":str(self.root/"source/syntax_memo.py"),"lark":str(self.runtime/"lark/__init__.py")},
    "inputs_unchanged":True,"sources_unchanged":True,"runtime_unchanged":True,"request_unchanged":True}
 def tearDown(self):self.tmp.cleanup()
 def emit(self,n=None):
   for p in self.out.iterdir():p.unlink()
   rows=self.result["rows"];write(self.out/"RESULT.json",self.result)
   for i,row in enumerate(rows[:len(rows) if n is None else n]):write(self.out/("SCREEN-"+str(i)+".json"),row)
 def inspect(self):return inspect_outputs(self.out,99,self.pin,self.request,self.root)
 def test_complete_cached_history_and_import(self):
  self.emit();r=self.inspect()
  self.assertTrue(r["completed_contract"]);self.assertTrue(r["previous_costs_preserved"])
  self.assertTrue(r["prior_screen_costs_preserved"]);self.assertTrue(r["declared_import_paths_ok"])
  self.assertEqual(r["emitted_rows"],76)
 def test_each_new_history_component_is_bound(self):
  saved=copy.deepcopy(self.result["prior_screen_costs"])
  for key in ("driver_wall_s","work","contexts","outer_process","caller_process"):
   with self.subTest(component=key):
    self.result["prior_screen_costs"]=copy.deepcopy(saved);self.result["prior_screen_costs"].pop(key)
    self.emit();r=self.inspect();self.assertFalse(r["completed_contract"]);self.assertFalse(r["prior_screen_costs_preserved"])
  self.result["prior_screen_costs"]=saved
  self.request["inputs"]["prior_screen_result"]["sha256"]="tampered"
  self.emit();r=self.inspect();self.assertFalse(r["completed_contract"]);self.assertTrue(r["errors"])
 def test_cached_discriminator_cannot_be_absent_or_substituted(self):
  for replacement in (None,"uncached"):
   with self.subTest(method=replacement):
    self.result["syntax_method"]=replacement;self.emit();self.assertFalse(self.inspect()["completed_contract"])
  self.result["syntax_method"]=self.request["syntax_method"]="uncached"
  self.emit();self.assertFalse(self.inspect()["completed_contract"])
 def test_new_cache_module_must_be_current(self):
  for path in (None,"/unexpected/syntax_memo.py"):
   with self.subTest(path=path):
    self.result["imported_modules"]["syntax_memo"]=path;self.emit();r=self.inspect()
    self.assertFalse(r["completed_contract"]);self.assertFalse(r["declared_import_paths_ok"])
 def test_new_cache_report_must_be_retained(self):
  self.result["contexts"][0].pop("syntax_cache");self.emit();r=self.inspect()
  self.assertFalse(r["completed_contract"]);self.assertFalse(r["cache_reports_present"])
if __name__=="__main__":
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(OutputControls);ids=[t.id() for t in suite]
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 modules={n:str(Path(m.__file__).resolve()) for n,m in sys.modules.items() if getattr(m,"__file__",None)}
 receipt={"pid":os.getpid(),"parent_pid":os.getppid(),"cwd":os.getcwd(),"python":sys.executable,
  "tests":ids,"tests_run":result.testsRun,"passed":result.wasSuccessful(),"imported_modules":modules}
 with (HERE/"qualification-01/CONTROL-RESULT.json").open("x") as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write("\n")
 raise SystemExit(0 if result.wasSuccessful() else 1)
