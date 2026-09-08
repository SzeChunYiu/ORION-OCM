"""Only affected metadata-alias regression controls, with an authored old-source witness."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,sys,unittest
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent.parent/"ordinary-cut-screen-revival-v1"
sys.path[:0]=[str(ROOT/"source"),str(PARENT/"donor/lark-runtime")]
from syntax_adapter import SyntaxPool
from syntax_engine import SyntaxEngine
from screen_work import Work
spec=importlib.util.spec_from_file_location("old_unsafe_memo",ROOT/"history/syntax_memo.py")
OLD=importlib.util.module_from_spec(spec);sys.modules[spec.name]=OLD;spec.loader.exec_module(OLD)
PARAMS=[{"id":"V"+str(i),"type":"class"} for i in range(3)]
ROWS=[{"label":"relation","kind":"$a","statement":["wff","X","rel","Y"],
 "floating":[{"label":"fx","statement":["class","X"]},{"label":"fy","statement":["class","Y"]}],"essential":[],"dv":[]},
 {"label":"unsupported","kind":"$a","statement":["wff","P","P"],
 "floating":[{"label":"fp","statement":["wff","P"]}],"essential":[],"dv":[]}]
OBS=[]
class Metadata(unittest.TestCase):
 def test_old_source_exposes_metadata_and_false_negative(self):
  w=Work();c=OLD.Context(SyntaxEngine(ROWS,PARAMS),w,("authored-old","context"))
  first=c.prove("wff",["ABSENT"]);saved=copy.deepcopy(first)
  first["unsupported_contracts"].clear()
  repeated=c.prove("wff",["ABSENT"])
  self.assertEqual(saved["status"],"UNKNOWN")
  self.assertEqual(repeated["status"],"NOT_DERIVABLE_REGISTERED_GRAMMAR")
  self.assertTrue(repeated["coverage_complete"]);self.assertEqual(c._memo.cache_info().currsize,1)
  OBS.append({"case":"KNOWN_OLD_DEFECT_REPRODUCED","first":saved,"after_mutation":repeated,"work":w.snapshot()})
 def test_successor_mutation_keeps_repeated_unknown_uncached(self):
  w=Work();c=SyntaxPool(ROWS,w).context(PARAMS)
  first=c.prove("wff",["ABSENT"]);saved=copy.deepcopy(first)
  first["unsupported_contracts"].clear()
  repeated=c.prove("wff",["ABSENT"])
  self.assertEqual(repeated["status"],"UNKNOWN");self.assertFalse(repeated["coverage_complete"])
  self.assertTrue(c.engine.compiled["unsupported"]);self.assertTrue(repeated["unsupported_contracts"])
  self.assertEqual(c._memo.cache_info().currsize,0);self.assertEqual(w["cache_misses"],2)
  OBS.append({"case":"REPAIRED_MUTATION_REFUSES","first":saved,"repeated":repeated,"work":w.snapshot()})
 def test_deadline_unknown_metadata_is_detached(self):
  w=Work();c=SyntaxPool(ROWS,w).context(PARAMS);w.started-=61
  refused=c.prove("wff",["ABSENT"]);saved=copy.deepcopy(refused)
  refused["unsupported_contracts"].clear()
  self.assertTrue(c.engine.compiled["unsupported"]);self.assertFalse(saved["cache_lookup_performed"])
  repeated=c.engine.prove("wff",["ABSENT"])
  self.assertEqual(repeated["status"],"UNKNOWN");self.assertFalse(repeated["coverage_complete"])
  OBS.append({"case":"DEADLINE_COPYOUT_REFUSES","deadline":saved,"authored_engine_recheck":repeated,"work":w.snapshot()})
if __name__=="__main__":
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Metadata);ids=[x.id() for x in suite]
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 modules={}
 for name,m in sorted(sys.modules.items()):
  path=getattr(m,"__file__",None)
  if path and Path(path).is_file():
   p=Path(path).resolve();raw=p.read_bytes()
   modules[name]={"path":str(p),"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
 receipt={"schema":"ordinary.syntax-cache-metadata-controls.v1","pid":os.getpid(),"parent_pid":os.getppid(),
 "cwd":os.getcwd(),"argv":sys.argv,"python":sys.executable,"tests":ids,"tests_run":result.testsRun,
 "success":result.wasSuccessful(),"failures":[[x.id(),t] for x,t in result.failures],"errors":[[x.id(),t] for x,t in result.errors],
 "observations":OBS,"imported_modules":modules,"scope":"Three authored metadata controls; no retained data or prior suite replay."}
 with (Path(sys.argv[1])/"CONTROLS.json").open("x") as f:json.dump(receipt,f,indent=2,sort_keys=True,allow_nan=False);f.write("\n")
 raise SystemExit(0 if result.wasSuccessful() else 1)
