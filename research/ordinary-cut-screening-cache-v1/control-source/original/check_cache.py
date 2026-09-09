"""Twelve authored memoization controls; no retained data or earlier suite is run."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,sys,unittest
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/"ordinary-cut-screen-revival-v1"
sys.path[:0]=[str(ROOT/"source"),str(BASE/"donor/lark-runtime")]
import syntax_engine as E
from syntax_adapter import SyntaxPool
from screen_work import Work
from screen import screen
spec=importlib.util.spec_from_file_location("baseline_adapter",ROOT/"history/syntax_adapter.py")
OLD=importlib.util.module_from_spec(spec);sys.modules[spec.name]=OLD;spec.loader.exec_module(OLD)
PARAMS=[{"id":"V"+str(i),"type":"class"} for i in range(3)]
TOKENS=["V0","rel","V1"]
def row(label,typecode,body,floats):
 return {"label":label,"kind":"$a","statement":[typecode]+body,
  "floating":[{"label":"f"+v,"statement":[t,v]} for t,v in floats],"essential":[],"dv":[]}
def library(incomplete=False):
 rows=[row("rel","wff",["X","rel","Y"],[("class","X"),("class","Y")]),
       row("then","wff",["(","P","then","Q",")"],[("wff","P"),("wff","Q")])]
 if incomplete:rows.append(row("nonlinear","wff",["P","P"],[("wff","P")]))
 return rows
def context(incomplete=False):
 w=Work();p=SyntaxPool(library(incomplete),w);return p.context(PARAMS),p,w
OBS=[]
class CacheControls(unittest.TestCase):
 def keep(self,c,w):OBS.append({"test":self.id(),"context":c.report(),"work":w.snapshot()})
 def test_positive_hit_reuses_parse_and_context(self):
  c,p,w=context();a=c.prove("wff",TOKENS);cost=w["parse_emit_wall_s"];calls=w["parse_calls"]
  d=p.context(copy.deepcopy(PARAMS));self.assertIs(d,c)
  b=d.prove("wff",TOKENS);self.assertTrue(b["cache_hit"]);self.assertFalse(b["syntax_computation_performed"])
  self.assertEqual(a["proof"],["cut-f0","cut-f1","rel"]);self.assertEqual(b["proof"],a["proof"])
  self.assertEqual(w["parse_calls"],calls);self.assertEqual(w["parse_emit_wall_s"],cost);self.assertEqual(b["parse_emit_wall_s"],0)
  self.assertEqual((w["cache_hits"],w["cache_misses"],w["cache_entries"]),(1,1,1))
  self.assertEqual((w["cache_stored_key_tokens"],w["cache_stored_proof_labels"]),(3,3))
  self.assertEqual(w["grammar_construction_attempts"],1);self.keep(c,w)
 def test_complete_nonmembership_cached(self):
  c,_,w=context();t=TOKENS+["V2"]
  a=c.prove("wff",t);b=c.prove("wff",t)
  self.assertEqual(a["status"],"NOT_DERIVABLE_REGISTERED_GRAMMAR");self.assertTrue(b["cache_hit"])
  self.assertEqual(w["parse_calls"],1);self.assertEqual(w["cache_stored_proof_labels"],0)
  with self.assertRaises(ValueError):c.checker("wff",t)
  self.keep(c,w)
 def test_incomplete_unknown_not_cached(self):
  c,_,w=context(True)
  for _ in range(2):
   r=c.prove("wff",["ABSENT"]);self.assertEqual(r["status"],"UNKNOWN");self.assertFalse(r["coverage_complete"])
  self.assertEqual(c._memo.cache_info().currsize,0);self.assertEqual(w["cache_misses"],2)
  self.assertEqual(w["cache_uncacheable_results"],2);self.assertGreater(w["cache_compute_wall_s"],0)
  self.keep(c,w)
 def test_replay_unknown_recomputed_then_valid_witness_cached(self):
  c,_,w=context();saved=E.replay
  def refuse(*a):raise ValueError("AUTHORED_REPLAY_FAILURE")
  E.replay=refuse
  try:
   for _ in range(2):self.assertEqual(c.prove("wff",TOKENS)["status"],"UNKNOWN")
   self.assertEqual(c._memo.cache_info().currsize,0)
  finally:E.replay=saved
  self.assertEqual(c.prove("wff",TOKENS)["status"],"SYNTAX_PROVED")
  self.assertTrue(c.prove("wff",TOKENS)["cache_hit"])
  self.assertEqual(w["parse_calls"],3);self.keep(c,w)
 def test_input_domain_refusal_bypasses_cache(self):
  c,_,w=context()
  for _ in range(2):self.assertEqual(c.prove("wff",["V0"]*513)["status"],"UNKNOWN")
  self.assertEqual(c._memo.cache_info().currsize,0);self.assertEqual(w["cache_misses"],0)
  self.assertEqual(w["cache_input_bypasses"],2);self.assertFalse(issubclass(E.SyntaxUnknown,ValueError))
  with self.assertRaises(E.SyntaxUnknown):c.checker("wff",["V0"]*513)
  self.keep(c,w)
 def test_deadline_before_hit_refuses_without_lookup(self):
  c,_,w=context();c.prove("wff",TOKENS);w.started-=61
  r=c.prove("wff",TOKENS);self.assertEqual(r["status"],"UNKNOWN");self.assertIsNone(r["proof"])
  self.assertFalse(r["cache_lookup_performed"]);self.assertEqual(w["cache_hits"],0)
  self.assertEqual(c._memo.cache_info().currsize,1);self.keep(c,w)
 def test_deadline_after_hit_refuses_without_changing_entry(self):
  c,_,w=context();c.prove("wff",TOKENS);saved=w.checkpoint;calls=[0]
  def after():
   calls[0]+=1
   if calls[0]==2:raise E.SyntaxUnknown("AUTHORED_POST_HIT_DEADLINE")
  w.checkpoint=after
  try:
   r=c.prove("wff",TOKENS);self.assertEqual(r["status"],"UNKNOWN");self.assertIsNone(r["proof"])
   self.assertTrue(r["cache_hit"]);self.assertFalse(r["coverage_complete"])
  finally:w.checkpoint=saved
  self.assertTrue(c.prove("wff",TOKENS)["cache_hit"]);self.assertEqual(w["parse_calls"],1);self.keep(c,w)
 def test_proof_and_metadata_copy_out(self):
  c,_,w=context(True);a=c.prove("wff",TOKENS)
  self.assertFalse(a["coverage_complete"]);a["proof"][0]="MUTATED";a["unsupported_contracts"].clear()
  b=c.prove("wff",TOKENS);self.assertEqual(b["proof"],["cut-f0","cut-f1","rel"])
  self.assertTrue(b["unsupported_contracts"]);self.assertFalse(b["coverage_complete"]);self.keep(c,w)
 def test_library_snapshot_and_readonly_matcher_view(self):
  rows=library();w=Work();p=SyntaxPool(rows,w);rows[0]["label"]="changed"
  c=p.context(PARAMS);self.assertEqual(c.prove("wff",TOKENS)["proof"][-1],"rel")
  with self.assertRaises(TypeError):p.contracts[0]["label"]="mutated"
  other=SyntaxPool(rows,Work()).context(PARAMS)
  self.assertEqual(other.prove("wff",TOKENS)["proof"][-1],"changed")
  self.assertNotEqual(other.namespace,c.namespace);self.keep(c,w)
 def test_parameter_type_and_token_boundary_keys(self):
  c,p,w=context();c.prove("wff",TOKENS)
  self.assertEqual(c.prove("wff",["V0 rel V1"])["status"],"NOT_DERIVABLE_REGISTERED_GRAMMAR")
  self.assertEqual(c.prove("class",TOKENS)["status"],"NOT_DERIVABLE_REGISTERED_GRAMMAR")
  d=p.context([{"id":"V"+str(i),"type":"wff"} for i in range(3)])
  self.assertEqual(c.prove("class",["V0"])["status"],"SYNTAX_PROVED")
  self.assertEqual(d.prove("class",["V0"])["status"],"NOT_DERIVABLE_REGISTERED_GRAMMAR")
  self.assertNotEqual(c.namespace,d.namespace);self.assertEqual(w["grammar_construction_attempts"],2);self.keep(c,w)
 def test_same_ordinary_screen_semantics_with_cache_reuse(self):
  rows=library()+[row("refl","|-",["(","P","then","P",")"],[("wff","P")])]
  body={"parameters":PARAMS,"query":["|-","(","V0","rel","V1","then","V0","rel","V1",")"],"premises":[]}
  w=Work();p=SyntaxPool(rows,w);w0=Work();baseline=OLD.SyntaxPool(rows,w0)
  self.assertEqual(screen(body,p,w),screen(body,baseline,w0))
  calls=w["parse_calls"];screen(body,p,w)
  self.assertEqual(w["parse_calls"],calls);self.assertEqual(w["grammar_construction_attempts"],1)
  self.assertEqual(w["P1_assertions_visited"],2*len(rows));self.keep(p.context(PARAMS),w)
 def test_actual_cache_primitive_and_miss_cost_on_post_refusal(self):
  c,_,w=context();saved=w.checkpoint;calls=[0]
  def delayed():
   calls[0]+=1
   # Delegate actual parser checkpoints; refuse after a completed miss when
   # Context has recorded its returned parse cost.
   if c._last_parse_wall>0:raise E.SyntaxUnknown("AUTHORED_POST_MISS_DEADLINE")
  w.checkpoint=delayed
  try:
   r=c.prove("wff",TOKENS);self.assertEqual(r["status"],"UNKNOWN");self.assertIsNone(r["proof"])
   self.assertGreater(r["parse_emit_wall_s"],0);self.assertEqual(r["parse_emit_wall_s"],w["parse_emit_wall_s"])
  finally:w.checkpoint=saved
  self.assertEqual(c.report()["primitive"],"functools._lru_cache_wrapper");self.keep(c,w)
if __name__=="__main__":
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(CacheControls);ids=[x.id() for x in suite]
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 modules={}
 for name,m in sorted(sys.modules.items()):
  path=getattr(m,"__file__",None)
  if path and Path(path).is_file():
   p=Path(path).resolve();raw=p.read_bytes()
   modules[name]={"path":str(p),"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
 payload={"schema":"ordinary.syntax-cache-controls.v1","pid":os.getpid(),"parent_pid":os.getppid(),
 "cwd":os.getcwd(),"argv":sys.argv,"python":sys.executable,"tests":ids,"tests_run":result.testsRun,
 "success":result.wasSuccessful(),"failures":[[x.id(),t] for x,t in result.failures],"errors":[[x.id(),t] for x,t in result.errors],
 "observations":OBS,"imported_modules":modules,
 "scope":"Twelve authored affected controls; no retained data parse/screen/native or old suite replay."}
 with (Path(sys.argv[1])/"CONTROLS.json").open("x") as f:json.dump(payload,f,indent=2,sort_keys=True,allow_nan=False);f.write("\n")
 raise SystemExit(0 if result.wasSuccessful() else 1)
