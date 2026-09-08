"""Nine authored output branches; no actual screen input or research module imported."""
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
  self.request={"inputs":{"previous_result":bound(pr),"P1_contracts":bound(pp),"previous_outer_process":bound(outer),"previous_caller_process":bound(caller)},
   "P1_count":4,"proposal_occurrences":76,"sources":{"run_screening.py":{},"source/screen.py":{}},
   "runtime":{"path":str(self.runtime),"files":{"lark/__init__.py":{}}},
   "python":{"path":sys.executable}}
  h=hashlib.sha256(json.dumps(self.body,sort_keys=True,separators=(",",":")).encode()).hexdigest()
  rows=[{"occurrence_index":i,"root_index":0,"root_ordinal":4120,"root_label":"root","cut_index":i,"canonical_id":"repeated","body_sha256":h,
    "screen":{"status":"UNKNOWN","coverage_complete":False,"grammar_coverage_complete":True,"P1_total":4,"P1_visited":2,
     "aliases":[],"native_acceptance":False,"new_native_admissions":0}} for i in range(76)]
  self.result={"schema":"ordinary.retained-screening-result.v1","terminal":"ALL_RETAINED_SCREENING_OCCURRENCES_RECORDED","rows":rows,"pid":99,
   "request":self.pin,"cwd":str(self.root),"inputs":self.request["inputs"],"P1_count":4,"occurrence_count":76,"native_calls":0,"new_native_admissions":0,
   "previous_costs":{"driver_wall_s":0.5,"work":{"original":7},"outer_process":{"window":1.0},"caller_process":{"window":1.5}},
   "imported_modules":{"__main__":str(self.root/"run_screening.py"),"screen":str(self.root/"source/screen.py"),"lark":str(self.runtime/"lark/__init__.py")},
   "inputs_unchanged":True,"sources_unchanged":True,"runtime_unchanged":True,"request_unchanged":True}
 def tearDown(self):self.tmp.cleanup()
 def emit(self,n=None):
  for p in self.out.iterdir():p.unlink()
  rows=self.result["rows"];write(self.out/"RESULT.json",self.result)
  for i,row in enumerate(rows[:len(rows) if n is None else n]):write(self.out/("SCREEN-"+str(i)+".json"),row)
 def inspect(self):return inspect_outputs(self.out,99,self.pin,self.request,self.root)
 def test_complete_76_and_duplicate_id_retention(self):
  self.emit();r=self.inspect();self.assertTrue(r["completed_contract"]);self.assertEqual(r["emitted_rows"],76)
 def test_failed_partial_prefix_with_unemitted_last_record(self):
  self.result["terminal"]="SCREENING_FAILED";self.result["rows"]=self.result["rows"][:3]
  self.emit(2);r=self.inspect();self.assertTrue(r["population_ok"]);self.assertFalse(r["completed_contract"])
  self.assertEqual(r["missing_emitted_rows"],[2]);self.assertEqual(len(r["not_recorded_occurrences"]),73)
 def test_missing_result_retains_partial_file_hashes(self):
  self.emit(2);(self.out/"RESULT.json").unlink();r=self.inspect()
  self.assertFalse(r["completed_contract"]);self.assertEqual(len(r["files"]),2);self.assertTrue(r["errors"])
 def test_swapped_identity_refuses(self):
  self.result["rows"][1]["cut_index"]=0;self.emit();self.assertFalse(self.inspect()["population_ok"])
 def test_missing_or_disagreeing_screen_refuses_completion(self):
  self.emit();(self.out/"SCREEN-1.json").unlink();self.assertFalse(self.inspect()["population_ok"])
  self.emit();write(self.out/"SCREEN-2.json",{});self.assertFalse(self.inspect()["population_ok"])
 def test_extra_file_or_nonregular_output_refuses(self):
  self.emit();write(self.out/"EXTRA.json",{});self.assertFalse(self.inspect()["population_ok"])
  self.emit();(self.out/"LINK").symlink_to(self.out/"RESULT.json");self.assertFalse(self.inspect()["population_ok"])
 def test_full_parent_and_prior_binding_refuse(self):
  self.emit();self.request["P1_count"]=3;self.assertFalse(self.inspect()["population_ok"])
  self.request["P1_count"]=4;self.request["inputs"]["P1_contracts"]["sha256"]="tampered"
  self.assertFalse(self.inspect()["population_ok"])
 def test_import_path_and_native_boundary_refuse(self):
  self.result["imported_modules"]["screen"]="/unexpected/screen.py";self.emit()
  self.assertFalse(self.inspect()["completed_contract"])
  self.result["rows"][0]["screen"]["native_acceptance"]=True;self.emit()
  self.assertFalse(self.inspect()["population_ok"])
 def test_unknown_coverage_and_lost_prior_cost_refuse(self):
  self.result["rows"][0]["screen"]["coverage_complete"]=True;self.emit()
  self.assertFalse(self.inspect()["population_ok"])
  self.result["rows"][0]["screen"]["coverage_complete"]=False;self.result["previous_costs"]["driver_wall_s"]=0
  self.emit();self.assertFalse(self.inspect()["completed_contract"])
if __name__=="__main__":
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(OutputControls);ids=[t.id() for t in suite]
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 modules={n:str(Path(m.__file__).resolve()) for n,m in sys.modules.items() if getattr(m,"__file__",None)}
 receipt={"pid":os.getpid(),"parent_pid":os.getppid(),"cwd":os.getcwd(),"python":sys.executable,
  "tests":ids,"tests_run":result.testsRun,"passed":result.wasSuccessful(),"imported_modules":modules}
 with (HERE/"qualification-01/CONTROL-RESULT.json").open("x") as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write("\n")
 raise SystemExit(0 if result.wasSuccessful() else 1)
